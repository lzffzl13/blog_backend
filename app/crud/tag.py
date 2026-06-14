import logging

from sqlalchemy.orm import Session

from app.models.tag import Tag
from app.schemas.tag import TagCreate

logger = logging.getLogger(__name__)


def get_tags(db: Session, owner_id: int | None = None, skip: int = 0, limit: int = 100) -> list[Tag]:
    query = db.query(Tag)
    if owner_id is not None:
        query = query.filter(Tag.owner_id == owner_id)
    return query.offset(skip).limit(limit).all()


def get_tag_by_id(db: Session, tag_id: int) -> Tag | None:
    return db.query(Tag).filter(Tag.id == tag_id).first()


def get_tag_by_name(db: Session, owner_id: int, name: str) -> Tag | None:
    return db.query(Tag).filter(Tag.owner_id == owner_id, Tag.name == name).first()


def create_tag(db: Session, tag: TagCreate, owner_id: int) -> Tag:
    db_tag = Tag(name=tag.name, owner_id=owner_id)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    logger.info("Tag created | id=%d | name='%s' | owner_id=%d", db_tag.id, db_tag.name, owner_id)
    return db_tag


def delete_tag(db: Session, tag_id: int) -> Tag | None:
    db_tag = get_tag_by_id(db, tag_id)
    if not db_tag:
        logger.warning("Attempt to delete non-existent tag | id=%d", tag_id)
        return None

    db.delete(db_tag)
    db.commit()
    logger.info("Tag deleted | id=%d | name='%s'", tag_id, db_tag.name)
    return db_tag
