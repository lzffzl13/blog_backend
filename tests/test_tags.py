"""Tag API tests for blog-style ownership."""

from .conftest import promote_user_to_admin, register_and_login


def _headers_for(client, username: str, email: str):
    token = register_and_login(client, username, email)
    return {"Authorization": f"Bearer {token}"}


def _admin_headers_for(client, db_session, username: str, email: str):
    headers = _headers_for(client, username, email)
    promote_user_to_admin(db_session, username)
    return headers


def test_user_can_create_own_tag(client):
    headers = _headers_for(client, "alice", "alice@example.com")
    r = client.post("/tags", json={"name": "Python"}, headers=headers)
    assert r.status_code == 201
    assert r.json()["name"] == "Python"


def test_tag_names_only_need_to_be_unique_per_owner(client):
    headers_a = _headers_for(client, "alice", "alice@example.com")
    headers_b = _headers_for(client, "bob", "bob@example.com")

    assert client.post("/tags", json={"name": "Python"}, headers=headers_a).status_code == 201
    assert client.post("/tags", json={"name": "Python"}, headers=headers_b).status_code == 201


def test_duplicate_tag_for_same_owner_returns_409(client):
    headers = _headers_for(client, "alice", "alice@example.com")
    client.post("/tags", json={"name": "Python"}, headers=headers)
    r = client.post("/tags", json={"name": "Python"}, headers=headers)
    assert r.status_code == 409


def test_user_only_sees_own_tags(client):
    headers_a = _headers_for(client, "alice", "alice@example.com")
    headers_b = _headers_for(client, "bob", "bob@example.com")

    client.post("/tags", json={"name": "Python"}, headers=headers_a)
    client.post("/tags", json={"name": "JavaScript"}, headers=headers_b)

    r = client.get("/tags", headers=headers_a)
    assert r.status_code == 200
    names = [item["name"] for item in r.json()]
    assert names == ["Python"]


def test_admin_sees_all_tags(client, db_session):
    headers_a = _headers_for(client, "alice", "alice@example.com")
    headers_b = _headers_for(client, "bob", "bob@example.com")
    admin_headers = _admin_headers_for(client, db_session, "admin", "admin@example.com")

    client.post("/tags", json={"name": "Python"}, headers=headers_a)
    client.post("/tags", json={"name": "JavaScript"}, headers=headers_b)

    r = client.get("/tags", headers=admin_headers)
    assert r.status_code == 200
    names = sorted(item["name"] for item in r.json())
    assert names == ["JavaScript", "Python"]


def test_user_cannot_read_other_users_tag(client):
    headers_a = _headers_for(client, "alice", "alice@example.com")
    headers_b = _headers_for(client, "bob", "bob@example.com")
    tag_id = client.post("/tags", json={"name": "Python"}, headers=headers_a).json()["id"]

    r = client.get(f"/tags/{tag_id}", headers=headers_b)
    assert r.status_code == 403


def test_user_can_delete_own_tag(client):
    headers = _headers_for(client, "alice", "alice@example.com")
    tag_id = client.post("/tags", json={"name": "Python"}, headers=headers).json()["id"]

    r = client.delete(f"/tags/{tag_id}", headers=headers)
    assert r.status_code == 204


def test_user_cannot_delete_other_users_tag(client):
    headers_a = _headers_for(client, "alice", "alice@example.com")
    headers_b = _headers_for(client, "bob", "bob@example.com")
    tag_id = client.post("/tags", json={"name": "Python"}, headers=headers_a).json()["id"]

    r = client.delete(f"/tags/{tag_id}", headers=headers_b)
    assert r.status_code == 403


def test_admin_can_delete_any_tag(client, db_session):
    headers_a = _headers_for(client, "alice", "alice@example.com")
    admin_headers = _admin_headers_for(client, db_session, "admin", "admin@example.com")
    tag_id = client.post("/tags", json={"name": "Python"}, headers=headers_a).json()["id"]

    r = client.delete(f"/tags/{tag_id}", headers=admin_headers)
    assert r.status_code == 204
