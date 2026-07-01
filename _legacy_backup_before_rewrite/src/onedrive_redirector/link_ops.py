from __future__ import annotations

import logging
import os
import stat
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def is_windows() -> bool:
    return sys.platform.startswith("win")


def is_link_path(path: Path) -> bool:
    if not path.exists():
        return False
    if path.is_symlink():
        return True
    try:
        return bool(path.stat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except AttributeError:
        return False


def get_link_target(path: Path) -> Path | None:
    if not path.exists():
        return None
    try:
        if path.is_symlink():
            return path.resolve(strict=False)
    except OSError:
        return None

    if not is_windows():
        return None

    result = subprocess.run(
        ["fsutil", "reparsepoint", "query", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout + result.stderr
    marker = "Substitute Name:"
    for line in output.splitlines():
        if marker not in line:
            continue
        raw = line.split(marker, 1)[1].strip()
        cleaned = raw.replace("\\??\\", "")
        return Path(cleaned)
    return None


def create_junction(local_path: Path, cloud_path: Path) -> tuple[bool, str]:
    logger.info("Creating junction: local=%s cloud=%s", local_path, cloud_path)
    if not is_windows():
        return False, "Current version supports Windows only."
    if not cloud_path.exists():
        return False, f"Cloud directory does not exist: {cloud_path}"
    if local_path.exists():
        return False, f"Local path already exists: {local_path}"

    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(local_path), str(cloud_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "Failed to create junction.").strip()
        logger.error("Failed to create junction: %s", message)
        return False, message
    if not local_path.exists():
        return False, "Local path was not created."
    if not is_link_path(local_path):
        return False, "Created path is not a verified reparse point."
    return True, "Junction created successfully."


def remove_path(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir() and not path.is_symlink():
        os.rmdir(path)
    else:
        path.unlink()
