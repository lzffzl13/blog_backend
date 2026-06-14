from datetime import UTC, datetime, timedelta

import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models.article  # noqa: F401
import app.models.comment  # noqa: F401
import app.models.user  # noqa: F401
from app.core.redis import get_redis
from app.db.session import Base, get_db
from app.main import app as fastapi_app


class AsyncRedisStub:
    def __init__(self):
        self._store: dict[str, str] = {}
        self._expires_at: dict[str, datetime] = {}

    def _cleanup_key(self, key: str) -> None:
        expires_at = self._expires_at.get(key)
        if expires_at and expires_at <= datetime.now(UTC):
            self._store.pop(key, None)
            self._expires_at.pop(key, None)

    async def get(self, key: str):
        self._cleanup_key(key)
        return self._store.get(key)

    async def set(self, key: str, value: str, ex: int | None = None):
        self._store[key] = value
        if ex is not None:
            self._expires_at[key] = datetime.now(UTC) + timedelta(seconds=ex)
        else:
            self._expires_at.pop(key, None)
        return True

    async def setex(self, key: str, ttl: int, value: str):
        return await self.set(key, value, ex=ttl)

    async def delete(self, *keys: str):
        deleted = 0
        for key in keys:
            self._cleanup_key(key)
            if key in self._store:
                deleted += 1
                self._store.pop(key, None)
            self._expires_at.pop(key, None)
        return deleted

    async def incr(self, key: str):
        self._cleanup_key(key)
        current = int(self._store.get(key, "0")) + 1
        self._store[key] = str(current)
        return current

    async def eval(self, script: str, num_keys: int, *args):
        key = args[0]
        window = int(args[1])
        current = await self.incr(key)
        if current == 1:
            self._expires_at[key] = datetime.now(UTC) + timedelta(seconds=window)
        return current

    async def aclose(self):
        self._store.clear()
        self._expires_at.clear()


@pytest_asyncio.fixture(scope="function")
def db_session():
    """鍒涘缓涓存椂SQLite鍐呭瓨鏁版嵁搴?姣忔娴嬭瘯鐙珛"""
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

    session = Session(bind=engine)
    yield session

    session.close()
    engine.dispose()


def register_and_login(client, username: str, email: str, password: str = "secret123"):
    """杈呭姪鍑芥暟锛氭敞鍐屽苟鐧诲綍锛岃繑鍥?access_token"""
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
    """姣忔娴嬭瘯鐙珛鐨勫紓姝?Redis stub瀹㈡埛绔?"""
    client = AsyncRedisStub()
    yield client
    await client.aclose()


@pytest_asyncio.fixture(scope="function")
def client(db_session, redis_client):
    """鍩轰簬娴嬭瘯鏁版嵁搴撳拰fake Redis鐨?FastAPI TestClient,鑷姩瑕嗙洊渚濊禆骞舵竻鐞?"""
    fastapi_app.dependency_overrides[get_db] = lambda: db_session
    fastapi_app.dependency_overrides[get_redis] = lambda: redis_client
    yield TestClient(fastapi_app)
    fastapi_app.dependency_overrides.clear()
