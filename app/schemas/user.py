from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(
        ..., min_length=1, max_length=50, description="Username", examples=["testuser"]
    )
    email: EmailStr = Field(
        ..., description="Email address", examples=["testuser@example.com"]
    )
    password: str = Field(
        ..., min_length=8, max_length=255, description="Password", examples=["password123"]
    )


class UserResponse(BaseModel):
    id: int
    username: str = Field(
        ..., min_length=1, max_length=50, description="Username", examples=["testuser"]
    )
    email: EmailStr = Field(
        ..., description="Email address", examples=["testuser@example.com"]
    )
    role: str = Field(..., description="User role", examples=["user"])

    model_config = ConfigDict(from_attributes=True)


class UserUpdatePassword(BaseModel):
    old_password: str = Field(
        ..., min_length=8, max_length=255, description="Current password", examples=["oldpass123"]
    )
    new_password: str = Field(
        ..., min_length=8, max_length=255, description="New password", examples=["newpass456"]
    )
