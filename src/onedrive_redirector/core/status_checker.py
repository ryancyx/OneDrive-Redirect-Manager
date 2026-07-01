from __future__ import annotations

from pathlib import Path

from .file_ops import dir_has_entries
from .junction_ops import is_junction_or_reparse_point, points_to_target
from .models import Project, ProjectStatus, StatusResult
from .path_utils import cloud_relative_to_absolute


def check_project_status(project: Project, onedrive_root: Path | None) -> StatusResult:
    if not onedrive_root:
        return StatusResult(ProjectStatus.ROOT_NOT_SET, "未设置 OneDrive 根目录。")

    if not project.local_path:
        return StatusResult(ProjectStatus.LOCAL_NOT_CONFIGURED, "本机未配置本地源文件夹。")

    local_path = Path(project.local_path)
    cloud_path = cloud_relative_to_absolute(onedrive_root, project.cloud_relative_path)

    if is_junction_or_reparse_point(local_path):
        if not cloud_path.exists():
            return StatusResult(ProjectStatus.CLOUD_MISSING, "OneDrive 目标文件夹不存在。", str(local_path), str(cloud_path))
        if points_to_target(local_path, cloud_path):
            return StatusResult(ProjectStatus.OK, "已正常同步。", str(local_path), str(cloud_path))
        return StatusResult(ProjectStatus.LINK_ERROR, "本地链接未指向当前 OneDrive 目标文件夹。", str(local_path), str(cloud_path))

    if not local_path.exists():
        return StatusResult(ProjectStatus.LOCAL_MISSING, "本地路径不存在。", str(local_path), str(cloud_path))

    if not cloud_path.exists():
        return StatusResult(ProjectStatus.CLOUD_MISSING, "云端路径不存在。", str(local_path), str(cloud_path))

    local_has_data = dir_has_entries(local_path)
    cloud_has_data = dir_has_entries(cloud_path)

    if local_has_data and cloud_has_data:
        return StatusResult(ProjectStatus.CONFLICT, "本地和云端都已有数据。", str(local_path), str(cloud_path))
    if not local_has_data and cloud_has_data:
        return StatusResult(ProjectStatus.LOCAL_MISSING, "本地目录为空，可直接创建链接。", str(local_path), str(cloud_path))
    if local_has_data and not cloud_has_data:
        return StatusResult(ProjectStatus.CLOUD_MISSING, "云端目录为空，可迁移本地数据。", str(local_path), str(cloud_path))

    return StatusResult(ProjectStatus.LINK_ERROR, "当前不是有效链接，且缺少可自动判断的同步状态。", str(local_path), str(cloud_path))
