"""Singleton helpers for `data_quality_monitor.py`."""

from __future__ import annotations

from typing import Any, Dict, Optional

from app.services.data_quality_monitor import DataQualityMonitor


_global_monitor: Optional[DataQualityMonitor] = None


def get_data_quality_monitor() -> DataQualityMonitor:
    """获取全局数据质量监控实例"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = DataQualityMonitor()
    return _global_monitor


async def monitor_data_quality(
    data: Any, source: str, response_time: Optional[float] = None, success: bool = True,
) -> Dict[str, Any]:
    """便捷函数：监控数据质量"""
    monitor = get_data_quality_monitor()
    return await monitor.evaluate_data_quality(data, source, response_time, success)
