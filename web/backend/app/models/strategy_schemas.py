"""
策略管理数据模型

定义策略管理相关的Pydantic模型，用于策略CRUD和回测引擎的API请求和响应。

版本: 1.0.0
日期: 2025-11-21
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


# ============================================================================
# 枚举类型
# ============================================================================

class StrategyStatus(str, Enum):
    """策略状态"""
    DRAFT = "draft"  # 草稿
    ACTIVE = "active"  # 激活
    PAUSED = "paused"  # 暂停
    ARCHIVED = "archived"  # 归档


class StrategyType(str, Enum):
    """策略类型"""
    MOMENTUM = "momentum"  # 动量策略
    MEAN_REVERSION = "mean_reversion"  # 均值回归
    BREAKOUT = "breakout"  # 突破策略
    GRID = "grid"  # 网格策略
    CUSTOM = "custom"  # 自定义策略


class BacktestStatus(str, Enum):
    """回测状态"""
    PENDING = "pending"  # 等待中
    RUNNING = "running"  # 运行中
    COMPLETED = "completed"  # 完成
    FAILED = "failed"  # 失败


# ============================================================================
# 策略配置模型
# ============================================================================

class StrategyParameter(BaseModel):
    """策略参数"""
    name: str = Field(..., description="参数名称")
    value: Any = Field(..., description="参数值")
    description: Optional[str] = Field(None, description="参数说明")
    data_type: str = Field("string", description="数据类型: string/int/float/bool")


class StrategyConfig(BaseModel):
    """策略配置"""
    strategy_id: Optional[int] = Field(None, description="策略ID (创建时为None)")
    user_id: int = Field(..., description="用户ID", ge=1)
    strategy_name: str = Field(..., description="策略名称", min_length=1, max_length=100)
    strategy_type: StrategyType = Field(..., description="策略类型")
    description: Optional[str] = Field(None, description="策略描述", max_length=500)

    # 策略参数
    parameters: List[StrategyParameter] = Field(
        default_factory=list,
        description="策略参数列表"
    )

    # 风险控制
    max_position_size: float = Field(0.1, description="最大仓位比例 (0-1)", ge=0, le=1)
    stop_loss_percent: Optional[float] = Field(None, description="止损百分比", ge=0, le=100)
    take_profit_percent: Optional[float] = Field(None, description="止盈百分比", ge=0)

    # 状态和元数据
    status: StrategyStatus = Field(StrategyStatus.DRAFT, description="策略状态")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    tags: List[str] = Field(default_factory=list, description="标签列表")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1001,
                "strategy_name": "双均线策略",
                "strategy_type": "momentum",
                "description": "基于5日和20日均线的金叉死叉策略",
                "parameters": [
                    {
                        "name": "short_period",
                        "value": 5,
                        "description": "短期均线周期",
                        "data_type": "int"
                    },
                    {
                        "name": "long_period",
                        "value": 20,
                        "description": "长期均线周期",
                        "data_type": "int"
                    }
                ],
                "max_position_size": 0.2,
                "stop_loss_percent": 5.0,
                "take_profit_percent": 10.0,
                "status": "active",
                "tags": ["均线", "趋势跟踪"]
            }
        }


class StrategyCreateRequest(BaseModel):
    """创建策略请求"""
    user_id: int = Field(..., description="用户ID", ge=1)
    strategy_name: str = Field(..., description="策略名称", min_length=1, max_length=100)
    strategy_type: StrategyType = Field(..., description="策略类型")
    description: Optional[str] = Field(None, description="策略描述", max_length=500)
    parameters: List[StrategyParameter] = Field(default_factory=list, description="策略参数")
    max_position_size: float = Field(0.1, description="最大仓位比例", ge=0, le=1)
    stop_loss_percent: Optional[float] = Field(None, description="止损百分比", ge=0, le=100)
    take_profit_percent: Optional[float] = Field(None, description="止盈百分比", ge=0)
    tags: List[str] = Field(default_factory=list, description="标签列表")


class StrategyUpdateRequest(BaseModel):
    """更新策略请求"""
    strategy_name: Optional[str] = Field(None, description="策略名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="策略描述", max_length=500)
    parameters: Optional[List[StrategyParameter]] = Field(None, description="策略参数")
    max_position_size: Optional[float] = Field(None, description="最大仓位比例", ge=0, le=1)
    stop_loss_percent: Optional[float] = Field(None, description="止损百分比", ge=0, le=100)
    take_profit_percent: Optional[float] = Field(None, description="止盈百分比", ge=0)
    status: Optional[StrategyStatus] = Field(None, description="策略状态")
    tags: Optional[List[str]] = Field(None, description="标签列表")


class StrategyListResponse(BaseModel):
    """策略列表响应"""
    total_count: int = Field(..., description="总数量")
    strategies: List[StrategyConfig] = Field(..., description="策略列表")
    page: int = Field(1, description="当前页码", ge=1)
    page_size: int = Field(20, description="每页数量", ge=1, le=100)


# ============================================================================
# 回测请求模型
# ============================================================================

class BacktestRequest(BaseModel):
    """回测请求"""
    strategy_id: int = Field(..., description="策略ID", ge=1)
    user_id: int = Field(..., description="用户ID", ge=1)

    # 回测范围
    symbols: List[str] = Field(..., description="股票代码列表", min_items=1)
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")

    # 初始资金和成本
    initial_capital: float = Field(100000.0, description="初始资金", ge=1000)
    commission_rate: float = Field(0.0003, description="手续费率", ge=0, le=0.01)
    slippage_rate: float = Field(0.001, description="滑点率", ge=0, le=0.01)

    # 回测选项
    benchmark: Optional[str] = Field(None, description="基准指数代码")
    include_analysis: bool = Field(True, description="是否包含详细分析")

    @validator('end_date')
    def validate_date_range(cls, v, values):
        """验证日期范围"""
        if 'start_date' in values and v < values['start_date']:
            raise ValueError("结束日期必须晚于开始日期")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "strategy_id": 123,
                "user_id": 1001,
                "symbols": ["000001.SZ", "600000.SH"],
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "initial_capital": 100000.0,
                "commission_rate": 0.0003,
                "slippage_rate": 0.001,
                "benchmark": "000300.SH",
                "include_analysis": True
            }
        }


# ============================================================================
# 回测结果模型
# ============================================================================

class TradeRecord(BaseModel):
    """交易记录"""
    trade_id: int = Field(..., description="交易ID")
    symbol: str = Field(..., description="股票代码")
    trade_date: date = Field(..., description="交易日期")
    action: str = Field(..., description="操作: buy/sell")
    price: float = Field(..., description="成交价格", ge=0)
    quantity: int = Field(..., description="数量", ge=0)
    amount: float = Field(..., description="交易金额", ge=0)
    commission: float = Field(..., description="手续费", ge=0)
    profit_loss: Optional[float] = Field(None, description="盈亏金额")


class PerformanceMetrics(BaseModel):
    """绩效指标"""
    # 收益指标
    total_return: float = Field(..., description="总收益率 (%)")
    annual_return: float = Field(..., description="年化收益率 (%)")
    benchmark_return: Optional[float] = Field(None, description="基准收益率 (%)")
    alpha: Optional[float] = Field(None, description="阿尔法值")
    beta: Optional[float] = Field(None, description="贝塔值")

    # 风险指标
    sharpe_ratio: float = Field(..., description="夏普比率")
    max_drawdown: float = Field(..., description="最大回撤 (%)", le=0)
    volatility: float = Field(..., description="波动率 (%)", ge=0)

    # 交易统计
    total_trades: int = Field(..., description="总交易次数", ge=0)
    win_rate: float = Field(..., description="胜率 (%)", ge=0, le=100)
    profit_factor: float = Field(..., description="盈亏比", ge=0)

    # 其他指标
    calmar_ratio: Optional[float] = Field(None, description="卡玛比率")
    sortino_ratio: Optional[float] = Field(None, description="索提诺比率")


class EquityCurvePoint(BaseModel):
    """权益曲线点"""
    date: date = Field(..., description="日期")
    equity: float = Field(..., description="权益", ge=0)
    drawdown: float = Field(..., description="回撤 (%)", le=0)
    benchmark_equity: Optional[float] = Field(None, description="基准权益")


class BacktestResult(BaseModel):
    """回测结果"""
    backtest_id: int = Field(..., description="回测ID")
    strategy_id: int = Field(..., description="策略ID")
    user_id: int = Field(..., description="用户ID")

    # 回测配置
    symbols: List[str] = Field(..., description="股票代码列表")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    initial_capital: float = Field(..., description="初始资金")

    # 回测结果
    final_capital: float = Field(..., description="最终资金", ge=0)
    performance: PerformanceMetrics = Field(..., description="绩效指标")
    equity_curve: List[EquityCurvePoint] = Field(
        default_factory=list,
        description="权益曲线"
    )
    trades: List[TradeRecord] = Field(default_factory=list, description="交易记录")

    # 元数据
    status: BacktestStatus = Field(..., description="回测状态")
    created_at: datetime = Field(..., description="创建时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    error_message: Optional[str] = Field(None, description="错误消息")

    class Config:
        json_schema_extra = {
            "example": {
                "backtest_id": 456,
                "strategy_id": 123,
                "user_id": 1001,
                "symbols": ["000001.SZ", "600000.SH"],
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "initial_capital": 100000.0,
                "final_capital": 115000.0,
                "performance": {
                    "total_return": 15.0,
                    "annual_return": 15.0,
                    "benchmark_return": 8.0,
                    "alpha": 7.0,
                    "beta": 1.05,
                    "sharpe_ratio": 1.8,
                    "max_drawdown": -8.5,
                    "volatility": 12.3,
                    "total_trades": 45,
                    "win_rate": 62.2,
                    "profit_factor": 1.85,
                    "calmar_ratio": 1.76,
                    "sortino_ratio": 2.1
                },
                "equity_curve": [],
                "trades": [],
                "status": "completed",
                "created_at": "2024-12-01T10:00:00",
                "completed_at": "2024-12-01T10:05:00"
            }
        }


class BacktestResultSummary(BaseModel):
    """回测结果汇总"""
    backtest_id: int = Field(..., description="回测ID")
    strategy_id: int = Field(..., description="策略ID")
    strategy_name: str = Field(..., description="策略名称")
    symbols: List[str] = Field(..., description="股票列表")
    date_range: str = Field(..., description="日期范围")
    total_return: float = Field(..., description="总收益率 (%)")
    sharpe_ratio: float = Field(..., description="夏普比率")
    max_drawdown: float = Field(..., description="最大回撤 (%)")
    status: BacktestStatus = Field(..., description="回测状态")
    created_at: datetime = Field(..., description="创建时间")


class BacktestListResponse(BaseModel):
    """回测列表响应"""
    total_count: int = Field(..., description="总数量")
    backtests: List[BacktestResultSummary] = Field(..., description="回测列表")
    page: int = Field(1, description="当前页码", ge=1)
    page_size: int = Field(20, description="每页数量", ge=1, le=100)


# ============================================================================
# 错误响应模型
# ============================================================================

class StrategyErrorResponse(BaseModel):
    """策略管理错误响应"""
    error_code: str = Field(..., description="错误代码")
    error_message: str = Field(..., description="错误消息")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误时间")

    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "STRATEGY_NOT_FOUND",
                "error_message": "策略不存在",
                "details": {"strategy_id": 123},
                "timestamp": "2025-11-21T10:30:00"
            }
        }
