# Blog Backend

一个基于 FastAPI 的博客后端 API，支持用户注册、JWT 认证、文章 CRUD 及 Redis 缓存。

## 技术栈

- **Web 框架**: FastAPI 0.115
- **ORM**: SQLAlchemy 2.0
- **数据库**: MySQL (生产) / SQLite (测试)
- **缓存**: Redis (异步)
- **密码哈希**: bcrypt
- **JWT 认证**: access_token + refresh_token
- **测试**: pytest + fakeredis
- **日志**: Python logging
- **包管理**: uv

## 项目结构

```text
├── app/
│   ├── api/          # 路由层
│   ├── core/         # 配置、安全、日志、限流
│   ├── crud/         # 数据库操作
│   ├── db/           # 数据库连接与会话
│   ├── models/       # ORM 模型
│   ├── schemas/      # Pydantic 数据模型
│   ├── services/     # 业务逻辑（缓存等）
│   └── main.py       # 入口
├── scripts/          # 手动测试脚本
├── tests/            # 自动化测试
└── requirements.txt
```

## 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd blog_backend
```

### 2. 创建虚拟环境并激活

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / Mac
.venv\Scripts\activate      # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
# 或使用 uv
uv sync
```

### 4. 配置环境变量

在项目根目录创建 .env 文件：

```env
DATABASE_URL=mysql+pymysql://root:密码@localhost:3306/blog_db
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379/0
```

### 5. 启动服务

```bash
uvicorn app.main:app --reload
```

访问 http://127.0.0.1:8000/docs 查看交互式 API 文档。

## API 概览

### 认证

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| POST | /users | 注册新用户 | ❌ |
| POST | /auth/login | 登录，返回 access_token + refresh_token | ❌ |
| POST | /auth/refresh | 刷新 access_token | ❌ |

### 用户

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | /users/me | 获取当前用户信息 | ✅ |
| PUT | /users/me/password | 修改密码 | ✅ |
| DELETE | /users/me | 删除账号（级联删除文章） | ✅ |

### 文章

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | /articles | 获取文章列表（分页，缓存 60s） | ❌ |
| POST | /articles | 创建文章 | ✅ |
| GET | /articles/{id} | 获取文章详情（缓存 300s） | ❌ |
| PUT | /articles/{id} | 更新文章（仅作者） | ✅ |
| DELETE | /articles/{id} | 删除文章（仅作者） | ✅ |

## 缓存策略

| 缓存项 | Key 格式 | TTL | 失效时机 |
|--------|----------|-----|----------|
| 单篇文章 | article:{id} | 300s | 更新/删除文章时删除 |
| 文章列表 | article_list:v{version}:{skip}:{limit} | 60s | 增/删/改文章时版本号+1 |

Redis 不可用时自动降级：读失败查库，写失败忽略，限流放行。

## 限流

- **登录接口** (POST /auth/login)：60 秒窗口内最多 5 次请求，超限返回 429
- 基于客户端 IP + Lua 原子脚本实现
- Redis 不可用时自动放行

## 运行测试

```bash
# 自动化测试（27 个用例）
pytest tests/ -v

# 使用 uv
uv run pytest tests/ -v

# 手动测试 (需先启动服务)
python scripts/test_api.py
```

## 待实现

- [ ] 文章分类与标签
- [ ] 分页优化
- [ ] 单元测试覆盖率提升
