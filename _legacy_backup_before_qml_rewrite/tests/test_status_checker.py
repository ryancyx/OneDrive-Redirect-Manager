from pathlib import Path

from onedrive_redirector.models import Project, ProjectStatus
from onedrive_redirector.status_checker import check_project_status


def make_project(local_path: str) -> Project:
    return Project(
        id="demo",
        name="Demo",
        local_path=local_path,
        cloud_relative_path="data/demo",
        created_at="2026-07-01T22:00:00+08:00",
        updated_at="2026-07-01T22:00:00+08:00",
    )


def test_local_path_empty_means_not_configured(tmp_path: Path) -> None:
    result = check_project_status(make_project(""), tmp_path)
    assert result.status == ProjectStatus.LOCAL_NOT_CONFIGURED


def test_local_path_missing(tmp_path: Path) -> None:
    result = check_project_status(make_project(str(tmp_path / "missing")), tmp_path)
    assert result.status == ProjectStatus.LOCAL_MISSING


def test_cloud_target_missing(tmp_path: Path) -> None:
    local_path = tmp_path / "local"
    local_path.mkdir()
    result = check_project_status(make_project(str(local_path)), tmp_path)
    assert result.status == ProjectStatus.CLOUD_MISSING


def test_conflict_when_both_have_data(tmp_path: Path) -> None:
    local_path = tmp_path / "local"
    local_path.mkdir()
    (local_path / "a.txt").write_text("a", encoding="utf-8")
    cloud_path = tmp_path / "data" / "demo"
    cloud_path.mkdir(parents=True)
    (cloud_path / "b.txt").write_text("b", encoding="utf-8")
    result = check_project_status(make_project(str(local_path)), tmp_path)
    assert result.status == ProjectStatus.CONFLICT


def test_normal_when_junction_points_to_target(monkeypatch, tmp_path: Path) -> None:
    local_path = tmp_path / "local"
    local_path.mkdir()
    cloud_path = tmp_path / "data" / "demo"
    cloud_path.mkdir(parents=True)
    monkeypatch.setattr("onedrive_redirector.status_checker.is_junction_or_reparse_point", lambda _: True)
    monkeypatch.setattr("onedrive_redirector.status_checker.points_to_target", lambda *_: True)
    result = check_project_status(make_project(str(local_path)), tmp_path)
    assert result.status == ProjectStatus.OK


def test_link_error_when_junction_points_elsewhere(monkeypatch, tmp_path: Path) -> None:
    local_path = tmp_path / "local"
    local_path.mkdir()
    cloud_path = tmp_path / "data" / "demo"
    cloud_path.mkdir(parents=True)
    monkeypatch.setattr("onedrive_redirector.status_checker.is_junction_or_reparse_point", lambda _: True)
    monkeypatch.setattr("onedrive_redirector.status_checker.points_to_target", lambda *_: False)
    result = check_project_status(make_project(str(local_path)), tmp_path)
    assert result.status == ProjectStatus.LINK_ERROR
