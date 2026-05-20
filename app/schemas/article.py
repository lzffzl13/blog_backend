from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class ArticleCreate(BaseModel):
    """创建文章请求体"""
    title: str = Field(..., min_length=3,max_length=200,description="文章标题(3-200字)")
    content: str = Field(..., min_length=10,description="文章内容(至少10个字)")


class ArticleUpdate(BaseModel):
    """更新文章请求体"""
    title: Optional[str] = Field(None, min_length=3,max_length=200,description="文章标题(3-200字)")
    content: Optional[str] = Field(None, min_length=10,description="文章内容(至少10个字)")

class ArticleResponse(BaseModel):
    """文章响应体"""
    id: int
    title: str
    content: str
    author_id: int         
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ArticleListResponse(BaseModel):
    """文章列表响应体"""
    items: list[ArticleResponse]
    total: int
    skip: int
    limit: int 
