from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("OneDrive 目录重定向管理器")
    window = MainWindow()
    window.show()
    app.main_window = window
    return app.exec()
