"""股票搜索 API 请求/响应模型定义。"""

import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class StockSearchResult(BaseModel):
    """股票搜索结果"""

    symbol: str = Field(..., description="股票代码")
    description: str = Field(..., description="股票名称")
    displaySymbol: str = Field(..., description="显示代码")
    type: str = Field(..., description="类型")
    exchange: str = Field(..., description="交易所")
    market: Optional[str] = Field(None, description="市场")


class StockQuote(BaseModel):
    """股票报价"""

    symbol: Optional[str] = None
    name: Optional[str] = None
    current: float = Field(..., description="当前价格")
    change: float = Field(..., description="涨跌额")
    percent_change: float = Field(..., description="涨跌幅")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    open: float = Field(..., description="开盘价")
    previous_close: float = Field(..., description="昨收")
    volume: Optional[float] = Field(None, description="成交量")
    amount: Optional[float] = Field(None, description="成交额")
    timestamp: float = Field(..., description="时间戳")


class NewsItem(BaseModel):
    """新闻条目"""

    headline: str = Field(..., description="标题", max_length=200)
    summary: str = Field(..., description="摘要", max_length=1000)
    source: str = Field(..., description="来源", max_length=100)
    datetime: float = Field(..., description="时间戳")
    url: str = Field(..., description="链接", max_length=500)
    image: Optional[str] = Field(None, description="图片", max_length=500)
    category: Optional[str] = Field(None, description="分类", max_length=50)

    @field_validator("headline")
    @classmethod
    def validate_headline(cls, value: str) -> str:
        """验证新闻标题"""
        if not value.strip():
            raise ValueError("新闻标题不能为空")
        if re.search(r"<script|javascript:|onload=|onerror=", value, re.IGNORECASE):
            raise ValueError("新闻标题包含不安全的脚本或标签")
        return value.strip()

    @field_validator("summary")
    @classmethod
    def validate_summary(cls, value: str) -> str:
        """验证新闻摘要"""
        if not value.strip():
            raise ValueError("新闻摘要不能为空")
        if re.search(r"<script|javascript:|onload=|onerror=", value, re.IGNORECASE):
            raise ValueError("新闻摘要包含不安全的脚本或标签")
        return value.strip()


class SearchRequest(BaseModel):
    """搜索请求模型"""

    query: str = Field(..., description="搜索关键词", min_length=1, max_length=100)
    market: str = Field("auto", description="市场类型", pattern=r"^(auto|cn|hk)$")
    limit: int = Field(20, description="返回结果数量", ge=1, le=100)

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        """验证搜索关键词"""
        if not value.strip():
            raise ValueError("搜索关键词不能为空")
        value = re.sub(r'[<>"\'/\\]', "", value)
        if len(value.strip()) > 100:
            raise ValueError("搜索关键词过长，最多100个字符")
        return value.strip()
