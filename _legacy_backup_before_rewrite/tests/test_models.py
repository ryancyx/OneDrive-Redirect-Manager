from onedrive_redirector.models import AppSettings, MappingStatus, SyncConfig, SyncProject


def test_sync_config_roundtrip() -> None:
    project = SyncProject(
        id="demo",
        name="Demo",
        local_path="D:/Data/demo",
        cloud_relative_path="data/demo",
        enabled=True,
        created_at="2026-07-01T22:30:00+08:00",
        last_checked_at=None,
    )
    config = SyncConfig(version=1, projects=[project])
    loaded = SyncConfig.from_dict(config.to_dict())
    assert loaded.projects[0].id == "demo"


def test_sync_config_get_project() -> None:
    project = SyncProject(
        id="demo",
        name="Demo",
        local_path="D:/Data/demo",
        cloud_relative_path="data/demo",
        enabled=True,
        created_at="2026-07-01T22:30:00+08:00",
        last_checked_at=None,
    )
    config = SyncConfig(projects=[project])
    assert config.get_project("demo") is project


def test_app_settings_roundtrip() -> None:
    settings = AppSettings(onedrive_root="D:/OneDrive/OneDriveRedirector")
    loaded = AppSettings.from_dict(settings.to_dict())
    assert loaded.onedrive_root == settings.onedrive_root
    assert MappingStatus.NORMAL.value == "NORMAL"
