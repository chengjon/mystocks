"""
市场数据模型 (SQLAlchemy ORM)

包含7个核心实体:
- FundFlow: 个股资金流向
- ETFData: ETF基金数据
- ChipRaceData: 竞价抢筹数据
- LongHuBangData: 龙虎榜数据
- SectorFundFlow: 行业/概念资金流向
- StockDividend: 股票分红配送
- StockBlockTrade: 股票大宗交易
"""

from sqlalchemy import (
    Column,
    String,
    Date,
    DECIMAL,
    BigInteger,
    Integer,
    TIMESTAMP,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class FundFlow(Base):
    """个股资金流向表"""

    __tablename__ = "stock_fund_flow"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, comment="股票代码")
    trade_date = Column(Date, primary_key=True, nullable=False, comment="交易日期")
    timeframe = Column(String(10), nullable=False, comment="时间维度(1/3/5/10天)")
    main_net_inflow = Column(DECIMAL(20, 2), comment="主力净流入额")
    main_net_inflow_rate = Column(DECIMAL(10, 4), comment="主力净流入占比")
    super_large_net_inflow = Column(DECIMAL(20, 2), comment="超大单净流入额")
    large_net_inflow = Column(DECIMAL(20, 2), comment="大单净流入额")
    medium_net_inflow = Column(DECIMAL(20, 2), comment="中单净流入额")
    small_net_inflow = Column(DECIMAL(20, 2), comment="小单净流入额")
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="创建时间")

    __table_args__ = (
        Index("idx_stock_fund_flow_symbol_date", "symbol", "trade_date"),
        Index("idx_stock_fund_flow_timeframe", "timeframe", "trade_date"),
        {"comment": "个股资金流向表"},
    )

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "trade_date": self.trade_date.isoformat() if self.trade_date else None,
            "timeframe": self.timeframe,
            "main_net_inflow": (
                float(self.main_net_inflow) if self.main_net_inflow else 0
            ),
            "main_net_inflow_rate": (
                float(self.main_net_inflow_rate) if self.main_net_inflow_rate else 0
            ),
            "super_large_net_inflow": (
                float(self.super_large_net_inflow) if self.super_large_net_inflow else 0
            ),
            "large_net_inflow": (
                float(self.large_net_inflow) if self.large_net_inflow else 0
            ),
            "medium_net_inflow": (
                float(self.medium_net_inflow) if self.medium_net_inflow else 0
            ),
            "small_net_inflow": (
                float(self.small_net_inflow) if self.small_net_inflow else 0
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ETFData(Base):
    """ETF实时数据表"""

    __tablename__ = "etf_spot_data"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, comment="ETF代码")
    name = Column(String(100), comment="ETF名称")
    trade_date = Column(Date, primary_key=True, nullable=False, comment="交易日期")
    latest_price = Column(DECIMAL(10, 3), comment="最新价")
    change_percent = Column(DECIMAL(10, 4), comment="涨跌幅")
    change_amount = Column(DECIMAL(10, 3), comment="涨跌额")
    volume = Column(BigInteger, comment="成交量")
    amount = Column(DECIMAL(20, 2), comment="成交额")
    open_price = Column(DECIMAL(10, 3), comment="开盘价")
    high_price = Column(DECIMAL(10, 3), comment="最高价")
    low_price = Column(DECIMAL(10, 3), comment="最低价")
    prev_close = Column(DECIMAL(10, 3), comment="昨收价")
    turnover_rate = Column(DECIMAL(10, 4), comment="换手率")
    total_market_cap = Column(DECIMAL(20, 2), comment="总市值")
    circulating_market_cap = Column(DECIMAL(20, 2), comment="流通市值")
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="创建时间")

    __table_args__ = (
        Index("idx_etf_spot_symbol", "symbol", "trade_date"),
        {"comment": "ETF实时数据表"},
    )

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "name": self.name,
            "trade_date": self.trade_date.isoformat() if self.trade_date else None,
            "latest_price": float(self.latest_price) if self.latest_price else 0,
            "change_percent": float(self.change_percent) if self.change_percent else 0,
            "change_amount": float(self.change_amount) if self.change_amount else 0,
            "volume": int(self.volume) if self.volume else 0,
            "amount": float(self.amount) if self.amount else 0,
            "open_price": float(self.open_price) if self.open_price else 0,
            "high_price": float(self.high_price) if self.high_price else 0,
            "low_price": float(self.low_price) if self.low_price else 0,
            "prev_close": float(self.prev_close) if self.prev_close else 0,
            "turnover_rate": float(self.turnover_rate) if self.turnover_rate else 0,
            "total_market_cap": (
                float(self.total_market_cap) if self.total_market_cap else 0
            ),
            "circulating_market_cap": (
                float(self.circulating_market_cap) if self.circulating_market_cap else 0
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ChipRaceData(Base):
    """竞价抢筹数据表"""

    __tablename__ = "chip_race_data"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, comment="股票代码")
    name = Column(String(100), comment="股票名称")
    trade_date = Column(Date, primary_key=True, nullable=False, comment="交易日期")
    race_type = Column(String(10), nullable=False, comment="抢筹类型(open/end)")
    latest_price = Column(DECIMAL(10, 3), comment="最新价")
    change_percent = Column(DECIMAL(10, 4), comment="涨跌幅")
    prev_close = Column(DECIMAL(10, 3), comment="昨收价")
    open_price = Column(DECIMAL(10, 3), comment="今开价")
    race_amount = Column(DECIMAL(20, 2), comment="抢筹金额")
    race_amplitude = Column(DECIMAL(10, 4), comment="抢筹幅度")
    race_commission = Column(DECIMAL(20, 2), comment="抢筹委托金额")
    race_transaction = Column(DECIMAL(20, 2), comment="抢筹成交金额")
    race_ratio = Column(DECIMAL(10, 4), comment="抢筹占比")
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="创建时间")

    __table_args__ = (
        Index("idx_chip_race_symbol", "symbol", "trade_date"),
        {"comment": "竞价抢筹数据表"},
    )

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "name": self.name,
            "trade_date": self.trade_date.isoformat() if self.trade_date else None,
            "race_type": self.race_type,
            "latest_price": float(self.latest_price) if self.latest_price else 0,
            "change_percent": float(self.change_percent) if self.change_percent else 0,
            "prev_close": float(self.prev_close) if self.prev_close else 0,
            "open_price": float(self.open_price) if self.open_price else 0,
            "race_amount": float(self.race_amount) if self.race_amount else 0,
            "race_amplitude": float(self.race_amplitude) if self.race_amplitude else 0,
            "race_commission": (
                float(self.race_commission) if self.race_commission else 0
            ),
            "race_transaction": (
                float(self.race_transaction) if self.race_transaction else 0
            ),
            "race_ratio": float(self.race_ratio) if self.race_ratio else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class LongHuBangData(Base):
    """龙虎榜详细数据表"""

    __tablename__ = "stock_lhb_detail"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, comment="股票代码")
    name = Column(String(100), comment="股票名称")
    trade_date = Column(Date, primary_key=True, nullable=False, comment="交易日期")
    reason = Column(String(200), comment="上榜原因")
    buy_amount = Column(DECIMAL(20, 2), comment="买入总额")
    sell_amount = Column(DECIMAL(20, 2), comment="卖出总额")
    net_amount = Column(DECIMAL(20, 2), comment="净买入额")
    turnover_rate = Column(DECIMAL(10, 4), comment="换手率")
    institution_buy = Column(DECIMAL(20, 2), comment="机构买入额")
    institution_sell = Column(DECIMAL(20, 2), comment="机构卖出额")
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="创建时间")

    __table_args__ = (
        Index("idx_stock_lhb_symbol", "symbol", "trade_date"),
        {"comment": "龙虎榜详细数据表"},
    )

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "name": self.name,
            "trade_date": self.trade_date.isoformat() if self.trade_date else None,
            "reason": self.reason,
            "buy_amount": float(self.buy_amount) if self.buy_amount else 0,
            "sell_amount": float(self.sell_amount) if self.sell_amount else 0,
            "net_amount": float(self.net_amount) if self.net_amount else 0,
            "turnover_rate": float(self.turnover_rate) if self.turnover_rate else 0,
            "institution_buy": (
                float(self.institution_buy) if self.institution_buy else 0
            ),
            "institution_sell": (
                float(self.institution_sell) if self.institution_sell else 0
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class SectorFundFlow(Base):
    """行业/概念资金流向表"""

    __tablename__ = "sector_fund_flow"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sector_code = Column(String(50), nullable=False, comment="板块代码")
    sector_name = Column(String(100), nullable=False, comment="板块名称")
    sector_type = Column(String(20), nullable=False, comment="板块类型(行业/概念/地域)")
    trade_date = Column(Date, primary_key=True, nullable=False, comment="交易日期")
    timeframe = Column(
        String(10), nullable=False, comment="时间维度(今日/3日/5日/10日)"
    )
    latest_price = Column(DECIMAL(10, 3), comment="最新指数")
    change_percent = Column(DECIMAL(10, 4), comment="涨跌幅")
    main_net_inflow = Column(DECIMAL(20, 2), comment="主力净流入额")
    main_net_inflow_rate = Column(DECIMAL(10, 4), comment="主力净流入占比")
    super_large_net_inflow = Column(DECIMAL(20, 2), comment="超大单净流入额")
    super_large_net_inflow_rate = Column(DECIMAL(10, 4), comment="超大单净流入占比")
    large_net_inflow = Column(DECIMAL(20, 2), comment="大单净流入额")
    large_net_inflow_rate = Column(DECIMAL(10, 4), comment="大单净流入占比")
    medium_net_inflow = Column(DECIMAL(20, 2), comment="中单净流入额")
    medium_net_inflow_rate = Column(DECIMAL(10, 4), comment="中单净流入占比")
    small_net_inflow = Column(DECIMAL(20, 2), comment="小单净流入额")
    small_net_inflow_rate = Column(DECIMAL(10, 4), comment="小单净流入占比")
    leading_stock = Column(String(100), comment="领涨股")
    leading_stock_change_percent = Column(DECIMAL(10, 4), comment="领涨股涨跌幅")
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="创建时间")

    __table_args__ = (
        Index("idx_sector_fund_flow_code", "sector_code", "trade_date"),
        Index("idx_sector_fund_flow_type", "sector_type", "timeframe", "trade_date"),
        {"comment": "行业/概念资金流向表"},
    )

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "sector_code": self.sector_code,
            "sector_name": self.sector_name,
            "sector_type": self.sector_type,
            "trade_date": self.trade_date.isoformat() if self.trade_date else None,
            "timeframe": self.timeframe,
            "latest_price": float(self.latest_price) if self.latest_price else 0,
            "change_percent": float(self.change_percent) if self.change_percent else 0,
            "main_net_inflow": (
                float(self.main_net_inflow) if self.main_net_inflow else 0
            ),
            "main_net_inflow_rate": (
                float(self.main_net_inflow_rate) if self.main_net_inflow_rate else 0
            ),
            "super_large_net_inflow": (
                float(self.super_large_net_inflow) if self.super_large_net_inflow else 0
            ),
            "super_large_net_inflow_rate": (
                float(self.super_large_net_inflow_rate)
                if self.super_large_net_inflow_rate
                else 0
            ),
            "large_net_inflow": (
                float(self.large_net_inflow) if self.large_net_inflow else 0
            ),
            "large_net_inflow_rate": (
                float(self.large_net_inflow_rate) if self.large_net_inflow_rate else 0
            ),
            "medium_net_inflow": (
                float(self.medium_net_inflow) if self.medium_net_inflow else 0
            ),
            "medium_net_inflow_rate": (
                float(self.medium_net_inflow_rate) if self.medium_net_inflow_rate else 0
            ),
            "small_net_inflow": (
                float(self.small_net_inflow) if self.small_net_inflow else 0
            ),
            "small_net_inflow_rate": (
                float(self.small_net_inflow_rate) if self.small_net_inflow_rate else 0
            ),
            "leading_stock": self.leading_stock,
            "leading_stock_change_percent": (
                float(self.leading_stock_change_percent)
                if self.leading_stock_change_percent
                else 0
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class StockDividend(Base):
    """股票分红配送表"""

    __tablename__ = "stock_dividend"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, comment="股票代码")
    stock_name = Column(String(100), comment="股票名称")
    announce_date = Column(Date, comment="公告日期")
    ex_dividend_date = Column(Date, comment="除权除息日")
    record_date = Column(Date, comment="股权登记日")
    payment_date = Column(Date, comment="派息日")
    dividend_year = Column(String(10), comment="分红年度")
    plan_profile = Column(String(200), comment="分红方案说明")
    dividend_ratio = Column(DECIMAL(10, 4), comment="每股派息(元)")
    bonus_share_ratio = Column(DECIMAL(10, 4), comment="每股送股(股)")
    transfer_ratio = Column(DECIMAL(10, 4), comment="每股转增(股)")
    allotment_ratio = Column(DECIMAL(10, 4), comment="每股配股(股)")
    allotment_price = Column(DECIMAL(10, 3), comment="配股价格(元)")
    plan_progress = Column(String(50), comment="方案进度")
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="创建时间")

    __table_args__ = (
        Index("idx_stock_dividend_symbol", "symbol", "announce_date"),
        Index("idx_stock_dividend_ex_date", "ex_dividend_date"),
        {"comment": "股票分红配送表"},
    )

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "stock_name": self.stock_name,
            "announce_date": (
                self.announce_date.isoformat() if self.announce_date else None
            ),
            "ex_dividend_date": (
                self.ex_dividend_date.isoformat() if self.ex_dividend_date else None
            ),
            "record_date": self.record_date.isoformat() if self.record_date else None,
            "payment_date": (
                self.payment_date.isoformat() if self.payment_date else None
            ),
            "dividend_year": self.dividend_year,
            "plan_profile": self.plan_profile,
            "dividend_ratio": float(self.dividend_ratio) if self.dividend_ratio else 0,
            "bonus_share_ratio": (
                float(self.bonus_share_ratio) if self.bonus_share_ratio else 0
            ),
            "transfer_ratio": float(self.transfer_ratio) if self.transfer_ratio else 0,
            "allotment_ratio": (
                float(self.allotment_ratio) if self.allotment_ratio else 0
            ),
            "allotment_price": (
                float(self.allotment_price) if self.allotment_price else 0
            ),
            "plan_progress": self.plan_progress,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class StockBlockTrade(Base):
    """股票大宗交易表"""

    __tablename__ = "stock_blocktrade"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, comment="股票代码")
    stock_name = Column(String(100), comment="股票名称")
    trade_date = Column(Date, primary_key=True, nullable=False, comment="交易日期")
    deal_price = Column(DECIMAL(10, 3), comment="成交价(元)")
    close_price = Column(DECIMAL(10, 3), comment="收盘价(元)")
    premium_ratio = Column(DECIMAL(10, 4), comment="溢价率(%)")
    deal_amount = Column(DECIMAL(20, 2), comment="成交金额(元)")
    deal_volume = Column(BigInteger, comment="成交量(股)")
    turnover_rate = Column(DECIMAL(10, 4), comment="成交占比(%)")
    buyer_name = Column(String(200), comment="买方营业部")
    seller_name = Column(String(200), comment="卖方营业部")
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="创建时间")

    __table_args__ = (
        Index("idx_stock_blocktrade_symbol", "symbol", "trade_date"),
        Index("idx_stock_blocktrade_date", "trade_date"),
        {"comment": "股票大宗交易表"},
    )

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "stock_name": self.stock_name,
            "trade_date": self.trade_date.isoformat() if self.trade_date else None,
            "deal_price": float(self.deal_price) if self.deal_price else 0,
            "close_price": float(self.close_price) if self.close_price else 0,
            "premium_ratio": float(self.premium_ratio) if self.premium_ratio else 0,
            "deal_amount": float(self.deal_amount) if self.deal_amount else 0,
            "deal_volume": int(self.deal_volume) if self.deal_volume else 0,
            "turnover_rate": float(self.turnover_rate) if self.turnover_rate else 0,
            "buyer_name": self.buyer_name,
            "seller_name": self.seller_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
