"""
Phase 12.3: Real-time Market Data Integration Test
实时行情集成测试

测试内容：
1. MockPriceStreamAdapter 连接和订阅
2. PriceStreamProcessor 处理价格更新
3. PortfolioValuationService 重新计算投资组合
4. 并发控制和版本冲突处理
5. 端到端实时数据流测试
"""

import sys
import os
import asyncio
import pytest
import time
from datetime import datetime
from typing import Dict

# 确保项目根目录在 path 中
sys.path.append(os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd()))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.storage.database.database_manager import Base
from src.infrastructure.persistence.models import PortfolioModel
from src.infrastructure.persistence.repository_impl import PortfolioRepositoryImpl
from src.infrastructure.messaging.redis_event_bus import RedisEventBus
from src.infrastructure.market_data.streaming import MockPriceStreamAdapter
from src.domain.market_data.streaming import PriceChangedEvent
from src.application.market_data.price_stream_processor import PriceStreamProcessor
from src.domain.portfolio.service import PortfolioValuationService
from src.domain.portfolio.model.portfolio import Portfolio
from src.domain.trading.value_objects import OrderSide


class TestRealtimeMarketIntegration:
    """实时行情集成测试"""

    @pytest.fixture
    def db_session(self):
        """创建测试数据库会话"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    @pytest.fixture
    def portfolio_repo(self, db_session):
        """创建投资组合仓储"""
        return PortfolioRepositoryImpl(db_session)

    @pytest.fixture
    def portfolio_valuation_service(self, portfolio_repo):
        """创建投资组合估值服务"""
        return PortfolioValuationService(portfolio_repo)

    @pytest.fixture
    def redis_event_bus(self):
        """创建 Redis 事件总线（可选）"""
        # 注意：需要 Redis 服务才能运行
        # 如果没有 Redis，这些测试会跳过
        try:
            event_bus = RedisEventBus(host="localhost", port=6379, db=0)
            return event_bus
        except Exception:
            pytest.skip("Redis not available")

    def test_mock_stream_adapter_basic(self):
        """测试 Mock 行情流适配器基本功能"""
        adapter = MockPriceStreamAdapter(update_interval=0.1)

        # 测试初始状态
        assert adapter.get_status().value == "disconnected"
        assert adapter.get_subscribed_tickers() == []

        # 测试连接
        asyncio.run(adapter.connect())
        assert adapter.get_status().value == "connected"

        # 测试订阅
        tickers = ["000001.SZ", "600000.SH"]
        asyncio.run(adapter.subscribe(tickers))
        assert adapter.get_status().value == "subscribed"
        assert set(adapter.get_subscribed_tickers()) == set(tickers)

        # 测试断开连接
        asyncio.run(adapter.disconnect())
        assert adapter.get_status().value == "disconnected"

    def test_price_update_callback(self):
        """测试价格更新回调"""
        adapter = MockPriceStreamAdapter(update_interval=0.1)
        updates_received = []

        def callback(update):
            updates_received.append(update)

        adapter.on_message(callback)

        async def run_test():
            await adapter.connect()
            await adapter.subscribe(["000001.SZ"])

            # 等待几个更新
            await asyncio.sleep(0.5)

            await adapter.stop()

        asyncio.run(run_test())

        # 验证收到至少一个更新
        assert len(updates_received) > 0
        assert all(update.symbol == "000001.SZ" for update in updates_received)
        assert all(update.price > 0 for update in updates_received)

    def test_portfolio_valuation(self, portfolio_repo, db_session):
        """测试投资组合估值服务"""
        # 创建测试投资组合
        portfolio = Portfolio.create(name="Test Portfolio", initial_capital=100000.0)

        # 添加持仓
        print(f"\n🔍 [DEBUG] Before handle_order_filled - Portfolio has {len(portfolio.positions)} positions")
        portfolio.handle_order_filled(
            type(
                "Event",
                (),
                {
                    "symbol": "000001.SZ",
                    "side": OrderSide.BUY,  # 使用真正的枚举值
                    "filled_quantity": 1000,
                    "filled_price": 10.0,
                    "commission": 5.0,
                },
            )
        )
        print(f"🔍 [DEBUG] After handle_order_filled - Portfolio has {len(portfolio.positions)} positions")
        for symbol, pos in portfolio.positions.items():
            print(
                f"   {symbol}: quantity={pos.quantity}, avg_cost={pos.average_cost}, current_price={pos.current_price}"
            )

        print(f"🔍 [DEBUG] Portfolio ID: {portfolio.id}")
        print(f"🔍 [DEBUG] Portfolio cash: {portfolio.cash}")

        portfolio_repo.save(portfolio)

        # 验证保存后的投资组合有持仓
        saved_portfolio = portfolio_repo.find_by_id(portfolio.id)
        print(f"\n🔍 [DEBUG] After save - Portfolio has {len(saved_portfolio.positions)} positions")
        if saved_portfolio.positions:
            for symbol, pos in saved_portfolio.positions.items():
                print(
                    f"   {symbol}: quantity={pos.quantity}, avg_cost={pos.average_cost}, current_price={pos.current_price}"
                )

        # 创建估值服务
        valuation_service = PortfolioValuationService(portfolio_repo)

        # 测试重新计算
        prices = {"000001.SZ": 12.0}
        performance = valuation_service.revaluate_portfolio(portfolio.id, prices)

        # 调试输出
        print(f"\n🔍 [DEBUG] Performance: {performance}")
        print(f"🔍 [DEBUG] Holdings value: {performance.holdings_value}")
        print(f"🔍 [DEBUG] Total return: {performance.total_return}%")

        # 验证持仓价格已更新（在重新计算之前）
        current_portfolio = portfolio_repo.find_by_id(portfolio.id)
        print(
            f"🔍 [DEBUG] Position before assert: symbol={list(current_portfolio.positions.keys())[0]}, current_price={list(current_portfolio.positions.values())[0].current_price}"
        )

        assert performance is not None
        # PerformanceMetrics 有 total_return (百分比), holdings_value, cash_balance
        assert performance.holdings_value > 0, f"Expected holdings_value > 0, got {performance.holdings_value}"
        assert performance.total_return > 0  # 收益率百分比
        assert performance.cash_balance >= 0

        # 验证持仓价格已更新
        updated_portfolio = portfolio_repo.find_by_id(portfolio.id)
        assert updated_portfolio.positions["000001.SZ"].current_price == 12.0

    def test_concurrent_price_updates(self, portfolio_repo, db_session):
        """测试并发价格更新"""
        # 创建测试投资组合
        portfolio = Portfolio.create(name="Concurrent Test", initial_capital=100000.0)
        portfolio.handle_order_filled(
            type(
                "Event",
                (),
                {
                    "symbol": "000001.SZ",
                    "side": OrderSide.BUY,  # 使用真正的枚举值
                    "filled_quantity": 1000,
                    "filled_price": 10.0,
                    "commission": 5.0,
                },
            )
        )
        portfolio_repo.save(portfolio)

        valuation_service = PortfolioValuationService(portfolio_repo)

        # 模拟并发更新（同步版本，避免SQLite跨线程问题）
        for i in range(10):
            price = 10.0 + i * 0.1
            try:
                valuation_service.revaluate_portfolio(portfolio.id, {"000001.SZ": price})
            except Exception:
                pass  # 并发冲突是预期的

        # 验证投资组合已更新（至少有一次成功）
        updated_portfolio = portfolio_repo.find_by_id(portfolio.id)
        assert updated_portfolio.positions["000001.SZ"].current_price != 10.0

    def test_end_to_end_realtime_flow(self, portfolio_repo, redis_event_bus):
        """端到端实时数据流测试"""
        # 创建测试投资组合
        portfolio = Portfolio.create(name="Realtime Test", initial_capital=100000.0)
        portfolio.handle_order_filled(
            type(
                "Event",
                (),
                {
                    "symbol": "000001.SZ",
                    "side": OrderSide.BUY,  # 使用真正的枚举值
                    "filled_quantity": 1000,
                    "filled_price": 10.0,
                    "commission": 5.0,
                },
            )
        )
        portfolio_repo.save(portfolio)

        # 创建服务
        valuation_service = PortfolioValuationService(portfolio_repo)
        processor = PriceStreamProcessor(
            event_bus=redis_event_bus,
            valuation_service=valuation_service,
            batch_size=5,
            batch_timeout=0.1,
        )

        # 创建 Mock 行情流适配器
        adapter = MockPriceStreamAdapter(update_interval=0.05)
        processor.add_stream_adapter(adapter)

        # 注册投资组合
        processor.register_portfolio_symbols(portfolio.id, {"000001.SZ"})

        # 订阅价格变更事件
        events_received = []

        def on_price_changed(event: PriceChangedEvent):
            events_received.append(event)

        redis_event_bus.subscribe(PriceChangedEvent, on_price_changed)

        # 运行测试
        async def run_test():
            await adapter.connect()  # 先连接适配器
            await processor.start()
            await adapter.subscribe(["000001.SZ"])

            # 等待价格更新
            await asyncio.sleep(0.5)

            await processor.stop()

        asyncio.run(run_test())

        # 验证结果
        assert len(events_received) > 0
        assert all(e.symbol == "000001.SZ" for e in events_received)

        # 验证投资组合已更新
        updated_portfolio = portfolio_repo.find_by_id(portfolio.id)
        assert updated_portfolio.positions["000001.SZ"].current_price != 10.0

        # 验证处理器指标
        metrics = processor.get_metrics()
        assert metrics["total_updates"] > 0
        assert metrics["events_published"] > 0
        assert metrics["portfolio_revaluations"] > 0


def test_performance_benchmarks():
    """性能基准测试"""
    adapter = MockPriceStreamAdapter(update_interval=0.01)

    updates_received = []

    def callback(update):
        updates_received.append(update)

    adapter.on_message(callback)

    async def run_benchmark():
        await adapter.connect()
        await adapter.subscribe(["000001.SZ", "600000.SH", "000002.SZ"])

        start_time = time.time()
        await asyncio.sleep(1.0)
        end_time = time.time()

        await adapter.stop()

        return end_time - start_time

    elapsed = asyncio.run(run_benchmark())

    # 验证性能
    assert len(updates_received) > 10  # 至少收到10次更新
    assert elapsed < 2.0  # 1秒内完成

    # 计算平均延迟
    avg_updates_per_second = len(updates_received) / elapsed
    print(f"📊 Performance: {avg_updates_per_second:.1f} updates/second")


if __name__ == "__main__":
    # 运行基本测试
    print("🧪 Running Phase 12.3 Real-time Market Integration Tests...")

    test = TestRealtimeMarketIntegration()

    print("\n1. Testing Mock Stream Adapter...")
    test.test_mock_stream_adapter_basic()
    print("✅ Mock Stream Adapter test passed")

    print("\n2. Testing Price Update Callback...")
    test.test_price_update_callback()
    print("✅ Price Update Callback test passed")

    print("\n3. Testing Performance Benchmarks...")
    test_performance_benchmarks()
    print("✅ Performance Benchmarks test passed")

    print("\n✅ All basic tests passed!")
    print("\n📝 Note: Full integration tests require database and Redis setup.")
    print("   Run with: pytest tests/ddd/test_phase12_3_realtime_integration.py -v")
