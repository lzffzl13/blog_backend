import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.core.redis import get_redis
from app.core.security import ACCESS_TOKEN_TYPE, decode_token
from app.crud.user import get_user_by_username
from app.db.session import get_db
from app.models.user import ADMIN_USER_ROLE, User
from app.services.auth_tokens import is_token_blacklisted

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> User:
    """从请求头 Bearer token 中获取当前用户"""
    try:
        payload = decode_token(token, expected_type=ACCESS_TOKEN_TYPE)
    except ExpiredSignatureError:
        raise HTTPException(  # noqa: B904
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError:
        raise HTTPException(  # noqa: B904
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 Token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if await is_token_blacklisted(redis, payload):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 已失效",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str | None = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 中缺少用户标识",
        )

    user = get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != ADMIN_USER_ROLE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
