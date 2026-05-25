import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models.article  # noqa: F401
import app.models.user  # noqa: F401
from app.db.session import Base, get_db
from app.main import app as fastapi_app


@pytest.fixture(scope="function")
def db_session():
    """创建临时SQLite内存数据库,每次测试独立"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    # print("✅ Created tables in SQLite:", list(Base.metadata.tables.keys()))

    session = Session(bind=engine)
    yield session

    session.close()
    engine.dispose()


def register_and_login(client, username: str, email: str, password: str = "secret123"):
    """辅助函数：注册并登录，返回 access_token"""
    client.post(
        "/users",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    login_resp = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )
    return login_resp.json()["access_token"]


@pytest.fixture(scope="function")
def client(db_session):
    """基于测试数据库的 FastAPI TestClient,自动覆盖依赖并清理"""
    fastapi_app.dependency_overrides[get_db] = lambda: db_session
    yield TestClient(fastapi_app)
    fastapi_app.dependency_overrides.clear()
