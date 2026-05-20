import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.schemas.article import ArticleCreate, ArticleResponse, ArticleUpdate, ArticleListResponse
from app.crud.article import (
    get_articles,
    get_article_by_id,
    create_article,
    update_article,
    delete_article
)
from app.db.session import get_db
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()

#get /articles 获取文章列表
@router.get("", response_model=ArticleListResponse)
def get_articles_list(skip: int = Query(0,ge = 0,description = "跳过条数"), 
                      limit: int = Query(10, ge = 1,le = 100,description = "返回条数" ), 
                      db: Session = Depends(get_db)):
    """获取文章列表"""
    total,articles= get_articles(db=db, skip=skip, limit=limit)
    return {
        "items": articles,
        "total": total,
        "skip": skip,
        "limit": limit
    }

#post /articles 创建文章
@router.post(
    "",
    response_model=ArticleResponse,
    status_code=status.HTTP_201_CREATED
    )
#临时设计为需要传入author_id,后续会改为从token中获取
def create_new_article(article: ArticleCreate, author_id: int, db: Session = Depends(get_db)):
    """创建新文章"""
    author = db.query(User).filter(User.id == author_id).first()
    if not author:
        logger.warning("Create article failed: author not found | author_id=%d", author_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作者不存在"
        )
    db_article = create_article(db=db, article=article, author_id=author_id)
    logger.info("Article API: created | id=%d | title='%s'", db_article.id, db_article.title)
    return db_article

#get /{article_id} 获取文章详情
@router.get("/{article_id}", response_model=ArticleResponse)
def read_article(article_id: int, db: Session = Depends(get_db)):
    """获取文章详情"""
    db_article = get_article_by_id(db, article_id=article_id)
    if not db_article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
    return db_article

#put /{article_id} 更新文章
@router.put("/{article_id}", response_model=ArticleResponse)
def update_existing_article(article_id: int, article: ArticleUpdate, db: Session = Depends(get_db)):
    """更新文章"""
    db_article = update_article(db, article_id=article_id, article=article)
    if not db_article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在")
    return db_article

#delete /{article_id} 删除文章
@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_article(article_id: int, db: Session = Depends(get_db)):
    """删除文章"""
    db_article = delete_article(db, article_id=article_id)
    if not db_article:
        logger.warning("Delete article failed: not found | id=%d", article_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    logger.info("Article API: deleted | id=%d", article_id)
    return None
