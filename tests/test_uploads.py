from pathlib import Path

from app.core.config import settings
from .conftest import register_and_login


def test_upload_file_requires_auth(client):
    response = client.post(
        "/uploads",
        files={"file": ("note.txt", b"hello world", "text/plain")},
    )
    assert response.status_code == 401


def test_upload_text_file_success(client, tmp_path, monkeypatch):
    monkeypatch.setattr("app.api.upload.settings.UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr("app.services.file_storage.Path", Path)

    token = register_and_login(client, "uploader", "uploader@example.com")
    response = client.post(
        "/uploads",
        files={"file": ("note.txt", b"hello world", "text/plain")},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["original_filename"] == "note.txt"
    assert data["content_type"] == "text/plain"
    assert data["size"] == 11
    stored_path = tmp_path / data["filename"]
    assert stored_path.exists()
    assert stored_path.read_bytes() == b"hello world"


def test_upload_rejects_unsupported_type(client, tmp_path, monkeypatch):
    monkeypatch.setattr("app.api.upload.settings.UPLOAD_DIR", str(tmp_path))

    token = register_and_login(client, "uploader2", "uploader2@example.com")
    response = client.post(
        "/uploads",
        files={"file": ("data.exe", b"binary", "application/octet-stream")},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 415


def test_upload_rejects_large_file(client, tmp_path, monkeypatch):
    monkeypatch.setattr("app.api.upload.settings.UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr("app.api.upload.settings.MAX_UPLOAD_SIZE_BYTES", 5)

    token = register_and_login(client, "uploader3", "uploader3@example.com")
    response = client.post(
        "/uploads",
        files={"file": ("big.txt", b"123456", "text/plain")},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 413
    assert not any(tmp_path.iterdir())
