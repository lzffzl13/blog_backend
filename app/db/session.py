from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,DeclarativeBase,Session
from typing import Generator
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

#负责与数据库建立连接
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,     #连接前置ping
    pool_size=20,           #连接池中的最大连接数
    max_overflow=10,        #连接池中连接数最大overflow
    pool_recycle=3600,      #连接回收时间
    pool_timeout=30,        #超时等待时间
    echo=True               #显示SQL语句日志，开发环境建议开启，生产环境建议关闭
)

#创建会话工厂
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

#Base基类
class Base(DeclarativeBase):
    pass

#依赖注入函数，提供数据库会话
def get_db()->  Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
