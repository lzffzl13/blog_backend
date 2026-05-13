from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password

def create_user(db: Session, user_create: UserCreate) -> User:
    """创建新用户并保存到数据库"""
    hashed_password = hash_password(user_create.password)

    db_user = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)  

    return db_user