import json
import time
from datetime import datetime, date
from typing import Optional
import redis.asyncio as redis
from app.core.config import get_settings

class _RedisCache:
    def __init__(self, url: str, ttl: int):
        self.redis = redis.from_url(url, decode_responses=True)
        self.ttl = ttl

    async def get(self, key: str) -> Optional[dict]:
        val = await self.redis.get(key)
        return json.loads(val) if val else None

    async def set(self, key: str, value: dict) -> None:
        def json_serial(obj):
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        await self.redis.set(key, json.dumps(value, default=json_serial), ex=self.ttl)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def close(self):
        await self.redis.aclose()


class _InMemoryCache:
    def __init__(self, ttl: int):
        self.cache = {}
        self.ttl = ttl

    async def get(self, key: str) -> Optional[dict]:
        if key in self.cache:
            value, expires_at = self.cache[key]
            if time.time() < expires_at:
                return value
            else:
                del self.cache[key]
        return None

    async def set(self, key: str, value: dict) -> None:
        self.cache[key] = (value, time.time() + self.ttl)

    async def delete(self, key: str) -> None:
        if key in self.cache:
            del self.cache[key]

    async def close(self):
        pass


class CacheService:
    def __init__(self):
        settings = get_settings()
        if settings.redis_url:
            self._backend = _RedisCache(settings.redis_url, settings.cache_ttl_seconds)
        else:
            self._backend = _InMemoryCache(settings.cache_ttl_seconds)

    def _format_key(self, resource_type: str, identifier: str) -> str:
        return f"vt:{resource_type}:{identifier}"

    async def get_domain(self, domain: str) -> Optional[dict]:
        return await self._backend.get(self._format_key("domain", domain))

    async def set_domain(self, domain: str, data: dict) -> None:
        await self._backend.set(self._format_key("domain", domain), data)

    async def invalidate_domain(self, domain: str) -> None:
        await self._backend.delete(self._format_key("domain", domain))

    async def get_ip(self, ip: str) -> Optional[dict]:
        return await self._backend.get(self._format_key("ip", ip))

    async def set_ip(self, ip: str, data: dict) -> None:
        await self._backend.set(self._format_key("ip", ip), data)

    async def invalidate_ip(self, ip: str) -> None:
        await self._backend.delete(self._format_key("ip", ip))

    async def get_hash(self, file_hash: str) -> Optional[dict]:
        return await self._backend.get(self._format_key("hash", file_hash))

    async def set_hash(self, file_hash: str, data: dict) -> None:
        await self._backend.set(self._format_key("hash", file_hash), data)

    async def invalidate_hash(self, file_hash: str) -> None:
        await self._backend.delete(self._format_key("hash", file_hash))

    async def close(self):
        await self._backend.close()

cache_service = CacheService()
