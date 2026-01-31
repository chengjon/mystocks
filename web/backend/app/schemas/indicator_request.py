"""
Pydantic Request Schemas for Indicator API
定义指标计算API的请求数据模型
"""

import re
from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class IndicatorSpec(BaseModel):
    """
    单个指标规格

    Example:
        {"abbreviation": "SMA", "parameters": {"timeperiod": 20}}
    """

    abbreviation: str = Field(..., description="指标缩写 (如 SMA, RSI, MACD)", min_length=2, max_length=20)
    parameters: Dict[str, Any] = Field(default_factory=dict, description="指标参数字典")

    @validator("abbreviation")
    def abbreviation_must_be_uppercase(cls, v):
        """指标缩写必须为大写"""
        if not v.isupper():
            raise ValueError(f"指标缩写必须为大写: {v}")
        return v

    @validator("parameters")
    def parameters_must_be_valid(cls, v):
        """参数值必须为有效类型"""
        for key, value in v.items():
            if not isinstance(value, (int, float, str, bool)):
                raise ValueError(f"参数 {key} 的值类型无效: {type(value).__name__}. " "只支持 int, float, str, bool")
        return v


class IndicatorCalculateRequest(BaseModel):
    """
    指标计算请求

    Example:
        {
            "symbol": "600519.SH",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "indicators": [
                {"abbreviation": "SMA", "parameters": {"timeperiod": 20}},
                {"abbreviation": "RSI", "parameters": {"timeperiod": 14}}
            ],
            "use_cache": true
        }
    """

    symbol: str = Field(
        ...,
        description="股票代码 (格式: XXXXXX.SH 或 XXXXXX.SZ)",
        min_length=9,
        max_length=9,
    )
    start_date: date = Field(..., description="开始日期 (YYYY-MM-DD)")
    end_date: date = Field(..., description="结束日期 (YYYY-MM-DD)")
    indicators: List[IndicatorSpec] = Field(..., description="指标列表", min_items=1, max_items=10)
    use_cache: bool = Field(default=True, description="是否使用缓存 (默认true)")

    @validator("symbol")
    def symbol_must_be_valid_format(cls, v):
        """验证股票代码格式"""
        pattern = r"^\d{6}\.(SH|SZ)$"
        if not re.match(pattern, v):
            raise ValueError(f"股票代码格式无效: {v}. 正确格式: 6位数字 + .SH 或 .SZ (如 600519.SH)")
        return v

    @validator("end_date")
    def end_date_must_not_be_future(cls, v):
        """结束日期不能晚于今天"""
        today = date.today()
        if v > today:
            raise ValueError(f"结束日期不能晚于今天: {v} > {today}")
        return v

    @validator("end_date")
    def end_date_must_be_after_start_date(cls, v, values):
        """结束日期必须晚于开始日期"""
        if "start_date" in values:
            start_date = values["start_date"]
            if v <= start_date:
                raise ValueError(f"结束日期必须晚于开始日期: {v} <= {start_date}")

            # 检查日期范围不超过5年
            days_diff = (v - start_date).days
            if days_diff > 365 * 5:
                raise ValueError(f"日期范围不能超过5年: {days_diff} 天 > 1825 天")
        return v

    @validator("indicators")
    def indicators_must_not_have_duplicates(cls, v):
        """检查指标列表中是否有完全相同的指标(包括参数)"""
        # 将每个指标转换为可哈希的元组形式 (abbreviation, sorted(parameters.items()))
        indicator_tuples = []
        for ind in v:
            # 将parameters字典转换为排序后的元组,使其可哈希
            params_tuple = tuple(sorted(ind.parameters.items()))
            indicator_tuples.append((ind.abbreviation, params_tuple))

        # 检查是否有完全相同的指标(abbreviation + parameters都相同)
        if len(indicator_tuples) != len(set(indicator_tuples)):
            # 找出重复的项
            seen = set()
            duplicates = []
            for item in indicator_tuples:
                if item in seen:
                    abb, params = item
                    duplicates.append(f"{abb}{dict(params)}")
                seen.add(item)

            raise ValueError(f"指标列表中有完全相同的指标配置: {duplicates}")
        return v


class IndicatorConfigCreateRequest(BaseModel):
    """
    创建指标配置请求

    Example:
        {
            "name": "我的常用配置",
            "indicators": [
                {"abbreviation": "MA", "parameters": {"timeperiod": 20}},
                {"abbreviation": "RSI", "parameters": {"timeperiod": 14}}
            ]
        }
    """

    name: str = Field(..., description="配置名称", min_length=1, max_length=100)
    indicators: List[IndicatorSpec] = Field(..., description="指标列表", min_items=1, max_items=20)

    @validator("name")
    def name_must_not_be_empty(cls, v):
        """配置名称不能为空或只包含空格"""
        if not v.strip():
            raise ValueError("配置名称不能为空")
        return v.strip()


class IndicatorConfigUpdateRequest(BaseModel):
    """
    更新指标配置请求

    Example:
        {
            "name": "我的新配置名称",
            "indicators": [...]
        }
    """

    name: Optional[str] = Field(None, description="配置名称 (可选)", min_length=1, max_length=100)
    indicators: Optional[List[IndicatorSpec]] = Field(None, description="指标列表 (可选)", min_items=1, max_items=20)

    @validator("name")
    def name_must_not_be_empty_if_provided(cls, v):
        """如果提供了配置名称,不能为空或只包含空格"""
        if v is not None and not v.strip():
            raise ValueError("配置名称不能为空")
        return v.strip() if v else v

    class Config:
        # 至少需要提供一个字段
        @staticmethod
        def schema_extra(schema, model):
            schema["minProperties"] = 1
