"""
实时监控服务
Phase 1: ValueCell Migration - Real-time Monitoring System

基于 ValueCell 的监控模式,适配中国A股市场
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import asyncio

import akshare as ak
import pandas as pd
from sqlalchemy import create_engine, and_, or_, desc
from sqlalchemy.orm import sessionmaker, Session

from app.models.monitoring import (
    AlertRule,
    AlertRecord,
    RealtimeMonitoring,
    DragonTigerList,
    MonitoringStatistics,
    Base,
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitoringService:
    """实时监控服务 (单例模式)"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # 数据库连接
        self.db_url = self._get_database_url()
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # 监控状态
        self.is_monitoring = False
        self.monitored_symbols: List[str] = []

        # A股交易时间
        self.market_open_time = "09:30"
        self.market_close_time = "15:00"

        self._initialized = True
        logger.info("MonitoringService initialized")

    def _get_database_url(self) -> str:
        """获取数据库连接URL"""
        import os
        from dotenv import load_dotenv

        load_dotenv()

        host = os.getenv("POSTGRESQL_HOST", "192.168.123.104")
        port = os.getenv("POSTGRESQL_PORT", "5438")
        user = os.getenv("POSTGRESQL_USER", "postgres")
        password = os.getenv("POSTGRESQL_PASSWORD", "c790414J")
        database = os.getenv("POSTGRESQL_DATABASE", "mystocks")

        return f"postgresql://{user}:{password}@{host}:{port}/{database}"

    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()

    # ========================================================================
    # 告警规则管理
    # ========================================================================

    def create_alert_rule(self, rule_data: Dict) -> AlertRule:
        """创建告警规则"""
        session = self.get_session()
        try:
            rule = AlertRule(**rule_data)
            session.add(rule)
            session.commit()
            session.refresh(rule)
            logger.info(f"Created alert rule: {rule.rule_name}")
            return rule
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create alert rule: {e}")
            raise
        finally:
            session.close()

    def get_alert_rules(
        self, rule_type: Optional[str] = None, is_active: Optional[bool] = None
    ) -> List[AlertRule]:
        """获取告警规则列表"""
        session = self.get_session()
        try:
            query = session.query(AlertRule)

            if rule_type:
                query = query.filter(AlertRule.rule_type == rule_type)
            if is_active is not None:
                query = query.filter(AlertRule.is_active == is_active)

            rules = query.order_by(desc(AlertRule.priority)).all()
            return rules
        finally:
            session.close()

    def update_alert_rule(self, rule_id: int, updates: Dict) -> AlertRule:
        """更新告警规则"""
        session = self.get_session()
        try:
            rule = session.query(AlertRule).filter(AlertRule.id == rule_id).first()
            if not rule:
                raise ValueError(f"Alert rule {rule_id} not found")

            for key, value in updates.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)

            rule.updated_at = datetime.now()
            session.commit()
            session.refresh(rule)
            logger.info(f"Updated alert rule: {rule.rule_name}")
            return rule
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update alert rule: {e}")
            raise
        finally:
            session.close()

    def delete_alert_rule(self, rule_id: int) -> bool:
        """删除告警规则"""
        session = self.get_session()
        try:
            rule = session.query(AlertRule).filter(AlertRule.id == rule_id).first()
            if not rule:
                raise ValueError(f"Alert rule {rule_id} not found")

            session.delete(rule)
            session.commit()
            logger.info(f"Deleted alert rule: {rule.rule_name}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete alert rule: {e}")
            raise
        finally:
            session.close()

    # ========================================================================
    # 实时数据获取
    # ========================================================================

    def fetch_realtime_data(self, symbols: List[str] = None) -> pd.DataFrame:
        """获取实时行情数据"""
        try:
            if symbols and len(symbols) > 0:
                # 获取指定股票的实时数据
                df = ak.stock_zh_a_spot_em()
                df = df[df["代码"].isin(symbols)]
            else:
                # 获取全市场实时数据
                df = ak.stock_zh_a_spot_em()

            if df.empty:
                logger.warning("No realtime data fetched")
                return pd.DataFrame()

            # 重命名列
            df = df.rename(
                columns={
                    "代码": "symbol",
                    "名称": "stock_name",
                    "最新价": "price",
                    "今开": "open_price",
                    "最高": "high_price",
                    "最低": "low_price",
                    "昨收": "pre_close",
                    "涨跌额": "change_amount",
                    "涨跌幅": "change_percent",
                    "成交量": "volume",
                    "成交额": "amount",
                    "换手率": "turnover_rate",
                }
            )

            logger.info(f"Fetched {len(df)} stocks realtime data")
            return df

        except Exception as e:
            logger.error(f"Failed to fetch realtime data: {e}")
            return pd.DataFrame()

    def save_realtime_data(self, df: pd.DataFrame) -> int:
        """保存实时数据到数据库"""
        if df.empty:
            return 0

        session = self.get_session()
        try:
            now = datetime.now()
            today = date.today()
            count = 0

            for _, row in df.iterrows():
                # 判断是否涨停/跌停 (约10%,考虑ST股票5%)
                is_limit_up = False
                is_limit_down = False
                change_pct = row.get("change_percent", 0)

                if change_pct >= 9.9:
                    is_limit_up = True
                elif change_pct <= -9.9:
                    is_limit_down = True

                # 判断是否ST股票
                stock_name = row.get("stock_name", "")
                is_st = "ST" in stock_name or "*ST" in stock_name

                # 创建记录
                record = RealtimeMonitoring(
                    symbol=row.get("symbol"),
                    stock_name=stock_name,
                    timestamp=now,
                    trade_date=today,
                    price=row.get("price"),
                    open_price=row.get("open_price"),
                    high_price=row.get("high_price"),
                    low_price=row.get("low_price"),
                    pre_close=row.get("pre_close"),
                    change_amount=row.get("change_amount"),
                    change_percent=change_pct,
                    volume=row.get("volume"),
                    amount=row.get("amount"),
                    turnover_rate=row.get("turnover_rate"),
                    is_limit_up=is_limit_up,
                    is_limit_down=is_limit_down,
                    is_st=is_st,
                )
                session.add(record)
                count += 1

            session.commit()
            logger.info(f"Saved {count} realtime monitoring records")
            return count

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save realtime data: {e}")
            return 0
        finally:
            session.close()

    # ========================================================================
    # 告警检测和触发
    # ========================================================================

    def evaluate_alert_rules(self, df: pd.DataFrame) -> List[AlertRecord]:
        """评估告警规则并触发告警"""
        if df.empty:
            return []

        # 获取活跃的告警规则
        rules = self.get_alert_rules(is_active=True)
        if not rules:
            logger.info("No active alert rules")
            return []

        triggered_alerts = []

        for rule in rules:
            try:
                alerts = self._evaluate_single_rule(rule, df)
                triggered_alerts.extend(alerts)
            except Exception as e:
                logger.error(f"Failed to evaluate rule {rule.rule_name}: {e}")

        # 保存告警记录
        if triggered_alerts:
            self._save_alert_records(triggered_alerts)
            logger.info(f"Triggered {len(triggered_alerts)} alerts")

        return triggered_alerts

    def _evaluate_single_rule(self, rule: AlertRule, df: pd.DataFrame) -> List[Dict]:
        """评估单个告警规则"""
        alerts = []
        rule_type = rule.rule_type
        parameters = rule.parameters or {}

        # 如果规则指定了特定股票,只检查该股票
        if rule.symbol:
            df = df[df["symbol"] == rule.symbol]

        if df.empty:
            return alerts

        # 根据规则类型评估
        if rule_type == "price_change":
            alerts = self._check_price_change(rule, df, parameters)
        elif rule_type == "volume_surge":
            alerts = self._check_volume_surge(rule, df, parameters)
        elif rule_type == "limit_up":
            alerts = self._check_limit_up(rule, df, parameters)
        elif rule_type == "limit_down":
            alerts = self._check_limit_down(rule, df, parameters)
        elif rule_type == "technical_break":
            alerts = self._check_technical_break(rule, df, parameters)

        return alerts

    def _check_price_change(
        self, rule: AlertRule, df: pd.DataFrame, params: Dict
    ) -> List[Dict]:
        """检查价格变动"""
        alerts = []
        threshold = params.get("change_percent", 5)
        direction = params.get("direction", "both")  # up, down, both

        for _, row in df.iterrows():
            change_pct = row.get("change_percent", 0)

            triggered = False
            if direction == "up" and change_pct >= threshold:
                triggered = True
            elif direction == "down" and change_pct <= -abs(threshold):
                triggered = True
            elif direction == "both" and abs(change_pct) >= threshold:
                triggered = True

            if triggered:
                alerts.append(
                    {
                        "rule": rule,
                        "symbol": row["symbol"],
                        "stock_name": row.get("stock_name"),
                        "alert_type": "price_change",
                        "alert_level": "warning" if abs(change_pct) >= 7 else "info",
                        "alert_title": f"价格{'急涨' if change_pct > 0 else '急跌'}",
                        "alert_message": f"{row.get('stock_name')}({row['symbol']}) 涨跌幅{change_pct:.2f}%",
                        "snapshot_data": row.to_dict(),
                    }
                )

        return alerts

    def _check_volume_surge(
        self, rule: AlertRule, df: pd.DataFrame, params: Dict
    ) -> List[Dict]:
        """检查成交量激增"""
        alerts = []
        # 实际应该获取历史平均成交量对比,这里简化处理
        # TODO: 添加历史数据对比逻辑
        return alerts

    def _check_limit_up(
        self, rule: AlertRule, df: pd.DataFrame, params: Dict
    ) -> List[Dict]:
        """检查涨停"""
        alerts = []
        include_st = params.get("include_st", False)

        # 筛选涨停股票
        limit_up_df = df[df["change_percent"] >= 9.9]

        if not include_st:
            # 排除ST股票
            limit_up_df = limit_up_df[
                ~limit_up_df["stock_name"].str.contains("ST", na=False)
            ]

        for _, row in limit_up_df.iterrows():
            alerts.append(
                {
                    "rule": rule,
                    "symbol": row["symbol"],
                    "stock_name": row.get("stock_name"),
                    "alert_type": "limit_up",
                    "alert_level": "warning",
                    "alert_title": "涨停",
                    "alert_message": f"{row.get('stock_name')}({row['symbol']}) 涨停",
                    "snapshot_data": row.to_dict(),
                }
            )

        return alerts

    def _check_limit_down(
        self, rule: AlertRule, df: pd.DataFrame, params: Dict
    ) -> List[Dict]:
        """检查跌停"""
        alerts = []
        include_st = params.get("include_st", False)

        # 筛选跌停股票
        limit_down_df = df[df["change_percent"] <= -9.9]

        if not include_st:
            # 排除ST股票
            limit_down_df = limit_down_df[
                ~limit_down_df["stock_name"].str.contains("ST", na=False)
            ]

        for _, row in limit_down_df.iterrows():
            alerts.append(
                {
                    "rule": rule,
                    "symbol": row["symbol"],
                    "stock_name": row.get("stock_name"),
                    "alert_type": "limit_down",
                    "alert_level": "critical",
                    "alert_title": "跌停",
                    "alert_message": f"{row.get('stock_name')}({row['symbol']}) 跌停",
                    "snapshot_data": row.to_dict(),
                }
            )

        return alerts

    def _check_technical_break(
        self, rule: AlertRule, df: pd.DataFrame, params: Dict
    ) -> List[Dict]:
        """检查技术突破"""
        alerts = []
        # TODO: 实现技术指标突破检测
        # 需要获取历史数据计算技术指标
        return alerts

    def _save_alert_records(self, alerts: List[Dict]) -> int:
        """保存告警记录"""
        session = self.get_session()
        try:
            count = 0
            for alert_data in alerts:
                rule = alert_data.pop("rule")
                snapshot = alert_data.pop("snapshot_data", {})

                alert = AlertRecord(
                    rule_id=rule.id,
                    rule_name=rule.rule_name,
                    symbol=alert_data["symbol"],
                    stock_name=alert_data.get("stock_name"),
                    alert_type=alert_data["alert_type"],
                    alert_level=alert_data.get("alert_level", "info"),
                    alert_title=alert_data.get("alert_title"),
                    alert_message=alert_data.get("alert_message"),
                    alert_details=alert_data.get("alert_details"),
                    snapshot_data=snapshot,
                )
                session.add(alert)
                count += 1

            session.commit()
            return count
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save alert records: {e}")
            return 0
        finally:
            session.close()

    # ========================================================================
    # 告警记录查询
    # ========================================================================

    def get_alert_records(
        self,
        symbol: Optional[str] = None,
        alert_type: Optional[str] = None,
        alert_level: Optional[str] = None,
        is_read: Optional[bool] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[AlertRecord], int]:
        """查询告警记录"""
        session = self.get_session()
        try:
            query = session.query(AlertRecord)

            # 应用筛选条件
            if symbol:
                query = query.filter(AlertRecord.symbol == symbol)
            if alert_type:
                query = query.filter(AlertRecord.alert_type == alert_type)
            if alert_level:
                query = query.filter(AlertRecord.alert_level == alert_level)
            if is_read is not None:
                query = query.filter(AlertRecord.is_read == is_read)
            if start_date:
                query = query.filter(AlertRecord.alert_time >= start_date)
            if end_date:
                query = query.filter(
                    AlertRecord.alert_time < end_date + timedelta(days=1)
                )

            # 获取总数
            total = query.count()

            # 分页和排序
            records = (
                query.order_by(desc(AlertRecord.alert_time))
                .limit(limit)
                .offset(offset)
                .all()
            )

            return records, total
        finally:
            session.close()

    def mark_alert_read(self, alert_id: int) -> bool:
        """标记告警为已读"""
        session = self.get_session()
        try:
            alert = (
                session.query(AlertRecord).filter(AlertRecord.id == alert_id).first()
            )
            if not alert:
                return False

            alert.is_read = True
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to mark alert read: {e}")
            return False
        finally:
            session.close()

    # ========================================================================
    # 龙虎榜数据
    # ========================================================================

    def fetch_dragon_tiger_list(
        self, trade_date: Optional[date] = None
    ) -> pd.DataFrame:
        """获取龙虎榜数据"""
        try:
            if trade_date is None:
                trade_date = date.today()

            date_str = trade_date.strftime("%Y%m%d")
            df = ak.stock_lhb_detail_daily_sina(date=date_str)

            if df.empty:
                logger.info(f"No dragon tiger data for {date_str}")
                return pd.DataFrame()

            logger.info(f"Fetched {len(df)} dragon tiger records for {date_str}")
            return df

        except Exception as e:
            logger.error(f"Failed to fetch dragon tiger list: {e}")
            return pd.DataFrame()

    def save_dragon_tiger_data(self, df: pd.DataFrame, trade_date: date) -> int:
        """保存龙虎榜数据"""
        if df.empty:
            return 0

        session = self.get_session()
        try:
            count = 0
            for _, row in df.iterrows():
                # 检查是否已存在
                existing = (
                    session.query(DragonTigerList)
                    .filter(
                        and_(
                            DragonTigerList.symbol == row["股票代码"],
                            DragonTigerList.trade_date == trade_date,
                        )
                    )
                    .first()
                )

                if existing:
                    continue

                record = DragonTigerList(
                    symbol=row["股票代码"],
                    stock_name=row.get("股票名称"),
                    trade_date=trade_date,
                    reason=row.get("上榜原因"),
                    total_buy_amount=row.get("买入总额"),
                    total_sell_amount=row.get("卖出总额"),
                    net_amount=row.get("净买额"),
                    detail_data=row.to_dict(),
                )
                session.add(record)
                count += 1

            session.commit()
            logger.info(f"Saved {count} dragon tiger records")
            return count

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save dragon tiger data: {e}")
            return 0
        finally:
            session.close()

    # ========================================================================
    # 监控摘要和统计
    # ========================================================================

    def get_monitoring_summary(self) -> Dict:
        """获取监控摘要"""
        session = self.get_session()
        try:
            today = date.today()

            # 实时监控统计
            realtime_stats = (
                session.query(RealtimeMonitoring)
                .filter(RealtimeMonitoring.trade_date == today)
                .all()
            )

            limit_up_count = sum(1 for r in realtime_stats if r.is_limit_up)
            limit_down_count = sum(1 for r in realtime_stats if r.is_limit_down)
            strong_up_count = sum(
                1 for r in realtime_stats if r.change_percent and r.change_percent > 5
            )
            strong_down_count = sum(
                1 for r in realtime_stats if r.change_percent and r.change_percent < -5
            )

            avg_change = (
                sum(r.change_percent for r in realtime_stats if r.change_percent)
                / len(realtime_stats)
                if realtime_stats
                else 0
            )
            total_amount = (
                sum(r.amount for r in realtime_stats if r.amount)
                if realtime_stats
                else 0
            )

            # 告警统计
            unread_alerts = (
                session.query(AlertRecord)
                .filter(
                    and_(AlertRecord.alert_time >= today, AlertRecord.is_read == False)
                )
                .count()
            )

            active_alerts = (
                session.query(AlertRecord)
                .filter(AlertRecord.alert_time >= today)
                .count()
            )

            return {
                "total_stocks": len(realtime_stats),
                "limit_up_count": limit_up_count,
                "limit_down_count": limit_down_count,
                "strong_up_count": strong_up_count,
                "strong_down_count": strong_down_count,
                "avg_change_percent": round(avg_change, 2),
                "total_amount": total_amount,
                "active_alerts": active_alerts,
                "unread_alerts": unread_alerts,
            }

        finally:
            session.close()

    # ========================================================================
    # 主监控循环
    # ========================================================================

    async def start_monitoring(self, symbols: List[str] = None, interval: int = 60):
        """启动监控"""
        self.is_monitoring = True
        self.monitored_symbols = symbols or []

        logger.info(f"Starting monitoring with interval {interval}s")

        while self.is_monitoring:
            try:
                # 检查是否在交易时间
                now = datetime.now()
                current_time = now.strftime("%H:%M")

                if self.market_open_time <= current_time <= self.market_close_time:
                    # 在交易时间内执行监控
                    logger.info("Fetching realtime data...")
                    df = self.fetch_realtime_data(self.monitored_symbols)

                    if not df.empty:
                        # 保存数据
                        self.save_realtime_data(df)

                        # 评估告警规则
                        self.evaluate_alert_rules(df)
                else:
                    logger.info(f"Market closed. Current time: {current_time}")

                # 等待下一次更新
                await asyncio.sleep(interval)

            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(interval)

    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        logger.info("Monitoring stopped")


# 创建全局单例
monitoring_service = MonitoringService()
