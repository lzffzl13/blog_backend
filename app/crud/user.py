import logging

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)


def get_user_by_username_or_email(db: Session, username: str, email: str) -> User | None:
    return db.query(User).filter((User.username == username) | (User.email == email)).first()


def create_user(db: Session, user_create: UserCreate) -> User | None:
    """创建新用户并保存到数据库"""
    existing_user = get_user_by_username_or_email(db, user_create.username, user_create.email)
    if existing_user:
        logger.warning(
            "Registration attempt with existing username/email | username='%s' email='%s'",
            user_create.username,
            user_create.email,
        )
        return None

    hashed_password = hash_password(user_create.password)

    db_user = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=hashed_password,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info("User registered | id=%d | username='%s'", db_user.id, db_user.username)
    return db_user
