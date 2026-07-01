from __future__ import annotations

import logging

from PySide6.QtCore import QObject, Property, Signal, Slot

from ..core.project_service import ProjectService

logger = logging.getLogger(__name__)


class AppController(QObject):
    projectsChanged = Signal()
    rootChanged = Signal()
    errorOccurred = Signal(str)
    messageOccurred = Signal(str)
    conflictRequired = Signal(str, "QVariantMap")

    def __init__(self, service: ProjectService | None = None) -> None:
        super().__init__()
        self.service = service or ProjectService()
        self._pending_action: tuple[str, str, dict[str, str]] | None = None

    @Property("QVariantList", notify=projectsChanged)
    def projectList(self) -> list[dict]:
        return self.service.get_project_list_view()

    @Property(str, notify=rootChanged)
    def currentRoot(self) -> str:
        settings = self.service.load_settings()
        return settings.onedrive_root or ""

    @Property(bool, notify=rootChanged)
    def hasRoot(self) -> bool:
        return bool(self.currentRoot)

    @Slot()
    def refreshProjects(self) -> None:
        self.projectsChanged.emit()
        self.rootChanged.emit()

    @Slot(result="QVariantList")
    def getProjectList(self) -> list[dict]:
        return self.projectList

    @Slot(result=str)
    def getCurrentOneDriveRoot(self) -> str:
        return self.currentRoot

    @Slot()
    def chooseOneDriveRoot(self) -> None:
        try:
            path = self.service.choose_root_path()
            if not path:
                return
            self.service.save_onedrive_root(path)
            self.rootChanged.emit()
            self.projectsChanged.emit()
            self.messageOccurred.emit("已更新 OneDrive 根目录。")
        except Exception as exc:
            logger.exception("Failed to choose OneDrive root")
            self.errorOccurred.emit(str(exc))

    @Slot()
    def openLogDirectory(self) -> None:
        try:
            self.service.open_log_directory()
        except Exception as exc:
            logger.exception("Failed to open log directory")
            self.errorOccurred.emit(str(exc))

    @Slot("QVariantMap")
    def createProject(self, project_data: dict) -> None:
        self._run_create(project_data, None)

    def _run_create(self, project_data: dict, conflict_strategy: str | None) -> None:
        try:
            self.service.create_project(dict(project_data), conflict_strategy)
            self.projectsChanged.emit()
            self.messageOccurred.emit("已创建项目。")
        except RuntimeError as exc:
            if str(exc) == "CONFLICT":
                self._pending_action = ("create", "", dict(project_data))
                self.conflictRequired.emit("create", dict(project_data))
                return
            logger.exception("Failed to create project")
            self.errorOccurred.emit(str(exc))
        except Exception as exc:
            logger.exception("Failed to create project")
            self.errorOccurred.emit(str(exc))

    @Slot(str, "QVariantMap")
    def updateProject(self, project_id: str, project_data: dict) -> None:
        self._run_update(project_id, project_data, None)

    def _run_update(self, project_id: str, project_data: dict, conflict_strategy: str | None) -> None:
        try:
            self.service.update_project(project_id, dict(project_data), conflict_strategy)
            self.projectsChanged.emit()
            self.messageOccurred.emit("已更新项目。")
        except RuntimeError as exc:
            if str(exc) == "CONFLICT":
                self._pending_action = ("update", project_id, dict(project_data))
                self.conflictRequired.emit("update", dict(project_data))
                return
            logger.exception("Failed to update project")
            self.errorOccurred.emit(str(exc))
        except Exception as exc:
            logger.exception("Failed to update project")
            self.errorOccurred.emit(str(exc))

    @Slot(str, bool, bool)
    def deleteProject(self, project_id: str, delete_cloud: bool, delete_local_link: bool) -> None:
        try:
            self.service.delete_project(project_id, delete_cloud, delete_local_link)
            self.projectsChanged.emit()
            self.messageOccurred.emit("已删除项目。")
        except Exception as exc:
            logger.exception("Failed to delete project")
            self.errorOccurred.emit(str(exc))

    @Slot(str)
    def restoreProjectToLocal(self, project_id: str) -> None:
        try:
            self.service.restore_project_to_local(project_id)
            self.projectsChanged.emit()
            self.messageOccurred.emit("已恢复到本地并取消同步。")
        except Exception as exc:
            logger.exception("Failed to restore project")
            self.errorOccurred.emit(str(exc))

    @Slot(str)
    def resolveConflict(self, strategy: str) -> None:
        if not self._pending_action:
            return
        action, project_id, payload = self._pending_action
        self._pending_action = None
        if action == "create":
            self._run_create(payload, strategy)
        elif action == "update":
            self._run_update(project_id, payload, strategy)
