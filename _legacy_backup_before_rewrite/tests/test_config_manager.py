from pathlib import Path

from onedrive_redirector.config_manager import ConfigManager
from onedrive_redirector.models import SyncProject


def test_app_settings_is_created_on_first_load(tmp_path: Path) -> None:
    manager = ConfigManager(appdata_root=tmp_path / "appdata")
    settings = manager.load_app_settings()
    assert settings.onedrive_root is None
    assert manager.settings_path.exists()


def test_sync_config_save_and_load(tmp_path: Path) -> None:
    manager = ConfigManager(appdata_root=tmp_path / "appdata")
    onedrive_root = tmp_path / "OneDriveRedirector"
    config = manager.initialize_onedrive_root(onedrive_root)
    assert config.version == 1
    assert (onedrive_root / "data").exists()

    project = SyncProject(
        id="demo",
        name="Demo",
        local_path="D:/Data/demo",
        cloud_relative_path="data/demo",
        enabled=True,
        created_at="2026-07-01T22:30:00+08:00",
        last_checked_at=None,
    )
    manager.upsert_project(onedrive_root, project)
    loaded = manager.load_sync_config(onedrive_root)
    assert loaded.projects[0].id == "demo"


def test_delete_project_updates_config(tmp_path: Path) -> None:
    manager = ConfigManager(appdata_root=tmp_path / "appdata")
    onedrive_root = tmp_path / "OneDriveRedirector"
    manager.initialize_onedrive_root(onedrive_root)

    project = SyncProject(
        id="demo",
        name="Demo",
        local_path="D:/Data/demo",
        cloud_relative_path="data/demo",
        enabled=True,
        created_at="2026-07-01T22:30:00+08:00",
        last_checked_at=None,
    )
    manager.upsert_project(onedrive_root, project)
    config = manager.delete_project(onedrive_root, "demo")
    assert config.projects == []
