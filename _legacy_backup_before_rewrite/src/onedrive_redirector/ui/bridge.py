from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

from ..config_manager import ConfigManager, now_iso
from ..conflict_resolver import ConflictResolver
from ..constants import APP_NAME, DEFAULT_ROOT_DIR_NAME, LOG_DIR_NAME
from ..file_ops import backup_existing_path, copy_directory_contents, ensure_directory, move_directory, open_in_file_explorer, remove_directory_tree
from ..link_ops import create_junction, is_link_path, remove_path
from ..models import AppSettings, MappingStatus, SyncConfig, SyncProject
from ..path_utils import cloud_relative_to_absolute, is_path_empty, to_portable_path, validate_cloud_relative_path, validate_local_path
from ..status_checker import check_project_status
from .dialogs import ConflictResolutionDialog, DeleteProjectDialog, ProjectDialog, SettingsDialog, confirm_delete_cloud

logger = logging.getLogger(__name__)


def _simplified_status(status: MappingStatus) -> tuple[str, str, str]:
    if status == MappingStatus.NORMAL:
        return "已正常同步", "#1f7a1f", "正常"
    if status == MappingStatus.LOCAL_NOT_CONFIGURED:
        return "本机未配置", "#6b7280", "未配置"
    if status in {MappingStatus.LOCAL_MISSING, MappingStatus.LOCAL_EMPTY_CLOUD_HAS_DATA}:
        return "本机路径不存在", "#b45309", "异常"
    if status in {MappingStatus.CLOUD_MISSING, MappingStatus.LOCAL_HAS_DATA_CLOUD_EMPTY, MappingStatus.BOTH_EMPTY}:
        return "云端路径不存在", "#b45309", "异常"
    if status == MappingStatus.CONFLICT_BOTH_HAVE_DATA:
        return "存在冲突", "#b3261e", "冲突"
    return "链接异常", "#b3261e", "异常"


