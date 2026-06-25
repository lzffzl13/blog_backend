import logging

from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.redis import get_redis
from app.crud.user import create_user, delete_user, update_user_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdatePassword
from app.services.article_cache import delete_cached_article, increment_list_version

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="注册新用户",
    description="使用用户名、邮箱和密码注册新用户。如果用户名或邮箱已被注册，返回 409 冲突错误。",
)
def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """
    注册新用户
    如果已存在，返回409错误
    """
    user = create_user(db=db, user_create=user_create)
    if user is None:
        logger.warning(
            "Registration failed: duplicate user | username='%s' email='%s'",
            user_create.username,
            user_create.email,
        )
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名或邮箱已被注册")
    logger.info("Registration successful | id=%d | username='%s'", user.id, user.username)
    return user


@router.get(
    "/me",
    response_model=UserResponse,
    summary="获取当前用户信息",
    description="获取当前登录用户的详细信息。需要提供有效的 JWT Token。",
)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.put(
    "/me/password",
    summary="修改当前用户密码",
    description="修改当前登录用户的密码。需要提供旧密码和新密码，旧密码验证通过后才能修改。",
)
def change_password(
    password_data: UserUpdatePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """修改当前用户密码"""
    success = update_user_password(
        db=db,
        user=current_user,
        old_password=password_data.old_password,
        new_password=password_data.new_password,
    )
    if not success:
        logger.warning(
            "Password change failed: incorrect old password | user_id=%d",
            current_user.id,
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码不正确")
    logger.info("Password changed successfully | user_id=%d", current_user.id)
    return {"detail": "密码修改成功"}


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除当前用户",
    description="删除当前登录的用户账号。此操作不可撤销。",
)
async def delete_current_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
):
    """删除当前用户"""
    article_ids = [article.id for article in current_user.articles]
    delete_user(db=db, user=current_user)
    for article_id in article_ids:
        await delete_cached_article(redis, article_id)
    if article_ids:
        await increment_list_version(redis)
    logger.info("User deleted | user_id=%d | username='%s'", current_user.id, current_user.username)
    return None
