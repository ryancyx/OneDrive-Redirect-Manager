from pathlib import Path

import pytest

import onedrive_redirector.core.file_ops as file_ops_module
from onedrive_redirector.core.file_ops import (
    backup_path,
    copy_directory_contents,
    move_directory,
    remove_tree,
    unique_backup_path,
)


def test_backup_name_uses_backup_suffix(tmp_path: Path) -> None:
    source = tmp_path / "FolderA"
    source.mkdir()
    backup = backup_path(source)
    assert backup.name == "FolderA_backup"


def test_backup_name_increments_when_existing(tmp_path: Path) -> None:
    source = tmp_path / "FolderA"
    source.mkdir()
    (tmp_path / "FolderA_backup").mkdir()
    assert unique_backup_path(source).name == "FolderA_backup_1"


def test_move_directory_moves_local_to_cloud(tmp_path: Path) -> None:
    source = tmp_path / "local"
    source.mkdir()
    (source / "data.txt").write_text("hello", encoding="utf-8")
    target = tmp_path / "cloud" / "project"

    move_directory(source, target)

    assert not source.exists()
    assert (target / "data.txt").read_text(encoding="utf-8") == "hello"


def test_copy_directory_contents_restores_cloud_to_local(tmp_path: Path) -> None:
    source = tmp_path / "cloud"
    source.mkdir()
    (source / "data.txt").write_text("hello", encoding="utf-8")
    target = tmp_path / "local"

    copy_directory_contents(source, target)

    assert (target / "data.txt").read_text(encoding="utf-8") == "hello"


def test_remove_tree_deletes_plain_directory(tmp_path: Path) -> None:
    target = tmp_path / "cloud" / "project"
    target.mkdir(parents=True)
    (target / "data.txt").write_text("hello", encoding="utf-8")

    remove_tree(target)

    assert not target.exists()


def test_remove_tree_uses_windows_rmdir_fallback_after_python_delete_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "cloud" / "project"
    target.mkdir(parents=True)
    (target / "data.txt").write_text("hello", encoding="utf-8")
    calls: list[tuple[str, object]] = []

    monkeypatch.setattr(file_ops_module, "is_junction_or_reparse_point", lambda path: False)

    def fake_rmtree(path: Path) -> None:
        calls.append(("rmtree", Path(path)))
        raise PermissionError("python delete failed")

    def fake_run(command: list[str], capture_output: bool, text: bool, shell: bool, check: bool):
        calls.append(("run", tuple(command)))
        for child in target.rglob("*"):
            if child.is_file():
                child.unlink()
        target.rmdir()

        class Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return Result()

    monkeypatch.setattr(file_ops_module.shutil, "rmtree", fake_rmtree)
    monkeypatch.setattr(file_ops_module.os, "name", "nt", raising=False)
    monkeypatch.setattr(file_ops_module.subprocess, "run", fake_run)

    remove_tree(target)

    assert calls == [("rmtree", target), ("run", ("cmd", "/c", "rmdir", "/S", "/Q", str(target)))]
    assert not target.exists()


def test_remove_tree_rejects_reparse_point(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target = tmp_path / "cloud-link"
    target.mkdir()
    monkeypatch.setattr(file_ops_module, "is_junction_or_reparse_point", lambda path: Path(path) == target)

    with pytest.raises(RuntimeError, match="目标是链接入口，不允许作为云端目录递归删除"):
        remove_tree(target)
