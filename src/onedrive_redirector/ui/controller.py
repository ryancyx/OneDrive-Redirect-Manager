from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, Property, QRunnable, QThreadPool, QTimer, Signal, Slot

from ..core.project_service import ProjectService

logger = logging.getLogger(__name__)


class _ServiceTaskSignals(QObject):
    success = Signal(object)
    error = Signal(str)
    conflict = Signal()
    finished = Signal(str)


class _ServiceTask(QRunnable):
    def __init__(self, operation: Callable[[], Any], *, allow_conflict: bool = False) -> None:
        super().__init__()
        self._operation = operation
        self._allow_conflict = allow_conflict
        self.signals = _ServiceTaskSignals()

    def run(self) -> None:
        outcome = "error"
        try:
            result = self._operation()
        except RuntimeError as exc:
            if self._allow_conflict and str(exc) == "CONFLICT":
                outcome = "conflict"
                self.signals.conflict.emit()
            else:
                logger.exception("Background service task failed")
                self.signals.error.emit(str(exc))
        except BaseException as exc:
            logger.exception("Background service task failed")
            self.signals.error.emit(str(exc))
        else:
            outcome = "success"
            self.signals.success.emit(result)
        finally:
            self.signals.finished.emit(outcome)


class AppController(QObject):
    projectsChanged = Signal()
    rootChanged = Signal()
    errorOccurred = Signal(str)
    messageOccurred = Signal(str)
    conflictRequired = Signal(str, "QVariantMap")
    busyChanged = Signal()
    busyTextChanged = Signal()

    def __init__(self, service: ProjectService | None = None) -> None:
        super().__init__()
        self.service = service or ProjectService()
        self._pending_action: tuple[str, str, dict[str, str]] | None = None
        self._busy = False
        self._busy_text = ""
        self._thread_pool = QThreadPool(self)
        self._active_tasks: set[_ServiceTask] = set()

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

    @Property(bool, notify=busyChanged)
    def busy(self) -> bool:
        return self._busy

    @Property(str, notify=busyTextChanged)
    def busyText(self) -> str:
        return self._busy_text

    def _set_busy(self, text: str) -> None:
        busy_text = text or "正在处理，请稍候。"
        if self._busy_text != busy_text:
            self._busy_text = busy_text
            self.busyTextChanged.emit()
        if not self._busy:
            self._busy = True
            self.busyChanged.emit()

    def _clear_busy(self) -> None:
        busy_changed = self._busy
        text_changed = bool(self._busy_text)
        self._busy = False
        self._busy_text = ""
        if busy_changed:
            self.busyChanged.emit()
        if text_changed:
            self.busyTextChanged.emit()

    def _handle_task_success(
        self,
        success_message: str | None,
        *,
        refresh_projects: bool = False,
        refresh_root: bool = False,
    ) -> None:
        self._clear_busy()
        if refresh_root:
            self.rootChanged.emit()
        if refresh_projects:
            self.projectsChanged.emit()
        if success_message:
            self.messageOccurred.emit(success_message)

    def _handle_task_error(self, message: str) -> None:
        self._clear_busy()
        self.errorOccurred.emit(message)

    def _handle_task_conflict(self, action: str, project_id: str, payload: dict[str, str]) -> None:
        self._pending_action = (action, project_id, dict(payload))
        self._clear_busy()
        self.conflictRequired.emit(action, dict(payload))

    def _handle_task_finished(self, task: _ServiceTask, outcome: str) -> None:
        self._active_tasks.discard(task)
        if outcome not in {"success", "error", "conflict"}:
            self._handle_task_error("后台任务异常结束。")

    def _start_task(
        self,
        operation: Callable[[], Any],
        *,
        success_message: str | None = None,
        refresh_projects: bool = False,
        refresh_root: bool = False,
        allow_conflict: bool = False,
        conflict_action: str = "",
        conflict_project_id: str = "",
        conflict_payload: dict[str, str] | None = None,
    ) -> None:
        task = _ServiceTask(operation, allow_conflict=allow_conflict)
        self._active_tasks.add(task)

        task.signals.success.connect(
            lambda _result=None, message=success_message, projects=refresh_projects, root=refresh_root: self._handle_task_success(
                message,
                refresh_projects=projects,
                refresh_root=root,
            )
        )
        task.signals.error.connect(self._handle_task_error)

        if allow_conflict:
            payload = dict(conflict_payload or {})
            task.signals.conflict.connect(
                lambda action=conflict_action, project_id=conflict_project_id, data=payload: self._handle_task_conflict(
                    action,
                    project_id,
                    data,
                )
            )

        task.signals.finished.connect(lambda outcome, running_task=task: self._handle_task_finished(running_task, outcome))
        self._thread_pool.start(task)

    def _queue_task(
        self,
        busy_text: str,
        operation: Callable[[], Any],
        *,
        success_message: str | None = None,
        refresh_projects: bool = False,
        refresh_root: bool = False,
        allow_conflict: bool = False,
        conflict_action: str = "",
        conflict_project_id: str = "",
        conflict_payload: dict[str, str] | None = None,
    ) -> None:
        if self._busy:
            return
        self._set_busy(busy_text)
        QTimer.singleShot(
            0,
            lambda: self._start_task(
                operation,
                success_message=success_message,
                refresh_projects=refresh_projects,
                refresh_root=refresh_root,
                allow_conflict=allow_conflict,
                conflict_action=conflict_action,
                conflict_project_id=conflict_project_id,
                conflict_payload=conflict_payload,
            ),
        )

    def _busy_text_for_action(self, action: str) -> str:
        if action == "create":
            return "正在创建项目并建立 junction 链接，请稍候。"
        if action == "update":
            return "正在更新项目并调整同步关系，请稍候。"
        return "正在处理，请稍候。"

    @Slot()
    def refreshProjects(self) -> None:
        if self._busy:
            return
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
        if self._busy:
            return
        try:
            path = self.service.choose_root_path()
        except Exception as exc:
            logger.exception("Failed to choose OneDrive root")
            self.errorOccurred.emit(str(exc))
            return

        if not path:
            return

        self._queue_task(
            "正在更新 Cloud 工作目录，请稍候。",
            lambda selected_path=path: self.service.save_onedrive_root(selected_path),
            success_message="已更新 Cloud 工作目录。",
            refresh_projects=True,
            refresh_root=True,
        )

    @Slot()
    def openLogDirectory(self) -> None:
        if self._busy:
            return
        try:
            self.service.open_log_directory()
        except Exception as exc:
            logger.exception("Failed to open log directory")
            self.errorOccurred.emit(str(exc))

    @Slot("QVariantMap")
    def createProject(self, project_data: dict) -> None:
        payload = dict(project_data)
        self._queue_task(
            "正在创建项目并建立 junction 链接，请稍候。",
            lambda data=payload: self.service.create_project(dict(data), None),
            success_message="已创建项目。",
            refresh_projects=True,
            allow_conflict=True,
            conflict_action="create",
            conflict_payload=payload,
        )

    @Slot(str, "QVariantMap")
    def updateProject(self, project_id: str, project_data: dict) -> None:
        payload = dict(project_data)
        self._queue_task(
            "正在更新项目并调整同步关系，请稍候。",
            lambda target_id=project_id, data=payload: self.service.update_project(target_id, dict(data), None),
            success_message="已更新项目。",
            refresh_projects=True,
            allow_conflict=True,
            conflict_action="update",
            conflict_project_id=project_id,
            conflict_payload=payload,
        )

    @Slot(str, bool, bool)
    def deleteProject(self, project_id: str, delete_cloud: bool, delete_local_link: bool) -> None:
        self._queue_task(
            "正在删除项目，请不要关闭软件。云盘客户端正在同步时可能需要几秒钟。",
            lambda target_id=project_id, cloud=delete_cloud, local=delete_local_link: self.service.delete_project(target_id, cloud, local),
            success_message="已删除项目。",
            refresh_projects=True,
        )

    @Slot(str)
    def restoreProjectToLocal(self, project_id: str) -> None:
        self._queue_task(
            "正在恢复数据到本地，请不要关闭软件。",
            lambda target_id=project_id: self.service.restore_project_to_local(target_id),
            success_message="已恢复到本地并取消同步。",
            refresh_projects=True,
        )

    @Slot(str)
    def resolveConflict(self, strategy: str) -> None:
        if self._busy or not self._pending_action:
            return

        action, project_id, payload = self._pending_action
        self._pending_action = None

        if action == "create":
            self._queue_task(
                self._busy_text_for_action(action),
                lambda data=payload, selected_strategy=strategy: self.service.create_project(dict(data), selected_strategy),
                success_message="已创建项目。",
                refresh_projects=True,
                allow_conflict=True,
                conflict_action=action,
                conflict_payload=payload,
            )
        elif action == "update":
            self._queue_task(
                self._busy_text_for_action(action),
                lambda target_id=project_id, data=payload, selected_strategy=strategy: self.service.update_project(
                    target_id,
                    dict(data),
                    selected_strategy,
                ),
                success_message="已更新项目。",
                refresh_projects=True,
                allow_conflict=True,
                conflict_action=action,
                conflict_project_id=project_id,
                conflict_payload=payload,
            )