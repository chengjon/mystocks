"""
Pydantic Response Schemas for Indicator API
定义指标计算API的响应数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class IndicatorValueOutput(BaseModel):
    """
    单个指标的输出值

    Example:
        {
            "output_name": "sma",
            "values": [10.5, 11.2, 10.8, ...],
            "display_name": "SMA(20)"
        }
    """
    output_name: str = Field(
        ...,
        description="输出字段名称 (如 sma, macd, rsi)"
    )
    values: List[Optional[float]] = Field(
        ...,
        description="指标值数组 (与日期一一对应, None表示数据不足)"
    )
    display_name: str = Field(
        ...,
        description="显示名称 (如 SMA(20), RSI(14))"
    )


class IndicatorResult(BaseModel):
    """
    单个指标的计算结果

    Example:
        {
            "abbreviation": "SMA",
            "parameters": {"timeperiod": 20},
            "outputs": [
                {
                    "output_name": "sma",
                    "values": [10.5, 11.2, ...],
                    "display_name": "SMA(20)"
                }
            ],
            "panel_type": "overlay",
            "reference_lines": null,
            "error": null
        }
    """
    abbreviation: str = Field(
        ...,
        description="指标缩写"
    )
    parameters: Dict[str, Any] = Field(
        ...,
        description="使用的参数"
    )
    outputs: List[IndicatorValueOutput] = Field(
        default_factory=list,
        description="指标输出列表"
    )
    panel_type: str = Field(
        ...,
        description="面板类型: overlay (叠加主图) 或 oscillator (独立面板)"
    )
    reference_lines: Optional[List[float]] = Field(
        None,
        description="参考线数值 (如 RSI 的 30, 70)"
    )
    error: Optional[str] = Field(
        None,
        description="错误信息 (如果计算失败)"
    )


class OHLCVData(BaseModel):
    """
    OHLCV K线数据

    Example:
        {
            "dates": ["2024-01-01", "2024-01-02", ...],
            "open": [10.5, 10.8, ...],
            "high": [11.0, 11.5, ...],
            "low": [10.2, 10.5, ...],
            "close": [10.8, 11.2, ...],
            "volume": [1000000, 1200000, ...],
            "turnover": [10800000, 12544000, ...]
        }
    """
    dates: List[str] = Field(
        ...,
        description="日期列表 (YYYY-MM-DD 格式)"
    )
    open: List[float] = Field(
        ...,
        description="开盘价列表"
    )
    high: List[float] = Field(
        ...,
        description="最高价列表"
    )
    low: List[float] = Field(
        ...,
        description="最低价列表"
    )
    close: List[float] = Field(
        ...,
        description="收盘价列表"
    )
    volume: List[float] = Field(
        ...,
        description="成交量列表"
    )
    turnover: List[float] = Field(
        default_factory=list,
        description="成交额列表 (可选, 用于EMV和AVP指标)"
    )


class IndicatorCalculateResponse(BaseModel):
    """
    指标计算响应

    Example:
        {
            "symbol": "600519.SH",
            "symbol_name": "贵州茅台",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "ohlcv": {
                "dates": [...],
                "open": [...],
                ...
            },
            "indicators": [
                {
                    "abbreviation": "SMA",
                    "parameters": {"timeperiod": 20},
                    "outputs": [...],
                    "panel_type": "overlay",
                    "reference_lines": null,
                    "error": null
                }
            ],
            "calculation_time_ms": 15.5,
            "cached": false
        }
    """
    symbol: str = Field(
        ...,
        description="股票代码"
    )
    symbol_name: str = Field(
        ...,
        description="股票名称"
    )
    start_date: str = Field(
        ...,
        description="开始日期 (YYYY-MM-DD)"
    )
    end_date: str = Field(
        ...,
        description="结束日期 (YYYY-MM-DD)"
    )
    ohlcv: OHLCVData = Field(
        ...,
        description="K线OHLCV数据"
    )
    indicators: List[IndicatorResult] = Field(
        ...,
        description="指标计算结果列表"
    )
    calculation_time_ms: float = Field(
        ...,
        description="计算耗时 (毫秒)",
        ge=0
    )
    cached: bool = Field(
        default=False,
        description="是否来自缓存"
    )


class IndicatorMetadata(BaseModel):
    """
    指标元数据

    Example:
        {
            "abbreviation": "SMA",
            "full_name": "Simple Moving Average",
            "chinese_name": "简单移动平均线",
            "category": "trend",
            "description": "计算收盘价的算术平均值",
            "panel_type": "overlay",
            "parameters": [
                {
                    "name": "timeperiod",
                    "type": "int",
                    "default": 20,
                    "min": 2,
                    "max": 200,
                    "description": "周期"
                }
            ],
            "outputs": [
                {
                    "name": "sma",
                    "description": "SMA值"
                }
            ],
            "reference_lines": null,
            "min_data_points_formula": "timeperiod"
        }
    """
    abbreviation: str = Field(
        ...,
        description="指标缩写"
    )
    full_name: str = Field(
        ...,
        description="完整英文名称"
    )
    chinese_name: str = Field(
        ...,
        description="中文名称"
    )
    category: str = Field(
        ...,
        description="指标分类: trend, momentum, volatility, volume, candlestick"
    )
    description: str = Field(
        ...,
        description="指标描述"
    )
    panel_type: str = Field(
        ...,
        description="面板类型: overlay 或 oscillator"
    )
    parameters: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="参数定义列表"
    )
    outputs: List[Dict[str, str]] = Field(
        ...,
        description="输出定义列表"
    )
    reference_lines: Optional[List[float]] = Field(
        None,
        description="参考线数值"
    )
    min_data_points_formula: str = Field(
        ...,
        description="最小数据点计算公式"
    )


class IndicatorRegistryResponse(BaseModel):
    """
    指标注册表响应

    Example:
        {
            "total_count": 161,
            "categories": {
                "trend": 15,
                "momentum": 20,
                "volatility": 10,
                "volume": 8,
                "candlestick": 61
            },
            "indicators": [
                {...},
                {...}
            ]
        }
    """
    total_count: int = Field(
        ...,
        description="指标总数",
        ge=0
    )
    categories: Dict[str, int] = Field(
        ...,
        description="各分类指标数量"
    )
    indicators: List[IndicatorMetadata] = Field(
        ...,
        description="指标元数据列表"
    )


class IndicatorConfigResponse(BaseModel):
    """
    指标配置响应

    Example:
        {
            "id": 1,
            "user_id": 123,
            "name": "我的常用配置",
            "indicators": [
                {"abbreviation": "MA", "parameters": {"timeperiod": 20}},
                {"abbreviation": "RSI", "parameters": {"timeperiod": 14}}
            ],
            "created_at": "2024-01-01T10:00:00",
            "updated_at": "2024-01-02T15:30:00",
            "last_used_at": "2024-01-03T09:00:00"
        }
    """
    id: int = Field(
        ...,
        description="配置ID"
    )
    user_id: int = Field(
        ...,
        description="用户ID"
    )
    name: str = Field(
        ...,
        description="配置名称"
    )
    indicators: List[Dict[str, Any]] = Field(
        ...,
        description="指标列表 (JSON格式)"
    )
    created_at: datetime = Field(
        ...,
        description="创建时间"
    )
    updated_at: datetime = Field(
        ...,
        description="更新时间"
    )
    last_used_at: Optional[datetime] = Field(
        None,
        description="最后使用时间"
    )


class IndicatorConfigListResponse(BaseModel):
    """
    指标配置列表响应

    Example:
        {
            "total_count": 5,
            "configs": [
                {...},
                {...}
            ]
        }
    """
    total_count: int = Field(
        ...,
        description="配置总数",
        ge=0
    )
    configs: List[IndicatorConfigResponse] = Field(
        ...,
        description="配置列表"
    )


class ErrorDetail(BaseModel):
    """
    错误详情

    Example:
        {
            "error_code": "INSUFFICIENT_DATA",
            "error_message": "指标 SMA(200) 需要至少 200 个数据点",
            "details": {
                "indicator": "SMA",
                "required_points": 200,
                "actual_points": 150
            }
        }
    """
    error_code: str = Field(
        ...,
        description="错误代码"
    )
    error_message: str = Field(
        ...,
        description="错误消息"
    )
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="错误详细信息"
    )


class APIResponse(BaseModel):
    """
    通用API响应包装器

    Example:
        {
            "success": true,
            "data": {...},
            "error": null,
            "timestamp": "2024-01-01T10:00:00"
        }
    """
    success: bool = Field(
        ...,
        description="请求是否成功"
    )
    data: Optional[Any] = Field(
        None,
        description="响应数据"
    )
    error: Optional[ErrorDetail] = Field(
        None,
        description="错误详情 (如果失败)"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="响应时间戳"
    )
