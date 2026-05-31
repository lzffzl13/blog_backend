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
from app.models.user import User
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


@router.get(
    "",
    response_model=ArticleListResponse,
    summary="获取文章列表",
    description="分页获取文章列表，支持 skip 和 limit 参数。结果会缓存到 Redis 中以提高性能。",
)
async def get_articles_list(
    skip: int = Query(0, ge=0, description="跳过条数"),
    limit: int = Query(10, ge=1, le=100, description="返回条数"),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """获取文章列表"""
    # 获取当前文章列表版本号
    version = await get_list_version(redis)
    cache_key = f"articles_list:{version}:{skip}:{limit}"

    # 从缓存中读取
    try:
        cached_articles = await redis.get(cache_key)
        if cached_articles:
            logger.debug("Cache hit | key=%s", cache_key)
            return json.loads(cached_articles)
    except Exception as e:
        logger.warning("Redis read failed, fallback to DB | key=%s | error=%s", cache_key, str(e))
    logger.debug("Cache miss | key=%s", cache_key)
    total, articles = get_articles(db=db, skip=skip, limit=limit)
    result = {"items": articles, "total": total, "skip": skip, "limit": limit}

    # 写入redis。TTL60秒
    try:
        await redis.setex(cache_key, 60, json.dumps(result, default=str))
        logger.debug("Cache set | key=%s| ttl = 60", cache_key)
    except Exception as e:
        logger.warning("Redis write failed | key=%s | error=%s", cache_key, str(e))
    return result


@router.post(
    "",
    response_model=ArticleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建文章",
    description="创建一篇新文章。需要提供标题、内容，可选提供分类和标签。需要登录认证。",
)
async def create_new_article(
    article: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
):
    """创建新文章"""
    db_article = create_article(db=db, article=article, author_id=current_user.id)
    logger.info(
        "Article API: created | id=%d | title='%s' | author_id=%d",
        db_article.id,
        db_article.title,
        current_user.id,
    )
    await increment_list_version(redis)
    return db_article


@router.get(
    "/{article_id}",
    response_model=ArticleResponse,
    summary="获取文章详情",
    description="根据文章 ID 获取文章详细信息。优先从 Redis 缓存读取，未命中则从数据库读取并写入缓存。",
)
async def read_article(
    article_id: int, db: Session = Depends(get_db), redis: Redis = Depends(get_redis)
):
    """获取文章详情,从缓存中读取,未命中则从DB中读取"""
    # 查缓存
    cached_article = await get_cached_article(redis, article_id=article_id)
    if cached_article:
        return cached_article

    # 未命中
    db_article = get_article_by_id(db, article_id=article_id)
    if not db_article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")

    # 写入缓存
    article_response = ArticleResponse.model_validate(db_article)
    await set_cached_article(redis, article=article_response)
    return db_article


@router.put(
    "/{article_id}",
    response_model=ArticleResponse,
    summary="更新文章",
    description="更新指定文章的内容。只能更新自己创建的文章，非作者尝试更新会返回 403 错误。",
)
async def update_existing_article(
    article_id: int,
    article: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
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

    # 更新缓存
    await delete_cached_article(redis, article_id)
    await increment_list_version(redis)
    return db_article


@router.delete(
    "/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除文章",
    description="删除指定文章。只能删除自己创建的文章，非作者尝试删除会返回 403 错误。",
)
async def delete_existing_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
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

    # 删除缓存
    await delete_cached_article(redis, article_id)
    await increment_list_version(redis)
    logger.info("Article API: deleted | id=%d", article_id)
    return None
