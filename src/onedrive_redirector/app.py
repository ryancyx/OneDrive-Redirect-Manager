from __future__ import annotations

from pathlib import Path
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from .core.logger_setup import setup_logging
from .ui.main_window import MainWindow


def _resource_path(relative_path: str) -> Path:
    """Return a project/bundled resource path.

    During normal development, resources are resolved from the project root.
    During PyInstaller one-file/one-dir execution, resources can be resolved
    from sys._MEIPASS if they were bundled with --add-data.
    """
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path

    # app.py is located at:
    # <project_root>/src/onedrive_redirector/app.py
    return Path(__file__).resolve().parents[2] / relative_path


def main() -> int:
    setup_logging()

    app = QApplication(sys.argv)
    app.setApplicationName("Cloud Redirect Manager")
    app.setOrganizationName("Ryan Cheung")

    icon_path = _resource_path("assets/CloudRedirectManager.ico")
    app_icon = QIcon(str(icon_path)) if icon_path.exists() else QIcon()

    # This sets the application/taskbar/default window icon.
    # Do not call window.setWindowIcon() here because MainWindow is a custom
    # wrapper class, not necessarily a QWidget/QMainWindow instance.
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    try:
        window = MainWindow()
        window.show()
        app.main_window = window
    except Exception as exc:
        QMessageBox.critical(None, "Cloud Redirect Manager", f"主界面加载失败：{exc}")
        return 1

    return app.exec()
