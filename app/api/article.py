import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud.article import (
    create_article,
    delete_article,
    get_article_by_id,
    get_articles,
    update_article,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.article import (
    ArticleCreate,
    ArticleListResponse,
    ArticleResponse,
    ArticleUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/articles", tags=["articles"])


# get /articles 获取文章列表
@router.get("", response_model=ArticleListResponse)
def get_articles_list(
    skip: int = Query(0, ge=0, description="跳过条数"),
    limit: int = Query(10, ge=1, le=100, description="返回条数"),
    db: Session = Depends(get_db),
):
    """获取文章列表"""
    total, articles = get_articles(db=db, skip=skip, limit=limit)
    return {"items": articles, "total": total, "skip": skip, "limit": limit}


# post /articles 创建文章
@router.post("", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
def create_new_article(
    article: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建新文章"""
    db_article = create_article(db=db, article=article, author_id=current_user.id)
    logger.info(
        "Article API: created | id=%d | title='%s' | author_id=%d",
        db_article.id,
        db_article.title,
        current_user.id,
    )
    return db_article


# get /{article_id} 获取文章详情
@router.get("/{article_id}", response_model=ArticleResponse)
def read_article(article_id: int, db: Session = Depends(get_db)):
    """获取文章详情"""
    db_article = get_article_by_id(db, article_id=article_id)
    if not db_article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
    return db_article


# put /{article_id} 更新文章
@router.put("/{article_id}", response_model=ArticleResponse)
def update_existing_article(
    article_id: int,
    article: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新文章"""
    db_article = get_article_by_id(db, article_id=article_id)
    if not db_article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
    if db_article.author_id != current_user.id:
        logger.warning(
            "Update forbidden | article_id=%d | requester_id=%d | author_id=%d",
            article_id,
            current_user.id,
            db_article.author_id,
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有权限修改此文章")
    db_article = update_article(db, article_id=article_id, article=article)
    return db_article


# delete /{article_id} 删除文章
@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_article(
    article_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """删除文章"""
    db_article = get_article_by_id(db, article_id=article_id)
    if not db_article:
        logger.warning("Delete article failed: not found | id=%d", article_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
    if db_article.author_id != current_user.id:
        logger.warning(
            "Delete forbidden | article_id=%d | requester_id=%d | author_id=%d",
            article_id,
            current_user.id,
            db_article.author_id,
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有权限删除此文章")
    delete_article(db, article_id=article_id)
    logger.info("Article API: deleted | id=%d", article_id)
    return None
