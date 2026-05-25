from pydantic import BaseModel, ConfigDict, EmailStr, Field


# 用户注册请求体
class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=8, max_length=255, description="密码")


# 用户响应结构（不含密码）
class UserResponse(BaseModel):
    id: int
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")

    model_config = ConfigDict(from_attributes=True)

# 改密码请求体
class UserUpdatePassword(BaseModel):
    old_password: str = Field(..., min_length=8, max_length=255, description="旧密码")
    new_password: str = Field(..., min_length=8, max_length=255, description="新密码")
