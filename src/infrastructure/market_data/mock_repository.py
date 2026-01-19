"""
Mock市场数据仓储
Mock Market Data Repository

用于Phase 0原型验证的Mock数据源，返回固定K线数据。
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta

from ...domain.market_data.model.bar import Bar
from ...domain.market_data.repository.imarket_data_repository import IMarketDataRepository


class MockMarketDataRepository(IMarketDataRepository):
    """
    Mock市场数据仓储

    职责：
    - 为Phase 0原型验证提供固定数据
    - 支持单元测试
    - 不依赖外部数据源

    使用场景：
    - 原型验证
    - 单元测试
    - 本地开发
    """

    def __init__(self):
        """初始化Mock数据"""
        # 生成10天的MockK线数据
        self._mock_bars = self._generate_mock_bars()

    def _generate_mock_bars(self) -> List[Bar]:
        """生成Mock K线数据"""
        bars = []
        base_price = 10.0
        base_time = datetime.now() - timedelta(days=10)

        for i in range(10):
            # 生成随机波动
            open_price = base_price + (i * 0.1)
            high_price = open_price + 0.2
            low_price = open_price - 0.2
            close_price = open_price + (0.1 if i % 2 == 0 else -0.1)
            volume = 1000000 + (i * 100000)

            bar = Bar(
                symbol="000001.SZ",
                timestamp=base_time + timedelta(days=i),
                open=round(open_price, 2),
                high=round(high_price, 2),
                low=round(low_price, 2),
                close=round(close_price, 2),
                volume=float(volume),
            )
            bars.append(bar)
            base_price = close_price

        return bars

    def get_bars(self, symbol: str, start_date: str, end_date: str) -> List[Bar]:
        """
        获取K线数据

        Args:
            symbol: 标的代码
            start_date: 开始日期（ISO格式）
            end_date: 结束日期（ISO格式）

        Returns:
            List[Bar]: K线数据列表
        """
        # Phase 0简化：忽略日期范围，返回所有Mock数据
        print(f"[MockMarketDataRepository] Returning {len(self._mock_bars)} bars for {symbol}")
        return self._mock_bars

    def get_latest_bar(self, symbol: str) -> Bar:
        """
        获取最新K线数据

        Args:
            symbol: 标的代码

        Returns:
            Bar: 最新K线数据
        """
        return self._mock_bars[-1]

    def get_market_snapshot(self, symbol: str) -> Dict[str, Any]:
        """
        获取市场快照（包含当前价格和指标）

        Args:
            symbol: 标的代码

        Returns:
            Dict: 市场快照数据
        """
        latest_bar = self.get_latest_bar(symbol)

        # Phase 0简化：返回固定指标值
        return {
            "symbol": symbol,
            "price": latest_bar.close,
            "timestamp": latest_bar.timestamp,
            "indicators": {"RSI": 75.0, "MACD": 0.5, "MA_5": 10.2, "MA_10": 10.5, "MA_20": 10.8},  # 超买
        }
