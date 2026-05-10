from sqlalchemy import Column,Integer,String,DateTime,func
from sqlalchemy.orm import Mapped,mapped_column
from app.db.session import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True,index=True)
    username: Mapped[str] = mapped_column(String(50),unique=True,index=True)
    email: Mapped[str] = mapped_column(String(100),unique=True,index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime,default=func.now())

