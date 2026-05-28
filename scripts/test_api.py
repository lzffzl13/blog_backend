"""手动测试脚本:覆盖CURD及异常处理"""

import sys

import requests

BASE_URL = "http://127.0.0.1:8000"
passed = 0
failed = 0


def check(case_name, response, expected_status: int) -> None:
    global passed, failed
    if response.status_code == expected_status:
        passed += 1
        print(f"✅{case_name}")
    else:
        failed += 1
        print(f"❌{case_name} - Expected: {expected_status}, Got: {response.status_code}")
        print(f"body: {response.text}")


##准备数据
# 注册用户作为文章作者
print("准备数据:注册用户作为文章作者")
r = requests.post(
    f"{BASE_URL}/users",
    json={
        "username": "autotest",
        "email": "autotest@example.com",
        "password": "secret123",
    },
)
check("注册用户", r, 201)
user_id = r.json().get("id") if r.status_code == 201 else None

# 注册重复用户
print("准备数据:注册重复用户")
r = requests.post(
    f"{BASE_URL}/users",
    json={
        "username": "autotest",
        "email": "autotest@example.com",
        "password": "secret123",
    },
)
check("重复注册返回 409", r, 409)

# 登录获取 token
print("准备数据:登录获取 token")
r = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "username": "autotest",
        "password": "secret123",
    },
)
check("登录", r, 200)
token = r.json().get("access_token") if r.status_code == 200 else None
headers = {"Authorization": f"Bearer {token}"} if token else {}

##文章CURD
# 创建文章
article_id = None
if user_id:
    print("\n--- 创建文章 ---")
    r = requests.post(
        f"{BASE_URL}/articles",
        json={
            "title": "自动化测试文章",
            "content": "这是一篇由脚本自动创建的文章，用于测试。",
        },
    )
    check("创建文章", r, 201)
    if r.status_code == 201:
        article_id = r.json()["id"]

# 获取文章列表
print("\n--- 获取文章列表 ---")
r = requests.get(f"{BASE_URL}/articles")
check("获取文章列表", r, 200)
if r.status_code == 200:
    data = r.json()
    print(f"   共 {data['total']} 篇文章，当前返回 {len(data['items'])} 篇")

# 获取文章详情
if article_id:
    print("\n--- 获取文章详情 ---")
    r = requests.get(f"{BASE_URL}/articles/{article_id}")
    check("获取文章详情", r, 200)

# 查询不存在的文章
print("\n--- 查询不存在的文章 ---")
r = requests.get(f"{BASE_URL}/articles/99999")
check("查询不存在的文章返回 404", r, 404)

# 更新文章
if article_id:
    print("\n--- 更新文章 ---")
    r = requests.put(
        f"{BASE_URL}/articles/{article_id}",
        headers=headers,
        json={"title": "自动化测试文章 - 更新", "content": "这篇文章已经被更新了。"},
    )
    check("更新文章", r, 200)
    if r.status_code == 200:
        updated_data = r.json()
        print(f"   更新后标题: {updated_data['title']}")

# 空标题创建文章（422）
if user_id:
    print("\n--- 空标题创建文章 ---")
    r = requests.post(
        f"{BASE_URL}/articles",
        json={"title": "", "content": "第二篇文章,内容不空,但标题为空。"},
    )
    check("空标题创建文章返回 422", r, 422)

# 删除文章
if article_id:
    print("\n--- 删除文章 ---")
    r = requests.delete(f"{BASE_URL}/articles/{article_id}", headers=headers)
    check("删除文章", r, 204)

# 删除已删除的文章
if article_id:
    print("\n--- 删除已删除的文章 ---")
    r = requests.delete(f"{BASE_URL}/articles/{article_id}", headers=headers)
    check("删除已删除的文章返回 404", r, 404)


##结果汇总
print("\n--- 测试结果汇总 ---")
print(f"\n{'=' * 30}")
print(f"测试通过: {passed}, 测试失败: {failed}")
if failed > 0:
    sys.exit(1)  # 返回非零状态码表示测试失败
