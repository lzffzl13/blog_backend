import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from jwt import ExpiredSignatureError, InvalidTokenError
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.core.rate_limit import check_login_rate_limit
from app.core.redis import get_redis
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.crud.user import get_user_by_username
from app.db.session import get_db
from app.schemas.auth import LoginRequest, RefreshTokenRequest, Token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=Token,
    summary="用户登录",
    description="使用用户名和密码进行登录，验证通过后返回 access token 和 refresh token。包含登录频率限制。",
)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> Token:
    """用户登录,验证用户名和密码,返回access token和refresh token"""
    await check_login_rate_limit(redis, request)
    user = get_user_by_username(db, login_data.username)
    if not user:
        logger.warning("Login failed: user not found  | username='%s'", login_data.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    if not verify_password(login_data.password, user.hashed_password):
        logger.warning("Login failed: incorrect password  | username='%s'", login_data.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    token_data = {"sub": user.username}
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)

    logger.info("User logged in | id=%d | username='%s'", user.id, user.username)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post(
    "/refresh",
    response_model=Token,
    summary="刷新 Access Token",
    description="使用 refresh token 获取新的 access token。refresh token 过期或无效时会返回 401 错误。",
)
def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """刷新access token"""
    try:
        payload = decode_token(refresh_data.refresh_token)
    except ExpiredSignatureError:
        raise HTTPException(  # noqa: B904
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token 已过期",
        )
    except InvalidTokenError:
        raise HTTPException(  # noqa: B904
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 refresh token",
        )

    username: str | None = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token 中缺少用户标识",
        )

    user = get_user_by_username(db, username=username)
    if user is None:
        logger.warning("Refresh token failed: user not found  | username='%s'", username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    new_access_token = create_access_token(data={"sub": user.username})
    logger.info("Access token refreshed | id=%d | username='%s'", user.id, user.username)
    return {
        "access_token": new_access_token,
        "refresh_token": refresh_data.refresh_token,  # 刷新时不更换refresh token
        "token_type": "bearer",
    }
