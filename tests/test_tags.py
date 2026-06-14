"""Tag API tests."""

from .conftest import promote_user_to_admin, register_and_login


def _admin_headers(client, db_session, username: str = "admin_user"):
    token = register_and_login(client, username, f"{username}@example.com")
    promote_user_to_admin(db_session, username)
    return {"Authorization": f"Bearer {token}"}


def test_create_tag_requires_admin(client):
    token = register_and_login(client, "regular_user", "regular@example.com")
    r = client.post(
        "/tags",
        json={"name": "Python"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


def test_create_tag_success(client, db_session):
    r = client.post(
        "/tags",
        json={"name": "Python"},
        headers=_admin_headers(client, db_session),
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Python"
    assert "id" in data


def test_create_duplicate_tag_returns_409(client, db_session):
    headers = _admin_headers(client, db_session)
    client.post("/tags", json={"name": "Python"}, headers=headers)
    r = client.post("/tags", json={"name": "Python"}, headers=headers)
    assert r.status_code == 409


def test_get_tags_list(client, db_session):
    headers = _admin_headers(client, db_session)
    client.post("/tags", json={"name": "Python"}, headers=headers)
    client.post("/tags", json={"name": "JavaScript"}, headers=headers)

    r = client.get("/tags")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    names = [t["name"] for t in data]
    assert "Python" in names
    assert "JavaScript" in names


def test_get_tag_by_id(client, db_session):
    create_resp = client.post(
        "/tags",
        json={"name": "Python"},
        headers=_admin_headers(client, db_session),
    )
    tag_id = create_resp.json()["id"]

    r = client.get(f"/tags/{tag_id}")
    assert r.status_code == 200
    assert r.json()["name"] == "Python"


def test_get_tag_not_found_returns_404(client):
    r = client.get("/tags/9999")
    assert r.status_code == 404


def test_delete_tag_success(client, db_session):
    headers = _admin_headers(client, db_session)
    create_resp = client.post("/tags", json={"name": "Python"}, headers=headers)
    tag_id = create_resp.json()["id"]

    r = client.delete(f"/tags/{tag_id}", headers=headers)
    assert r.status_code == 204

    r_get = client.get(f"/tags/{tag_id}")
    assert r_get.status_code == 404


def test_delete_tag_requires_admin(client, db_session):
    headers = _admin_headers(client, db_session)
    create_resp = client.post("/tags", json={"name": "Python"}, headers=headers)
    tag_id = create_resp.json()["id"]

    token = register_and_login(client, "deleter", "deleter@example.com")
    r = client.delete(
        f"/tags/{tag_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


def test_delete_tag_not_found_returns_404(client, db_session):
    r = client.delete("/tags/9999", headers=_admin_headers(client, db_session))
    assert r.status_code == 404
