"""
数据源管理器 - 血缘追踪集成

自动记录数据获取、转换和存储的血缘关系。

集成策略:
1. 在数据源调用时自动记录血缘
2. 跟踪从datasource -> dataset -> storage的数据流
3. 支持手动和自动血缘记录模式

Author: Claude Code (Main CLI)
Date: 2026-01-09
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class LineageIntegrationMixin:
    """
    血缘追踪集成混入类

    为DataSourceManagerV2添加自动血缘记录功能。
    """

    def __init__(self, *args, enable_lineage: bool = True, lineage_tracker=None, **kwargs):
        """
        初始化血缘追踪集成

        Args:
            enable_lineage: 是否启用血缘追踪（默认True）
            lineage_tracker: LineageTracker实例（可选，自动创建）
        """
        super().__init__(*args, **kwargs)

        self.enable_lineage = enable_lineage
        self._lineage_tracker = None
        self._lineage_initialized = False

        if enable_lineage and lineage_tracker:
            self._lineage_tracker = lineage_tracker
            self._lineage_initialized = True
            logger.info("✅ Lineage tracking enabled with provided tracker")

    def _initialize_lineage_tracker(self):
        """
        延迟初始化LineageTracker

        仅在第一次需要时创建，避免启动时的数据库连接开销。
        """
        if not self.enable_lineage or self._lineage_initialized:
            return

        try:
            import asyncpg
            from src.data_governance.lineage import LineageTracker, LineageStorage

            # 创建数据库连接
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # 异步创建连接
            async def create_connection():
                conn = await asyncpg.connect(
                    host=self._get_db_config().get("host", "localhost"),
                    port=self._get_db_config().get("port", 5432),
                    user=self._get_db_config().get("user", "postgres"),
                    password=self._get_db_config().get("password"),
                    database=self._get_db_config().get("database", "mystocks"),
                )
                return conn

            conn = loop.run_until_complete(create_connection())
            storage = LineageStorage(conn)
            self._lineage_tracker = LineageTracker(storage)
            self._lineage_initialized = True
            self._lineage_connection = conn

            logger.info("✅ Lineage tracker initialized successfully")

        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize lineage tracker: {e}")
            logger.warning("⚠️ Lineage tracking will be disabled")
            self.enable_lineage = False

    def _get_db_config(self) -> Dict[str, Any]:
        """
        获取数据库配置

        Returns:
            数据库配置字典
        """
        import os

        return {
            "host": os.getenv("POSTGRESQL_HOST", "localhost"),
            "port": int(os.getenv("POSTGRESQL_PORT", 5432)),
            "user": os.getenv("POSTGRESQL_USER", "postgres"),
            "password": os.getenv("POSTGRESQL_PASSWORD"),
            "database": os.getenv("POSTGRESQL_DATABASE", "mystocks"),
        }

    def _record_lineage_fetch(
        self,
        from_node: str,
        to_node: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        记录数据获取血缘

        Args:
            from_node: 源节点ID（通常是数据源endpoint_name）
            to_node: 目标节点ID（通常是数据集标识）
            metadata: 元数据
        """
        if not self.enable_lineage:
            return

        try:
            # 确保tracker已初始化
            if not self._lineage_initialized:
                self._initialize_lineage_tracker()

            if not self._lineage_tracker:
                return

            # 使用tracker的上下文管理器记录血缘
            import asyncio

            async def record():
                from src.data_governance.lineage import LineageNode, LineageEdge, NodeType, OperationType

                # 创建节点和边
                source_node = LineageNode(
                    node_id=from_node,
                    node_type=NodeType.DATASOURCE,
                    name=from_node,
                )

                target_node = LineageNode(
                    node_id=to_node,
                    node_type=NodeType.DATASET,
                    name=to_node,
                    metadata=metadata or {},
                )

                edge = LineageEdge(
                    from_node=from_node,
                    to_node=to_node,
                    operation=OperationType.FETCH,
                    metadata=metadata or {},
                )

                # 保存到数据库
                await self._lineage_tracker._storage.save_node(source_node)
                await self._lineage_tracker._storage.save_node(target_node)
                await self._lineage_tracker._storage.save_edge(edge)

            # 运行异步任务
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(record())
            loop.close()

            logger.debug(f"📊 Recorded fetch lineage: {from_node} -> {to_node}")

        except Exception as e:
            logger.warning(f"⚠️ Failed to record fetch lineage: {e}")

    def _record_lineage_store(
        self,
        from_node: str,
        to_node: str,
        storage_type: str = "database",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        记录数据存储血缘

        Args:
            from_node: 源节点ID（通常是数据集标识）
            to_node: 目标节点ID（通常是存储位置标识）
            storage_type: 存储类型
            metadata: 元数据
        """
        if not self.enable_lineage:
            return

        try:
            # 确保tracker已初始化
            if not self._lineage_initialized:
                self._initialize_lineage_tracker()

            if not self._lineage_tracker:
                return

            # 使用tracker记录血缘
            import asyncio

            async def record():
                from src.data_governance.lineage import LineageNode, LineageEdge, NodeType, OperationType

                # 创建节点和边
                source_node = LineageNode(
                    node_id=from_node,
                    node_type=NodeType.DATASET,
                    name=from_node,
                )

                target_node = LineageNode(
                    node_id=to_node,
                    node_type=NodeType.STORAGE,
                    name=to_node,
                    metadata={"storage_type": storage_type},
                )

                edge = LineageEdge(
                    from_node=from_node,
                    to_node=to_node,
                    operation=OperationType.STORE,
                    metadata={
                        "storage_type": storage_type,
                        **(metadata or {}),
                    },
                )

                # 保存到数据库
                await self._lineage_tracker._storage.save_node(source_node)
                await self._lineage_tracker._storage.save_node(target_node)
                await self._lineage_tracker._storage.save_edge(edge)

            # 运行异步任务
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(record())
            loop.close()

            logger.debug(f"📊 Recorded store lineage: {from_node} -> {to_node}")

        except Exception as e:
            logger.warning(f"⚠️ Failed to record store lineage: {e}")

    def _record_lineage_transform(
        self,
        from_node: str,
        to_node: str,
        transform_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        记录数据转换血缘

        Args:
            from_node: 源节点ID
            to_node: 目标节点ID
            transform_type: 转换类型
            metadata: 元数据
        """
        if not self.enable_lineage:
            return

        try:
            # 确保tracker已初始化
            if not self._lineage_initialized:
                self._initialize_lineage_tracker()

            if not self._lineage_tracker:
                return

            # 使用tracker记录血缘
            import asyncio

            async def record():
                from src.data_governance.lineage import LineageNode, LineageEdge, NodeType, OperationType

                # 创建节点和边
                source_node = LineageNode(
                    node_id=from_node,
                    node_type=NodeType.DATASET,
                    name=from_node,
                )

                target_node = LineageNode(
                    node_id=to_node,
                    node_type=NodeType.TRANSFORM,
                    name=to_node,
                    metadata={"transform_type": transform_type},
                )

                edge = LineageEdge(
                    from_node=from_node,
                    to_node=to_node,
                    operation=OperationType.TRANSFORM,
                    metadata={
                        "transform_type": transform_type,
                        **(metadata or {}),
                    },
                )

                # 保存到数据库
                await self._lineage_tracker._storage.save_node(source_node)
                await self._lineage_tracker._storage.save_node(target_node)
                await self._lineage_tracker._storage.save_edge(edge)

            # 运行异步任务
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(record())
            loop.close()

            logger.debug(f"📊 Recorded transform lineage: {from_node} -> {to_node}")

        except Exception as e:
            logger.warning(f"⚠️ Failed to record transform lineage: {e}")

    def shutdown_lineage_tracker(self):
        """
        关闭血缘追踪器

        清理数据库连接等资源。
        """
        if self._lineage_initialized and hasattr(self, "_lineage_connection"):
            try:
                import asyncio

                async def close():
                    self._lineage_connection.close()

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(close())
                loop.close()

                logger.info("✅ Lineage tracker shutdown successfully")

            except Exception as e:
                logger.warning(f"⚠️ Error shutting down lineage tracker: {e}")

            self._lineage_initialized = False


class LineageEnabledDataSourceManager(LineageIntegrationMixin, object):
    """
    血缘追踪增强的数据源管理器

    继承自DataSourceManagerV2，添加自动血缘记录功能。

    使用示例:
        >>> manager = LineageEnabledDataSourceManager(enable_lineage=True)
        >>> # 正常使用，血缘自动记录
        >>> data = manager.get_stock_daily("000001")
        >>> manager.shutdown_lineage_tracker()
    """

    def __init__(self, *args, **kwargs):
        """
        初始化血缘增强的数据源管理器

        Args:
            enable_lineage: 是否启用血缘追踪（默认True）
            lineage_tracker: 自定义LineageTracker（可选）
            **kwargs: 其他DataSourceManagerV2参数
        """
        # 先初始化LineageIntegrationMixin
        LineageIntegrationMixin.__init__(self, *args, **kwargs)

        # 导入并继承DataSourceManagerV2
        from .base import DataSourceManagerV2

        DataSourceManagerV2.__init__(self, *args, **kwargs)

        logger.info("✅ LineageEnabledDataSourceManager initialized")

    def _call_endpoint(self, endpoint_info: Dict, **kwargs) -> Any:
        """
        调用数据源端点并自动记录血缘

        Args:
            endpoint_info: 端点信息
            **kwargs: 调用参数

        Returns:
            数据源返回结果
        """
        # 调用原始方法
        result = super()._call_endpoint(endpoint_info, **kwargs)

        # 自动记录血缘
        if result is not None and self.enable_lineage:
            endpoint_name = endpoint_info.get("config", {}).get("endpoint_name", "unknown")

            # 构建数据集标识
            symbol = kwargs.get("symbol", "")
            data_category = endpoint_info.get("config", {}).get("data_category", "")

            dataset_id = f"{data_category}_{symbol}" if symbol else data_category

            # 记录fetch血缘
            self._record_lineage_fetch(
                from_node=endpoint_name,
                to_node=dataset_id,
                metadata={
                    "params": kwargs,
                    "timestamp": datetime.now().isoformat(),
                },
            )

        return result


# 便捷函数
def create_lineage_enabled_manager(
    yaml_config_path: str = "config/data_sources_registry.yaml", enable_lineage: bool = True, **kwargs
) -> LineageEnabledDataSourceManager:
    """
    创建血缘增强的数据源管理器

    Args:
        yaml_config_path: YAML配置文件路径
        enable_lineage: 是否启用血缘追踪
        **kwargs: 其他参数

    Returns:
        LineageEnabledDataSourceManager实例
    """
    return LineageEnabledDataSourceManager(yaml_config_path=yaml_config_path, enable_lineage=enable_lineage, **kwargs)
