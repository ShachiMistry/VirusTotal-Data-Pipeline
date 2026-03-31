from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.logging import setup_logging
from app.db.session import init_db
from app.services.cache import cache_service
from app.api.routes import domains, ip_addresses, file_hashes

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await init_db()
    yield
    await cache_service.close()

app = FastAPI(title="VirusTotal Data Pipeline", version="1.0.0", lifespan=lifespan)

app.include_router(domains.router, prefix="/api/v1/domains", tags=["domains"])
app.include_router(ip_addresses.router, prefix="/api/v1/ips", tags=["ips"])
app.include_router(file_hashes.router, prefix="/api/v1/files", tags=["files"])

@app.get("/health")
async def health():
    return {"status": "ok"}
