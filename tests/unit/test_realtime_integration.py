"""
测试用例: Phase 12.3 - Real-time Data Stream Integration

测试内容:
1. 行情数据解析器测试
2. 持仓市值计算引擎测试
3. 性能优化模块测试
4. 集成测试

Author: Claude Code
Date: 2026-01-09
"""

import asyncio
import os
import sys
from datetime import datetime
from decimal import Decimal

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMarketDataParser:
    """行情数据解析器测试"""

    def setup_method(self):
        """测试初始化"""
        from src.services.market_data_parser import MarketDataParser

        self.parser = MarketDataParser()

    def test_parse_efinance_data(self):
        """测试解析 efinance 数据"""
        data = {
            "代码": "600519",
            "名称": "贵州茅台",
            "最新价": 1850.50,
            "开盘": 1840.00,
            "最高": 1860.00,
            "最低": 1835.00,
            "昨收": 1845.00,
            "成交量": 5000000,
            "成交额": 9250000000,
            "涨跌额": 5.50,
            "涨跌幅": 0.30,
        }

        result = self.parser.parse(data, "efinance")

        assert result is not None
        assert result.symbol == "600519"
        assert result.name == "贵州茅台"
        assert result.price == 1850.50
        assert result.open == 1840.00
        assert result.high == 1860.00
        assert result.low == 1835.00
        assert result.volume == 5000000

    def test_parse_easyquotation_data(self):
        """测试解析 easyquotation 数据"""
        data = {
            "code": "600519",
            "now": 1850.50,
            "info": {
                "name": "贵州茅台",
                "open": 1840.00,
                "high": 1860.00,
                "low": 1835.00,
                "close": 1845.00,
                "change": 5.50,
                "pct": 0.30,
            },
            "vol": 5000000,
            "amount": 9250000000,
        }

        result = self.parser.parse(data, "easyquotation")

        assert result is not None
        assert result.symbol == "600519"
        assert result.price == 1850.50

    def test_normalize_symbol(self):
        """测试股票代码标准化"""
        assert self.parser._normalize_symbol("600519") == "600519"
        assert self.parser._normalize_symbol("600519.SH") == "600519"
        assert self.parser._normalize_symbol("sh600519") == "600519"
        # SZ 前缀需要特殊处理
        assert self.parser._normalize_symbol("000001") == "000001"

    def test_safe_float_conversion(self):
        """测试安全类型转换"""
        assert self.parser._safe_float("1850.50") == 1850.50
        assert self.parser._safe_float(None) == 0.0
        assert self.parser._safe_float("invalid") == 0.0
        assert self.parser._safe_float(1850.50) == 1850.50

    def test_parse_batch(self):
        """测试批量解析"""
        data_list = [
            {"代码": "600519", "名称": "贵州茅台", "最新价": 1850.50},
            {"代码": "000001", "名称": "平安银行", "最新价": 12.30},
            {"代码": "600036", "名称": "招商银行", "最新价": 45.60},
        ]

        results = self.parser.parse_batch(data_list, "efinance")

        assert len(results) == 3
        assert results[0].symbol == "600519"
        assert results[1].symbol == "000001"
        assert results[2].symbol == "600036"


class TestPositionMTMEngine:
    """持仓市值计算引擎测试"""

    def setup_method(self):
        """测试初始化"""
        from src.services.position_mtm_engine import PositionMTMEngine

        self.engine = PositionMTMEngine()

    def test_register_position(self):
        """测试注册持仓"""
        snapshot = self.engine.register_position(
            position_id="pos_001",
            portfolio_id="portfolio_001",
            symbol="600519",
            quantity=100,
            avg_price=1800.00,
        )

        assert snapshot is not None
        assert snapshot.position_id == "pos_001"
        assert snapshot.symbol == "600519"
        assert snapshot.quantity == 100
        assert snapshot.avg_price == 1800.00

    def test_update_price(self):
        """测试更新价格"""
        self.engine.register_position(
            position_id="pos_001",
            portfolio_id="portfolio_001",
            symbol="600519",
            quantity=100,
            avg_price=1800.00,
        )

        updates = self.engine.update_price("600519", 1850.00)

        assert len(updates) == 1
        assert updates[0].old_price == 1800.00
        assert updates[0].new_price == 1850.00

        position = self.engine.get_position_snapshot("pos_001")
        assert position.market_price == 1850.00
        assert position.market_value == 185000.00
        assert position.unrealized_profit == 5000.00

    def test_update_price_batch(self):
        """测试批量更新价格"""
        self.engine.register_position(
            position_id="pos_001",
            portfolio_id="portfolio_001",
            symbol="600519",
            quantity=100,
            avg_price=1800.00,
        )
        self.engine.register_position(
            position_id="pos_002",
            portfolio_id="portfolio_001",
            symbol="000001",
            quantity=200,
            avg_price=12.00,
        )

        async def run_test():
            updates = await self.engine.update_price_batch(
                {
                    "600519": 1850.00,
                    "000001": 12.50,
                }
            )
            return updates

        updates = asyncio.run(run_test())

        assert len(updates) == 2

        portfolio = self.engine.get_portfolio_snapshot("portfolio_001")
        assert portfolio is not None
        assert portfolio.position_count == 2

    def test_unregister_position(self):
        """测试注销持仓"""
        self.engine.register_position(
            position_id="pos_001",
            portfolio_id="portfolio_001",
            symbol="600519",
            quantity=100,
            avg_price=1800.00,
        )

        result = self.engine.unregister_position("pos_001")

        assert result is True
        assert self.engine.get_position_snapshot("pos_001") is None

    def test_profit_calculation(self):
        """测试盈亏计算"""
        self.engine.register_position(
            position_id="pos_001",
            portfolio_id="portfolio_001",
            symbol="600519",
            quantity=100,
            avg_price=1800.00,
        )

        self.engine.update_price("600519", 1900.00)

        position = self.engine.get_position_snapshot("pos_001")
        assert position.unrealized_profit == 10000.00
        assert abs(position.profit_ratio - 5.56) < 0.01

        self.engine.update_price("600519", 1700.00)

        position = self.engine.get_position_snapshot("pos_001")
        assert position.unrealized_profit == -10000.00
        assert abs(position.profit_ratio + 5.56) < 0.01

    def test_get_metrics(self):
        """测试获取指标"""
        self.engine.register_position(
            position_id="pos_001",
            portfolio_id="portfolio_001",
            symbol="600519",
            quantity=100,
            avg_price=1800.00,
        )

        metrics = self.engine.get_metrics()

        assert metrics["position_count"] == 1
        assert metrics["portfolio_count"] == 1
        assert metrics["total_updates"] == 0

    def test_listener_notification(self):
        """测试监听器通知"""
        from src.services.position_mtm_engine import PositionMTMEngine

        engine = PositionMTMEngine(enable_batching=False)

        engine.register_position(
            position_id="pos_001",
            portfolio_id="portfolio_001",
            symbol="600519",
            quantity=100,
            avg_price=1800.00,
        )

        notified_updates = []

        async def async_listener(updates):
            notified_updates.extend(updates)

        engine.add_listener(async_listener)

        updates = engine.update_price("600519", 1850.00)

        assert len(updates) == 1
        assert updates[0].symbol == "600519"


