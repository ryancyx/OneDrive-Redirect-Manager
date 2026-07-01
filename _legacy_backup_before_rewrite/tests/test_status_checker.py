from pathlib import Path

from onedrive_redirector.models import MappingStatus, SyncProject
from onedrive_redirector.status_checker import check_project_status


def make_project(local_path: Path | str) -> SyncProject:
    return SyncProject(
        id="demo",
        name="Demo",
        local_path=local_path.as_posix() if isinstance(local_path, Path) else local_path,
        cloud_relative_path="data/demo",
        enabled=True,
        created_at="2026-07-01T22:30:00+08:00",
        last_checked_at=None,
    )


def test_status_local_not_configured(tmp_path: Path) -> None:
    result = check_project_status(make_project(""), tmp_path)
    assert result.status == MappingStatus.LOCAL_NOT_CONFIGURED


def test_status_local_missing_when_cloud_exists(tmp_path: Path) -> None:
    cloud_path = tmp_path / "data" / "demo"
    cloud_path.mkdir(parents=True)
    (cloud_path / "b.txt").write_text("b", encoding="utf-8")
    result = check_project_status(make_project(tmp_path / "missing-local"), tmp_path)
    assert result.status == MappingStatus.LOCAL_EMPTY_CLOUD_HAS_DATA


def test_status_local_missing_when_cloud_empty(tmp_path: Path) -> None:
    cloud_path = tmp_path / "data" / "demo"
    cloud_path.mkdir(parents=True)
    result = check_project_status(make_project(tmp_path / "missing-local"), tmp_path)
    assert result.status == MappingStatus.LOCAL_MISSING


def test_status_local_has_data_cloud_missing(tmp_path: Path) -> None:
    local_path = tmp_path / "local"
    local_path.mkdir()
    (local_path / "a.txt").write_text("a", encoding="utf-8")
    result = check_project_status(make_project(local_path), tmp_path)
    assert result.status == MappingStatus.LOCAL_HAS_DATA_CLOUD_EMPTY


def test_status_local_has_data_cloud_empty(tmp_path: Path) -> None:
    local_path = tmp_path / "local"
    cloud_path = tmp_path / "data" / "demo"
    local_path.mkdir()
    cloud_path.mkdir(parents=True)
    (local_path / "a.txt").write_text("a", encoding="utf-8")
    result = check_project_status(make_project(local_path), tmp_path)
    assert result.status == MappingStatus.LOCAL_HAS_DATA_CLOUD_EMPTY


def test_status_local_empty_cloud_has_data(tmp_path: Path) -> None:
    local_path = tmp_path / "local"
    cloud_path = tmp_path / "data" / "demo"
    local_path.mkdir()
    cloud_path.mkdir(parents=True)
    (cloud_path / "b.txt").write_text("b", encoding="utf-8")
    result = check_project_status(make_project(local_path), tmp_path)
    assert result.status == MappingStatus.LOCAL_EMPTY_CLOUD_HAS_DATA


def test_status_conflict_both_have_data(tmp_path: Path) -> None:
    local_path = tmp_path / "local"
    cloud_path = tmp_path / "data" / "demo"
    local_path.mkdir()
    cloud_path.mkdir(parents=True)
    (local_path / "a.txt").write_text("a", encoding="utf-8")
    (cloud_path / "b.txt").write_text("b", encoding="utf-8")
    result = check_project_status(make_project(local_path), tmp_path)
    assert result.status == MappingStatus.CONFLICT_BOTH_HAVE_DATA


def test_status_both_empty_when_local_and_cloud_empty(tmp_path: Path) -> None:
    local_path = tmp_path / "local"
    cloud_path = tmp_path / "data" / "demo"
    local_path.mkdir()
    cloud_path.mkdir(parents=True)
    result = check_project_status(make_project(local_path), tmp_path)
    assert result.status == MappingStatus.BOTH_EMPTY


def test_status_both_empty_when_local_empty_and_cloud_missing(tmp_path: Path) -> None:
    local_path = tmp_path / "local"
    local_path.mkdir()
    result = check_project_status(make_project(local_path), tmp_path)
    assert result.status == MappingStatus.BOTH_EMPTY


def test_status_cloud_missing_for_existing_link(monkeypatch, tmp_path: Path) -> None:
    local_path = tmp_path / "linked-local"
    local_path.mkdir()

    monkeypatch.setattr("onedrive_redirector.status_checker.is_link_path", lambda _: True)
    monkeypatch.setattr("onedrive_redirector.status_checker.get_link_target", lambda _: None)

    result = check_project_status(make_project(local_path), tmp_path)
    assert result.status == MappingStatus.CLOUD_MISSING


def test_status_normal_for_correct_link(monkeypatch, tmp_path: Path) -> None:
    local_path = tmp_path / "linked-local"
    local_path.mkdir()
    cloud_path = tmp_path / "data" / "demo"
    cloud_path.mkdir(parents=True)

    monkeypatch.setattr("onedrive_redirector.status_checker.is_link_path", lambda _: True)
    monkeypatch.setattr("onedrive_redirector.status_checker.get_link_target", lambda _: cloud_path)

    result = check_project_status(make_project(local_path), tmp_path)
    assert result.status == MappingStatus.NORMAL


def test_status_wrong_link_target(monkeypatch, tmp_path: Path) -> None:
    local_path = tmp_path / "linked-local"
    local_path.mkdir()
    cloud_path = tmp_path / "data" / "demo"
    cloud_path.mkdir(parents=True)
    wrong_target = tmp_path / "data" / "other"
    wrong_target.mkdir(parents=True)

    monkeypatch.setattr("onedrive_redirector.status_checker.is_link_path", lambda _: True)
    monkeypatch.setattr("onedrive_redirector.status_checker.get_link_target", lambda _: wrong_target)

    result = check_project_status(make_project(local_path), tmp_path)
    assert result.status == MappingStatus.WRONG_LINK_TARGET
