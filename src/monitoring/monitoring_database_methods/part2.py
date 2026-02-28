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
from datetime import datetime, timedelta
from typing import Dict, Optional


logger = logging.getLogger(__name__)


class MonitoringDatabaseCleanupOldRecordsMixin:
    """MonitoringDatabase 方法集 Part 2"""

    def cleanup_old_records(self, days_to_keep: Optional[Dict[str, int]] = None) -> Dict[str, int]:
        """
        清理过期记录

        Args:
            days_to_keep: 各表保留天数配置 {
                'operation_logs': 30,
                'performance_metrics': 90,
                'data_quality_checks': 7,
                'alert_records': 90
            }

        Returns:
            dict: 各表删除的记录数
        """
        if not self.enable_monitoring:
            return {}

        if days_to_keep is None:
            days_to_keep = {
                "operation_logs": 30,
                "performance_metrics": 90,
                "data_quality_checks": 7,
                "alert_records": 90,
            }

        deleted_counts = {}

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                for table_name, days in days_to_keep.items():
                    cutoff_date = datetime.now() - timedelta(days=days)

                    cursor.execute(
                        f"""
                        DELETE FROM {table_name}
                        WHERE created_at < %s
                    """,
                        (cutoff_date,),
                    )

                    deleted_counts[table_name] = cursor.rowcount
                    logger.info("清理 %s: 删除 %s 条记录 (>%s天)", table_name, cursor.rowcount, days)

                cursor.close()

            return deleted_counts

        except Exception as e:
            logger.error("清理过期记录失败: %s", e)
            return deleted_counts

