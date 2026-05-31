from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(
        ..., min_length=1, max_length=50, description="分类名称", examples=["技术"]
    )
    description: str | None = Field(
        None, max_length=255, description="分类描述", examples=["技术相关文章"]
    )


class CategoryUpdate(BaseModel):
    name: str | None = Field(
        None, min_length=1, max_length=50, description="分类名称", examples=["生活"]
    )
    description: str | None = Field(
        None, max_length=255, description="分类描述", examples=["生活相关文章"]
    )


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
