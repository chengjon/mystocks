"""
Indicator Metadata System
=========================

标准化指标元数据定义，包含：
- IndicatorCategory: 指标分类枚举
- PanelType: 显示面板类型
- ComplexityLevel: 计算复杂度等级
- ParameterType: 参数类型
- IndicatorParameter: 指标参数定义
- IndicatorOutput: 指标输出定义
- IndicatorMetadata: 指标完整元数据

Version: 1.0.0
Author: MyStocks Project
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class IndicatorCategory(str, Enum):
    """指标分类"""

    TREND = "trend"
    MOMENTUM = "momentum"
    VOLATILITY = "volatility"
    VOLUME = "volume"
    CANDLESTICK = "candlestick"
    CUSTOM = "custom"


class PanelType(str, Enum):
    """显示面板类型"""

    OVERLAY = "overlay"
    OSCILLATOR = "oscillator"


class ComplexityLevel(str, Enum):
    """计算复杂度等级"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ParameterType(str, Enum):
    """参数类型"""

    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    STRING = "string"


class DataField(str, Enum):
    """需要的基础数据字段"""

    OPEN = "open"
    HIGH = "high"
    LOW = "low"
    CLOSE = "close"
    VOLUME = "volume"
    AMOUNT = "amount"


@dataclass
class ParameterConstraint:
    """参数约束定义"""

    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[List[Any]] = None
    step: Optional[float] = None
    depends_on: Optional[str] = None
    valid_if: Optional[str] = None

    def validate(self, value: Any) -> tuple[bool, str]:
        """验证参数值是否满足约束"""
        if self.min_value is not None and value < self.min_value:
            return False, f"值 {value} 小于最小值 {self.min_value}"
        if self.max_value is not None and value > self.max_value:
            return False, f"值 {value} 大于最大值 {self.max_value}"
        if self.allowed_values is not None and value not in self.allowed_values:
            return False, f"值 {value} 不在允许的值列表中"
        return True, ""


class IndicatorParameter(BaseModel):
    """指标参数定义"""

    name: str = Field(..., description="参数名称（英文标识符）")
    type: ParameterType = Field(..., description="参数类型")
    default: Any = Field(..., description="默认值")
    description: str = Field("", description="参数描述")
    display_name: str = Field("", description="中文显示名称")
    unit: Optional[str] = Field(None, description="参数单位")
    constraints: ParameterConstraint = Field(default_factory=ParameterConstraint, description="参数约束")
    advanced: bool = Field(False, description="是否高级参数")
    hidden: bool = Field(False, description="是否隐藏（不显示在UI）")

    class Config:
        json_encoders = {
            ParameterConstraint: lambda v: {
                "min_value": v.min_value,
                "max_value": v.max_value,
                "allowed_values": v.allowed_values,
                "step": v.step,
            }
        }


class IndicatorOutput(BaseModel):
    """指标输出定义"""

    name: str = Field(..., description="输出标识符")
    display_name: str = Field(..., description="显示名称")
    description: str = Field("", description="输出描述")
    reference_lines: Optional[List[float]] = Field(None, description="参考线值，如RSI的30、70")


class IndicatorMetadata(BaseModel):
    """指标完整元数据"""

    abbreviation: str = Field(..., description="指标缩写（如SMA、RSI）")
    full_name: str = Field(..., description="指标完整英文名称")
    chinese_name: str = Field(..., description="指标中文名称")
    category: IndicatorCategory = Field(..., description="指标分类")
    description: str = Field(..., description="指标功能描述")

    version: str = Field("1.0.0", description="指标版本号")

    parameters: List[IndicatorParameter] = Field(default_factory=list, description="参数列表")

    outputs: List[IndicatorOutput] = Field(default_factory=list, description="输出列表")

    dependencies: List[str] = Field(default_factory=list, description="依赖的其他指标缩写")

    data_requirements: List[DataField] = Field(
        default_factory=lambda: [DataField.CLOSE], description="需要的基础数据字段"
    )

    panel_type: PanelType = Field(PanelType.OVERLAY, description="显示面板类型")

    display_colors: List[str] = Field(default_factory=list, description="显示颜色列表")

    line_width: float = Field(1.5, description="线条宽度")

    complexity: ComplexityLevel = Field(ComplexityLevel.LOW, description="计算复杂度")

    performance_tags: List[str] = Field(default_factory=list, description="性能标签，如['cpu', 'memory']")

    deprecated: bool = Field(False, description="是否已废弃")
    replaced_by: Optional[str] = Field(None, description="替代指标")
    changelog: List[str] = Field(default_factory=list, description="版本变更记录")

    author: str = Field("", description="指标作者")
    created_at: str = Field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"), description="创建时间")
    updated_at: str = Field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"), description="更新时间")

    class Config:
        use_enum_values = True
        json_encoders = {
            IndicatorParameter: lambda v: v.dict(),
            IndicatorOutput: lambda v: v.dict(),
            ComplexityLevel: lambda v: v.value,
            PanelType: lambda v: v.value,
            IndicatorCategory: lambda v: v.value,
        }

    def get_parameter(self, name: str) -> Optional[IndicatorParameter]:
        """根据名称获取参数"""
        for param in self.parameters:
            if param.name == name:
                return param
        return None

    def get_output(self, name: str) -> Optional[IndicatorOutput]:
        """根据名称获取输出"""
        for output in self.outputs:
            if output.name == name:
                return output
        return None

    def get_min_data_points(self, params: Dict[str, Any]) -> int:
        """计算所需最小数据点数"""
        if not self.parameters:
            return 1

        max_period = 0
        for param in self.parameters:
            if param.name in params:
                value = params[param.name]
            else:
                value = param.default

            if param.name in [
                "timeperiod",
                "period",
                "fastperiod",
                "slowperiod",
                "signalperiod",
                "k_period",
                "d_period",
                "j_period",
            ]:
                max_period = max(max_period, int(value))

        return max_period if max_period > 0 else 1

    def validate_parameters(self, params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """验证参数值"""
        for param in self.parameters:
            if param.name in params:
                value = params[param.name]
                is_valid, error_msg = param.constraints.validate(value)
                if not is_valid:
                    return False, f"参数 {param.name}: {error_msg}"
        return True, None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IndicatorMetadata":
        """从字典创建"""
        return cls(**data)


class IndicatorTemplate(BaseModel):
    """指标模板配置"""

    id: str = Field(..., description="模板ID")
    name: str = Field(..., description="模板名称")
    description: str = Field("", description="模板描述")
    indicators: List[Dict[str, Any]] = Field(..., description="指标配置列表")
    market_type: str = Field("medium", description="适用市场类型")
    tags: List[str] = Field(default_factory=list, description="标签")


class IndicatorConfig(BaseModel):
    """完整指标配置"""

    version: str = Field("1.0.0", description="配置版本")
    indicators: Dict[str, Dict] = Field(..., description="所有指标配置")
    templates: Dict[str, IndicatorTemplate] = Field(default_factory=dict, description="指标模板")
    environments: Dict[str, Dict] = Field(default_factory=dict, description="环境差异化配置")

    class Config:
        json_encoders = {IndicatorTemplate: lambda v: v.dict()}
