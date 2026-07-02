from pathlib import Path

from onedrive_redirector.core.settings_store import SettingsStore


def test_settings_store_loads_utf8_bom_settings(tmp_path: Path) -> None:
    store = SettingsStore(tmp_path / "appdata")
    store.settings_path.parent.mkdir(parents=True, exist_ok=True)
    store.settings_path.write_text(
        '{"onedrive_root": "D:/CloudRoot"}',
        encoding="utf-8-sig",
    )

    settings = store.load()

    assert settings.onedrive_root == "D:/CloudRoot"
