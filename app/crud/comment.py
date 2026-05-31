import logging

from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate

logger = logging.getLogger(__name__)


def get_comments_by_article(
    db: Session, article_id: int, skip: int = 0, limit: int = 20
) -> list[Comment]:
    """获取文章评论列表"""
    return (
        db.query(Comment)
        .filter(Comment.article_id == article_id)
        .order_by(Comment.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_comment_by_id(db: Session, comment_id: int) -> Comment | None:
    """根据ID获取评论,如果不存在返回None"""
    return db.query(Comment).filter(Comment.id == comment_id).first()


def create_comment(db: Session, comment: CommentCreate, article_id: int, author_id: int) -> Comment:
    """创建评论"""
    db_comment = Comment(
        content=comment.content,
        article_id=article_id,
        author_id=author_id,
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    logger.info(
        "Comment created | id=%d | article_id=%d | author_id=%d",
        db_comment.id,
        article_id,
        author_id,
    )
    return db_comment


def update_comment(db: Session, comment_id: int, comment: CommentUpdate) -> Comment | None:
    """更新评论"""
    db_comment = get_comment_by_id(db, comment_id)
    if not db_comment:
        logger.warning("Comment not found for update | id=%d", comment_id)
        return None

    db_comment.content = comment.content
    db.commit()
    db.refresh(db_comment)
    logger.info("Comment updated | id=%d", comment_id)
    return db_comment


def delete_comment(db: Session, comment_id: int) -> bool:
    """删除评论"""
    db_comment = get_comment_by_id(db, comment_id)
    if not db_comment:
        logger.warning("Attempt to delete non-existent comment | id=%d", comment_id)
        return False

    db.delete(db_comment)
    db.commit()
    logger.info("Comment deleted | id=%d", comment_id)
    return True
