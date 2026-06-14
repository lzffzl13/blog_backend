"""Category API tests for blog-style ownership."""

from .conftest import promote_user_to_admin, register_and_login


def _headers_for(client, username: str, email: str):
    token = register_and_login(client, username, email)
    return {"Authorization": f"Bearer {token}"}


def _admin_headers_for(client, db_session, username: str, email: str):
    headers = _headers_for(client, username, email)
    promote_user_to_admin(db_session, username)
    return headers


def test_user_can_create_own_category(client):
    headers = _headers_for(client, "alice", "alice@example.com")
    r = client.post("/categories", json={"name": "Tech", "description": "Tech posts"}, headers=headers)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Tech"
    assert data["owner_id"] > 0


def test_category_names_only_need_to_be_unique_per_owner(client):
    headers_a = _headers_for(client, "alice", "alice@example.com")
    headers_b = _headers_for(client, "bob", "bob@example.com")

    assert client.post("/categories", json={"name": "Tech"}, headers=headers_a).status_code == 201
    assert client.post("/categories", json={"name": "Tech"}, headers=headers_b).status_code == 201


def test_duplicate_category_for_same_owner_returns_409(client):
    headers = _headers_for(client, "alice", "alice@example.com")
    client.post("/categories", json={"name": "Tech"}, headers=headers)
    r = client.post("/categories", json={"name": "Tech"}, headers=headers)
    assert r.status_code == 409


def test_user_only_sees_own_categories(client):
    headers_a = _headers_for(client, "alice", "alice@example.com")
    headers_b = _headers_for(client, "bob", "bob@example.com")

    client.post("/categories", json={"name": "Tech"}, headers=headers_a)
    client.post("/categories", json={"name": "Life"}, headers=headers_b)

    r = client.get("/categories", headers=headers_a)
    assert r.status_code == 200
    names = [item["name"] for item in r.json()]
    assert names == ["Tech"]


def test_admin_sees_all_categories(client, db_session):
    headers_a = _headers_for(client, "alice", "alice@example.com")
    headers_b = _headers_for(client, "bob", "bob@example.com")
    admin_headers = _admin_headers_for(client, db_session, "admin", "admin@example.com")

    client.post("/categories", json={"name": "Tech"}, headers=headers_a)
    client.post("/categories", json={"name": "Life"}, headers=headers_b)

    r = client.get("/categories", headers=admin_headers)
    assert r.status_code == 200
    names = sorted(item["name"] for item in r.json())
    assert names == ["Life", "Tech"]


def test_user_cannot_read_other_users_category(client):
    headers_a = _headers_for(client, "alice", "alice@example.com")
    headers_b = _headers_for(client, "bob", "bob@example.com")
    category_id = client.post("/categories", json={"name": "Tech"}, headers=headers_a).json()["id"]

    r = client.get(f"/categories/{category_id}", headers=headers_b)
    assert r.status_code == 403


def test_user_can_update_own_category(client):
    headers = _headers_for(client, "alice", "alice@example.com")
    category_id = client.post("/categories", json={"name": "Tech"}, headers=headers).json()["id"]

    r = client.put(
        f"/categories/{category_id}",
        json={"name": "Science", "description": "Science posts"},
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Science"


def test_user_cannot_update_other_users_category(client):
    headers_a = _headers_for(client, "alice", "alice@example.com")
    headers_b = _headers_for(client, "bob", "bob@example.com")
    category_id = client.post("/categories", json={"name": "Tech"}, headers=headers_a).json()["id"]

    r = client.put(f"/categories/{category_id}", json={"name": "Science"}, headers=headers_b)
    assert r.status_code == 403


def test_admin_can_update_any_category(client, db_session):
    headers_a = _headers_for(client, "alice", "alice@example.com")
    admin_headers = _admin_headers_for(client, db_session, "admin", "admin@example.com")
    category_id = client.post("/categories", json={"name": "Tech"}, headers=headers_a).json()["id"]

    r = client.put(f"/categories/{category_id}", json={"name": "Science"}, headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["name"] == "Science"


def test_user_can_delete_own_category(client):
    headers = _headers_for(client, "alice", "alice@example.com")
    category_id = client.post("/categories", json={"name": "Tech"}, headers=headers).json()["id"]

    r = client.delete(f"/categories/{category_id}", headers=headers)
    assert r.status_code == 204


def test_user_cannot_delete_other_users_category(client):
    headers_a = _headers_for(client, "alice", "alice@example.com")
    headers_b = _headers_for(client, "bob", "bob@example.com")
    category_id = client.post("/categories", json={"name": "Tech"}, headers=headers_a).json()["id"]

    r = client.delete(f"/categories/{category_id}", headers=headers_b)
    assert r.status_code == 403
