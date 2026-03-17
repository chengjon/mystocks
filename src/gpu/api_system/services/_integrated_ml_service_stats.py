"""IntegratedMLService 统计方法集。"""

from __future__ import annotations

import json
import logging
from datetime import datetime

import grpc


logger = logging.getLogger(__name__)


class IntegratedMLServiceStatsMixin:
    """ML 统计方法。"""

    def GetMLStats(self, request, context):
        """获取ML统计信息。"""
        try:
            with self.task_lock:
                active_training_count = sum(1 for task in self.training_tasks.values() if task["status"] == "training")

            stats = {
                "timestamp": datetime.now().isoformat(),
                "total_models_trained": self.stats["total_models_trained"],
                "total_predictions": self.stats["total_predictions"],
                "active_training_tasks": active_training_count,
                "total_models": len(self.models),
                "gpu_training_ratio": (
                    self.stats["gpu_training_count"]
                    / (self.stats["gpu_training_count"] + self.stats["cpu_training_count"])
                    * 100
                    if (self.stats["gpu_training_count"] + self.stats["cpu_training_count"]) > 0
                    else 0
                ),
                "gpu_utilization": self.gpu_manager.get_gpu_stats().get("utilization", 0),
            }
            return json.dumps(stats, ensure_ascii=False)

        except Exception as e:
            logger.error("获取ML统计失败: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")
            return json.dumps({"error": str(e)})
