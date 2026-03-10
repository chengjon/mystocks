"""Metrics helpers for the data adapter."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional


class DataAdapterMetricsMixin:
    """Shared metrics helpers for `DataDataSourceAdapter`."""

    def get_metrics(self) -> Dict[str, Any]:
        success_rate = (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "error_count": self.error_count,
            "success_rate": success_rate,
            "last_response_time_ms": self.last_response_time,
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl,
            "source_type": self.source_type,
            "name": self.name,
        }

    def _update_metrics(self, success: bool, response_time: float, error: Optional[str] = None) -> None:
        self.metrics.total_requests += 1
        self.metrics.last_check = datetime.now()

        if success:
            if self.metrics.response_time == 0:
                self.metrics.response_time = response_time
            else:
                alpha = 0.3
                self.metrics.response_time = alpha * response_time + (1 - alpha) * self.metrics.response_time
        else:
            self.metrics.error_count += 1
            self.metrics.last_error = error

        if self.metrics.total_requests > 0:
            self.metrics.success_rate = (
                (self.metrics.total_requests - self.metrics.error_count) / self.metrics.total_requests * 100
            )
        self.metrics.availability = self.metrics.success_rate

    async def close(self) -> None:
        """关闭连接和清理资源。"""
