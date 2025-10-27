"""
DataManager - 简化的数据管理核心类 (US3 Architecture Simplification)

这个类整合了原来的多层架构:
- 合并了DataStorageStrategy的路由逻辑
- 提供适配器注册和管理
- 统一的数据保存/加载接口
- 直接管理数据库连接

目标:
- <5ms 路由决策时间
- 简化的API接口
- 更好的可维护性

创建日期: 2025-10-25
版本: 1.0.0 (US3)
"""

import pandas as pd
import time
import logging
import traceback
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from core.data_classification import DataClassification, DatabaseTarget

logger = logging.getLogger(__name__)

# 尝试导入新的监控模块（可选依赖）
try:
    from core.datamanager_monitoring import DataManagerMonitor, RoutingOperationContext
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    logger.warning("DataManagerMonitor not available - monitoring disabled")


class _NullMonitoring:
    """
    Null监控实现 - 用于禁用监控时的占位
    实现监控接口但不执行任何操作
    """

    def log_operation_start(self, *args, **kwargs):
        """记录操作开始 - 无操作"""
        return "null_operation_id"

    def log_operation_result(self, *args, **kwargs):
        """记录操作结果 - 无操作"""
        return True

    def log_operation(self, *args, **kwargs):
        """记录操作 - 无操作"""
        return True

    def record_performance_metric(self, *args, **kwargs):
        """记录性能指标 - 无操作"""
        return True

    def record_operation(self, *args, **kwargs):
        """记录操作性能 - 无操作"""
        return True

    def log_quality_check(self, *args, **kwargs):
        """记录质量检查 - 无操作"""
        return True


