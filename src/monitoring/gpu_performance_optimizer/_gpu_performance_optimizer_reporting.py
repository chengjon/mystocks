#!/usr/bin/env python3
"""
GPUPerformanceOptimizer reporting mixin compatibility layer.
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class GPUPerformanceOptimizerReportingMixin:
    """Provide lightweight reporting/persistence helpers for the optimizer."""

    async def get_performance_report(self) -> Dict[str, Any]:
        current_metrics = await self._collect_gpu_metrics()
        optimization_count = len(getattr(self, "optimization_history", []))
        current_dict = asdict(current_metrics) if is_dataclass(current_metrics) else dict(current_metrics)
        if isinstance(current_dict.get("timestamp"), datetime):
            current_dict["timestamp"] = current_dict["timestamp"].isoformat()

        return {
            "timestamp": datetime.now().isoformat(),
            "gpu_available": getattr(self, "gpu_available", False),
            "current_metrics": current_dict,
            "optimization_stats": getattr(self, "optimization_stats", {}),
            "adaptive_params": getattr(self, "adaptive_params", {}),
            "recommendations": self._build_recommendations(current_metrics),
            "optimization_count": optimization_count,
        }

    def save_optimization_state(self, file_path: str) -> None:
        state = {
            "timestamp": datetime.now().isoformat(),
            "gpu_available": getattr(self, "gpu_available", False),
            "optimization_stats": getattr(self, "optimization_stats", {}),
            "adaptive_params": getattr(self, "adaptive_params", {}),
        }
        Path(file_path).write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    def _build_recommendations(self, metrics) -> list[str]:
        recommendations: list[str] = []
        gpu_utilization = getattr(metrics, "gpu_utilization", 0.0)
        memory_utilization = getattr(metrics, "gpu_memory_utilization", 0.0)

        if gpu_utilization < 40:
            recommendations.append("GPU 利用率偏低，可考虑增加批处理规模")
        if memory_utilization > 85:
            recommendations.append("GPU 显存占用偏高，建议执行内存回收或降低批量大小")
        if not recommendations:
            recommendations.append("当前 GPU 性能状态稳定，无额外优化建议")

        return recommendations
