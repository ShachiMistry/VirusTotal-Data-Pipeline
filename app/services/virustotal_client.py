import httpx
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from app.core.config import get_settings
from app.core.rate_limiter import RateLimiter

settings = get_settings()
rate_limiter = RateLimiter(max_calls=settings.vt_rate_limit_rpm, period=60.0)

class VirusTotalClient:
    def __init__(self):
        self.settings = get_settings()
        self.client = httpx.AsyncClient(
            base_url=self.settings.vt_base_url,
            headers={"x-apikey": self.settings.virustotal_api_key}
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    @retry(
        retry=retry_if_exception_type((httpx.TransportError, httpx.TimeoutException)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _get(self, endpoint: str) -> dict:
        async with rate_limiter:
            response = await self.client.get(endpoint)
            if response.status_code == 404:
                return {}
            if response.status_code == 429:
                raise httpx.TransportError("Rate limit exceeded")
            response.raise_for_status()
            return response.json()

    async def get_domain_report(self, domain: str) -> dict:
        return await self._get(f"/domains/{domain}")

    async def get_ip_report(self, ip: str) -> dict:
        return await self._get(f"/ip_addresses/{ip}")

    async def get_file_report(self, file_hash: str) -> dict:
        return await self._get(f"/files/{file_hash}")
