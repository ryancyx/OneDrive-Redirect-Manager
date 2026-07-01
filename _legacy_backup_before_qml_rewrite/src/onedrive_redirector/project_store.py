from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .models import Project, ProjectConfig
from .path_utils import validate_cloud_relative_path


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


class ProjectStore:
    def __init__(self, onedrive_root: Path) -> None:
        self.onedrive_root = Path(onedrive_root)

    @property
    def config_path(self) -> Path:
        return self.onedrive_root / "config.json"

    @property
    def data_dir(self) -> Path:
        return self.onedrive_root / "data"

    @property
    def backups_dir(self) -> Path:
        return self.onedrive_root / "backups"

    def ensure_root(self) -> None:
        self.onedrive_root.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        if not self.config_path.exists():
            self.config_path.write_text(
                json.dumps(ProjectConfig().to_dict(), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

    def load(self) -> ProjectConfig:
        self.ensure_root()
        data = json.loads(self.config_path.read_text(encoding="utf-8"))
        return ProjectConfig.from_dict(data)

    def save(self, config: ProjectConfig) -> None:
        self.ensure_root()
        self.config_path.write_text(
            json.dumps(config.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def add_project(self, project: Project) -> ProjectConfig:
        validate_cloud_relative_path(project.cloud_relative_path)
        config = self.load()
        if config.get_project(project.id):
            raise ValueError(f"项目 ID 已存在：{project.id}")
        config.projects.append(project)
        self.save(config)
        return config

    def update_project(self, original_id: str, project: Project) -> ProjectConfig:
        validate_cloud_relative_path(project.cloud_relative_path)
        config = self.load()
        original = config.get_project(original_id)
        if not original:
            raise ValueError(f"未找到项目：{original_id}")
        duplicate = config.get_project(project.id)
        if duplicate and duplicate.id != original_id:
            raise ValueError(f"项目 ID 已存在：{project.id}")
        config.projects = [entry for entry in config.projects if entry.id != original_id]
        config.projects.append(project)
        config.projects.sort(key=lambda item: item.id.lower())
        self.save(config)
        return config

    def delete_project(self, project_id: str) -> ProjectConfig:
        config = self.load()
        config.projects = [project for project in config.projects if project.id != project_id]
        self.save(config)
        return config
