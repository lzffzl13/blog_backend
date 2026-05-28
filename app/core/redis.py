from collections.abc import AsyncGenerator

import redis.asyncio as aioredis

from app.core.config import settings

# 模块级全局客户端实例，启动时创建一次
redis_client = aioredis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    max_connections=20,  # 连接池最大连接数
)


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    """依赖注入函数，提供 Redis 客户端实例"""
    yield redis_client
