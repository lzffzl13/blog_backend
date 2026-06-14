"""Category API tests."""

from .conftest import promote_user_to_admin, register_and_login


def _admin_headers(client, db_session, username: str = "admin_user"):
    token = register_and_login(client, username, f"{username}@example.com")
    promote_user_to_admin(db_session, username)
    return {"Authorization": f"Bearer {token}"}


def test_create_category_requires_admin(client):
    token = register_and_login(client, "regular_user", "regular@example.com")
    r = client.post(
        "/categories",
        json={"name": "Tech", "description": "Tech posts"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


def test_create_category_success_for_admin(client, db_session):
    r = client.post(
        "/categories",
        json={"name": "Tech", "description": "Tech posts"},
        headers=_admin_headers(client, db_session),
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Tech"
    assert data["description"] == "Tech posts"
    assert "id" in data


def test_create_duplicate_category_returns_409(client, db_session):
    headers = _admin_headers(client, db_session)
    client.post("/categories", json={"name": "Tech"}, headers=headers)
    r = client.post("/categories", json={"name": "Tech"}, headers=headers)
    assert r.status_code == 409


def test_get_categories_list(client, db_session):
    headers = _admin_headers(client, db_session)
    client.post("/categories", json={"name": "Tech"}, headers=headers)
    client.post("/categories", json={"name": "Life"}, headers=headers)

    r = client.get("/categories")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    names = [c["name"] for c in data]
    assert "Tech" in names
    assert "Life" in names


def test_get_category_by_id(client, db_session):
    create_resp = client.post(
        "/categories",
        json={"name": "Tech"},
        headers=_admin_headers(client, db_session),
    )
    category_id = create_resp.json()["id"]

    r = client.get(f"/categories/{category_id}")
    assert r.status_code == 200
    assert r.json()["name"] == "Tech"


def test_get_category_not_found_returns_404(client):
    r = client.get("/categories/9999")
    assert r.status_code == 404


def test_update_category_requires_admin(client, db_session):
    headers = _admin_headers(client, db_session)
    create_resp = client.post("/categories", json={"name": "Tech"}, headers=headers)
    category_id = create_resp.json()["id"]

    token = register_and_login(client, "editor", "editor@example.com")
    r = client.put(
        f"/categories/{category_id}",
        json={"name": "Science"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


def test_update_category_success(client, db_session):
    headers = _admin_headers(client, db_session)
    create_resp = client.post("/categories", json={"name": "Tech"}, headers=headers)
    category_id = create_resp.json()["id"]

    r = client.put(
        f"/categories/{category_id}",
        json={"name": "Science", "description": "Science posts"},
        headers=headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Science"
    assert data["description"] == "Science posts"


def test_update_category_not_found_returns_404(client, db_session):
    r = client.put(
        "/categories/9999",
        json={"name": "Science"},
        headers=_admin_headers(client, db_session),
    )
    assert r.status_code == 404


def test_delete_category_success(client, db_session):
    headers = _admin_headers(client, db_session)
    create_resp = client.post("/categories", json={"name": "Tech"}, headers=headers)
    category_id = create_resp.json()["id"]

    r = client.delete(f"/categories/{category_id}", headers=headers)
    assert r.status_code == 204

    r_get = client.get(f"/categories/{category_id}")
    assert r_get.status_code == 404


def test_delete_category_requires_admin(client, db_session):
    headers = _admin_headers(client, db_session)
    create_resp = client.post("/categories", json={"name": "Tech"}, headers=headers)
    category_id = create_resp.json()["id"]

    token = register_and_login(client, "deleter", "deleter@example.com")
    r = client.delete(
        f"/categories/{category_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


def test_delete_category_not_found_returns_404(client, db_session):
    r = client.delete("/categories/9999", headers=_admin_headers(client, db_session))
    assert r.status_code == 404
