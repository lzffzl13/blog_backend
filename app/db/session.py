from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# 负责与数据库建立连接
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # 连接前置ping
    pool_size=20,  # 连接池中的最大连接数
    max_overflow=10,  # 连接池中连接数最大overflow
    pool_recycle=3600,  # 连接回收时间
    pool_timeout=30,  # 超时等待时间
    echo=True,  # 显示SQL语句日志，开发环境建议开启，生产环境建议关闭
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """SQLite需要启用外键支持"""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base基类
class Base(DeclarativeBase):
    pass


# 依赖注入函数，提供数据库会话
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
