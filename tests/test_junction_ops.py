from pathlib import Path
import sys

import pytest

from onedrive_redirector.core import junction_ops


def test_create_junction_rejects_existing_normal_directory(tmp_path: Path) -> None:
    link = tmp_path / "link"
    link.mkdir()
    target = tmp_path / "target"
    target.mkdir()

    with pytest.raises(FileExistsError):
        junction_ops.create_junction(link, target)


def test_create_junction_rejects_missing_target(tmp_path: Path) -> None:
    link = tmp_path / "link"
    target = tmp_path / "missing-target"

    if not junction_ops.is_windows():
        with pytest.raises(OSError):
            junction_ops.create_junction(link, target)
    else:
        with pytest.raises(FileNotFoundError):
            junction_ops.create_junction(link, target)


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="Windows junction test only")
def test_create_and_remove_real_junction(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    (target / "hello.txt").write_text("world", encoding="utf-8")
    link = tmp_path / "link"

    try:
        junction_ops.create_junction(link, target)
    except PermissionError:
        pytest.skip("No permission to create junction")
    except RuntimeError as exc:
        if "privilege" in str(exc).lower():
            pytest.skip("No permission to create junction")
        raise

    assert junction_ops.is_junction_or_reparse_point(link)
    assert junction_ops.points_to_target(link, target)
    assert (link / "hello.txt").read_text(encoding="utf-8") == "world"

    junction_ops.remove_junction(link)

    assert not link.exists()
    assert (target / "hello.txt").exists()


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="Windows junction test only")
def test_remove_junction_does_not_delete_target_contents(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    (target / "keep.txt").write_text("keep", encoding="utf-8")
    link = tmp_path / "link"

    try:
        junction_ops.create_junction(link, target)
    except PermissionError:
        pytest.skip("No permission to create junction")
    except RuntimeError as exc:
        if "privilege" in str(exc).lower():
            pytest.skip("No permission to create junction")
        raise

    junction_ops.remove_junction(link)

    assert not link.exists()
    assert target.exists()
    assert (target / "keep.txt").exists()


def test_remove_junction_allows_broken_reparse_point_without_path_exists(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    link = tmp_path / "broken-link"
    calls: list[list[str]] = []

    monkeypatch.setattr(Path, "exists", lambda self: False)
    monkeypatch.setattr(junction_ops, "is_reparse_point", lambda path: True)
    monkeypatch.setattr(junction_ops, "is_junction_or_reparse_point", lambda path: True)

    def fake_run(cmd: list[str], capture_output: bool, text: bool, shell: bool, check: bool):
        calls.append(cmd)

        class Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return Result()

    monkeypatch.setattr(junction_ops.subprocess, "run", fake_run)

    junction_ops.remove_junction(link)

    assert calls == [["cmd", "/c", "rmdir", str(link)]]
