from pathlib import Path

import pytest

from onedrive_redirector.path_utils import (
    PathValidationError,
    is_same_or_inside_path,
    validate_cloud_relative_path,
    validate_local_path,
)


def test_cloud_relative_path_must_stay_under_data() -> None:
    assert validate_cloud_relative_path("data/fireaxe") == "data/fireaxe"


@pytest.mark.parametrize("value", ["", "D:/a", "../x", "/x", "configs/x", "data"])
def test_invalid_cloud_relative_path_is_rejected(value: str) -> None:
    with pytest.raises(PathValidationError):
        validate_cloud_relative_path(value)


def test_local_path_outside_onedrive_root_is_allowed() -> None:
    validate_local_path(
        Path("D:/ODR_LocalTest/LocalA"),
        Path("D:/ODR_CloudTest/OneDriveRedirector"),
        Path("D:/ODR_CloudTest/OneDriveRedirector/data/cloud-empty"),
    )


def test_local_path_inside_onedrive_root_is_rejected() -> None:
    with pytest.raises(PathValidationError):
        validate_local_path(
            Path("D:/ODR_CloudTest/OneDriveRedirector/data"),
            Path("D:/ODR_CloudTest/OneDriveRedirector"),
            Path("D:/ODR_CloudTest/OneDriveRedirector/data/cloud-empty"),
        )


def test_local_path_equal_to_onedrive_root_is_rejected() -> None:
    with pytest.raises(PathValidationError):
        validate_local_path(
            Path("D:/ODR_CloudTest/OneDriveRedirector"),
            Path("D:/ODR_CloudTest/OneDriveRedirector"),
            Path("D:/ODR_CloudTest/OneDriveRedirector/data/cloud-empty"),
        )


def test_cloud_target_inside_path_is_rejected() -> None:
    with pytest.raises(PathValidationError):
        validate_local_path(
            Path("D:/ODR_CloudTest/OneDriveRedirector/data/cloud-empty/sub"),
            Path("D:/ODR_CloudTest/OneDriveRedirector"),
            Path("D:/ODR_CloudTest/OneDriveRedirector/data/cloud-empty"),
        )


def test_same_drive_but_not_nested_is_allowed() -> None:
    validate_local_path(
        Path("D:/Projects/LocalA"),
        Path("D:/ODR_CloudTest/OneDriveRedirector"),
        Path("D:/ODR_CloudTest/OneDriveRedirector/data/cloud-empty"),
    )


def test_sibling_directory_is_allowed() -> None:
    validate_local_path(
        Path("D:/ODR_CloudTest/LocalSibling"),
        Path("D:/ODR_CloudTest/OneDriveRedirector"),
        Path("D:/ODR_CloudTest/OneDriveRedirector/data/cloud-empty"),
    )


@pytest.mark.parametrize("value", [Path("C:/"), Path("C:/Windows"), Path("C:/Program Files"), Path("C:/Users")])
def test_dangerous_system_directory_is_rejected(value: Path) -> None:
    with pytest.raises(PathValidationError):
        validate_local_path(value, Path("D:/ODR_CloudTest/OneDriveRedirector"), Path("D:/ODR_CloudTest/OneDriveRedirector/data/a"))


def test_path_containment_direction_is_correct() -> None:
    assert is_same_or_inside_path(Path("D:/a/b"), Path("D:/a"))
    assert not is_same_or_inside_path(Path("D:/a"), Path("D:/a/b"))
