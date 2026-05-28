import json
import logging

from redis.asyncio import Redis

from app.schemas.article import ArticleResponse

logger = logging.getLogger(__name__)

# 单篇文章缓存TTL ：300s
ARTICLE_CACHE_TTL = 300

# 文章列表版本号key
ARTICLE_LIST_VERSION_KEY = "article_list_version"


async def get_cached_article(redis: Redis, article_id: int) -> ArticleResponse | None:
    """从缓存中获取文章命中返回ArticleResponse,未命中返回None"""
    key = f"article:{article_id}"
    try:
        data = await redis.get(key)
        if data:
            logger.debug("Cache hit | key=%s", key)
            return ArticleResponse(**json.loads(data))
        logger.debug("Cache miss | key=%s", key)
        return None
    except Exception as e:
        logger.warning("Redis read failed, fallback to DB | key=%s | error=%s", key, str(e))
        return None


async def set_cached_article(redis: Redis, article: ArticleResponse) -> None:
    """将文章写入缓存"""
    key = f"article:{article.id}"
    try:
        data = article.model_dump_json()
        await redis.setex(key, ARTICLE_CACHE_TTL, data)
        logger.debug("Cache set | key=%s", key)
    except Exception as e:
        logger.warning("Redis write failed | key=%s | error=%s", key, str(e))


async def delete_cached_article(redis: Redis, article_id: int) -> None:
    """删除单篇文章缓存"""
    key = f"article:{article_id}"
    try:
        await redis.delete(key)
        logger.debug("Cache deleted | key=%s", key)
    except Exception as e:
        logger.warning("Redis delete failed | key=%s | error=%s", key, str(e))


async def get_list_version(redis: Redis) -> int:
    """获取当前文章列表版本号"""
    try:
        version = await redis.get(ARTICLE_LIST_VERSION_KEY)
        return int(version) if version else 0
    except Exception as e:
        logger.warning(
            "Redis read failed, fallback to DB | key=%s | error=%s",
            ARTICLE_LIST_VERSION_KEY,
            str(e),
        )
        return 0


async def increment_list_version(redis: Redis) -> None:
    """自增文章列表版本号"""
    try:
        await redis.incr(ARTICLE_LIST_VERSION_KEY)
        logger.debug("List version incremented | key=%s", ARTICLE_LIST_VERSION_KEY)
    except Exception as e:
        logger.warning("Redis increment list version failed | error=%s", str(e))
