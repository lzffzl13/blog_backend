# Blog Backend

一个基于 FastAPI 的博客后端 API，支持用户注册和文章 CRUD。

## 技术栈

- **Web 框架**: FastAPI 0.115
- **ORM**: SQLAlchemy 2.0
- **数据库**: MySQL (生产) / SQLite (测试)
- **密码哈希**: bcrypt
- **测试**: pytest + requests
- **日志**: Python logging

## 项目结构

```text
├── app/
│   ├── api/          # 路由层
│   ├── core/         # 配置、安全、日志
│   ├── crud/         # 数据库操作
│   ├── db/           # 数据库连接与会话
│   ├── models/       # ORM 模型
│   ├── schemas/      # Pydantic 数据模型
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
```

### 4. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
DATABASE_URL=mysql+pymysql://root:密码@localhost:3306/blog_db
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
LOG_LEVEL=INFO
```

### 5. 启动服务

```bash
uvicorn app.main:app --reload
```

访问 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) 查看交互式 API 文档。

## API 概览

| 方法 | 路径 | 描述 |
| ------ | ------ | ------ |
| POST | `/register` | 注册新用户 |
| GET | `/articles` | 获取文章列表 |
| POST | `/articles?author_id=1` | 创建文章 |
| GET | `/articles/{id}` | 获取文章详情 |
| PUT | `/articles/{id}` | 更新文章 |
| DELETE | `/articles/{id}` | 删除文章 |

## 运行测试

```bash
# 自动化测试
pytest tests/ -v

# 手动测试 (需先启动服务)
python scripts/test_api.py
```

## 待实现


- [ ] 文章分类与标签
- [ ] 分页优化
- [ ] 单元测试覆盖率提升
