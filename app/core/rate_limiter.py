import asyncio
import time

class RateLimiter:
    def __init__(self, max_calls: int = 4, period: float = 60.0):
        self.max_calls = max_calls
        self.period = period
        self.timestamps = []
        self._lock = asyncio.Lock()

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def acquire(self):
        async with self._lock:
            while True:
                now = time.monotonic()
                self.timestamps = [t for t in self.timestamps if now - t <= self.period]
                
                if len(self.timestamps) < self.max_calls:
                    self.timestamps.append(now)
                    break
                
                sleep_time = self.period - (now - self.timestamps[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
