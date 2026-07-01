from __future__ import annotations

import os
import stat
import subprocess
import sys
from pathlib import Path

from .path_utils import normalized_abs_path, same_path


def is_windows() -> bool:
    return sys.platform.startswith("win")


def is_reparse_point(path: Path | str) -> bool:
    candidate = Path(path)
    try:
        attrs = os.lstat(candidate).st_file_attributes
    except FileNotFoundError:
        return False
    except AttributeError:
        return candidate.is_symlink()
    return bool(attrs & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def is_junction_or_reparse_point(path: Path | str) -> bool:
    candidate = Path(path)
    if hasattr(candidate, "is_junction"):
        try:
            if candidate.is_junction():
                return True
        except OSError:
            pass
    return is_reparse_point(candidate)


def create_junction(link_path: Path | str, target_path: Path | str) -> None:
    link = Path(link_path)
    target = Path(target_path)

    if not is_windows():
        raise OSError("当前版本仅支持 Windows junction。")
    if link.exists() or is_reparse_point(link):
        raise FileExistsError(f"Link path already exists: {link}")
    if not target.exists() or not target.is_dir():
        raise FileNotFoundError(f"Target directory does not exist: {target}")

    link.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link), str(target)],
        capture_output=True,
        text=True,
        shell=False,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "Failed to create junction.\n"
            f"Command: mklink /J {link} {target}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
    if not is_junction_or_reparse_point(link):
        raise RuntimeError(f"Created path is not a verified reparse point: {link}")


def remove_junction(link_path: Path | str) -> None:
    link = Path(link_path)
    if not link.exists() and not is_reparse_point(link):
        return
    if not is_junction_or_reparse_point(link):
        raise ValueError(f"Path is not a junction or reparse point: {link}")
    result = subprocess.run(
        ["cmd", "/c", "rmdir", str(link)],
        capture_output=True,
        text=True,
        shell=False,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Failed to remove junction.\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )


def get_link_target(path: Path | str) -> Path | None:
    candidate = Path(path)
    if not candidate.exists():
        return None
    try:
        return normalized_abs_path(os.path.realpath(candidate))
    except OSError:
        return None


def points_to_target(link_path: Path | str, target_path: Path | str) -> bool:
    link = Path(link_path)
    if not is_junction_or_reparse_point(link):
        return False
    actual = get_link_target(link)
    if actual is None:
        return False
    return same_path(actual, target_path)
