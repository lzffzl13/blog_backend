import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db.session import Base
from sqlalchemy.pool import StaticPool
from app.models.user import User
from app.models.article import Article

@pytest.fixture(scope="function")
def db_session():
    """创建临时SQLite内存数据库,每次测试独立"""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)

    #print("✅ Created tables in SQLite:", list(Base.metadata.tables.keys()))
    
    session = Session(bind=engine)
    yield session

    session.close()
    engine.dispose()
