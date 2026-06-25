"""用户相关测试 - 覆盖注册、个人信息、修改密码、删除账号等场景"""

from .conftest import register_and_login


def test_register_duplicate_returns_409(client):
    """重复注册同一用户应该返回409冲突"""
    payload = {
        "username": "duplicate_user",
        "email": "dup@example.com",
        "password": "secret123",
    }
    r1 = client.post("/users", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/users", json=payload)
    assert r2.status_code == 409
    assert isinstance(r2.json()["detail"], str)
    assert r2.json()["detail"]


def test_get_me_with_token(client):
    """带 token 获取个人信息，返回 200，username 和 email 正确"""
    token = register_and_login(client, "testuser", "testuser@example.com")

    r = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert data["role"] == "user"
    assert "id" in data


def test_get_me_without_token_returns_401(client):
    """不带 token 获取个人信息，返回 401"""
    r = client.get("/users/me")
    assert r.status_code == 401


def test_change_password_success(client):
    """正确修改密码，返回 200；旧密码失效，新密码可用"""
    client.post(
        "/users",
        json={
            "username": "pwuser",
            "email": "pwuser@example.com",
            "password": "oldpass123",
        },
    )
    login_resp = client.post(
        "/auth/login",
        json={"username": "pwuser", "password": "oldpass123"},
    )
    token = login_resp.json()["access_token"]

    r = client.put(
        "/users/me/password",
        json={"old_password": "oldpass123", "new_password": "newpass123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200

    r_old = client.post(
        "/auth/login",
        json={"username": "pwuser", "password": "oldpass123"},
    )
    assert r_old.status_code == 401

    r_new = client.post(
        "/auth/login",
        json={"username": "pwuser", "password": "newpass123"},
    )
    assert r_new.status_code == 200
    assert "access_token" in r_new.json()


def test_change_password_wrong_old_password_returns_400(client):
    """旧密码错误时返回 400"""
    token = register_and_login(client, "pwuser2", "pwuser2@example.com", "oldpass123")

    r = client.put(
        "/users/me/password",
        json={"old_password": "wrongpass", "new_password": "newpass123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 400
    assert isinstance(r.json()["detail"], str)
    assert r.json()["detail"]


def test_delete_me_success(client):
    """带 token 删除账号，返回 204,删除后用同一 token 访问返回 401"""
    token = register_and_login(client, "deluser", "deluser@example.com")
    client.post(
        "/articles",
        json={"title": "to be deleted", "content": "gone with user"},
        headers={"Authorization": f"Bearer {token}"},
    )

    r_article = client.get("/articles/1")
    assert r_article.status_code == 200

    r = client.delete("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 204

    r_article2 = client.get("/articles/1")
    assert r_article2.status_code == 404

    r2 = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 401


def test_delete_me_without_token_returns_401(client):
    """不带 token 删除账号，返回 401"""
    r = client.delete("/users/me")
    assert r.status_code == 401
