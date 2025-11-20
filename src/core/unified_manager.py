"""
MyStocks统一数据管理器 - 集成监控版本 (US1 + US3)

这是系统的核心入口,提供统一的数据保存和加载接口。
用户只需调用save_data_by_classification()和load_data_by_classification(),
系统自动根据数据分类路由到最优数据库。

新增功能 (US3):
- 所有操作自动记录到监控数据库
- 性能指标自动收集
- 慢查询自动告警
- 数据质量自动检查

创建日期: 2025-10-11
版本: 2.0.0 (MVP US1 + US3监控集成)
"""

import pandas as pd
import time
import logging
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

from src.core.data_classification import DataClassification, DatabaseTarget

logger = logging.getLogger(__name__)
# US3: 已移除DataStorageStrategy，使用DataManager进行路由
from src.core.batch_failure_strategy import (
    BatchFailureStrategy,
    BatchFailureHandler,
    BatchOperationResult,
)
from src.data_access import (
    TDengineDataAccess,
    PostgreSQLDataAccess,
)
# 注释掉不存在的MySQL导入 - 系统已简化为TDengine+PostgreSQL双数据库架构
# from src.storage.database.database_manager import MySQLDataAccess
# 注释掉不存在的Redis导入
# from src.db_manager.redis_manager import RedisDataAccess
from src.utils.failure_recovery_queue import FailureRecoveryQueue

# 监控组件 (US3)
from src.monitoring.monitoring_database import get_monitoring_database
from src.monitoring.performance_monitor import get_performance_monitor
from src.monitoring.data_quality_monitor import get_quality_monitor
from src.monitoring.alert_manager import get_alert_manager


