from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .dialogs import ConflictDialog, DeleteProjectDialog, ProjectDialog, SettingsDialog, confirm_delete_cloud
from .file_ops import backup_path, copy_directory_contents, dir_has_entries, ensure_dir, move_directory, remove_tree
from .junction_ops import create_junction, delete_junction, is_junction_or_reparse_point, points_to_target
from .logger_setup import setup_logging
from .models import AppSettings, Project, ProjectStatus
from .path_utils import cloud_relative_to_absolute, validate_cloud_relative_path, validate_local_path
from .project_store import ProjectStore, now_iso
from .settings_store import SettingsStore
from .status_checker import check_project_status

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("OneDrive 目录重定向管理器")
        self.resize(1100, 680)

        self.settings_store = SettingsStore()
        self.settings = self.settings_store.load()
        setup_logging(self.settings_store.appdata_root)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["项目 ID", "名称", "本地源文件夹路径", "OneDrive 中的路径", "运行状态"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.edit_selected_project)

        self.root_label = QLabel()
        self.root_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        button_row = QHBoxLayout()
        self.new_button = QPushButton("新建")
        self.edit_button = QPushButton("编辑")
        self.delete_button = QPushButton("删除")
        self.refresh_button = QPushButton("刷新")
        self.settings_button = QPushButton("设置")
        self.restore_button = QPushButton("恢复到本地并取消同步")

        for button in [
            self.new_button,
            self.edit_button,
            self.delete_button,
            self.refresh_button,
            self.settings_button,
            self.restore_button,
        ]:
            button_row.addWidget(button)
        button_row.addStretch(1)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self.root_label)
        layout.addLayout(button_row)
        layout.addWidget(self.table)
        self.setCentralWidget(central)

        self.new_button.clicked.connect(self.create_project)
        self.edit_button.clicked.connect(self.edit_selected_project)
        self.delete_button.clicked.connect(self.delete_selected_project)
        self.refresh_button.clicked.connect(self.refresh_table)
        self.settings_button.clicked.connect(self.open_settings)
        self.restore_button.clicked.connect(self.restore_selected_project)

        self.refresh_table()

    def current_root(self) -> Path | None:
        return Path(self.settings.onedrive_root) if self.settings.onedrive_root else None

    def current_store(self) -> ProjectStore | None:
        root = self.current_root()
        if not root:
            return None
        return ProjectStore(root)

    def _selected_project_id(self) -> str | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).text()

    def _load_projects(self) -> list[Project]:
        store = self.current_store()
        if not store:
            return []
        return store.load().projects

    def _get_project(self, project_id: str) -> Project:
        for project in self._load_projects():
            if project.id == project_id:
                return project
        raise ValueError(f"未找到项目：{project_id}")

    def refresh_table(self) -> None:
        root = self.current_root()
        if root:
            self.root_label.setText(f"当前 OneDrive 根目录：{root}")
        else:
            self.root_label.setText("当前 OneDrive 根目录：未设置")

        projects = self._load_projects() if root else []
        self.table.setRowCount(len(projects))

        for row, project in enumerate(sorted(projects, key=lambda item: item.id.lower())):
            status = check_project_status(project, root)
            values = [
                project.id,
                project.name,
                project.local_path,
                project.cloud_relative_path,
                status.status.value,
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                self.table.setItem(row, column, item)

        self.table.resizeColumnsToContents()

    def open_settings(self) -> None:
        dialog = SettingsDialog(self.settings.onedrive_root or "", self)
        if dialog.exec() != QDialog.Accepted:
            return
        selected_root = dialog.selected_root()
        self.settings = AppSettings(onedrive_root=selected_root or None)
        self.settings_store.save(self.settings)
        if selected_root:
            ProjectStore(Path(selected_root)).ensure_root()
            logger.info("Set OneDrive root: %s", selected_root)
        self.refresh_table()

    def _ensure_root_set(self) -> Path:
        root = self.current_root()
        if not root:
            raise RuntimeError("请先在设置中选择 OneDrive 根目录。")
        return root

    def _sync_project(self, project: Project) -> None:
        root = self._ensure_root_set()
        local_path = Path(project.local_path)
        cloud_path = cloud_relative_to_absolute(root, project.cloud_relative_path)
        cloud_has_data = dir_has_entries(cloud_path)
        local_exists = local_path.exists()
        local_has_data = dir_has_entries(local_path)
        local_is_link = is_junction_or_reparse_point(local_path)

        if local_is_link:
            if points_to_target(local_path, cloud_path):
                return
            raise RuntimeError("本地路径已经是链接，但未指向当前 OneDrive 目标文件夹。")

        if local_has_data and not cloud_has_data:
            ensure_dir(cloud_path.parent)
            if cloud_path.exists() and cloud_path.is_dir() and not dir_has_entries(cloud_path):
                cloud_path.rmdir()
            move_directory(local_path, cloud_path)
            create_junction(local_path, cloud_path)
            logger.info("Moved local data to cloud and created junction: %s -> %s", local_path, cloud_path)
            return

        if cloud_has_data and (not local_exists or not local_has_data):
            if local_exists and local_path.is_dir() and not dir_has_entries(local_path):
                local_path.rmdir()
            create_junction(local_path, cloud_path)
            logger.info("Created junction to existing cloud data: %s -> %s", local_path, cloud_path)
            return

        if local_has_data and cloud_has_data:
            dialog = ConflictDialog(local_path, cloud_path, self)
            if dialog.exec() != QDialog.Accepted:
                raise RuntimeError("已取消冲突处理。")
            if dialog.choice == ConflictDialog.USE_CLOUD:
                backup_path(local_path)
                create_junction(local_path, cloud_path)
                logger.info("Backed up local folder and used cloud data: %s", local_path)
                return
            if dialog.choice == ConflictDialog.USE_LOCAL:
                backup_path(cloud_path)
                move_directory(local_path, cloud_path)
                create_junction(local_path, cloud_path)
                logger.info("Backed up cloud folder and used local data: %s", cloud_path)
                return
            raise RuntimeError("已取消冲突处理。")

        if not local_exists and not cloud_path.exists():
            raise RuntimeError("本地和 OneDrive 目标文件夹都不存在，无法建立同步。")

        raise RuntimeError("当前状态无法自动处理，请检查路径内容。")

    def create_project(self) -> None:
        try:
            root = self._ensure_root_set()
        except Exception as exc:
            QMessageBox.warning(self, "未设置根目录", str(exc))
            return

        dialog = ProjectDialog(parent=self)
        if dialog.exec() != QDialog.Accepted:
            return

        try:
            data = dialog.get_data()
            if not data["id"] or not data["name"] or not data["local_path"]:
                raise ValueError("项目 ID、项目名称和本地源文件夹路径不能为空。")
            cloud_relative_path = validate_cloud_relative_path(data["cloud_relative_path"])
            cloud_target = cloud_relative_to_absolute(root, cloud_relative_path)
            local_path = validate_local_path(data["local_path"], root, cloud_target)
            now = now_iso()
            project = Project(
                id=data["id"],
                name=data["name"],
                local_path=local_path.as_posix(),
                cloud_relative_path=cloud_relative_path,
                created_at=now,
                updated_at=now,
            )
            self._sync_project(project)
            ProjectStore(root).add_project(project)
            logger.info("Created project: %s", project.id)
            self.refresh_table()
        except Exception as exc:
            logger.exception("Failed to create project")
            QMessageBox.critical(self, "新建失败", str(exc))

    def edit_selected_project(self) -> None:
        project_id = self._selected_project_id()
        if not project_id:
            return

        try:
            root = self._ensure_root_set()
            existing = self._get_project(project_id)
        except Exception as exc:
            QMessageBox.warning(self, "编辑失败", str(exc))
            return

        dialog = ProjectDialog(
            {
                "id": existing.id,
                "name": existing.name,
                "local_path": existing.local_path,
                "cloud_relative_path": existing.cloud_relative_path,
            },
            self,
        )
        if dialog.exec() != QDialog.Accepted:
            return

        try:
            data = dialog.get_data()
            if not data["id"] or not data["name"] or not data["local_path"]:
                raise ValueError("项目 ID、项目名称和本地源文件夹路径不能为空。")
            cloud_relative_path = validate_cloud_relative_path(data["cloud_relative_path"])
            cloud_target = cloud_relative_to_absolute(root, cloud_relative_path)
            local_path = validate_local_path(data["local_path"], root, cloud_target)
            project = Project(
                id=data["id"],
                name=data["name"],
                local_path=local_path.as_posix(),
                cloud_relative_path=cloud_relative_path,
                created_at=existing.created_at,
                updated_at=now_iso(),
            )
            self._sync_project(project)
            ProjectStore(root).update_project(existing.id, project)
            logger.info("Updated project: %s", project.id)
            self.refresh_table()
        except Exception as exc:
            logger.exception("Failed to update project")
            QMessageBox.critical(self, "编辑失败", str(exc))

    def delete_selected_project(self) -> None:
        project_id = self._selected_project_id()
        if not project_id:
            return
        try:
            root = self._ensure_root_set()
            project = self._get_project(project_id)
        except Exception as exc:
            QMessageBox.warning(self, "删除失败", str(exc))
            return

        dialog = DeleteProjectDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return

        cloud_path = cloud_relative_to_absolute(root, project.cloud_relative_path)
        try:
            if dialog.should_delete_cloud():
                if cloud_path == root or cloud_path == root / "data":
                    raise RuntimeError("禁止删除 OneDrive 根目录或 data 根目录。")
                if not confirm_delete_cloud(self, cloud_path):
                    return
                remove_tree(cloud_path)
            ProjectStore(root).delete_project(project.id)
            logger.info("Deleted project: %s", project.id)
            self.refresh_table()
        except Exception as exc:
            logger.exception("Failed to delete project")
            QMessageBox.critical(self, "删除失败", str(exc))

    def restore_selected_project(self) -> None:
        project_id = self._selected_project_id()
        if not project_id:
            return
        try:
            root = self._ensure_root_set()
            project = self._get_project(project_id)
        except Exception as exc:
            QMessageBox.warning(self, "恢复失败", str(exc))
            return

        local_path = Path(project.local_path)
        cloud_path = cloud_relative_to_absolute(root, project.cloud_relative_path)
        try:
            if not cloud_path.exists() or not cloud_path.is_dir():
                raise RuntimeError("OneDrive 目标文件夹不存在。")

            if is_junction_or_reparse_point(local_path):
                delete_junction(local_path)
                ensure_dir(local_path)
                copy_directory_contents(cloud_path, local_path)
            elif local_path.exists() and dir_has_entries(local_path):
                answer = QMessageBox.question(
                    self,
                    "检测到本地冲突",
                    "本地真实目录已存在且非空。是否先备份本地目录，再恢复云端内容？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if answer != QMessageBox.Yes:
                    return
                backup_path(local_path)
                ensure_dir(local_path)
                copy_directory_contents(cloud_path, local_path)
            else:
                ensure_dir(local_path)
                copy_directory_contents(cloud_path, local_path)

            ProjectStore(root).delete_project(project.id)
            logger.info("Restored project to local and removed config: %s", project.id)
            self.refresh_table()
        except Exception as exc:
            logger.exception("Failed to restore project")
            QMessageBox.critical(self, "恢复失败", str(exc))
