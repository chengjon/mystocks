"""
股票评级数据API Schema
Sina Finance Stock Ratings API Schemas

定义股票评级相关的请求和响应数据模型。
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class StockRatingItem(BaseModel):
    """单条股票评级数据"""

    股票代码: str = Field(..., description="股票代码", example="000001")
    股票名称: str = Field(..., description="股票名称", example="平安银行")
    目标价: str = Field(..., description="目标价", example="15.50")
    最新评级: str = Field(..., description="最新评级", example="买入")
    评级机构: str = Field(..., description="评级机构", example="中信证券")
    分析师: str = Field(..., description="分析师姓名", example="张三")
    行业: str = Field(..., description="行业分类", example="银行")
    评级日期: str = Field(..., description="评级日期", example="2024-01-15")
    摘要: str = Field(..., description="评级摘要", example="看好未来发展前景")


class StockRatingsRequest(BaseModel):
    """股票评级数据请求"""

    max_pages: Optional[int] = Field(5, description="最大爬取页数", ge=1, le=10, example=5)


class StockRatingsResponse(BaseModel):
    """股票评级数据响应"""

    data: List[StockRatingItem] = Field(..., description="股票评级数据列表")
    total_count: int = Field(..., description="总记录数", example=250)
    pages_scraped: int = Field(..., description="实际爬取的页数", example=5)
    max_pages: int = Field(..., description="请求的最大页数", example=5)
    timestamp: str = Field(..., description="数据获取时间戳", example="2024-01-15T10:30:00Z")
    source: str = Field("sina_finance", description="数据来源", example="sina_finance")


class StockRatingsSummary(BaseModel):
    """股票评级数据汇总统计"""

    total_ratings: int = Field(..., description="总评级数量")
    unique_stocks: int = Field(..., description="唯一股票数量")
    rating_agencies: int = Field(..., description="评级机构数量")
    industries: int = Field(..., description="行业数量")
    latest_update: str = Field(..., description="最新更新时间")
    rating_distribution: dict = Field(..., description="评级分布", example={"买入": 120, "增持": 80, "中性": 30})


class StockRatingsHealthResponse(BaseModel):
    """股票评级API健康检查响应"""

    status: str = Field(..., description="服务状态", example="healthy")
    last_successful_scrape: Optional[str] = Field(None, description="最后成功爬取时间")
    average_response_time: float = Field(..., description="平均响应时间(秒)", example=15.5)
    success_rate: float = Field(..., description="成功率", example=0.95)
    total_scrapes: int = Field(..., description="总爬取次数", example=100)
    recent_errors: List[str] = Field(default_factory=list, description="最近错误列表")
