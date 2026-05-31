"""标签相关测试 - 覆盖创建、查询、删除等场景"""


def test_create_tag_success(client):
    """创建标签成功应返回 201"""
    r = client.post("/tags", json={"name": "Python"})
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Python"
    assert "id" in data


def test_create_duplicate_tag_returns_409(client):
    """创建重复标签应返回 409"""
    client.post("/tags", json={"name": "Python"})
    r = client.post("/tags", json={"name": "Python"})
    assert r.status_code == 409
    assert "标签已存在" in r.json()["detail"]


def test_get_tags_list(client):
    """获取标签列表应返回 200"""
    client.post("/tags", json={"name": "Python"})
    client.post("/tags", json={"name": "JavaScript"})

    r = client.get("/tags")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    names = [t["name"] for t in data]
    assert "Python" in names
    assert "JavaScript" in names


def test_get_tag_by_id(client):
    """根据ID获取标签详情应返回 200"""
    create_resp = client.post("/tags", json={"name": "Python"})
    tag_id = create_resp.json()["id"]

    r = client.get(f"/tags/{tag_id}")
    assert r.status_code == 200
    assert r.json()["name"] == "Python"


def test_get_tag_not_found_returns_404(client):
    """获取不存在的标签应返回 404"""
    r = client.get("/tags/9999")
    assert r.status_code == 404
    assert r.json()["detail"] == "标签不存在"


def test_delete_tag_success(client):
    """删除标签成功应返回 204"""
    create_resp = client.post("/tags", json={"name": "Python"})
    tag_id = create_resp.json()["id"]

    r = client.delete(f"/tags/{tag_id}")
    assert r.status_code == 204

    # 确认已被删除
    r_get = client.get(f"/tags/{tag_id}")
    assert r_get.status_code == 404


def test_delete_tag_not_found_returns_404(client):
    """删除不存在的标签应返回 404"""
    r = client.delete("/tags/9999")
    assert r.status_code == 404
    assert r.json()["detail"] == "标签不存在"
