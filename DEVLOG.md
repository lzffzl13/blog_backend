AI增强博客系统 V1 当前进度总结
当前阶段
已经正式进入：FastAPI 后端工程化开发阶段
目前不再是语法学习，而是在真正搭建：工程结构、数据库层、CRUD、API接口

---
当前技术栈
后端：Python、FastAPI、SQLAlchemy ORM、MySQL、PyMySQL、Pydantic、passlib[bcrypt]
工具：VSCode、Git（本地仓库）、MySQL 命令行

---
已完成内容
1. 项目初始化
完成：.venv 虚拟环境、requirements.txt、.gitignore、FastAPI 基础运行
2. 工程目录结构
当前结构：
app/
├── api/
├── core/
├── crud/
├── db/
├── models/
├── schemas/
├── services/
用户目前采用“任务拆解式引导”开发方式：需要明确：在哪个文件、实现什么、需要哪些字段/函数，而不是抽象目标。
3. 数据库层
文件：app/db/session.py
已完成：engine、SessionLocal、Base、get_db()
用户已经开始理解：request 生命周期、Session 是请求级数据库会话、Depends(get_db)、ORM Session 工作流程
4. ORM Model
文件：app/models/user.py
已完成 User 模型，字段包括：id、username、email、hashed_password、created_at
用户已经经历一次真实 ORM 报错：VARCHAR requires a length on dialect mysql
已经开始学会：看 traceback、找 Error、根据报错定位问题
5. main.py
文件：app/main.py
已完成：FastAPI app 初始化、startup create_all()、root 路由、include_router()
用户已经理解：router 注册、app 生命周期
6. Git
已完成：git init、git add、git commit
第一次 commit：feat: complete database initialization
7. Schema 层
文件：app/schemas/user.py
已实现：UserCreate、UserResponse
8. 密码加密模块（Day2）
文件：app/core/security.py
已实现：pwd_context、hash_password()、verify_password()
使用：CryptContext(schemes=["bcrypt"])
用户已经理解：明文密码不能存数据库、hash 与 verify 的区别
目前注释较详细，是为了帮助理解模块逻辑。
9. CRUD 层
文件：app/crud/user.py
已实现：create_user()
包含：hash_password、User ORM 创建、db.add、db.commit、db.refresh
用户开始理解 ORM 数据流：
Schema
↓
ORM对象
↓
Session
↓
commit
↓
MySQL
并理解：db.refresh() 是从数据库同步完整对象。
10. API 层
文件：app/api/user.py
正在实现：POST /register
已经使用：APIRouter、Depends(get_db)、response_model、status_code=202
用户已经开始真正接触：FastAPI 依赖注入

---
当前开发习惯
用户要求：一次不要给太多内容、采用“小步开发”、一个模块一个模块推进、给明确文件位置与任务拆解、保留自己编码过程
ChatGPT 主要负责：工程规划、任务拆解、Debug、代码审查、解释原理