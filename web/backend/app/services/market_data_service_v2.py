"""
市场数据服务 V2 (MarketDataServiceV2)
使用东方财富直接API，不依赖akshare

业务逻辑层,负责:
1. 数据获取: 调用EastMoney适配器获取外部数据
2. 数据存储: 保存到PostgreSQL+TimescaleDB
3. 数据查询: 从数据库读取历史数据
4. 数据刷新: 定时更新最新数据
"""

from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
import pandas as pd
import logging
import os

from app.models.market_data import (
    FundFlow,
    ETFData,
    ChipRaceData,
    LongHuBangData,
    SectorFundFlow,
    StockDividend,
    StockBlockTrade,
)
from app.adapters.eastmoney_adapter import get_eastmoney_adapter

logger = logging.getLogger(__name__)


class MarketDataServiceV2:
    """市场数据服务V2"""

    def __init__(self):
        """初始化数据库连接"""
        db_url = os.getenv("DATABASE_URL") or self._build_db_url()
        self.engine = create_engine(db_url, pool_pre_ping=True, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # 初始化东方财富适配器
        self.em_adapter = get_eastmoney_adapter()

    def _build_db_url(self) -> str:
        """从环境变量构建数据库URL"""
        return (
            f"postgresql://{os.getenv('POSTGRESQL_USER')}:"
            f"{os.getenv('POSTGRESQL_PASSWORD')}@"
            f"{os.getenv('POSTGRESQL_HOST')}:"
            f"{os.getenv('POSTGRESQL_PORT')}/"
            f"{os.getenv('POSTGRESQL_DATABASE')}"
        )

    # ==================== 资金流向 (Fund Flow) ====================

    def fetch_and_save_fund_flow(
        self, symbol: Optional[str] = None, timeframe: str = "今日"
    ) -> Dict[str, Any]:
        """
        获取并保存资金流向数据

        Args:
            symbol: 股票代码(可选，不传则保存全市场)
            timeframe: 时间维度 (今日/3日/5日/10日)

        Returns:
            保存结果字典
        """
        try:
            # 1. 从东方财富获取数据
            df = self.em_adapter.get_stock_fund_flow(symbol, timeframe)

            if df.empty:
                return {"success": False, "message": "未获取到数据"}

            # 2. 批量保存到数据库
            db = self.SessionLocal()
            try:
                today = datetime.now().date()
                saved_count = 0

                # 时间维度映射
                timeframe_map = {"今日": "1", "3日": "3", "5日": "5", "10日": "10"}
                tf_value = timeframe_map.get(timeframe, "1")

                for _, row in df.iterrows():
                    fund_flow = FundFlow(
                        symbol=row["代码"],
                        trade_date=today,
                        timeframe=tf_value,
                        main_net_inflow=row.get(f"{timeframe}主力净流入-净额", 0),
                        main_net_inflow_rate=row.get(
                            f"{timeframe}主力净流入-净占比", 0
                        ),
                        super_large_net_inflow=row.get(
                            f"{timeframe}超大单净流入-净额", 0
                        ),
                        large_net_inflow=row.get(f"{timeframe}大单净流入-净额", 0),
                        medium_net_inflow=row.get(f"{timeframe}中单净流入-净额", 0),
                        small_net_inflow=row.get(f"{timeframe}小单净流入-净额", 0),
                    )

                    # 检查是否已存在
                    existing = (
                        db.query(FundFlow)
                        .filter(
                            and_(
                                FundFlow.symbol == fund_flow.symbol,
                                FundFlow.trade_date == today,
                                FundFlow.timeframe == tf_value,
                            )
                        )
                        .first()
                    )

                    if not existing:
                        db.add(fund_flow)
                        saved_count += 1

                db.commit()
                logger.info(f"保存资金流向数据成功: {saved_count}条")

                return {
                    "success": True,
                    "message": f"保存成功: {saved_count}条",
                    "saved": saved_count,
                }

            finally:
                db.close()

        except Exception as e:
            logger.error(f"获取资金流向失败: {e}")
            return {"success": False, "message": str(e)}

    def query_fund_flow(
        self,
        symbol: str,
        timeframe: str = "1",
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict]:
        """查询资金流向历史数据"""
        db = self.SessionLocal()
        try:
            query = db.query(FundFlow).filter(
                and_(FundFlow.symbol == symbol, FundFlow.timeframe == timeframe)
            )

            if start_date:
                query = query.filter(FundFlow.trade_date >= start_date)
            if end_date:
                query = query.filter(FundFlow.trade_date <= end_date)

            results = query.order_by(FundFlow.trade_date.desc()).all()
            return [r.to_dict() for r in results]

        finally:
            db.close()

    # ==================== ETF数据 (ETF Spot) ====================

    def fetch_and_save_etf_spot(self) -> Dict[str, Any]:
        """获取并保存ETF实时数据(全市场)"""
        try:
            # 1. 从东方财富获取全市场ETF数据
            df = self.em_adapter.get_etf_spot()

            if df.empty:
                return {"success": False, "message": "未获取到ETF数据"}

            # 2. 批量保存到数据库
            db = self.SessionLocal()
            try:
                today = datetime.now().date()
                saved_count = 0

                for _, row in df.iterrows():
                    etf_data = ETFData(
                        symbol=row["代码"],
                        name=row["名称"],
                        trade_date=today,
                        latest_price=row.get("最新价", 0),
                        change_percent=row.get("涨跌幅", 0),
                        change_amount=row.get("涨跌额", 0),
                        volume=row.get("成交量", 0),
                        amount=row.get("成交额", 0),
                        open_price=row.get("开盘价", 0),
                        high_price=row.get("最高价", 0),
                        low_price=row.get("最低价", 0),
                        prev_close=row.get("昨收", 0),
                        turnover_rate=row.get("换手率", 0),
                        total_market_cap=row.get("总市值", 0),
                        circulating_market_cap=row.get("流通市值", 0),
                    )

                    # 检查是否已存在
                    existing = (
                        db.query(ETFData)
                        .filter(
                            and_(
                                ETFData.symbol == etf_data.symbol,
                                ETFData.trade_date == today,
                            )
                        )
                        .first()
                    )

                    if not existing:
                        db.add(etf_data)
                        saved_count += 1

                db.commit()
                logger.info(f"保存ETF数据成功: {saved_count}条")

                return {
                    "success": True,
                    "message": f"保存成功: {saved_count}条",
                    "total": len(df),
                    "saved": saved_count,
                }

            finally:
                db.close()

        except Exception as e:
            logger.error(f"获取ETF数据失败: {e}")
            return {"success": False, "message": str(e)}

    def query_etf_spot(
        self,
        symbol: Optional[str] = None,
        keyword: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict]:
        """查询ETF数据（查询最新可用数据）"""
        db = self.SessionLocal()
        try:
            # 先找到最新的交易日期
            from sqlalchemy import func

            latest_date_query = db.query(func.max(ETFData.trade_date)).scalar()

            if not latest_date_query:
                return []

            # 查询最新日期的数据
            query = db.query(ETFData).filter(ETFData.trade_date == latest_date_query)

            if symbol:
                query = query.filter(ETFData.symbol == symbol)

            if keyword:
                query = query.filter(
                    or_(
                        ETFData.symbol.like(f"%{keyword}%"),
                        ETFData.name.like(f"%{keyword}%"),
                    )
                )

            results = query.order_by(ETFData.change_percent.desc()).limit(limit).all()
            return [r.to_dict() for r in results]

        finally:
            db.close()

    # ==================== 龙虎榜 (Long Hu Bang) ====================

    def fetch_and_save_lhb_detail(self, trade_date: str) -> Dict[str, Any]:
        """获取并保存龙虎榜数据"""
        try:
            # 1. 从东方财富获取数据
            df = self.em_adapter.get_stock_lhb_detail(trade_date)

            if df.empty:
                return {"success": False, "message": f"{trade_date}无龙虎榜数据"}

            # 2. 批量保存
            db = self.SessionLocal()
            try:
                saved_count = 0
                date_obj = datetime.strptime(trade_date, "%Y-%m-%d").date()

                for _, row in df.iterrows():
                    lhb_data = LongHuBangData(
                        symbol=row["代码"],
                        name=row["名称"],
                        trade_date=date_obj,
                        reason=row.get("解读"),
                        buy_amount=row.get("龙虎榜买入额", 0),
                        sell_amount=row.get("龙虎榜卖出额", 0),
                        net_amount=row.get("龙虎榜净买额", 0),
                        turnover_rate=row.get("换手率", 0),
                        institution_buy=row.get("机构买入额"),
                        institution_sell=row.get("机构卖出额"),
                    )

                    existing = (
                        db.query(LongHuBangData)
                        .filter(
                            and_(
                                LongHuBangData.symbol == lhb_data.symbol,
                                LongHuBangData.trade_date == date_obj,
                            )
                        )
                        .first()
                    )

                    if not existing:
                        db.add(lhb_data)
                        saved_count += 1

                db.commit()
                logger.info(f"保存龙虎榜数据成功: {saved_count}条")

                return {"success": True, "message": f"保存成功: {saved_count}条"}

            finally:
                db.close()

        except Exception as e:
            logger.error(f"获取龙虎榜数据失败: {e}")
            return {"success": False, "message": str(e)}

    def query_lhb_detail(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        min_net_amount: Optional[float] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """查询龙虎榜数据"""
        db = self.SessionLocal()
        try:
            query = db.query(LongHuBangData)

            if symbol:
                query = query.filter(LongHuBangData.symbol == symbol)

            if start_date:
                query = query.filter(LongHuBangData.trade_date >= start_date)

            if end_date:
                query = query.filter(LongHuBangData.trade_date <= end_date)

            if min_net_amount:
                query = query.filter(LongHuBangData.net_amount >= min_net_amount)

            results = (
                query.order_by(LongHuBangData.trade_date.desc()).limit(limit).all()
            )
            return [r.to_dict() for r in results]

        finally:
            db.close()

    # ==================== 行业/概念资金流向 ====================

    def fetch_and_save_sector_fund_flow(
        self, sector_type: str = "行业", timeframe: str = "今日"
    ) -> Dict[str, Any]:
        """获取并保存行业/概念资金流向"""
        try:
            # 1. 从东方财富获取数据
            df = self.em_adapter.get_sector_fund_flow(sector_type, timeframe)

            if df.empty:
                return {"success": False, "message": "未获取到板块资金流向数据"}

            # 2. 批量保存
            db = self.SessionLocal()
            try:
                today = datetime.now().date()
                saved_count = 0

                for _, row in df.iterrows():
                    sector_flow = SectorFundFlow(
                        sector_code=row["代码"],
                        sector_name=row["名称"],
                        sector_type=sector_type,
                        trade_date=today,
                        timeframe=timeframe,
                        latest_price=row.get("最新价", 0),
                        change_percent=row.get("涨跌幅", 0),
                        main_net_inflow=row.get("主力净流入", 0),
                        main_net_inflow_rate=row.get("主力净流入占比", 0),
                        super_large_net_inflow=row.get("超大单净流入", 0),
                        super_large_net_inflow_rate=row.get("超大单净流入占比", 0),
                        large_net_inflow=row.get("大单净流入", 0),
                        large_net_inflow_rate=row.get("大单净流入占比", 0),
                        medium_net_inflow=row.get("中单净流入", 0),
                        medium_net_inflow_rate=row.get("中单净流入占比", 0),
                        small_net_inflow=row.get("小单净流入", 0),
                        small_net_inflow_rate=row.get("小单净流入占比", 0),
                        leading_stock=None,
                        leading_stock_change_percent=None,
                    )

                    existing = (
                        db.query(SectorFundFlow)
                        .filter(
                            and_(
                                SectorFundFlow.sector_code == sector_flow.sector_code,
                                SectorFundFlow.trade_date == today,
                                SectorFundFlow.timeframe == timeframe,
                            )
                        )
                        .first()
                    )

                    if not existing:
                        db.add(sector_flow)
                        saved_count += 1

                db.commit()
                logger.info(f"保存{sector_type}资金流向成功: {saved_count}条")

                return {"success": True, "message": f"保存成功: {saved_count}条"}

            finally:
                db.close()

        except Exception as e:
            logger.error(f"获取板块资金流向失败: {e}")
            return {"success": False, "message": str(e)}

    def query_sector_fund_flow(
        self, sector_type: str = "行业", timeframe: str = "今日", limit: int = 100
    ) -> List[Dict]:
        """查询行业/概念资金流向"""
        db = self.SessionLocal()
        try:
            # 查询最新日期的数据
            from sqlalchemy import func

            latest_date = (
                db.query(func.max(SectorFundFlow.trade_date))
                .filter(
                    and_(
                        SectorFundFlow.sector_type == sector_type,
                        SectorFundFlow.timeframe == timeframe,
                    )
                )
                .scalar()
            )

            if not latest_date:
                return []

            query = db.query(SectorFundFlow).filter(
                and_(
                    SectorFundFlow.sector_type == sector_type,
                    SectorFundFlow.timeframe == timeframe,
                    SectorFundFlow.trade_date == latest_date,
                )
            )

            results = (
                query.order_by(SectorFundFlow.main_net_inflow.desc()).limit(limit).all()
            )
            return [r.to_dict() for r in results]

        finally:
            db.close()

    # ==================== 股票分红配送 ====================

    def fetch_and_save_stock_dividend(self, symbol: str) -> Dict[str, Any]:
        """获取并保存股票分红配送数据"""
        try:
            # 1. 从东方财富获取数据
            df = self.em_adapter.get_stock_dividend(symbol)

            if df.empty:
                return {"success": False, "message": f"{symbol}无分红配送数据"}

            # 2. 批量保存
            db = self.SessionLocal()
            try:
                saved_count = 0

                for _, row in df.iterrows():
                    dividend = StockDividend(
                        symbol=symbol,
                        stock_name=row.get("股票名称"),
                        announce_date=(
                            pd.to_datetime(row.get("公告日期")).date()
                            if pd.notna(row.get("公告日期"))
                            else None
                        ),
                        ex_dividend_date=(
                            pd.to_datetime(row.get("除权除息日")).date()
                            if pd.notna(row.get("除权除息日"))
                            else None
                        ),
                        record_date=(
                            pd.to_datetime(row.get("股权登记日")).date()
                            if pd.notna(row.get("股权登记日"))
                            else None
                        ),
                        payment_date=(
                            pd.to_datetime(row.get("派息日")).date()
                            if pd.notna(row.get("派息日"))
                            else None
                        ),
                        dividend_year=row.get("分红年度"),
                        plan_profile=row.get("分红方案"),
                        dividend_ratio=row.get("每股派息", 0),
                        bonus_share_ratio=row.get("每股送股", 0),
                        transfer_ratio=row.get("每股转增", 0),
                        plan_progress=row.get("方案进度"),
                    )

                    db.add(dividend)
                    saved_count += 1

                db.commit()
                logger.info(f"保存分红配送数据成功: {saved_count}条")

                return {"success": True, "message": f"保存成功: {saved_count}条"}

            finally:
                db.close()

        except Exception as e:
            logger.error(f"获取分红配送数据失败: {e}")
            return {"success": False, "message": str(e)}

    def query_stock_dividend(self, symbol: str, limit: int = 50) -> List[Dict]:
        """查询股票分红配送数据"""
        db = self.SessionLocal()
        try:
            results = (
                db.query(StockDividend)
                .filter(StockDividend.symbol == symbol)
                .order_by(StockDividend.announce_date.desc())
                .limit(limit)
                .all()
            )

            return [r.to_dict() for r in results]

        finally:
            db.close()

    # ==================== 股票大宗交易 ====================

    def fetch_and_save_blocktrade(
        self, trade_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取并保存大宗交易数据"""
        try:
            # 1. 从东方财富获取数据
            df = self.em_adapter.get_stock_blocktrade(trade_date)

            if df.empty:
                return {"success": False, "message": "未获取到大宗交易数据"}

            # 2. 批量保存
            db = self.SessionLocal()
            try:
                saved_count = 0

                for _, row in df.iterrows():
                    blocktrade = StockBlockTrade(
                        symbol=row["股票代码"],
                        stock_name=row["股票名称"],
                        trade_date=pd.to_datetime(row["交易日期"]).date(),
                        deal_price=row.get("成交价", 0),
                        close_price=row.get("收盘价", 0),
                        premium_ratio=row.get("溢价率", 0),
                        deal_amount=row.get("成交金额", 0),
                        deal_volume=row.get("成交量", 0),
                        turnover_rate=row.get("成交占比", 0),
                        buyer_name=row.get("买方营业部"),
                        seller_name=row.get("卖方营业部"),
                    )

                    db.add(blocktrade)
                    saved_count += 1

                db.commit()
                logger.info(f"保存大宗交易数据成功: {saved_count}条")

                return {"success": True, "message": f"保存成功: {saved_count}条"}

            finally:
                db.close()

        except Exception as e:
            logger.error(f"获取大宗交易数据失败: {e}")
            return {"success": False, "message": str(e)}

    def query_blocktrade(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """查询大宗交易数据"""
        db = self.SessionLocal()
        try:
            query = db.query(StockBlockTrade)

            if symbol:
                query = query.filter(StockBlockTrade.symbol == symbol)

            if start_date:
                query = query.filter(StockBlockTrade.trade_date >= start_date)

            if end_date:
                query = query.filter(StockBlockTrade.trade_date <= end_date)

            results = (
                query.order_by(StockBlockTrade.trade_date.desc()).limit(limit).all()
            )
            return [r.to_dict() for r in results]

        finally:
            db.close()


# 全局单例
_market_data_service_v2 = None


def get_market_data_service_v2() -> MarketDataServiceV2:
    """获取市场数据服务V2单例"""
    global _market_data_service_v2
    if _market_data_service_v2 is None:
        _market_data_service_v2 = MarketDataServiceV2()
    return _market_data_service_v2
