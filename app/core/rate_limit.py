import logging

from fastapi import HTTPException, Request, status
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

# Lua 原子脚本：自增key，首次设置过期时间
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


async def check_login_rate_limit(
    redis: Redis, request: Request, max_request: int = 5, window: int = 60
):
    """
    登录接口限流检查
    window: 窗口时间，单位秒
    max_request: 最大请求数量
    """
    # 提取客户端IP
    client_ip = request.client.host if request.client else "unknown"

    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()

    # 生成key
    key = f"login_rate_limit:{client_ip}"
    try:
        # 执行原子脚本
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
                detail=f"请求过于频繁,请{window}秒后再试",
            )

        logger.debug(
            "Rate limit check passed | ip=%s | count=%d | window=%ds",
            client_ip,
            current,
            window,
        )
    except HTTPException:
        raise

    except Exception as e:
        # 如果Redis不可用，直接跳过限流
        logger.warning("Redis unavailable, rate limit bypassed | error=%s", str(e))
