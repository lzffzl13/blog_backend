from sqlalchemy import Column,Integer,String,DateTime,func,DateTime,Text,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.db.session import Base
from datetime import datetime

class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True,index=True)
    title: Mapped[str] = mapped_column(String(255),index=True)
    content: Mapped[str] = mapped_column(Text,nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime,default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime,default=func.now(),onupdate=func.now())

    author = relationship("User", back_populates="articles")