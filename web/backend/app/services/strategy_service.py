"""
股票策略服务 (StrategyService)

业务逻辑层,负责:
1. 策略执行: 对股票运行策略检查
2. 数据存储: 保存策略筛选结果
3. 数据查询: 查询策略结果
4. 批量扫描: 扫描全市场股票
"""

from sqlalchemy import create_engine, and_, desc
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime, timedelta
from typing import List, Dict, Any
import pandas as pd
import logging
import os
import akshare as ak

from app.models.strategy import StrategyDefinition, StrategyResult
from app.strategies.stock_strategies import get_strategy

logger = logging.getLogger(__name__)


class StrategyService:
    """股票策略服务"""

    def __init__(self):
        """初始化数据库连接"""
        db_url = os.getenv("DATABASE_URL") or self._build_db_url()
        self.engine = create_engine(db_url, pool_pre_ping=True, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def _build_db_url(self) -> str:
        """从环境变量构建数据库URL"""
        return (
            f"postgresql://{os.getenv('POSTGRESQL_USER')}:"
            f"{os.getenv('POSTGRESQL_PASSWORD')}@"
            f"{os.getenv('POSTGRESQL_HOST')}:"
            f"{os.getenv('POSTGRESQL_PORT')}/"
            f"{os.getenv('POSTGRESQL_DATABASE')}"
        )

    # ==================== 数据获取 ====================

    def get_stock_history(
        self,
        symbol: str,
        period: str = "daily",
        start_date: str = None,
        end_date: str = None,
        adjust: str = "qfq",
    ) -> pd.DataFrame:
        """
        获取股票历史数据

        Args:
            symbol: 股票代码 (如: 600519)
            period: 周期 (daily/weekly/monthly)
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            adjust: 复权类型 (qfq=前复权, hfq=后复权, "空"=不复权)

        Returns:
            DataFrame with columns: date, open, high, low, close, volume, amount, p_change
        """
        try:
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
            if end_date is None:
                end_date = datetime.now().strftime("%Y%m%d")

            # 使用akshare获取A股历史数据
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust,
            )

            if df is None or df.empty:
                logger.warning(f"未获取到股票{symbol}的历史数据")
                return pd.DataFrame()

            # 标准化列名
            column_mapping = {
                "日期": "date",
                "开盘": "open",
                "最高": "high",
                "最低": "low",
                "收盘": "close",
                "成交量": "volume",
                "成交额": "amount",
                "涨跌幅": "p_change",
                "涨跌额": "change",
                "振幅": "amplitude",
                "换手率": "turnover",
            }
            df = df.rename(columns=column_mapping)

            # 确保有必需的列
            required_cols = ["date", "open", "high", "low", "close", "volume"]
            if not all(col in df.columns for col in required_cols):
                logger.error(f"股票{symbol}数据缺少必需的列")
                return pd.DataFrame()

            # 确保日期格式正确
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

            return df

        except Exception as e:
            logger.error(f"获取股票{symbol}历史数据失败: {e}")
            return pd.DataFrame()

    def get_stock_list(self, market: str = "A") -> List[Dict[str, str]]:
        """
        获取股票列表

        Args:
            market: 市场类型 (A=A股全部, SH=上证, SZ=深证, CYB=创业板, KCB=科创板)

        Returns:
            List of dict with keys: symbol, name
        """
        try:
            # 获取A股实时行情
            df = ak.stock_zh_a_spot_em()

            if df is None or df.empty:
                logger.warning("未获取到股票列表")
                return []

            # 筛选市场
            if market != "A":
                market_filter = {
                    "SH": lambda x: x.startswith("60") or x.startswith("68"),
                    "SZ": lambda x: x.startswith("00") or x.startswith("30"),
                    "CYB": lambda x: x.startswith("30"),
                    "KCB": lambda x: x.startswith("68"),
                }
                if market in market_filter:
                    df = df[df["代码"].apply(market_filter[market])]

            # 提取股票代码和名称
            result = []
            for _, row in df.iterrows():
                result.append({"symbol": row["代码"], "name": row["名称"]})

            return result

        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return []

    # ==================== 策略执行 ====================

    def run_strategy_for_stock(
        self,
        strategy_code: str,
        symbol: str,
        stock_name: str = None,
        check_date: date = None,
        threshold: int = 60,
    ) -> Dict[str, Any]:
        """
        对单只股票运行策略

        Args:
            strategy_code: 策略代码
            symbol: 股票代码
            stock_name: 股票名称
            check_date: 检查日期 (None表示今天)
            threshold: 数据窗口天数

        Returns:
            {
                "success": bool,
                "match_result": bool,
                "message": str
            }
        """
        try:
            # 1. 获取策略实例
            strategy = get_strategy(strategy_code)
            if strategy is None:
                return {"success": False, "message": f"策略{strategy_code}不存在"}

            # 2. 获取股票历史数据
            days_needed = threshold + 300  # 多取一些数据以确保足够
            start_date = (datetime.now() - timedelta(days=days_needed)).strftime(
                "%Y%m%d"
            )
            end_date = (
                datetime.now().strftime("%Y%m%d")
                if check_date is None
                else check_date.strftime("%Y%m%d")
            )

            df = self.get_stock_history(
                symbol, start_date=start_date, end_date=end_date
            )

            if df.empty:
                return {"success": False, "message": f"未获取到股票{symbol}的历史数据"}

            # 3. 运行策略检查
            check_datetime = (
                datetime.combine(check_date, datetime.min.time())
                if check_date
                else None
            )
            match_result = strategy.check(symbol, df, check_datetime, threshold)

            # 4. 保存结果到数据库
            db = self.SessionLocal()
            try:
                today = check_date or datetime.now().date()

                # 获取最新价格和涨跌幅
                latest_price = str(df.iloc[-1]["close"]) if not df.empty else None
                change_percent = (
                    str(df.iloc[-1]["p_change"])
                    if "p_change" in df.columns and not df.empty
                    else None
                )

                # 检查是否已存在
                existing = (
                    db.query(StrategyResult)
                    .filter(
                        and_(
                            StrategyResult.strategy_code == strategy_code,
                            StrategyResult.symbol == symbol,
                            StrategyResult.check_date == today,
                        )
                    )
                    .first()
                )

                if existing:
                    # 更新现有记录
                    existing.match_result = match_result
                    existing.stock_name = stock_name
                    existing.latest_price = latest_price
                    existing.change_percent = change_percent
                else:
                    # 创建新记录
                    result = StrategyResult(
                        strategy_code=strategy_code,
                        symbol=symbol,
                        stock_name=stock_name,
                        check_date=today,
                        match_result=match_result,
                        latest_price=latest_price,
                        change_percent=change_percent,
                    )
                    db.add(result)

                db.commit()

                return {
                    "success": True,
                    "match_result": match_result,
                    "message": f"{'匹配' if match_result else '不匹配'}策略条件",
                }

            finally:
                db.close()

        except Exception as e:
            logger.error(f"运行策略{strategy_code}失败: {e}")
            return {"success": False, "message": str(e)}

    def run_strategy_batch(
        self,
        strategy_code: str,
        symbols: List[str] = None,
        check_date: date = None,
        limit: int = None,
    ) -> Dict[str, Any]:
        """
        批量运行策略

        Args:
            strategy_code: 策略代码
            symbols: 股票代码列表 (None表示全市场)
            check_date: 检查日期
            limit: 限制处理数量

        Returns:
            {
                "success": bool,
                "total": int,
                "matched": int,
                "failed": int,
                "message": str
            }
        """
        try:
            # 1. 获取股票列表
            if symbols is None:
                stock_list = self.get_stock_list()
                if limit:
                    stock_list = stock_list[:limit]
            else:
                stock_list = [{"symbol": s, "name": ""} for s in symbols]

            total = len(stock_list)
            matched = 0
            failed = 0

            logger.info(f"开始批量运行策略{strategy_code}, 共{total}只股票")

            # 2. 逐个运行策略
            for i, stock in enumerate(stock_list, 1):
                if i % 100 == 0:
                    logger.info(f"进度: {i}/{total}")

                result = self.run_strategy_for_stock(
                    strategy_code=strategy_code,
                    symbol=stock["symbol"],
                    stock_name=stock.get("name"),
                    check_date=check_date,
                )

                if result["success"]:
                    if result.get("match_result"):
                        matched += 1
                else:
                    failed += 1

            return {
                "success": True,
                "total": total,
                "matched": matched,
                "failed": failed,
                "message": f"完成: 总计{total}, 匹配{matched}, 失败{failed}",
            }

        except Exception as e:
            logger.error(f"批量运行策略失败: {e}")
            return {"success": False, "message": str(e)}

    # ==================== 查询方法 ====================

    def query_strategy_results(
        self,
        strategy_code: str = None,
        symbol: str = None,
        check_date: date = None,
        match_result: bool = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict]:
        """
        查询策略结果

        Args:
            strategy_code: 策略代码
            symbol: 股票代码
            check_date: 检查日期
            match_result: 是否匹配
            limit: 返回数量
            offset: 偏移量

        Returns:
            策略结果列表
        """
        db = self.SessionLocal()
        try:
            query = db.query(StrategyResult)

            # 添加过滤条件
            if strategy_code:
                query = query.filter(StrategyResult.strategy_code == strategy_code)
            if symbol:
                query = query.filter(StrategyResult.symbol == symbol)
            if check_date:
                query = query.filter(StrategyResult.check_date == check_date)
            if match_result is not None:
                query = query.filter(StrategyResult.match_result == match_result)

            # 排序和分页
            results = (
                query.order_by(desc(StrategyResult.check_date), StrategyResult.symbol)
                .limit(limit)
                .offset(offset)
                .all()
            )

            return [r.to_dict() for r in results]

        finally:
            db.close()

    def get_strategy_definitions(self) -> List[Dict]:
        """获取所有策略定义"""
        db = self.SessionLocal()
        try:
            strategies = (
                db.query(StrategyDefinition)
                .filter(StrategyDefinition.is_active == True)
                .all()
            )
            return [s.to_dict() for s in strategies]
        finally:
            db.close()

    def get_matched_stocks(
        self, strategy_code: str, check_date: date = None, limit: int = 100
    ) -> List[Dict]:
        """
        获取匹配指定策略的股票列表

        Args:
            strategy_code: 策略代码
            check_date: 检查日期 (None表示最新)
            limit: 返回数量

        Returns:
            匹配的股票列表
        """
        db = self.SessionLocal()
        try:
            query = db.query(StrategyResult).filter(
                and_(
                    StrategyResult.strategy_code == strategy_code,
                    StrategyResult.match_result == True,
                )
            )

            if check_date:
                query = query.filter(StrategyResult.check_date == check_date)
            else:
                # 如果没有指定日期，获取最近的结果
                query = query.order_by(desc(StrategyResult.check_date))

            results = query.limit(limit).all()
            return [r.to_dict() for r in results]

        finally:
            db.close()


# 单例模式
_strategy_service_instance = None


def get_strategy_service() -> StrategyService:
    """获取策略服务单例"""
    global _strategy_service_instance
    if _strategy_service_instance is None:
        _strategy_service_instance = StrategyService()
    return _strategy_service_instance
