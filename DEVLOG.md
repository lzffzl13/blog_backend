# AI增强博客系统 V1 当前进度总结

## 当前阶段

已经正式进入：

## FastAPI 后端工程化开发阶段

目前不再是语法学习，而是在真正搭建：

* 工程结构
* 数据库层
* CRUD
* API接口

---

## 当前技术栈

后端：

* Python
* FastAPI
* SQLAlchemy ORM
* MySQL
* PyMySQL
* Pydantic
* passlib[bcrypt]

工具：

* VSCode
* Git（本地仓库）
* MySQL 命令行

---

## 已完成内容

## 1. 项目初始化

完成：

* `.venv` 虚拟环境
* requirements.txt
* `.gitignore`
* FastAPI 基础运行

---

## 2. 工程目录结构

当前结构：

```text
app/
├── api/
├── core/
├── crud/
├── db/
├── models/
├── schemas/
├── services/
```

用户目前采用“任务拆解式引导”开发方式：
需要明确：

* 在哪个文件
* 实现什么
* 需要哪些字段/函数
  而不是抽象目标。

---

## 3. 数据库层

文件：

```text
app/db/session.py
```

已完成：

* engine
* SessionLocal
* Base
* get_db()

用户已经开始理解：

* request 生命周期
* Session 是请求级数据库会话
* Depends(get_db)
* ORM Session 工作流程

---

## 4. ORM Model

文件：

```text
app/models/user.py
```

已完成 User 模型：

字段包括：

* id
* username
* email
* hashed_password
* created_at

用户已经经历一次真实 ORM 报错：

```text
VARCHAR requires a length on dialect mysql
```

已经开始学会：

* 看 traceback
* 找 Error
* 根据报错定位问题

---

## 5. main.py

文件：

```text
app/main.py
```

已完成：

* FastAPI app 初始化
* startup create_all()
* root 路由
* include_router()

用户已经理解：

* router 注册
* app 生命周期

---

## 6. Git

已完成：

* git init
* git add
* git commit

第一次 commit：

```text
feat: complete database initialization
```

用户已经理解：

* Git 是本地版本控制
* GitHub 是远程托管
* commit 是开发阶段记录

---

## Day2 已完成内容

---

## 1. Schema 层

文件：

```text
app/schemas/user.py
```

已实现：

* UserCreate
* UserResponse

## 2. 密码加密模块

文件：

```text
app/core/security.py
```

已实现：

* pwd_context
* hash_password()
* verify_password()

使用：

```python
CryptContext(schemes=["bcrypt"])
```

用户已经理解：

* 明文密码不能存数据库
* hash 与 verify 的区别

目前注释较详细，是为了帮助理解模块逻辑。

---

## 3. CRUD 层

文件：

```text
app/crud/user.py
```

已实现：

```python
create_user()
```

包含：

* hash_password
* User ORM 创建
* db.add
* db.commit
* db.refresh

用户开始理解：

## ORM 数据流

```text
Schema
↓
ORM对象
↓
Session
↓
commit
↓
MySQL
```

并理解：

```python
db.refresh()
```

是从数据库同步完整对象。

---

## 4. API 层（进行中）

文件：

```text
app/api/user.py
```

正在实现：

```python
POST /register
```

已经使用：

* APIRouter
* Depends(get_db)
* response_model
* status_code=201

用户已经开始真正接触：

## FastAPI 依赖注入

---

## 当前开发习惯

用户要求：

* 一次不要给太多内容
* 采用“小步开发”
* 一个模块一个模块推进
* 给明确文件位置与任务拆解
* 保留自己编码过程
* ChatGPT 主要负责：

  * 工程规划
  * 任务拆解
  * Debug
  * 代码审查
  * 解释原理

---

## 当前卡点（新对话继续）

app/api/user.py 中：

```python
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST
    detail="用户名或邮箱已存在"
)
```

缺少逗号：

```python
status_code=..., detail=...
```

导致：

* router 导入失败
* POST /register 不显示

另外建议：

当前阶段先删掉 try/except。

保留：

```python
user = create_user(...)
return user
```

方便学习真实 Debug。

---

## 下一步

修复 user.py 后：

继续：

1. 注册 router
2. 启动项目
3. 打开 `/docs`
4. 测试 POST /register
5. 验证：

   * 数据是否写入 MySQL
   * password 是否未返回
   * response_model 是否正常
   * CRUD 链路是否完整

成功后进行：

第二次 Git commit。
