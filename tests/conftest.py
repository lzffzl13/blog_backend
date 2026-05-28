import fakeredis.aioredis
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models.article  # noqa: F401
import app.models.user  # noqa: F401
from app.core.redis import get_redis
from app.db.session import Base, get_db
from app.main import app as fastapi_app


@pytest_asyncio.fixture(scope="function")
def db_session():
    """创建临时SQLite内存数据库,每次测试独立"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

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


@pytest_asyncio.fixture(scope="function")
async def redis_client():
    """每次测试独立的fake Redis客户端,使用 fakeredis库模拟"""
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield client
    await client.aclose()


@pytest_asyncio.fixture(scope="function")
def client(db_session, redis_client):
    """基于测试数据库和fake Redis的 FastAPI TestClient,自动覆盖依赖并清理"""
    fastapi_app.dependency_overrides[get_db] = lambda: db_session
    fastapi_app.dependency_overrides[get_redis] = lambda: redis_client
    yield TestClient(fastapi_app)
    fastapi_app.dependency_overrides.clear()
