"""
MyStocks统一数据管理器 - 简化版本 (US3 Architecture Simplification)

这是系统的向后兼容性包装器,提供与之前版本相同的API。
所有核心逻辑已委托给DataManager以简化架构。

版本: 3.0.0 (US3 Simplified - Thin Wrapper)
创建日期: 2025-10-25
"""

import pandas as pd
import logging
from typing import Optional, Dict, Any, Union
from datetime import datetime

from src.core.data_classification import DataClassification
from src.core.data_manager import DataManager
from src.core.batch_failure_strategy import (
    BatchFailureStrategy,
    BatchFailureHandler,
    BatchOperationResult,
)
from src.utils.failure_recovery_queue import FailureRecoveryQueue

# 监控组件 (可选)
try:
    from src.monitoring.monitoring_database import get_monitoring_database
    from src.monitoring.performance_monitor import get_performance_monitor
    from src.monitoring.data_quality_monitor import get_quality_monitor
    from src.monitoring.alert_manager import get_alert_manager

    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

logger = logging.getLogger(__name__)


class MyStocksUnifiedManager:
    """
    MyStocks统一数据管理器 - Thin Wrapper版本

    **重要**: 这是一个向后兼容性包装器。所有核心功能已委托给DataManager。

    **核心功能**:
    1. 自动路由: 根据数据分类自动选择最优数据库
    2. 统一接口: 2行代码完成保存/加载操作
    3. 故障恢复: 数据库不可用时自动排队
    4. 批量操作: 支持高性能批量保存

    **使用示例**:
        ```python
        manager = MyStocksUnifiedManager()

        # 保存Tick数据 → 自动路由到TDengine
        manager.save_data_by_classification(
            DataClassification.TICK_DATA,
            tick_df,
            table_name='tick_600000'
        )

        # 加载日线数据 → 自动路由到PostgreSQL
        kline_df = manager.load_data_by_classification(
            DataClassification.DAILY_KLINE,
            table_name='daily_kline',
            filters={'symbol': '600000.SH'}
        )
        ```
    """

    def __init__(self, enable_monitoring: bool = True) -> None:
        """
        初始化统一管理器

        Args:
            enable_monitoring: 是否启用监控功能 (默认True)
        """
        # 核心：使用DataManager处理所有数据操作
        self._data_manager = DataManager(enable_monitoring=enable_monitoring)

        # 保持向后兼容：直接访问数据库连接
        self.tdengine = self._data_manager._tdengine
        self.postgresql = self._data_manager._postgresql

        # 故障恢复队列
        self.recovery_queue = FailureRecoveryQueue()

        # 监控组件
        self.enable_monitoring = enable_monitoring
        if enable_monitoring and MONITORING_AVAILABLE:
            try:
                self.monitoring_db = get_monitoring_database()
                self.performance_monitor = get_performance_monitor()
                self.quality_monitor = get_quality_monitor()
                self.alert_manager = get_alert_manager()
                print("   - 监控组件已启用 ✅")
            except Exception as e:
                print(f"   - 监控组件初始化失败,已禁用: {e}")
                self.enable_monitoring = False
                self.monitoring_db = None
                self.performance_monitor = None
                self.quality_monitor = None
                self.alert_manager = None
        else:
            self.monitoring_db = None
            self.performance_monitor = None
            self.quality_monitor = None
            self.alert_manager = None

        print("✅ MyStocksUnifiedManager 初始化成功 (US3 Simplified)")
        print("   - 支持34个数据分类的自动路由")
        print("   - 2种数据库连接就绪 (TDengine + PostgreSQL)")
        print("   - 基于DataManager的简化架构")

    def save_data_by_classification(
        self,
        classification: DataClassification,
        data: pd.DataFrame,
        table_name: str,
        **kwargs,
    ) -> bool:
        """
        按分类保存数据 (核心方法 #1)

        委托给DataManager处理。

        Args:
            classification: 数据分类枚举
            data: 数据DataFrame
            table_name: 目标表名
            **kwargs: 额外参数

        Returns:
            bool: 保存是否成功
        """
        if data.empty:
            logger.warning("数据为空,跳过保存")
            return True

        try:
            # 委托给DataManager
            return self._data_manager.save_data(
                classification, data, table_name, **kwargs
            )
        except Exception as e:
            logger.error(f"保存数据失败: {classification} - {e}")
            # 故障恢复：加入队列
            self.recovery_queue.add_failed_operation(
                operation_type="save",
                classification=classification.value,
                data=data,
                table_name=table_name,
                kwargs=kwargs,
                error=str(e),
            )
            return False

    def load_data_by_classification(
        self,
        classification: DataClassification,
        table_name: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Optional[pd.DataFrame]:
        """
        按分类加载数据 (核心方法 #2)

        委托给DataManager处理。

        Args:
            classification: 数据分类枚举
            table_name: 源表名
            filters: 过滤条件字典

        Returns:
            Optional[pd.DataFrame]: 加载的数据或None
        """
        try:
            # 委托给DataManager
            if filters is None:
                filters = {}

            return self._data_manager.load_data(classification, table_name, **filters)
        except Exception as e:
            logger.error(f"加载数据失败: {classification} - {e}")
            return None

    def get_routing_info(self, classification: DataClassification) -> Dict[str, Any]:
        """
        获取数据分类的路由信息

        Args:
            classification: 数据分类

        Returns:
            路由信息字典
        """
        target_db = self._data_manager.get_target_database(classification)

        return {
            "classification": classification.value,
            "target_db": target_db.value,
        }

    def save_data_batch_with_strategy(
        self,
        classification: DataClassification,
        data: pd.DataFrame,
        table_name: str,
        batch_size: int = 1000,
        failure_strategy: BatchFailureStrategy = BatchFailureStrategy.CONTINUE,
        **kwargs,
    ) -> BatchOperationResult:
        """
        批量保存数据（带故障处理策略）

        Args:
            classification: 数据分类
            data: 要保存的数据
            table_name: 目标表名
            batch_size: 批次大小
            failure_strategy: 失败处理策略
            **kwargs: 额外参数

        Returns:
            BatchOperationResult: 批量操作结果
        """
        handler = BatchFailureHandler(strategy=failure_strategy)

        # 分批处理
        total_rows = len(data)
        for i in range(0, total_rows, batch_size):
            batch_data = data.iloc[i : i + batch_size]

            success = self.save_data_by_classification(
                classification, batch_data, table_name, **kwargs
            )

            handler.record_batch_result(
                batch_index=i // batch_size, success=success, row_count=len(batch_data)
            )

            # 根据策略决定是否继续
            if not success and failure_strategy == BatchFailureStrategy.ROLLBACK:
                break

        return handler.get_result()

    def get_monitoring_statistics(self) -> Dict[str, Any]:
        """
        获取监控统计信息

        Returns:
            监控统计字典
        """
        stats = {
            "manager_type": "MyStocksUnifiedManager (US3 Simplified)",
            "data_manager_stats": self._data_manager.get_routing_stats(),
            "monitoring_enabled": self.enable_monitoring,
            "timestamp": datetime.now().isoformat(),
        }

        if self.enable_monitoring and self.performance_monitor:
            try:
                stats["performance"] = self.performance_monitor.get_statistics()
            except Exception:
                pass

        return stats

    def check_data_quality(
        self,
        classification: DataClassification,
        table_name: str,
        **filters: Union[str, int, float],
    ) -> Dict[str, Any]:
        """
        检查数据质量

        Args:
            classification: 数据分类
            table_name: 表名
            **filters: 过滤条件

        Returns:
            数据质量检查结果
        """
        result = {
            "classification": classification.value,
            "table_name": table_name,
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # 加载数据
            data = self.load_data_by_classification(classification, table_name, filters)

            if data is not None:
                result["row_count"] = len(data)
                result["column_count"] = len(data.columns)
                result["null_counts"] = data.isnull().sum().to_dict()
                result["status"] = "success"
            else:
                result["status"] = "no_data"

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def close_all_connections(self) -> None:
        """
        关闭所有数据库连接
        """
        try:
            if hasattr(self.tdengine, "close"):
                self.tdengine.close()
            if hasattr(self.postgresql, "close"):
                self.postgresql.close()
            logger.info("所有数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭连接时出错: {e}")

    def __del__(self) -> None:
        """析构函数：确保连接被关闭"""
        try:
            self.close_all_connections()
        except Exception:
            pass
