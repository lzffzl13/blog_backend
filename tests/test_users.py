"""鐢ㄦ埛鐩稿叧娴嬭瘯 - 瑕嗙洊娉ㄥ唽銆佷釜浜轰俊鎭€佷慨鏀瑰瘑鐮併€佸垹闄よ处鍙风瓑鍦烘櫙"""

from .conftest import register_and_login


def test_register_duplicate_returns_409(client):
    """閲嶅娉ㄥ唽鍚屼竴鐢ㄦ埛搴旇杩斿洖409鍐茬獊"""
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
    """甯?token 鑾峰彇涓汉淇℃伅锛岃繑鍥?200锛寀sername 鍜?email 姝ｇ‘"""
    token = register_and_login(client, "testuser", "testuser@example.com")

    r = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert "id" in data


def test_get_me_without_token_returns_401(client):
    """涓嶅甫 token 鑾峰彇涓汉淇℃伅锛岃繑鍥?401"""
    r = client.get("/users/me")
    assert r.status_code == 401


def test_change_password_success(client):
    """姝ｇ‘淇敼瀵嗙爜锛岃繑鍥?200锛涙棫瀵嗙爜澶辨晥锛屾柊瀵嗙爜鍙敤"""
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
    """鏃у瘑鐮侀敊璇椂杩斿洖 400"""
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
    """甯?token 鍒犻櫎璐﹀彿锛岃繑鍥?204,鍒犻櫎鍚庣敤鍚屼竴 token 璁块棶杩斿洖 401"""
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
    """涓嶅甫 token 鍒犻櫎璐﹀彿锛岃繑鍥?401"""
    r = client.delete("/users/me")
    assert r.status_code == 401
