from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


@dataclass(slots=True)
class SyncProject:
    id: str
    name: str
    local_path: str
    cloud_relative_path: str
    enabled: bool
    created_at: str
    last_checked_at: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SyncProject":
        return cls(**data)


@dataclass(slots=True)
class SyncConfig:
    version: int = 1
    projects: list[SyncProject] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "projects": [project.to_dict() for project in self.projects],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SyncConfig":
        return cls(
            version=data.get("version", 1),
            projects=[SyncProject.from_dict(item) for item in data.get("projects", [])],
        )

    def get_project(self, project_id: str) -> SyncProject | None:
        return next((project for project in self.projects if project.id == project_id), None)


@dataclass(slots=True)
class AppSettings:
    onedrive_root: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppSettings":
        return cls(onedrive_root=data.get("onedrive_root"))


class MappingStatus(str, Enum):
    NORMAL = "NORMAL"
    LOCAL_NOT_CONFIGURED = "LOCAL_NOT_CONFIGURED"
    LOCAL_MISSING = "LOCAL_MISSING"
    LOCAL_IS_NOT_LINK = "LOCAL_IS_NOT_LINK"
    CLOUD_MISSING = "CLOUD_MISSING"
    WRONG_LINK_TARGET = "WRONG_LINK_TARGET"
    CONFLICT_BOTH_HAVE_DATA = "CONFLICT_BOTH_HAVE_DATA"
    LOCAL_HAS_DATA_CLOUD_EMPTY = "LOCAL_HAS_DATA_CLOUD_EMPTY"
    LOCAL_EMPTY_CLOUD_HAS_DATA = "LOCAL_EMPTY_CLOUD_HAS_DATA"
    BOTH_EMPTY = "BOTH_EMPTY"
    PERMISSION_ERROR = "PERMISSION_ERROR"
    INVALID_CONFIG = "INVALID_CONFIG"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


@dataclass(slots=True)
class StatusResult:
    status: MappingStatus
    message: str
    details: dict[str, Any] = field(default_factory=dict)
