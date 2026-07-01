from pathlib import Path

import pytest

from onedrive_redirector.junction_ops import create_junction, delete_junction, is_junction_or_reparse_point, is_windows


@pytest.mark.skipif(not is_windows(), reason="Windows only")
def test_create_junction_and_verify_reparse_point(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "link"
    create_junction(link, target)
    assert is_junction_or_reparse_point(link)


@pytest.mark.skipif(not is_windows(), reason="Windows only")
def test_existing_normal_directory_is_rejected(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "link"
    link.mkdir()
    with pytest.raises(FileExistsError):
        create_junction(link, target)


@pytest.mark.skipif(not is_windows(), reason="Windows only")
def test_missing_target_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        create_junction(tmp_path / "link", tmp_path / "missing")


@pytest.mark.skipif(not is_windows(), reason="Windows only")
def test_delete_junction_does_not_delete_target_contents(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    (target / "a.txt").write_text("a", encoding="utf-8")
    link = tmp_path / "link"
    create_junction(link, target)
    delete_junction(link)
    assert target.exists()
    assert (target / "a.txt").exists()
