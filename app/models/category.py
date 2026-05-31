from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, comment="分类名称")
    description: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="分类描述")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    articles = relationship("Article", back_populates="category")
