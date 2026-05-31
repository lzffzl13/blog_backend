from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, comment="标签名称")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    articles = relationship("Article", secondary="article_tags", back_populates="tags")
