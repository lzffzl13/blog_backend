import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud.article import get_article_by_id
from app.crud.comment import (
    create_comment,
    delete_comment,
    get_comment_by_id,
    get_comments_by_article,
    update_comment,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/articles/{article_id}/comments", tags=["comments"])


@router.get(
    "",
    response_model=list[CommentResponse],
    summary="获取评论列表",
    description="获取指定文章的所有评论列表，支持分页参数 skip 和 limit。如果文章不存在，返回 404 错误。",
)
def get_comments_list(
    article_id: int,
    skip: int = Query(0, ge=0, description="跳过条数"),
    limit: int = Query(20, ge=1, le=100, description="返回条数"),
    db: Session = Depends(get_db),
):
    """获取文章评论列表"""
    article = get_article_by_id(db, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
    return get_comments_by_article(db, article_id=article_id, skip=skip, limit=limit)


@router.post(
    "",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建评论",
    description="在指定文章下创建一条评论。需要登录认证。如果文章不存在，返回 404 错误。",
)
def create_new_comment(
    article_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建评论"""
    article = get_article_by_id(db, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
    db_comment = create_comment(
        db=db, comment=comment, article_id=article_id, author_id=current_user.id
    )
    logger.info(
        "Comment API: created | id=%d | article_id=%d | author_id=%d",
        db_comment.id,
        article_id,
        current_user.id,
    )
    return db_comment


@router.get(
    "/{comment_id}",
    response_model=CommentResponse,
    summary="获取评论详情",
    description="根据评论 ID 获取评论的详细信息。如果评论不存在或不属于指定文章，返回 404 错误。",
)
def read_comment(article_id: int, comment_id: int, db: Session = Depends(get_db)):
    """获取评论详情"""
    db_comment = get_comment_by_id(db, comment_id)
    if not db_comment or db_comment.article_id != article_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")
    return db_comment


@router.put(
    "/{comment_id}",
    response_model=CommentResponse,
    summary="更新评论",
    description="更新指定评论的内容。只能更新自己的评论，非作者尝试更新会返回 403 错误。需要登录认证。",
)
def update_existing_comment(
    article_id: int,
    comment_id: int,
    comment: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新评论"""
    db_comment = get_comment_by_id(db, comment_id)
    if not db_comment or db_comment.article_id != article_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")
    if db_comment.author_id != current_user.id:
        logger.warning(
            "Comment update forbidden | comment_id=%d | requester_id=%d | author_id=%d",
            comment_id,
            current_user.id,
            db_comment.author_id,
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有权限修改此评论")
    db_comment = update_comment(db, comment_id=comment_id, comment=comment)
    logger.info("Comment API: updated | id=%d", comment_id)
    return db_comment


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除评论",
    description="删除指定评论。只能删除自己的评论，非作者尝试删除会返回 403 错误。需要登录认证。",
)
def delete_existing_comment(
    article_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除评论"""
    db_comment = get_comment_by_id(db, comment_id)
    if not db_comment or db_comment.article_id != article_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")
    if db_comment.author_id != current_user.id:
        logger.warning(
            "Comment delete forbidden | comment_id=%d | requester_id=%d | author_id=%d",
            comment_id,
            current_user.id,
            db_comment.author_id,
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有权限删除此评论")
    delete_comment(db, comment_id=comment_id)
    logger.info("Comment API: deleted | id=%d", comment_id)
    return None
