from pydantic import BaseModel,EmailStr
from typing import Optional

#用户注册请求体
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

#用户响应结构（不含密码）
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True