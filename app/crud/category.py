import logging

from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

logger = logging.getLogger(__name__)


def get_categories(db: Session, owner_id: int | None = None, skip: int = 0, limit: int = 100) -> list[Category]:
    query = db.query(Category)
    if owner_id is not None:
        query = query.filter(Category.owner_id == owner_id)
    return query.offset(skip).limit(limit).all()


def get_category_by_id(db: Session, category_id: int) -> Category | None:
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_by_name(db: Session, owner_id: int, name: str) -> Category | None:
    return db.query(Category).filter(Category.owner_id == owner_id, Category.name == name).first()


def create_category(db: Session, category: CategoryCreate, owner_id: int) -> Category:
    db_category = Category(name=category.name, description=category.description, owner_id=owner_id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    logger.info("Category created | id=%d | name='%s' | owner_id=%d", db_category.id, db_category.name, owner_id)
    return db_category


def update_category(db: Session, category_id: int, category: CategoryUpdate) -> Category | None:
    db_category = get_category_by_id(db, category_id)
    if not db_category:
        logger.warning("Category not found for update | id=%d", category_id)
        return None

    update_data = category.model_dump(exclude_unset=True)
    if not update_data:
        return db_category

    for field, value in update_data.items():
        setattr(db_category, field, value)

    db.commit()
    db.refresh(db_category)
    logger.info("Category updated | id=%d | name='%s'", category_id, db_category.name)
    return db_category


def delete_category(db: Session, category_id: int) -> Category | None:
    db_category = get_category_by_id(db, category_id)
    if not db_category:
        logger.warning("Attempt to delete non-existent category | id=%d", category_id)
        return None

    db.delete(db_category)
    db.commit()
    logger.info("Category deleted | id=%d | name='%s'", category_id, db_category.name)
    return db_category