class TestPerformanceOptimizer:
    """性能优化模块测试"""

    def setup_method(self):
        """测试初始化"""
        from src.services.performance_optimizer import (
            BatchProcessor,
            CacheKeyGenerator,
            IncrementalCalculator,
            LRUCache,
        )

        self.cache = LRUCache(max_size=10, ttl=60.0)
        self.batch_processor = BatchProcessor(max_batch_size=5)

    def test_lru_cache(self):
        """测试 LRU 缓存"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")

        assert self.cache.get("key1") == "value1"
        assert self.cache.get("key2") == "value2"
        assert self.cache.get("key3") is None

    def test_lru_cache_eviction(self):
        """测试 LRU 缓存淘汰"""
        for i in range(15):
            self.cache.set(f"key{i}", f"value{i}")

        assert self.cache.get("key0") is None
        assert self.cache.get("key5") is not None
        assert self.cache.get("key14") is not None

    def test_batch_processor(self):
        """测试批量处理器"""
        processed_items = []

        async def processor(items):
            processed_items.extend(items)

        self.batch_processor.processor = processor

        async def run_test():
            for i in range(3):
                await self.batch_processor.add(f"item{i}")

            await self.batch_processor.flush()

        asyncio.run(run_test())

        assert len(processed_items) == 3

    def test_incremental_calculator(self):
        """测试增量计算器"""
        from src.services.performance_optimizer import IncrementalCalculator

        calc = IncrementalCalculator(initial_value=100.0)

        assert calc.get_value() == 100.0

        calc.add_delta(10.0)
        assert calc.get_value() == 110.0

        calc.set_value(150.0)
        assert calc.get_value() == 150.0

    def test_cache_key_generator(self):
        """测试缓存键生成器"""
        from src.services.performance_optimizer import CacheKeyGenerator

        key1 = CacheKeyGenerator.position_key("600519", 100, 1800.00)
        key2 = CacheKeyGenerator.position_key("600519", 100, 1800.00)
        key3 = CacheKeyGenerator.position_key("600519", 200, 1800.00)

        assert key1 == key2
        assert key1 != key3


class TestIntegration:
    """集成测试"""

    def test_full_mtm_flow(self):
        """测试完整的 MTM 计算流程"""
        from src.services.market_data_parser import MarketDataParser
        from src.services.position_mtm_engine import PositionMTMEngine

        parser = MarketDataParser()
        engine = PositionMTMEngine()

        raw_data = {
            "代码": "600519",
            "名称": "贵州茅台",
            "最新价": 1850.50,
            "开盘": 1840.00,
            "最高": 1860.00,
            "最低": 1835.00,
            "昨收": 1845.00,
            "成交量": 5000000,
            "成交额": 9250000000,
            "涨跌额": 5.50,
            "涨跌幅": 0.30,
        }

        quote = parser.parse(raw_data, "efinance")
        assert quote is not None

        engine.register_position(
            position_id="pos_001",
            portfolio_id="portfolio_001",
            symbol=quote.symbol,
            quantity=100,
            avg_price=quote.pre_close,
        )

        engine.update_price(quote.symbol, quote.price)

        position = engine.get_position_snapshot("pos_001")
        assert position is not None
        assert position.market_price == quote.price
        assert position.unrealized_profit == quote.change * position.quantity

        portfolio = engine.get_portfolio_snapshot("portfolio_001")
        assert portfolio is not None
        assert portfolio.position_count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
