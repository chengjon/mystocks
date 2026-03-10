"""
# 功能：监控数据库模块，独立记录所有操作日志和指标
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025
"""

import logging
from datetime import datetime
from typing import Any, Dict, List


logger = logging.getLogger(__name__)


class MonitoringDatabaseHistoryMixin:
    """MonitoringDatabase 方法集 Part 3"""

    async def get_metrics_history(
        self, metric_name: str, start_time: datetime, end_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        获取指标历史数据

        Args:
            metric_name: 指标名称
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            List[Dict]: 指标历史记录列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT timestamp, value
                    FROM performance_metrics
                    WHERE metric_name = %s
                        AND timestamp >= %s
                        AND timestamp <= %s
                    ORDER BY timestamp ASC
                    """,
                    (metric_name, start_time, end_time),
                )

                records = cursor.fetchall()
                cursor.close()

                return [{"timestamp": r[0], "value": r[1]} for r in records]

        except Exception:
            logger.error("获取指标历史数据失败: %(e)s")
            return []

    async def save_threshold_adjustment(self, adjustment: Dict[str, Any]) -> bool:
        """
        保存阈值调整记录

        Args:
            adjustment: 调整记录字典 {
                'rule_name': str,
                'metric_name': str,
                'old_value': float,
                'new_value': float,
                'adjustment_type': str,
                'reason': str,
                'timestamp': datetime
            }

        Returns:
            bool: 保存是否成功
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO threshold_adjustments (
                        rule_name, metric_name, old_value, new_value,
                        adjustment_type, reason, timestamp
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        adjustment.get("rule_name"),
                        adjustment.get("metric_name"),
                        adjustment.get("old_value"),
                        adjustment.get("new_value"),
                        adjustment.get("adjustment_type"),
                        adjustment.get("reason"),
                        adjustment.get("timestamp", datetime.now()),
                    ),
                )

                cursor.close()

            return True

        except Exception:
            logger.error("保存阈值调整记录失败: %(e)s")
            return False
