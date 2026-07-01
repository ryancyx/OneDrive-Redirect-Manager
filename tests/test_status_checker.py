from pathlib import Path

from onedrive_redirector.core.models import Project, ProjectStatus
from onedrive_redirector.core import status_checker


def make_project(local_path: str, cloud_relative_path: str = "data/project") -> Project:
    return Project(
        id="alpha",
        name="Alpha",
        local_path=local_path,
        cloud_relative_path=cloud_relative_path,
        created_at="2026-07-01T22:00:00+08:00",
        updated_at="2026-07-01T22:00:00+08:00",
    )


def test_root_not_set() -> None:
    result = status_checker.check_project_status(make_project("D:/Local/Alpha"), None)
    assert result.status is ProjectStatus.ROOT_NOT_SET


def test_local_not_configured() -> None:
    result = status_checker.check_project_status(make_project(""), Path("D:/Cloud/OneDriveRedirector"))
    assert result.status is ProjectStatus.LOCAL_NOT_CONFIGURED


def test_local_missing(tmp_path: Path) -> None:
    root = tmp_path / "cloud"
    (root / "data" / "project").mkdir(parents=True)
    result = status_checker.check_project_status(make_project(str(tmp_path / "missing")), root)
    assert result.status is ProjectStatus.LOCAL_MISSING


def test_cloud_missing(tmp_path: Path) -> None:
    root = tmp_path / "cloud"
    local = tmp_path / "local"
    local.mkdir()
    (local / "item.txt").write_text("x", encoding="utf-8")
    result = status_checker.check_project_status(make_project(str(local)), root)
    assert result.status is ProjectStatus.CLOUD_MISSING


def test_conflict_when_both_have_data(tmp_path: Path) -> None:
    root = tmp_path / "cloud"
    cloud = root / "data" / "project"
    cloud.mkdir(parents=True)
    (cloud / "cloud.txt").write_text("cloud", encoding="utf-8")
    local = tmp_path / "local"
    local.mkdir()
    (local / "local.txt").write_text("local", encoding="utf-8")

    result = status_checker.check_project_status(make_project(str(local)), root)
    assert result.status is ProjectStatus.CONFLICT


def test_ok_when_link_points_to_target(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "cloud"
    cloud = root / "data" / "project"
    cloud.mkdir(parents=True)
    local = tmp_path / "local-link"
    local.mkdir()

    monkeypatch.setattr(status_checker, "is_junction_or_reparse_point", lambda path: True)
    monkeypatch.setattr(status_checker, "points_to_target", lambda link, target: True)

    result = status_checker.check_project_status(make_project(str(local)), root)
    assert result.status is ProjectStatus.OK


def test_link_error_when_link_points_wrong_target(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "cloud"
    cloud = root / "data" / "project"
    cloud.mkdir(parents=True)
    local = tmp_path / "local-link"
    local.mkdir()

    monkeypatch.setattr(status_checker, "is_junction_or_reparse_point", lambda path: True)
    monkeypatch.setattr(status_checker, "points_to_target", lambda link, target: False)

    result = status_checker.check_project_status(make_project(str(local)), root)
    assert result.status is ProjectStatus.LINK_ERROR


def test_empty_local_with_cloud_data_returns_local_missing(tmp_path: Path) -> None:
    root = tmp_path / "cloud"
    cloud = root / "data" / "project"
    cloud.mkdir(parents=True)
    (cloud / "cloud.txt").write_text("cloud", encoding="utf-8")
    local = tmp_path / "local"
    local.mkdir()

    result = status_checker.check_project_status(make_project(str(local)), root)
    assert result.status is ProjectStatus.LOCAL_MISSING


def test_local_has_data_with_empty_cloud_returns_cloud_missing(tmp_path: Path) -> None:
    root = tmp_path / "cloud"
    cloud = root / "data" / "project"
    cloud.mkdir(parents=True)
    local = tmp_path / "local"
    local.mkdir()
    (local / "local.txt").write_text("local", encoding="utf-8")

    result = status_checker.check_project_status(make_project(str(local)), root)
    assert result.status is ProjectStatus.CLOUD_MISSING
