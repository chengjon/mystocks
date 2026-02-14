"""Mock 数据子模块"""

import logging
import random
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MockExtendedDataMixin:
    """Mock 扩展数据：自选股、回测、默认数据、缓存"""

    def _generate_watchlist_data(user_id: int = 1) -> List[Dict[str, Any]]:
        """生成自选股Mock数据"""
        import random
        from datetime import datetime

        # 模拟自选股数据
        stocks = [
            {"symbol": "600519", "name": "贵州茅台", "exchange": "SSE", "market": "CN"},
            {"symbol": "000001", "name": "平安银行", "exchange": "SZSE", "market": "CN"},
            {"symbol": "000858", "name": "五粮液", "exchange": "SZSE", "market": "CN"},
            {"symbol": "601318", "name": "中国平安", "exchange": "SSE", "market": "CN"},
            {"symbol": "600276", "name": "恒瑞医药", "exchange": "SSE", "market": "CN"},
        ]

        # 模拟分组
        groups = [
            {"id": 1, "name": "默认分组", "created_at": "2024-01-01", "is_default": True},
            {"id": 2, "name": "核心持仓", "created_at": "2024-01-15", "is_default": False},
            {"id": 3, "name": "技术股", "created_at": "2024-02-01", "is_default": False},
        ]

        watchlist_data = []
        for i, stock in enumerate(stocks):
            # 随机分配到不同分组
            group_id = random.choice([1, 2, 3])
            added_date = datetime.now() - timedelta(days=random.randint(1, 90))

            watchlist_data.append(
                {
                    "id": i + 1,
                    "symbol": stock["symbol"],
                    "display_name": stock["name"],
                    "exchange": stock["exchange"],
                    "market": stock["market"],
                    "notes": f"备注信息 {random.randint(1, 5)}",
                    "group_id": group_id,
                    "group_name": next(g["name"] for g in groups if g["id"] == group_id),
                    "added_at": added_date.isoformat(),
                    "price": round(random.uniform(10, 500), 2),
                    "change": round(random.uniform(-10, 10), 2),
                    "change_percent": round(random.uniform(-5, 5), 2),
                }
            )

        return watchlist_data

    def _generate_mock_backtest_data(self, **kwargs) -> Dict[str, Any]:
        """
        Generate mock backtest data.
        """
        task_id = kwargs.get("task_id", "mock-task-123")

        # Mock Trades
        trades = [
            {
                "symbol": "AAPL",
                "entry_date": "2024-01-05T10:00:00",
                "exit_date": "2024-01-10T14:00:00",
                "entry_price": 150.0,
                "exit_price": 155.0,
                "quantity": 100,
                "pnl": 500.0,
                "return_pct": 0.033,
            },
            {
                "symbol": "GOOGL",
                "entry_date": "2024-02-01T11:00:00",
                "exit_date": "2024-02-05T15:00:00",
                "entry_price": 2800.0,
                "exit_price": 2750.0,
                "quantity": 10,
                "pnl": -500.0,
                "return_pct": -0.018,
            },
        ]

        # Mock Equity Curve
        equity_curve = [
            {"date": "2024-01-01", "equity": 100000.0},
            {"date": "2024-01-02", "equity": 100100.0},
            {"date": "2024-01-03", "equity": 100200.0},
            {"date": "2024-01-04", "equity": 100150.0},
            {"date": "2024-01-05", "equity": 100500.0},
        ]

        # Mock Summary
        summary = {
            "total_return": 0.15,
            "annualized_return": 0.18,
            "max_drawdown": -0.10,
            "sharpe_ratio": 1.5,
            "win_rate": 0.6,
            "total_trades": 50,
        }

        return {
            "task_id": task_id,
            "status": "completed",
            "summary": summary,
            "equity_curve": equity_curve,
            "trades": trades,
            "error_message": None,
            "timestamp": datetime.now().isoformat(),
        }

    def _get_default_data(self, data_type: str, **kwargs) -> Dict[str, Any]:
        """获取默认数据"""
        if data_type == "technical":
            return {
                "indicators": {
                    "trend": {"ma5": 10.5, "ma10": 10.8, "ma20": 11.2},
                    "momentum": {"rsi6": 65.5, "rsi12": 58.2},
                    "volatility": {
                        "bb_upper": 12.5,
                        "bb_middle": 11.0,
                        "bb_lower": 9.5,
                    },
                    "volume": {"obv": 1250000, "vwap": 10.8},
                },
                "signals": {"overall_signal": "hold"},
                "timestamp": datetime.now().isoformat(),
            }
        elif data_type == "strategy":
            return {
                "data": [
                    {
                        "strategy_code": "volume_surge",
                        "strategy_name_cn": "成交量激增",
                        "strategy_name_en": "Volume Surge",
                    },
                    {
                        "strategy_code": "ma_bullish",
                        "strategy_name_cn": "均线多头",
                        "strategy_name_en": "MA Bullish",
                    },
                ],
                "total": 2,
                "timestamp": datetime.now().isoformat(),
            }
        elif data_type == "watchlist":
            return {
                "data": [
                    {
                        "id": 1,
                        "symbol": "000001",
                        "name": "平安银行",
                        "price": 15.32,
                        "change": 0.45,
                    },
                    {
                        "id": 2,
                        "symbol": "600519",
                        "name": "贵州茅台",
                        "price": 1680.50,
                        "change": -15.20,
                    },
                ],
                "total": 2,
                "timestamp": datetime.now().isoformat(),
            }
        else:
            return {"data": [], "total": 0, "timestamp": datetime.now().isoformat()}

    def _get_real_data(self, data_type: str, **kwargs) -> Dict[str, Any]:
        """获取真实数据库数据"""
        # 这里应该连接真实的数据库
        # 暂时抛出异常，提示需要实现真实数据获取逻辑
        raise NotImplementedError(f"真实数据库数据获取功能尚未实现: {data_type}")

    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查缓存是否有效"""
        if cache_key not in self._cache_timestamp:
            return False

        timestamp = self._cache_timestamp[cache_key]
        return (datetime.now() - timestamp).total_seconds() < self._cache_ttl

    def _update_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """更新缓存"""
        self._data_cache[cache_key] = data
        self._cache_timestamp[cache_key] = datetime.now()

        # 缓存大小限制
        if len(self._data_cache) > 1000:
            # 清理最旧的缓存
            oldest_key = min(self._cache_timestamp.keys(), key=lambda k: self._cache_timestamp[k])
            del self._data_cache[oldest_key]
            del self._cache_timestamp[oldest_key]

    def clear_cache(self) -> None:
        """清除缓存"""
        self._data_cache.clear()
        self._cache_timestamp.clear()
        logger.info("缓存已清除")

    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        return {
            "cache_size": len(self._data_cache),
            "cache_ttl": self._cache_ttl,
            "mock_mode": self.use_mock_data,
        }

    def get_technical_indicators(self, symbol: str) -> Dict[str, Any]:
        """
        获取技术指标数据 - 兼容Technical Analysis适配器

        Args:
            symbol: 股票代码

        Returns:
            技术指标数据
        """
        try:
            # 调用现有的technical数据类型
            result = self.get_data("technical", symbol=symbol)

            if result and "indicators" in result:
                indicators = result["indicators"]

                # indicators 直接包含 trend, momentum, volatility, volume 等字段
                # 格式化返回数据结构，适配TechnicalAnalysisDataSourceAdapter的期望
                return {
                    "trend": indicators.get("trend", {}),
                    "momentum": indicators.get("momentum", {}),
                    "volatility": indicators.get("volatility", {}),
                    "volume": indicators.get("volume", {}),
                    "signals": result.get("signals", {}),
                    "symbol": symbol,
                    "latest_price": 100.0,  # 添加默认最新价格
                    "latest_date": datetime.now().strftime("%Y-%m-%d"),
                    "data_points": 252,
                    "total_indicators": 19,
                    "timestamp": result.get("timestamp", datetime.now().isoformat()),
                }
            else:
                # 返回默认的技术指标结构
                return {
                    "trend": {
                        "ma5": 10.5,
                        "ma10": 10.8,
                        "ma20": 11.2,
                        "ma30": 11.5,
                        "ema12": 10.6,
                        "ema26": 10.9,
                        "macd": 0.15,
                        "macd_signal": 0.12,
                        "macd_hist": 0.03,
                        "adx": 25.5,
                        "plus_di": 18.2,
                        "minus_di": 15.8,
                        "sar": 10.3,
                    },
                    "momentum": {
                        "rsi6": 65.5,
                        "rsi12": 58.2,
                        "rsi24": 52.8,
                        "kdj_k": 62.5,
                        "kdj_d": 58.3,
                        "kdj_j": 70.9,
                        "cci": 85.2,
                        "willr": 35.5,
                        "roc": 2.5,
                    },
                    "volatility": {
                        "bb_upper": 12.5,
                        "bb_middle": 11.0,
                        "bb_lower": 9.5,
                        "bb_width": 0.27,
                        "atr": 0.85,
                        "atr_percent": 7.7,
                        "kc_upper": 12.2,
                        "kc_middle": 11.0,
                        "kc_lower": 9.8,
                        "stddev": 0.95,
                    },
                    "volume": {
                        "obv": 1250000,
                        "vwap": 10.8,
                        "volume_ma5": 850000,
                        "volume_ma10": 920000,
                        "volume_ratio": 1.15,
                    },
                    "signals": {
                        "overall_signal": "hold",
                        "signal_strength": 0.65,
                        "signals": [
                            {"type": "trend", "signal": "hold", "strength": 0.6},
                            {"type": "momentum", "signal": "buy", "strength": 0.7},
                            {"type": "volatility", "signal": "hold", "strength": 0.5},
                        ],
                        "signal_count": {"buy": 1, "sell": 0, "hold": 2},
                    },
                    "symbol": symbol,
                    "timestamp": datetime.now().isoformat(),
                }
        except Exception:
            logger.error("获取技术指标失败: %(e)s")
            return None

    def set_mock_mode(self, enabled: bool) -> None:
        """设置Mock模式"""
        self.use_mock_data = enabled
        logger.info("设置Mock模式: %(enabled)s")

        # 切换模式时清除缓存
        self.clear_cache()

