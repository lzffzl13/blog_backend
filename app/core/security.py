from datetime import UTC, datetime, timedelta
from uuid import uuid4

import bcrypt
import jwt
from jwt import InvalidTokenError

from app.core.config import settings

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def hash_password(password: str) -> str:
    """哈希密码"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否匹配"""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def _create_token(data: dict, token_type: str, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_delta
    to_encode.update(
        {
            "exp": expire,
            "jti": str(uuid4()),
            "token_type": token_type,
        }
    )
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """签发access token"""
    ttl = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token(data=data, token_type=ACCESS_TOKEN_TYPE, expires_delta=ttl)


def create_refresh_token(data: dict) -> str:
    """签发refresh token，7天过期"""
    return _create_token(
        data=data,
        token_type=REFRESH_TOKEN_TYPE,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str, expected_type: str | None = None) -> dict:
    """解码token，返回payload"""
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    token_type = payload.get("token_type")
    if expected_type and token_type != expected_type:
        raise InvalidTokenError(f"Invalid token type: expected {expected_type}")
    return payload
