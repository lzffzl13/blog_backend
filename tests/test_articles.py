from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_db

# 从conftest.py导入 fixture
def test_get_articles(db_session):
    """测试空文章列表返回200,且 items 为空"""
    #覆盖FastAPI的get_db依赖,使用测试数据库会话
    app.dependency_overrides[get_db] = lambda: db_session
    client = TestClient(app)

    response = client.get("/articles")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 0
    assert isinstance(data["items"], list)

    #清除覆盖，避免影响后续测试
    app.dependency_overrides.clear()

def test_create_article_empty_title_returns_422(db_session):
    """测试创建文章时,如果标题为空,返回422"""
    app.dependency_overrides[get_db] = lambda: db_session
    client = TestClient(app)

    client.post("/register", json={
        "username": "author1",
        "email": "author1@example.com",
        "password": "secret123",
    })
    r = client.post("/articles",params={"author_id": 1},json={
        "title": "",
        "content": "这篇文章标题为空",
    })
    assert r.status_code == 422
    app.dependency_overrides.clear()

def test_get_article_not_found_returns_404(db_session):
    """测试获取不存在的文章返回404"""
    app.dependency_overrides[get_db] = lambda: db_session
    client = TestClient(app)

    r = client.get("/articles/9999")
    assert r.status_code == 404
    assert r.json()["detail"] == "文章不存在"
    app.dependency_overrides.clear()