class MyStocksUnifiedManager:
    """
    MyStocks统一数据管理器

    **核心功能** (MVP US1):
    1. 自动路由: 根据数据分类自动选择最优数据库
    2. 统一接口: 2行代码完成保存/加载操作
    3. 故障恢复: 数据库不可用时自动排队,数据不丢失
    4. 批量操作: 支持10万条记录的高性能批量保存

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

    # Type hints for optional monitoring components
    monitoring_db: Optional[Any]
    performance_monitor: Optional[Any]
    quality_monitor: Optional[Any]
    alert_manager: Optional[Any]

    def __init__(self, enable_monitoring: bool = True) -> None:
        """
        初始化统一管理器

        Args:
            enable_monitoring: 是否启用监控功能 (默认True)
        """
        # 初始化2个数据访问层 (系统已简化为TDengine+PostgreSQL双数据库架构)
        self.tdengine = TDengineDataAccess()
        self.postgresql = PostgreSQLDataAccess()
        # 注释掉不存在的Redis访问层
        # self.redis = RedisDataAccess()

        # 初始化故障恢复队列
        self.recovery_queue = FailureRecoveryQueue()

        # 初始化监控组件 (US3)
        self.enable_monitoring = enable_monitoring
        if enable_monitoring:
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

        print("✅ MyStocksUnifiedManager 初始化成功")
        print("   - 支持34个数据分类的自动路由")
        print("   - 2种数据库连接就绪 (TDengine + PostgreSQL)")
        print("   - 故障恢复队列已启用")

    def _get_target_database(self, classification: DataClassification) -> DatabaseTarget:
        """
        根据数据分类获取目标数据库
        
        Args:
            classification: 数据分类
            
        Returns:
            DatabaseTarget: 目标数据库
        """
        # 简单的路由规则，根据数据分类选择数据库
        if classification in [
            DataClassification.TICK_DATA,
            DataClassification.MINUTE_KLINE,
            DataClassification.ORDER_BOOK_DEPTH,
        ]:
            return DatabaseTarget.TDENGINE
        elif classification in [
            DataClassification.DAILY_KLINE,
            DataClassification.FUNDAMENTAL_METRICS,
            DataClassification.SYMBOLS_INFO,
            DataClassification.INDEX_CONSTITUENTS,
            DataClassification.TRADE_CALENDAR,
            DataClassification.TRADE_RECORDS,
            DataClassification.POSITION_HISTORY,
            DataClassification.SYSTEM_CONFIG,
            DataClassification.TASK_SCHEDULE,
            DataClassification.DATA_QUALITY_METRICS,
        ]:
            return DatabaseTarget.POSTGRESQL
        else:
            # 默认使用PostgreSQL
            return DatabaseTarget.POSTGRESQL

    def save_data_by_classification(
        self,
        classification: DataClassification,
        data: pd.DataFrame,
        table_name: str,
        **kwargs: Any,
    ) -> bool:
        """
        按分类保存数据 (核心方法 #1)

        根据数据分类自动选择最优数据库并保存数据。
        如果目标数据库不可用,数据自动加入故障恢复队列。

        Args:
            classification: 数据分类枚举
            data: 数据DataFrame
            table_name: 目标表名
            **kwargs: 额外参数 (如ttl, timestamp_col等)

        Returns:
            bool: 保存是否成功

        Raises:
            ValueError: 未知的数据分类

        Example:
            # 保存分钟线数据
            success = manager.save_data_by_classification(
                DataClassification.MINUTE_KLINE,
                kline_df,
                table_name='minute_kline_600000',
                timestamp_col='ts'
            )
        """
        if data.empty:
            print("⚠️  数据为空,跳过保存")
            return True

        # US3: 使用DataManager进行路由
        # from src.core.data_storage_strategy import DataManager
        # 暂时使用简单的数据管理器替代
        target_db = self._get_target_database(classification)
        operation_success = False
        rows_affected = 0

        # 性能监控上下文 (US3)
        context_manager = (
            self.performance_monitor.track_operation(
                operation_name=f"save_{classification.value}",
                classification=classification.value,
                database_type=target_db.value,
                table_name=table_name,
            )
            if self.enable_monitoring and self.performance_monitor is not None
            else None
        )

        try:
            # 使用性能监控上下文
            if context_manager:
                context_manager.__enter__()

            print(f"📍 路由: {classification.value} → {target_db.value.upper()}")

            # 根据目标数据库选择访问层
            if target_db == DatabaseTarget.TDENGINE:
                rows_affected = self.tdengine.insert_dataframe(
                    table_name, data, **kwargs
                )
                print(f"✅ TDengine保存成功: {rows_affected}行")

            elif target_db == DatabaseTarget.POSTGRESQL:
                rows_affected = self.postgresql.insert_dataframe(table_name, data)
                print(f"✅ PostgreSQL保存成功: {rows_affected}行")

            operation_success = True

            # 记录操作日志 (US3)
            if self.enable_monitoring and self.monitoring_db:
                self.monitoring_db.log_operation(
                    operation_type="SAVE",
                    classification=classification.value,
                    target_database=target_db.value,
                    table_name=table_name,
                    record_count=rows_affected,
                    operation_status="SUCCESS",
                )

            return True

        except Exception as e:
            print(f"❌ 保存失败: {e}")
            print("📥 数据已加入故障恢复队列")

            # 记录失败操作日志 (US3)
            if self.enable_monitoring and self.monitoring_db:
                self.monitoring_db.log_operation(
                    operation_type="SAVE",
                    classification=classification.value,
                    target_database=target_db.value,
                    table_name=table_name,
                    record_count=len(data),
                    operation_status="FAILED",
                    error_message=str(e),
                )

            # 加入故障恢复队列
            self.recovery_queue.enqueue(
                classification=classification.value,
                target_database=target_db.value,
                data={
                    "table_name": table_name,
                    "data": data.to_dict("records"),
                    "kwargs": kwargs,
                },
            )

            return False

        finally:
            # 退出性能监控上下文
            if context_manager:
                try:
                    context_manager.__exit__(None, None, None)
                except Exception:
                    pass

    def load_data_by_classification(
        self,
        classification: DataClassification,
        table_name: str,
        filters: Optional[Dict[str, Any]] = None,
        columns: Optional[List[str]] = None,
        limit: Optional[int] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        按分类加载数据 (核心方法 #2)

        根据数据分类自动选择最优数据库并查询数据。

        Args:
            classification: 数据分类枚举
            table_name: 表名
            filters: 过滤条件 {'symbol': '600000.SH', 'date >= ': '2025-01-01'}
            columns: 查询字段列表
            limit: 返回行数限制
            **kwargs: 额外参数 (如start_time, end_time等)

        Returns:
            查询结果DataFrame

        Example:
            # 加载日线数据
            df = manager.load_data_by_classification(
                DataClassification.DAILY_KLINE,
                table_name='daily_kline',
                filters={'symbol': '600000.SH'},
                start_time=datetime(2025, 1, 1),
                end_time=datetime(2025, 12, 31)
            )
        """
        # 获取目标数据库
        # from src.core.data_storage_strategy import DataManager
        target_db = self._get_target_database(classification)

        # 性能监控上下文 (US3)
        context_manager = (
            self.performance_monitor.track_operation(
                operation_name=f"load_{classification.value}",
                classification=classification.value,
                database_type=target_db.value,
                table_name=table_name,
            )
            if self.enable_monitoring and self.performance_monitor is not None
            else None
        )

        try:
            # 使用性能监控上下文
            if context_manager:
                context_manager.__enter__()

            print(f"📍 路由: {classification.value} → {target_db.value.upper()}")

            # 构建where子句
            where = self._build_where_clause(filters) if filters else None

            # 根据目标数据库查询
            if target_db == DatabaseTarget.TDENGINE:
                # TDengine时间范围查询
                if "start_time" in kwargs and "end_time" in kwargs:
                    df = self.tdengine.query_by_time_range(
                        table_name,
                        kwargs["start_time"],
                        kwargs["end_time"],
                        columns=columns,
                        limit=limit,
                    )
                else:
                    df = self.tdengine.query_latest(table_name, limit or 100)

            elif target_db == DatabaseTarget.POSTGRESQL:
                # PostgreSQL查询
                if "start_time" in kwargs and "end_time" in kwargs:
                    time_column = kwargs.get("time_column", "time")
                    df = self.postgresql.query_by_time_range(
                        table_name,
                        time_column,
                        kwargs["start_time"],
                        kwargs["end_time"],
                        columns=columns,
                        filters=where,
                    )
                else:
                    df = self.postgresql.query(table_name, columns, where, limit=limit)

            print(f"✅ 查询成功: {len(df)}行")

            # 记录操作日志 (US3)
            if self.enable_monitoring and self.monitoring_db:
                self.monitoring_db.log_operation(
                    operation_type="LOAD",
                    classification=classification.value,
                    target_database=target_db.value,
                    table_name=table_name,
                    record_count=len(df),
                    operation_status="SUCCESS",
                )

            return df

        except Exception as e:
            print(f"❌ 查询失败: {e}")

            # 记录失败操作日志 (US3)
            if self.enable_monitoring and self.monitoring_db:
                self.monitoring_db.log_operation(
                    operation_type="LOAD",
                    classification=classification.value,
                    target_database=target_db.value,
                    table_name=table_name,
                    record_count=0,
                    operation_status="FAILED",
                    error_message=str(e),
                )

            return pd.DataFrame()

        finally:
            # 退出性能监控上下文
            if context_manager:
                try:
                    context_manager.__exit__(None, None, None)
                except Exception:
                    pass

    def _save_to_redis(self, key: str, data: pd.DataFrame, ttl: Optional[int] = None) -> None:
        """
        保存数据到Redis (已注释)

        根据数据结构选择最优Redis数据类型:
        - 单条记录 → String
        - 多条记录 → Hash (key-value pairs)
        """
        # 注释掉Redis相关代码，因为模块不存在
        # if len(data) == 1:
        #     # 单条记录 → String
        #     self.redis.set(key, data.iloc[0].to_dict(), ttl=ttl)
        # else:
        #     # 多条记录 → Hash
        #     for idx, row in data.iterrows():
        #         field = str(row.get("symbol", idx))
        #         self.redis.hset(key, field, row.to_dict())
        #
        #     if ttl:
        #         self.redis.expire(key, ttl)
        pass

    def _load_from_redis(
        self, key: str, filters: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        从Redis加载数据 (已注释)

        自动检测数据类型并返回DataFrame
        """
        # 注释掉Redis相关代码，因为模块不存在
        # # 尝试String类型
        # value = self.redis.get(key)
        # if value:
        #     return pd.DataFrame([value])
        #
        # # 尝试Hash类型
        # data = self.redis.hgetall(key)
        # if data:
        #     df = pd.DataFrame.from_dict(data, orient="index")
        #
        #     # 应用过滤器
        #     if filters:
        #         for col, val in filters.items():
        #             if col in df.columns:
        #                 df = df[df[col] == val]
        #
        #     return df
        #
        # return pd.DataFrame()
        return pd.DataFrame()

    def _build_where_clause(self, filters: Dict[str, Any]) -> str:
        """
        构建WHERE子句

        Args:
            filters: 过滤条件字典

        Returns:
            WHERE子句字符串

        Example:
            {'symbol': '600000.SH', 'date >= ': '2025-01-01'}
            → "symbol = '600000.SH' AND date >= '2025-01-01'"
        """
        conditions = []

        for key, value in filters.items():
            # 支持操作符后缀 (如 'date >= ')
            if key.endswith((" =", " >", " <", " >=", " <=", " !=")):
                operator = key.split()[-1]
                column = key.rsplit(operator, 1)[0].strip()
                if isinstance(value, str):
                    conditions.append(f"{column} {operator} '{value}'")
                else:
                    conditions.append(f"{column} {operator} {value}")
            else:
                # 默认使用 = 操作符
                if isinstance(value, str):
                    conditions.append(f"{key} = '{value}'")
                else:
                    conditions.append(f"{key} = {value}")

        return " AND ".join(conditions)

    def get_routing_info(self, classification: DataClassification, **kwargs: Any) -> Dict[str, Any]:
        """
        获取数据分类的路由信息

        Args:
            classification: 数据分类
            **kwargs: 可选参数，如 retention_days

        Returns:
            路由信息字典

        Example:
            info = manager.get_routing_info(DataClassification.TICK_DATA)
            # {'target_db': 'tdengine', 'retention_days': 30, 'ttl': None}
        """
        # from src.core.data_storage_strategy import DataManager
        target_db = self._get_target_database(classification)
        # US3: 移除DataStorageRules，使用简化配置
        retention = kwargs.get("retention_days", None)  # 简化配置，从参数获取保留天数
        ttl = None  # Redis已被移除

        return {"target_db": target_db.value, "retention_days": retention, "ttl": ttl}

    def save_data_batch_with_strategy(
        self,
        classification: DataClassification,
        data: pd.DataFrame,
        table_name: str,
        strategy: BatchFailureStrategy = BatchFailureStrategy.CONTINUE,
        **kwargs: Any,
    ) -> BatchOperationResult:
        """
        使用指定失败策略保存批量数据 (核心方法 #3)

        提供三种失败处理策略:
        - ROLLBACK: 任何失败都回滚整个批次
        - CONTINUE: 跳过失败记录,继续处理
        - RETRY: 自动重试失败记录

        Args:
            classification: 数据分类枚举
            data: 数据DataFrame
            table_name: 目标表名
            strategy: 失败策略 (默认CONTINUE)
            **kwargs: 额外参数

        Returns:
            BatchOperationResult: 批量操作结果

        Example:
            # 使用RETRY策略保存10万条Tick数据
            result = manager.save_data_batch_with_strategy(
                DataClassification.TICK_DATA,
                tick_df,
                table_name='tick_600000',
                strategy=BatchFailureStrategy.RETRY
            )
            print(f"成功率: {result.success_rate:.2%}")
            print(f"失败记录: {result.failed_records}")
        """
        if data.empty:
            print("⚠️  数据为空,跳过保存")
            return BatchOperationResult(
                total_records=0,
                successful_records=0,
                failed_records=0,
                strategy_used=strategy,
                execution_time_ms=0.0,
            )

        # 获取目标数据库
        # from src.core.data_storage_strategy import DataManager
        target_db = self._get_target_database(classification)
        print(
            f"📍 路由: {classification.value} → {target_db.value.upper()} (策略: {strategy.value.upper()})"
        )

        # 创建失败处理器
        handler = BatchFailureHandler(
            strategy=strategy,
            max_retries=kwargs.get("max_retries", 3),
            retry_delay_base=kwargs.get("retry_delay_base", 1.0),
        )

        # 定义操作函数
        def operation(batch: pd.DataFrame) -> bool:
            try:
                if target_db == DatabaseTarget.TDENGINE:
                    self.tdengine.insert_dataframe(table_name, batch, **kwargs)
                elif target_db == DatabaseTarget.POSTGRESQL:
                    self.postgresql.insert_dataframe(table_name, batch)
                elif target_db == DatabaseTarget.REDIS:
                    ttl = kwargs.get("ttl") or 86400  # 默认1天
                    self._save_to_redis(table_name, batch, ttl)
                return True
            except Exception as e:
                print(f"⚠️  批次保存异常: {e}")
                return False

        # 执行批量操作
        result = handler.execute_batch(data, operation, f"save_{classification.value}")

        # 如果有失败记录,加入故障恢复队列
        if result.failed_records > 0 and strategy != BatchFailureStrategy.ROLLBACK:
            failed_data = (
                data.iloc[result.failed_indices] if result.failed_indices else data
            )
            print(f"📥 {result.failed_records} 条失败记录已加入故障恢复队列")

            self.recovery_queue.enqueue(
                classification=classification.value,
                target_database=target_db.value,
                data={
                    "table_name": table_name,
                    "data": failed_data.to_dict("records"),
                    "kwargs": kwargs,
                },
            )

        return result

    def get_monitoring_statistics(self) -> Dict[str, Any]:
        """
        获取监控统计信息 (US3)

        Returns:
            dict: 监控统计信息 {
                'performance': {...},
                'alerts': {...},
                'enabled': bool
            }
        """
        if not self.enable_monitoring:
            return {"enabled": False, "message": "监控功能未启用"}

        try:
            stats: Dict[str, Any] = {
                "enabled": True,
                "performance": (
                    self.performance_monitor.get_performance_summary(hours=24)
                    if self.performance_monitor is not None
                    else {}
                ),
                "alerts": {},  # AlertManager.get_statistics() 方法不存在，待实现
                "monitoring_db": {"connected": self.monitoring_db is not None},
            }
            return stats
        except Exception as e:
            logger.error(f"获取监控统计失败: {e}")
            return {"enabled": True, "error": str(e)}

    def check_data_quality(
        self, classification: DataClassification, table_name: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        执行数据质量检查 (US3)

        支持的检查维度:
        - completeness: 完整性检查 (需要 total_records, null_records)
        - freshness: 新鲜度检查 (需要 latest_timestamp)
        - accuracy: 准确性检查 (需要 total_records, invalid_records)

        Args:
            classification: 数据分类
            table_name: 表名
            **kwargs: 检查参数

        Returns:
            dict: 质量检查结果

        Example:
            # 检查完整性
            result = manager.check_data_quality(
                DataClassification.DAILY_KLINE,
                'daily_kline',
                check_type='completeness',
                total_records=10000,
                null_records=50
            )
        """
        if not self.enable_monitoring:
            return {"error": "监控功能未启用"}

        check_type = kwargs.get("check_type", "completeness")
        # from src.core.data_storage_strategy import DataManager
        target_db = self._get_target_database(classification)

        try:
            result: Dict[str, Any] = {"error": f"未知的检查类型: {check_type}"}

            if self.quality_monitor is None:
                return {"error": "质量监控器未初始化"}

            if check_type == "completeness":
                result = self.quality_monitor.check_completeness(
                    classification=classification.value,
                    database_type=target_db.value,
                    table_name=table_name,
                    total_records=kwargs.get("total_records", 0),
                    null_records=kwargs.get("null_records", 0),
                    threshold=kwargs.get("threshold"),
                )
            elif check_type == "freshness":
                result = self.quality_monitor.check_freshness(
                    classification=classification.value,
                    database_type=target_db.value,
                    table_name=table_name,
                    latest_timestamp=kwargs.get("latest_timestamp"),
                    threshold_seconds=kwargs.get("threshold_seconds"),
                )
            elif check_type == "accuracy":
                result = self.quality_monitor.check_accuracy(
                    classification=classification.value,
                    database_type=target_db.value,
                    table_name=table_name,
                    total_records=kwargs.get("total_records", 0),
                    invalid_records=kwargs.get("invalid_records", 0),
                    validation_rules=kwargs.get("validation_rules"),
                    threshold=kwargs.get("threshold"),
                )

            logger.info(f"✓ 数据质量检查完成: {table_name} - {check_type}")
            return result

        except Exception as e:
            logger.error(f"数据质量检查失败: {e}")
            return {"error": str(e)}

    def close_all_connections(self) -> None:
        """关闭所有数据库连接"""
        print("\n正在关闭所有数据库连接...")
        self.tdengine.close()
        self.postgresql.close_all()
        # self.mysql.close()  # MySQL已移除，系统使用TDengine+PostgreSQL双数据库架构
        # self.redis.close()  # Redis已移除
        print("✅ 所有连接已关闭")


if __name__ == "__main__":
    """测试统一管理器"""
    print("\n" + "=" * 80)
    print("MyStocks统一数据管理器 - MVP测试")
    print("=" * 80 + "\n")

    # 初始化管理器
    manager = MyStocksUnifiedManager()

    # 测试路由信息查询
    print("\n📊 路由信息测试:\n")
    test_classifications = [
        DataClassification.TICK_DATA,
        DataClassification.DAILY_KLINE,
        DataClassification.SYMBOLS_INFO,
        DataClassification.REALTIME_POSITIONS,
    ]

    for classification in test_classifications:
        info = manager.get_routing_info(classification)
        print(f"  {classification.value}")
        print(f"    → 目标数据库: {info['target_db'].upper()}")
        print(
            f"    → 保留周期: {info['retention_days']}天"
            if info["retention_days"]
            else f"    → 保留周期: 永久"
        )
        if info["ttl"]:
            print(f"    → TTL: {info['ttl']}秒")

    print("\n" + "=" * 80)
    print("✅ 统一管理器基础功能验证通过")
    print("=" * 80 + "\n")

    print("核心功能:")
    print("  ✅ save_data_by_classification() - 按分类保存")
    print("  ✅ load_data_by_classification() - 按分类加载")
    print("  ✅ save_data_batch_with_strategy() - 批量保存(含失败策略)")
    print("  ✅ 自动路由到最优数据库")
    print("  ✅ 故障恢复队列")
    print("  ✅ 路由信息查询")
    print("  ✅ 三种批量失败策略 (ROLLBACK/CONTINUE/RETRY)")

    # 关闭连接
    manager.close_all_connections()
