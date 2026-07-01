from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from .config_manager import ConfigManager
from .constants import APP_NAME, WINDOWS_ONLY_MESSAGE
from .link_ops import is_windows
from .logger_setup import setup_logging
from .ui.main_window import MainWindow


def main() -> int:
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting %s.", APP_NAME)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    if not is_windows():
        QMessageBox.warning(None, APP_NAME, WINDOWS_ONLY_MESSAGE)

    try:
        main_window = MainWindow(ConfigManager())
        app.main_window = main_window
    except Exception as exc:
        logger.exception("Failed to load QML window")
        QMessageBox.critical(None, APP_NAME, f"主界面加载失败：{exc}")
        return 1
    return app.exec()
