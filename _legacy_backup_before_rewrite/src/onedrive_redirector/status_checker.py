from __future__ import annotations

import logging
from pathlib import Path

from .link_ops import get_link_target, is_link_path
from .models import MappingStatus, StatusResult, SyncProject
from .path_utils import cloud_relative_to_absolute, is_path_empty

logger = logging.getLogger(__name__)


def check_project_status(project: SyncProject, onedrive_root: Path) -> StatusResult:
    try:
        cloud_path = cloud_relative_to_absolute(onedrive_root, project.cloud_relative_path)
    except Exception as exc:
        return StatusResult(MappingStatus.INVALID_CONFIG, f"云端路径配置无效：{exc}", {"project_id": project.id})

    if not project.local_path:
        return StatusResult(
            MappingStatus.LOCAL_NOT_CONFIGURED,
            "当前项目还没有配置本地源文件夹。",
            {"cloud_path": str(cloud_path)},
        )

    local_path = Path(project.local_path)
    cloud_exists = cloud_path.exists()

    try:
        if is_link_path(local_path):
            if not cloud_exists:
                return StatusResult(
                    MappingStatus.CLOUD_MISSING,
                    "云端路径不存在。",
                    {"local_path": str(local_path), "cloud_path": str(cloud_path)},
                )
            target = get_link_target(local_path)
            if target is not None and target.resolve(strict=False) != cloud_path.resolve(strict=False):
                return StatusResult(
                    MappingStatus.WRONG_LINK_TARGET,
                    "本地链接指向异常。",
                    {"local_path": str(local_path), "cloud_path": str(cloud_path), "target": str(target)},
                )
            return StatusResult(
                MappingStatus.NORMAL,
                "本地路径已经正常链接到 OneDrive 目录。",
                {"local_path": str(local_path), "cloud_path": str(cloud_path)},
            )

        if not local_path.exists():
            if cloud_exists and not is_path_empty(cloud_path):
                return StatusResult(
                    MappingStatus.LOCAL_EMPTY_CLOUD_HAS_DATA,
                    "云端已有数据，本地路径不存在或为空。",
                    {"local_path": str(local_path), "cloud_path": str(cloud_path)},
                )
            return StatusResult(
                MappingStatus.LOCAL_MISSING,
                "本地源文件夹不存在。",
                {"local_path": str(local_path), "cloud_path": str(cloud_path)},
            )

        if not local_path.is_dir():
            return StatusResult(
                MappingStatus.LOCAL_IS_NOT_LINK,
                "本地路径不是可用文件夹或链接。",
                {"local_path": str(local_path), "cloud_path": str(cloud_path)},
            )

        local_empty = is_path_empty(local_path)

        if not cloud_exists:
            if local_empty:
                return StatusResult(
                    MappingStatus.BOTH_EMPTY,
                    "本地和云端都为空。",
                    {"local_path": str(local_path), "cloud_path": str(cloud_path)},
                )
            return StatusResult(
                MappingStatus.LOCAL_HAS_DATA_CLOUD_EMPTY,
                "本地有数据，云端不存在或为空。",
                {"local_path": str(local_path), "cloud_path": str(cloud_path)},
            )

        if not cloud_path.is_dir():
            return StatusResult(
                MappingStatus.INVALID_CONFIG,
                "云端路径不是文件夹。",
                {"local_path": str(local_path), "cloud_path": str(cloud_path)},
            )

        cloud_empty = is_path_empty(cloud_path)

        if local_empty and cloud_empty:
            return StatusResult(
                MappingStatus.BOTH_EMPTY,
                "本地和云端都为空。",
                {"local_path": str(local_path), "cloud_path": str(cloud_path)},
            )
        if local_empty and not cloud_empty:
            return StatusResult(
                MappingStatus.LOCAL_EMPTY_CLOUD_HAS_DATA,
                "云端已有数据，本地路径不存在或为空。",
                {"local_path": str(local_path), "cloud_path": str(cloud_path)},
            )
        if not local_empty and cloud_empty:
            return StatusResult(
                MappingStatus.LOCAL_HAS_DATA_CLOUD_EMPTY,
                "本地有数据，云端不存在或为空。",
                {"local_path": str(local_path), "cloud_path": str(cloud_path)},
            )
        return StatusResult(
            MappingStatus.CONFLICT_BOTH_HAVE_DATA,
            "本地和云端同时存在数据，需要你手动选择保留哪一侧。",
            {"local_path": str(local_path), "cloud_path": str(cloud_path)},
        )
    except PermissionError:
        return StatusResult(
            MappingStatus.PERMISSION_ERROR,
            "权限不足，无法检查项目状态。",
            {"local_path": str(local_path), "cloud_path": str(cloud_path)},
        )
    except Exception as exc:
        logger.exception("Unexpected error while checking project status")
        return StatusResult(
            MappingStatus.UNKNOWN_ERROR,
            f"状态检查失败：{exc}",
            {"local_path": str(local_path), "cloud_path": str(cloud_path)},
        )
