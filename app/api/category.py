import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin_user
from app.crud.category import (
    create_category,
    delete_category,
    get_categories,
    get_category_by_id,
    get_category_by_name,
    update_category,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
def get_categories_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_categories(db, skip=skip, limit=limit)


@router.get("/{category_id}", response_model=CategoryResponse)
def read_category(category_id: int, db: Session = Depends(get_db)):
    db_category = get_category_by_id(db, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return db_category


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_new_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    existing = get_category_by_name(db, name=category.name)
    if existing:
        logger.warning("Category creation failed: duplicate name | name='%s'", category.name)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")
    db_category = create_category(db=db, category=category)
    logger.info(
        "Category API: created | id=%d | name='%s' | admin_id=%d",
        db_category.id,
        db_category.name,
        current_user.id,
    )
    return db_category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_existing_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    db_category = update_category(db, category_id=category_id, category=category)
    if not db_category:
        logger.warning("Category update failed: not found | id=%d", category_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    logger.info(
        "Category API: updated | id=%d | name='%s' | admin_id=%d",
        category_id,
        db_category.name,
        current_user.id,
    )
    return db_category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    db_category = delete_category(db, category_id=category_id)
    if not db_category:
        logger.warning("Category delete failed: not found | id=%d", category_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    logger.info("Category API: deleted | id=%d | admin_id=%d", category_id, current_user.id)
    return None
