import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.core.rate_limit import check_login_rate_limit
from app.core.redis import get_redis
from app.core.security import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.crud.user import get_user_by_username
from app.db.session import get_db
from app.schemas.auth import LoginRequest, LogoutRequest, RefreshTokenRequest, Token
from app.services.auth_tokens import blacklist_token, is_token_blacklisted

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post(
    "/login",
    response_model=Token,
    summary="鐢ㄦ埛鐧诲綍",
    description="浣跨敤鐢ㄦ埛鍚嶅拰瀵嗙爜杩涜鐧诲綍锛岄獙璇侀€氳繃鍚庤繑鍥?access token 鍜?refresh token銆傚寘鍚櫥褰曢鐜囬檺鍒躲€?",
)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> Token:
    """鐢ㄦ埛鐧诲綍,楠岃瘉鐢ㄦ埛鍚嶅拰瀵嗙爜,杩斿洖access token鍜宺efresh token"""
    await check_login_rate_limit(redis, request)
    user = get_user_by_username(db, login_data.username)
    if not user:
        logger.warning("Login failed: user not found  | username='%s'", login_data.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="鐢ㄦ埛鍚嶆垨瀵嗙爜閿欒")

    if not verify_password(login_data.password, user.hashed_password):
        logger.warning("Login failed: incorrect password  | username='%s'", login_data.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="鐢ㄦ埛鍚嶆垨瀵嗙爜閿欒")

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
    summary="鍒锋柊 Access Token",
    description="浣跨敤 refresh token 鑾峰彇鏂扮殑 access token銆俽efresh token 杩囨湡鎴栨棤鏁堟椂浼氳繑鍥?401 閿欒銆?",
)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """鍒锋柊access token"""
    try:
        payload = decode_token(refresh_data.refresh_token, expected_type=REFRESH_TOKEN_TYPE)
    except ExpiredSignatureError:
        raise HTTPException(  # noqa: B904
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token 宸茶繃鏈?",
        )
    except InvalidTokenError:
        raise HTTPException(  # noqa: B904
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="鏃犳晥鐨?refresh token",
        )

    if await is_token_blacklisted(redis, payload):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token 宸插け鏁?",
        )

    username: str | None = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token 涓己灏戠敤鎴锋爣璇?",
        )

    user = get_user_by_username(db, username=username)
    if user is None:
        logger.warning("Refresh token failed: user not found  | username='%s'", username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="鐢ㄦ埛涓嶅瓨鍦?",
        )

    new_access_token = create_access_token(data={"sub": user.username})
    logger.info("Access token refreshed | id=%d | username='%s'", user.id, user.username)
    return {
        "access_token": new_access_token,
        "refresh_token": refresh_data.refresh_token,
        "token_type": "bearer",
    }


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="閫€鍑虹櫥褰?",
    description="灏嗗綋鍓?access token 鍔犲叆黑名单锛屽彲閫夊悓鏃跺け鏁?refresh token銆?",
)
async def logout(
    logout_data: LogoutRequest,
    token: str = Depends(oauth2_scheme),
    redis: Redis = Depends(get_redis),
):
    """灏嗗綋鍓?token 鍔犲叆黑名单"""
    try:
        access_payload = decode_token(token, expected_type=ACCESS_TOKEN_TYPE)
    except ExpiredSignatureError:
        raise HTTPException(  # noqa: B904
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 宸茶繃鏈?",
        )
    except InvalidTokenError:
        raise HTTPException(  # noqa: B904
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="鏃犳晥鐨?Token",
        )

    await blacklist_token(redis, access_payload)

    if logout_data.refresh_token:
        try:
            refresh_payload = decode_token(
                logout_data.refresh_token,
                expected_type=REFRESH_TOKEN_TYPE,
            )
        except ExpiredSignatureError:
            raise HTTPException(  # noqa: B904
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token 宸茶繃鏈?",
            )
        except InvalidTokenError:
            raise HTTPException(  # noqa: B904
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="鏃犳晥鐨?refresh token",
            )

        await blacklist_token(redis, refresh_payload)

    return {"detail": "閫€鍑烘垚鍔?"}
