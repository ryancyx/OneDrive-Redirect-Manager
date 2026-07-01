from pathlib import Path

from onedrive_redirector.file_ops import backup_path, copy_directory_contents, move_directory, unique_backup_path


def test_backup_name_uses_backup_suffix(tmp_path: Path) -> None:
    path = tmp_path / "demo"
    path.mkdir()
    result = backup_path(path)
    assert result.name == "demo_backup"


def test_backup_name_increments_when_needed(tmp_path: Path) -> None:
    path = tmp_path / "demo"
    path.mkdir()
    (tmp_path / "demo_backup").mkdir()
    assert unique_backup_path(path).name == "demo_backup_1"


def test_move_local_to_cloud(tmp_path: Path) -> None:
    source = tmp_path / "local"
    source.mkdir()
    (source / "a.txt").write_text("a", encoding="utf-8")
    target = tmp_path / "cloud" / "demo"
    move_directory(source, target)
    assert not source.exists()
    assert (target / "a.txt").exists()


def test_restore_cloud_to_local_copies_contents(tmp_path: Path) -> None:
    source = tmp_path / "cloud"
    source.mkdir()
    (source / "a.txt").write_text("a", encoding="utf-8")
    target = tmp_path / "local"
    copy_directory_contents(source, target)
    assert (target / "a.txt").exists()
