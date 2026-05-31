from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.category import CategoryResponse
from app.schemas.tag import TagResponse


class ArticleCreate(BaseModel):
    """创建文章请求体"""

    title: str = Field(..., min_length=3, max_length=200, description="文章标题(3-200字)")
    content: str = Field(..., min_length=10, description="文章内容(至少10个字)")
    category_id: int | None = Field(None, description="文章分类ID")
    tag_ids: list[int] | None = Field(None, description="文章标签ID列表")


class ArticleUpdate(BaseModel):
    """更新文章请求体"""

    title: str | None = Field(None, min_length=3, max_length=200, description="文章标题(3-200字)")
    content: str | None = Field(None, min_length=10, description="文章内容(至少10个字)")
    category_id: int | None = Field(None, description="文章分类ID")
    tag_ids: list[int] | None = Field(None, description="文章标签ID列表")


class ArticleResponse(BaseModel):
    """文章响应体"""

    id: int
    title: str
    content: str
    author_id: int
    category_id: int | None
    category: CategoryResponse | None
    tags: list[TagResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ArticleListResponse(BaseModel):
    """文章列表响应体"""

    items: list[ArticleResponse]
    total: int
    skip: int
    limit: int
