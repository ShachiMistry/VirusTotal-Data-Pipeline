import pytest
import time
from app.services.cache import _InMemoryCache

@pytest.mark.asyncio
async def test_in_memory_cache():
    cache = _InMemoryCache(ttl=1)
    
    await cache.set("test_key", {"data": "value"})
    val = await cache.get("test_key")
    assert val == {"data": "value"}
    
    await cache.delete("test_key")
    val = await cache.get("test_key")
    assert val is None

    await cache.set("expire_key", {"data": "value"})
    time.sleep(1.1)
    val = await cache.get("expire_key")
    assert val is None
