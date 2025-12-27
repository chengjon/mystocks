"""
股票策略模型 (SQLAlchemy ORM)

包含2个核心实体:
- StrategyDefinition: 策略定义和元数据
- StrategyResult: 策略筛选结果
"""

from sqlalchemy import (
    Column,
    String,
    Date,
    Boolean,
    Text,
    Integer,
    BigInteger,
    TIMESTAMP,
    Index,
    JSON,
)
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class StrategyDefinition(Base):
    """策略定义表"""

    __tablename__ = "strategy_definition"

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_code = Column(String(50), unique=True, nullable=False, comment="策略代码")
    strategy_name_cn = Column(String(100), nullable=False, comment="策略中文名")
    strategy_name_en = Column(String(100), nullable=False, comment="策略英文名")
    description = Column(Text, comment="策略描述")
    parameters = Column(JSON, comment="策略参数(JSON格式)")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    __table_args__ = (
        Index("idx_strategy_code", "strategy_code"),
        {"comment": "策略定义表"},
    )

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "strategy_code": self.strategy_code,
            "strategy_name_cn": self.strategy_name_cn,
            "strategy_name_en": self.strategy_name_en,
            "description": self.description,
            "parameters": self.parameters,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class StrategyResult(Base):
    """策略筛选结果表"""

    __tablename__ = "strategy_result"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    strategy_code = Column(String(50), nullable=False, comment="策略代码")
    symbol = Column(String(20), nullable=False, comment="股票代码")
    stock_name = Column(String(100), comment="股票名称")
    check_date = Column(Date, nullable=False, comment="检查日期")
    match_result = Column(Boolean, nullable=False, comment="是否匹配策略条件")
    match_score = Column(Integer, comment="匹配度评分(0-100)")
    match_details = Column(JSON, comment="匹配详情(JSON格式)")
    latest_price = Column(String(20), comment="最新价")
    change_percent = Column(String(20), comment="涨跌幅")
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="创建时间")

    __table_args__ = (
        Index("idx_strategy_result_code_date", "strategy_code", "check_date"),
        Index("idx_strategy_result_symbol_date", "symbol", "check_date"),
        Index("idx_strategy_result_match", "match_result", "check_date"),
        {"comment": "策略筛选结果表"},
    )

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "strategy_code": self.strategy_code,
            "symbol": self.symbol,
            "stock_name": self.stock_name,
            "check_date": self.check_date.isoformat() if self.check_date else None,
            "match_result": self.match_result,
            "match_score": self.match_score,
            "match_details": self.match_details,
            "latest_price": self.latest_price,
            "change_percent": self.change_percent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class StrategyBacktest(Base):
    """策略回测结果表"""

    __tablename__ = "strategy_backtest"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    strategy_code = Column(String(50), nullable=False, comment="策略代码")
    symbol = Column(String(20), nullable=False, comment="股票代码")
    stock_name = Column(String(100), comment="股票名称")
    signal_date = Column(Date, nullable=False, comment="信号日期")
    entry_price = Column(String(20), comment="入场价格")
    exit_price = Column(String(20), comment="出场价格")
    exit_date = Column(Date, comment="出场日期")
    holding_days = Column(Integer, comment="持有天数")
    return_rate = Column(String(20), comment="收益率(%)")
    max_drawdown = Column(String(20), comment="最大回撤(%)")
    backtest_period = Column(String(50), comment="回测区间")
    parameters = Column(JSON, comment="策略参数")
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="创建时间")

    __table_args__ = (
        Index("idx_backtest_code_date", "strategy_code", "signal_date"),
        Index("idx_backtest_symbol", "symbol", "signal_date"),
        {"comment": "策略回测结果表"},
    )

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "strategy_code": self.strategy_code,
            "symbol": self.symbol,
            "stock_name": self.stock_name,
            "signal_date": self.signal_date.isoformat() if self.signal_date else None,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "exit_date": self.exit_date.isoformat() if self.exit_date else None,
            "holding_days": self.holding_days,
            "return_rate": self.return_rate,
            "max_drawdown": self.max_drawdown,
            "backtest_period": self.backtest_period,
            "parameters": self.parameters,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
