from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .models import AppSettings


def get_appdata_root() -> Path:
    candidates: list[Path] = []
    appdata = os.environ.get("APPDATA")
    if appdata:
        candidates.append(Path(appdata) / "OneDriveRedirector")
    candidates.append(Path.home() / "AppData" / "Roaming" / "OneDriveRedirector")

    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            probe = candidate / ".write_probe"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink()
            return candidate
        except OSError:
            continue

    fallback = Path.cwd() / ".onedrive_redirector_runtime"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


class SettingsStore:
    def __init__(self, appdata_root: Path | None = None) -> None:
        self.appdata_root = appdata_root or get_appdata_root()
        self.appdata_root.mkdir(parents=True, exist_ok=True)

    @property
    def settings_path(self) -> Path:
        return self.appdata_root / "settings.json"

    @property
    def log_dir(self) -> Path:
        return self.appdata_root / "logs"

    def _read_json_utf8(self) -> dict[str, Any]:
        with self.settings_path.open("r", encoding="utf-8-sig") as handle:
            return json.load(handle)

    def _write_json_utf8(self, data: dict[str, Any]) -> None:
        with self.settings_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)

    def load(self) -> AppSettings:
        if not self.settings_path.exists():
            settings = AppSettings()
            self.save(settings)
            return settings
        data = self._read_json_utf8()
        return AppSettings.from_dict(data)

    def save(self, settings: AppSettings) -> None:
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        self._write_json_utf8(settings.to_dict())
