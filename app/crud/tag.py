import logging

from sqlalchemy.orm import Session

from app.models.tag import Tag
from app.schemas.tag import TagCreate

logger = logging.getLogger(__name__)


def get_tags(db: Session, skip: int = 0, limit: int = 100) -> list[Tag]:
    """获取标签列表"""
    return db.query(Tag).offset(skip).limit(limit).all()


def get_tag_by_id(db: Session, tag_id: int) -> Tag | None:
    """根据ID获取标签,如果不存在返回None"""
    return db.query(Tag).filter(Tag.id == tag_id).first()


def get_tag_by_name(db: Session, name: str) -> Tag | None:
    """根据名称获取标签,如果不存在返回None"""
    return db.query(Tag).filter(Tag.name == name).first()


def create_tag(db: Session, tag: TagCreate) -> Tag:
    """创建标签"""
    db_tag = Tag(name=tag.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    logger.info("Tag created | id=%d | name='%s'", db_tag.id, db_tag.name)
    return db_tag


def delete_tag(db: Session, tag_id: int) -> None:
    """删除标签"""
    db_tag = get_tag_by_id(db, tag_id)
    if not db_tag:
        logger.warning("Attempt to delete non-existent tag | id=%d", tag_id)
        return None

    db.delete(db_tag)
    db.commit()
    logger.info("Tag deleted | id=%d | name='%s'", tag_id, db_tag.name)
    return None