class AppBridge(QObject):
    settingsChanged = Signal()
    projectListChanged = Signal()
    selectedProjectChanged = Signal()
    recentActivityChanged = Signal()

    def __init__(self, config_manager: ConfigManager) -> None:
        super().__init__()
        self.config_manager = config_manager
        self.conflict_resolver = ConflictResolver()
        self.settings: AppSettings = self.config_manager.load_app_settings()
        self.sync_config: SyncConfig = SyncConfig()
        self._selected_project_id = ""
        self._recent_activity = "尚未执行任何操作。"
        self._load_root_config()

    @property
    def onedrive_root(self) -> Path | None:
        return Path(self.settings.onedrive_root) if self.settings.onedrive_root else None

    @Property("QVariantMap", notify=settingsChanged)
    def settingsSummary(self) -> dict:
        root = str(self.onedrive_root) if self.onedrive_root else ""
        return {
            "rootPath": root,
            "isConfigured": bool(root),
            "settingsPath": str(self.config_manager.settings_path),
            "logDir": str(self.config_manager.appdata_root / LOG_DIR_NAME),
            "projectCount": len(self.sync_config.projects),
        }

    @Property("QVariantList", notify=projectListChanged)
    def projectList(self) -> list[dict]:
        views: list[dict] = []
        root = self.onedrive_root
        if not root:
            return views
        for project in self.sync_config.projects:
            result = check_project_status(project, root)
            label, color, group = _simplified_status(result.status)
            views.append(
                {
                    "id": project.id,
                    "name": project.name,
                    "localPath": project.local_path,
                    "cloudRelativePath": project.cloud_relative_path,
                    "cloudAbsolutePath": str(cloud_relative_to_absolute(root, project.cloud_relative_path)),
                    "statusCode": result.status.value,
                    "statusLabel": label,
                    "statusColor": color,
                    "statusGroup": group,
                    "message": result.message,
                    "enabled": project.enabled,
                    "lastCheckedAt": project.last_checked_at or "",
                    "createdAt": project.created_at,
                }
            )
        return views

    @Property("QVariantMap", notify=selectedProjectChanged)
    def selectedProject(self) -> dict:
        return next((project for project in self.projectList if project["id"] == self._selected_project_id), {})

    @Property(str, notify=recentActivityChanged)
    def recentActivity(self) -> str:
        return self._recent_activity

    def _set_recent(self, text: str) -> None:
        self._recent_activity = f"[{datetime.now().astimezone().strftime('%H:%M:%S')}] {text}"
        self.recentActivityChanged.emit()

    def _load_root_config(self) -> None:
        if self.onedrive_root:
            self.sync_config = self.config_manager.initialize_onedrive_root(self.onedrive_root)
        else:
            self.sync_config = SyncConfig()
        self.settingsChanged.emit()
        self.projectListChanged.emit()
        self.selectedProjectChanged.emit()

    def _save_sync_config(self) -> None:
        if not self.onedrive_root:
            raise RuntimeError("尚未设置 OneDrive 根目录。")
        self.config_manager.save_sync_config(self.onedrive_root, self.sync_config)
        self.projectListChanged.emit()
        self.selectedProjectChanged.emit()

    def _upsert_project_record(self, project: SyncProject, original_id: str | None = None) -> None:
        if not self.onedrive_root:
            raise RuntimeError("尚未设置 OneDrive 根目录。")
        self.sync_config = self.config_manager.upsert_project(self.onedrive_root, project, original_id)
        self._selected_project_id = project.id
        self.projectListChanged.emit()
        self.selectedProjectChanged.emit()

    def _find_project(self, project_id: str) -> SyncProject:
        project = self.sync_config.get_project(project_id)
        if not project:
            raise RuntimeError(f"未找到项目：{project_id}")
        return project

    def _cloud_path_for(self, project: SyncProject) -> Path:
        if not self.onedrive_root:
            raise RuntimeError("尚未设置 OneDrive 根目录。")
        return cloud_relative_to_absolute(self.onedrive_root, project.cloud_relative_path)

    def _prepare_project(self, data: dict[str, str], existing: SyncProject | None = None) -> SyncProject:
        if not data["id"] or not data["name"] or not data["local_path"]:
            raise ValueError("项目 ID、项目名称和本地源文件夹路径不能为空。")
        if not self.onedrive_root:
            raise RuntimeError("请先设置 OneDrive 根目录。")
        cloud_relative_path = validate_cloud_relative_path(data["cloud_relative_path"])
        cloud_target_path = cloud_relative_to_absolute(self.onedrive_root, cloud_relative_path)
        validate_local_path(
            Path(data["local_path"]),
            one_drive_root=self.onedrive_root,
            cloud_target_path=cloud_target_path,
        )
        return SyncProject(
            id=data["id"],
            name=data["name"],
            local_path=to_portable_path(data["local_path"]),
            cloud_relative_path=cloud_relative_path,
            enabled=True,
            created_at=existing.created_at if existing else now_iso(),
            last_checked_at=existing.last_checked_at if existing else None,
        )

    def _sync_project_paths(self, project: SyncProject) -> None:
        root = self.onedrive_root
        if not root:
            raise RuntimeError("请先设置 OneDrive 根目录。")

        local_path = Path(project.local_path)
        cloud_path = self._cloud_path_for(project)
        result = check_project_status(project, root)

        if result.status == MappingStatus.NORMAL:
            return

        if result.status in {MappingStatus.LOCAL_HAS_DATA_CLOUD_EMPTY, MappingStatus.BOTH_EMPTY}:
            ensure_directory(cloud_path.parent)
            if cloud_path.exists() and is_path_empty(cloud_path):
                cloud_path.rmdir()
            if not local_path.exists():
                ensure_directory(cloud_path)
                ok, message = create_junction(local_path, cloud_path)
                if not ok:
                    raise RuntimeError(message)
                return
            if local_path.exists() and is_path_empty(local_path) and not cloud_path.exists():
                local_path.rmdir()
                ensure_directory(cloud_path)
                ok, message = create_junction(local_path, cloud_path)
                if not ok:
                    raise RuntimeError(message)
                return
            move_directory(local_path, cloud_path)
            ok, message = create_junction(local_path, cloud_path)
            if not ok:
                raise RuntimeError(message)
            return

        if result.status in {MappingStatus.LOCAL_EMPTY_CLOUD_HAS_DATA, MappingStatus.LOCAL_MISSING}:
            if local_path.exists() and is_path_empty(local_path):
                local_path.rmdir()
            ensure_directory(cloud_path)
            ok, message = create_junction(local_path, cloud_path)
            if not ok:
                raise RuntimeError(message)
            return

        if result.status == MappingStatus.CONFLICT_BOTH_HAVE_DATA:
            dialog = ConflictResolutionDialog(local_path, cloud_path)
            if dialog.exec() != QDialog.Accepted:
                raise RuntimeError("已取消冲突处理。")
            if dialog.selected_action == ConflictResolutionDialog.ACTION_USE_CLOUD:
                ok, message = self.conflict_resolver.backup_local_and_use_cloud(local_path, cloud_path)
            elif dialog.selected_action == ConflictResolutionDialog.ACTION_USE_LOCAL:
                ok, message = self.conflict_resolver.backup_cloud_and_use_local(local_path, cloud_path)
            else:
                raise RuntimeError("已取消冲突处理。")
            if not ok:
                raise RuntimeError(message)
            return

        if result.status == MappingStatus.CLOUD_MISSING and is_link_path(local_path):
            raise RuntimeError("当前链接指向的云端路径不存在，请先检查 OneDrive 目录。")

        if result.status in {MappingStatus.LOCAL_IS_NOT_LINK, MappingStatus.WRONG_LINK_TARGET, MappingStatus.INVALID_CONFIG}:
            raise RuntimeError("当前本地路径存在异常链接，请先手动检查。")

    @Slot()
    def chooseRoot(self) -> None:
        path = QFileDialog.getExistingDirectory(None, "选择 OneDrive 同步根目录")
        if not path:
            return
        root = Path(path)
        if root.name != DEFAULT_ROOT_DIR_NAME:
            root = root / DEFAULT_ROOT_DIR_NAME
        self.settings.onedrive_root = to_portable_path(root)
        self.config_manager.save_app_settings(self.settings)
        self._load_root_config()
        self._set_recent(f"已设置 OneDrive 根目录：{root}")

    @Slot()
    def refreshStatus(self) -> None:
        if self.onedrive_root:
            self.sync_config = self.config_manager.load_sync_config(self.onedrive_root)
            for project in self.sync_config.projects:
                project.last_checked_at = now_iso()
            self._save_sync_config()
        self._set_recent("已刷新项目状态。")

    @Slot(str)
    def selectProject(self, project_id: str) -> None:
        self._selected_project_id = project_id
        self.selectedProjectChanged.emit()

    @Slot()
    def createProject(self) -> None:
        if not self.onedrive_root:
            QMessageBox.information(None, APP_NAME, "请先在设置中选择 OneDrive 同步根目录。")
            self.chooseRoot()
            return
        dialog = ProjectDialog()
        if dialog.exec() != QDialog.Accepted:
            return
        try:
            project = self._prepare_project(dialog.get_data())
            self._sync_project_paths(project)
            project.last_checked_at = now_iso()
            self._upsert_project_record(project)
            self._set_recent(f"已创建同步项目：{project.name}")
        except Exception as exc:
            QMessageBox.critical(None, "创建失败", str(exc))

    @Slot(str)
    def editProject(self, project_id: str) -> None:
        if not self.onedrive_root:
            return
        existing = self._find_project(project_id)
        dialog = ProjectDialog(
            {
                "id": existing.id,
                "name": existing.name,
                "local_path": existing.local_path,
                "cloud_relative_path": existing.cloud_relative_path,
            }
        )
        if dialog.exec() != QDialog.Accepted:
            return
        try:
            project = self._prepare_project(dialog.get_data(), existing)
            self._sync_project_paths(project)
            project.last_checked_at = now_iso()
            self._upsert_project_record(project, original_id=existing.id)
            self._set_recent(f"已更新同步项目：{project.name}")
        except Exception as exc:
            QMessageBox.critical(None, "编辑失败", str(exc))

    @Slot(str)
    def deleteProject(self, project_id: str) -> None:
        if not self.onedrive_root:
            return
        project = self._find_project(project_id)
        dialog = DeleteProjectDialog(project.name)
        if dialog.exec() != QDialog.Accepted:
            return
        cloud_path = self._cloud_path_for(project)
        try:
            if dialog.should_delete_cloud():
                if not confirm_delete_cloud(None, cloud_path):
                    return
                remove_directory_tree(cloud_path)
            self.sync_config = self.config_manager.delete_project(self.onedrive_root, project_id)
            if self._selected_project_id == project_id:
                self._selected_project_id = ""
            self.projectListChanged.emit()
            self.selectedProjectChanged.emit()
            self._set_recent(f"已删除同步项目：{project.name}")
        except Exception as exc:
            QMessageBox.critical(None, "删除失败", str(exc))

    @Slot(str)
    def restoreToLocal(self, project_id: str) -> None:
        if not self.onedrive_root:
            return
        project = self._find_project(project_id)
        local_path = Path(project.local_path)
        cloud_path = self._cloud_path_for(project)
        if not cloud_path.exists():
            QMessageBox.critical(None, "恢复失败", "OneDrive 中的目标文件夹不存在。")
            return
        try:
            if is_link_path(local_path):
                remove_path(local_path)
            elif local_path.exists() and not is_path_empty(local_path):
                answer = QMessageBox.question(
                    None,
                    "本地存在冲突",
                    "本地真实目录已存在且非空。是否先备份该目录，再恢复云端内容到本地？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if answer != QMessageBox.Yes:
                    return
                backup_existing_path(local_path)
            elif local_path.exists() and is_path_empty(local_path):
                local_path.rmdir()

            ensure_directory(local_path)
            copy_directory_contents(cloud_path, local_path)
            self.sync_config = self.config_manager.delete_project(self.onedrive_root, project_id)
            if self._selected_project_id == project_id:
                self._selected_project_id = ""
            self.projectListChanged.emit()
            self.selectedProjectChanged.emit()
            self._set_recent(f"已恢复到本地并取消同步：{project.name}")
        except Exception as exc:
            QMessageBox.critical(None, "恢复失败", str(exc))

    @Slot()
    def openSettings(self) -> None:
        dialog = SettingsDialog(
            onedrive_root=str(self.onedrive_root) if self.onedrive_root else "",
            settings_path=str(self.config_manager.settings_path),
            log_dir=str(self.config_manager.appdata_root / LOG_DIR_NAME),
            on_change_root=self.chooseRoot,
        )
        dialog.exec()

    @Slot()
    def openLog(self) -> None:
        open_in_file_explorer(ensure_directory(self.config_manager.appdata_root / LOG_DIR_NAME))

    @Slot()
    def openRootFolder(self) -> None:
        if self.onedrive_root:
            open_in_file_explorer(self.onedrive_root)
