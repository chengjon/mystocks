#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据质量指标

提供测试数据质量分析和评估功能：
- 数据完整性检查
- 数据一致性验证
- 数据唯一性检测
- 重复数据识别
- 数据分布分析
"""

import hashlib
import json
import time
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from collections import Counter


@dataclass
class QualityMetrics:
    """数据质量指标"""

    total_records: int = 0
    complete_records: int = 0
    incomplete_records: int = 0
    unique_records: int = 0
    duplicate_records: int = 0
    null_field_count: int = 0
    invalid_value_count: int = 0
    completeness_score: float = 0.0
    uniqueness_score: float = 0.0
    validity_score: float = 0.0
    overall_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_records": self.total_records,
            "complete_records": self.complete_records,
            "incomplete_records": self.incomplete_records,
            "unique_records": self.unique_records,
            "duplicate_records": self.duplicate_records,
            "null_field_count": self.null_field_count,
            "invalid_value_count": self.invalid_value_count,
            "completeness_score": self.completeness_score,
            "uniqueness_score": self.uniqueness_score,
            "validity_score": self.validity_score,
            "overall_score": self.overall_score,
        }


@dataclass
class FieldQualityMetrics:
    """字段质量指标"""

    field_name: str
    total_count: int = 0
    null_count: int = 0
    unique_count: int = 0
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    avg_value: Optional[float] = None
    distribution: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field_name": self.field_name,
            "total_count": self.total_count,
            "null_count": self.null_count,
            "unique_count": self.unique_count,
            "null_percentage": (self.null_count / self.total_count * 100) if self.total_count > 0 else 0,
            "min_value": str(self.min_value) if self.min_value is not None else None,
            "max_value": str(self.max_value) if self.max_value is not None else None,
            "avg_value": self.avg_value,
            "distribution": self.distribution,
        }


class DataQualityAnalyzer:
    """数据质量分析器"""

    def __init__(
        self,
        primary_key_fields: Optional[List[str]] = None,
        required_fields: Optional[List[str]] = None,
    ):
        """
        初始化数据质量分析器

        Args:
            primary_key_fields: 主键字段列表（用于判断唯一性）
            required_fields: 必填字段列表（用于检查完整性）
        """
        self.primary_key_fields = primary_key_fields or ["id", "symbol", "date"]
        self.required_fields = required_fields or []

    def analyze(self, data: List[Dict[str, Any]], schema: Optional[Dict[str, Any]] = None) -> QualityMetrics:
        """
        分析数据集质量

        Args:
            data: 数据列表
            schema: 数据 schema 定义

        Returns:
            QualityMetrics: 质量指标
        """
        if not data:
            return QualityMetrics()

        metrics = QualityMetrics()
        metrics.total_records = len(data)

        null_counts = Counter()
        value_sets: Dict[str, Set] = {}
        duplicate_count = 0

        for record in data:
            is_complete = True
            record_hash = hashlib.md5(json.dumps(record, sort_keys=True).encode()).hexdigest()

            for field_name, value in record.items():
                if value is None:
                    null_counts[field_name] += 1
                    is_complete = False
                else:
                    if field_name not in value_sets:
                        value_sets[field_name] = set()
                    value_sets[field_name].add(str(value))

            if is_complete:
                metrics.complete_records += 1

        metrics.null_field_count = sum(null_counts.values())
        metrics.incomplete_records = metrics.total_records - metrics.complete_records

        unique_hashes = set()
        for record in data:
            record_hash = hashlib.md5(json.dumps(record, sort_keys=True).encode()).hexdigest()
            if record_hash in unique_hashes:
                duplicate_count += 1
            else:
                unique_hashes.add(record_hash)

        metrics.unique_records = metrics.total_records - duplicate_count
        metrics.duplicate_records = duplicate_count

        metrics.completeness_score = (
            metrics.complete_records / metrics.total_records * 100 if metrics.total_records > 0 else 0
        )
        metrics.uniqueness_score = (
            metrics.unique_records / metrics.total_records * 100 if metrics.total_records > 0 else 0
        )

        valid_count = metrics.total_records - metrics.incomplete_records
        metrics.validity_score = valid_count / metrics.total_records * 100 if metrics.total_records > 0 else 0

        metrics.overall_score = (
            metrics.completeness_score * 0.4 + metrics.uniqueness_score * 0.3 + metrics.validity_score * 0.3
        )

        return metrics

    def analyze_field(self, data: List[Dict], field_name: str) -> FieldQualityMetrics:
        """
        分析单个字段的质量

        Args:
            data: 数据列表
            field_name: 字段名

        Returns:
            FieldQualityMetrics: 字段质量指标
        """
        metrics = FieldQualityMetrics(field_name=field_name)
        values = []

        for record in data:
            value = record.get(field_name)
            metrics.total_count += 1

            if value is None:
                metrics.null_count += 1
            else:
                values.append(value)

        if values:
            metrics.unique_count = len(set(str(v) for v in values))

            numeric_values = [v for v in values if isinstance(v, (int, float))]
            if numeric_values:
                metrics.min_value = min(numeric_values)
                metrics.max_value = max(numeric_values)
                metrics.avg_value = sum(numeric_values) / len(numeric_values)

            value_strs = [str(v) for v in values]
            value_counter = Counter(value_strs)
            metrics.distribution = dict(value_counter.most_common(10))

        return metrics

    def detect_duplicates(self, data: List[Dict[str, Any]], similarity_threshold: float = 0.9) -> List[Dict[str, Any]]:
        """
        检测相似重复数据

        Args:
            data: 数据列表
            similarity_threshold: 相似度阈值

        Returns:
            List: 重复数据组
        """
        duplicates = []
        processed_indices = set()

        for i, record1 in enumerate(data):
            if i in processed_indices:
                continue

            similar_records = [record1]
            record1_str = json.dumps(record1, sort_keys=True)

            for j, record2 in enumerate(data):
                if i >= j or j in processed_indices:
                    continue

                record2_str = json.dumps(record2, sort_keys=True)
                similarity = self._calculate_similarity(record1_str, record2_str)

                if similarity >= similarity_threshold:
                    similar_records.append(record2)
                    processed_indices.add(j)

            if len(similar_records) > 1:
                duplicates.append(
                    {
                        "representative": similar_records[0],
                        "count": len(similar_records),
                        "similar_records": similar_records[1:],
                        "similarity": similarity_threshold,
                    }
                )

        return duplicates

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """计算两个字符串的相似度"""
        if str1 == str2:
            return 1.0

        # 简单的相似度计算（避免外部依赖）
        len1, len2 = len(str1), len(str2)
        if len1 == 0 or len2 == 0:
            return 0.0

        # 使用哈希进行精确匹配检测
        if str1 == str2:
            return 1.0

        # 简单的相似度估算：基于公共子序列
        min_len = min(len1, len2)
        common_chars = len(set(str1) & set(str2))
        return common_chars / (len(set(str1) | set(str2)) + 0.001)


class DataQualityReport:
    """数据质量报告生成器"""

    def __init__(self, analyzer: Optional[DataQualityAnalyzer] = None):
        self.analyzer = analyzer or DataQualityAnalyzer()

    def generate_report(
        self,
        data: List[Dict[str, Any]],
        schema: Optional[Dict[str, Any]] = None,
        report_title: str = "Data Quality Report",
    ) -> Dict[str, Any]:
        """
        生成数据质量报告

        Args:
            data: 数据列表
            schema: 数据 schema
            report_title: 报告标题

        Returns:
            Dict: 完整报告
        """
        metrics = self.analyzer.analyze(data, schema)

        field_metrics = {}
        if data:
            all_fields = set()
            for record in data:
                all_fields.update(record.keys())

            for field_name in all_fields:
                field_metrics[field_name] = self.analyzer.analyze_field(data, field_name).to_dict()

        duplicate_groups = self.analyzer.detect_duplicates(data)

        return {
            "report_title": report_title,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": metrics.to_dict(),
            "field_metrics": field_metrics,
            "duplicates": {
                "total_groups": len(duplicate_groups),
                "total_duplicates": sum(g["count"] - 1 for g in duplicate_groups),
                "groups": duplicate_groups[:10],
            },
            "recommendations": self._generate_recommendations(metrics),
        }

    def _generate_recommendations(self, metrics: QualityMetrics) -> List[str]:
        """生成改进建议"""
        recommendations = []

        if metrics.completeness_score < 90:
            recommendations.append(
                f"数据完整性较低 ({metrics.completeness_score:.1f}%)，建议检查必填字段和数据源质量。"
            )

        if metrics.duplicate_records > metrics.total_records * 0.05:
            recommendations.append(f"存在 {metrics.duplicate_records} 条重复数据，建议实施数据去重机制。")

        if metrics.validity_score < 95:
            recommendations.append(f"数据有效性较低 ({metrics.validity_score:.1f}%)，建议加强数据验证和清洗。")

        return recommendations


def validate_schema(data: List[Dict[str, Any]], schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证数据是否符合 schema

    Args:
        data: 数据列表
        schema: Schema 定义

    Returns:
        Dict: 验证结果
    """
    required_fields = schema.get("required", [])
    field_types = schema.get("types", {})
    field_patterns = schema.get("patterns", {})

    errors = []
    valid_count = 0

    for record in data:
        record_errors = []

        for field_name in required_fields:
            if field_name not in record or record[field_name] is None:
                record_errors.append(f"Missing required field: {field_name}")

        for field_name, expected_type in field_types.items():
            if field_name in record and record[field_name] is not None:
                if not isinstance(record[field_name], expected_type):
                    record_errors.append(f"Field {field_name} expected {expected_type}, got {type(record[field_name])}")

        for field_name, pattern in field_patterns.items():
            if field_name in record and record[field_name] is not None:
                import re

                if not re.match(pattern, str(record[field_name])):
                    record_errors.append(f"Field {field_name} does not match pattern: {pattern}")

        if not record_errors:
            valid_count += 1
        else:
            errors.extend(record_errors)

    return {
        "total_records": len(data),
        "valid_records": valid_count,
        "invalid_records": len(data) - valid_count,
        "validity_rate": (valid_count / len(data) * 100) if data else 0,
        "errors": errors[:20],
    }


