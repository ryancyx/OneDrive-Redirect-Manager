from pathlib import Path

import pytest

from onedrive_redirector.path_utils import PathValidationError, validate_cloud_relative_path, validate_local_path


def test_validate_cloud_relative_path_accepts_valid_value() -> None:
    assert validate_cloud_relative_path("data/fireaxe-backup") == "data/fireaxe-backup"


@pytest.mark.parametrize(
    "value",
    [
        "D:/OneDrive/data/test",
        r"C:\Users\Ryan\OneDrive\data\test",
        "../data/test",
        "/data/test",
        ".",
        "configs/test",
        "",
    ],
)
def test_validate_cloud_relative_path_rejects_invalid_value(value: str) -> None:
    with pytest.raises(PathValidationError):
        validate_cloud_relative_path(value)


def test_validate_local_path_rejects_dangerous_paths() -> None:
    with pytest.raises(PathValidationError):
        validate_local_path(Path("C:/"))

    with pytest.raises(PathValidationError):
        validate_local_path(Path("C:/Windows"))


def test_validate_local_path_rejects_onedrive_and_library_root() -> None:
    onedrive_root = Path("D:/Users/Test/OneDrive")
    app_root = onedrive_root / "OneDriveRedirector"

    with pytest.raises(PathValidationError):
        validate_local_path(onedrive_root, one_drive_root=onedrive_root, library_root=app_root)

    with pytest.raises(PathValidationError):
        validate_local_path(app_root, one_drive_root=onedrive_root, library_root=app_root)


def test_validate_local_path_outside_onedrive_root_is_allowed() -> None:
    onedrive_root = Path("D:/ODR_CloudTest/OneDriveRedirector")
    local_path = Path("D:/ODR_LocalTest/LocalA")
    cloud_target = onedrive_root / "data" / "cloud-empty"

    validate_local_path(local_path, one_drive_root=onedrive_root, cloud_target_path=cloud_target)


def test_validate_local_path_inside_onedrive_root_is_rejected() -> None:
    onedrive_root = Path("D:/ODR_CloudTest/OneDriveRedirector")
    local_path = onedrive_root / "data"
    cloud_target = onedrive_root / "data" / "cloud-empty"

    with pytest.raises(PathValidationError):
        validate_local_path(local_path, one_drive_root=onedrive_root, cloud_target_path=cloud_target)


def test_validate_local_path_equal_to_onedrive_root_is_rejected() -> None:
    onedrive_root = Path("D:/ODR_CloudTest/OneDriveRedirector")
    cloud_target = onedrive_root / "data" / "cloud-empty"

    with pytest.raises(PathValidationError):
        validate_local_path(onedrive_root, one_drive_root=onedrive_root, cloud_target_path=cloud_target)
