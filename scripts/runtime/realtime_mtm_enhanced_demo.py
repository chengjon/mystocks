"""Phase 12.4 + 12.5: Enhanced Real-time MTM Demo
增强版实时盯市演示脚本

演示内容：
1. Phase 12.4: API 层集成 DDD 架构
2. Phase 12.5: 性能优化集成（LRU 缓存 + 增量计算）
3. 对比基准性能与优化后性能

使用方法：
    python scripts/runtime/realtime_mtm_enhanced_demo.py
"""

import asyncio
import os
import sys
import time


# 确保项目根目录在 path 中
sys.path.append(os.getcwd())

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.application.market_data.price_stream_processor_cached import CachedPriceStreamProcessor
from src.domain.portfolio.model.portfolio import Portfolio
from src.domain.portfolio.service.portfolio_valuation_service import PortfolioValuationService
from src.domain.portfolio.service.portfolio_valuation_service_optimized import OptimizedPortfolioValuationService
from src.infrastructure.market_data.streaming import MockPriceStreamAdapter
from src.infrastructure.persistence.repository_impl import PortfolioRepositoryImpl
from src.storage.database.database_manager import Base


class PerformanceBenchmark:
    """性能基准测试"""

    def __init__(self):
        self.results = {}

    def measure(self, name: str, func):
        """测量函数执行时间"""
        start = time.time()
        result = func()
        elapsed = time.time() - start
        self.results[name] = {
            "elapsed": elapsed,
            "result": result,
        }
        return result


async def demo_baseline_performance():
    """演示基准性能（Phase 12.3）"""
    print("\n" + "=" * 80)
    print("📊 Phase 12.3: Baseline Performance (No Cache)")
    print("=" * 80)

    # 初始化数据库
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    portfolio_repo = PortfolioRepositoryImpl(session)
    valuation_service = PortfolioValuationService(portfolio_repo)

    # 创建测试投资组合
    portfolio = Portfolio.create(name="Baseline Portfolio", initial_capital=100000.0)

    # 添加多个持仓以测试性能
    test_positions = [
        {"symbol": "000001.SZ", "quantity": 1000, "price": 10.0},
        {"symbol": "600000.SH", "quantity": 500, "price": 20.0},
        {"symbol": "000002.SZ", "quantity": 2000, "price": 5.0},
        {"symbol": "000004.SZ", "quantity": 1500, "price": 8.0},
        {"symbol": "600004.SH", "quantity": 800, "price": 15.0},
    ]

    for pos in test_positions:
        from src.domain.trading.value_objects import OrderSide

        class MockEvent:
            def __init__(self, symbol, quantity, price):
                self.symbol = symbol
                self.side = OrderSide.BUY
                self.filled_quantity = quantity
                self.filled_price = price
                self.commission = 5.0

        event = MockEvent(pos["symbol"], pos["quantity"], pos["price"])
        portfolio.handle_order_filled(event)

    portfolio_repo.save(portfolio)

    print(f"✅ Portfolio created: {portfolio.id}")
    print(f"   Positions: {len(portfolio.positions)}")

    # 性能测试：连续更新价格
    print("\n⏱️ Testing price updates (10 iterations)...")
    start = time.time()

    for i in range(10):
        # 模拟价格更新
        prices = {pos["symbol"]: pos["price"] * (1 + 0.01 * i) for pos in test_positions}
        performance = valuation_service.revaluate_portfolio(portfolio.id, prices)

        if i % 5 == 0:
            print(f"   [{i + 1}/10] Holdings value: ¥{performance.holdings_value:,.2f}")

    elapsed_baseline = time.time() - start
    print(f"\n⏱️ Total time: {elapsed_baseline:.3f}s")
    print(f"   Average per update: {elapsed_baseline / 10 * 1000:.2f}ms")

    return elapsed_baseline


