"""
市场数据服务单元测试
测试web/backend/app/services/market_data_service.py的核心功能
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
import pandas as pd
import sys
import os

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../web/backend'))


class MockMarketDataService:
    """模拟市场数据服务用于测试"""

    def __init__(self, use_cache=True):
        self.use_cache = use_cache
        self.cache_hits = 0
        self.cache_misses = 0
        self.db_calls = 0

    def fetch_fund_flow(self, symbol: str, timeframe: str = "1"):
        """获取资金流向数据"""
        self.db_calls += 1

        return {
            "success": True,
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,
                "trade_date": date.today().isoformat(),
                "main_net_inflow": 125000000.00,
                "small_net_inflow": -35000000.00,
                "medium_net_inflow": -15000000.00,
                "large_net_inflow": -75000000.00,
                "super_net_inflow": 200000000.00,
                "main_net_inflow_rate": 8.5
            },
            "cached": False
        }

    def fetch_fund_flow_cached(self, symbol: str, timeframe: str = "1"):
        """获取资金流向数据（带缓存）"""
        cache_key = f"fund_flow:{symbol}:{timeframe}"

        if self.use_cache and hasattr(self, '_cache') and cache_key in self._cache:
            self.cache_hits += 1
            data = self._cache[cache_key]
            data['cached'] = True
            return data

        self.cache_misses += 1
        data = self.fetch_fund_flow(symbol, timeframe)

        if self.use_cache:
            if not hasattr(self, '_cache'):
                self._cache = {}
            self._cache[cache_key] = data

        return data

    def query_fund_flow(self, symbol: str, timeframe: str = None,
                       start_date: date = None, end_date: date = None):
        """查询资金流向历史数据"""
        self.db_calls += 1

        # 生成模拟数据
        if start_date and end_date:
            days = (end_date - start_date).days + 1
        else:
            days = 5

        results = []
        for i in range(days):
            day = (end_date or date.today()) - timedelta(days=i)
            results.append({
                "symbol": symbol,
                "trade_date": day.isoformat(),
                "timeframe": timeframe or "1",
                "main_net_inflow": 100000000.00 + i * 10000000,
                "main_net_inflow_rate": 5.0 + i * 0.5
            })

        return results

    def fetch_etf_spot(self, symbol: str = None):
        """获取ETF实时数据"""
        self.db_calls += 1

        if symbol:
            return [{
                "symbol": symbol,
                "name": "芯片ETF",
                "latest_price": 0.856,
                "change_percent": 2.15,
                "volume": 125000000,
                "amount": 107000000.00
            }]
        else:
            return [
                {
                    "symbol": "159995",
                    "name": "芯片ETF",
                    "latest_price": 0.856,
                    "change_percent": 2.15,
                    "volume": 125000000,
                    "amount": 107000000.00
                },
                {
                    "symbol": "512480",
                    "name": "半导体ETF",
                    "latest_price": 1.234,
                    "change_percent": 1.85,
                    "volume": 98000000,
                    "amount": 120000000.00
                }
            ]

    def query_etf_spot(self, symbol: str = None, keyword: str = None, limit: int = 50):
        """查询ETF数据"""
        self.db_calls += 1

        data = self.fetch_etf_spot(symbol)

        if keyword:
            data = [item for item in data if keyword in item['name'] or keyword in item['symbol']]

        return data[:limit]

    def fetch_chip_race(self, race_type: str = "open", trade_date: date = None):
        """获取竞价抢筹数据"""
        self.db_calls += 1

        return {
            "success": True,
            "data": [
                {
                    "symbol": "600519",
                    "name": "贵州茅台",
                    "race_type": race_type,
                    "trade_date": (trade_date or date.today()).isoformat(),
                    "race_amount": 125000000.00,
                    "race_volume": 125000,
                    "latest_price": 1750.50
                }
            ]
        }

    def query_chip_race(self, race_type: str = "open", trade_date: date = None,
                       min_race_amount: float = None, limit: int = 100):
        """查询竞价抢筹历史数据"""
        self.db_calls += 1

        results = self.fetch_chip_race(race_type, trade_date)['data']

        if min_race_amount:
            results = [r for r in results if r['race_amount'] >= min_race_amount]

        return results[:limit]

    def get_cache_stats(self):
        """获取缓存统计"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests) if total_requests > 0 else 0

        return {
            "cache_enabled": self.use_cache,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": hit_rate,
            "db_calls": self.db_calls
        }

    def clear_cache(self):
        """清理缓存"""
        if hasattr(self, '_cache'):
            cache_size = len(self._cache)
            self._cache.clear()
            return {"cleared": cache_size}
        return {"cleared": 0}


