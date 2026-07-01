from pathlib import Path

import pytest

from onedrive_redirector.models import Project
from onedrive_redirector.project_store import ProjectStore, now_iso


def make_project(project_id: str = "demo") -> Project:
    stamp = now_iso()
    return Project(
        id=project_id,
        name="Demo",
        local_path="D:/Local/Demo",
        cloud_relative_path="data/demo",
        created_at=stamp,
        updated_at=stamp,
    )


def test_missing_config_is_created(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "OneDriveRedirector")
    config = store.load()
    assert config.version == 1
    assert store.config_path.exists()


def test_save_and_load_project(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "OneDriveRedirector")
    store.add_project(make_project())
    config = store.load()
    assert config.projects[0].id == "demo"


def test_delete_project(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "OneDriveRedirector")
    store.add_project(make_project())
    config = store.delete_project("demo")
    assert config.projects == []


def test_duplicate_id_is_rejected(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "OneDriveRedirector")
    store.add_project(make_project())
    with pytest.raises(ValueError):
        store.add_project(make_project())


def test_absolute_cloud_relative_path_is_rejected(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "OneDriveRedirector")
    stamp = now_iso()
    project = Project(
        id="demo",
        name="Demo",
        local_path="D:/Local/Demo",
        cloud_relative_path="D:/Cloud/Demo",
        created_at=stamp,
        updated_at=stamp,
    )
    with pytest.raises(ValueError):
        store.add_project(project)
