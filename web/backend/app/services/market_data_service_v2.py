"""
市场数据服务 V2 (MarketDataServiceV2)
使用东方财富直接API，不依赖akshare

业务逻辑层,负责:
1. 数据获取: 调用EastMoney适配器获取外部数据
2. 数据存储: 保存到PostgreSQL+TimescaleDB
3. 数据查询: 从数据库读取历史数据
4. 数据刷新: 定时更新最新数据
"""

import asyncio
import logging
import os
import threading
from datetime import date, datetime
from typing import Any, Callable, Dict, List, Mapping, Optional

import pandas as pd
from sqlalchemy import and_, create_engine, or_
from sqlalchemy.orm import sessionmaker

from app.adapters.eastmoney_adapter import get_eastmoney_adapter
from app.models.market_data import (
    ETFData,
    FundFlow,
    LongHuBangData,
    SectorFundFlow,
    StockBlockTrade,
    StockDividend,
)
from app.services.openstock_client import OpenStockClient, OpenStockClientConfig, OpenStockFetchResult

logger = logging.getLogger(__name__)
DEFAULT_OPENSTOCK_BASE_URL = "http://localhost:8050"


class MarketDataServiceV2:
    """市场数据服务V2"""

    def __init__(self):
        """初始化数据库连接"""
        db_url = os.getenv("DATABASE_URL") or self._build_db_url()
        self.engine = create_engine(db_url, pool_pre_ping=True, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # 初始化东方财富适配器
        self.em_adapter = get_eastmoney_adapter()
        self._openstock_client_factory: Callable[[], OpenStockClient] = self._build_openstock_client

    def _build_db_url(self) -> str:
        """从环境变量构建数据库URL"""
        return (
            f"postgresql://{os.getenv('POSTGRESQL_USER')}:"
            f"{os.getenv('POSTGRESQL_PASSWORD')}@"
            f"{os.getenv('POSTGRESQL_HOST')}:"
            f"{os.getenv('POSTGRESQL_PORT')}/"
            f"{os.getenv('POSTGRESQL_DATABASE')}"
        )

    def _runtime_fallback_enabled(self) -> bool:
        return (
            os.getenv("TESTING", "false").lower() == "true"
            or os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"
        )

    def _build_openstock_client(self) -> OpenStockClient:
        base_url = (
            os.getenv("OPENSTOCK_BASE_URL")
            or os.getenv("OPENSTOCK_API_BASE_URL")
            or DEFAULT_OPENSTOCK_BASE_URL
        ).strip()
        try:
            timeout_seconds = float(os.getenv("OPENSTOCK_TIMEOUT_SECONDS", "5.0"))
        except ValueError:
            timeout_seconds = 5.0
        return OpenStockClient(
            OpenStockClientConfig(
                base_url=base_url or DEFAULT_OPENSTOCK_BASE_URL,
                timeout_seconds=timeout_seconds,
            )
        )

    def _fetch_openstock_sync(
        self,
        data_category: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> OpenStockFetchResult:
        async def fetch_once() -> OpenStockFetchResult:
            client = self._openstock_client_factory()
            try:
                return await client.fetch(data_category, params=params)
            finally:
                await client.aclose()

        return self._run_async(fetch_once)

    def _run_async(self, async_factory: Callable[[], Any]) -> Any:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(async_factory())

        result: Any = None
        error: BaseException | None = None

        def run_in_thread() -> None:
            nonlocal result, error
            try:
                result = asyncio.run(async_factory())
            except BaseException as exc:
                error = exc

        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()
        thread.join()
        if error is not None:
            raise error
        return result

    def _fetch_openstock_records(
        self,
        data_category: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> List[Mapping[str, Any]]:
        result = self._fetch_openstock_sync(data_category, params=params)
        if not isinstance(result.data, list):
            return []
        return [record for record in result.data if isinstance(record, Mapping)]

    @staticmethod
    def _record_value(record: Mapping[str, Any], *keys: str, default: Any = 0) -> Any:
        for key in keys:
            value = record.get(key)
            if value is not None:
                return value
        return default

    @staticmethod
    def _record_date(value: Any, fallback: date) -> date:
        if value is None:
            return fallback
        parsed = pd.to_datetime(value, errors="coerce")
        if pd.isna(parsed):
            return fallback
        return parsed.date()

    def _build_sector_fund_flow_runtime_rows(
        self,
        sector_type: str,
        timeframe: str,
        limit: int,
    ) -> List[Dict[str, Any]]:
        df = self.em_adapter.get_sector_fund_flow(sector_type, timeframe)

        if df.empty:
            return []

        today = datetime.now().date().isoformat()
        rows: List[Dict[str, Any]] = []

        for _, row in df.head(limit).iterrows():
            rows.append(
                {
                    "id": None,
                    "sector_code": row.get("代码"),
                    "sector_name": row.get("名称"),
                    "sector_type": sector_type,
                    "trade_date": today,
                    "timeframe": timeframe,
                    "latest_price": float(row.get("最新价", 0) or 0),
                    "change_percent": float(row.get("涨跌幅", 0) or 0),
                    "main_net_inflow": float(row.get("主力净流入", 0) or 0),
                    "main_net_inflow_rate": float(row.get("主力净流入占比", 0) or 0),
                    "super_large_net_inflow": float(row.get("超大单净流入", 0) or 0),
                    "super_large_net_inflow_rate": float(row.get("超大单净流入占比", 0) or 0),
                    "large_net_inflow": float(row.get("大单净流入", 0) or 0),
                    "large_net_inflow_rate": float(row.get("大单净流入占比", 0) or 0),
                    "medium_net_inflow": float(row.get("中单净流入", 0) or 0),
                    "medium_net_inflow_rate": float(row.get("中单净流入占比", 0) or 0),
                    "small_net_inflow": float(row.get("小单净流入", 0) or 0),
                    "small_net_inflow_rate": float(row.get("小单净流入占比", 0) or 0),
                    "leading_stock": None,
                    "leading_stock_change_percent": 0,
                    "created_at": None,
                }
            )

        return rows

    # ==================== 资金流向 (Fund Flow) ====================

    def fetch_and_save_fund_flow(self, symbol: Optional[str] = None, timeframe: str = "今日") -> Dict[str, Any]:
        """
        获取并保存资金流向数据

        Args:
            symbol: 股票代码(可选，不传则保存全市场)
            timeframe: 时间维度 (今日/3日/5日/10日)

        Returns:
            保存结果字典
        """
        try:
            if symbol and timeframe in {"今日", "1"}:
                return self._fetch_and_save_openstock_fund_flow(symbol)

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
                        main_net_inflow_rate=row.get(f"{timeframe}主力净流入-净占比", 0),
                        super_large_net_inflow=row.get(f"{timeframe}超大单净流入-净额", 0),
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
                logger.info("保存资金流向数据成功: %(saved_count)s条")

                return {
                    "success": True,
                    "message": f"保存成功: {saved_count}条",
                    "saved": saved_count,
                }

            finally:
                db.close()

        except Exception as e:
            logger.error("获取资金流向失败: %(e)s")
            return {"success": False, "message": str(e)}

    def _fetch_and_save_openstock_fund_flow(self, symbol: str) -> Dict[str, Any]:
        records = self._fetch_openstock_records("FUND_FLOW", params={"symbol": symbol})

        if not records:
            return {"success": False, "message": "未获取到数据"}

        db = self.SessionLocal()
        try:
            today = datetime.now().date()
            saved_count = 0

            for row in records:
                trade_date = self._record_date(self._record_value(row, "trade_date", default=None), today)
                fund_flow = FundFlow(
                    symbol=self._record_value(row, "symbol", default=symbol),
                    trade_date=trade_date,
                    timeframe="1",
                    main_net_inflow=self._record_value(row, "main_net_inflow"),
                    main_net_inflow_rate=self._record_value(row, "main_net_inflow_ratio"),
                    super_large_net_inflow=self._record_value(row, "super_large_net_inflow"),
                    large_net_inflow=self._record_value(row, "large_net_inflow"),
                    medium_net_inflow=self._record_value(row, "medium_net_inflow"),
                    small_net_inflow=self._record_value(row, "small_net_inflow"),
                )

                existing = (
                    db.query(FundFlow)
                    .filter(
                        and_(
                            FundFlow.symbol == fund_flow.symbol,
                            FundFlow.trade_date == fund_flow.trade_date,
                            FundFlow.timeframe == fund_flow.timeframe,
                        )
                    )
                    .first()
                )

                if not existing:
                    db.add(fund_flow)
                    saved_count += 1

            db.commit()
            logger.info("保存资金流向数据成功: %(saved_count)s条")
            return {
                "success": True,
                "message": f"保存成功: {saved_count}条",
                "saved": saved_count,
            }
        finally:
            db.close()

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
            query = db.query(FundFlow).filter(and_(FundFlow.symbol == symbol, FundFlow.timeframe == timeframe))

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
            # 1. 从OpenStock获取全市场ETF数据
            records = self._fetch_openstock_records("ETF_SPOT", params={"limit": 500})

            if not records:
                return {"success": False, "message": "未获取到ETF数据"}

            # 2. 批量保存到数据库
            db = self.SessionLocal()
            try:
                today = datetime.now().date()
                saved_count = 0

                for row in records:
                    symbol = self._record_value(row, "symbol", default=None)
                    if not symbol:
                        continue
                    etf_data = ETFData(
                        symbol=symbol,
                        name=self._record_value(row, "name", default=""),
                        trade_date=self._record_date(self._record_value(row, "trade_date", default=None), today),
                        latest_price=self._record_value(row, "latest_price", "price"),
                        change_percent=self._record_value(row, "change_percent", "pct_chg"),
                        change_amount=self._record_value(row, "change_amount", "change"),
                        volume=self._record_value(row, "volume"),
                        amount=self._record_value(row, "amount"),
                        open_price=self._record_value(row, "open_price", "open"),
                        high_price=self._record_value(row, "high_price", "high"),
                        low_price=self._record_value(row, "low_price", "low"),
                        prev_close=self._record_value(row, "prev_close"),
                        turnover_rate=self._record_value(row, "turnover_rate"),
                        total_market_cap=self._record_value(row, "total_market_cap", "market_cap"),
                        circulating_market_cap=self._record_value(
                            row,
                            "circulating_market_cap",
                            "float_market_cap",
                        ),
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
                logger.info("保存ETF数据成功: %(saved_count)s条")

                return {
                    "success": True,
                    "message": f"保存成功: {saved_count}条",
                    "total": len(records),
                    "saved": saved_count,
                }

            finally:
                db.close()

        except Exception as e:
            logger.error("获取ETF数据失败: %(e)s")
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
            records = self._fetch_openstock_records("DRAGON_TIGER", params={"trade_date": trade_date})

            if not records:
                return {"success": False, "message": f"{trade_date}无龙虎榜数据"}

            # 2. 批量保存
            db = self.SessionLocal()
            try:
                saved_count = 0
                date_obj = datetime.strptime(trade_date, "%Y-%m-%d").date()

                for record in records:
                    lhb_data = LongHuBangData(
                        symbol=record["symbol"],
                        name=self._record_value(record, "name", default=""),
                        trade_date=date_obj,
                        reason=self._record_value(record, "reason", "interpretation", default=None),
                        buy_amount=self._record_value(record, "buy_amount"),
                        sell_amount=self._record_value(record, "sell_amount"),
                        net_amount=self._record_value(record, "net_amount"),
                        turnover_rate=self._record_value(record, "turnover_rate", "turnover"),
                        institution_buy=self._record_value(record, "institution_buy", default=None),
                        institution_sell=self._record_value(record, "institution_sell", default=None),
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
                logger.info("保存龙虎榜数据成功: %(saved_count)s条")

                return {"success": True, "message": f"保存成功: {saved_count}条"}

            finally:
                db.close()

        except Exception as e:
            logger.error("获取龙虎榜数据失败: %(e)s")
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

            results = query.order_by(LongHuBangData.trade_date.desc()).limit(limit).all()
            return [r.to_dict() for r in results]

        finally:
            db.close()

    # ==================== 行业/概念资金流向 ====================

    def fetch_and_save_sector_fund_flow(self, sector_type: str = "行业", timeframe: str = "今日") -> Dict[str, Any]:
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
                logger.info("保存%(sector_type)s资金流向成功: %(saved_count)s条")

                return {"success": True, "message": f"保存成功: {saved_count}条"}

            finally:
                db.close()

        except Exception as e:
            logger.error("获取板块资金流向失败: %(e)s")
            return {"success": False, "message": str(e)}

    def query_sector_fund_flow(
        self, sector_type: str = "行业", timeframe: str = "今日", limit: int = 100
    ) -> List[Dict]:
        """查询行业/概念资金流向"""
        try:
            db = self.SessionLocal()
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
                if self._runtime_fallback_enabled():
                    return self._build_sector_fund_flow_runtime_rows(sector_type, timeframe, limit)
                return []

            query = db.query(SectorFundFlow).filter(
                and_(
                    SectorFundFlow.sector_type == sector_type,
                    SectorFundFlow.timeframe == timeframe,
                    SectorFundFlow.trade_date == latest_date,
                )
            )

            results = query.order_by(SectorFundFlow.main_net_inflow.desc()).limit(limit).all()
            return [r.to_dict() for r in results]

        except Exception as e:
            if self._runtime_fallback_enabled():
                logger.warning("查询板块资金流向降级到 runtime fallback: %s", str(e))
                return self._build_sector_fund_flow_runtime_rows(sector_type, timeframe, limit)
            raise
        finally:
            if "db" in locals():
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
                            pd.to_datetime(row.get("公告日期")).date() if pd.notna(row.get("公告日期")) else None
                        ),
                        ex_dividend_date=(
                            pd.to_datetime(row.get("除权除息日")).date() if pd.notna(row.get("除权除息日")) else None
                        ),
                        record_date=(
                            pd.to_datetime(row.get("股权登记日")).date() if pd.notna(row.get("股权登记日")) else None
                        ),
                        payment_date=(
                            pd.to_datetime(row.get("派息日")).date() if pd.notna(row.get("派息日")) else None
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
                logger.info("保存分红配送数据成功: %(saved_count)s条")

                return {"success": True, "message": f"保存成功: {saved_count}条"}

            finally:
                db.close()

        except Exception as e:
            logger.error("获取分红配送数据失败: %(e)s")
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

    def fetch_and_save_blocktrade(self, trade_date: Optional[str] = None) -> Dict[str, Any]:
        """获取并保存大宗交易数据"""
        try:
            effective_trade_date = trade_date or date.today().isoformat()
            fallback_trade_date = self._record_date(effective_trade_date, date.today())
            records = self._fetch_openstock_records("BLOCK_TRADE", params={"trade_date": effective_trade_date})

            if not records:
                return {"success": False, "message": "未获取到大宗交易数据"}

            # 2. 批量保存
            db = self.SessionLocal()
            try:
                saved_count = 0

                for record in records:
                    blocktrade = StockBlockTrade(
                        symbol=record["symbol"],
                        stock_name=self._record_value(record, "stock_name", "name", default=""),
                        trade_date=self._record_date(record.get("trade_date"), fallback_trade_date),
                        deal_price=self._record_value(record, "deal_price"),
                        close_price=self._record_value(record, "close_price", "close"),
                        premium_ratio=self._record_value(record, "premium_ratio"),
                        deal_amount=self._record_value(record, "deal_amount", "amount"),
                        deal_volume=self._record_value(record, "deal_volume", "volume"),
                        turnover_rate=self._record_value(
                            record,
                            "turnover_rate",
                            "amount_float_market_cap_ratio",
                        ),
                        buyer_name=self._record_value(record, "buyer_name", default=None),
                        seller_name=self._record_value(record, "seller_name", default=None),
                    )

                    db.add(blocktrade)
                    saved_count += 1

                db.commit()
                logger.info("保存大宗交易数据成功: %(saved_count)s条")

                return {"success": True, "message": f"保存成功: {saved_count}条"}

            finally:
                db.close()

        except Exception as e:
            logger.error("获取大宗交易数据失败: %(e)s")
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

            results = query.order_by(StockBlockTrade.trade_date.desc()).limit(limit).all()
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
