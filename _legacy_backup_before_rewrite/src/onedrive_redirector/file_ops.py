from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def timestamp_string() -> str:
    return datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")


def unique_backup_path(path: Path) -> Path:
    candidate = path.with_name(f"{path.name}_backup")
    index = 0
    while candidate.exists():
        index += 1
        candidate = path.with_name(f"{path.name}_backup_{index}")
    return candidate


def backup_existing_path(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"路径不存在，无法备份：{path}")
    backup_path = unique_backup_path(path)
    path.rename(backup_path)
    return backup_path


def move_directory(source: Path, target: Path) -> None:
    if target.exists():
        raise FileExistsError(f"目标路径已存在：{target}")
    ensure_directory(target.parent)
    shutil.move(str(source), str(target))


def copy_directory(source: Path, target: Path) -> None:
    if target.exists():
        raise FileExistsError(f"目标路径已存在：{target}")
    shutil.copytree(source, target)


def copy_directory_contents(source: Path, target: Path) -> None:
    ensure_directory(target)
    for child in source.iterdir():
        destination = target / child.name
        if child.is_dir():
            shutil.copytree(child, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(child, destination)


def remove_directory_tree(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def open_in_file_explorer(path: Path) -> None:
    import os
    import subprocess
    import sys

    if sys.platform.startswith("win"):
        os.startfile(str(path))  # type: ignore[attr-defined]
        return
    subprocess.run(["xdg-open", str(path)], check=False)
