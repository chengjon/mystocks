"""IntegratedBacktestService 统计方法集。"""

from __future__ import annotations

import json
import logging
from datetime import datetime

import grpc


logger = logging.getLogger(__name__)


class IntegratedBacktestServiceStatsMixin:
    """回测统计方法。"""

    def GetIntegratedBacktestStats(self, request, context):
        """获取集成回测统计信息。"""
        try:
            with self.backtest_lock:
                running_count = len(self.running_backtests)
                gpu_accelerated_count = sum(
                    1 for info in self.running_backtests.values() if info.get("gpu_accelerated", False)
                )

            stats = {
                "timestamp": datetime.now().isoformat(),
                "running_backtests": running_count,
                "gpu_accelerated_backtests": gpu_accelerated_count,
                "total_backtests": len(self.running_backtests),
                "gpu_utilization": self.gpu_manager.get_gpu_stats().get("utilization", 0),
                "cache_hit_rate": self.cache_manager.get_cache_performance_report()
                .get("cache_stats", {})
                .get("overall_hit_rate", 0),
                "system_status": ("healthy" if running_count < self.config["max_concurrent_backtests"] else "busy"),
            }

            return json.dumps(stats, ensure_ascii=False)

        except Exception as e:
            logger.error("获取集成回测统计失败: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")
            return json.dumps({"error": str(e)})