if __name__ == "__main__":
    print("=== Data Quality Analysis ===")

    try:
        from src.data_sources.factory import get_relational_source

        rel_source = get_relational_source(source_type="mock")
        sample_data = rel_source.get_watchlist(user_id=1)

        if not sample_data:
            raise ValueError("Mock 数据源返回为空")
    except Exception as e:
        print(f"⚠️  无法从 Mock 数据源获取数据，使用生成数据: {e}")
        import random

        sample_data = [
            {
                "id": i,
                "symbol": f"60{random.randint(0, 9999):04d}",
                "name": f"股票{i}",
                "price": round(random.uniform(5, 50), 2),
            }
            for i in range(1, 21)
        ]
        sample_data[2]["name"] = None
        sample_data[2]["price"] = None
        sample_data[5]["id"] = sample_data[0]["id"]
        sample_data[5]["symbol"] = sample_data[0]["symbol"]
    analyzer = DataQualityAnalyzer()
    metrics = analyzer.analyze(sample_data)
    print(f"Total records: {metrics.total_records}")
    print(f"Completeness: {metrics.completeness_score:.1f}%")
    print(f"Uniqueness: {metrics.uniqueness_score:.1f}%")
    print(f"Overall Score: {metrics.overall_score:.1f}%")

    print("\n=== Field Analysis ===")
    for field_name in ["id", "symbol", "name", "price"]:
        field_metrics = analyzer.analyze_field(sample_data, field_name)
        print(f"{field_name}: null={field_metrics.null_count}, unique={field_metrics.unique_count}")

    print("\n=== Duplicate Detection ===")
    duplicates = analyzer.detect_duplicates(sample_data)
    print(f"Found {len(duplicates)} duplicate groups")

    print("\n=== Full Report ===")
    report = DataQualityReport(analyzer).generate_report(sample_data)
    print(json.dumps(report, indent=2, ensure_ascii=False))
