"""IntegratedRealTimeService 统计辅助方法。"""

from __future__ import annotations

import json
import logging
from datetime import datetime

import grpc


logger = logging.getLogger(__name__)


class IntegratedRealTimeServiceStatsMixin:
    """流统计相关方法集。"""

    def GetStreamStats(self, request, context):
        """获取流统计信息。"""
        try:
            with self.stream_lock:
                active_stream_count = len(self.active_streams)
                sum(stream["data_count"] for stream in self.active_streams.values())

            stats = {
                "timestamp": datetime.now().isoformat(),
                "active_streams": active_stream_count,
                "total_data_points": self.stats["total_data_points"],
                "total_features_computed": self.stats["total_features_computed"],
                "cache_hit_rate": (
                    self.stats["cache_hits"] / (self.stats["cache_hits"] + self.stats["cache_misses"]) * 100
                    if (self.stats["cache_hits"] + self.stats["cache_misses"]) > 0
                    else 0
                ),
                "gpu_computation_ratio": (
                    self.stats["gpu_computations"]
                    / (self.stats["gpu_computations"] + self.stats["cpu_computations"])
                    * 100
                    if (self.stats["gpu_computations"] + self.stats["cpu_computations"]) > 0
                    else 0
                ),
                "data_buffer_count": len(self.data_buffers),
                "feature_cache_count": len(self.feature_cache),
            }

            return json.dumps(stats, ensure_ascii=False)

        except Exception as e:
            logger.error("获取流统计失败: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")
            return json.dumps({"error": str(e)})
