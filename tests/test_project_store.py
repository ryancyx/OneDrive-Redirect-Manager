from pathlib import Path

import pytest

from onedrive_redirector.core.models import Project
from onedrive_redirector.core.project_store import ProjectStore


def make_project(project_id: str = "alpha") -> Project:
    return Project(
        id=project_id,
        name="Alpha",
        local_path="D:/Local/Alpha",
        cloud_relative_path=f"data/{project_id}",
        created_at="2026-07-01T22:00:00+08:00",
        updated_at="2026-07-01T22:00:00+08:00",
    )


def test_store_creates_default_config_when_missing(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "OneDriveRedirector")
    config = store.load()
    assert config.version == 1
    assert config.projects == []
    assert store.config_path.exists()


def test_store_saves_and_loads_projects(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "OneDriveRedirector")
    store.add_project(make_project())
    config = store.load()
    assert len(config.projects) == 1
    assert config.projects[0].id == "alpha"


def test_store_preserves_chinese_project_name_in_utf8(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "OneDriveRedirector")
    project = Project(
        id="delete-both-test",
        name="删除两端入口测试",
        local_path="D:/Local/DeleteBothTest",
        cloud_relative_path="data/delete-both-test",
        created_at="2026-07-02T10:00:00+08:00",
        updated_at="2026-07-02T10:00:00+08:00",
    )

    store.add_project(project)

    raw_text = store.config_path.read_text(encoding="utf-8")
    reloaded = store.load()

    assert '"name": "删除两端入口测试"' in raw_text
    assert reloaded.get_project("delete-both-test").name == "删除两端入口测试"


def test_store_deletes_project(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "OneDriveRedirector")
    store.add_project(make_project())
    store.delete_project("alpha")
    assert store.load().projects == []


def test_store_rejects_duplicate_id(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "OneDriveRedirector")
    store.add_project(make_project())
    with pytest.raises(ValueError):
        store.add_project(make_project())


def test_store_rejects_absolute_cloud_path(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "OneDriveRedirector")
    project = Project(
        id="bad",
        name="Bad",
        local_path="D:/Local/Bad",
        cloud_relative_path="D:/absolute/path",
        created_at="2026-07-01T22:00:00+08:00",
        updated_at="2026-07-01T22:00:00+08:00",
    )
    with pytest.raises(ValueError):
        store.add_project(project)


def test_store_rejects_parent_escape_cloud_path(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "OneDriveRedirector")
    project = Project(
        id="bad2",
        name="Bad2",
        local_path="D:/Local/Bad2",
        cloud_relative_path="data/../oops",
        created_at="2026-07-01T22:00:00+08:00",
        updated_at="2026-07-01T22:00:00+08:00",
    )
    with pytest.raises(ValueError):
        store.add_project(project)
