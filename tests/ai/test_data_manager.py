#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI测试数据管理器
提供智能的测试数据生成、管理和优化功能
"""

import json
import logging
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import numpy as np
from dataclasses import dataclass, field
import hashlib

from .test_ai_assisted_testing import AITestGenerator, IntelligentTestOptimizer
from .test_data_analyzer import AITestDataAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class TestDataProfile:
    """测试数据配置档案"""

    name: str
    description: str
    data_type: str  # 'unit', 'integration', 'e2e', 'performance'
    size: int
    constraints: Dict[str, Any] = field(default_factory=dict)
    freshness: float = 1.0  # 0-1 数据新鲜度
    quality_score: float = 1.0  # 0-1 数据质量分数
    usage_count: int = 0
    last_used: datetime = field(default_factory=datetime.now)
    generation_source: str = "ai_generated"
    cost_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class DataGenerationRequest:
    """数据生成请求"""

    profile_name: str
    target_size: int
    data_schema: Dict[str, Any]
    use_ai_enhancement: bool = True
    simulate_real_data: bool = True
    seed: Optional[int] = None
    constraints: Dict[str, Any] = field(default_factory=dict)


class IntelligentDataGenerator:
    """智能数据生成器"""

    def __init__(self):
        self.data_cache: Dict[str, Any] = {}
        self.generation_history: List[Dict[str, Any]] = []
        self.generator = AITestGenerator()

    def generate_test_data(self, request: DataGenerationRequest) -> Dict[str, Any]:
        """生成测试数据"""
        print(f"🤖 AI正在生成测试数据: {request.profile_name}")

        start_time = time.time()

        try:
            # 生成基础数据
            if request.use_ai_enhancement:
                data = self._generate_ai_enhanced_data(request)
            else:
                data = self._generate_basic_data(request)

            # 应用约束
            constrained_data = self._apply_constraints(data, request.constraints)

            # 模拟真实数据（如果需要）
            if request.simulate_real_data:
                constrained_data = self._simulate_real_patterns(constrained_data)

            # 缓存结果
            data_key = self._generate_data_key(request)
            self.data_cache[data_key] = constrained_data

            # 记录生成历史
            self._record_generation(request, constrained_data, start_time)

            return constrained_data

        except Exception as e:
            logger.error(f"数据生成失败: {e}")
            return self._generate_fallback_data(request)

    def _generate_ai_enhanced_data(
        self, request: DataGenerationRequest
    ) -> Dict[str, Any]:
        """AI增强的数据生成"""
        # 使用AI分析数据模式
        if request.seed:
            np.random.seed(request.seed)
            random.seed(request.seed)

        data = {}

        # 生成整数型数据
        for field_name, field_schema in request.data_schema.get(
            "properties", {}
        ).items():
            field_type = field_schema.get("type")

            if field_type == "integer":
                data[field_name] = self._generate_integer_data(field_schema)
            elif field_type == "number":
                data[field_name] = self._generate_number_data(field_schema)
            elif field_type == "string":
                data[field_name] = self._generate_string_data(field_schema)
            elif field_type == "boolean":
                data[field_name] = random.choice([True, False])
            elif field_type == "array":
                data[field_name] = self._generate_array_data(field_schema)
            elif field_type == "object":
                data[field_name] = self._generate_object_data(field_schema)

        return data

    def _generate_integer_data(self, schema: Dict[str, Any]) -> int:
        """生成整数数据"""
        minimum = schema.get("minimum", 0)
        maximum = schema.get("maximum", 1000)

        # 应用范围约束
        if minimum is not None and maximum is not None:
            return random.randint(minimum, maximum)
        elif minimum is not None:
            return random.randint(minimum, minimum + 1000)
        else:
            return random.randint(0, 1000)

    def _generate_number_data(self, schema: Dict[str, Any]) -> float:
        """生成浮点数数据"""
        minimum = schema.get("minimum", 0.0)
        maximum = schema.get("maximum", 1000.0)

        # 生成带趋势的数值（模拟真实市场数据）
        trend_factor = random.uniform(0.95, 1.05)
        value = random.uniform(minimum, maximum) * trend_factor

        return round(value, 2)

    def _generate_string_data(self, schema: Dict[str, Any]) -> str:
        """生成字符串数据"""
        format_type = schema.get("format", "")

        if format_type == "email":
            return f"test_{random.randint(1000, 9999)}@example.com"
        elif format_type == "date-time":
            return datetime.now().isoformat()
        elif format_type == "date":
            return datetime.now().date().isoformat()
        else:
            # 生成有意义的测试字符串
            patterns = [
                f"测试_{random.choice(['用户', '股票', '策略', '指标'])}_{random.randint(1, 100)}",
                f"data_{random.choice(['market', 'trade', 'analysis', 'report'])}_{random.randint(100, 999)}",
                f"{random.choice(['成功', '失败', '处理中', '已完成'])}_{random.randint(1000, 9999)}",
            ]
            return random.choice(patterns)

    def _generate_array_data(self, schema: Dict[str, Any]) -> List[Any]:
        """生成数组数据"""
        min_items = schema.get("minItems", 1)
        max_items = schema.get("maxItems", 5)
        item_count = random.randint(min_items, max_items)

        items_schema = schema.get("items", {})
        item_type = items_schema.get("type", "string")

        items = []
        for i in range(item_count):
            if item_type == "string":
                items.append(f"item_{i + 1}")
            elif item_type == "integer":
                items.append(random.randint(1, 100))
            elif item_type == "number":
                items.append(round(random.uniform(0.1, 100.0), 2))

        return items

    def _generate_object_data(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """生成对象数据"""
        properties = schema.get("properties", {})
        obj = {}

        for prop_name, prop_schema in properties.items():
            obj[prop_name] = self._generate_string_data(prop_schema)

        return obj

    def _apply_constraints(
        self, data: Dict[str, Any], constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """应用约束条件"""
        constraint_type = constraints.get("type")

        if constraint_type == "range":
            return self._apply_range_constraints(data, constraints)
        elif constraint_type == "pattern":
            return self._apply_pattern_constraints(data, constraints)
        elif constraint_type == "uniqueness":
            return self._apply_uniqueness_constraints(data, constraints)
        else:
            return data

    def _apply_range_constraints(
        self, data: Dict[str, Any], constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """应用范围约束"""
        field_ranges = constraints.get("ranges", {})

        for field_name, range_info in field_ranges.items():
            if field_name in data and isinstance(data[field_name], (int, float)):
                min_val = range_info.get("min")
                max_val = range_info.get("max")

                if min_val is not None and data[field_name] < min_val:
                    data[field_name] = min_val
                if max_val is not None and data[field_name] > max_val:
                    data[field_name] = max_val

        return data

    def _apply_pattern_constraints(
        self, data: Dict[str, Any], constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """应用模式约束"""
        # 可以添加更复杂的模式匹配逻辑
        return data

    def _apply_uniqueness_constraints(
        self, data: Dict[str, Any], constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """应用唯一性约束"""
        # 确保生成的数据具有唯一性
        return data

    def _simulate_real_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """模拟真实数据模式"""
        # 添加时间序列趋势
        if "price" in data:
            # 价格通常呈现趋势性
            base_price = data["price"]
            if isinstance(base_price, (int, float)):
                data["price"] = base_price * random.uniform(0.95, 1.05)

        # 添加相关性
        if "volume" in data and "price" in data:
            # 交易量和价格有相关性
            volume_multiplier = data.get("price", 1) / 100
            data["volume"] = int(data.get("volume", 1000) * volume_multiplier)

        return data

    def _generate_basic_data(self, request: DataGenerationRequest) -> Dict[str, Any]:
        """生成基础数据"""
        # 简单的数据生成逻辑
        return {
            "id": f"test_{random.randint(1000, 9999)}",
            "name": f"测试数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "value": random.randint(1, 100),
            "timestamp": datetime.now().isoformat(),
        }

    def _generate_fallback_data(self, request: DataGenerationRequest) -> Dict[str, Any]:
        """生成备用数据"""
        return {
            "id": f"fallback_{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}",
            "name": "备用测试数据",
            "value": 0,
            "timestamp": datetime.now().isoformat(),
            "error": "数据生成失败，使用备用数据",
        }

    def _generate_data_key(self, request: DataGenerationRequest) -> str:
        """生成数据缓存键"""
        key_data = f"{request.profile_name}_{request.target_size}_{json.dumps(request.data_schema, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _record_generation(
        self, request: DataGenerationRequest, data: Dict[str, Any], start_time: float
    ):
        """记录生成历史"""
        history_entry = {
            "timestamp": datetime.now(),
            "profile_name": request.profile_name,
            "target_size": request.target_size,
            "use_ai_enhancement": request.use_ai_enhancement,
            "generation_time": time.time() - start_time,
            "data_size": len(json.dumps(data)),
            "cache_hit": False,
        }
        self.generation_history.append(history_entry)

        # 保留最近1000条记录
        if len(self.generation_history) > 1000:
            self.generation_history = self.generation_history[-1000:]


class IntelligentDataOptimizer:
    """智能数据优化器"""

    def __init__(self):
        self.optimizer = IntelligentTestOptimizer()

    def optimize_data_profiles(
        self, profiles: List[TestDataProfile], test_results: List[Dict[str, Any]]
    ) -> List[TestDataProfile]:
        """优化数据档案"""
        print("🤖 AI正在优化数据档案...")

        optimized_profiles = []

        for profile in profiles:
            # 分析测试结果中的性能指标
            performance_metrics = self._analyze_performance_metrics(
                profile, test_results
            )

            # 生成优化建议
            optimization_suggestions = self._generate_optimization_suggestions(
                profile, performance_metrics
            )

            # 应用优化
            optimized_profile = self._apply_optimizations(
                profile, optimization_suggestions
            )

            optimized_profiles.append(optimized_profile)

        return optimized_profiles

    def _analyze_performance_metrics(
        self, profile: TestDataProfile, test_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """分析性能指标"""
        metrics = {
            "avg_execution_time": 0,
            "success_rate": 0,
            "memory_usage": 0,
            "cpu_usage": 0,
            "data_freshness_needed": True,
        }

        # 过滤相关的测试结果
        relevant_results = [
            r for r in test_results if r.get("data_profile") == profile.name
        ]

        if relevant_results:
            execution_times = [r.get("execution_time", 0) for r in relevant_results]
            success_count = sum(
                1 for r in relevant_results if r.get("status") == "success"
            )

            metrics["avg_execution_time"] = sum(execution_times) / len(execution_times)
            metrics["success_rate"] = success_count / len(relevant_results)

            # 检查数据新鲜度
            last_used = profile.last_used
            time_diff = datetime.now() - last_used

            metrics["data_freshness_needed"] = time_diff.total_seconds() > 3600  # 1小时

        return metrics

    def _generate_optimization_suggestions(
        self, profile: TestDataProfile, metrics: Dict[str, Any]
    ) -> List[str]:
        """生成优化建议"""
        suggestions = []

        if metrics["avg_execution_time"] > 1.0:  # 执行时间过长
            suggestions.append(
                f"减少数据大小以降低执行时间 (当前: {metrics['avg_execution_time']:.2f}s)"
            )

        if metrics["success_rate"] < 0.9:  # 成功率低
            suggestions.append(
                f"改善数据质量以提高成功率 (当前: {metrics['success_rate']:.2%})"
            )

        if metrics["data_freshness_needed"]:
            suggestions.append("更新数据以保持新鲜度")

        if profile.quality_score < 0.8:
            suggestions.append("提升数据质量分数 (当前: {profile.quality_score:.2f})")

        return suggestions

    def _apply_optimizations(
        self, profile: TestDataProfile, suggestions: List[str]
    ) -> TestDataProfile:
        """应用优化"""
        optimized_profile = TestDataProfile(
            name=profile.name,
            description=profile.description,
            data_type=profile.data_type,
            size=max(profile.size // 2, 100),  # 减少数据大小
            constraints=profile.constraints,
            freshness=min(profile.freshness + 0.1, 1.0),  # 提高新鲜度
            quality_score=min(profile.quality_score + 0.1, 1.0),  # 提高质量分数
            usage_count=profile.usage_count,
            last_used=datetime.now(),
            generation_source=f"ai_optimized_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            cost_metrics=profile.cost_metrics,
        )

        # 记录优化历史
        logger.info(f"数据档案 {profile.name} 已优化: {suggestions}")

        return optimized_profile


class AITestDataManager:
    """AI测试数据管理器 - 主控制器"""

    def __init__(self):
        self.profiles: Dict[str, TestDataProfile] = {}
        self.generator = IntelligentDataGenerator()
        self.optimizer = IntelligentDataOptimizer()
        self.analyzer = AITestDataAnalyzer()
        self.data_storage_path = Path("test_data/ai_managed")
        self.data_storage_path.mkdir(parents=True, exist_ok=True)

        # 初始化默认档案
        self._initialize_default_profiles()

    def _initialize_default_profiles(self):
        """初始化默认数据档案"""
        default_profiles = [
            TestDataProfile(
                name="unit_test_data",
                description="单元测试数据",
                data_type="unit",
                size=100,
                constraints={"type": "unit", "coverage": 80},
                generation_source="ai_generated",
            ),
            TestDataProfile(
                name="integration_test_data",
                description="集成测试数据",
                data_type="integration",
                size=500,
                constraints={"type": "integration", "complexity": "medium"},
                generation_source="ai_generated",
            ),
            TestDataProfile(
                name="e2e_test_data",
                description="端到端测试数据",
                data_type="e2e",
                size=1000,
                constraints={"type": "e2e", "realism": "high"},
                generation_source="ai_generated",
            ),
            TestDataProfile(
                name="performance_test_data",
                description="性能测试数据",
                data_type="performance",
                size=10000,
                constraints={"type": "performance", "size": "large"},
                generation_source="ai_generated",
            ),
        ]

        for profile in default_profiles:
            self.profiles[profile.name] = profile

    def create_data_profile(
        self,
        name: str,
        description: str,
        data_type: str,
        size: int,
        constraints: Dict[str, Any] = None,
    ) -> TestDataProfile:
        """创建数据档案"""
        profile = TestDataProfile(
            name=name,
            description=description,
            data_type=data_type,
            size=size,
            constraints=constraints or {},
            generation_source="user_created",
        )

        self.profiles[name] = profile
        logger.info(f"创建数据档案: {name}")
        return profile

    def generate_test_data(
        self,
        profile_name: str,
        data_schema: Dict[str, Any],
        request_params: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """生成测试数据"""
        if profile_name not in self.profiles:
            raise ValueError(f"数据档案 {profile_name} 不存在")

        profile = self.profiles[profile_name]

        request = DataGenerationRequest(
            profile_name=profile_name,
            target_size=profile.size,
            data_schema=data_schema,
            use_ai_enhancement=request_params.get("use_ai_enhancement", True)
            if request_params
            else True,
            simulate_real_data=request_params.get("simulate_real_data", True)
            if request_params
            else True,
            seed=request_params.get("seed") if request_params else None,
            constraints=profile.constraints,
        )

        # 生成数据
        data = self.generator.generate_test_data(request)

        # 更新档案使用统计
        profile.usage_count += 1
        profile.last_used = datetime.now()

        # 保存数据
        self._save_generated_data(profile_name, data)

        return data

    def _save_generated_data(self, profile_name: str, data: Dict[str, Any]):
        """保存生成的数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{profile_name}_{timestamp}.json"
        filepath = self.data_storage_path / filename

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)

            # 创建符号链接指向最新数据
            latest_link = self.data_storage_path / f"{profile_name}_latest.json"
            if latest_link.exists():
                latest_link.unlink()
            latest_link.symlink_to(filename)

            logger.info(f"测试数据已保存: {filepath}")

        except Exception as e:
            logger.error(f"保存测试数据失败: {e}")

    def load_test_data(
        self, profile_name: str, timestamp: str = None
    ) -> Dict[str, Any]:
        """加载测试数据"""
        if timestamp:
            filename = f"{profile_name}_{timestamp}.json"
        else:
            filename = f"{profile_name}_latest.json"

        filepath = self.data_storage_path / filename

        if not filepath.exists():
            raise FileNotFoundError(f"测试数据文件不存在: {filepath}")

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            logger.info(f"加载测试数据: {filepath}")
            return data

        except Exception as e:
            logger.error(f"加载测试数据失败: {e}")
            raise

    def analyze_data_quality(self, profile_name: str) -> Dict[str, Any]:
        """分析数据质量"""
        if profile_name not in self.profiles:
            raise ValueError(f"数据档案 {profile_name} 不存在")

        profile = self.profiles[profile_name]

        # 获取最近的测试结果
        recent_tests = [
            r
            for r in self.generator.generation_history
            if r["profile_name"] == profile_name
        ][-10:]  # 最近10条

        # 分析质量指标
        quality_analysis = {
            "profile_name": profile_name,
            "freshness": profile.freshness,
            "quality_score": profile.quality_score,
            "usage_count": profile.usage_count,
            "recent_test_count": len(recent_tests),
            "average_generation_time": 0,
            "success_rate": 0,
            "size_distribution": {},
        }

        if recent_tests:
            generation_times = [t["generation_time"] for t in recent_tests]
            quality_analysis["average_generation_time"] = sum(generation_times) / len(
                generation_times
            )

            # 估算成功率（基于数据质量）
            quality_analysis["success_rate"] = min(profile.quality_score, 0.95)

        return quality_analysis

    def optimize_data_management(self, test_results: List[Dict[str, Any]] = None):
        """优化数据管理"""
        print("🤖 AI正在优化数据管理...")

        if test_results is None:
            test_results = []

        # 优化数据档案
        profiles = list(self.profiles.values())
        optimized_profiles = self.optimizer.optimize_data_profiles(
            profiles, test_results
        )

        # 更新档案
        for profile in optimized_profiles:
            self.profiles[profile.name] = profile

        # 清理过期数据
        self._cleanup_expired_data()

        # 生成优化报告
        self._generate_optimization_report()

        logger.info("数据管理优化完成")

    def _cleanup_expired_data(self):
        """清理过期数据"""
        cutoff_time = datetime.now() - timedelta(days=7)  # 7天前的数据

        for filepath in self.data_storage_path.glob("*.json"):
            if filepath.name.endswith("_latest.json"):
                continue

            try:
                # 检查文件修改时间
                if datetime.fromtimestamp(filepath.stat().st_mtime) < cutoff_time:
                    filepath.unlink()
                    logger.info(f"删除过期数据: {filepath.name}")

            except Exception as e:
                logger.error(f"清理过期数据失败: {e}")

    def _generate_optimization_report(self):
        """生成优化报告"""
        report_path = self.data_storage_path / "optimization_report.json"

        report = {
            "timestamp": datetime.now().isoformat(),
            "profiles_count": len(self.profiles),
            "data_files_count": len(list(self.data_storage_path.glob("*.json")))
            - 1,  # 排除latest
            "total_storage_mb": self._calculate_storage_usage(),
            "profiles_summary": {},
        }

        for name, profile in self.profiles.items():
            report["profiles_summary"][name] = {
                "type": profile.data_type,
                "size": profile.size,
                "usage_count": profile.usage_count,
                "quality_score": profile.quality_score,
                "freshness": profile.freshness,
            }

        try:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            logger.info(f"优化报告已生成: {report_path}")

        except Exception as e:
            logger.error(f"生成优化报告失败: {e}")

    def _calculate_storage_usage(self) -> float:
        """计算存储使用量"""
        total_size = 0

        for filepath in self.data_storage_path.glob("*.json"):
            if not filepath.name.endswith("_latest.json"):
                try:
                    total_size += filepath.stat().st_size
                except:
                    pass

        return round(total_size / (1024 * 1024), 2)  # MB

    def get_data_insights(self) -> Dict[str, Any]:
        """获取数据洞察"""
        insights = {
            "profiles_overview": {},
            "generation_stats": self._get_generation_statistics(),
            "quality_trends": self._get_quality_trends(),
            "optimization_recommendations": self._get_optimization_recommendations(),
        }

        # 添加档案概览
        for name, profile in self.profiles.items():
            insights["profiles_overview"][name] = {
                "type": profile.data_type,
                "size": profile.size,
                "usage_count": profile.usage_count,
                "quality_score": profile.quality_score,
                "freshness": profile.freshness,
                "last_used": profile.last_used.isoformat(),
            }

        return insights

    def _get_generation_statistics(self) -> Dict[str, Any]:
        """获取生成统计"""
        if not self.generator.generation_history:
            return {}

        recent_history = self.generator.generation_history[-100:]  # 最近100条

        stats = {
            "total_generations": len(recent_history),
            "avg_generation_time": sum(t["generation_time"] for t in recent_history)
            / len(recent_history),
            "ai_enhanced_usage": sum(
                1 for t in recent_history if t["use_ai_enhancement"]
            ),
            "cache_hits": sum(1 for t in recent_history if t["cache_hit"]),
            "most_used_profiles": {},
        }

        # 统计最常用的档案
        profile_counts = {}
        for entry in recent_history:
            profile = entry["profile_name"]
            profile_counts[profile] = profile_counts.get(profile, 0) + 1

        stats["most_used_profiles"] = dict(
            sorted(profile_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        )

        return stats

    def _get_quality_trends(self) -> Dict[str, Any]:
        """获取质量趋势"""
        trends = {}

        for name, profile in self.profiles.items():
            # 模拟质量趋势分析
            trends[name] = {
                "quality_score": profile.quality_score,
                "freshness_trend": "increasing"
                if profile.freshness > 0.8
                else "stable",
                "usage_trend": "high" if profile.usage_count > 10 else "medium",
            }

        return trends

    def _get_optimization_recommendations(self) -> List[str]:
        """获取优化建议"""
        recommendations = []

        # 检查数据新鲜度
        for name, profile in self.profiles.items():
            if profile.freshness < 0.5:
                recommendations.append(
                    f"档案 {name} 需要更新数据 (新鲜度: {profile.freshness:.2f})"
                )

        # 检查使用频率
        low_usage_profiles = [
            name for name, profile in self.profiles.items() if profile.usage_count == 0
        ]
        if low_usage_profiles:
            recommendations.append(
                f"以下档案从未被使用: {', '.join(low_usage_profiles)}"
            )

        # 检查存储使用
        storage_usage = self._calculate_storage_usage()
        if storage_usage > 100:  # 超过100MB
            recommendations.append(f"存储使用量较高 ({storage_usage:.2f}MB)，建议清理")

        return recommendations
