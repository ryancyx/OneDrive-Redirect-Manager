from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine

from ..core.project_service import ProjectService
from .controller import AppController


class MainWindow:
    def __init__(self) -> None:
        self.engine = QQmlApplicationEngine()
        self.controller = AppController(ProjectService())

        qml_path = Path(__file__).resolve().parent / "qml" / "MainWindow.qml"
        if not qml_path.exists():
            raise FileNotFoundError(f"找不到 QML 主界面文件：{qml_path}")

        self.engine.rootContext().setContextProperty("controller", self.controller)
        self.engine.load(QUrl.fromLocalFile(str(qml_path)))
        if not self.engine.rootObjects():
            raise RuntimeError(f"QML 主界面加载失败：{qml_path}")

    def show(self) -> None:
        return
