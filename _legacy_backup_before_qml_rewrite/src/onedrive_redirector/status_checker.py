from __future__ import annotations

from pathlib import Path

from .file_ops import dir_has_entries
from .junction_ops import is_junction_or_reparse_point, points_to_target
from .models import Project, ProjectStatus, StatusResult
from .path_utils import cloud_relative_to_absolute


def check_project_status(project: Project, onedrive_root: Path | None) -> StatusResult:
    if not onedrive_root:
        return StatusResult(ProjectStatus.ROOT_NOT_SET, "尚未设置 OneDrive 根目录。")

    if not project.local_path:
        return StatusResult(ProjectStatus.LOCAL_NOT_CONFIGURED, "本地源文件夹未配置。")

    local_path = Path(project.local_path)
    cloud_path = cloud_relative_to_absolute(onedrive_root, project.cloud_relative_path)

    if is_junction_or_reparse_point(local_path):
        if not cloud_path.exists():
            return StatusResult(ProjectStatus.CLOUD_MISSING, "OneDrive 目标文件夹不存在。", str(local_path), str(cloud_path))
        if points_to_target(local_path, cloud_path):
            return StatusResult(ProjectStatus.OK, "同步关系正常。", str(local_path), str(cloud_path))
        return StatusResult(ProjectStatus.LINK_ERROR, "本地链接未指向当前 OneDrive 目标文件夹。", str(local_path), str(cloud_path))

    if not local_path.exists():
        return StatusResult(ProjectStatus.LOCAL_MISSING, "本地源文件夹不存在。", str(local_path), str(cloud_path))

    if not cloud_path.exists():
        return StatusResult(ProjectStatus.CLOUD_MISSING, "OneDrive 目标文件夹不存在。", str(local_path), str(cloud_path))

    local_has_data = dir_has_entries(local_path)
    cloud_has_data = dir_has_entries(cloud_path)

    if local_has_data and cloud_has_data:
        return StatusResult(ProjectStatus.CONFLICT, "本地和 OneDrive 目标文件夹中都已有数据。", str(local_path), str(cloud_path))

    return StatusResult(ProjectStatus.LINK_ERROR, "当前路径不是有效 junction。", str(local_path), str(cloud_path))
