from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class ProjectDialog(QDialog):
    def __init__(self, project: dict[str, str] | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("新建同步项目" if project is None else "编辑同步项目")
        self.resize(560, 260)

        self.id_edit = QLineEdit(project["id"] if project else "")
        self.name_edit = QLineEdit(project["name"] if project else "")
        self.local_path_edit = QLineEdit(project["local_path"] if project else "")
        self.cloud_path_edit = QLineEdit(project["cloud_relative_path"] if project else "data/")

        browse_button = QPushButton("选择本地文件夹")
        browse_button.clicked.connect(self._select_local_path)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.addRow("项目 ID", self.id_edit)
        form.addRow("项目名称", self.name_edit)

        local_row = QHBoxLayout()
        local_row.addWidget(self.local_path_edit)
        local_row.addWidget(browse_button)
        form.addRow("本地源文件夹路径", local_row)
        form.addRow("OneDrive 中的路径", self.cloud_path_edit)
        layout.addLayout(form)

        buttons = QDialogButtonBox()
        buttons.addButton("确定", QDialogButtonBox.AcceptRole)
        buttons.addButton("取消", QDialogButtonBox.RejectRole)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _select_local_path(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "选择本地源文件夹")
        if path:
            self.local_path_edit.setText(path)

    def get_data(self) -> dict[str, str]:
        return {
            "id": self.id_edit.text().strip(),
            "name": self.name_edit.text().strip(),
            "local_path": self.local_path_edit.text().strip(),
            "cloud_relative_path": self.cloud_path_edit.text().strip(),
        }


class ConflictResolutionDialog(QDialog):
    ACTION_USE_CLOUD = "use_cloud"
    ACTION_USE_LOCAL = "use_local"
    ACTION_CANCEL = "cancel"

    def __init__(self, local_path: Path, cloud_path: Path, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("存在冲突")
        self.selected_action = self.ACTION_CANCEL
        self.resize(520, 280)

        layout = QVBoxLayout(self)
        text = QLabel(
            "本地文件夹和 OneDrive 目标路径中都存在数据。\n\n"
            "你可以选择：\n"
            "1. 备份本地文件夹并使用云端数据\n"
            "2. 备份云端文件夹并使用本地数据\n"
            "3. 取消"
        )
        text.setWordWrap(True)
        layout.addWidget(text)
        layout.addWidget(QLabel(f"本地路径：{local_path}"))
        layout.addWidget(QLabel(f"OneDrive 路径：{cloud_path}"))

        for label, action in [
            ("备份本地文件夹并使用云端数据", self.ACTION_USE_CLOUD),
            ("备份云端文件夹并使用本地数据", self.ACTION_USE_LOCAL),
            ("取消", self.ACTION_CANCEL),
        ]:
            button = QPushButton(label)
            button.clicked.connect(lambda _=False, chosen=action: self._finish(chosen))
            layout.addWidget(button)

    def _finish(self, action: str) -> None:
        self.selected_action = action
        if action == self.ACTION_CANCEL:
            self.reject()
        else:
            self.accept()


class DeleteProjectDialog(QDialog):
    def __init__(self, project_name: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("删除同步项目")
        self.resize(500, 220)

        layout = QVBoxLayout(self)
        label = QLabel(
            f"即将删除同步项目：{project_name}\n\n"
            "删除后，软件将不再管理该同步关系。如果本地路径当前是链接，"
            "原软件可能无法继续正常访问该路径。"
        )
        label.setWordWrap(True)
        layout.addWidget(label)

        self.delete_cloud_checkbox = QCheckBox("同时删除 OneDrive 中的目标文件夹")
        layout.addWidget(self.delete_cloud_checkbox)

        buttons = QDialogButtonBox()
        buttons.addButton("删除项目", QDialogButtonBox.AcceptRole)
        buttons.addButton("取消", QDialogButtonBox.RejectRole)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def should_delete_cloud(self) -> bool:
        return self.delete_cloud_checkbox.isChecked()


class SettingsDialog(QDialog):
    def __init__(self, onedrive_root: str, settings_path: str, log_dir: str, on_change_root, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.resize(560, 260)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.addRow("OneDrive 同步根目录", QLabel(onedrive_root or "尚未设置"))
        form.addRow("本机配置位置", QLabel(settings_path))
        form.addRow("日志位置", QLabel(log_dir))
        layout.addLayout(form)

        row = QHBoxLayout()
        change_root_button = QPushButton("更改 OneDrive 根目录")
        change_root_button.clicked.connect(on_change_root)
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        row.addWidget(change_root_button)
        row.addWidget(close_button)
        layout.addLayout(row)


def confirm_delete_cloud(parent, cloud_path: Path) -> bool:
    answer = QMessageBox.warning(
        parent,
        "确认删除云端文件夹",
        f"你勾选了同时删除 OneDrive 中的目标文件夹：\n{cloud_path}\n\n此操作无法自动恢复，是否继续？",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No,
    )
    return answer == QMessageBox.Yes