async def demo_optimized_performance():
    """演示优化后性能（Phase 12.5）"""
    print("\n" + "=" * 80)
    print("🚀 Phase 12.5: Optimized Performance (LRU Cache + Incremental Calculation)")
    print("=" * 80)

    # 初始化数据库
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    portfolio_repo = PortfolioRepositoryImpl(session)

    # 使用优化版估值服务
    valuation_service = OptimizedPortfolioValuationService(portfolio_repo, enable_incremental=True)

    # 创建测试投资组合
    portfolio = Portfolio.create(name="Optimized Portfolio", initial_capital=100000.0)

    # 添加多个持仓
    test_positions = [
        {"symbol": "000001.SZ", "quantity": 1000, "price": 10.0},
        {"symbol": "600000.SH", "quantity": 500, "price": 20.0},
        {"symbol": "000002.SZ", "quantity": 2000, "price": 5.0},
        {"symbol": "000004.SZ", "quantity": 1500, "price": 8.0},
        {"symbol": "600004.SH", "quantity": 800, "price": 15.0},
    ]

    for pos in test_positions:
        from src.domain.trading.value_objects import OrderSide

        class MockEvent:
            def __init__(self, symbol, quantity, price):
                self.symbol = symbol
                self.side = OrderSide.BUY
                self.filled_quantity = quantity
                self.filled_price = price
                self.commission = 5.0

        event = MockEvent(pos["symbol"], pos["quantity"], pos["price"])
        portfolio.handle_order_filled(event)

    portfolio_repo.save(portfolio)

    print(f"✅ Portfolio created: {portfolio.id}")
    print(f"   Positions: {len(portfolio.positions)}")

    # 性能测试：连续更新价格
    print("\n⏱️ Testing price updates (10 iterations)...")
    start = time.time()

    for i in range(10):
        # 模拟价格更新（只更新部分持仓）
        symbols_to_update = [pos["symbol"] for pos in test_positions[:3]]  # 只更新前3个
        prices = dict.fromkeys(symbols_to_update, test_positions[0]["price"] * (1 + 0.01 * i))

        performance = valuation_service.revaluate_portfolio(portfolio.id, prices)

        if i % 5 == 0:
            print(f"   [{i + 1}/10] Holdings value: ¥{performance.holdings_value:,.2f}")

    elapsed_optimized = time.time() - start
    print(f"\n⏱️ Total time: {elapsed_optimized:.3f}s")
    print(f"   Average per update: {elapsed_optimized / 10 * 1000:.2f}ms")

    # 显示优化指标
    metrics = valuation_service.get_metrics()
    print("\n📊 Optimization Metrics:")
    print(f"   Incremental updates: {metrics.get('incremental_updates', 0)}")
    print(f"   Full recalculations: {metrics.get('full_recalculations', 0)}")
    print(f"   Incremental ratio: {metrics.get('incremental_ratio', 0):.1%}")
    print(f"   Time saved: {metrics.get('calculation_time_saved_ms', 0):.2f}ms")

    return elapsed_optimized


