"""
AkShare Market API Base

Common instances and models.
"""
from src.adapters.akshare.market_adapter import AkshareMarketDataAdapter
from pydantic import BaseModel, Field

# Shared adapter instance
akshare_market_adapter = AkshareMarketDataAdapter()

class MarketOverviewSSERequest(BaseModel):
    pass

class MarketOverviewSZSERequest(BaseModel):
    date: str = Field(..., description="查询日期", example="2024-01-15")

class AreaTradingRequest(BaseModel):
    date: str = Field(..., description="查询日期", example="2024-01-15")

class SectorTradingRequest(BaseModel):
    symbol: str = Field(..., description="行业代码", example="BK0477")
    date: str = Field(..., description="查询日期", example="2024-01-15")

class SSEDailyDealRequest(BaseModel):
    date: str = Field(..., description="查询日期", example="2024-01-15")
