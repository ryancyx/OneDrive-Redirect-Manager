from __future__ import annotations

import logging
from pathlib import Path

from .file_ops import backup_existing_path, ensure_directory, move_directory
from .link_ops import create_junction

logger = logging.getLogger(__name__)


class ConflictResolver:
    def backup_local_and_use_cloud(self, local_path: Path, cloud_path: Path) -> tuple[bool, str]:
        ensure_directory(cloud_path)
        backup_existing_path(local_path)
        ok, message = create_junction(local_path, cloud_path)
        if ok:
            return True, "已备份本地文件夹并使用云端数据。"
        return False, message

    def backup_cloud_and_use_local(self, local_path: Path, cloud_path: Path) -> tuple[bool, str]:
        if cloud_path.exists():
            backup_existing_path(cloud_path)
        move_directory(local_path, cloud_path)
        ok, message = create_junction(local_path, cloud_path)
        if ok:
            return True, "已备份云端文件夹并使用本地数据。"
        return False, message
