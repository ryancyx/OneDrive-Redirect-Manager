from pathlib import Path

import pytest

from onedrive_redirector.core.path_utils import (
    PathValidationError,
    cloud_relative_to_absolute,
    normalized_abs_path,
    validate_cloud_relative_path,
    validate_local_path,
)


def test_validate_cloud_relative_path_accepts_data_path() -> None:
    assert validate_cloud_relative_path("data/project-a") == "data/project-a"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "C:/abs/path",
        "/data/project-a",
        "../data/project-a",
        "data/../project-a",
        "config/project-a",
        "data",
    ],
)
def test_validate_cloud_relative_path_rejects_invalid_values(value: str) -> None:
    with pytest.raises(PathValidationError):
        validate_cloud_relative_path(value)


def test_local_path_outside_onedrive_root_is_allowed(tmp_path: Path) -> None:
    root = tmp_path / "ODR_CloudTest" / "OneDriveRedirector"
    cloud = cloud_relative_to_absolute(root, "data/cloud-empty")
    local = tmp_path / "ODR_LocalTest" / "LocalA"
    assert validate_local_path(local, root, cloud) == normalized_abs_path(local)


def test_local_path_inside_onedrive_root_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "ODR_CloudTest" / "OneDriveRedirector"
    cloud = cloud_relative_to_absolute(root, "data/cloud-empty")
    local = root / "data"
    with pytest.raises(PathValidationError):
        validate_local_path(local, root, cloud)


def test_local_path_equal_to_onedrive_root_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "ODR_CloudTest" / "OneDriveRedirector"
    cloud = cloud_relative_to_absolute(root, "data/cloud-empty")
    with pytest.raises(PathValidationError):
        validate_local_path(root, root, cloud)


def test_local_path_inside_cloud_target_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "ODR_CloudTest" / "OneDriveRedirector"
    cloud = cloud_relative_to_absolute(root, "data/cloud-empty")
    local = cloud / "nested"
    with pytest.raises(PathValidationError):
        validate_local_path(local, root, cloud)


def test_sibling_directory_is_allowed(tmp_path: Path) -> None:
    root = tmp_path / "cloud" / "OneDriveRedirector"
    cloud = cloud_relative_to_absolute(root, "data/project")
    local = tmp_path / "cloud" / "LocalSibling"
    assert validate_local_path(local, root, cloud) == normalized_abs_path(local)


def test_nonexistent_path_is_not_misresolved(tmp_path: Path) -> None:
    root = tmp_path / "cloud" / "OneDriveRedirector"
    cloud = cloud_relative_to_absolute(root, "data/project")
    local = tmp_path / "missing-parent" / "missing-child"
    result = validate_local_path(local, root, cloud)
    assert str(result).endswith(str(Path("missing-parent") / "missing-child"))
