"""
市场数据服务 (MarketDataService)

业务逻辑层,负责:
1. 数据获取: 调用adapters获取外部数据
2. 数据存储: 保存到PostgreSQL+TimescaleDB
3. 数据查询: 从数据库读取历史数据
4. 数据刷新: 定时更新最新数据

复用组件:
- akshare_extension: ETF/资金流向/龙虎榜数据
- tqlex_adapter: 竞价抢筹数据
"""

from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime
from typing import List, Optional, Dict, Any
import pandas as pd
import logging
import os

from app.models.market_data import FundFlow, ETFData, ChipRaceOpenData, ChipRaceEndData, LongHuBangData
from app.adapters.akshare_extension import get_akshare_extension
from app.adapters.tqlex_adapter import get_tqlex_adapter
from app.core.cache_integration import get_cache_integration

logger = logging.getLogger(__name__)


class MarketDataService:
    """市场数据服务"""

    def __init__(self, use_cache: bool = True):
        """
        初始化数据库连接

        Args:
            use_cache: 是否启用缓存 (默认True)
        """
        db_url = os.getenv("DATABASE_URL") or self._build_db_url()
        self.engine = create_engine(db_url, pool_pre_ping=True, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # 初始化adapters
        self.akshare_ext = get_akshare_extension()

        # TQLEX适配器可能未配置token,需要优雅降级
        try:
            self.tqlex = get_tqlex_adapter()
        except ValueError as e:
            logger.warning(f"TQLEX适配器初始化失败(竞价抢筹功能将不可用): {e}")
            self.tqlex = None

        # 初始化缓存集成
        self.cache = get_cache_integration()
        self.use_cache = use_cache
        logger.info(f"市场数据服务初始化完成 (缓存: {'启用' if use_cache else '禁用'})")

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

    def fetch_and_save_fund_flow_cached(self, symbol: str, timeframe: str = "1") -> Dict[str, Any]:
        """
        获取并保存资金流向数据 (带缓存支持)

        先检查缓存，如果缓存有效则返回缓存数据；
        否则从Akshare获取数据，保存到数据库和缓存。

        Args:
            symbol: 股票代码
            timeframe: 时间维度 (1/3/5/10天)

        Returns:
            保存结果字典，包含缓存来源信息
        """

        def fetch_from_source():
            """从源获取并保存资金流向数据"""
            data = self.akshare_ext.get_stock_fund_flow(symbol, timeframe)
            if not data:
                return None

            db = self.SessionLocal()
            try:
                fund_flow = FundFlow(
                    symbol=symbol,
                    trade_date=datetime.now().date(),
                    timeframe=timeframe,
                    main_net_inflow=data.get("main_net_inflow", 0),
                    main_net_inflow_rate=data.get("main_net_inflow_rate", 0),
                    super_large_net_inflow=data.get("super_large_net_inflow", 0),
                    large_net_inflow=data.get("large_net_inflow", 0),
                    medium_net_inflow=data.get("medium_net_inflow", 0),
                    small_net_inflow=data.get("small_net_inflow", 0),
                )

                existing = (
                    db.query(FundFlow)
                    .filter(
                        and_(
                            FundFlow.symbol == symbol,
                            FundFlow.trade_date == fund_flow.trade_date,
                            FundFlow.timeframe == timeframe,
                        )
                    )
                    .first()
                )

                if existing:
                    for key, value in data.items():
                        setattr(existing, key, value)
                    db.commit()
                    logger.info(f"更新资金流向: {symbol} - {timeframe}天")
                else:
                    db.add(fund_flow)
                    db.commit()
                    logger.info(f"新增资金流向: {symbol} - {timeframe}天")

                return data

            finally:
                db.close()

        try:
            # 使用缓存读取模式
            result = self.cache.fetch_with_cache(
                symbol=symbol,
                data_type="fund_flow",
                fetch_fn=fetch_from_source,
                timeframe=timeframe,
                use_cache=self.use_cache,
                ttl_days=1,  # 资金流向数据每天更新
            )

            return {
                "success": True,
                "message": f"获取资金流向成功 (来源: {result.get('source', 'unknown')})",
                "data": result.get("data"),
                "source": result.get("source"),
                "timestamp": result.get("timestamp"),
            }

        except Exception as e:
            logger.error(f"获取资金流向失败: {e}")
            return {"success": False, "message": str(e)}

    def fetch_and_save_fund_flow(self, symbol: str, timeframe: str = "1") -> Dict[str, Any]:
        """
        获取并保存资金流向数据

        Args:
            symbol: 股票代码
            timeframe: 时间维度 (1/3/5/10天)

        Returns:
            保存结果字典
        """
        try:
            # 1. 从Akshare获取数据
            data = self.akshare_ext.get_stock_fund_flow(symbol, timeframe)

            if not data:
                return {"success": False, "message": "未获取到数据"}

            # 2. 保存到数据库
            db = self.SessionLocal()
            try:
                fund_flow = FundFlow(
                    symbol=symbol,
                    trade_date=datetime.now().date(),
                    timeframe=timeframe,
                    main_net_inflow=data.get("main_net_inflow", 0),
                    main_net_inflow_rate=data.get("main_net_inflow_rate", 0),
                    super_large_net_inflow=data.get("super_large_net_inflow", 0),
                    large_net_inflow=data.get("large_net_inflow", 0),
                    medium_net_inflow=data.get("medium_net_inflow", 0),
                    small_net_inflow=data.get("small_net_inflow", 0),
                )

                # 使用upsert策略(如果存在则更新)
                existing = (
                    db.query(FundFlow)
                    .filter(
                        and_(
                            FundFlow.symbol == symbol,
                            FundFlow.trade_date == fund_flow.trade_date,
                            FundFlow.timeframe == timeframe,
                        )
                    )
                    .first()
                )

                if existing:
                    for key, value in data.items():
                        setattr(existing, key, value)
                    db.commit()
                    logger.info(f"更新资金流向: {symbol} - {timeframe}天")
                else:
                    db.add(fund_flow)
                    db.commit()
                    logger.info(f"新增资金流向: {symbol} - {timeframe}天")

                return {
                    "success": True,
                    "message": "保存成功",
                    "data": fund_flow.to_dict(),
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
    ) -> List[FundFlow]:
        """
        查询资金流向历史数据

        Args:
            symbol: 股票代码
            timeframe: 时间维度
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            FundFlow对象列表
        """
        db = self.SessionLocal()
        try:
            query = db.query(FundFlow).filter(and_(FundFlow.symbol == symbol, FundFlow.timeframe == timeframe))

            if start_date:
                query = query.filter(FundFlow.trade_date >= start_date)
            if end_date:
                query = query.filter(FundFlow.trade_date <= end_date)

            return query.order_by(FundFlow.trade_date.desc()).all()

        finally:
            db.close()

    # ==================== ETF数据 (ETF Spot) ====================

    def fetch_and_save_etf_spot_cached(self) -> Dict[str, Any]:
        """
        获取并保存ETF实时数据(全市场) - 带缓存支持

        先检查缓存，如果缓存有效则返回缓存数据；
        否则从Akshare获取全市场数据，保存到数据库和缓存。

        Returns:
            保存结果字典，包含缓存来源信息
        """

        def fetch_from_source():
            """从源获取ETF数据"""
            df = self.akshare_ext.get_etf_spot()
            if df.empty:
                return None

            # 转换为字典列表格式便于缓存
            return df.to_dict("records")

        try:
            # 使用缓存读取模式
            result = self.cache.fetch_with_cache(
                symbol="all",  # 全市场标记
                data_type="etf",
                fetch_fn=fetch_from_source,
                timeframe="1d",
                use_cache=self.use_cache,
                ttl_days=1,  # ETF数据每天更新
            )

            etf_records = result.get("data") or []

            # 保存到数据库（如果来自源）
            if result.get("source") == "source" and etf_records:
                db = self.SessionLocal()
                try:
                    today = datetime.now().date()
                    saved_count = 0

                    def safe_float(value, default=0):
                        try:
                            if pd.isna(value) or value == "" or value is None:
                                return default
                            return float(value)
                        except (ValueError, TypeError):
                            return default

                    def safe_int(value, default=0):
                        try:
                            if pd.isna(value) or value == "" or value is None:
                                return default
                            return int(float(value))
                        except (ValueError, TypeError):
                            return default

                    for row in etf_records:
                        etf_data = ETFData(
                            symbol=row.get("symbol"),
                            name=row.get("name"),
                            trade_date=today,
                            latest_price=safe_float(row.get("latest_price"), 0),
                            change_percent=safe_float(row.get("change_percent"), 0),
                            change_amount=safe_float(row.get("change_amount"), 0),
                            volume=safe_int(row.get("volume"), 0),
                            amount=safe_float(row.get("amount"), 0),
                            open_price=safe_float(row.get("open_price"), 0),
                            high_price=safe_float(row.get("high_price"), 0),
                            low_price=safe_float(row.get("low_price"), 0),
                            prev_close=safe_float(row.get("prev_close"), 0),
                            turnover_rate=safe_float(row.get("turnover_rate"), 0),
                            total_market_cap=safe_float(row.get("total_market_cap"), 0),
                            circulating_market_cap=safe_float(row.get("circulating_market_cap"), 0),
                        )

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

                finally:
                    db.close()

            return {
                "success": True,
                "message": f"获取ETF数据成功 (来源: {result.get('source', 'unknown')})",
                "total": len(etf_records),
                "source": result.get("source"),
                "timestamp": result.get("timestamp"),
            }

        except Exception as e:
            logger.error(f"获取ETF数据失败: {e}")
            return {"success": False, "message": str(e)}

    def fetch_and_save_etf_spot(self) -> Dict[str, Any]:
        """
        获取并保存ETF实时数据(全市场)

        Returns:
            保存结果字典
        """
        try:
            # 1. 从Akshare获取全市场ETF数据
            df = self.akshare_ext.get_etf_spot()

            if df.empty:
                return {"success": False, "message": "未获取到ETF数据"}

            # 2. 批量保存到数据库
            db = self.SessionLocal()
            try:
                today = datetime.now().date()
                saved_count = 0

                for _, row in df.iterrows():
                    # 处理NaN值，将其转换为0或None
                    def safe_float(value, default=0):
                        try:
                            if pd.isna(value) or value == "" or value is None:
                                return default
                            return float(value)
                        except (ValueError, TypeError):
                            return default

                    def safe_int(value, default=0):
                        try:
                            if pd.isna(value) or value == "" or value is None:
                                return default
                            return int(float(value))
                        except (ValueError, TypeError):
                            return default

                    etf_data = ETFData(
                        symbol=row["symbol"],
                        name=row["name"],
                        trade_date=today,
                        latest_price=safe_float(row.get("latest_price"), 0),
                        change_percent=safe_float(row.get("change_percent"), 0),
                        change_amount=safe_float(row.get("change_amount"), 0),
                        volume=safe_int(row.get("volume"), 0),
                        amount=safe_float(row.get("amount"), 0),
                        open_price=safe_float(row.get("open_price"), 0),
                        high_price=safe_float(row.get("high_price"), 0),
                        low_price=safe_float(row.get("low_price"), 0),
                        prev_close=safe_float(row.get("prev_close"), 0),
                        turnover_rate=safe_float(row.get("turnover_rate"), 0),
                        total_market_cap=safe_float(row.get("total_market_cap"), 0),
                        circulating_market_cap=safe_float(row.get("circulating_market_cap"), 0),
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
    ) -> List[ETFData]:
        """
        查询ETF数据（查询最新可用数据）

        Args:
            symbol: ETF代码
            keyword: 关键词搜索
            limit: 返回数量限制

        Returns:
            ETFData对象列表
        """
        db = self.SessionLocal()
        try:
            # 先找到最新的交易日期
            from sqlalchemy import func

            latest_date_query = db.query(func.max(ETFData.trade_date)).scalar()

            if not latest_date_query:
                return []  # 无数据

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

            return query.order_by(ETFData.change_percent.desc()).limit(limit).all()

        finally:
            db.close()

    # ==================== 竞价抢筹 (Chip Race) ====================

    def fetch_and_save_chip_race_cached(
        self, race_type: str = "open", trade_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取并保存竞价抢筹数据 - 带缓存支持

        参考instock实现: /opt/iflow/instock/instock/core/stockfetch.py

        Args:
            race_type: 抢筹类型 (open=早盘, end=尾盘)
            trade_date: 交易日期

        Returns:
            保存结果字典，包含缓存来源信息
        """
        if not self.tqlex:
            return {"success": False, "message": "TQLEX适配器未配置"}

        def fetch_from_source():
            """从源获取竞价抢筹数据"""
            if race_type == "open":
                df = self.tqlex.get_chip_race_open(trade_date)
            else:
                df = self.tqlex.get_chip_race_end(trade_date)

            if df.empty:
                return None

            return df.to_dict("records")

        try:
            result = self.cache.fetch_with_cache(
                symbol="chip_race",
                data_type="chip_race",
                fetch_fn=fetch_from_source,
                timeframe=f"{race_type}_{trade_date or 'latest'}",
                use_cache=self.use_cache,
                ttl_days=1,
            )

            chip_records = result.get("data") or []

            if result.get("source") == "source" and chip_records:
                db = self.SessionLocal()
                try:
                    today = datetime.now().date()
                    saved_count = 0

                    ChipRaceModel = ChipRaceOpenData if race_type == "open" else ChipRaceEndData

                    for row in chip_records:
                        chip_data = ChipRaceModel(
                            date=today,
                            code=row.get("code"),
                            name=row.get("name"),
                            new_price=row.get("new_price", 0),
                            change_rate=row.get("change_rate", 0),
                            pre_close_price=row.get("pre_close_price", 0),
                            open_price=row.get("open_price", 0),
                            deal_amount=row.get("deal_amount", 0),
                            bid_rate=row.get("bid_rate", 0),
                            bid_trust_amount=row.get("bid_trust_amount", 0),
                            bid_deal_amount=row.get("bid_deal_amount", 0),
                            bid_ratio=row.get("bid_ratio", 0),
                        )

                        existing = (
                            db.query(ChipRaceModel)
                            .filter(
                                and_(
                                    ChipRaceModel.code == chip_data.code,
                                    ChipRaceModel.date == today,
                                )
                            )
                            .first()
                        )

                        if not existing:
                            db.add(chip_data)
                            saved_count += 1

                    db.commit()
                    logger.info(f"保存{race_type}抢筹数据成功: {saved_count}条")

                finally:
                    db.close()

            return {
                "success": True,
                "message": f"获取抢筹数据成功 (来源: {result.get('source', 'unknown')})",
                "total": len(chip_records),
                "source": result.get("source"),
                "timestamp": result.get("timestamp"),
            }

        except Exception as e:
            logger.error(f"获取抢筹数据失败: {e}")
            return {"success": False, "message": str(e)}

    def fetch_and_save_chip_race(self, race_type: str = "open", trade_date: Optional[str] = None) -> Dict[str, Any]:
        """
        获取并保存竞价抢筹数据

        Args:
            race_type: 抢筹类型 (open=早盘, end=尾盘)
            trade_date: 交易日期

        Returns:
            保存结果字典
        """
        try:
            if race_type == "open":
                df = self.tqlex.get_chip_race_open(trade_date)
            else:
                df = self.tqlex.get_chip_race_end(trade_date)

            if df.empty:
                return {"success": False, "message": "未获取到抢筹数据"}

            db = self.SessionLocal()
            try:
                today = datetime.now().date()
                saved_count = 0

                ChipRaceModel = ChipRaceOpenData if race_type == "open" else ChipRaceEndData

                for _, row in df.iterrows():
                    chip_data = ChipRaceModel(
                        date=today,
                        code=row.get("code"),
                        name=row.get("name"),
                        new_price=row.get("new_price", 0),
                        change_rate=row.get("change_rate", 0),
                        pre_close_price=row.get("pre_close_price", 0),
                        open_price=row.get("open_price", 0),
                        deal_amount=row.get("deal_amount", 0),
                        bid_rate=row.get("bid_rate", 0),
                        bid_trust_amount=row.get("bid_trust_amount", 0),
                        bid_deal_amount=row.get("bid_deal_amount", 0),
                        bid_ratio=row.get("bid_ratio", 0),
                    )

                    existing = (
                        db.query(ChipRaceModel)
                        .filter(
                            and_(
                                ChipRaceModel.code == chip_data.code,
                                ChipRaceModel.date == today,
                            )
                        )
                        .first()
                    )

                    if not existing:
                        db.add(chip_data)
                        saved_count += 1

                db.commit()
                logger.info(f"保存{race_type}抢筹数据成功: {saved_count}条")

                return {"success": True, "message": f"保存成功: {saved_count}条"}

            finally:
                db.close()

        except Exception as e:
            logger.error(f"获取抢筹数据失败: {e}")
            return {"success": False, "message": str(e)}

    def query_chip_race(
        self,
        race_type: str = "open",
        trade_date: Optional[date] = None,
        min_race_amount: Optional[float] = None,
        limit: int = 100,
    ) -> List:
        """
        查询竞价抢筹数据（查询最新可用数据）

        Args:
            race_type: 抢筹类型
            trade_date: 交易日期
            min_race_amount: 最小抢筹金额
            limit: 返回数量限制

        Returns:
            ChipRaceOpenData/ChipRaceEndData对象列表
        """
        db = self.SessionLocal()
        try:
            ChipRaceModel = ChipRaceOpenData if race_type == "open" else ChipRaceEndData

            query = db.query(ChipRaceModel)

            if trade_date:
                query = query.filter(ChipRaceModel.date == trade_date)
            else:
                from sqlalchemy import func

                latest_date = db.query(func.max(ChipRaceModel.date)).scalar()
                if latest_date:
                    query = query.filter(ChipRaceModel.date == latest_date)

            if min_race_amount:
                query = query.filter(ChipRaceModel.deal_amount >= min_race_amount)

            return query.order_by(ChipRaceModel.deal_amount.desc()).limit(limit).all()

        finally:
            db.close()

    # ==================== 龙虎榜 (Long Hu Bang) ====================

    def fetch_and_save_lhb_detail(self, trade_date: str) -> Dict[str, Any]:
        """
        获取并保存龙虎榜数据

        Args:
            trade_date: 交易日期 (YYYY-MM-DD)

        Returns:
            保存结果字典
        """
        try:
            # 1. 从Akshare获取数据
            df = self.akshare_ext.get_stock_lhb_detail(trade_date)

            if df.empty:
                return {"success": False, "message": f"{trade_date}无龙虎榜数据"}

            # 2. 批量保存
            db = self.SessionLocal()
            try:
                saved_count = 0
                date_obj = datetime.strptime(trade_date, "%Y-%m-%d").date()

                for _, row in df.iterrows():
                    lhb_data = LongHuBangData(
                        symbol=row["symbol"],
                        name=row["name"],
                        trade_date=date_obj,
                        reason=row.get("reason"),
                        buy_amount=row.get("buy_amount", 0),
                        sell_amount=row.get("sell_amount", 0),
                        net_amount=row.get("net_amount", 0),
                        turnover_rate=row.get("turnover_rate", 0),
                        institution_buy=row.get("institution_buy"),
                        institution_sell=row.get("institution_sell"),
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
    ) -> List[LongHuBangData]:
        """
        查询龙虎榜数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            min_net_amount: 最小净买入额
            limit: 返回数量限制

        Returns:
            LongHuBangData对象列表
        """
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

            return query.order_by(LongHuBangData.trade_date.desc()).limit(limit).all()

        finally:
            db.close()


# 全局单例
_market_data_service = None


def get_market_data_service() -> MarketDataService:
    """获取市场数据服务单例"""
    global _market_data_service
    if _market_data_service is None:
        _market_data_service = MarketDataService()
    return _market_data_service
