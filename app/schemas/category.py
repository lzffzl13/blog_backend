from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="分类名称")
    description: str | None = Field(None, max_length=255, description="分类描述")


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50, description="分类名称")
    description: str | None = Field(None, max_length=255, description="分类描述")


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
