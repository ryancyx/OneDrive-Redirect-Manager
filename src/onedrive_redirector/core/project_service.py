from __future__ import annotations

import logging
import os
from pathlib import Path

from .file_ops import backup_path, copy_directory_contents, dir_has_entries, ensure_dir, move_directory, remove_tree
from .junction_ops import create_junction, is_junction_or_reparse_point, points_to_target, remove_junction
from .models import AppSettings, Project, ProjectConfig, ProjectStatus
from .path_utils import (
    cloud_relative_to_absolute,
    is_same_or_inside_path,
    same_path,
    validate_cloud_relative_path,
    validate_local_path,
)
from .project_store import ProjectStore, now_iso
from .settings_store import SettingsStore
from .status_checker import check_project_status

logger = logging.getLogger(__name__)

STATUS_META: dict[ProjectStatus, tuple[str, str, str, str]] = {
    ProjectStatus.OK: ("已正常同步", "success", "#1f7a1f", "✓"),
    ProjectStatus.LOCAL_NOT_CONFIGURED: ("本机未配置", "muted", "#6b7280", "○"),
    ProjectStatus.LOCAL_MISSING: ("本机路径不存在", "warning", "#b45309", "!"),
    ProjectStatus.CLOUD_MISSING: ("云端路径不存在", "warning", "#b45309", "!"),
    ProjectStatus.CONFLICT: ("存在冲突", "danger", "#b3261e", "⚠"),
    ProjectStatus.LINK_ERROR: ("链接异常", "danger", "#b3261e", "✕"),
    ProjectStatus.ROOT_NOT_SET: ("未设置 OneDrive 根目录", "muted", "#6b7280", "○"),
}


