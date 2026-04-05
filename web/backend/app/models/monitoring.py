"""
监控系统数据模型
Real-time Monitoring System
"""

from datetime import date, datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import (
    DECIMAL,
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class AlertRule(Base):
    """告警规则表"""

    __tablename__ = "alert_rule"

    id = Column(Integer, primary_key=True)
    rule_name = Column(String(100), nullable=False, unique=True)
    rule_type = Column(String(50), nullable=False)  # price_change, volume_surge, technical_break, etc.
    description = Column(Text)
    symbol = Column(String(20), index=True)  # NULL表示全市场规则
    stock_name = Column(String(100))

    # 规则参数
    parameters = Column(JSONB, default=dict)
    trigger_conditions = Column(JSONB, default=dict)
    notification_config = Column(JSONB, default=dict)

    # 状态和元数据
    is_active = Column(Boolean, default=True, index=True)
    priority = Column(Integer, default=1)  # 1-5
    created_by = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    alert_records = relationship("AlertRecord", back_populates="rule")

    def __repr__(self):
        return f"<AlertRule(id={self.id}, name='{self.rule_name}', type='{self.rule_type}')>"


class AlertRecord(Base):
    """告警记录表"""

    __tablename__ = "alert_record"

    id = Column(Integer, primary_key=True)
    rule_id = Column(Integer, ForeignKey("alert_rule.id", ondelete="SET NULL"))
    rule_name = Column(String(100))

    # 股票信息
    symbol = Column(String(20), nullable=False, index=True)
    stock_name = Column(String(100))

    # 告警信息
    alert_time = Column(DateTime, default=datetime.now, index=True)
    alert_type = Column(String(50), nullable=False, index=True)
    alert_level = Column(String(20), default="info", index=True)  # info, warning, critical
    alert_title = Column(String(200))
    alert_message = Column(Text)
    alert_details = Column(JSONB)

    # 市场数据快照
    snapshot_data = Column(JSONB)

    # 状态
    is_read = Column(Boolean, default=False, index=True)
    is_handled = Column(Boolean, default=False)
    handled_by = Column(String(50))
    handled_at = Column(DateTime)
    handle_note = Column(Text)

    created_at = Column(DateTime, default=datetime.now)

    # 关系
    rule = relationship("AlertRule", back_populates="alert_records")

    def __repr__(self):
        return (
            f"<AlertRecord(id={self.id}, symbol='{self.symbol}', type='{self.alert_type}', level='{self.alert_level}')>"
        )


class RealtimeMonitoring(Base):
    """实时监控数据表"""

    __tablename__ = "realtime_monitoring"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    stock_name = Column(String(100))

    # 时间戳
    timestamp = Column(DateTime, nullable=False, index=True)
    trade_date = Column(Date, nullable=False, index=True)

    # 行情数据
    price = Column(DECIMAL(10, 2))
    open_price = Column(DECIMAL(10, 2))
    high_price = Column(DECIMAL(10, 2))
    low_price = Column(DECIMAL(10, 2))
    pre_close = Column(DECIMAL(10, 2))

    # 涨跌信息
    change_amount = Column(DECIMAL(10, 2))
    change_percent = Column(DECIMAL(10, 2))

    # 成交信息
    volume = Column(BigInteger)  # 成交量(手)
    amount = Column(DECIMAL(20, 2))  # 成交额(元)
    turnover_rate = Column(DECIMAL(10, 2))  # 换手率

    # 技术指标
    indicators = Column(JSONB, default=dict)

    # 市场强度
    market_strength = Column(String(20))  # strong, normal, weak

    # 特殊标记
    is_limit_up = Column(Boolean, default=False, index=True)
    is_limit_down = Column(Boolean, default=False, index=True)
    is_st = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (Index("idx_realtime_symbol_time", "symbol", "timestamp"),)

    def __repr__(self):
        return f"<RealtimeMonitoring(id={self.id}, symbol='{self.symbol}', price={self.price})>"


class DragonTigerList(Base):
    """龙虎榜数据表"""

    __tablename__ = "dragon_tiger_list"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    stock_name = Column(String(100))
    trade_date = Column(Date, nullable=False, index=True)

    # 上榜原因
    reason = Column(String(200))
    reason_code = Column(String(50))

    # 买卖数据
    total_buy_amount = Column(DECIMAL(20, 2))
    total_sell_amount = Column(DECIMAL(20, 2))
    net_amount = Column(DECIMAL(20, 2), index=True)  # 净买入额

    # 机构席位
    institution_buy_count = Column(Integer, default=0)
    institution_sell_count = Column(Integer, default=0)
    institution_net_amount = Column(DECIMAL(20, 2))

    # 详细数据
    detail_data = Column(JSONB)

    # 影响评估
    impact_score = Column(Integer)  # 1-10

    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (UniqueConstraint("symbol", "trade_date", name="uq_dragon_tiger_symbol_date"),)

    def __repr__(self):
        return f"<DragonTigerList(id={self.id}, symbol='{self.symbol}', date={self.trade_date})>"


class MonitoringStatistics(Base):
    """监控统计表"""

    __tablename__ = "monitoring_statistics"

    id = Column(Integer, primary_key=True)
    stat_date = Column(Date, nullable=False, index=True)
    stat_hour = Column(Integer)  # 0-23

    # 监控覆盖
    total_monitored_stocks = Column(Integer)
    active_alerts = Column(Integer)

    # 告警统计
    total_alerts_triggered = Column(Integer)
    alerts_by_type = Column(JSONB)
    alerts_by_level = Column(JSONB)

    # 市场统计
    limit_up_count = Column(Integer)
    limit_down_count = Column(Integer)
    dragon_tiger_count = Column(Integer)

    # 性能指标
    avg_response_time_ms = Column(Integer)
    data_update_frequency = Column(Integer)

    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (UniqueConstraint("stat_date", "stat_hour", name="uq_monitoring_stat_date_hour"),)

    def __repr__(self):
        return f"<MonitoringStatistics(date={self.stat_date}, hour={self.stat_hour})>"


# ============================================================================
# Pydantic schemas for API request/response
# ============================================================================

from enum import Enum


class AlertRuleType(str, Enum):
    """告警规则类型枚举"""

    PRICE_CHANGE = "price_change"
    VOLUME_SURGE = "volume_surge"
    TECHNICAL_BREAK = "technical_break"
    LIMIT_UP = "limit_up"
    LIMIT_DOWN = "limit_down"
    DRAGON_TIGER = "dragon_tiger"


class AlertLevel(str, Enum):
    """告警级别枚举"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertRuleCreate(BaseModel):
    """创建告警规则请求"""

    rule_name: str = Field(..., min_length=1, max_length=100, description="告警规则名称。")
    rule_type: AlertRuleType = Field(..., description="告警规则类型枚举。")
    description: Optional[str] = Field(None, description="规则业务说明。")
    symbol: Optional[str] = Field(None, description="绑定的股票或合约代码；为空表示全市场。")
    stock_name: Optional[str] = Field(None, description="股票或合约名称。")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="规则参数配置。")
    trigger_conditions: Dict[str, Any] = Field(default_factory=dict, description="触发条件配置。")
    notification_config: Dict[str, Any] = Field(default_factory=dict, description="通知策略配置。")
    priority: int = Field(default=1, ge=1, le=5, description="规则优先级，1 为最低，5 为最高。")
    is_active: bool = Field(True, description="规则是否启用。")

    @field_validator("rule_name")
    @classmethod
    def validate_rule_name(cls, v):
        if not v or not v.strip():
            raise ValueError("规则名称不能为空")
        return v.strip()


class AlertRuleUpdate(BaseModel):
    """更新告警规则请求"""

    rule_name: Optional[str] = Field(None, description="更新后的规则名称。")
    description: Optional[str] = Field(None, description="更新后的规则说明。")
    parameters: Optional[Dict[str, Any]] = Field(None, description="更新后的规则参数。")
    trigger_conditions: Optional[Dict[str, Any]] = Field(None, description="更新后的触发条件。")
    notification_config: Optional[Dict[str, Any]] = Field(None, description="更新后的通知配置。")
    priority: Optional[int] = Field(None, ge=1, le=5, description="更新后的规则优先级。")
    is_active: Optional[bool] = Field(None, description="更新后的启用状态。")


class AlertRuleResponse(BaseModel):
    """告警规则响应"""

    id: int = Field(..., description="规则主键ID。")
    rule_name: str = Field(..., description="规则名称。")
    rule_type: str = Field(..., description="规则类型。")
    description: Optional[str] = Field(None, description="规则说明。")
    symbol: Optional[str] = Field(None, description="绑定的股票或合约代码。")
    stock_name: Optional[str] = Field(None, description="股票或合约名称。")
    parameters: Dict[str, Any] = Field(..., description="规则参数。")
    trigger_conditions: Dict[str, Any] = Field(..., description="触发条件。")
    notification_config: Dict[str, Any] = Field(..., description="通知配置。")
    is_active: bool = Field(..., description="规则是否启用。")
    priority: int = Field(..., description="规则优先级。")
    created_at: datetime = Field(..., description="规则创建时间。")
    updated_at: datetime = Field(..., description="规则最近更新时间。")

    model_config = ConfigDict(from_attributes=True)


class AlertRecordResponse(BaseModel):
    """告警记录响应"""

    id: int = Field(..., description="告警记录主键ID。")
    rule_id: Optional[int] = Field(None, description="关联的规则ID。")
    rule_name: Optional[str] = Field(None, description="关联规则名称。")
    symbol: str = Field(..., description="触发告警的股票或合约代码。")
    stock_name: Optional[str] = Field(None, description="股票或合约名称。")
    alert_time: datetime = Field(..., description="告警触发时间。")
    alert_type: str = Field(..., description="告警类型。")
    alert_level: str = Field(..., description="告警级别。")
    alert_title: Optional[str] = Field(None, description="告警标题。")
    alert_message: Optional[str] = Field(None, description="告警消息正文。")
    alert_details: Optional[Dict[str, Any]] = Field(None, description="结构化告警详情。")
    snapshot_data: Optional[Dict[str, Any]] = Field(None, description="触发时快照数据。")
    is_read: bool = Field(..., description="是否已读。")
    is_handled: bool = Field(..., description="是否已处理。")
    created_at: datetime = Field(..., description="记录创建时间。")

    model_config = ConfigDict(from_attributes=True)


class RealtimeMonitoringResponse(BaseModel):
    """实时监控数据响应"""

    id: int = Field(..., description="实时监控记录ID。")
    symbol: str = Field(..., description="股票或合约代码。")
    stock_name: Optional[str] = Field(None, description="股票或合约名称。")
    timestamp: datetime = Field(..., description="监控快照时间。")
    trade_date: date = Field(..., description="交易日期。")
    price: Optional[float] = Field(None, description="最新价格。")
    change_percent: Optional[float] = Field(None, description="涨跌幅百分比。")
    volume: Optional[int] = Field(None, description="成交量。")
    amount: Optional[float] = Field(None, description="成交额。")
    indicators: Optional[Dict[str, Any]] = Field(None, description="技术指标快照。")
    market_strength: Optional[str] = Field(None, description="市场强弱标签。")
    is_limit_up: bool = Field(..., description="是否涨停。")
    is_limit_down: bool = Field(..., description="是否跌停。")

    model_config = ConfigDict(from_attributes=True)


class DragonTigerListResponse(BaseModel):
    """龙虎榜响应"""

    id: int = Field(..., description="龙虎榜记录ID。")
    symbol: str = Field(..., description="股票代码。")
    stock_name: Optional[str] = Field(None, description="股票名称。")
    trade_date: date = Field(..., description="上榜交易日期。")
    reason: Optional[str] = Field(None, description="上榜原因。")
    total_buy_amount: Optional[float] = Field(None, description="总买入金额。")
    total_sell_amount: Optional[float] = Field(None, description="总卖出金额。")
    net_amount: Optional[float] = Field(None, description="净买入金额。")
    institution_buy_count: int = Field(..., description="机构买入席位数量。")
    institution_sell_count: int = Field(..., description="机构卖出席位数量。")
    institution_net_amount: Optional[float] = Field(None, description="机构净买入金额。")
    detail_data: Optional[Dict[str, Any]] = Field(None, description="龙虎榜明细数据。")
    impact_score: Optional[int] = Field(None, description="影响评分。")

    model_config = ConfigDict(from_attributes=True)


class MonitoringSummaryResponse(BaseModel):
    """监控摘要响应"""

    total_stocks: int = Field(0, description="纳入监控的股票总数。")
    limit_up_count: int = Field(0, description="涨停数量。")
    limit_down_count: int = Field(0, description="跌停数量。")
    strong_up_count: int = Field(0, description="强势上涨股票数量。")
    strong_down_count: int = Field(0, description="强势下跌股票数量。")
    avg_change_percent: Optional[float] = Field(None, description="平均涨跌幅。")
    total_amount: Optional[float] = Field(None, description="总成交额。")
    active_alerts: int = Field(0, description="当前活跃告警数量。")
    unread_alerts: int = Field(0, description="未读告警数量。")
