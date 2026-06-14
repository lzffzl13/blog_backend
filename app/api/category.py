import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud.category import (
    create_category,
    delete_category,
    get_categories,
    get_category_by_id,
    get_category_by_name,
    update_category,
)
from app.db.session import get_db
from app.models.user import ADMIN_USER_ROLE, User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/categories", tags=["categories"])


def _ensure_category_access(category, current_user: User) -> None:
    if category.owner_id != current_user.id and current_user.role != ADMIN_USER_ROLE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission to access this category")


@router.get("", response_model=list[CategoryResponse])
def get_categories_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    owner_id = None if current_user.role == ADMIN_USER_ROLE else current_user.id
    return get_categories(db, owner_id=owner_id, skip=skip, limit=limit)


@router.get("/{category_id}", response_model=CategoryResponse)
def read_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_category = get_category_by_id(db, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    _ensure_category_access(db_category, current_user)
    return db_category


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_new_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = get_category_by_name(db, owner_id=current_user.id, name=category.name)
    if existing:
        logger.warning("Category creation failed: duplicate name | owner_id=%d | name='%s'", current_user.id, category.name)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")
    db_category = create_category(db=db, category=category, owner_id=current_user.id)
    logger.info(
        "Category API: created | id=%d | name='%s' | owner_id=%d",
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
    current_user: User = Depends(get_current_user),
):
    db_category = get_category_by_id(db, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    _ensure_category_access(db_category, current_user)

    if category.name and category.name != db_category.name:
        existing = get_category_by_name(db, owner_id=db_category.owner_id, name=category.name)
        if existing and existing.id != db_category.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")

    updated = update_category(db, category_id=category_id, category=category)
    return updated


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_category = get_category_by_id(db, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    _ensure_category_access(db_category, current_user)
    delete_category(db, category_id=category_id)
    return None
