from __future__ import annotations

import os
import re
from pathlib import Path, PurePosixPath

from .constants import CLOUD_DATA_DIR_NAME, RESERVED_WINDOWS_PATHS

DRIVE_RE = re.compile(r"^[a-zA-Z]:")


class PathValidationError(ValueError):
    pass


def normalize_cloud_relative_path(value: str) -> str:
    text = (value or "").strip().replace("\\", "/")
    while "//" in text:
        text = text.replace("//", "/")
    return text


def validate_cloud_relative_path(value: str) -> str:
    text = normalize_cloud_relative_path(value)
    if not text:
        raise PathValidationError("云端相对路径不能为空。")
    if text in {".", "/"}:
        raise PathValidationError("云端相对路径无效。")
    if DRIVE_RE.match(text):
        raise PathValidationError("云端相对路径不能包含盘符。")
    if text.startswith("/") or text.startswith("\\"):
        raise PathValidationError("云端相对路径不能是绝对路径。")

    pure_path = PurePosixPath(text)
    if any(part in {"..", "."} for part in pure_path.parts):
        raise PathValidationError("云端相对路径不能包含 . 或 ..。")
    if not pure_path.parts or pure_path.parts[0] != CLOUD_DATA_DIR_NAME:
        raise PathValidationError("云端相对路径必须位于 data/ 子目录下。")
    if len(pure_path.parts) < 2:
        raise PathValidationError("云端相对路径不能指向 data 根目录。")
    return pure_path.as_posix()


def cloud_relative_to_absolute(root: Path, cloud_relative_path: str) -> Path:
    return root / Path(validate_cloud_relative_path(cloud_relative_path))


def is_path_empty(path: Path) -> bool:
    if not path.exists():
        return True
    if path.is_file():
        return False
    try:
        next(path.iterdir())
    except StopIteration:
        return True
    return False


def path_has_data(path: Path) -> bool:
    return path.exists() and not is_path_empty(path)


def is_under(parent: Path, child: Path) -> bool:
    try:
        _absolute_path(child).relative_to(_absolute_path(parent))
        return True
    except ValueError:
        return False


def _absolute_path(path: Path) -> Path:
    return Path(os.path.abspath(str(path)))


def validate_local_path(
    local_path: Path,
    one_drive_root: Path | None = None,
    library_root: Path | None = None,
    cloud_target_path: Path | None = None,
) -> None:
    resolved = _absolute_path(local_path)
    parts = tuple(part.lower() for part in resolved.parts)

    if len(parts) <= 1:
        raise PathValidationError("不能映射磁盘根目录。")

    if resolved.name.lower() in RESERVED_WINDOWS_PATHS:
        raise PathValidationError("不能映射系统保留目录。")

    if len(parts) >= 2 and parts[1] == "users" and len(parts) <= 3:
        raise PathValidationError("不能映射 Users 根目录或用户主目录。")

    if one_drive_root:
        one_drive_root = _absolute_path(one_drive_root)
        if resolved == one_drive_root:
            raise PathValidationError("不能映射 OneDrive 根目录。")
        if is_under(one_drive_root, resolved):
            raise PathValidationError("不能映射 OneDrive 根目录内部目录。")

    if library_root:
        library_root = _absolute_path(library_root)
        if resolved == library_root:
            raise PathValidationError("不能映射 OneDriveRedirector 根目录。")
        if is_under(library_root, resolved):
            raise PathValidationError("不能映射 OneDriveRedirector 内部目录。")

    if cloud_target_path:
        cloud_target_path = _absolute_path(cloud_target_path)
        if resolved == cloud_target_path:
            raise PathValidationError("不能将本地路径设置为当前云端目标目录。")
        if is_under(cloud_target_path, resolved):
            raise PathValidationError("不能将本地路径设置为当前云端目标目录内部路径。")


def suggest_item_id(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    return slug or "item"


def to_portable_path(path: Path | str) -> str:
    return Path(path).as_posix()


def get_computer_name() -> str:
    return os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or "UNKNOWN-COMPUTER"
