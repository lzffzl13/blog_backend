import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud.tag import create_tag, delete_tag, get_tag_by_id, get_tag_by_name, get_tags
from app.db.session import get_db
from app.models.user import ADMIN_USER_ROLE, User
from app.schemas.tag import TagCreate, TagResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tags", tags=["tags"])


def _ensure_tag_access(tag, current_user: User) -> None:
    if tag.owner_id != current_user.id and current_user.role != ADMIN_USER_ROLE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission to access this tag")


@router.get("", response_model=list[TagResponse])
def get_tags_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    owner_id = None if current_user.role == ADMIN_USER_ROLE else current_user.id
    return get_tags(db, owner_id=owner_id, skip=skip, limit=limit)


@router.get("/{tag_id}", response_model=TagResponse)
def read_tag(tag_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_tag = get_tag_by_id(db, tag_id=tag_id)
    if not db_tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    _ensure_tag_access(db_tag, current_user)
    return db_tag


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_new_tag(
    tag: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = get_tag_by_name(db, owner_id=current_user.id, name=tag.name)
    if existing:
        logger.warning("Tag creation failed: duplicate name | owner_id=%d | name='%s'", current_user.id, tag.name)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tag already exists")
    db_tag = create_tag(db=db, tag=tag, owner_id=current_user.id)
    logger.info("Tag API: created | id=%d | name='%s' | owner_id=%d", db_tag.id, db_tag.name, current_user.id)
    return db_tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_tag = get_tag_by_id(db, tag_id=tag_id)
    if not db_tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    _ensure_tag_access(db_tag, current_user)
    delete_tag(db, tag_id=tag_id)
    return None
