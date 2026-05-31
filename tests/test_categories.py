"""分类相关测试 - 覆盖创建、查询、修改、删除等场景"""


def test_create_category_success(client):
    """创建分类成功应返回 201"""
    r = client.post("/categories", json={"name": "技术", "description": "技术相关文章"})
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "技术"
    assert data["description"] == "技术相关文章"
    assert "id" in data


def test_create_duplicate_category_returns_409(client):
    """创建重复分类应返回 409"""
    client.post("/categories", json={"name": "技术"})
    r = client.post("/categories", json={"name": "技术"})
    assert r.status_code == 409
    assert "分类已存在" in r.json()["detail"]


def test_get_categories_list(client):
    """获取分类列表应返回 200"""
    client.post("/categories", json={"name": "技术"})
    client.post("/categories", json={"name": "生活"})

    r = client.get("/categories")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    names = [c["name"] for c in data]
    assert "技术" in names
    assert "生活" in names


def test_get_category_by_id(client):
    """根据ID获取分类详情应返回 200"""
    create_resp = client.post("/categories", json={"name": "技术"})
    category_id = create_resp.json()["id"]

    r = client.get(f"/categories/{category_id}")
    assert r.status_code == 200
    assert r.json()["name"] == "技术"


def test_get_category_not_found_returns_404(client):
    """获取不存在的分类应返回 404"""
    r = client.get("/categories/9999")
    assert r.status_code == 404
    assert r.json()["detail"] == "分类不存在"


def test_update_category_success(client):
    """更新分类成功应返回 200"""
    create_resp = client.post("/categories", json={"name": "技术"})
    category_id = create_resp.json()["id"]

    r = client.put(
        f"/categories/{category_id}",
        json={"name": "科技", "description": "科技相关文章"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "科技"
    assert data["description"] == "科技相关文章"


def test_update_category_not_found_returns_404(client):
    """更新不存在的分类应返回 404"""
    r = client.put("/categories/9999", json={"name": "科技"})
    assert r.status_code == 404
    assert r.json()["detail"] == "分类不存在"


def test_delete_category_success(client):
    """删除分类成功应返回 204"""
    create_resp = client.post("/categories", json={"name": "技术"})
    category_id = create_resp.json()["id"]

    r = client.delete(f"/categories/{category_id}")
    assert r.status_code == 204

    # 确认已被删除
    r_get = client.get(f"/categories/{category_id}")
    assert r_get.status_code == 404


def test_delete_category_not_found_returns_404(client):
    """删除不存在的分类应返回 404"""
    r = client.delete("/categories/9999")
    assert r.status_code == 404
    assert r.json()["detail"] == "分类不存在"