class ProjectService:
    def __init__(self, settings_store: SettingsStore | None = None) -> None:
        self.settings_store = settings_store or SettingsStore()

    def load_settings(self) -> AppSettings:
        return self.settings_store.load()

    def save_onedrive_root(self, root_path: str) -> AppSettings:
        settings = AppSettings(onedrive_root=root_path or None)
        self.settings_store.save(settings)
        if root_path:
            ProjectStore(Path(root_path)).ensure_root()
        logger.info("Set OneDrive root: %s", root_path)
        return settings

    def choose_root_path(self) -> str:
        from PySide6.QtWidgets import QFileDialog

        return QFileDialog.getExistingDirectory(None, "选择 OneDrive 根目录")

    def open_log_directory(self) -> None:
        path = self.settings_store.log_dir
        path.mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            os.startfile(str(path))  # type: ignore[attr-defined]

    def get_store(self) -> ProjectStore | None:
        settings = self.load_settings()
        if not settings.onedrive_root:
            return None
        return ProjectStore(Path(settings.onedrive_root))

    def get_project_config(self) -> ProjectConfig:
        store = self.get_store()
        if not store:
            return ProjectConfig()
        return store.load()

    def get_project_list_view(self) -> list[dict]:
        settings = self.load_settings()
        root = Path(settings.onedrive_root) if settings.onedrive_root else None
        config = self.get_project_config()
        views: list[dict] = []
        for project in sorted(config.projects, key=lambda item: item.id.lower()):
            status = check_project_status(project, root)
            status_text, status_level, status_color, status_icon = STATUS_META[status.status]
            cloud_abs = str(cloud_relative_to_absolute(root, project.cloud_relative_path)) if root else ""
            views.append(
                {
                    "id": project.id,
                    "name": project.name,
                    "localPath": project.local_path,
                    "cloudRelativePath": project.cloud_relative_path,
                    "cloudAbsolutePath": cloud_abs,
                    "statusCode": status.status.value,
                    "statusText": status_text,
                    "statusLevel": status_level,
                    "statusColor": status_color,
                    "statusIcon": status_icon,
                    "message": status.message,
                }
            )
        return views

    def _ensure_root_set(self) -> Path:
        settings = self.load_settings()
        if not settings.onedrive_root:
            raise RuntimeError("请先在设置中选择 OneDrive 根目录。")
        return Path(settings.onedrive_root)

    def _make_project(self, data: dict[str, str], existing: Project | None = None) -> Project:
        root = self._ensure_root_set()
        project_id = data.get("id", "").strip()
        name = data.get("name", "").strip()
        local_raw = data.get("local_path", "").strip()
        if not project_id or not name or not local_raw:
            raise ValueError("项目 ID、项目名称和本地源文件夹路径不能为空。")

        cloud_relative = validate_cloud_relative_path(data.get("cloud_relative_path", ""))
        cloud_target = cloud_relative_to_absolute(root, cloud_relative)
        local_path = validate_local_path(local_raw, root, cloud_target)
        stamp = now_iso()
        return Project(
            id=project_id,
            name=name,
            local_path=local_path.as_posix(),
            cloud_relative_path=cloud_relative,
            created_at=existing.created_at if existing else stamp,
            updated_at=stamp,
        )

    def _sync_project(self, project: Project, conflict_strategy: str | None = None) -> None:
        root = self._ensure_root_set()
        local_path = Path(project.local_path)
        cloud_path = cloud_relative_to_absolute(root, project.cloud_relative_path)
        local_exists = local_path.exists()
        local_has_data = dir_has_entries(local_path)
        cloud_exists = cloud_path.exists()
        cloud_has_data = dir_has_entries(cloud_path)
        local_is_link = is_junction_or_reparse_point(local_path)

        if local_is_link:
            if points_to_target(local_path, cloud_path):
                return
            raise RuntimeError("本地路径已经是链接，但未指向当前 OneDrive 目标文件夹。")

        if local_has_data and (not cloud_exists or not cloud_has_data):
            ensure_dir(cloud_path.parent)
            if cloud_path.exists() and cloud_path.is_dir() and not dir_has_entries(cloud_path):
                cloud_path.rmdir()
            move_directory(local_path, cloud_path)
            create_junction(local_path, cloud_path)
            logger.info("Moved local data to cloud and created junction: %s -> %s", local_path, cloud_path)
            return

        if cloud_has_data and (not local_exists or not local_has_data):
            if local_exists and local_path.is_dir() and not dir_has_entries(local_path):
                local_path.rmdir()
            create_junction(local_path, cloud_path)
            logger.info("Created junction to cloud data: %s -> %s", local_path, cloud_path)
            return

        if local_has_data and cloud_has_data:
            if conflict_strategy == "use_cloud":
                backup = backup_path(local_path)
                logger.info("Backed up local folder: %s", backup)
                create_junction(local_path, cloud_path)
                logger.info("Created junction after choosing cloud data: %s -> %s", local_path, cloud_path)
                return
            if conflict_strategy == "use_local":
                backup = backup_path(cloud_path)
                logger.info("Backed up cloud folder: %s", backup)
                move_directory(local_path, cloud_path)
                create_junction(local_path, cloud_path)
                logger.info("Moved local data to cloud and recreated junction: %s -> %s", local_path, cloud_path)
                return
            raise RuntimeError("CONFLICT")

        if not local_exists and not cloud_exists:
            raise RuntimeError("本地和云端目录都不存在，无法建立同步。")
        if local_exists and not local_has_data and cloud_exists and not cloud_has_data:
            raise RuntimeError("本地和云端目录都为空，无法判断应使用哪一侧。")
        raise RuntimeError("当前状态无法自动处理，请检查本地和 OneDrive 目录内容。")

    def create_project(self, data: dict[str, str], conflict_strategy: str | None = None) -> None:
        root = self._ensure_root_set()
        store = ProjectStore(root)
        project = self._make_project(data)
        if store.load().get_project(project.id):
            raise ValueError(f"项目 ID 已存在：{project.id}")
        self._sync_project(project, conflict_strategy)
        store.add_project(project)
        logger.info("Created project: %s", project.id)

    def update_project(self, project_id: str, data: dict[str, str], conflict_strategy: str | None = None) -> None:
        root = self._ensure_root_set()
        store = ProjectStore(root)
        existing = store.load().get_project(project_id)
        if not existing:
            raise ValueError(f"未找到项目：{project_id}")
        project = self._make_project(data, existing)
        self._sync_project(project, conflict_strategy)
        store.update_project(project_id, project)
        logger.info("Updated project: %s", project.id)

    def _get_safe_cloud_delete_path(self, root: Path, cloud_relative_path: str) -> Path:
        normalized_relative = validate_cloud_relative_path(cloud_relative_path)
        cloud_path = cloud_relative_to_absolute(root, normalized_relative)
        data_root = root / "data"

        if same_path(cloud_path, root):
            raise RuntimeError("禁止删除 OneDrive root。")
        if same_path(cloud_path, data_root):
            raise RuntimeError("禁止删除 data 根目录。")
        if not is_same_or_inside_path(cloud_path, root):
            raise RuntimeError("云端目标路径不在 OneDrive root 内部，禁止删除。")
        return cloud_path

    def _is_dangerous_local_delete_path(self, path: Path) -> bool:
        if len(path.parts) <= 1:
            return True
        lowered_name = path.name.lower()
        if lowered_name in {"windows", "program files", "program files (x86)", "users"}:
            return True
        if len(path.parts) >= 2 and path.parts[1].lower() == "users" and len(path.parts) <= 3:
            return True
        return False

    def _get_safe_local_link_delete_path(self, root: Path, local_path_value: str) -> Path:
        if not local_path_value.strip():
            raise RuntimeError("本地路径为空，无法删除本地链接。")

        local_path = Path(local_path_value)
        if not local_path.exists():
            raise RuntimeError(f"本地链接不存在：{local_path}")
        if self._is_dangerous_local_delete_path(local_path):
            raise RuntimeError(f"禁止删除危险本地路径：{local_path}")
        if same_path(local_path, root):
            raise RuntimeError("禁止删除等于 OneDrive root 的本地路径。")
        if is_same_or_inside_path(local_path, root):
            raise RuntimeError("禁止删除位于 OneDrive root 内部的本地路径。")
        if not is_junction_or_reparse_point(local_path):
            raise RuntimeError("本地路径不是链接，已跳过删除本地链接。")
        return local_path

    def delete_project(self, project_id: str, delete_cloud: bool, delete_local_link: bool) -> None:
        root = self._ensure_root_set()
        store = ProjectStore(root)
        project = store.load().get_project(project_id)
        if not project:
            raise ValueError(f"未找到项目：{project_id}")

        local_link_path: Path | None = None
        cloud_path: Path | None = None

        if delete_local_link:
            local_link_path = self._get_safe_local_link_delete_path(root, project.local_path)
        if delete_cloud:
            cloud_path = self._get_safe_cloud_delete_path(root, project.cloud_relative_path)

        if local_link_path is not None:
            try:
                remove_junction(local_link_path)
            except Exception:
                logger.exception("Failed to delete local junction for project %s: %s", project.id, local_link_path)
                raise RuntimeError(f"删除本地链接失败：{local_link_path}")
            logger.info("Deleted local junction: %s", local_link_path)

        if cloud_path is not None:
            try:
                remove_tree(cloud_path)
            except Exception:
                logger.exception("Failed to delete cloud target for project %s: %s", project.id, cloud_path)
                raise RuntimeError(f"删除 OneDrive 目标文件夹失败：{cloud_path}")
            logger.info("Deleted cloud target: %s", cloud_path)

        store.delete_project(project.id)
        logger.info("Deleted project config: %s", project.id)

    def restore_project_to_local(self, project_id: str) -> None:
        root = self._ensure_root_set()
        store = ProjectStore(root)
        project = store.load().get_project(project_id)
        if not project:
            raise ValueError(f"未找到项目：{project_id}")

        local_path = Path(project.local_path)
        cloud_path = cloud_relative_to_absolute(root, project.cloud_relative_path)
        if not cloud_path.exists() or not cloud_path.is_dir():
            raise RuntimeError("OneDrive 目标文件夹不存在。")

        if is_junction_or_reparse_point(local_path):
            remove_junction(local_path)
            logger.info("Removed junction: %s", local_path)
        elif local_path.exists() and dir_has_entries(local_path):
            backup = backup_path(local_path)
            logger.info("Backed up existing local folder before restore: %s", backup)

        ensure_dir(local_path)
        copy_directory_contents(cloud_path, local_path)
        logger.info("Copied cloud data back to local: %s -> %s", cloud_path, local_path)
        store.delete_project(project.id)
        logger.info("Removed project config after restore: %s", project.id)
