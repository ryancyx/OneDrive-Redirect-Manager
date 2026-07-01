from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from .constants import CONFIG_FILE_NAME, CLOUD_DATA_DIR_NAME, SETTINGS_FILE_NAME, get_appdata_root
from .file_ops import ensure_directory
from .models import AppSettings, SyncConfig, SyncProject

logger = logging.getLogger(__name__)


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


class ConfigManager:
    def __init__(self, appdata_root: Path | None = None) -> None:
        self.appdata_root = appdata_root or get_appdata_root()
        ensure_directory(self.appdata_root)

    @property
    def settings_path(self) -> Path:
        return self.appdata_root / SETTINGS_FILE_NAME

    def load_app_settings(self) -> AppSettings:
        if not self.settings_path.exists():
            settings = AppSettings(onedrive_root=None)
            self.save_app_settings(settings)
            return settings
        return AppSettings.from_dict(json.loads(self.settings_path.read_text(encoding="utf-8")))

    def save_app_settings(self, settings: AppSettings) -> None:
        ensure_directory(self.settings_path.parent)
        self.settings_path.write_text(
            json.dumps(settings.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.info("Saved app settings: %s", self.settings_path)

    def config_path(self, onedrive_root: Path) -> Path:
        return onedrive_root / CONFIG_FILE_NAME

    def initialize_onedrive_root(self, onedrive_root: Path) -> SyncConfig:
        ensure_directory(onedrive_root)
        ensure_directory(onedrive_root / CLOUD_DATA_DIR_NAME)
        config_path = self.config_path(onedrive_root)
        if config_path.exists():
            return self.load_sync_config(onedrive_root)
        config = SyncConfig()
        self.save_sync_config(onedrive_root, config)
        return config

    def load_sync_config(self, onedrive_root: Path) -> SyncConfig:
        config_path = self.config_path(onedrive_root)
        if not config_path.exists():
            return self.initialize_onedrive_root(onedrive_root)
        return SyncConfig.from_dict(json.loads(config_path.read_text(encoding="utf-8")))

    def save_sync_config(self, onedrive_root: Path, config: SyncConfig) -> None:
        config_path = self.config_path(onedrive_root)
        ensure_directory(config_path.parent)
        config_path.write_text(
            json.dumps(config.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.info("Saved sync config: %s", config_path)

    def upsert_project(self, onedrive_root: Path, project: SyncProject, original_id: str | None = None) -> SyncConfig:
        config = self.load_sync_config(onedrive_root)
        existing = config.get_project(project.id)
        if existing and original_id != project.id:
            raise ValueError(f"项目 ID 已存在：{project.id}")

        if original_id:
            config.projects = [entry for entry in config.projects if entry.id != original_id]

        prior = next((entry for entry in config.projects if entry.id == project.id), None)
        if prior:
            config.projects = [project if entry.id == project.id else entry for entry in config.projects]
        else:
            config.projects.append(project)

        self.save_sync_config(onedrive_root, config)
        return config

    def delete_project(self, onedrive_root: Path, project_id: str) -> SyncConfig:
        config = self.load_sync_config(onedrive_root)
        config.projects = [project for project in config.projects if project.id != project_id]
        self.save_sync_config(onedrive_root, config)
        return config
