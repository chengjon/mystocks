"""Phase 12.3 Real-time MTM Demo
实时盯市演示脚本

演示内容：
1. 创建投资组合
2. 启动 Mock 行情流
3. 自动触发市值重算
4. 实时显示绩效指标

使用方法：
    python scripts/runtime/realtime_mtm_demo.py
"""

import asyncio
import os
import sys


# 确保项目根目录在 path 中
sys.path.append(os.getcwd())

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.application.market_data.price_stream_processor import PriceStreamProcessor
from src.domain.market_data.streaming import PriceChangedEvent
from src.domain.portfolio.model.portfolio import Portfolio
from src.domain.portfolio.service import PortfolioValuationService
from src.infrastructure.market_data.streaming import MockPriceStreamAdapter
from src.infrastructure.messaging.redis_event_bus import RedisEventBus
from src.infrastructure.persistence.repository_impl import PortfolioRepositoryImpl
from src.storage.database.database_manager import Base


async def main():
    """主演示函数"""
    print("=" * 80)
    print("🚀 Phase 12.3 Real-time MTM Demo")
    print("=" * 80)

    # 1. 初始化数据库
    print("\n📊 Step 1: Initializing database...")
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    portfolio_repo = PortfolioRepositoryImpl(session)

    # 2. 创建测试投资组合
    print("\n💼 Step 2: Creating test portfolio...")
    portfolio = Portfolio.create(name="Real-time MTM Portfolio", initial_capital=100000.0)

    # 添加持仓
    test_positions = [
        {"symbol": "000001.SZ", "quantity": 1000, "price": 10.0},
        {"symbol": "600000.SH", "quantity": 500, "price": 20.0},
        {"symbol": "000002.SZ", "quantity": 2000, "price": 5.0},
    ]

    for pos in test_positions:
        # 模拟订单成交事件
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
    print("   Positions:")
    for symbol, pos in portfolio.positions.items():
        print(f"     - {symbol}: {pos.quantity} shares @ ¥{pos.average_cost:.2f}")

    # 3. 创建服务
    print("\n🔧 Step 3: Initializing services...")
    valuation_service = PortfolioValuationService(portfolio_repo)

    # 尝试创建 Redis 事件总线（如果可用）
    try:
        redis_event_bus = RedisEventBus(host="localhost", port=6379, db=0)
        print("✅ Redis Event Bus connected")
    except Exception as e:
        print(f"⚠️ Redis not available: {e}")
        print("   Using mock event bus instead...")
        redis_event_bus = None

    # 4. 创建价格流处理器
    processor = PriceStreamProcessor(
        event_bus=redis_event_bus or type("MockEventBus", (), {"publish": lambda self, e: None})(),
        valuation_service=valuation_service,
        batch_size=10,
        batch_timeout=0.5,
    )

    # 5. 创建 Mock 行情流适配器
    adapter = MockPriceStreamAdapter(update_interval=0.5, price_volatility=0.05)
    processor.add_stream_adapter(adapter)

    # 6. 订阅价格变更事件
    events_received = []

    def on_price_changed(event: PriceChangedEvent):
        events_received.append(event)
        print(
            f"📈 Price update: {event.symbol} ¥{event.old_price:.2f} → ¥{event.new_price:.2f} ({event.price_change_pct:+.2f}%)"
        )

    if redis_event_bus:
        redis_event_bus.subscribe(PriceChangedEvent, on_price_changed)

    # 7. 注册投资组合
    symbols = set(portfolio.positions.keys())
    processor.register_portfolio_symbols(portfolio.id, symbols)

    print(f"✅ Registered portfolio {portfolio.id} with symbols: {symbols}")

    # 8. 启动实时流
    print("\n🎯 Step 4: Starting real-time price stream...")
    await adapter.connect()  # 先连接适配器
    await processor.start()  # 启动处理器
    await adapter.subscribe(list(symbols))  # 订阅股票

    # 9. 运行演示
    print("\n⏱️ Running for 5 seconds...")
    print("-" * 80)

    for i in range(5):
        await asyncio.sleep(1.0)

        # 获取最新投资组合状态
        current_portfolio = portfolio_repo.find_by_id(portfolio.id)

        # 调试：打印持仓的原始数据
        print("\n🔍 [DEBUG] Portfolio positions data:")
        for symbol, pos in current_portfolio.positions.items():
            print(
                f"   {symbol}: quantity={pos.quantity}, average_cost={pos.average_cost}, current_price={pos.current_price}"
            )

        # 手动计算绩效（简化版）
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

        # 显示持仓详情
        print("   Positions:")
        for symbol, pos in current_portfolio.positions.items():
            unrealized_pnl = (pos.current_price - pos.average_cost) * pos.quantity
            pnl_pct = ((pos.current_price - pos.average_cost) / pos.average_cost) * 100
            print(
                f"     - {symbol}: {pos.quantity} shares @ ¥{pos.current_price:.2f} | P&L: ¥{unrealized_pnl:,.2f} ({pnl_pct:+.2f}%)"
            )

    print("-" * 80)

    # 10. 停止服务
    print("\n🛑 Stopping services...")
    await processor.stop()

    # 11. 显示最终统计
    print("\n📈 Final Statistics:")
    print(f"   Total price updates: {len(events_received)}")
    print(f"   Updates per second: {len(events_received) / 10:.1f}")

    processor_metrics = processor.get_metrics()
    print("   Processor metrics:")
    print(f"     - Total updates: {processor_metrics['total_updates']}")
    print(f"     - Events published: {processor_metrics['events_published']}")
    print(f"     - Portfolio revaluations: {processor_metrics['portfolio_revaluations']}")

    service_metrics = valuation_service.get_metrics()
    print("   Valuation service metrics:")
    print(f"     - Total revaluations: {service_metrics['total_revaluations']}")
    print(f"     - Successful: {service_metrics['successful_revaluations']}")
    print(f"     - Conflicts: {service_metrics['concurrency_conflicts']}")
    print(f"     - Success rate: {service_metrics['success_rate']:.1%}")

    # 13. 显示最终投资组合状态
    final_portfolio = portfolio_repo.find_by_id(portfolio.id)

    # 手动计算绩效（简化版）
    holdings_value = sum(p.quantity * p.current_price for p in final_portfolio.positions.values())
    total_value = final_portfolio.cash + holdings_value
    total_return = total_value - final_portfolio.initial_capital
    return_rate = (total_return / final_portfolio.initial_capital) * 100 if final_portfolio.initial_capital > 0 else 0

    print("\n💰 Final Portfolio Value:")
    print(f"   Initial: ¥{final_portfolio.initial_capital:,.2f}")
    print(f"   Final: ¥{total_value:,.2f}")
    print(f"   Profit/Loss: ¥{total_return:,.2f} ({return_rate:.2f}%)")

    print("\n✅ Demo completed successfully!")
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