async def demo_cached_processor():
    """演示带缓存的处理器（Phase 12.5）"""
    print("\n" + "=" * 80)
    print("💾 Phase 12.5: Cached Price Stream Processor")
    print("=" * 80)

    # 初始化数据库
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    portfolio_repo = PortfolioRepositoryImpl(session)

    # 创建带缓存的处理器
    try:
        from src.infrastructure.messaging.redis_event_bus import RedisEventBus

        event_bus = RedisEventBus(host="localhost", port=6379, db=0)
        print("✅ Redis Event Bus connected")
    except Exception as e:
        print(f"⚠️ Redis not available: {e}")
        event_bus = None

    valuation_service = PortfolioValuationService(portfolio_repo)

    processor = CachedPriceStreamProcessor(
        event_bus=event_bus or type("MockEventBus", (), {"publish": lambda self, e: None})(),
        valuation_service=valuation_service,
        batch_size=10,
        batch_timeout=0.5,
        enable_cache=True,  # 启用缓存
        cache_max_size=100,
        cache_ttl=300.0,
    )

    # 创建 Mock 行情流
    adapter = MockPriceStreamAdapter(update_interval=0.5, price_volatility=0.05)
    processor.add_stream_adapter(adapter)

    # 创建测试投资组合
    portfolio = Portfolio.create(name="Cached Test Portfolio", initial_capital=100000.0)

    # 添加持仓
    test_positions = [
        {"symbol": "000001.SZ", "quantity": 1000, "price": 10.0},
        {"symbol": "600000.SH", "quantity": 500, "price": 20.0},
        {"symbol": "000002.SZ", "quantity": 2000, "price": 5.0},
    ]

    for pos in test_positions:
        from src.domain.trading.value_objects import OrderSide

        class MockEvent:
            def __init__(self, symbol, quantity, price):
                self.symbol = symbol
                self.side = OrderSide.BUY
                self.filled_quantity = quantity
                self.filled_price = price
                self.commission = 5.0

        event = MockEvent(pos["symbol"], pos["quantity"], pos["price"])
        portfolio.handle_order_filled(event)

    portfolio_repo.save(portfolio)

    print(f"✅ Portfolio created: {portfolio.id}")
    print(f"   Initial capital: ¥{portfolio.initial_capital:,.2f}")

    # 注册投资组合
    symbols = set(portfolio.positions.keys())
    processor.register_portfolio_symbols(portfolio.id, symbols)

    # 启动处理器
    await adapter.connect()
    await processor.start()
    await adapter.subscribe(list(symbols))

    # 运行演示
    print("\n⏱️ Running for 3 seconds...")
    print("-" * 80)

    for i in range(3):
        await asyncio.sleep(1.0)

        # 获取最新投资组合状态
        current_portfolio = portfolio_repo.find_by_id(portfolio.id)

        # 计算绩效
        holdings_value = sum(p.quantity * p.current_price for p in current_portfolio.positions.values())
        total_value = current_portfolio.cash + holdings_value
        total_return = total_value - current_portfolio.initial_capital
        return_rate = (
            (total_return / current_portfolio.initial_capital) * 100 if current_portfolio.initial_capital > 0 else 0
        )

        print(f"\n📊 [{i + 1}s] Portfolio Performance:")
        print(f"   Total Value: ¥{total_value:,.2f}")
        print(f"   Total Return: ¥{total_return:,.2f}")
        print(f"   Return Rate: {return_rate:.2f}%")

    print("-" * 80)

    # 停止处理器
    await processor.stop()

    # 显示缓存指标
    metrics = processor.get_metrics()
    print("\n💾 Cache Metrics:")
    print(f"   Cache hits: {metrics.get('cache_hits', 0)}")
    print(f"   Cache misses: {metrics.get('cache_misses', 0)}")
    print(f"   Cache hit rate: {metrics.get('cache_hit_rate', 0):.1%}")
    print(f"   Cache size: {metrics.get('cache_size', 0)}/{metrics.get('cache_max_size', 0)}")

    print("\n✅ Cached processor demo completed!")


async def main():
    """主演示函数"""
    print("=" * 80)
    print("🚀 Phase 12.4 + 12.5: Enhanced Real-time MTM Demo")
    print("=" * 80)

    # 1. 基准性能测试
    baseline_time = await demo_baseline_performance()

    # 2. 优化后性能测试
    optimized_time = await demo_optimized_performance()

    # 3. 性能对比
    print("\n" + "=" * 80)
    print("📊 Performance Comparison")
    print("=" * 80)
    print(f"Baseline (no cache):      {baseline_time:.3f}s")
    print(f"Optimized (cache + inc):  {optimized_time:.3f}s")
    print(f"Improvement:              {(baseline_time - optimized_time) / baseline_time * 100:.1f}% faster")

    # 4. 缓存处理器演示
    await demo_cached_processor()

    print("\n" + "=" * 80)
    print("✅ Phase 12.4 + 12.5 Demo completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
