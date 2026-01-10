"""
DDD 全链路集成演示脚本 (Phase 11)
验证: API -> Application -> Domain -> Event Bus -> Cross Context Portfolio Update

功能：
1. 创建投资组合
2. 通过应用服务下达订单
3. 模拟成交回报
4. 验证事件总线触发 Portfolio 更新

执行方式：
```bash
python scripts/ddd_full_chain_demo.py
```
"""

import sys
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent))


def run_demo():
    """
    全链路集成演示

    流程：
    1. 初始化数据库和会话
    2. 引导系统 (创建容器，注册事件处理器)
    3. 创建投资组合
    4. 下达买入订单
    5. 处理成交回报 (触发领域事件)
    6. 发布事件到总线
    7. 验证 Portfolio 更新
    """
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    from src.storage.database.database_manager import Base
    from src.application.bootstrap import DIContainer
    from src.application.dto.trading_dto import CreateOrderRequest
    from src.domain.portfolio.model.portfolio import Portfolio
    from src.domain.trading.value_objects import OrderId

    print("\n" + "=" * 70)
    print("MyStocks DDD 全链路集成演示")
    print("=" * 70)

    engine = create_engine("sqlite:///./ddd_demo.db", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    container = None
    try:
        container = DIContainer(db_url="sqlite:///./ddd_demo.db")
        container._db_url = "sqlite:///./ddd_demo.db"
        container._engine = engine
        container._session_factory = Session
        container._setup_event_bus()
        container._create_repositories()
        container._create_services()
        container._initialized = True

        portfolio = None
        order_id = None

        print("\n" + "=" * 70)
        print("步骤 1: 创建投资组合")
        print("=" * 70)

        portfolio = Portfolio.create(name="DDD Demo Fund", initial_capital=1000000.0)
        container.portfolio_repository.save(portfolio)

        print(f"  投资组合 ID: {portfolio.id}")
        print(f"  投资组合名称: {portfolio.name}")
        print(f"  初始资金: {portfolio.cash:.2f}")
        print(f"  持仓数量: {len(portfolio.positions)}")

        assert portfolio.cash == 1000000.0, "初始资金应为 1000000"
        logger.info("步骤 1 完成: 投资组合创建成功")

        print("\n" + "=" * 70)
        print("步骤 2: 下达买入订单")
        print("=" * 70)

        order_req = CreateOrderRequest(symbol="600519", quantity=100, side="BUY", order_type="LIMIT", price=1800.0)

        order_resp = container.order_service.place_order(order_req)
        order_id = order_resp.order_id

        print(f"  订单 ID: {order_id}")
        print(f"  标的: {order_resp.symbol}")
        print(f"  数量: {order_resp.quantity}")
        print(f"  方向: {order_resp.side}")
        print(f"  价格: {order_resp.price}")
        print(f"  状态: {order_resp.status}")

        assert order_resp.status == "SUBMITTED", "订单状态应为 SUBMITTED"
        logger.info("步骤 2 完成: 订单下达成功")

        print("\n" + "=" * 70)
        print("步骤 3: 处理成交回报 (核心：触发领域事件)")
        print("=" * 70)

        order_obj = container.order_repository.get_by_id(OrderId(order_id))
        print(f"  订单 ID: {order_id}")
        print(f"  成交数量: 100")
        print(f"  成交价格: 1800.00")

        container.order_service.handle_execution_report(order_id=order_id, filled_qty=100, price=1800.0)

        order_obj = container.order_repository.get_by_id(OrderId(order_id))
        print(f"  检查 Order 对象的事件缓冲区...")
        print(f"    - has _domain_events: {hasattr(order_obj, '_domain_events')}")
        if hasattr(order_obj, "_domain_events"):
            print(f"    - _domain_events 长度: {len(order_obj._domain_events)}")

        events = (
            order_obj.collect_domain_events()
            if hasattr(order_obj, "_domain_events") and order_obj._domain_events
            else []
        )
        print(f"  收集到 {len(events)} 个领域事件")

        for event in events:
            print(f"    - {event.event_name()}")
            print(f"      发布到事件总线...")
            container.event_bus.publish(event)

        logger.info("步骤 3 完成: 成交回报处理成功")

        print("\n" + "=" * 70)
        print("步骤 4: 验证 Portfolio 更新")
        print("=" * 70)

        updated_p = container.portfolio_repository.get_by_id(portfolio.id)

        print(f"  投资组合 ID: {updated_p.id}")
        print(f"  当前现金: {updated_p.cash:.2f}")
        print(f"  持仓数量: {len(updated_p.positions)}")

        if "600519" in updated_p.positions:
            pos = updated_p.positions["600519"]
            print(f"  标的 600519:")
            print(f"    - 持仓数量: {pos.quantity}")
            print(f"    - 平均成本: {pos.average_cost:.2f}")
            print(f"  交易流水数量: {len(updated_p.transactions)}")
        else:
            print("  警告: 未找到 600519 持仓")

        assert "600519" in updated_p.positions, "应持有 600519"
        assert updated_p.positions["600519"].quantity == 100, "持仓数量应为 100"
        assert len(updated_p.transactions) >= 1, "应有交易流水"

        logger.info("步骤 4 完成: 事件总线正确触发了 Portfolio 更新")

        print("\n" + "=" * 70)
        print("步骤 5: 验证数据库持久化")
        print("=" * 70)

        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM ddd_portfolios"))
            portfolio_count = result.fetchone()[0]
            print(f"  投资组合表记录数: {portfolio_count}")

            result = conn.execute(text("SELECT COUNT(*) FROM ddd_orders"))
            order_count = result.fetchone()[0]
            print(f"  订单表记录数: {order_count}")

            result = conn.execute(text("SELECT COUNT(*) FROM ddd_transactions"))
            transaction_count = result.fetchone()[0]
            print(f"  交易流水表记录数: {transaction_count}")

        assert portfolio_count >= 1, "投资组合应已持久化"
        assert order_count >= 1, "订单应已持久化"
        assert transaction_count >= 1, "交易流水应已持久化"

        logger.info("步骤 5 完成: 数据已正确持久化")

        print("\n" + "=" * 70)
        print("全链路集成演示成功完成！")
        print("=" * 70)
        print("\n关键验证点:")
        print("  ✓ 投资组合创建成功")
        print("  ✓ 订单下达成功")
        print("  ✓ 成交回报处理成功")
        print("  ✓ 领域事件正确发布到事件总线")
        print("  ✓ 事件总线触发 Portfolio 更新")
        print("  ✓ 数据持久化成功")
        print("\n系统架构验证通过！")

        return True

    except Exception as e:
        logger.error(f"演示失败: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        if container:
            try:
                container.shutdown()
            except:
                pass


if __name__ == "__main__":
    success = run_demo()
    sys.exit(0 if success else 1)
