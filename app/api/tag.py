import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.tag import (
    create_tag,
    delete_tag,
    get_tag_by_id,
    get_tag_by_name,
    get_tags,
)
from app.db.session import get_db
from app.schemas.tag import TagCreate, TagResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tags", tags=["tags"])


@router.get(
    "",
    response_model=list[TagResponse],
    summary="获取标签列表",
    description="获取所有标签的列表，支持分页参数 skip 和 limit。",
)
def get_tags_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取标签列表"""
    return get_tags(db, skip=skip, limit=limit)


@router.get(
    "/{tag_id}",
    response_model=TagResponse,
    summary="获取标签详情",
    description="根据标签 ID 获取标签的详细信息。如果标签不存在，返回 404 错误。",
)
def read_tag(tag_id: int, db: Session = Depends(get_db)):
    """获取标签详情"""
    db_tag = get_tag_by_id(db, tag_id=tag_id)
    if not db_tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="标签不存在")
    return db_tag


@router.post(
    "",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建标签",
    description="创建一个新的标签。如果标签名称已存在，返回 409 冲突错误。",
)
def create_new_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """创建标签"""
    existing = get_tag_by_name(db, name=tag.name)
    if existing:
        logger.warning("Tag creation failed: duplicate name | name='%s'", tag.name)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="标签已存在")
    db_tag = create_tag(db=db, tag=tag)
    logger.info("Tag API: created | id=%d | name='%s'", db_tag.id, db_tag.name)
    return db_tag


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除标签",
    description="删除指定标签。如果标签不存在，返回 404 错误。",
)
def delete_existing_tag(tag_id: int, db: Session = Depends(get_db)):
    """删除标签"""
    db_tag = delete_tag(db, tag_id=tag_id)
    if not db_tag:
        logger.warning("Tag delete failed: not found | id=%d", tag_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="标签不存在")
    logger.info("Tag API: deleted | id=%d", tag_id)
    return None
