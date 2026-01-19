"""
Snapshot Service (Optimized)
快照服务

职责：
- 动态路由数据源获取行情
- 捕获入选/实时/历史快照
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from uuid import uuid4
import pandas as pd

from src.domain.watchlist.value_objects import IndicatorSnapshot, IndicatorValue
from src.indicators.indicator_factory import IndicatorFactory

logger = logging.getLogger(__name__)


class SnapshotService:
    def __init__(self, data_source_manager=None, indicator_factory: IndicatorFactory = None):
        self.data_source_manager = data_source_manager
        self.indicator_factory = indicator_factory or IndicatorFactory()
        self._default_indicators = ["sma.5", "sma.20", "rsi.14", "macd.12.26.9"]

    def capture_entry_snapshot(
        self,
        stock_code: str,
        indicator_ids: List[str] = None,
        reference_days: int = 20,
        price_data: Dict[str, float] = None,
    ) -> IndicatorSnapshot:
        """捕获入选时的快照"""
        indicators = indicator_ids or self._default_indicators

        if price_data is None:
            price_data = self._get_latest_price(stock_code)

        if price_data is None:
            price_data = {"close": 0, "high": 0, "low": 0, "open": 0, "volume": 0}

        indicator_values = {}
        for ind_id in indicators:
            try:
                value = self._calculate_indicator(stock_code, ind_id, reference_days)
                indicator_values[ind_id] = IndicatorValue(indicator_id=ind_id, value=value)
            except Exception as e:
                logger.warning(f"Failed to calculate {ind_id} for {stock_code}: {e}")

        return IndicatorSnapshot(
            snapshot_id=str(uuid4()),
            stock_code=stock_code,
            captured_at=datetime.now(),
            indicators=indicator_values,
            price_data=price_data,
            reference_time=datetime.now() - timedelta(days=reference_days),
        )

    def _get_latest_price(self, stock_code: str) -> Optional[Dict[str, float]]:
        """优化：使用智能路由获取实时价格"""
        if not self.data_source_manager:
            return None

        try:
            # 动态查找最佳实时行情接口
            endpoint = self.data_source_manager.get_best_endpoint("REALTIME_QUOTE")
            if not endpoint:
                return None

            data = self.data_source_manager._call_endpoint(endpoint, symbols=[stock_code])
            if data is not None and not data.empty:
                row = data.iloc[0]
                return {
                    "close": float(row.get("price", row.get("close", 0))),
                    "high": float(row.get("high", 0)),
                    "low": float(row.get("low", 0)),
                    "open": float(row.get("open", 0)),
                    "volume": int(row.get("volume", 0)),
                }
        except Exception as e:
            logger.debug(f"Could not get realtime price for {stock_code}: {e}")
        return None

    def _calculate_indicator(self, stock_code: str, indicator_id: str, lookback_days: int) -> float:
        """优化：使用智能路由获取历史数据并计算"""
        if not self.data_source_manager:
            return 0.0

        try:
            # 动态查找最佳日线接口
            endpoint = self.data_source_manager.get_best_endpoint("DAILY_KLINE")
            if not endpoint:
                return 0.0

            data = self.data_source_manager._call_endpoint(endpoint, symbol=stock_code)
            if data is not None and not data.empty:
                # 截取计算所需长度
                if len(data) > lookback_days + 50:  # 多取一点缓冲
                    data = data.tail(lookback_days + 50)

                # 使用工厂计算指标
                result = self.indicator_factory.calculate(indicator_id, data)

                if isinstance(result, pd.Series):
                    return float(result.iloc[-1]) if not result.empty else 0.0
                elif isinstance(result, pd.DataFrame):
                    # 处理 MACD 等返回多列的情况
                    col = indicator_id.split(".")[0] if "." in indicator_id else result.columns[0]
                    return float(result[col].iloc[-1]) if not result.empty else 0.0
        except Exception as e:
            logger.debug(f"Indicator calculation failed for {stock_code}/{indicator_id}: {e}")

        return 0.0

    def capture_realtime_snapshot(self, stock_code: str, indicator_ids: List[str] = None) -> IndicatorSnapshot:
        return self.capture_entry_snapshot(stock_code, indicator_ids, reference_days=1)
