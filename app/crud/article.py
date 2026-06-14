import logging

from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.category import Category
from app.models.tag import Tag
from app.schemas.article import ArticleCreate, ArticleUpdate

logger = logging.getLogger(__name__)


def get_articles(db: Session, skip: int = 0, limit: int = 10):
    if skip < 0:
        skip = 0
    if limit < 1:
        limit = 10
    total = db.query(Article).count()
    article = db.query(Article).order_by(Article.created_at.desc()).offset(skip).limit(limit).all()
    return total, article


def get_article_by_id(db: Session, article_id: int) -> Article | None:
    return db.query(Article).filter(Article.id == article_id).first()


def _get_accessible_category(
    db: Session,
    category_id: int,
    owner_id: int,
    actor_is_admin: bool,
) -> Category | None:
    if actor_is_admin:
        return db.query(Category).filter(Category.id == category_id).first()
    return (
        db.query(Category)
        .filter(Category.id == category_id, Category.owner_id == owner_id)
        .first()
    )


def _get_accessible_tags(
    db: Session,
    tag_ids: list[int],
    owner_id: int,
    actor_is_admin: bool,
) -> list[Tag]:
    query = db.query(Tag).filter(Tag.id.in_(tag_ids))
    if not actor_is_admin:
        query = query.filter(Tag.owner_id == owner_id)
    return query.all()


def create_article(
    db: Session,
    article: ArticleCreate,
    author_id: int,
    actor_is_admin: bool = False,
) -> Article:
    if article.category_id is not None and _get_accessible_category(
        db,
        article.category_id,
        author_id,
        actor_is_admin,
    ) is None:
        raise ValueError("Category does not belong to the current user")

    db_article = Article(
        title=article.title,
        content=article.content,
        author_id=author_id,
        category_id=article.category_id,
    )
    if article.tag_ids:
        tags = _get_accessible_tags(db, article.tag_ids, author_id, actor_is_admin)
        if len(tags) != len(set(article.tag_ids)):
            raise ValueError("One or more tags do not belong to the current user")
        db_article.tags = tags

    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    logger.info(
        "Article created | id=%d | title='%s' | author_id=%d",
        db_article.id,
        db_article.title,
        author_id,
    )
    return db_article


def update_article(
    db: Session,
    article_id: int,
    article: ArticleUpdate,
    actor_is_admin: bool = False,
) -> Article | None:
    db_article = get_article_by_id(db, article_id)
    if not db_article:
        logger.warning("Article not found for update | id=%d", article_id)
        return None

    update_data = article.model_dump(exclude_unset=True)

    if "category_id" in update_data and update_data["category_id"] is not None:
        if _get_accessible_category(
            db,
            update_data["category_id"],
            db_article.author_id,
            actor_is_admin,
        ) is None:
            raise ValueError("Category does not belong to the current user")

    tag_ids = update_data.pop("tag_ids", None)
    if tag_ids is not None:
        tags = _get_accessible_tags(db, tag_ids, db_article.author_id, actor_is_admin)
        if len(tags) != len(set(tag_ids)):
            raise ValueError("One or more tags do not belong to the current user")
        db_article.tags = tags

    for field, value in update_data.items():
        setattr(db_article, field, value)

    db.commit()
    db.refresh(db_article)
    logger.info("Article updated | id=%d | title='%s'", article_id, db_article.title)
    return db_article


def delete_article(db: Session, article_id: int) -> Article | None:
    db_article = get_article_by_id(db, article_id)
    if not db_article:
        logger.warning("Attempt to delete non-existent article | id=%d", article_id)
        return None

    db.delete(db_article)
    db.commit()
    logger.info("Article deleted | id=%d | title='%s'", article_id, db_article.title)
    return db_article
