import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.redis import get_redis
from app.crud.article import (
    create_article,
    delete_article,
    get_article_by_id,
    get_articles,
    update_article,
)
from app.db.session import get_db
from app.models.user import ADMIN_USER_ROLE, User
from app.schemas.article import (
    ArticleCreate,
    ArticleListResponse,
    ArticleResponse,
    ArticleUpdate,
)
from app.services.article_cache import (
    delete_cached_article,
    get_cached_article,
    get_list_version,
    increment_list_version,
    set_cached_article,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/articles", tags=["articles"])


def _can_manage_article(current_user: User, author_id: int) -> bool:
    return current_user.id == author_id or current_user.role == ADMIN_USER_ROLE


@router.get("", response_model=ArticleListResponse)
async def get_articles_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    version = await get_list_version(redis)
    cache_key = f"articles_list:{version}:{skip}:{limit}"

    try:
        cached_articles = await redis.get(cache_key)
        if cached_articles:
            logger.debug("Cache hit | key=%s", cache_key)
            return json.loads(cached_articles)
    except Exception as exc:
        logger.warning("Redis read failed, fallback to DB | key=%s | error=%s", cache_key, str(exc))

    total, articles = get_articles(db=db, skip=skip, limit=limit)
    result = {"items": articles, "total": total, "skip": skip, "limit": limit}

    try:
        await redis.setex(cache_key, 60, json.dumps(result, default=str))
    except Exception as exc:
        logger.warning("Redis write failed | key=%s | error=%s", cache_key, str(exc))
    return result


@router.post("", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_new_article(
    article: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
):
    try:
        db_article = create_article(
            db=db,
            article=article,
            author_id=current_user.id,
            actor_is_admin=current_user.role == ADMIN_USER_ROLE,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    await increment_list_version(redis)
    return db_article


@router.get("/{article_id}", response_model=ArticleResponse)
async def read_article(
    article_id: int,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    cached_article = await get_cached_article(redis, article_id=article_id)
    if cached_article:
        return cached_article

    db_article = get_article_by_id(db, article_id=article_id)
    if not db_article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    article_response = ArticleResponse.model_validate(db_article)
    await set_cached_article(redis, article=article_response)
    return db_article


@router.put("/{article_id}", response_model=ArticleResponse)
async def update_existing_article(
    article_id: int,
    article: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
):
    db_article = get_article_by_id(db, article_id=article_id)
    if not db_article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    if not _can_manage_article(current_user, db_article.author_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission to modify this article")

    try:
        db_article = update_article(
            db,
            article_id=article_id,
            article=article,
            actor_is_admin=current_user.role == ADMIN_USER_ROLE,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    await delete_cached_article(redis, article_id)
    await increment_list_version(redis)
    return db_article


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
):
    db_article = get_article_by_id(db, article_id=article_id)
    if not db_article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    if not _can_manage_article(current_user, db_article.author_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission to delete this article")

    delete_article(db, article_id=article_id)
    await delete_cached_article(redis, article_id)
    await increment_list_version(redis)
    return None
