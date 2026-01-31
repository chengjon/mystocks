#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据优化器

提供智能的测试数据管理、优化和分析功能，包括：
- 数据去重和压缩
- 数据质量分析
- 数据生成策略优化
- 数据生命周期管理
"""

import asyncio
import hashlib
import json
import logging
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List

import numpy as np

from ..ai.test_data_analyzer import AITestDataAnalyzer
from ..ai.test_data_manager import AITestDataManager

logger = logging.getLogger(__name__)


@dataclass
class DataQualityMetrics:
    """数据质量指标"""

    total_records: int = 0
    unique_records: int = 0
    duplicate_ratio: float = 0.0
    completeness_score: float = 0.0
    consistency_score: float = 0.0
    accuracy_score: float = 0.0
    timeliness_score: float = 0.0
    overall_quality: float = 0.0


@dataclass
class CompressionResult:
    """压缩结果"""

    original_size: int
    compressed_size: int
    compression_ratio: float
    time_taken: float
    method_used: str
    records_removed: int = 0


@dataclass
class DataOptimizationStrategy:
    """数据优化策略"""

    name: str
    description: str
    priority: int = 1
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)
    estimated_improvement: float = 0.0


class TestDataOptimizer:
    """测试数据优化器"""

    def __init__(self, data_manager: AITestDataManager):
        self.data_manager = data_manager
        self.analyzer = AITestDataAnalyzer()
        self.optimization_history: List[Dict[str, Any]] = []
        self.compression_cache: Dict[str, bytes] = {}
        self.quality_baseline: Dict[str, DataQualityMetrics] = {}

        # 预定义的优化策略
        self.strategies = self._initialize_strategies()

        # 数据统计
        self.data_statistics = defaultdict(dict)

    def _initialize_strategies(self) -> List[DataOptimizationStrategy]:
        """初始化优化策略"""
        return [
            DataOptimizationStrategy(
                name="duplicate_removal",
                description="移除重复数据记录",
                priority=1,
                enabled=True,
                parameters={"threshold": 0.95},
                estimated_improvement=0.3,
            ),
            DataOptimizationStrategy(
                name="data_compression",
                description="压缩测试数据",
                priority=2,
                enabled=True,
                parameters={"algorithm": "zlib", "level": 6},
                estimated_improvement=0.5,
            ),
            DataOptimizationStrategy(
                name="quality_enhancement",
                description="提升数据质量",
                priority=3,
                enabled=True,
                parameters={"target_quality": 0.9},
                estimated_improvement=0.4,
            ),
            DataOptimizationStrategy(
                name="data_synthesis",
                description="生成合成数据",
                priority=4,
                enabled=True,
                parameters={"synthesis_ratio": 0.1},
                estimated_improvement=0.2,
            ),
            DataOptimizationStrategy(
                name="lifecycle_management",
                description="数据生命周期管理",
                priority=5,
                enabled=True,
                parameters={"retention_days": 30},
                estimated_improvement=0.1,
            ),
        ]

    async def optimize_test_data(self, profile_name: str) -> Dict[str, Any]:
        """优化测试数据"""
        logger.info("开始优化测试数据档案: %(profile_name)s")

        start_time = datetime.now()

        try:
            # 1. 分析当前数据质量
            current_quality = await self.analyze_data_quality(profile_name)
            self.quality_baseline[profile_name] = current_quality

            # 2. 选择并执行优化策略
            optimization_tasks = []
            for strategy in self.strategies:
                if strategy.enabled:
                    task = self._execute_strategy(strategy, profile_name, current_quality)
                    optimization_tasks.append(task)

            # 并行执行优化策略
            results = await asyncio.gather(*optimization_tasks, return_exceptions=True)

            # 3. 汇总优化结果
            optimization_summary = self._summarize_optimization_results(results)

            # 4. 验证优化效果
            final_quality = await self.analyze_data_quality(profile_name)
            improvement = self._calculate_quality_improvement(current_quality, final_quality)

            # 5. 生成优化报告
            optimization_report = {
                "profile_name": profile_name,
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration": (datetime.now() - start_time).total_seconds(),
                "initial_quality": current_quality.__dict__,
                "final_quality": final_quality.__dict__,
                "quality_improvement": improvement,
                "optimization_summary": optimization_summary,
                "strategies_applied": [s.name for s in self.strategies if s.enabled],
                "recommendations": self._generate_recommendations(current_quality, final_quality),
            }

            # 保存优化历史
            self.optimization_history.append(optimization_report)

            logger.info("测试数据优化完成: %(profile_name)s")
            return optimization_report

        except Exception as e:
            logger.error("优化测试数据失败: %(e)s")
            return {"profile_name": profile_name, "error": str(e), "status": "failed"}

    async def analyze_data_quality(self, profile_name: str) -> DataQualityMetrics:
        """分析数据质量"""
        try:
            # 获取测试数据
            test_data = await self.data_manager.get_test_data(profile_name)

            if not test_data:
                return DataQualityMetrics()

            # 计算各种质量指标
            metrics = DataQualityMetrics(total_records=len(test_data))

            # 1. 唯一性分析
            unique_records = len(set(json.dumps(record, sort_keys=True) for record in test_data))
            metrics.unique_records = unique_records
            metrics.duplicate_ratio = (
                (metrics.total_records - unique_records) / metrics.total_records if metrics.total_records > 0 else 0
            )

            # 2. 完整性分析
            completeness_scores = []
            for record in test_data:
                score = self._calculate_completeness_score(record)
                completeness_scores.append(score)
            metrics.completeness_score = statistics.mean(completeness_scores) if completeness_scores else 0

            # 3. 一致性分析
            consistency_scores = []
            for record in test_data:
                score = self._calculate_consistency_score(record)
                consistency_scores.append(score)
            metrics.consistency_score = statistics.mean(consistency_scores) if consistency_scores else 0

            # 4. 准确性分析
            accuracy_scores = []
            for record in test_data:
                score = self._calculate_accuracy_score(record)
                accuracy_scores.append(score)
            metrics.accuracy_score = statistics.mean(accuracy_scores) if accuracy_scores else 0

            # 5. 时效性分析
            timeliness_scores = []
            current_time = datetime.now()
            for record in test_data:
                if "timestamp" in record:
                    score = self._calculate_timeliness_score(record["timestamp"], current_time)
                    timeliness_scores.append(score)
            metrics.timeliness_score = statistics.mean(timeliness_scores) if timeliness_scores else 0

            # 计算总体质量分数
            weights = {
                "completeness": 0.3,
                "consistency": 0.2,
                "accuracy": 0.3,
                "timeliness": 0.2,
            }

            metrics.overall_quality = (
                metrics.completeness_score * weights["completeness"]
                + metrics.consistency_score * weights["consistency"]
                + metrics.accuracy_score * weights["accuracy"]
                + metrics.timeliness_score * weights["timeliness"]
            )

            return metrics

        except Exception as e:
            logger.error("分析数据质量失败: %(e)s")
            return DataQualityMetrics()

    def _calculate_completeness_score(self, record: Dict[str, Any]) -> float:
        """计算完整性得分"""
        if not record:
            return 0.0

        # 假设重要字段
        important_fields = ["id", "name", "value", "timestamp"]
        present_fields = sum(1 for field in important_fields if field in record)

        return present_fields / len(important_fields)

    def _calculate_consistency_score(self, record: Dict[str, Any]) -> float:
        """计算一致性得分"""
        if not record:
            return 0.0

        score = 1.0
        issues = 0

        # 检查数据类型一致性
        for key, value in record.items():
            if key == "id" and not isinstance(value, (int, str)):
                issues += 1
            elif key == "value" and not isinstance(value, (int, float)):
                issues += 1
            elif key == "timestamp" and not isinstance(value, (str, int, float)):
                issues += 1

        return max(0, 1 - issues / len(record))

    def _calculate_accuracy_score(self, record: Dict[str, Any]) -> float:
        """计算准确性得分"""
        # 简化的准确性检查
        score = 1.0

        # 检查数值范围
        if "value" in record:
            value = record["value"]
            if isinstance(value, (int, float)):
                if value < 0 or value > 1e12:  # 合理的范围检查
                    score -= 0.3

        # 检查字符串长度
        if "name" in record and isinstance(record["name"], str):
            if len(record["name"]) > 1000:
                score -= 0.2

        return max(0, score)

    def _calculate_timeliness_score(self, timestamp: Any, current_time: datetime) -> float:
        """计算时效性得分"""
        try:
            # 解析时间戳
            if isinstance(timestamp, str):
                record_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            elif isinstance(timestamp, (int, float)):
                record_time = datetime.fromtimestamp(timestamp)
            else:
                return 0.0

            # 计算时间差
            time_diff = current_time - record_time
            days_diff = time_diff.total_seconds() / (24 * 3600)

            # 根据时间差给出得分
            if days_diff < 1:
                return 1.0
            elif days_diff < 7:
                return 0.8
            elif days_diff < 30:
                return 0.5
            else:
                return max(0, 1 - days_diff / 365)

        except Exception:
            return 0.0

    async def _execute_strategy(
        self,
        strategy: DataOptimizationStrategy,
        profile_name: str,
        current_quality: DataQualityMetrics,
    ) -> Dict[str, Any]:
        """执行优化策略"""
        try:
            if strategy.name == "duplicate_removal":
                return await self._remove_duplicates(profile_name, strategy.parameters)
            elif strategy.name == "data_compression":
                return await self._compress_data(profile_name, strategy.parameters)
            elif strategy.name == "quality_enhancement":
                return await self._enhance_data_quality(profile_name, strategy.parameters, current_quality)
            elif strategy.name == "data_synthesis":
                return await self._synthesize_data(profile_name, strategy.parameters)
            elif strategy.name == "lifecycle_management":
                return await self._manage_lifecycle(profile_name, strategy.parameters)
            else:
                return {
                    "strategy": strategy.name,
                    "status": "skipped",
                    "reason": "unknown_strategy",
                }

        except Exception as e:
            logger.error("执行策略 {strategy.name} 失败: %(e)s")
            return {"strategy": strategy.name, "status": "error", "error": str(e)}

    async def _remove_duplicates(self, profile_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """移除重复数据"""
        threshold = parameters.get("threshold", 0.95)

        test_data = await self.data_manager.get_test_data(profile_name)
        if not test_data:
            return {
                "strategy": "duplicate_removal",
                "status": "skipped",
                "reason": "no_data",
            }

        # 计算记录相似度
        unique_records = []
        removed_count = 0

        for i, record1 in enumerate(test_data):
            is_duplicate = False
            for j, record2 in enumerate(unique_records):
                similarity = self._calculate_record_similarity(record1, record2)
                if similarity >= threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_records.append(record1)
            else:
                removed_count += 1

        # 更新数据
        await self.data_manager.update_test_data(profile_name, unique_records)

        return {
            "strategy": "duplicate_removal",
            "status": "completed",
            "original_count": len(test_data),
            "unique_count": len(unique_records),
            "removed_count": removed_count,
            "compression_ratio": removed_count / len(test_data) if test_data else 0,
        }

    def _calculate_record_similarity(self, record1: Dict[str, Any], record2: Dict[str, Any]) -> float:
        """计算记录相似度"""
        if not record1 or not record2:
            return 0.0

        # 简单的相似度计算
        common_keys = set(record1.keys()) & set(record2.keys())
        if not common_keys:
            return 0.0

        similarity_scores = []
        for key in common_keys:
            if key == "id":
                continue  # 跳过ID字段
            value1 = record1[key]
            value2 = record2[key]

            if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                if value2 != 0:
                    similarity = 1 - abs(value1 - value2) / max(abs(value1), abs(value2))
                else:
                    similarity = 1.0 if value1 == value2 else 0.0
            elif isinstance(value1, str) and isinstance(value2, str):
                # 简单的字符串相似度
                similarity = 1 if value1 == value2 else 0
            else:
                similarity = 1 if value1 == value2 else 0

            similarity_scores.append(similarity)

        return statistics.mean(similarity_scores) if similarity_scores else 0.0

    async def _compress_data(self, profile_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """压缩数据"""
        algorithm = parameters.get("algorithm", "zlib")
        level = parameters.get("level", 6)

        test_data = await self.data_manager.get_test_data(profile_name)
        if not test_data:
            return {
                "strategy": "data_compression",
                "status": "skipped",
                "reason": "no_data",
            }

        start_time = datetime.now()

        try:
            # 序列化数据
            serialized = json.dumps(test_data, separators=(",", ":")).encode("utf-8")
            original_size = len(serialized)

            # 压缩数据
            if algorithm == "zlib":
                import zlib

                compressed = zlib.compress(serialized, level=level)
            elif algorithm == "gzip":
                import gzip

                compressed = gzip.compress(serialized, compresslevel=level)
            else:
                compressed = serialized  # 不压缩

            compressed_size = len(compressed)
            compression_ratio = compressed_size / original_size if original_size > 0 else 0
            time_taken = (datetime.now() - start_time).total_seconds()

            # 保存压缩数据
            compressed_key = f"{profile_name}_{algorithm}"
            self.compression_cache[compressed_key] = compressed

            return {
                "strategy": "data_compression",
                "status": "completed",
                "algorithm": algorithm,
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": compression_ratio,
                "time_taken": time_taken,
                "space_saved": original_size - compressed_size,
            }

        except Exception as e:
            logger.error("数据压缩失败: %(e)s")
            return {"strategy": "data_compression", "status": "error", "error": str(e)}

    async def _enhance_data_quality(
        self,
        profile_name: str,
        parameters: Dict[str, Any],
        current_quality: DataQualityMetrics,
    ) -> Dict[str, Any]:
        """提升数据质量"""
        target_quality = parameters.get("target_quality", 0.9)

        test_data = await self.data_manager.get_test_data(profile_name)
        if not test_data:
            return {
                "strategy": "quality_enhancement",
                "status": "skipped",
                "reason": "no_data",
            }

        enhanced_data = []
        improvements_made = 0

        for record in test_data:
            enhanced_record = record.copy()

            # 提升完整性
            enhanced_record = self._enhance_completeness(enhanced_record)

            # 提升一致性
            enhanced_record = self._enhance_consistency(enhanced_record)

            # 提升准确性
            enhanced_record = self._enhance_accuracy(enhanced_record)

            if enhanced_record != record:
                improvements_made += 1

            enhanced_data.append(enhanced_record)

        # 更新数据
        await self.data_manager.update_test_data(profile_name, enhanced_data)

        # 计算改进效果
        enhanced_quality = await self.analyze_data_quality(profile_name)
        quality_improvement = enhanced_quality.overall_quality - current_quality.overall_quality

        return {
            "strategy": "quality_enhancement",
            "status": "completed",
            "original_quality": current_quality.overall_quality,
            "enhanced_quality": enhanced_quality.overall_quality,
            "improvement": quality_improvement,
            "records_improved": improvements_made,
            "target_quality_achieved": enhanced_quality.overall_quality >= target_quality,
        }

    def _enhance_completeness(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """提升数据完整性"""
        enhanced = record.copy()

        # 添加缺失的重要字段
        if "id" not in enhanced:
            enhanced["id"] = hashlib.md5(json.dumps(enhanced, sort_keys=True).encode()).hexdigest()[:8]

        if "timestamp" not in enhanced:
            enhanced["timestamp"] = datetime.now().isoformat()

        if "version" not in enhanced:
            enhanced["version"] = "1.0"

        return enhanced

    def _enhance_consistency(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """提升数据一致性"""
        enhanced = record.copy()

        # 确保数据类型一致
        if "value" in enhanced:
            try:
                if isinstance(enhanced["value"], str):
                    enhanced["value"] = float(enhanced["value"])
            except ValueError:
                enhanced["value"] = 0.0

        return enhanced

    def _enhance_accuracy(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """提升数据准确性"""
        enhanced = record.copy()

        # 清理不合理的数值
        if "value" in enhanced and isinstance(enhanced["value"], (int, float)):
            if enhanced["value"] < 0:
                enhanced["value"] = abs(enhanced["value"])
            elif enhanced["value"] > 1e12:
                enhanced["value"] = 1e12

        return enhanced

    async def _synthesize_data(self, profile_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """生成合成数据"""
        synthesis_ratio = parameters.get("synthesis_ratio", 0.1)

        test_data = await self.data_manager.get_test_data(profile_name)
        if not test_data:
            return {
                "strategy": "data_synthesis",
                "status": "skipped",
                "reason": "no_data",
            }

        # 计算需要生成的合成数据数量
        num_synthetic = int(len(test_data) * synthesis_ratio)

        # 生成合成数据
        synthetic_data = []
        for _ in range(num_synthetic):
            # 基于现有数据模式生成新数据
            base_record = np.random.choice(test_data)
            synthetic_record = self._generate_synthetic_record(base_record)
            synthetic_data.append(synthetic_record)

        # 合并数据
        combined_data = test_data + synthetic_data

        # 更新数据
        await self.data_manager.update_test_data(profile_name, combined_data)

        return {
            "strategy": "data_synthesis",
            "status": "completed",
            "original_count": len(test_data),
            "synthetic_count": num_synthetic,
            "total_count": len(combined_data),
            "synthesis_ratio": synthesis_ratio,
        }

    def _generate_synthetic_record(self, base_record: Dict[str, Any]) -> Dict[str, Any]:
        """生成合成记录"""
        synthetic = {}

        for key, value in base_record.items():
            if key == "id":
                synthetic[key] = hashlib.md5(json.dumps(base_record, sort_keys=True).encode()).hexdigest()[:8]
            elif key == "timestamp":
                # 生成稍有不同的时间戳
                base_time = datetime.fromisoformat(value) if isinstance(value, str) else datetime.now()
                time_diff = timedelta(minutes=np.random.randint(-60, 60))
                synthetic[key] = (base_time + time_diff).isoformat()
            elif isinstance(value, (int, float)):
                # 添加随机噪声
                noise = np.random.uniform(-0.1, 0.1)
                synthetic[key] = value * (1 + noise)
            elif isinstance(value, str):
                # 简单的字符串变化
                if value.isdigit():
                    synthetic[key] = str(int(value) + np.random.randint(-10, 10))
                else:
                    synthetic[key] = value + "_synthetic"
            else:
                synthetic[key] = value

        return synthetic

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

        # 过期数据
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
                except:
                    current_data.append(record)
            else:
                current_data.append(record)

        # 更新数据
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

    def _calculate_quality_improvement(self, initial: DataQualityMetrics, final: DataQualityMetrics) -> float:
        """计算质量改进"""
        return final.overall_quality - initial.overall_quality

    def _generate_recommendations(self, initial: DataQualityMetrics, final: DataQualityMetrics) -> List[str]:
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
        successful_optimizations = sum(1 for h in self.optimization_history if h.get("status") != "failed")
        failed_optimizations = total_optimizations - successful_optimizations

        # 计算平均改进
        improvements = [h.get("quality_improvement", 0) for h in self.optimization_history]
        avg_improvement = statistics.mean(improvements) if improvements else 0

        # 最常用的策略
        strategy_usage = Counter()
        for h in self.optimization_history:
            for strategy in h.get("strategies_applied", []):
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

        # 清理超过7天的缓存
        cutoff_time = datetime.now() - timedelta(days=7)
        keys_to_remove = []

        for key in self.compression_cache:
            # 假设key包含时间信息
            try:
                profile_name = key.split("_")[0]
                if profile_name in self.quality_baseline:
                    last_optimization = None
                    for h in self.optimization_history:
                        if h["profile_name"] == profile_name:
                            last_optimization = h["end_time"]
                            break
                    if last_optimization:
                        opt_time = datetime.fromisoformat(last_optimization)
                        if opt_time < cutoff_time:
                            keys_to_remove.append(key)
            except:
                keys_to_remove.append(key)

        # 删除过期缓存
        for key in keys_to_remove:
            del self.compression_cache[key]

        cache_size_after = len(self.compression_cache)

        return {
            "cache_size_before": cache_size_before,
            "cache_size_after": cache_size_after,
            "cleaned_entries": cache_size_before - cache_size_after,
            "compression_cache": self.compression_cache,
        }