class DataManager:
    """
    DataManager - 简化的数据管理核心类

    示例:
        ```python
        dm = DataManager()
        dm.register_adapter('akshare', akshare_adapter)

        # 保存数据 - 自动路由到正确的数据库
        dm.save_data(
            DataClassification.TICK_DATA,
            tick_df,
            table_name='tick_600000'
        )

        # 加载数据
        data = dm.load_data(
            DataClassification.DAILY_KLINE,
            table_name='daily_kline',
            symbol='600000.SH'
        )
        ```
    """

    # 预计算的路由映射 (优化性能 - 字典查找比函数调用快)
    _ROUTING_MAP: Dict[DataClassification, DatabaseTarget] = {
        # 第1类：市场数据 (6项) - 高频时序 → TDengine
        DataClassification.TICK_DATA: DatabaseTarget.TDENGINE,
        DataClassification.MINUTE_KLINE: DatabaseTarget.TDENGINE,
        DataClassification.DAILY_KLINE: DatabaseTarget.POSTGRESQL,
        DataClassification.ORDER_BOOK_DEPTH: DatabaseTarget.TDENGINE,
        DataClassification.LEVEL2_SNAPSHOT: DatabaseTarget.TDENGINE,
        DataClassification.INDEX_QUOTES: DatabaseTarget.TDENGINE,
        # 第2类：参考数据 (9项) → PostgreSQL
        DataClassification.SYMBOLS_INFO: DatabaseTarget.POSTGRESQL,
        DataClassification.INDUSTRY_CLASS: DatabaseTarget.POSTGRESQL,
        DataClassification.CONCEPT_CLASS: DatabaseTarget.POSTGRESQL,
        DataClassification.INDEX_CONSTITUENTS: DatabaseTarget.POSTGRESQL,
        DataClassification.TRADE_CALENDAR: DatabaseTarget.POSTGRESQL,
        DataClassification.FUNDAMENTAL_METRICS: DatabaseTarget.POSTGRESQL,
        DataClassification.DIVIDEND_DATA: DatabaseTarget.POSTGRESQL,
        DataClassification.SHAREHOLDER_DATA: DatabaseTarget.POSTGRESQL,
        DataClassification.MARKET_RULES: DatabaseTarget.POSTGRESQL,
        # 第3类：衍生数据 (6项) → PostgreSQL+TimescaleDB
        DataClassification.TECHNICAL_INDICATORS: DatabaseTarget.POSTGRESQL,
        DataClassification.QUANT_FACTORS: DatabaseTarget.POSTGRESQL,
        DataClassification.MODEL_OUTPUT: DatabaseTarget.POSTGRESQL,
        DataClassification.TRADE_SIGNALS: DatabaseTarget.POSTGRESQL,
        DataClassification.BACKTEST_RESULTS: DatabaseTarget.POSTGRESQL,
        DataClassification.RISK_METRICS: DatabaseTarget.POSTGRESQL,
        # 第4类：交易数据 (7项) → PostgreSQL
        DataClassification.ORDER_RECORDS: DatabaseTarget.POSTGRESQL,
        DataClassification.TRADE_RECORDS: DatabaseTarget.POSTGRESQL,
        DataClassification.POSITION_HISTORY: DatabaseTarget.POSTGRESQL,
        DataClassification.REALTIME_POSITIONS: DatabaseTarget.POSTGRESQL,
        DataClassification.REALTIME_ACCOUNT: DatabaseTarget.POSTGRESQL,
        DataClassification.FUND_FLOW: DatabaseTarget.POSTGRESQL,
        DataClassification.ORDER_QUEUE: DatabaseTarget.POSTGRESQL,
        # 第5类：元数据 (6项) → PostgreSQL
        DataClassification.DATA_SOURCE_STATUS: DatabaseTarget.POSTGRESQL,
        DataClassification.TASK_SCHEDULE: DatabaseTarget.POSTGRESQL,
        DataClassification.STRATEGY_PARAMS: DatabaseTarget.POSTGRESQL,
        DataClassification.SYSTEM_CONFIG: DatabaseTarget.POSTGRESQL,
        DataClassification.DATA_QUALITY_METRICS: DatabaseTarget.POSTGRESQL,
        DataClassification.USER_CONFIG: DatabaseTarget.POSTGRESQL,
    }

    def __init__(self, enable_monitoring: bool = True):
        """
        初始化DataManager

        Args:
            enable_monitoring: 是否启用Grafana监控 (默认True以使用新的监控系统)
        """
        # 监控开关 (US3 - 使用新的 Grafana 监控)
        self.enable_monitoring = enable_monitoring and MONITORING_AVAILABLE
        self.monitor = None

        # 初始化新的监控组件
        if self.enable_monitoring:
            try:
                self.monitor = DataManagerMonitor()
                logger.info(f"DataManager 监控: {'已启用' if self.monitor.enabled else '已禁用'}")
            except Exception as e:
                logger.warning(f"监控组件初始化失败: {e}")
                self.enable_monitoring = False
                self.monitor = None

        # 如果监控未启用，使用null实现
        if not self.enable_monitoring:
            null_monitor = _NullMonitoring()
            self.monitor = null_monitor
            # 保持向后兼容
            self._monitoring_db = null_monitor
            self._performance_monitor = null_monitor

        # 延迟导入以避免循环依赖
        from data_access import TDengineDataAccess, PostgreSQLDataAccess

        # 初始化数据库访问层（US3简化版本不需要监控参数）
        self._tdengine = TDengineDataAccess()
        self._postgresql = PostgreSQLDataAccess()

        # 适配器注册表
        self._adapters: Dict[str, Any] = {}

        logger.info(
            "DataManager initialized with dual-database architecture (TDengine + PostgreSQL)"
        )

    def register_adapter(self, name: str, adapter: Any) -> None:
        """
        注册数据适配器

        Args:
            name: 适配器名称 (如 'akshare', 'baostock', 'tdx')
            adapter: 适配器实例 (需实现IDataSource接口)
        """
        if name in self._adapters:
            logger.warning(f"适配器 '{name}' 已存在,将被覆盖")

        self._adapters[name] = adapter
        logger.info(f"已注册适配器: {name}")

    def unregister_adapter(self, name: str) -> bool:
        """
        注销数据适配器

        Args:
            name: 适配器名称

        Returns:
            True if successful, False if adapter not found
        """
        if name in self._adapters:
            del self._adapters[name]
            logger.info(f"已注销适配器: {name}")
            return True
        else:
            logger.warning(f"适配器 '{name}' 不存在")
            return False

    def list_adapters(self) -> List[str]:
        """
        列出所有已注册的适配器

        Returns:
            适配器名称列表
        """
        return list(self._adapters.keys())

    def get_adapter(self, name: str) -> Optional[Any]:
        """
        获取指定的适配器实例

        Args:
            name: 适配器名称

        Returns:
            适配器实例，如果不存在则返回None
        """
        return self._adapters.get(name)

    def get_target_database(self, classification: DataClassification) -> DatabaseTarget:
        """
        获取数据分类的目标数据库 (优化版 - <5ms)

        Args:
            classification: 数据分类

        Returns:
            目标数据库类型

        性能优化:
        - 使用预计算的字典映射
        - O(1) 时间复杂度
        - 预期<1ms响应时间
        """
        return self._ROUTING_MAP.get(classification, DatabaseTarget.POSTGRESQL)

    def save_data(
        self,
        classification: DataClassification,
        data: pd.DataFrame,
        table_name: str,
        **kwargs,
    ) -> bool:
        """
        保存数据到正确的数据库 (带 Grafana 监控)

        Args:
            classification: 数据分类
            data: 要保存的数据 (pandas DataFrame)
            table_name: 目标表名
            **kwargs: 其他参数传递给底层数据库访问层

        Returns:
            True if successful, False otherwise
        """
        # 获取目标数据库
        target_db = self.get_target_database(classification)

        # 使用监控上下文（如果启用）
        if self.enable_monitoring and MONITORING_AVAILABLE:
            with RoutingOperationContext(
                self.monitor,
                classification=classification.value,
                target_database=target_db.value,
                operation_type='save_data',
                table_name=table_name
            ) as ctx:
                # 标记路由决策完成
                ctx.mark_routing_complete()

                # 执行实际操作
                try:
                    if target_db == DatabaseTarget.TDENGINE:
                        success = self._tdengine.save_data(
                            data, classification, table_name, **kwargs
                        )
                    else:  # DatabaseTarget.POSTGRESQL
                        success = self._postgresql.save_data(
                            data, classification, table_name, **kwargs
                        )

                    # 记录结果
                    ctx.set_result(
                        success=success,
                        data_count=len(data) if hasattr(data, '__len__') else 0
                    )

                    if success:
                        logger.debug(
                            f"保存数据成功: {classification.value} → {target_db.value} "
                            f"({len(data)} rows)"
                        )
                    else:
                        logger.error(
                            f"保存数据失败: {classification.value} → {target_db.value}"
                        )

                    return success

                except Exception as e:
                    logger.error(f"保存数据异常: {classification.value} - {str(e)}")
                    logger.debug(traceback.format_exc())
                    ctx.set_result(success=False, error_message=str(e))
                    return False
        else:
            # 无监控模式 (向后兼容)
            try:
                if target_db == DatabaseTarget.TDENGINE:
                    success = self._tdengine.save_data(
                        data, classification, table_name, **kwargs
                    )
                else:  # DatabaseTarget.POSTGRESQL
                    success = self._postgresql.save_data(
                        data, classification, table_name, **kwargs
                    )

                if success:
                    logger.debug(
                        f"保存数据成功: {classification.value} → {target_db.value} "
                        f"({len(data)} rows)"
                    )
                else:
                    logger.error(
                        f"保存数据失败: {classification.value} → {target_db.value}"
                    )

                return success

            except Exception as e:
                logger.error(f"保存数据异常: {classification.value} - {str(e)}")
                logger.debug(traceback.format_exc())
                return False

    def load_data(
        self, classification: DataClassification, table_name: str, **filters
    ) -> Optional[pd.DataFrame]:
        """
        从正确的数据库加载数据 (带 Grafana 监控)

        Args:
            classification: 数据分类
            table_name: 源表名
            **filters: 过滤条件 (如 symbol='600000.SH', start_date='2024-01-01')

        Returns:
            pandas DataFrame if successful, None otherwise
        """
        # 获取目标数据库
        target_db = self.get_target_database(classification)

        # 使用监控上下文（如果启用）
        if self.enable_monitoring and MONITORING_AVAILABLE:
            with RoutingOperationContext(
                self.monitor,
                classification=classification.value,
                target_database=target_db.value,
                operation_type='load_data',
                table_name=table_name
            ) as ctx:
                # 标记路由决策完成
                ctx.mark_routing_complete()

                # 执行实际操作
                try:
                    if target_db == DatabaseTarget.TDENGINE:
                        data = self._tdengine.load_data(table_name, **filters)
                    else:  # DatabaseTarget.POSTGRESQL
                        data = self._postgresql.load_data(table_name, **filters)

                    # 记录结果
                    ctx.set_result(
                        success=(data is not None),
                        data_count=len(data) if data is not None else 0
                    )

                    if data is not None:
                        logger.debug(
                            f"加载数据成功: {classification.value} → {target_db.value} "
                            f"({len(data)} rows)"
                        )
                    else:
                        logger.warning(
                            f"加载数据为空: {classification.value} → {target_db.value}"
                        )

                    return data

                except Exception as e:
                    logger.error(f"加载数据异常: {classification.value} - {str(e)}")
                    logger.debug(traceback.format_exc())
                    ctx.set_result(success=False, error_message=str(e))
                    return None
        else:
            # 无监控模式 (向后兼容)
            try:
                if target_db == DatabaseTarget.TDENGINE:
                    data = self._tdengine.load_data(table_name, **filters)
                else:  # DatabaseTarget.POSTGRESQL
                    data = self._postgresql.load_data(table_name, **filters)

                if data is not None:
                    logger.debug(
                        f"加载数据成功: {classification.value} → {target_db.value} "
                        f"({len(data)} rows)"
                    )
                else:
                    logger.warning(
                        f"加载数据为空: {classification.value} → {target_db.value}"
                    )

                return data

            except Exception as e:
                logger.error(f"加载数据异常: {classification.value} - {str(e)}")
                logger.debug(traceback.format_exc())
                return None

    def get_routing_stats(self) -> Dict[str, Any]:
        """
        获取路由统计信息

        Returns:
            包含路由统计的字典
        """
        stats = {
            "total_classifications": len(self._ROUTING_MAP),
            "tdengine_count": sum(
                1 for db in self._ROUTING_MAP.values() if db == DatabaseTarget.TDENGINE
            ),
            "postgresql_count": sum(
                1
                for db in self._ROUTING_MAP.values()
                if db == DatabaseTarget.POSTGRESQL
            ),
            "registered_adapters": len(self._adapters),
            "adapter_names": list(self._adapters.keys()),
        }
        return stats

    def validate_data(
        self, classification: DataClassification, data: pd.DataFrame
    ) -> Tuple[bool, List[str]]:
        """
        验证数据有效性

        Args:
            classification: 数据分类
            data: 要验证的数据

        Returns:
            (is_valid, error_messages)
        """
        errors = []

        # 基本检查
        if data is None or data.empty:
            errors.append("数据为空")
            return False, errors

        # 数据分类特定的验证逻辑可在此扩展
        # 例如：检查必需列、数据类型、时间范围等

        return len(errors) == 0, errors

    def health_check(self) -> Dict[str, Any]:
        """
        检查DataManager和数据库连接健康状态

        Returns:
            健康状态字典
        """
        health = {
            "manager_status": "healthy",
            "tdengine": "unknown",
            "postgresql": "unknown",
            "timestamp": datetime.now().isoformat(),
        }

        # 检查TDengine
        try:
            # 简单的连接测试
            test_result = (
                self._tdengine.health_check()
                if hasattr(self._tdengine, "health_check")
                else True
            )
            health["tdengine"] = "healthy" if test_result else "unhealthy"
        except Exception as e:
            health["tdengine"] = f"unhealthy: {str(e)}"

        # 检查PostgreSQL
        try:
            test_result = (
                self._postgresql.health_check()
                if hasattr(self._postgresql, "health_check")
                else True
            )
            health["postgresql"] = "healthy" if test_result else "unhealthy"
        except Exception as e:
            health["postgresql"] = f"unhealthy: {str(e)}"

        return health
