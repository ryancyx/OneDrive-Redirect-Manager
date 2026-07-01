from pathlib import Path

from onedrive_redirector.core.file_ops import backup_path, copy_directory_contents, move_directory, unique_backup_path


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
