# Blog Backend

一个基于 FastAPI 的博客后端 API，覆盖认证、文章、评论、分类、标签、缓存和限流等常见后端能力。项目目标不是只做基础 CRUD，而是把一个小型内容系统需要的核心工程要素补齐。

## 功能概览

- 用户注册、登录、获取当前用户信息、修改密码、删除账号
- JWT 认证，区分 `access_token` 和 `refresh_token`
- 文章 CRUD，作者权限校验
- 评论 CRUD，评论作者权限校验
- 分类 CRUD
- 标签创建、查询、删除
- Redis 缓存文章详情和文章列表
- 登录接口基于 Redis + Lua 脚本限流
- Redis 不可用时自动降级
- Alembic 管理数据库迁移
- pytest + SQLite + fakeredis 做自动化测试

## 技术栈

- Python 3.12
- FastAPI
- SQLAlchemy 2.0
- Alembic
- MySQL
- Redis
- Pydantic v2
- bcrypt
- PyJWT
- pytest
- uv
- Docker / Docker Compose

## 项目结构

```text
blog_backend/
├── app/
│   ├── api/          # 路由层
│   ├── core/         # 配置、安全、日志、限流
│   ├── crud/         # 数据库访问
│   ├── db/           # 数据库连接与会话
│   ├── models/       # ORM 模型
│   ├── schemas/      # Pydantic 模型
│   ├── services/     # 缓存等服务逻辑
│   └── main.py       # FastAPI 入口
├── alembic/          # 数据库迁移
├── scripts/          # 手动测试脚本
├── tests/            # 自动化测试
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── requirements.txt
```

## 环境变量

复制 `.env.example` 为 `.env`，至少配置下面这些值：

```env
DATABASE_URL=mysql+pymysql://root:your-password@localhost:3306/blog_db
SECRET_KEY=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
LOG_LEVEL=INFO
```

说明：

- `SECRET_KEY` 在 `HS256` 模式下要求至少 32 字节
- `CORS_ORIGINS` 使用 JSON 数组格式
- 开发环境建议单独生成随机密钥，例如：

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 启动方式

### 方式一：本地 venv

```bash
python -m venv .venv
```

Windows:

```bash
.\.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Linux / macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### 方式二：使用 uv

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

### 方式三：使用 Docker Compose

```bash
docker compose up --build
```

启动后可访问：

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

## 数据库迁移

初始化或升级数据库：

```bash
alembic upgrade head
```

新建迁移：

```bash
alembic revision --autogenerate -m "your message"
```

注意：

- 自动生成的迁移脚本必须人工审核
- 后续迁移应该保持增量变更，不要删核心业务表后重建

## 测试

运行全部测试：

```bash
pytest tests -v
```

或使用 `uv`：

```bash
uv run pytest tests -v
```

测试覆盖的重点场景包括：

- 用户注册、登录、刷新 token
- 文章、评论的权限校验
- 分类、标签接口
- Redis 缓存命中与失效
- Redis 故障时的降级逻辑
- 配置项校验

## API 概览

### 认证

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/auth/login` | 用户登录，返回 access/refresh token |
| POST | `/auth/refresh` | 使用 refresh token 刷新 access token |

### 用户

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/users` | 注册用户 |
| GET | `/users/me` | 获取当前用户信息 |
| PUT | `/users/me/password` | 修改当前用户密码 |
| DELETE | `/users/me` | 删除当前用户账号 |

### 文章

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/articles` | 分页获取文章列表，带缓存 |
| POST | `/articles` | 创建文章 |
| GET | `/articles/{article_id}` | 获取文章详情，带缓存 |
| PUT | `/articles/{article_id}` | 更新文章，仅作者可操作 |
| DELETE | `/articles/{article_id}` | 删除文章，仅作者可操作 |

### 评论

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/articles/{article_id}/comments` | 获取文章评论列表 |
| POST | `/articles/{article_id}/comments` | 创建评论 |
| GET | `/articles/{article_id}/comments/{comment_id}` | 获取评论详情 |
| PUT | `/articles/{article_id}/comments/{comment_id}` | 更新评论，仅作者可操作 |
| DELETE | `/articles/{article_id}/comments/{comment_id}` | 删除评论，仅作者可操作 |

### 分类

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/categories` | 获取分类列表 |
| GET | `/categories/{category_id}` | 获取分类详情 |
| POST | `/categories` | 创建分类 |
| PUT | `/categories/{category_id}` | 更新分类 |
| DELETE | `/categories/{category_id}` | 删除分类 |

### 标签

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/tags` | 获取标签列表 |
| GET | `/tags/{tag_id}` | 获取标签详情 |
| POST | `/tags` | 创建标签 |
| DELETE | `/tags/{tag_id}` | 删除标签 |

## 缓存与限流设计

### 文章缓存

- 单篇文章缓存 Key：`article:{id}`
- TTL：300 秒
- 列表缓存 Key：`articles_list:{version}:{skip}:{limit}`
- TTL：60 秒
- 文章新增、更新、删除后会刷新列表版本号并删除详情缓存

### 登录限流

- 接口：`POST /auth/login`
- 策略：同一 IP 在 60 秒窗口内最多 5 次请求
- 实现：Redis + Lua 脚本保证原子自增
- 降级：Redis 不可用时放行请求并记录警告日志

## 当前设计选择

- `categories` 和 `tags` 接口当前未做管理员权限控制
- 测试使用 SQLite 内存库，生产环境目标数据库是 MySQL
- Redis 主要用于缓存和限流，不作为强一致状态存储

## 后续可扩展方向

- 给分类和标签接口补权限控制
- 引入分页总数优化和更细粒度查询能力
- 补充 CI 流程和覆盖率报告
- 增加刷新 token 轮换和黑名单机制
