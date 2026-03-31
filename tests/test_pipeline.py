import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.pipeline import PipelineService

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.mark.asyncio
@patch("app.services.pipeline.cache_service")
@patch("app.services.pipeline.VirusTotalClient")
async def test_pipeline_get_domain(mock_vt_client_class, mock_cache, mock_db_session):
    vt_instance = AsyncMock()
    vt_instance.__aenter__.return_value = vt_instance
    vt_instance.get_domain_report.return_value = {
        "data": {"attributes": {"last_analysis_stats": {"harmless": 1}}}
    }
    mock_vt_client_class.return_value = vt_instance

    pipeline = PipelineService(mock_db_session)
    
    # Test cache hit
    mock_cache.get_domain = AsyncMock(return_value={"cached": True})
    res = await pipeline.get_domain("example.com")
    assert res["source"] == "cache"
    
    # Test DB hit
    mock_cache.get_domain.return_value = None
    mock_record = MagicMock()
    mock_record.to_dict.return_value = {"db_hit": True}
    
    mock_result_db = MagicMock()
    mock_result_db.scalars.return_value.first.return_value = mock_record
    mock_db_session.execute.return_value = mock_result_db
    mock_cache.set_domain = AsyncMock()
    
    res = await pipeline.get_domain("example.com")
    assert res["source"] == "database"
    
    # Test VT hit
    mock_result_db.scalars.return_value.first.return_value = None
    res = await pipeline.get_domain("example.com")
    assert res["source"] == "virustotal"

    # Test force_refresh
    mock_cache.get_domain.return_value = {"cached": True}
    res = await pipeline.get_domain("example.com", force_refresh=True)
    assert res["source"] == "virustotal"
