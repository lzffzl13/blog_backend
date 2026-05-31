"""评论相关测试 - 覆盖创建、查询、修改、删除等场景"""

from .conftest import register_and_login


def _create_article(client, token):
    """辅助函数：创建一篇文章并返回 article_id"""
    resp = client.post(
        "/articles",
        json={
            "title": "测试文章标题",
            "content": "这是测试文章的内容部分，满足十个字的要求。",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    return resp.json()["id"]


def test_create_comment_success(client):
    """创建评论成功应返回 201"""
    token = register_and_login(client, "commenter", "commenter@example.com")
    article_id = _create_article(client, token)

    r = client.post(
        f"/articles/{article_id}/comments",
        json={"content": "这是一条评论"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["content"] == "这是一条评论"
    assert data["article_id"] == article_id
    assert "author_id" in data
    assert "id" in data


def test_create_comment_article_not_found_returns_404(client):
    """不存在的文章创建评论应返回 404"""
    token = register_and_login(client, "commenter", "commenter@example.com")

    r = client.post(
        "/articles/9999/comments",
        json={"content": "这是一条评论"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "文章不存在"


def test_create_comment_without_token_returns_401(client):
    """未登录创建评论应返回 401"""
    r = client.post(
        "/articles/1/comments",
        json={"content": "这是一条评论"},
    )
    assert r.status_code == 401


def test_get_comments_list(client):
    """获取文章评论列表应返回 200"""
    token = register_and_login(client, "commenter", "commenter@example.com")
    article_id = _create_article(client, token)

    # 创建2条评论
    client.post(
        f"/articles/{article_id}/comments",
        json={"content": "第一条评论"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        f"/articles/{article_id}/comments",
        json={"content": "第二条评论"},
        headers={"Authorization": f"Bearer {token}"},
    )

    r = client.get(f"/articles/{article_id}/comments")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    contents = [c["content"] for c in data]
    assert "第一条评论" in contents
    assert "第二条评论" in contents


def test_get_comment_detail(client):
    """获取评论详情应返回 200"""
    token = register_and_login(client, "commenter", "commenter@example.com")
    article_id = _create_article(client, token)

    create_resp = client.post(
        f"/articles/{article_id}/comments",
        json={"content": "这是一条评论"},
        headers={"Authorization": f"Bearer {token}"},
    )
    comment_id = create_resp.json()["id"]

    r = client.get(f"/articles/{article_id}/comments/{comment_id}")
    assert r.status_code == 200
    assert r.json()["content"] == "这是一条评论"


def test_get_comment_not_found_returns_404(client):
    """获取不存在的评论应返回 404"""
    token = register_and_login(client, "commenter", "commenter@example.com")
    article_id = _create_article(client, token)

    r = client.get(f"/articles/{article_id}/comments/9999")
    assert r.status_code == 404
    assert r.json()["detail"] == "评论不存在"


def test_update_own_comment_success(client):
    """更新自己的评论成功应返回 200"""
    token = register_and_login(client, "commenter", "commenter@example.com")
    article_id = _create_article(client, token)

    create_resp = client.post(
        f"/articles/{article_id}/comments",
        json={"content": "原评论内容"},
        headers={"Authorization": f"Bearer {token}"},
    )
    comment_id = create_resp.json()["id"]

    r = client.put(
        f"/articles/{article_id}/comments/{comment_id}",
        json={"content": "修改后的评论内容"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["content"] == "修改后的评论内容"


def test_update_others_comment_returns_403(client):
    """更新别人的评论应返回 403"""
    token_a = register_and_login(client, "author_a", "author_a@example.com")
    article_id = _create_article(client, token_a)

    # author_a 创建评论
    create_resp = client.post(
        f"/articles/{article_id}/comments",
        json={"content": "author_a 的评论"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    comment_id = create_resp.json()["id"]

    # 另一个用户尝试修改
    token_b = register_and_login(client, "user_b", "user_b@example.com")
    r = client.put(
        f"/articles/{article_id}/comments/{comment_id}",
        json={"content": "被修改的评论"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert r.status_code == 403
    assert "没有权限修改此评论" in r.json()["detail"]


def test_delete_own_comment_success(client):
    """删除自己的评论成功应返回 204"""
    token = register_and_login(client, "commenter", "commenter@example.com")
    article_id = _create_article(client, token)

    create_resp = client.post(
        f"/articles/{article_id}/comments",
        json={"content": "待删除的评论"},
        headers={"Authorization": f"Bearer {token}"},
    )
    comment_id = create_resp.json()["id"]

    r = client.delete(
        f"/articles/{article_id}/comments/{comment_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 204

    # 确认已被删除
    r_get = client.get(f"/articles/{article_id}/comments/{comment_id}")
    assert r_get.status_code == 404


def test_delete_others_comment_returns_403(client):
    """删除别人的评论应返回 403"""
    token_a = register_and_login(client, "author_a", "author_a@example.com")
    article_id = _create_article(client, token_a)

    # author_a 创建评论
    create_resp = client.post(
        f"/articles/{article_id}/comments",
        json={"content": "author_a 的评论"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    comment_id = create_resp.json()["id"]

    # 另一个用户尝试删除
    token_b = register_and_login(client, "user_b", "user_b@example.com")
    r = client.delete(
        f"/articles/{article_id}/comments/{comment_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert r.status_code == 403
    assert "没有权限删除此评论" in r.json()["detail"]
