from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """鐧诲綍璇锋眰浣?"""

    username: str = Field(
        ..., min_length=1, max_length=50, description="鐢ㄦ埛鍚?", examples=["testuser"]
    )
    password: str = Field(
        ..., min_length=1, max_length=255, description="瀵嗙爜", examples=["password123"]
    )


class Token(BaseModel):
    """鐧诲綍鍝嶅簲浣?"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """鍒锋柊Token璇锋眰浣?"""

    refresh_token: str = Field(
        ..., description="鍒锋柊Token", examples=["eyJhbGciOiJIUzI1NiIs..."]
    )


class LogoutRequest(BaseModel):
    """閫€鍑虹櫥褰曡姹備綋"""

    refresh_token: str | None = Field(
        None,
        description="鍙€夌殑 refresh token锛岀敤浜庡悓鏃跺け鏁?",
        examples=["eyJhbGciOiJIUzI1NiIs..."],
    )


class TokenPayload(BaseModel):
    """JWT 瑙ｆ瀽鍚庣殑Payload"""

    sub: str
    exp: int
    jti: str
    token_type: str
