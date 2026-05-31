from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求体"""
    username: str = Field(
        ..., min_length=1, max_length=50, description="用户名", examples=["testuser"]
    )
    password: str = Field(
        ..., min_length=1, max_length=255, description="密码", examples=["password123"]
    )


class Token(BaseModel):
    """登录响应体"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    """刷新Token请求体"""
    refresh_token: str = Field(
        ..., description="刷新Token", examples=["eyJhbGciOiJIUzI1NiIs..."]
    )

class TokenPayload(BaseModel):
    """JWT 解析后的Payload"""
    sub: str
    exp: int
