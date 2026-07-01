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


class SettingsDialog(QDialog):
    def __init__(self, current_root: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.resize(560, 180)
        self._selected_root = current_root

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.root_edit = QLineEdit(current_root)
        browse_button = QPushButton("更改 OneDrive 根目录")
        browse_button.clicked.connect(self._browse_root)

        row = QHBoxLayout()
        row.addWidget(self.root_edit)
        row.addWidget(browse_button)

        form.addRow("当前 OneDrive 根目录", row)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _browse_root(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "选择 OneDrive 根目录")
        if path:
            self.root_edit.setText(path)

    def selected_root(self) -> str:
        return self.root_edit.text().strip()


class ProjectDialog(QDialog):
    def __init__(self, project: dict[str, str] | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("新建项目" if project is None else "编辑项目")
        self.resize(620, 260)

        self.id_edit = QLineEdit(project["id"] if project else "")
        self.name_edit = QLineEdit(project["name"] if project else "")
        self.local_path_edit = QLineEdit(project["local_path"] if project else "")
        self.cloud_path_edit = QLineEdit(project["cloud_relative_path"] if project else "data/")

        browse_button = QPushButton("选择本地源文件夹")
        browse_button.clicked.connect(self._browse_local)

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

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _browse_local(self) -> None:
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


class ConflictDialog(QDialog):
    USE_CLOUD = "use_cloud"
    USE_LOCAL = "use_local"
    CANCEL = "cancel"

    def __init__(self, local_path: Path, cloud_path: Path, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("检测到冲突")
        self.resize(560, 260)
        self.choice = self.CANCEL

        layout = QVBoxLayout(self)
        text = QLabel(
            "检测到冲突：本地文件夹和 OneDrive 目标文件夹中都已有数据。\n\n"
            "请选择处理方式：\n"
            "1. 备份本地文件夹并使用云端数据\n"
            "2. 备份云端文件夹并使用本地数据\n"
            "3. 取消"
        )
        text.setWordWrap(True)
        layout.addWidget(text)
        layout.addWidget(QLabel(f"本地路径：{local_path}"))
        layout.addWidget(QLabel(f"OneDrive 路径：{cloud_path}"))

        for label, value in [
            ("备份本地文件夹并使用云端数据", self.USE_CLOUD),
            ("备份云端文件夹并使用本地数据", self.USE_LOCAL),
            ("取消", self.CANCEL),
        ]:
            button = QPushButton(label)
            button.clicked.connect(lambda _=False, chosen=value: self._finish(chosen))
            layout.addWidget(button)

    def _finish(self, choice: str) -> None:
        self.choice = choice
        if choice == self.CANCEL:
            self.reject()
        else:
            self.accept()


class DeleteProjectDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("删除同步项目")
        self.resize(560, 220)

        layout = QVBoxLayout(self)
        label = QLabel(
            "即将删除同步项目。\n\n"
            "删除后，软件将不再管理该同步关系。\n"
            "如果本地路径当前是链接，原软件可能无法继续正常访问该路径。"
        )
        label.setWordWrap(True)
        layout.addWidget(label)

        self.delete_cloud_checkbox = QCheckBox("同时删除 OneDrive 中的目标文件夹")
        layout.addWidget(self.delete_cloud_checkbox)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def should_delete_cloud(self) -> bool:
        return self.delete_cloud_checkbox.isChecked()


def confirm_delete_cloud(parent, cloud_path: Path) -> bool:
    answer = QMessageBox.warning(
        parent,
        "确认删除 OneDrive 目标文件夹",
        f"将删除以下目录：\n{cloud_path}\n\n此操作不可自动恢复，是否继续？",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No,
    )
    return answer == QMessageBox.Yes
