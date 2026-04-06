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

import logging
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import and_

from app.models.market_data import LongHuBangData

logger = logging.getLogger(__name__)


class MarketDataServiceFetchAndSaveMixin:
    """MarketDataService 方法集 Part 2"""

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

