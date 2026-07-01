from __future__ import annotations

import os
import re
from pathlib import Path, PurePosixPath

DRIVE_RE = re.compile(r"^[a-zA-Z]:")
RESERVED_NAMES = {"windows", "program files", "program files (x86)", "users"}


class PathValidationError(ValueError):
    pass


def normalized_abs_path(path: Path | str) -> Path:
    return Path(os.path.abspath(os.path.expanduser(str(path))))


def same_path(a: Path | str, b: Path | str) -> bool:
    return os.path.normcase(str(normalized_abs_path(a))) == os.path.normcase(str(normalized_abs_path(b)))


def is_same_or_inside_path(child: Path | str, parent: Path | str) -> bool:
    child_abs = normalized_abs_path(child)
    parent_abs = normalized_abs_path(parent)
    if same_path(child_abs, parent_abs):
        return True
    try:
        child_abs.relative_to(parent_abs)
        return True
    except ValueError:
        return False


def normalize_cloud_relative_path(value: str) -> str:
    text = (value or "").strip().replace("\\", "/")
    while "//" in text:
        text = text.replace("//", "/")
    return text


def validate_cloud_relative_path(value: str) -> str:
    text = normalize_cloud_relative_path(value)
    if not text:
        raise PathValidationError("OneDrive 路径不能为空。")
    if text in {".", "/"}:
        raise PathValidationError("OneDrive 路径无效。")
    if DRIVE_RE.match(text):
        raise PathValidationError("OneDrive 路径必须是相对路径。")
    if text.startswith("/") or text.startswith("\\"):
        raise PathValidationError("OneDrive 路径必须是相对路径。")

    pure = PurePosixPath(text)
    if any(part in {".", ".."} for part in pure.parts):
        raise PathValidationError("OneDrive 路径不能包含 . 或 ..。")
    if not pure.parts or pure.parts[0] != "data":
        raise PathValidationError("OneDrive 路径必须位于 data/ 下。")
    if len(pure.parts) < 2:
        raise PathValidationError("OneDrive 路径不能直接指向 data 根目录。")
    return pure.as_posix()


def cloud_relative_to_absolute(onedrive_root: Path | str, cloud_relative_path: str) -> Path:
    return normalized_abs_path(Path(onedrive_root) / Path(validate_cloud_relative_path(cloud_relative_path)))


def _is_dangerous_system_path(path: Path) -> bool:
    if len(path.parts) <= 1:
        return True
    if path.name.lower() in RESERVED_NAMES:
        return True
    if len(path.parts) >= 2 and path.parts[1].lower() == "users" and len(path.parts) <= 3:
        return True
    return False


def validate_local_path(local_path: Path | str, onedrive_root: Path | str, cloud_target_path: Path | str) -> Path:
    local_abs = normalized_abs_path(local_path)
    onedrive_abs = normalized_abs_path(onedrive_root)
    cloud_abs = normalized_abs_path(cloud_target_path)

    if _is_dangerous_system_path(local_abs):
        raise PathValidationError("不能使用危险系统目录作为本地源文件夹。")
    if is_same_or_inside_path(local_abs, onedrive_abs):
        raise PathValidationError("不能将本地源文件夹设置为 OneDrive 根目录或其内部目录。")
    if is_same_or_inside_path(local_abs, cloud_abs):
        raise PathValidationError("不能将本地源文件夹设置为当前云端目标目录或其内部目录。")
    return local_abs
