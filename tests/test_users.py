def test_register_duplicate_returns_409(client):
    """重复注册同一用户应该返回409冲突"""
    payload = {
        "username": "duplicate_user",
        "email": "dup@example.com",
        "password": "secret123"
    }
    r1 = client.post("/register", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/register", json=payload)
    assert r2.status_code == 409
    assert "已被注册" in r2.json()["detail"]
