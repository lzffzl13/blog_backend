"""文章相关测试 - 覆盖创建、查询、修改、删除等场景"""

from .conftest import register_and_login


def test_get_articles_without_token(client):
    """步骤12: 公开接口 GET /articles 不带 token 应返回 200"""
    response = client.get("/articles")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 0
    assert isinstance(data["items"], list)


def test_create_article_success(client):
    """步骤5: 带 token 创建文章应返回 201,author_id 等于当前用户"""
    # 注册并登录，拿到 token 和用户信息
    reg_resp = client.post(
        "/users",
        json={
            "username": "author1",
            "email": "author1@example.com",
            "password": "secret123",
        },
    )
    user_id = reg_resp.json()["id"]
    login_resp = client.post(
        "/auth/login",
        json={
            "username": "author1",
            "password": "secret123",
        },
    )
    token = login_resp.json()["access_token"]

    r = client.post(
        "/articles",
        json={
            "title": "我的第一篇文章",
            "content": "这是文章内容，至少需要十个字才能通过验证。",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "我的第一篇文章"
    assert data["content"] == "这是文章内容，至少需要十个字才能通过验证。"
    assert data["author_id"] == user_id
    assert "id" in data


def test_create_article_without_token_returns_401(client):
    """步骤6: 不带 token 创建文章应返回 401"""
    r = client.post(
        "/articles",
        json={
            "title": "无认证创建测试文章",
            "content": "这篇文章没有带 token,应该返回 401。",
        },
    )
    assert r.status_code == 401


def test_update_others_article_returns_403(client):
    """步骤8: 修改他人文章应返回 403,"没有权限修改此文章" """
    # 注册作者并创建文章
    token_a = register_and_login(client, "author_a", "a@example.com")
    create_resp = client.post(
        "/articles",
        json={
            "title": "A的文章标题",
            "content": "这是 author_a 的文章内容，足够十个字了吧。",
        },
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert create_resp.status_code == 201
    article_id = create_resp.json()["id"]

    # 注册另一个用户并尝试修改
    token_b = register_and_login(client, "user2", "user2@example.com")
    r = client.put(
        f"/articles/{article_id}",
        json={
            "title": "被黑了的文章标题",
            "content": "别人改了我的文章内容，太可恶了。",
        },
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert r.status_code == 403
    assert "没有权限修改此文章" in r.json()["detail"]


def test_delete_others_article_returns_403(client):
    """步骤9: 删除他人文章应返回 403,"没有权限删除此文章" """
    # 注册作者并创建文章
    token_a = register_and_login(client, "author_a", "a@example.com")
    create_resp = client.post(
        "/articles",
        json={
            "title": "A的文章标题",
            "content": "这是 author_a 的文章内容，足够十个字了吧。",
        },
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert create_resp.status_code == 201
    article_id = create_resp.json()["id"]

    # 注册另一个用户并尝试删除
    token_b = register_and_login(client, "user2", "user2@example.com")
    r = client.delete(
        f"/articles/{article_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert r.status_code == 403
    assert "没有权限删除此文章" in r.json()["detail"]


def test_get_articles_list_returns_all_articles(client):
    """验证 GET /articles 能正确返回已创建的文章"""
    token = register_and_login(client, "author1", "author1@example.com")

    # 创建2篇文章
    client.post(
        "/articles",
        json={"title": "第一篇文章标题", "content": "这是第一篇文章的内容部分，满足十个字。"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/articles",
        json={"title": "第二篇文章标题", "content": "这是第二篇文章的内容部分，满足十个字。"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # 获取文章列表
    r = client.get("/articles")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_get_article_detail_without_token(client):
    """步骤10: 不带 token 获取文章详情应返回 200（公开接口）"""
    # 先创建一篇文章
    token = register_and_login(client, "author1", "author1@example.com")
    create_resp = client.post(
        "/articles",
        json={"title": "公开文章标题", "content": "这是公开文章的内容部分，满足十个字。"},
        headers={"Authorization": f"Bearer {token}"},
    )
    article_id = create_resp.json()["id"]

    # 不带 token 获取详情
    r = client.get(f"/articles/{article_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == article_id
    assert data["title"] == "公开文章标题"


def test_get_article_not_found_returns_404(client):
    """获取不存在的文章应返回 404"""
    r = client.get("/articles/9999")
    assert r.status_code == 404
    assert r.json()["detail"] == "文章不存在"
