"""认证相关测试 - 覆盖注册、登录、刷新 token 等场景"""

import time


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
    # 先注册
    client.post(
        "/users",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "secret123",
        },
    )
    # 登录
    r = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "secret123",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password_returns_401(client):
    """步骤3: 错误密码应返回 401,"用户名或密码错误" """
    # 先注册
    client.post(
        "/users",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "secret123",
        },
    )
    # 用错误密码登录
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
    # 注册并登录
    client.post(
        "/users",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "secret123",
        },
    )
    login_resp = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "secret123",
        },
    )
    refresh_token = login_resp.json()["refresh_token"]
    old_access_token = login_resp.json()["access_token"]

    # 等待1秒，确保新 token 的 exp 不同
    time.sleep(1)

    # 刷新 token
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
