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
    summary="娉ㄥ唽鏂扮敤鎴?",
    description="浣跨敤鐢ㄦ埛鍚嶃€侀偖绠卞拰瀵嗙爜娉ㄥ唽鏂扮敤鎴枫€傚鏋滅敤鎴峰悕鎴栭偖绠卞凡琚敞鍐岋紝杩斿洖 409 鍐茬獊閿欒銆?",
)
def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """
    娉ㄥ唽鏂扮敤鎴?
    濡傛灉宸插瓨鍦?杩斿洖409閿欒
    """
    user = create_user(db=db, user_create=user_create)
    if user is None:
        logger.warning(
            "Registration failed: duplicate user | username='%s' email='%s'",
            user_create.username,
            user_create.email,
        )
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="鐢ㄦ埛鍚嶆垨閭宸茶娉ㄥ唽")
    logger.info("Registration successful | id=%d | username='%s'", user.id, user.username)
    return user


@router.get(
    "/me",
    response_model=UserResponse,
    summary="鑾峰彇褰撳墠鐢ㄦ埛淇℃伅",
    description="鑾峰彇褰撳墠鐧诲綍鐢ㄦ埛鐨勮缁嗕俊鎭€傞渶瑕佹彁渚涙湁鏁堢殑 JWT Token銆?",
)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """鑾峰彇褰撳墠鐢ㄦ埛淇℃伅"""
    return current_user


@router.put(
    "/me/password",
    summary="淇敼褰撳墠鐢ㄦ埛瀵嗙爜",
    description="淇敼褰撳墠鐧诲綍鐢ㄦ埛鐨勫瘑鐮併€傞渶瑕佹彁渚涙棫瀵嗙爜鍜屾柊瀵嗙爜锛屾棫瀵嗙爜楠岃瘉閫氳繃鍚庢墠鑳戒慨鏀广€?",
)
def change_password(
    password_data: UserUpdatePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """淇敼褰撳墠鐢ㄦ埛瀵嗙爜"""
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="鏃у瘑鐮佷笉姝ｇ‘")
    logger.info("Password changed successfully | user_id=%d", current_user.id)
    return {"detail": "瀵嗙爜淇敼鎴愬姛"}


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="鍒犻櫎褰撳墠鐢ㄦ埛",
    description="鍒犻櫎褰撳墠鐧诲綍鐨勭敤鎴疯处鍙枫€傛鎿嶄綔涓嶅彲鎾ら攢銆?",
)
async def delete_current_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
):
    """鍒犻櫎褰撳墠鐢ㄦ埛"""
    article_ids = [article.id for article in current_user.articles]
    delete_user(db=db, user=current_user)
    for article_id in article_ids:
        await delete_cached_article(redis, article_id)
    if article_ids:
        await increment_list_version(redis)
    logger.info("User deleted | user_id=%d | username='%s'", current_user.id, current_user.username)
    return None
