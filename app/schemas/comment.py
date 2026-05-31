from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, description="评论内容")


class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, description="评论内容")


class CommentResponse(BaseModel):
    id: int
    content: str
    article_id: int
    author_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
