import logging
from datetime import UTC, datetime

from fastapi import HTTPException, status
from redis.asyncio import Redis

BLACKLIST_PREFIX = "token_blacklist"
logger = logging.getLogger(__name__)


def _get_token_jti(payload: dict) -> str:
    jti = payload.get("jti")
    if not jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 缺少唯一标识",
        )
    return jti


def _get_token_ttl_seconds(payload: dict) -> int:
    exp = payload.get("exp")
    if exp is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 缺少过期时间",
        )

    expires_at = datetime.fromtimestamp(exp, tz=UTC)
    ttl = int((expires_at - datetime.now(UTC)).total_seconds())
    return max(ttl, 0)


def get_blacklist_key(payload: dict) -> str:
    return f"{BLACKLIST_PREFIX}:{_get_token_jti(payload)}"


async def is_token_blacklisted(redis: Redis, payload: dict) -> bool:
    try:
        return bool(await redis.get(get_blacklist_key(payload)))
    except Exception as exc:
        logger.warning("Redis unavailable, blacklist check bypassed | error=%s", str(exc))
        return False


async def blacklist_token(redis: Redis, payload: dict) -> None:
    ttl = _get_token_ttl_seconds(payload)
    if ttl <= 0:
        return

    await redis.setex(get_blacklist_key(payload), ttl, "1")
