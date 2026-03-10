#!/usr/bin/env python3
"""Tail mixin extracted from `tests/performance/test_stress_test.py`."""

import json
from datetime import datetime
from typing import Any, Dict, List

import numpy as np


class StressTestSuiteTailMixin:
    """Support methods extracted from `StressTestSuite`."""

    def _generate_stress_test_report(self) -> str:
        """生成压力测试报告"""
        total_duration = (self.result.end_time - self.result.start_time).total_seconds()

        if self.result.response_times:
            avg_response_time = sum(self.result.response_times) / len(self.result.response_times)
            max_response_time = max(self.result.response_times)
            min_response_time = min(self.result.response_times)
            p95_response_time = np.percentile(self.result.response_times, 95)
            p99_response_time = np.percentile(self.result.response_times, 99)
        else:
            avg_response_time = 0
            max_response_time = 0
            min_response_time = 0
            p95_response_time = 0
            p99_response_time = 0

        tps = self.result.total_requests / total_duration if total_duration > 0 else 0

        report_data = {
            "test_summary": {
                "test_type": self.config.test_type.value,
                "start_time": self.result.start_time.isoformat(),
                "end_time": self.result.end_time.isoformat(),
                "duration_seconds": round(total_duration, 2),
                "total_requests": self.result.total_requests,
                "successful_requests": self.result.successful_requests,
                "failed_requests": self.result.failed_requests,
                "breakpoint": self.result.breaking_point,
                "recovery_point": self.result.recovery_point,
            },
            "performance_metrics": {
                "tps": round(tps, 2),
                "success_rate_percent": round(
                    (self.result.successful_requests / max(self.result.total_requests, 1)) * 100,
                    2,
                ),
                "avg_response_time_ms": round(avg_response_time, 2),
                "max_response_time_ms": round(max_response_time, 2),
                "min_response_time_ms": round(min_response_time, 2),
                "p95_response_time_ms": round(p95_response_time, 2),
                "p99_response_time_ms": round(p99_response_time, 2),
            },
            "error_analysis": {
                "total_errors": len(self.result.error_messages),
                "error_messages": self.result.error_messages[:10],
                "most_common_errors": self._get_most_common_errors(),
            },
            "system_metrics": self.result.system_metrics,
            "test_conclusions": self._generate_test_conclusions(),
        }

        report_path = f"/tmp/stress_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w", encoding="utf-8") as file_handle:
            json.dump(report_data, file_handle, ensure_ascii=False, indent=2)

        return report_path

    def _get_most_common_errors(self) -> List[Dict[str, Any]]:
        """获取最常见的错误"""
        error_counts = {}
        for error in self.result.error_messages:
            error_counts[error] = error_counts.get(error, 0) + 1

        return [
            {"error": error, "count": count}
            for error, count in sorted(error_counts.items(), key=lambda item: item[1], reverse=True)[:5]
        ]

    def _generate_test_conclusions(self) -> List[str]:
        """生成测试结论"""
        conclusions = []
        success_rate = self.result.successful_requests / max(self.result.total_requests, 1)

        if success_rate >= 0.95:
            conclusions.append(f"✅ 系统表现优秀，成功率 {success_rate * 100:.1f}%")
        elif success_rate >= 0.8:
            conclusions.append(f"⚠️  系统表现一般，成功率 {success_rate * 100:.1f}%")
        else:
            conclusions.append(f"❌ 系统表现不佳，成功率 {success_rate * 100:.1f}%")

        if self.result.breaking_point:
            conclusions.append(f"🚫 系统断点在 {self.result.breaking_point} 用户")
            if self.result.recovery_point:
                conclusions.append(f"🔄 系统恢复点在 {self.result.recovery_point} 用户")

        if self.result.response_times:
            avg_time = sum(self.result.response_times) / len(self.result.response_times)
            if avg_time > self.config.response_time_threshold * 1000:
                conclusions.append(f"⏱️  响应时间过长，平均 {avg_time:.0f}ms")

        return conclusions
