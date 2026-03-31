import pytest
from fastapi.testclient import TestClient
from main import app
from app.db.session import get_db
from unittest.mock import patch, AsyncMock

client = TestClient(app)

async def override_get_db():
    yield AsyncMock()

app.dependency_overrides[get_db] = override_get_db

@patch("app.api.routes.domains.PipelineService")
def test_get_domain_api(mock_pipeline_cls):
    mock_pipeline = AsyncMock()
    mock_pipeline.get_domain.return_value = {"source": "mock", "domain": "example.com"}
    mock_pipeline_cls.return_value = mock_pipeline
    
    resp = client.get("/api/v1/domains/example.com")
    assert resp.status_code == 200
    assert resp.json() == {"source": "mock", "domain": "example.com"}
    mock_pipeline.get_domain.assert_called_with("example.com", force_refresh=False)
    
    resp = client.get("/api/v1/domains/example.com?refresh=true")
    assert resp.status_code == 200
    mock_pipeline.get_domain.assert_called_with("example.com", force_refresh=True)

@patch("app.api.routes.ip_addresses.PipelineService")
def test_get_ip_api(mock_pipeline_cls):
    mock_pipeline = AsyncMock()
    mock_pipeline.get_ip.return_value = {"error": "not_found", "ip_address": "8.8.8.8"}
    mock_pipeline_cls.return_value = mock_pipeline
    
    resp = client.get("/api/v1/ips/8.8.8.8")
    assert resp.status_code == 200
    assert resp.json() == {"error": "not_found", "ip_address": "8.8.8.8"}

@patch("app.api.routes.file_hashes.PipelineService")
def test_get_file_hash_api(mock_pipeline_cls):
    mock_pipeline = AsyncMock()
    mock_pipeline.get_file_hash.return_value = {"source": "mock"}
    mock_pipeline_cls.return_value = mock_pipeline
    
    resp = client.get("/api/v1/files/abc123hash")
    assert resp.status_code == 200
