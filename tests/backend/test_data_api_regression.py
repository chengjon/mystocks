import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import FastAPI
import sys
import os

# Add web/backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../web/backend")))

# Import the router and dependencies
from app.api.data import router
from app.core.security import get_current_user

app = FastAPI()
app.include_router(router)

# Global dependency override for tests
app.dependency_overrides[get_current_user] = lambda: MagicMock()

client = TestClient(app)

@pytest.fixture
def mock_factory():
    with patch("app.services.data_source_factory.get_data_source_factory") as mock:
        factory_instance = AsyncMock()
        mock.return_value = factory_instance
        yield factory_instance

def test_get_stocks_basic(mock_factory):
    mock_factory.get_data.return_value = {
        "status": "success",
        "data": [{"symbol": "000001", "name": "Ping An"}],
        "total": 1
    }
    
    response = client.get("/api/v1/data/stocks/basic")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert len(response.json()["data"]) == 1

def test_get_market_overview(mock_factory):
    mock_factory.get_data.return_value = {
        "status": "success",
        "data": {"index": "sh000001"}
    }
    
    response = client.get("/api/v1/data/markets/overview")
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_get_kline(mock_factory):
    mock_factory.get_data.return_value = {
        "status": "success",
        "data": [{"date": "2025-01-01", "close": 10.0}]
    }
    
    response = client.get("/api/v1/data/stocks/daily?symbol=000001")
    assert response.status_code == 200
    assert response.json()["success"] is True