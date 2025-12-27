# -*- coding: utf-8 -*-
# 功能：股票基础信息模型
# 作者：JohnC (ninjas@sina.com) & Claude
# 日期：2025-11-24
# 版本：1.0.0
# 版权：© 2025 MyStocks Project

"""
股票基础信息模型 (SQLAlchemy ORM)

定义 stock_info 表的ORM模型。
"""

from datetime import datetime

from sqlalchemy import DECIMAL, TIMESTAMP, Column, Date, Index, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class StockInfo(Base):
    """股票基础信息表"""

    __tablename__ = "stock_info"

    symbol = Column(String(20), primary_key=True, nullable=False, comment="股票代码")
    name = Column(String(100), nullable=False, comment="股票名称")
    exchange = Column(String(20), comment="交易所")
    security_type = Column(String(50), comment="证券类型")
    list_date = Column(Date, comment="上市日期")
    status = Column(String(20), comment="上市状态")
    listing_board = Column(String(50), comment="上市板块")
    market_cap = Column(DECIMAL(25, 2), comment="总市值")
    circulating_market_cap = Column(DECIMAL(25, 2), comment="流通市值")
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    __table_args__ = (
        Index("idx_stock_info_name", "name"),
        Index("idx_stock_info_exchange", "exchange"),
        Index("idx_stock_info_security_type", "security_type"),
        {"comment": "股票基础信息表"},
    )

    def to_dict(self):
        """转换为字典"""
        return {
            "symbol": self.symbol,
            "name": self.name,
            "exchange": self.exchange,
            "security_type": self.security_type,
            "list_date": self.list_date.isoformat() if self.list_date else None,
            "status": self.status,
            "listing_board": self.listing_board,
            "market_cap": float(self.market_cap) if self.market_cap else None,
            "circulating_market_cap": (float(self.circulating_market_cap) if self.circulating_market_cap else None),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
