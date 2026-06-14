import logging

from fastapi import HTTPException, Request, status
from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)

LUA_SCRIPT = """
local key = KEYS[1]
local window = tonumber(ARGV[1])
local max_requests = tonumber(ARGV[2])

local current = redis.call('INCR', key)
if current == 1 then
    redis.call('expire', key, window)
end

return current
"""


def get_client_ip(request: Request) -> str:
    client_ip = request.client.host if request.client else "unknown"

    if settings.TRUST_PROXY_HEADERS:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()

    return client_ip


async def check_login_rate_limit(
    redis: Redis, request: Request, max_request: int = 5, window: int = 60
):
    client_ip = get_client_ip(request)
    key = f"login_rate_limit:{client_ip}"
    try:
        current = await redis.eval(LUA_SCRIPT, 1, key, window, max_request)

        if current > max_request:
            logging.warning(
                "Rate limit exceeded | ip=%s | count=%d | window=%ds",
                client_ip,
                current,
                window,
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"请求过于频繁，请在 {window} 秒后重试",
            )

        logger.debug(
            "Rate limit check passed | ip=%s | count=%d | window=%ds",
            client_ip,
            current,
            window,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("Redis unavailable, rate limit bypassed | error=%s", str(exc))
