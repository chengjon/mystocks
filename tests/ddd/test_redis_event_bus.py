"""
Verification Script for Redis Event Bus
验证 Redis 事件总线的异步分发与反序列化
"""
import sys
import os
import time
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# 确保项目根目录在 path 中
sys.path.append(os.getcwd())

from src.storage.database.database_manager import Base
from src.application.bootstrap import bootstrap_app
from src.domain.trading.events import OrderFilledEvent
from src.domain.trading.value_objects import OrderSide
from src.domain.portfolio.model.portfolio import Portfolio
from datetime import datetime

def test_redis_integration():
    """
    验证 Redis 事件总线。需要本地运行 Redis 服务。
    """
    # 1. 强制使用 Redis
    os.environ["EVENT_BUS_TYPE"] = "REDIS"
    
    # 2. 准备 DB - 开启 check_same_thread=False 以支持多线程监听
    engine = create_engine(
        "sqlite:///test_ddd.db", 
        connect_args={"check_same_thread": False}
    )
    Base.metadata.drop_all(engine) # 清理旧数据
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 3. 引导系统
    container = bootstrap_app(session)
    
    # 4. 创建测试数据
    p = Portfolio.create(name="Redis Test Fund", initial_capital=100000.0)
    container.portfolio_repo.save(p)
    session.commit()
    print(f"\n[Init] Created Portfolio: {p.name}, Cash: {p.cash}")
    
    # 5. 发布事件 (模拟从另一个服务发来的成交)
    event = OrderFilledEvent(
        order_id="test_o1",
        symbol="600519",
        filled_quantity=100,
        filled_price=1800.0,
        side=OrderSide.BUY,
        commission=5.0,
        filled_at=datetime.now(),
        is_fully_filled=True
    )
    
    print(f"Publishing event to Redis: {event.event_name()}")
    container.event_bus.publish(event)
    
    # 6. 等待异步处理
    print("Waiting 3 seconds for async processing...")
    time.sleep(3.0)
    
    # 7. 验证结果
    # 注意：后台线程修改了 DB，我们需要刷新 session
    session.expire_all()
    updated_p = container.portfolio_repo.get_by_id(p.id)
    
    print(f"Final Cash: {updated_p.cash}")
    print(f"Positions: {list(updated_p.positions.keys())}")
    
    # 停止监听线程
    if hasattr(container.event_bus, 'stop'):
        container.event_bus.stop()

    if len(updated_p.positions) > 0:
        print("\n✅ Success: Portfolio updated asynchronously via Redis Event Bus!")
    else:
        print("\n❌ Failure: Portfolio not updated. Check Redis status and logs.")

if __name__ == "__main__":
    test_redis_integration()