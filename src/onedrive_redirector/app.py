from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from .core.logger_setup import setup_logging
from .ui.main_window import MainWindow


def main() -> int:
    setup_logging()
    app = QApplication(sys.argv)
    app.setApplicationName("OneDrive 目录重定向管理器")

    try:
        window = MainWindow()
        window.show()
        app.main_window = window
    except Exception as exc:
        QMessageBox.critical(None, "OneDrive 目录重定向管理器", f"主界面加载失败：{exc}")
        return 1
    return app.exec()
