import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud.user import create_user, delete_user, update_user_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdatePassword

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """
    注册新用户
    如果已存在,返回409错误
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


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.put("/me/password")
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


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除当前用户"""
    delete_user(db=db, user=current_user)
    logger.info("User deleted | user_id=%d | username='%s'", current_user.id, current_user.username)
    return None
