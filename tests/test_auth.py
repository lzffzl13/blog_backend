"""认证相关测试 - 覆盖注册、登录、刷新 token 等场景"""

import time


def _register_and_login(client, username: str = "testuser"):
    client.post(
        "/users",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "secret123",
        },
    )
    return client.post(
        "/auth/login",
        json={
            "username": username,
            "password": "secret123",
        },
    )


def test_register_success(client):
    """步骤1: 注册新用户应返回 201"""
    r = client.post(
        "/users",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "secret123",
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert "id" in data


def test_login_success(client):
    """步骤2: 用正确用户名密码登录应返回 200 和 token"""
    r = _register_and_login(client)
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password_returns_401(client):
    """步骤3: 错误密码应返回 401,"用户名或密码错误" """
    client.post(
        "/users",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "secret123",
        },
    )
    r = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "wrongpassword",
        },
    )
    assert r.status_code == 401
    assert "用户名或密码错误" in r.json()["detail"]


def test_login_nonexistent_user_returns_401(client):
    """步骤4: 不存在的用户登录应返回 401"""
    r = client.post(
        "/auth/login",
        json={
            "username": "nobody",
            "password": "secret123",
        },
    )
    assert r.status_code == 401
    assert "用户名或密码错误" in r.json()["detail"]


def test_refresh_token_returns_new_access_token(client):
    """步骤8: 刷新 token 应返回新的 access_token,且不等于旧的"""
    login_resp = _register_and_login(client)
    refresh_token = login_resp.json()["refresh_token"]
    old_access_token = login_resp.json()["access_token"]

    time.sleep(1)

    r = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["access_token"] != old_access_token
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_with_invalid_token_returns_401(client):
    """步骤11: 传一个无效的 refresh_token 应返回 401"""
    r = client.post("/auth/refresh", json={"refresh_token": "invalid_token_here"})
    assert r.status_code == 401
    assert "无效的 refresh token" in r.json()["detail"]


def test_access_token_cannot_be_used_to_refresh(client):
    login_resp = _register_and_login(client)
    access_token = login_resp.json()["access_token"]

    r = client.post("/auth/refresh", json={"refresh_token": access_token})
    assert r.status_code == 401
    assert "无效的 refresh token" in r.json()["detail"]


def test_refresh_token_cannot_access_protected_endpoint(client):
    login_resp = _register_and_login(client)
    refresh_token = login_resp.json()["refresh_token"]

    r = client.get("/users/me", headers={"Authorization": f"Bearer {refresh_token}"})
    assert r.status_code == 401
    assert "无效的 Token" in r.json()["detail"]


def test_logout_blacklists_access_and_refresh_tokens(client):
    login_resp = _register_and_login(client)
    access_token = login_resp.json()["access_token"]
    refresh_token = login_resp.json()["refresh_token"]

    logout_resp = client.post(
        "/auth/logout",
        json={"refresh_token": refresh_token},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert logout_resp.status_code == 200

    me_resp = client.get("/users/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me_resp.status_code == 401
    assert "Token 已失效" in me_resp.json()["detail"]

    refresh_resp = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_resp.status_code == 401
    assert "Refresh token 已失效" in refresh_resp.json()["detail"]
