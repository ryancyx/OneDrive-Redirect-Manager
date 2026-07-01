from __future__ import annotations

import shutil
from pathlib import Path


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def dir_has_entries(path: Path) -> bool:
    if not path.exists():
        return False
    if path.is_file():
        return True
    try:
        next(path.iterdir())
        return True
    except StopIteration:
        return False


def unique_backup_path(path: Path) -> Path:
    candidate = path.with_name(f"{path.name}_backup")
    index = 0
    while candidate.exists():
        index += 1
        candidate = path.with_name(f"{path.name}_backup_{index}")
    return candidate


def backup_path(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"路径不存在，无法备份：{path}")
    candidate = unique_backup_path(path)
    path.rename(candidate)
    return candidate


def move_directory(source: Path, target: Path) -> None:
    if not source.exists() or not source.is_dir():
        raise FileNotFoundError(f"源目录不存在：{source}")
    if target.exists():
        raise FileExistsError(f"目标目录已存在：{target}")
    ensure_dir(target.parent)
    shutil.move(str(source), str(target))


def copy_directory_contents(source: Path, target: Path) -> None:
    if not source.exists() or not source.is_dir():
        raise FileNotFoundError(f"源目录不存在：{source}")
    ensure_dir(target)
    for child in source.iterdir():
        destination = target / child.name
        if child.is_dir():
            shutil.copytree(child, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(child, destination)


def remove_tree(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
