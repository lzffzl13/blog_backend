def test_get_articles(client):
    """测试空文章列表返回200,且 items 为空"""
    response = client.get("/articles")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 0
    assert isinstance(data["items"], list)


def test_create_article_empty_title_returns_422(client):
    """测试创建文章时,如果标题为空,返回422"""
    # 先注册作者，并断言成功
    reg_resp = client.post("/register", json={
        "username": "author1",
        "email": "author1@example.com",
        "password": "secret123",
    })
    assert reg_resp.status_code == 201, f"注册作者失败: {reg_resp.json()}"
    author_id = reg_resp.json()["id"]

    # 用空标题创建文章
    r = client.post("/articles", params={"author_id": author_id}, json={
        "title": "",
        "content": "这篇文章标题为空",
    })
    assert r.status_code == 422


def test_get_article_not_found_returns_404(client):
    """测试获取不存在的文章返回404"""
    r = client.get("/articles/9999")
    assert r.status_code == 404
    assert r.json()["detail"] == "文章不存在"
