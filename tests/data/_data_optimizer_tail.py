#!/usr/bin/env python3
"""Tail mixin extracted from `tests/data/test_data_optimizer.py`."""

import statistics
from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Dict, List


class TestDataOptimizerTailMixin:
    """Support methods extracted from `TestDataOptimizer`."""

    async def _manage_lifecycle(self, profile_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """管理数据生命周期"""
        retention_days = parameters.get("retention_days", 30)

        test_data = await self.data_manager.get_test_data(profile_name)
        if not test_data:
            return {
                "strategy": "lifecycle_management",
                "status": "skipped",
                "reason": "no_data",
            }

        current_time = datetime.now()
        cutoff_date = current_time - timedelta(days=retention_days)
        expired_data = []
        current_data = []

        for record in test_data:
            timestamp = record.get("timestamp")
            if timestamp:
                try:
                    if isinstance(timestamp, str):
                        record_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    elif isinstance(timestamp, (int, float)):
                        record_time = datetime.fromtimestamp(timestamp)
                    else:
                        current_data.append(record)
                        continue

                    if record_time < cutoff_date:
                        expired_data.append(record)
                    else:
                        current_data.append(record)
                except Exception:
                    current_data.append(record)
            else:
                current_data.append(record)

        await self.data_manager.update_test_data(profile_name, current_data)

        return {
            "strategy": "lifecycle_management",
            "status": "completed",
            "retention_days": retention_days,
            "total_records": len(test_data),
            "current_records": len(current_data),
            "expired_records": len(expired_data),
            "retention_ratio": len(current_data) / len(test_data) if test_data else 0,
        }

    def _summarize_optimization_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """汇总优化结果"""
        summary = {
            "total_strategies": len(results),
            "successful_strategies": 0,
            "failed_strategies": 0,
            "skipped_strategies": 0,
            "total_time_saved": 0,
            "total_space_saved": 0,
            "overall_improvement": 0,
        }

        for result in results:
            status = result.get("status", "unknown")
            if status == "completed":
                summary["successful_strategies"] += 1
                summary["total_time_saved"] += result.get("time_taken", 0)
                summary["total_space_saved"] += result.get("space_saved", 0)
                summary["overall_improvement"] += result.get("improvement", 0)
            elif status == "error":
                summary["failed_strategies"] += 1
            elif status == "skipped":
                summary["skipped_strategies"] += 1

        return summary

    def _calculate_quality_improvement(self, initial: Any, final: Any) -> float:
        """计算质量改进"""
        return final.overall_quality - initial.overall_quality

    def _generate_recommendations(self, initial: Any, final: Any) -> List[str]:
        """生成优化建议"""
        recommendations = []

        if initial.duplicate_ratio > 0.1:
            recommendations.append("考虑增加数据去重频率以减少存储空间")
        if final.completeness_score < 0.8:
            recommendations.append("数据完整性有待提升，建议完善缺失字段")
        if final.consistency_score < 0.8:
            recommendations.append("检测到数据一致性问题，建议加强数据验证")
        if final.accuracy_score < 0.8:
            recommendations.append("数据准确性需要改进，建议添加数据清洗规则")
        if final.timeliness_score < 0.5:
            recommendations.append("数据时效性较差，建议优化数据更新策略")
        if not recommendations:
            recommendations.append("数据质量良好，继续保持当前维护策略")

        return recommendations

    async def get_optimization_statistics(self) -> Dict[str, Any]:
        """获取优化统计信息"""
        if not self.optimization_history:
            return {"message": "暂无优化历史"}

        total_optimizations = len(self.optimization_history)
        successful_optimizations = sum(1 for item in self.optimization_history if item.get("status") != "failed")
        failed_optimizations = total_optimizations - successful_optimizations

        improvements = [item.get("quality_improvement", 0) for item in self.optimization_history]
        avg_improvement = statistics.mean(improvements) if improvements else 0

        strategy_usage = Counter()
        for item in self.optimization_history:
            for strategy in item.get("strategies_applied", []):
                strategy_usage[strategy] += 1

        return {
            "total_optimizations": total_optimizations,
            "successful_optimizations": successful_optimizations,
            "failed_optimizations": failed_optimizations,
            "success_rate": successful_optimizations / total_optimizations if total_optimizations > 0 else 0,
            "average_quality_improvement": avg_improvement,
            "most_used_strategies": strategy_usage.most_common(),
            "baseline_qualities": {
                profile: metrics.overall_quality for profile, metrics in self.quality_baseline.items()
            },
        }

    async def cleanup_optimization_cache(self) -> Dict[str, Any]:
        """清理优化缓存"""
        cache_size_before = len(self.compression_cache)
        cutoff_time = datetime.now() - timedelta(days=7)
        keys_to_remove = []

        for key in self.compression_cache:
            try:
                profile_name = key.split("_")[0]
                if profile_name in self.quality_baseline:
                    last_optimization = None
                    for item in self.optimization_history:
                        if item["profile_name"] == profile_name:
                            last_optimization = item["end_time"]
                            break
                    if last_optimization:
                        opt_time = datetime.fromisoformat(last_optimization)
                        if opt_time < cutoff_time:
                            keys_to_remove.append(key)
            except Exception:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.compression_cache[key]

        cache_size_after = len(self.compression_cache)
        return {
            "cache_size_before": cache_size_before,
            "cache_size_after": cache_size_after,
            "cleaned_entries": cache_size_before - cache_size_after,
            "compression_cache": self.compression_cache,
        }