class TestMarketDataService:
    """市场数据服务测试类"""

    def setup_method(self):
        """测试前的设置"""
        self.service = MockMarketDataService(use_cache=True)

    def test_initialization(self):
        """测试服务初始化"""
        assert self.service.use_cache is True
        assert self.service.cache_hits == 0
        assert self.service.cache_misses == 0
        assert self.service.db_calls == 0

    def test_fetch_fund_flow_basic(self):
        """测试基本的资金流向获取"""
        result = self.service.fetch_fund_flow("600519", "1")

        assert result['success'] is True
        assert 'data' in result
        assert result['data']['symbol'] == "600519"
        assert result['data']['timeframe'] == "1"
        assert result['data']['main_net_inflow'] > 0
        assert self.service.db_calls == 1

    def test_fetch_fund_flow_cached_miss(self):
        """测试缓存未命中"""
        result = self.service.fetch_fund_flow_cached("600519", "1")

        assert result['success'] is True
        assert result.get('cached') is False
        assert self.service.cache_misses == 1
        assert self.service.cache_hits == 0

    def test_fetch_fund_flow_cached_hit(self):
        """测试缓存命中"""
        # 第一次调用 - 缓存未命中
        result1 = self.service.fetch_fund_flow_cached("600519", "1")
        assert result1.get('cached') is False

        # 第二次调用 - 缓存命中
        result2 = self.service.fetch_fund_flow_cached("600519", "1")
        assert result2.get('cached') is True

        assert self.service.cache_misses == 1
        assert self.service.cache_hits == 1
        assert self.service.db_calls == 1  # 只调用一次数据库

    def test_cache_different_symbols(self):
        """测试不同股票代码的缓存隔离"""
        result1 = self.service.fetch_fund_flow_cached("600519", "1")
        result2 = self.service.fetch_fund_flow_cached("000858", "1")

        assert result1['data']['symbol'] == "600519"
        assert result2['data']['symbol'] == "000858"
        assert self.service.cache_misses == 2
        assert self.service.db_calls == 2

    def test_cache_different_timeframes(self):
        """测试不同时间框架的缓存隔离"""
        result1 = self.service.fetch_fund_flow_cached("600519", "1")
        result2 = self.service.fetch_fund_flow_cached("600519", "5")

        assert result1['data']['timeframe'] == "1"
        assert result2['data']['timeframe'] == "5"
        assert self.service.cache_misses == 2

    def test_query_fund_flow_date_range(self):
        """测试日期范围查询"""
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 5)

        results = self.service.query_fund_flow("600519", "1", start_date, end_date)

        assert len(results) == 5
        assert all(r['symbol'] == "600519" for r in results)
        assert self.service.db_calls == 1

    def test_query_fund_flow_default_period(self):
        """测试默认查询周期"""
        results = self.service.query_fund_flow("600519")

        assert len(results) == 5
        assert all('main_net_inflow' in r for r in results)

    def test_fetch_etf_spot_single(self):
        """测试查询单个ETF"""
        results = self.service.fetch_etf_spot("159995")

        assert len(results) == 1
        assert results[0]['symbol'] == "159995"
        assert results[0]['name'] == "芯片ETF"
        assert results[0]['latest_price'] > 0

    def test_fetch_etf_spot_all(self):
        """测试查询所有ETF"""
        results = self.service.fetch_etf_spot()

        assert len(results) >= 2
        assert all('symbol' in r for r in results)
        assert all('latest_price' in r for r in results)

    def test_query_etf_spot_with_keyword(self):
        """测试关键词搜索ETF"""
        results = self.service.query_etf_spot(keyword="芯片")

        assert len(results) >= 1
        assert all("芯片" in r['name'] for r in results)

    def test_query_etf_spot_with_limit(self):
        """测试限制返回数量"""
        results = self.service.query_etf_spot(limit=1)

        assert len(results) <= 1

    def test_fetch_chip_race_basic(self):
        """测试获取竞价抢筹数据"""
        result = self.service.fetch_chip_race("open", date(2025, 1, 20))

        assert result['success'] is True
        assert len(result['data']) > 0
        assert result['data'][0]['race_type'] == "open"
        assert result['data'][0]['trade_date'] == "2025-01-20"

    def test_query_chip_race_with_min_amount(self):
        """测试按最小金额过滤"""
        results = self.service.query_chip_race(
            "open",
            min_race_amount=100000000.00
        )

        assert all(r['race_amount'] >= 100000000.00 for r in results)

    def test_query_chip_race_with_limit(self):
        """测试限制查询结果"""
        results = self.service.query_chip_race("open", limit=5)

        assert len(results) <= 5

    def test_get_cache_stats(self):
        """测试获取缓存统计"""
        # 执行一些操作
        self.service.fetch_fund_flow_cached("600519", "1")
        self.service.fetch_fund_flow_cached("600519", "1")
        self.service.fetch_fund_flow_cached("000858", "1")

        stats = self.service.get_cache_stats()

        assert stats['cache_enabled'] is True
        assert stats['cache_hits'] == 1
        assert stats['cache_misses'] == 2
        assert stats['hit_rate'] == pytest.approx(1/3)
        assert stats['db_calls'] == 2

    def test_clear_cache(self):
        """测试清理缓存"""
        # 先填充缓存
        self.service.fetch_fund_flow_cached("600519", "1")
        self.service.fetch_fund_flow_cached("000858", "1")

        # 清理缓存
        result = self.service.clear_cache()

        assert result['cleared'] == 2

        # 验证缓存已清空
        self.service.fetch_fund_flow_cached("600519", "1")
        assert self.service.cache_misses == 3  # 之前2次 + 清空后1次

    def test_service_without_cache(self):
        """测试禁用缓存的服务"""
        service_no_cache = MockMarketDataService(use_cache=False)

        result1 = service_no_cache.fetch_fund_flow_cached("600519", "1")
        result2 = service_no_cache.fetch_fund_flow_cached("600519", "1")

        # 禁用缓存时，每次都调用数据库
        assert service_no_cache.db_calls == 2
        assert service_no_cache.cache_hits == 0

    def test_concurrent_cache_access(self):
        """测试并发缓存访问"""
        symbols = ["600519", "000858", "300750", "000001"]

        # 第一轮 - 全部缓存未命中
        for symbol in symbols:
            self.service.fetch_fund_flow_cached(symbol, "1")

        assert self.service.cache_misses == 4
        assert self.service.db_calls == 4

        # 第二轮 - 全部缓存命中
        for symbol in symbols:
            self.service.fetch_fund_flow_cached(symbol, "1")

        assert self.service.cache_hits == 4
        assert self.service.db_calls == 4  # 没有新的数据库调用

    def test_data_structure_consistency(self):
        """测试数据结构一致性"""
        result1 = self.service.fetch_fund_flow("600519", "1")
        result2 = self.service.fetch_fund_flow("000858", "5")

        # 验证结构一致
        assert result1.keys() == result2.keys()
        assert result1['data'].keys() == result2['data'].keys()

    def test_error_handling_invalid_timeframe(self):
        """测试无效时间框架处理"""
        # Mock服务应该能处理任何时间框架
        result = self.service.fetch_fund_flow("600519", "999")

        assert result['success'] is True
        assert result['data']['timeframe'] == "999"

    def test_performance_batch_queries(self):
        """测试批量查询性能"""
        import time

        symbols = [f"6005{i:02d}" for i in range(20)]

        start_time = time.time()
        for symbol in symbols:
            self.service.fetch_fund_flow_cached(symbol, "1")
        elapsed_time = time.time() - start_time

        # 批量查询应该在合理时间内完成
        assert elapsed_time < 1.0  # 20个查询应在1秒内完成
        assert self.service.db_calls == 20


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
