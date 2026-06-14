from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Category name", examples=["Tech"])
    description: str | None = Field(
        None,
        max_length=255,
        description="Category description",
        examples=["Technical posts"],
    )


class CategoryUpdate(BaseModel):
    name: str | None = Field(
        None,
        min_length=1,
        max_length=50,
        description="Category name",
        examples=["Life"],
    )
    description: str | None = Field(
        None,
        max_length=255,
        description="Category description",
        examples=["Lifestyle posts"],
    )


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
