import logging

from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

logger = logging.getLogger(__name__)


def get_categories(db: Session, skip: int = 0, limit: int = 100) -> list[Category]:
    """获取分类列表"""
    return db.query(Category).offset(skip).limit(limit).all()


def get_category_by_id(db: Session, category_id: int) -> Category | None:
    """根据ID获取分类,如果不存在返回None"""
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_by_name(db: Session, name: str) -> Category | None:
    """根据名称获取分类,如果不存在返回None"""
    return db.query(Category).filter(Category.name == name).first()


def create_category(db: Session, category: CategoryCreate) -> Category:
    """创建分类"""
    db_category = Category(name=category.name, description=category.description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    logger.info("Category created | id=%d | name='%s'", db_category.id, db_category.name)
    return db_category


def update_category(db: Session, category_id: int, category: CategoryUpdate) -> Category | None:
    """更新分类"""
    db_category = get_category_by_id(db, category_id)
    if not db_category:
        logger.warning("Category not found for update | id=%d", category_id)
        return None

    update_data = category.model_dump(exclude_unset=True)
    if not update_data:
        logger.warning("Category update with empty data | id=%d", category_id)
        return db_category

    for field, value in update_data.items():
        setattr(db_category, field, value)

    db.commit()
    db.refresh(db_category)
    logger.info("Category updated | id=%d | name='%s'", category_id, db_category.name)
    return db_category


def delete_category(db: Session, category_id: int) -> Category | None:
    """删除分类"""
    db_category = get_category_by_id(db, category_id)
    if not db_category:
        logger.warning("Attempt to delete non-existent category | id=%d", category_id)
        return None

    db.delete(db_category)
    db.commit()
    logger.info("Category deleted | id=%d | name='%s'", category_id, db_category.name)
    return db_category
