from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_db

def test_register_duplicate_returns_409(db_session):
    """重复注册同一用户应该返回409冲突"""
    app.dependency_overrides[get_db] = lambda: db_session
    client = TestClient(app)

    # 首次注册 -> 201
    payload = {
        "username": "duplicate_user",
        "email": "dup@example.com",
        "password": "secret123"
    }
    r1 = client.post("/register", json=payload)
    assert r1.status_code == 201

    # 重复注册 -> 409
    r2 = client.post("/register", json=payload)
    assert r2.status_code == 409
    assert "已被注册" in r2.json()["detail"]

    app.dependency_overrides.clear()