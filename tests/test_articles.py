"""Article API tests."""

from .conftest import promote_user_to_admin, register_and_login


def _headers_for(client, username: str, email: str, db_session=None, as_admin: bool = False):
    token = register_and_login(client, username, email)
    if as_admin and db_session is not None:
        promote_user_to_admin(db_session, username)
    return {"Authorization": f"Bearer {token}"}


def _create_category(client, headers, name="Tech"):
    response = client.post("/categories", json={"name": name}, headers=headers)
    return response.json()["id"]


def _create_tag(client, headers, name="Python"):
    response = client.post("/tags", json={"name": name}, headers=headers)
    return response.json()["id"]


def test_get_articles_without_token(client):
    response = client.get("/articles")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert isinstance(data["items"], list)


def test_create_article_success(client):
    headers = _headers_for(client, "author1", "author1@example.com")
    category_id = _create_category(client, headers)
    tag_id = _create_tag(client, headers)

    r = client.post(
        "/articles",
        json={
            "title": "My first article",
            "content": "This is enough content for validation.",
            "category_id": category_id,
            "tag_ids": [tag_id],
        },
        headers=headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "My first article"
    assert data["category_id"] == category_id
    assert data["tags"][0]["id"] == tag_id


def test_create_article_rejects_other_users_category(client):
    alice_headers = _headers_for(client, "alice", "alice@example.com")
    bob_headers = _headers_for(client, "bob", "bob@example.com")
    category_id = _create_category(client, alice_headers)

    r = client.post(
        "/articles",
        json={
            "title": "Invalid article",
            "content": "This should fail because the category is not owned.",
            "category_id": category_id,
        },
        headers=bob_headers,
    )
    assert r.status_code == 400


def test_create_article_rejects_other_users_tag(client):
    alice_headers = _headers_for(client, "alice", "alice@example.com")
    bob_headers = _headers_for(client, "bob", "bob@example.com")
    tag_id = _create_tag(client, alice_headers)

    r = client.post(
        "/articles",
        json={
            "title": "Invalid article",
            "content": "This should fail because the tag is not owned.",
            "tag_ids": [tag_id],
        },
        headers=bob_headers,
    )
    assert r.status_code == 400


def test_create_article_without_token_returns_401(client):
    r = client.post(
        "/articles",
        json={
            "title": "Unauthorized article",
            "content": "This request should be rejected without auth.",
        },
    )
    assert r.status_code == 401


def test_update_others_article_returns_403(client):
    token_a = register_and_login(client, "author_a", "a@example.com")
    create_resp = client.post(
        "/articles",
        json={
            "title": "Owner article",
            "content": "This article belongs to author_a and has enough text.",
        },
        headers={"Authorization": f"Bearer {token_a}"},
    )
    article_id = create_resp.json()["id"]

    token_b = register_and_login(client, "user2", "user2@example.com")
    r = client.put(
        f"/articles/{article_id}",
        json={"title": "Hijacked", "content": "Someone else tried to modify this article."},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert r.status_code == 403


def test_admin_can_update_other_users_article(client, db_session):
    owner_headers = _headers_for(client, "owner", "owner@example.com")
    admin_headers = _headers_for(client, "admin", "admin@example.com", db_session, as_admin=True)
    article_id = client.post(
        "/articles",
        json={
            "title": "Owner article",
            "content": "This article belongs to the owner and has enough text.",
        },
        headers=owner_headers,
    ).json()["id"]

    r = client.put(
        f"/articles/{article_id}",
        json={"title": "Admin updated", "content": "Admin is allowed to modify this article."},
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert r.json()["title"] == "Admin updated"


def test_delete_others_article_returns_403(client):
    token_a = register_and_login(client, "author_a", "a@example.com")
    article_id = client.post(
        "/articles",
        json={
            "title": "Owner article",
            "content": "This article belongs to author_a and has enough text.",
        },
        headers={"Authorization": f"Bearer {token_a}"},
    ).json()["id"]

    token_b = register_and_login(client, "user2", "user2@example.com")
    r = client.delete(f"/articles/{article_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert r.status_code == 403


def test_get_articles_list_returns_all_articles(client):
    headers = _headers_for(client, "author1", "author1@example.com")
    client.post(
        "/articles",
        json={"title": "First article", "content": "This is the first article with enough length."},
        headers=headers,
    )
    client.post(
        "/articles",
        json={"title": "Second article", "content": "This is the second article with enough length."},
        headers=headers,
    )

    r = client.get("/articles")
    assert r.status_code == 200
    assert r.json()["total"] == 2


def test_get_article_detail_without_token(client):
    headers = _headers_for(client, "author1", "author1@example.com")
    article_id = client.post(
        "/articles",
        json={"title": "Public article", "content": "This public article has enough content."},
        headers=headers,
    ).json()["id"]

    r = client.get(f"/articles/{article_id}")
    assert r.status_code == 200
    assert r.json()["id"] == article_id


def test_get_article_not_found_returns_404(client):
    r = client.get("/articles/9999")
    assert r.status_code == 404


def test_create_article_invalidates_list_cache(client):
    headers = _headers_for(client, "author1", "author1@example.com")
    assert client.get("/articles").json()["total"] == 0

    client.post(
        "/articles",
        json={"title": "Cached article", "content": "This article should invalidate the list cache."},
        headers=headers,
    )

    assert client.get("/articles").json()["total"] == 1


def test_update_article_invalidates_detail_cache(client):
    headers = _headers_for(client, "author1", "author1@example.com")
    article_id = client.post(
        "/articles",
        json={"title": "Original title", "content": "This is the original article content."},
        headers=headers,
    ).json()["id"]

    assert client.get(f"/articles/{article_id}").json()["title"] == "Original title"

    client.put(
        f"/articles/{article_id}",
        json={"title": "Updated title", "content": "This is the updated article content."},
        headers=headers,
    )

    assert client.get(f"/articles/{article_id}").json()["title"] == "Updated title"


def test_delete_article_invalidates_detail_cache(client):
    headers = _headers_for(client, "author1", "author1@example.com")
    article_id = client.post(
        "/articles",
        json={"title": "Delete me", "content": "This article will be deleted after cache warmup."},
        headers=headers,
    ).json()["id"]

    client.get(f"/articles/{article_id}")
    client.delete(f"/articles/{article_id}", headers=headers)

    assert client.get(f"/articles/{article_id}").status_code == 404
    assert client.get("/articles").json()["total"] == 0


def test_get_article_detail_when_redis_down(client):
    class BrokenRedis:
        async def get(self, key):
            raise ConnectionError("Redis is down")

        async def setex(self, key, ttl, value):
            raise ConnectionError("Redis is down")

        async def delete(self, key):
            raise ConnectionError("Redis is down")

        async def incr(self, key):
            raise ConnectionError("Redis is down")

        async def eval(self, script, num_keys, *args):
            raise ConnectionError("Redis is down")

    from app.core.redis import get_redis

    client.app.dependency_overrides[get_redis] = lambda: BrokenRedis()
    headers = _headers_for(client, "author1", "author1@example.com")
    article_id = client.post(
        "/articles",
        json={"title": "Redis down", "content": "Redis down should still allow DB fallback."},
        headers=headers,
    ).json()["id"]

    r = client.get(f"/articles/{article_id}")
    assert r.status_code == 200
    assert r.json()["title"] == "Redis down"


def test_login_when_redis_down(client):
    class BrokenRedis:
        async def eval(self, script, num_keys, *args):
            raise ConnectionError("Redis is down")

    from app.core.redis import get_redis

    client.app.dependency_overrides[get_redis] = lambda: BrokenRedis()
    client.post(
        "/users",
        json={"username": "testuser", "email": "test@example.com", "password": "secret123"},
    )
    r = client.post("/auth/login", json={"username": "testuser", "password": "secret123"})
    assert r.status_code == 200
