from pathlib import Path

import pytest

import onedrive_redirector.core.project_service as project_service_module
from onedrive_redirector.core.models import Project
from onedrive_redirector.core.project_service import ProjectService
from onedrive_redirector.core.project_store import ProjectStore
from onedrive_redirector.core.settings_store import SettingsStore


def make_service(tmp_path: Path) -> tuple[ProjectService, Path]:
    settings_store = SettingsStore(tmp_path / "appdata")
    root = tmp_path / "OneDriveRedirector"
    service = ProjectService(settings_store)
    service.save_onedrive_root(str(root))
    return service, root


def add_project(
    root: Path,
    *,
    project_id: str = "conflict-test",
    local_path: str | None = None,
    cloud_relative_path: str = "data/cloud-conflict",
) -> Project:
    store = ProjectStore(root)
    project = Project(
        id=project_id,
        name="Conflict Test",
        local_path=local_path or str(root.parent / "ODR_LocalTest" / "LocalConflict"),
        cloud_relative_path=cloud_relative_path,
        created_at="2026-07-02T10:00:00+08:00",
        updated_at="2026-07-02T10:00:00+08:00",
    )
    store.add_project(project)
    return project


def test_delete_project_without_delete_cloud_or_local_link_removes_config_only(tmp_path: Path) -> None:
    service, root = make_service(tmp_path)
    local_parent = tmp_path / "ODR_LocalTest"
    local_parent.mkdir()
    local_link = local_parent / "LocalConflict"
    local_link.mkdir()
    add_project(root, local_path=str(local_link))
    cloud_target = root / "data" / "cloud-conflict"
    cloud_target.mkdir(parents=True)
    (cloud_target / "cloud.txt").write_text("cloud", encoding="utf-8")

    service.delete_project("conflict-test", False, False)

    assert ProjectStore(root).load().get_project("conflict-test") is None
    assert cloud_target.exists()
    assert local_link.exists()


def test_delete_project_with_delete_cloud_and_local_link_removes_both(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    service, root = make_service(tmp_path)
    local_parent = tmp_path / "ODR_LocalTest"
    local_parent.mkdir()
    local_link = local_parent / "LocalConflict"
    local_link.mkdir()
    add_project(root, local_path=str(local_link))
    cloud_target = root / "data" / "cloud-conflict"
    cloud_target.mkdir(parents=True)
    (cloud_target / "cloud.txt").write_text("cloud", encoding="utf-8")
    other_project_dir = root / "data" / "other-project"
    other_project_dir.mkdir(parents=True)
    (other_project_dir / "keep.txt").write_text("keep", encoding="utf-8")
    backup_dir = local_parent / "LocalConflict_backup"
    backup_dir.mkdir()

    monkeypatch.setattr(project_service_module, "is_junction_or_reparse_point", lambda path: True)

    def fake_remove_junction(path: Path) -> None:
        Path(path).rmdir()

    monkeypatch.setattr(project_service_module, "remove_junction", fake_remove_junction)

    service.delete_project("conflict-test", True, True)

    assert ProjectStore(root).load().get_project("conflict-test") is None
    assert not cloud_target.exists()
    assert not local_link.exists()
    assert local_parent.exists()
    assert backup_dir.exists()
    assert other_project_dir.exists()


def test_delete_project_with_delete_both_deletes_local_link_before_cloud(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    service, root = make_service(tmp_path)
    local_parent = tmp_path / "ODR_LocalTest"
    local_parent.mkdir()
    local_link = local_parent / "DeleteBothTest"
    local_link.mkdir()
    add_project(
        root,
        project_id="delete-both-test",
        local_path=str(local_link),
        cloud_relative_path="data/delete-both-test",
    )
    cloud_target = root / "data" / "delete-both-test"
    cloud_target.mkdir(parents=True)
    (cloud_target / "cloud.txt").write_text("cloud", encoding="utf-8")

    monkeypatch.setattr(project_service_module, "is_junction_or_reparse_point", lambda path: True)
    events: list[str] = []

    def fake_remove_junction(path: Path) -> None:
        events.append("remove_junction")
        Path(path).rmdir()

    def fake_remove_tree(path: Path) -> None:
        events.append("remove_tree")
        import shutil
        shutil.rmtree(path)

    monkeypatch.setattr(project_service_module, "remove_junction", fake_remove_junction)
    monkeypatch.setattr(project_service_module, "remove_tree", fake_remove_tree)

    service.delete_project("delete-both-test", True, True)

    assert events == ["remove_junction", "remove_tree"]
    assert ProjectStore(root).load().get_project("delete-both-test") is None
    assert not local_link.exists()
    assert not cloud_target.exists()
    assert local_parent.exists()


def test_delete_project_with_delete_local_link_only_removes_link_and_keeps_cloud(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    service, root = make_service(tmp_path)
    local_parent = tmp_path / "ODR_LocalTest"
    local_parent.mkdir()
    local_link = local_parent / "LocalConflict"
    local_link.mkdir()
    add_project(root, local_path=str(local_link))
    cloud_target = root / "data" / "cloud-conflict"
    cloud_target.mkdir(parents=True)

    monkeypatch.setattr(project_service_module, "is_junction_or_reparse_point", lambda path: True)

    def fake_remove_junction(path: Path) -> None:
        Path(path).rmdir()

    monkeypatch.setattr(project_service_module, "remove_junction", fake_remove_junction)

    service.delete_project("conflict-test", False, True)

    assert ProjectStore(root).load().get_project("conflict-test") is None
    assert not local_link.exists()
    assert local_parent.exists()
    assert cloud_target.exists()


def test_delete_local_link_rejects_ordinary_directory_and_preserves_contents(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    service, root = make_service(tmp_path)
    local_dir = tmp_path / "ODR_LocalTest" / "LocalConflict"
    local_dir.mkdir(parents=True)
    (local_dir / "local.txt").write_text("keep", encoding="utf-8")
    add_project(root, local_path=str(local_dir))
    cloud_target = root / "data" / "cloud-conflict"
    cloud_target.mkdir(parents=True)

    monkeypatch.setattr(project_service_module, "is_junction_or_reparse_point", lambda path: False)

    with pytest.raises(RuntimeError, match="本地路径不是链接"):
        service.delete_project("conflict-test", False, True)

    assert ProjectStore(root).load().get_project("conflict-test") is not None
    assert local_dir.exists()
    assert (local_dir / "local.txt").exists()
    assert cloud_target.exists()


def test_delete_cloud_rejects_onedrive_root(tmp_path: Path) -> None:
    service, root = make_service(tmp_path)
    with pytest.raises(Exception):
        service._get_safe_cloud_delete_path(root, "")


def test_delete_cloud_rejects_data_root(tmp_path: Path) -> None:
    service, root = make_service(tmp_path)
    with pytest.raises(Exception):
        service._get_safe_cloud_delete_path(root, "data")


def test_delete_cloud_rejects_parent_escape(tmp_path: Path) -> None:
    service, root = make_service(tmp_path)
    with pytest.raises(Exception):
        service._get_safe_cloud_delete_path(root, "data/../../escape")
