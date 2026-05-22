import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user import create_user
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
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
