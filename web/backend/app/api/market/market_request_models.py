"""市场数据 API 请求模型。
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class MarketDataRequest(BaseModel):
    """市场数据请求基类"""

    symbol: str = Field(..., description="股票代码", min_length=1, max_length=20, pattern=r"^[A-Z0-9.]+$")

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, value: str) -> str:
        if value.startswith("."):
            raise ValueError("股票代码不能以点开头")
        if ".." in value:
            raise ValueError("股票代码不能包含连续的点")
        return value.upper()


class FundFlowRequest(BaseModel):
    """资金流向请求参数"""

    symbol: str = Field(..., description="股票代码", min_length=1, max_length=20, pattern=r"^[A-Z0-9.]+$")
    timeframe: str = Field("1", description="时间维度: 1/3/5/10天", pattern=r"^[13510]$")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, value: str) -> str:
        if value.startswith("."):
            raise ValueError("股票代码不能以点开头")
        if ".." in value:
            raise ValueError("股票代码不能包含连续的点")
        return value.upper()

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, value: Optional[date], values) -> Optional[date]:
        if value is None or "start_date" not in values or values["start_date"] is None:
            return value

        if value <= values["start_date"]:
            raise ValueError("结束日期必须大于开始日期")

        if (value - values["start_date"]).days > 365:
            raise ValueError("查询时间范围不能超过365天")

        return value


class ETFQueryParams(BaseModel):
    """ETF查询参数"""

    symbol: Optional[str] = Field(None, description="ETF代码", min_length=1, max_length=10, pattern=r"^[A-Z0-9]+$")
    keyword: Optional[str] = Field(None, description="关键词搜索", min_length=1, max_length=50)
    market: Optional[str] = Field(None, description="市场类型", pattern=r"^(SH|SZ)$")
    category: Optional[str] = Field(None, description="ETF类型", pattern=r"^(股票|债券|商品|货币|QDII)$")
    limit: int = Field(100, description="返回数量", ge=1, le=500)
    offset: int = Field(0, description="偏移量", ge=0, le=10000)

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return value.upper()

    @field_validator("keyword")
    @classmethod
    def validate_keyword(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        for pattern in ["union", "select", "insert", "update", "delete", "drop", "exec"]:
            if pattern in value.lower():
                raise ValueError("搜索关键词包含不安全内容")

        return value.strip()


class RefreshRequest(BaseModel):
    """数据刷新请求"""

    symbol: str = Field(..., description="股票代码", min_length=1, max_length=20, pattern=r"^[A-Z0-9.]+$")
    timeframe: Optional[str] = Field(None, description="时间维度", pattern=r"^[13510]$")

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, value: str) -> str:
        if value.startswith("."):
            raise ValueError("股票代码不能以点开头")
        if ".." in value:
            raise ValueError("股票代码不能包含连续的点")
        return value.upper()
