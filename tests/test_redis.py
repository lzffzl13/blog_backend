import pytest


@pytest.mark.asyncio
async def test_redis_set_and_get(redis_client):
    """验证 fakeredis 基本读写"""
    await redis_client.set("test:hello", "world", ex=60)
    result = await redis_client.get("test:hello")
    assert result == "world"

