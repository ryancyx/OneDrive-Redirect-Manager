from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "OneDrive 目录重定向管理器"
APP_SUBTITLE = "单 OneDrive 根目录下的同步项目管理工具"
DEFAULT_ROOT_DIR_NAME = "OneDriveRedirector"
CONFIG_FILE_NAME = "config.json"
SETTINGS_FILE_NAME = "settings.json"
LOG_DIR_NAME = "logs"
LOG_FILE_NAME = "app.log"
CLOUD_DATA_DIR_NAME = "data"
SUPPORTED_LINK_TYPE = "junction"
WINDOWS_ONLY_MESSAGE = "当前版本仅支持 Windows。"

RESERVED_WINDOWS_PATHS = {
    "windows",
    "program files",
    "program files (x86)",
    "users",
}


def get_appdata_root() -> Path:
    candidates = []

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
