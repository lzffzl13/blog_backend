import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.category import (
    create_category,
    delete_category,
    get_categories,
    get_category_by_id,
    get_category_by_name,
    update_category,
)
from app.db.session import get_db
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/categories", tags=["categories"])


@router.get(
    "",
    response_model=list[CategoryResponse],
    summary="获取分类列表",
    description="获取所有分类的列表，支持分页参数 skip 和 limit。",
)
def get_categories_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取分类列表"""
    return get_categories(db, skip=skip, limit=limit)


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="获取分类详情",
    description="根据分类 ID 获取分类的详细信息。如果分类不存在，返回 404 错误。",
)
def read_category(category_id: int, db: Session = Depends(get_db)):
    """获取分类详情"""
    db_category = get_category_by_id(db, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在")
    return db_category


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建分类",
    description="创建一个新的分类。如果分类名称已存在，返回 409 冲突错误。",
)
def create_new_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """创建分类"""
    existing = get_category_by_name(db, name=category.name)
    if existing:
        logger.warning(
            "Category creation failed: duplicate name | name='%s'", category.name
        )
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="分类已存在")
    db_category = create_category(db=db, category=category)
    logger.info("Category API: created | id=%d | name='%s'", db_category.id, db_category.name)
    return db_category


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="更新分类",
    description="更新指定分类的名称或描述。如果分类不存在，返回 404 错误。",
)
def update_existing_category(
    category_id: int, category: CategoryUpdate, db: Session = Depends(get_db)
):
    """更新分类"""
    db_category = update_category(db, category_id=category_id, category=category)
    if not db_category:
        logger.warning("Category update failed: not found | id=%d", category_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在")
    logger.info("Category API: updated | id=%d | name='%s'", category_id, db_category.name)
    return db_category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除分类",
    description="删除指定分类。如果分类不存在，返回 404 错误。",
)
def delete_existing_category(category_id: int, db: Session = Depends(get_db)):
    """删除分类"""
    db_category = delete_category(db, category_id=category_id)
    if not db_category:
        logger.warning("Category delete failed: not found | id=%d", category_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在")
    logger.info("Category API: deleted | id=%d", category_id)
    return None
