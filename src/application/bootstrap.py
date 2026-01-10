"""
DDD Bootstrap & Composition Root
负责系统运行态的依赖注入、事件订阅和环境初始化
"""
import logging
import os
import redis
from sqlalchemy.orm import Session
from src.infrastructure.persistence.repository_impl import (
    StrategyRepositoryImpl, 
    OrderRepositoryImpl, 
    PortfolioRepositoryImpl,
    TradingPositionRepositoryImpl
)
from src.infrastructure.messaging.local_event_bus import LocalEventBus
from src.infrastructure.messaging.redis_event_bus import RedisEventBus
from src.infrastructure.market_data.adapter import DataSourceV2Adapter
from src.infrastructure.calculation.gpu_calculator import GPUIndicatorCalculator
from src.infrastructure.cache.redis_lock import RedisDistributedLock

from src.application.strategy.backtest_service import BacktestApplicationService
from src.application.trading.order_mgmt_service import OrderManagementService
from src.domain.strategy.service import SignalGenerationService
from src.domain.trading.events import OrderFilledEvent

logger = logging.getLogger(__name__)

class AppContainer:
    """
    简单的依赖容器 (Composition Root)
    """
    def __init__(self, db_session: Session):
        self.db_session = db_session
        
        # Redis 客户端初始化 (复用于总线和锁)
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )
        
        # 1. 基础设施实现 - 根据配置选择事件总线
        bus_type = os.getenv("EVENT_BUS_TYPE", "LOCAL").upper()
        if bus_type == "REDIS":
            self.event_bus = RedisEventBus(
                redis_client=self.redis_client
            )
            logger.info("Using Distributed Redis Event Bus")
        else:
            self.event_bus = LocalEventBus()
            logger.info("Using Synchronous Local Event Bus")

        # 初始化分布式锁
        self.dist_lock = RedisDistributedLock(self.redis_client)

        self.strategy_repo = StrategyRepositoryImpl(db_session)
        self.order_repo = OrderRepositoryImpl(db_session)
        self.portfolio_repo = PortfolioRepositoryImpl(db_session)
        self.trading_pos_repo = TradingPositionRepositoryImpl(db_session)
        
        self.market_data_repo = DataSourceV2Adapter()
        self.gpu_calculator = GPUIndicatorCalculator()
        
        # 2. 领域服务
        self.signal_service = SignalGenerationService(self.gpu_calculator)
        
        # 3. 应用服务
        self.backtest_service = BacktestApplicationService(
            self.strategy_repo, 
            self.market_data_repo, 
            self.signal_service
        )
        self.order_service = OrderManagementService(self.order_repo)
        
        # 4. 执行事件布线
        self._wire_events()

    def _wire_events(self):
        """
        核心布线逻辑：将不同上下文的事件处理器连接起来
        """
        # 当订单成交时，自动更新投资组合
        self.event_bus.subscribe(OrderFilledEvent, self._on_order_filled)
        logger.info("Event Bus wired: OrderFilledEvent -> Portfolio Update")

    def _on_order_filled(self, event: OrderFilledEvent):
        """跨上下文订阅处理器：Trading -> Portfolio"""
        logger.info(f"Cross-context trigger: Handling {event.event_name()} for {event.symbol}")
        
        # 1. 找到该订单关联的投资组合 (演示先取第一个)
        portfolios = self.portfolio_repo.get_all()
        if not portfolios:
            logger.warning("No portfolio found to update position")
            return
            
        p = portfolios[0]
        
        # 使用分布式锁确保并发安全 (虽然我们已经有了乐观锁，这里演示双重保障)
        lock_name = f"portfolio_update:{p.id}"
        token = self.dist_lock.acquire(lock_name)
        
        if not token:
            logger.error(f"Failed to acquire lock for portfolio {p.id}")
            return
            
        try:
            # 2. 调用领域逻辑更新
            p.handle_order_filled(event)
            # 3. 持久化 (Repository 会触发乐观锁检查)
            self.portfolio_repo.save(p)
            logger.info(f"Portfolio {p.name} updated successfully via Event Bus")
        finally:
            self.dist_lock.release(lock_name, token)

def bootstrap_app(session: Session) -> AppContainer:
    """初始化并返回 App 容器"""
    return AppContainer(session)
