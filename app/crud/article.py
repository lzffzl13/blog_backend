import logging
from sqlalchemy.orm import Session
from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate

logger = logging.getLogger(__name__)

def get_articles(db: Session, skip: int = 0, limit: int = 10):
    """获取文章分页"""
    if skip < 0:
        skip = 0
    if limit < 1:
        limit = 10
    total = db.query(Article).count()
    article =db.query(Article).offset(skip).limit(limit).all()
    return total, article

def get_article_by_id(db: Session, article_id: int) -> Article | None:
    """根据ID获取文章,如果不存在返回None"""
    return db.query(Article).filter(Article.id == article_id).first()


def create_article(db: Session, article: ArticleCreate, author_id: int) -> Article:
    """创建文章"""
    db_article = Article(
        title=article.title,
        content=article.content,
        author_id=author_id
    )

    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    logger.info("Article created | id=%d | title='%s' | author_id=%d",
                db_article.id, db_article.title, author_id)
    return db_article


def update_article(db: Session, article_id: int, article: ArticleUpdate) -> Article | None:
    """更新文章"""
    db_article = get_article_by_id(db, article_id)
    if not db_article:
        logger.warning
        ("Article not found for update | id=%d", article_id)
        return None
    
    update_data = article.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_article, field, value)

    db.commit()
    db.refresh(db_article)
    logger.info("Article updated | id=%d | title='%s'", article_id, db_article.title)
    return db_article


def delete_article(db: Session, article_id: int) -> Article | None:
    """删除文章"""
    db_article = get_article_by_id(db, article_id)
    if not db_article:
        logger.warning("Attempt to delete non-existent article | id=%d", article_id)
        return None
    
    db.delete(db_article)
    db.commit()
    logger.info("Article deleted | id=%d | title='%s'", article_id, db_article.title)
    return db_article