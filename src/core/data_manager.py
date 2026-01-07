"""
DataManager - 重构后的核心数据协调器 (Refactored for Decoupling & Saga Support)

这个类现在是一个纯粹的协调者 (Coordinator)，职责如下:
1. 使用 DataRouter 决定存储目标
2. 使用 AdapterRegistry 管理数据源
3. 使用 EventBus 发出监控事件
4. 协调底层 DataAccess 执行操作

解决了:
- 过度封装 (通过拆分职责)
- 混合职责 (通过委托)
- 模块耦合 (通过依赖注入和事件总线)

版本: 2.0.0 (Refactored)
修改日期: 2026-01-03
"""

import pandas as pd
import time
import logging
import traceback
from typing import Dict, List, Optional, Any, Callable

from src.core.data_classification import DataClassification, DatabaseTarget
from src.storage.database.database_manager import DatabaseTableManager

# 引入新组件
from src.core.infrastructure.data_router import DataRouter
from src.core.infrastructure.adapter_registry import AdapterRegistry
from src.core.infrastructure.event_bus import EventBus
from src.core.transaction.saga_coordinator import SagaCoordinator

logger = logging.getLogger(__name__)


class DataManager:
    """
    DataManager - 核心数据协调器
    """

    def __init__(
        self,
        enable_monitoring: bool = False,
        db_manager: DatabaseTableManager = None,
        # 依赖注入参数 (可选，为了向后兼容默认为 None)
        router: DataRouter = None,
        registry: AdapterRegistry = None,
        event_bus: EventBus = None,
        td_access=None,
        pg_access=None,
    ):
        """
        初始化DataManager

        Args:
            enable_monitoring: 是否启用监控 (保留参数以兼容旧代码)
            db_manager: 数据库表管理器
            router: 数据路由策略组件
            registry: 适配器注册表组件
            event_bus: 事件总线组件
            td_access: TDengine 访问层实例
            pg_access: PostgreSQL 访问层实例
        """
        self.enable_monitoring = enable_monitoring

        # 1. 初始化基础设施组件
        self.router = router or DataRouter()
        self.registry = registry or AdapterRegistry()
        self.event_bus = event_bus or EventBus()

        # 2. 初始化数据库访问层
        self._db_manager = db_manager or DatabaseTableManager()

        # 如果未注入访问层，则按传统方式创建 (向后兼容)
        if not td_access or not pg_access:
            # 延迟导入以避免循环依赖
            from src.data_access import TDengineDataAccess, PostgreSQLDataAccess

            # 这里的 monitoring_db 参数是旧架构的遗留，新架构建议使用 EventBus
            # 但为了兼容 DataAccess 层的现有签名，我们可能仍需传递它
            # 在完全重构 DataAccess 之前，我们保持这种混合状态
            monitoring_db = None
            if enable_monitoring:
                try:
                    from src.monitoring.monitoring_database import get_monitoring_database

                    monitoring_db = get_monitoring_database()
                except ImportError:
                    pass

            self._tdengine = td_access or TDengineDataAccess(self._db_manager, monitoring_db)
            self._postgresql = pg_access or PostgreSQLDataAccess(self._db_manager, monitoring_db)
        else:
            self._tdengine = td_access
            self._postgresql = pg_access

        # 3. 初始化 Saga 协调器
        self.saga_coordinator = SagaCoordinator(self._postgresql, self._tdengine)

        # 4. 如果启用了监控，且未注入 EventBus，尝试自动连接监控系统到 EventBus
        if enable_monitoring and not event_bus:
            self._setup_monitoring_listeners()

        logger.info("DataManager initialized with Refactored Architecture (Router + Registry + EventBus)")

    def _setup_monitoring_listeners(self):
        """配置默认的监控监听器 (用于兼容旧的监控行为)"""
        try:
            from src.monitoring.performance_monitor import get_performance_monitor

            perf_monitor = get_performance_monitor()

            # 定义监听器
            def on_operation_complete(data):
                if perf_monitor:
                    perf_monitor.record_operation(
                        operation=data.get("operation"),
                        classification=data.get("classification"),
                        duration_ms=data.get("duration_ms"),
                        success=data.get("success"),
                    )

            self.event_bus.subscribe("data_operation_complete", on_operation_complete)
            logger.info("EventBus connected to PerformanceMonitor")
        except ImportError:
            logger.warning("Monitoring modules not found, EventBus running in detached mode")

    # --- 适配器管理 (委托给 Registry) ---

    def register_adapter(self, name: str, adapter: Any) -> None:
        self.registry.register(name, adapter)

    def unregister_adapter(self, name: str) -> bool:
        return self.registry.unregister(name)

    def list_adapters(self) -> List[str]:
        return self.registry.list_all()

    def get_adapter(self, name: str) -> Optional[Any]:
        return self.registry.get(name)

    # --- 路由管理 (委托给 Router) ---

    def get_target_database(self, classification: DataClassification) -> DatabaseTarget:
        return self.router.get_target_database(classification)

    def get_routing_stats(self) -> Dict[str, Any]:
        stats = self.router.get_stats()
        stats["registered_adapters"] = len(self.registry.list_all())
        return stats

    # --- 核心数据操作 ---

    def save_data(
        self,
        classification: DataClassification,
        data: pd.DataFrame,
        table_name: str,
        use_saga: bool = False,  # 新增参数：是否启用 Saga 事务
        metadata_callback: Callable = None,  # 新增参数：元数据更新回调 (用于 Saga)
        **kwargs,
    ) -> bool:
        """
        保存数据

        Args:
            classification: 数据分类
            data: 数据 DataFrame
            table_name: 目标表名
            use_saga: 是否使用 Saga 分布式事务模式 (针对跨库操作)
            metadata_callback: Saga 模式下的元数据更新回调
            **kwargs: 其他参数
        """
        start_time = time.time()
        success = False
        target_db = DatabaseTarget.POSTGRESQL  # Default

        try:
            # 1. 路由决策
            target_db = self.router.get_target_database(classification)

            # 2. 执行保存
            if use_saga and target_db == DatabaseTarget.TDENGINE and metadata_callback:
                # 使用 Saga 模式 (TDengine + PG Metadata)
                # 构造唯一的 business_id (简单起见，这里用表名+时间)
                business_id = f"{table_name}_{int(time.time())}"
                success = self.saga_coordinator.execute_kline_sync(
                    business_id, data, classification, table_name, metadata_callback
                )
            else:
                # 传统模式
                if target_db == DatabaseTarget.TDENGINE:
                    success = self._tdengine.save_data(data, classification, table_name, **kwargs)
                else:
                    success = self._postgresql.save_data(data, classification, table_name, **kwargs)

            # 3. 记录性能 (发出事件)
            duration_ms = (time.time() - start_time) * 1000

            self.event_bus.emit(
                "data_operation_complete",
                {
                    "operation": "save_data",
                    "classification": classification.value,
                    "target_db": target_db.value,
                    "row_count": len(data) if data is not None else 0,
                    "duration_ms": duration_ms,
                    "success": success,
                },
            )

            if success:
                logger.debug(f"Save success: {classification.value} -> {target_db.value}")

            return success

        except Exception as e:
            logger.error(f"Save failed: {classification.value} - {str(e)}")
            logger.debug(traceback.format_exc())
            return False

    def load_data(self, classification: DataClassification, table_name: str, **filters) -> Optional[pd.DataFrame]:
        """加载数据"""
        start_time = time.time()
        data = None
        target_db = DatabaseTarget.POSTGRESQL

        try:
            # 1. 路由决策
            target_db = self.router.get_target_database(classification)

            # 2. 执行加载
            if target_db == DatabaseTarget.TDENGINE:
                data = self._tdengine.load_data(table_name, **filters)
            else:
                data = self._postgresql.load_data(table_name, **filters)

            # 3. 记录性能 (发出事件)
            duration_ms = (time.time() - start_time) * 1000

            self.event_bus.emit(
                "data_operation_complete",
                {
                    "operation": "load_data",
                    "classification": classification.value,
                    "target_db": target_db.value,
                    "row_count": len(data) if data is not None else 0,
                    "duration_ms": duration_ms,
                    "success": (data is not None),
                },
            )

            return data

        except Exception as e:
            logger.error(f"Load failed: {classification.value} - {str(e)}")
            return None

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        # 简化实现，实际应调用 access layers
        return {"status": "active", "router": "healthy", "event_bus": "active"}
