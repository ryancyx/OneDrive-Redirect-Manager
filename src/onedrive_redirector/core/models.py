from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


@dataclass(slots=True)
class AppSettings:
    onedrive_root: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppSettings":
        return cls(onedrive_root=data.get("onedrive_root"))


@dataclass(slots=True)
class Project:
    id: str
    name: str
    local_path: str
    cloud_relative_path: str
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Project":
        return cls(
            id=data["id"],
            name=data["name"],
            local_path=data.get("local_path", ""),
            cloud_relative_path=data["cloud_relative_path"],
            created_at=data["created_at"],
            updated_at=data.get("updated_at", data["created_at"]),
        )


@dataclass(slots=True)
class ProjectConfig:
    version: int = 1
    projects: list[Project] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "projects": [project.to_dict() for project in self.projects],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProjectConfig":
        return cls(
            version=data.get("version", 1),
            projects=[Project.from_dict(item) for item in data.get("projects", [])],
        )

    def get_project(self, project_id: str) -> Project | None:
        return next((project for project in self.projects if project.id == project_id), None)


class ProjectStatus(str, Enum):
    OK = "OK"
    LOCAL_NOT_CONFIGURED = "LOCAL_NOT_CONFIGURED"
    LOCAL_MISSING = "LOCAL_MISSING"
    CLOUD_MISSING = "CLOUD_MISSING"
    CONFLICT = "CONFLICT"
    LINK_ERROR = "LINK_ERROR"
    ROOT_NOT_SET = "ROOT_NOT_SET"


@dataclass(slots=True)
class StatusResult:
    status: ProjectStatus
    message: str
    local_path: str = ""
    cloud_path: str = ""
