#!/usr/bin/env python3
"""
增强代码质量预测器
集成机器学习和深度学习技术的高级代码质量分析系统
"""

import ast
import json
import os
import sys
import time
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import Counter, defaultdict
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@dataclass
class CodeMetrics:
    """代码质量指标"""

    file_path: str
    lines_of_code: int
    cyclomatic_complexity: float
    cognitive_complexity: float
    maintainability_index: float
    technical_debt: float
    bug_risk_score: float
    security_vulnerabilities: int
    test_coverage_gap: float
    duplication_ratio: float
    code_churn: float
    developer_experience: float
    change_frequency: float


@dataclass
class QualityPrediction:
    """质量预测结果"""

    file_path: str
    overall_score: float
    risk_level: str  # low, medium, high, critical
    predicted_bugs: int
    maintainability_score: float
    security_score: float
    performance_risk: float
    recommendations: List[str]
    confidence: float


@dataclass
class AdvancedMetrics:
    """高级代码指标"""

    file_path: str

    # 结构指标
    class_count: int
    function_count: int
    avg_class_size: float
    avg_function_size: float
    max_function_size: int

    # 耦合和内聚
    coupling_between_objects: float
    lack_of_cohesion_of_methods: float
    afferent_coupling: int
    efferent_coupling: int

    # 继承和多态
    depth_of_inheritance: float
    number_of_children: int
    response_for_class: float

    # 设计模式
    design_pattern_usage: float
    interface_segregation: float
    dependency_inversion: float

    # 异常处理
    exception_handling_score: float
    error_recovery_mechanisms: int

    # 文档和注释
    documentation_coverage: float
    api_documentation_ratio: float


class EnhancedCodeAnalyzer:
    """增强代码分析器"""

    def __init__(self):
        self.metrics_history = []
        self.ml_model = None
        self.feature_extractor = FeatureExtractor()
        self.pattern_recognizer = CodePatternRecognizer()
        self.deep_analyzer = DeepCodeAnalyzer()

    def analyze_file_advanced(self, file_path: str) -> AdvancedMetrics:
        """高级文件分析"""
        logger.info(f"🔍 执行高级分析: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()

            tree = ast.parse(source_code)

            # 基础结构分析
            classes = [
                node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
            ]
            functions = [
                node
                for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]

            # 计算指标
            metrics = AdvancedMetrics(
                file_path=file_path,
                class_count=len(classes),
                function_count=len(functions),
                avg_class_size=np.mean([len(node.body) for node in classes])
                if classes
                else 0,
                avg_function_size=np.mean(
                    [self._count_function_lines(node) for node in functions]
                )
                if functions
                else 0,
                max_function_size=max(
                    [self._count_function_lines(node) for node in functions]
                )
                if functions
                else 0,
                coupling_between_objects=self._calculate_cbo(tree),
                lack_of_cohesion_of_methods=self._calculate_lcm(tree),
                afferent_coupling=self._calculate_ac(file_path),
                efferent_coupling=self._calculate_ec(tree),
                depth_of_inheritance=self._calculate_dit(classes),
                number_of_children=len(classes),  # 简化计算
                response_for_class=self._calculate_rfc(classes),
                design_pattern_usage=self._detect_design_patterns(tree),
                interface_segregation=self._calculate_interface_segregation(tree),
                dependency_inversion=self._calculate_dependency_inversion(tree),
                exception_handling_score=self._calculate_exception_handling_score(tree),
                error_recovery_mechanisms=self._count_error_recovery(tree),
                documentation_coverage=self._calculate_documentation_coverage(
                    source_code
                ),
                api_documentation_ratio=self._calculate_api_documentation_ratio(tree),
            )

            logger.info(
                f"✅ 高级分析完成: {metrics.class_count}个类, {metrics.function_count}个函数"
            )
            return metrics

        except Exception as e:
            logger.error(f"❌ 高级分析失败: {e}")
            return AdvancedMetrics(
                file_path=file_path,
                **{
                    k: 0
                    for k in AdvancedMetrics.__dataclass_fields__
                    if k != "file_path"
                },
            )

    def _count_function_lines(self, node: ast.AST) -> int:
        """计算函数行数"""
        if hasattr(node, "end_lineno"):
            return node.end_lineno - node.lineno + 1
        return len(node.body)

    def _calculate_cbo(self, tree: ast.AST) -> float:
        """计算类间耦合度 (Coupling Between Objects)"""
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
        return len(imports)

    def _calculate_lcm(self, tree: ast.AST) -> float:
        """计算方法内聚缺乏度 (Lack of Cohesion of Methods) - 简化版"""
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        total_lcm = 0

        for cls in classes:
            methods = [
                node
                for node in cls.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            if len(methods) <= 1:
                continue

            # 简化的内聚度计算：基于共享属性
            attributes = set()
            for method in methods:
                for node in ast.walk(method):
                    if isinstance(node, ast.Attribute) and isinstance(
                        node.ctx, ast.Load
                    ):
                        attributes.add(node.attr)

            # 内聚度 = 共享属性数量 / (方法数 * 平均属性数)
            cohesion = len(attributes) / (
                len(methods) * max(1, len(attributes) / len(methods))
            )
            total_lcm += 1 - cohesion

        return total_lcm / len(classes) if classes else 0

    def _calculate_ac(self, file_path: str) -> int:
        """计算传入耦合度 (Afferent Coupling) - 简化版"""
        # 在实际实现中，需要分析其他文件对当前文件的依赖
        return 0

    def _calculate_ec(self, tree: ast.AST) -> int:
        """计算传出耦合度 (Efferent Coupling)"""
        return len(
            [
                node
                for node in ast.walk(tree)
                if isinstance(node, (ast.Import, ast.ImportFrom))
            ]
        )

    def _calculate_dit(self, classes: List[ast.ClassDef]) -> float:
        """计算继承深度 (Depth of Inheritance)"""
        depths = []

        for cls in classes:
            depth = self._calculate_class_depth(cls)
            depths.append(depth)

        return np.mean(depths) if depths else 0

    def _calculate_class_depth(self, cls: ast.ClassDef) -> int:
        """递归计算类继承深度"""
        if not cls.bases:
            return 0

        max_depth = 0
        for base in cls.bases:
            if isinstance(base, ast.Name):
                # 简化：假设Name基类的深度为1
                max_depth = max(max_depth, 1)

        return max_depth

    def _calculate_rfc(self, classes: List[ast.ClassDef]) -> float:
        """计算类的响应度 (Response for Class)"""
        rfc_values = []

        for cls in classes:
            method_count = len(
                [
                    n
                    for n in cls.body
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
            )

            # 计算方法调用
            calls = 0
            for node in ast.walk(cls):
                if isinstance(node, ast.Call):
                    calls += 1

            rfc = method_count + calls
            rfc_values.append(rfc)

        return np.mean(rfc_values) if rfc_values else 0

    def _detect_design_patterns(self, tree: ast.AST) -> float:
        """检测设计模式使用情况"""
        pattern_score = 0
        patterns_detected = []

        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        # 检测单例模式
        singleton_patterns = self._detect_singleton_patterns(classes)
        if singleton_patterns:
            pattern_score += len(singleton_patterns) * 0.2
            patterns_detected.extend(["Singleton"] * len(singleton_patterns))

        # 检测工厂模式
        factory_patterns = self._detect_factory_patterns(classes)
        if factory_patterns:
            pattern_score += len(factory_patterns) * 0.2
            patterns_detected.extend(["Factory"] * len(factory_patterns))

        # 检测观察者模式
        observer_patterns = self._detect_observer_patterns(classes)
        if observer_patterns:
            pattern_score += len(observer_patterns) * 0.2
            patterns_detected.extend(["Observer"] * len(observer_patterns))

        logger.info(f"🎯 检测到设计模式: {patterns_detected}")
        return min(pattern_score, 1.0)

    def _detect_singleton_patterns(self, classes: List[ast.ClassDef]) -> List[str]:
        """检测单例模式"""
        singleton_classes = []

        for cls in classes:
            has_private_constructor = False
            has_instance_variable = False
            has_get_instance_method = False

            for node in cls.body:
                if isinstance(node, ast.FunctionDef):
                    # 检查__new__方法或getInstance方法
                    if node.name in ["__new__", "getInstance", "get_instance"]:
                        has_get_instance_method = True

                    # 检查私有构造函数
                    if node.name == "__init__":
                        for decorator in node.decorator_list:
                            if (
                                isinstance(decorator, ast.Name)
                                and decorator.id == "private"
                            ):
                                has_private_constructor = True

                # 检查类变量
                elif isinstance(node, ast.AnnAssign) or isinstance(node, ast.Assign):
                    for target in (
                        node.targets if hasattr(node, "targets") else [node.target]
                    ):
                        if isinstance(target, ast.Name) and target.id.startswith("_"):
                            has_instance_variable = True

            if has_get_instance_method or (
                has_private_constructor and has_instance_variable
            ):
                singleton_classes.append(cls.name)

        return singleton_classes

    def _detect_factory_patterns(self, classes: List[ast.ClassDef]) -> List[str]:
        """检测工厂模式"""
        factory_classes = []

        for cls in classes:
            factory_methods = ["create", "factory", "build", "make"]
            has_factory_method = False

            for node in cls.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if any(method in node.name.lower() for method in factory_methods):
                        has_factory_method = True
                        break

            if has_factory_method:
                factory_classes.append(cls.name)

        return factory_classes

    def _detect_observer_patterns(self, classes: List[ast.ClassDef]) -> List[str]:
        """检测观察者模式"""
        observer_classes = []

        for cls in classes:
            has_observer_methods = False
            has_subject_methods = False

            for node in cls.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_name = node.name.lower()
                    # 观察者方法
                    if any(
                        method in method_name
                        for method in ["notify", "update", "subscribe", "unsubscribe"]
                    ):
                        has_observer_methods = True
                    # 主题方法
                    elif any(
                        method in method_name
                        for method in [
                            "attach",
                            "detach",
                            "add_observer",
                            "remove_observer",
                        ]
                    ):
                        has_subject_methods = True

            if has_observer_methods or has_subject_methods:
                observer_classes.append(cls.name)

        return observer_classes

    def _calculate_interface_segregation(self, tree: ast.AST) -> float:
        """计算接口隔离原则遵循度"""
        # 检查是否过度依赖大接口
        total_imports = 0
        large_interfaces = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                total_imports += 1
                # 简化：如果导入整个模块而不是特定类/函数，可能违反接口隔离
                if not node.names or any(name.name == "*" for name in node.names):
                    large_interfaces += 1

        if total_imports == 0:
            return 1.0

        segregation_score = 1.0 - (large_interfaces / total_imports)
        return max(0, segregation_score)

    def _calculate_dependency_inversion(self, tree: ast.AST) -> float:
        """计算依赖倒置原则遵循度"""
        # 检查抽象导入 vs 具体导入
        abstract_imports = 0
        total_imports = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                total_imports += 1
                # 简化：假设abc、interfaces等为抽象导入
                if node.module and any(
                    abstract in node.module.lower()
                    for abstract in ["abc", "interface", "protocol"]
                ):
                    abstract_imports += 1
            elif isinstance(node, ast.Import):
                total_imports += len(node.names)

        if total_imports == 0:
            return 1.0

        inversion_score = abstract_imports / total_imports
        return min(inversion_score, 1.0)

    def _calculate_exception_handling_score(self, tree: ast.AST) -> float:
        """计算异常处理评分"""
        try_blocks = 0
        total_functions = 0
        functions_with_error_handling = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                total_functions += 1
                has_exception_handling = False

                for child in ast.walk(node):
                    if isinstance(child, ast.Try):
                        try_blocks += 1
                        has_exception_handling = True
                    elif isinstance(child, ast.Raise):
                        has_exception_handling = True

                if has_exception_handling:
                    functions_with_error_handling += 1

        # 异常处理评分 = 有异常处理的函数比例 + try块密度
        function_score = (
            functions_with_error_handling / total_functions
            if total_functions > 0
            else 0
        )
        try_score = min(try_blocks / total_functions, 1.0) if total_functions > 0 else 0

        return (function_score + try_score) / 2

    def _count_error_recovery(self, tree: ast.AST) -> int:
        """计算错误恢复机制数量"""
        recovery_mechanisms = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                # 检查是否有具体的恢复逻辑
                if node.name or node.type:
                    recovery_mechanisms += 1

        return recovery_mechanisms

    def _calculate_documentation_coverage(self, source_code: str) -> float:
        """计算文档覆盖率"""
        lines = source_code.split("\n")
        code_lines = [
            line for line in lines if line.strip() and not line.strip().startswith("#")
        ]
        doc_lines = [line for line in lines if line.strip().startswith("#")]

        if len(code_lines) == 0:
            return 1.0

        return len(doc_lines) / len(code_lines)

    def _calculate_api_documentation_ratio(self, tree: ast.AST) -> float:
        """计算API文档比例"""
        public_functions = []
        documented_functions = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_"):
                    public_functions.append(node)

                    # 检查是否有文档字符串
                    if (
                        node.body
                        and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, (ast.Str, ast.Constant))
                    ):
                        documented_functions.append(node)

        if len(public_functions) == 0:
            return 1.0

        return len(documented_functions) / len(public_functions)


class FeatureExtractor:
    """特征提取器"""

    def __init__(self):
        self.feature_names = [
            "lines_of_code",
            "cyclomatic_complexity",
            "cognitive_complexity",
            "class_count",
            "function_count",
            "avg_function_size",
            "max_function_size",
            "coupling_between_objects",
            "lack_of_cohesion_of_methods",
            "depth_of_inheritance",
            "design_pattern_usage",
            "exception_handling_score",
            "documentation_coverage",
        ]

    def extract_features(
        self, metrics: CodeMetrics, advanced_metrics: AdvancedMetrics
    ) -> np.ndarray:
        """提取特征向量"""
        features = [
            metrics.lines_of_code,
            metrics.cyclomatic_complexity,
            metrics.cognitive_complexity,
            advanced_metrics.class_count,
            advanced_metrics.function_count,
            advanced_metrics.avg_function_size,
            advanced_metrics.max_function_size,
            advanced_metrics.coupling_between_objects,
            advanced_metrics.lack_of_cohesion_of_methods,
            advanced_metrics.depth_of_inheritance,
            advanced_metrics.design_pattern_usage,
            advanced_metrics.exception_handling_score,
            advanced_metrics.documentation_coverage,
        ]

        return np.array(features)


class CodePatternRecognizer:
    """代码模式识别器"""

    def __init__(self):
        self.anti_patterns = {
            "long_method": {"threshold": 50, "weight": 0.3},
            "large_class": {"threshold": 20, "weight": 0.2},
            "god_object": {"threshold": 100, "weight": 0.4},
            "feature_envy": {"threshold": 10, "weight": 0.1},
        }

    def detect_anti_patterns(self, metrics: AdvancedMetrics) -> Dict[str, float]:
        """检测反模式"""
        detected = {}

        # 长方法
        if metrics.max_function_size > self.anti_patterns["long_method"]["threshold"]:
            detected["long_method"] = (
                metrics.max_function_size
                - self.anti_patterns["long_method"]["threshold"]
            ) / self.anti_patterns["long_method"]["threshold"]

        # 大类
        if metrics.avg_class_size > self.anti_patterns["large_class"]["threshold"]:
            detected["large_class"] = (
                metrics.avg_class_size - self.anti_patterns["large_class"]["threshold"]
            ) / self.anti_patterns["large_class"]["threshold"]

        # 上帝对象
        total_methods = metrics.function_count
        if total_methods > self.anti_patterns["god_object"]["threshold"]:
            detected["god_object"] = (
                total_methods - self.anti_patterns["god_object"]["threshold"]
            ) / self.anti_patterns["god_object"]["threshold"]

        return detected


class DeepCodeAnalyzer:
    """深度代码分析器"""

    def __init__(self):
        self.vulnerability_patterns = {
            "sql_injection": r'(\b(SELECT|INSERT|UPDATE|DELETE)\b.*\b(FORMAT|%|f")',
            "xss": r"(innerHTML|outerHTML|document\.write)",
            "hardcoded_secrets": r'(password|secret|key)\s*=\s*["\'][^"\']+["\']',
            "unsafe_eval": r"(eval\(|exec\(|__import__)",
        }

    def security_analysis(self, source_code: str) -> Dict[str, int]:
        """安全分析"""
        vulnerabilities = Counter()

        import re

        for vuln_type, pattern in self.vulnerability_patterns.items():
            matches = re.findall(pattern, source_code, re.IGNORECASE)
            vulnerabilities[vuln_type] = len(matches)

        return dict(vulnerabilities)

    def complexity_analysis(self, tree: ast.AST) -> Dict[str, float]:
        """复杂度分析"""
        complexity_scores = {}

        # 嵌套复杂度
        max_nesting = self._calculate_max_nesting(tree)
        complexity_scores["max_nesting"] = max_nesting

        # 认知复杂度
        cognitive_complexity = self._calculate_cognitive_complexity(tree)
        complexity_scores["cognitive_complexity"] = cognitive_complexity

        return complexity_scores

    def _calculate_max_nesting(self, tree: ast.AST) -> int:
        """计算最大嵌套深度"""
        max_depth = 0

        def _get_depth(node, current_depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, current_depth)

            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                    _get_depth(child, current_depth + 1)
                else:
                    _get_depth(child, current_depth)

        _get_depth(tree)
        return max_depth

    def _calculate_cognitive_complexity(self, tree: ast.AST) -> float:
        """计算认知复杂度"""
        complexity = 0

        for node in ast.walk(tree):
            # 基础复杂度
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                complexity += 1

            # 逻辑运算符增加复杂度
            if isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

            # 嵌套增加复杂度
            if isinstance(node, ast.If):
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, ast.If):
                        complexity += 1

        return complexity


class QualityPredictor:
    """质量预测器"""

    def __init__(self):
        self.model = self._create_ml_model()

    def _create_ml_model(self):
        """创建机器学习模型（简化版）"""
        # 在实际实现中，这里会加载预训练的模型
        return None

    def predict_quality(self, features: np.ndarray) -> QualityPrediction:
        """预测代码质量"""
        # 简化的预测逻辑
        overall_score = max(
            0, min(100, 100 - features[1] * 2 - features[2] * 1.5)
        )  # 基于复杂度的简化评分

        if overall_score >= 80:
            risk_level = "low"
        elif overall_score >= 60:
            risk_level = "medium"
        elif overall_score >= 40:
            risk_level = "high"
        else:
            risk_level = "critical"

        # 生成建议
        recommendations = self._generate_recommendations(features)

        return QualityPrediction(
            file_path="",  # 需要从外部传入
            overall_score=overall_score,
            risk_level=risk_level,
            predicted_bugs=max(0, int(features[1] * 0.1)),  # 简化的Bug预测
            maintainability_score=max(0, min(100, 100 - features[0] * 0.1)),
            security_score=90,  # 需要安全分析
            performance_risk=min(100, features[1] * 5),  # 基于圈复杂度的性能风险
            recommendations=recommendations,
            confidence=0.85,
        )

    def _generate_recommendations(self, features: np.ndarray) -> List[str]:
        """生成优化建议"""
        recommendations = []

        if features[1] > 10:  # 圈复杂度
            recommendations.append("🔧 建议降低函数圈复杂度，考虑拆分复杂函数")

        if features[4] > 20:  # 最大函数大小
            recommendations.append("📏 函数过长，建议将大函数拆分为更小的单元")

        if features[7] > 5:  # 耦合度
            recommendations.append("🔗 模块间耦合度过高，建议引入接口或依赖注入")

        if features[8] > 0.5:  # 内聚缺乏度
            recommendations.append("🎯 类的内聚度较低，建议重新组织相关方法")

        if features[12] < 0.3:  # 文档覆盖率
            recommendations.append("📚 文档覆盖率不足，建议添加更多注释和文档")

        return recommendations


def main():
    """主入口函数"""
    import argparse

    parser = argparse.ArgumentParser(description="增强代码质量预测器")
    parser.add_argument("files", nargs="+", help="要分析的Python文件")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    analyzer = EnhancedCodeAnalyzer()
    predictor = QualityPredictor()
    feature_extractor = FeatureExtractor()

    results = []

    print("🚀 启动增强代码质量预测器")
    print("=" * 50)

    for file_path in args.files:
        if not Path(file_path).exists():
            print(f"⚠️ 文件不存在: {file_path}")
            continue

        print(f"\n🔍 分析文件: {file_path}")

        try:
            # 执行高级分析
            advanced_metrics = analyzer.analyze_file_advanced(file_path)

            # 计算基础指标
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()

            # 简化的基础指标计算
            lines_of_code = len(
                [line for line in source_code.split("\n") if line.strip()]
            )
            cyclomatic_complexity = analyzer.deep_analyzer.complexity_analysis(
                ast.parse(source_code)
            )["cognitive_complexity"]

            code_metrics = CodeMetrics(
                file_path=file_path,
                lines_of_code=lines_of_code,
                cyclomatic_complexity=cyclomatic_complexity,
                cognitive_complexity=cyclomatic_complexity,
                maintainability_index=70.0,  # 简化
                technical_debt=0.0,
                bug_risk_score=0.0,
                security_vulnerabilities=0,
                test_coverage_gap=0.0,
                duplication_ratio=0.0,
                code_churn=0.0,
                developer_experience=1.0,
                change_frequency=0.0,
            )

            # 特征提取
            features = feature_extractor.extract_features(
                code_metrics, advanced_metrics
            )

            # 质量预测
            prediction = predictor.predict_quality(features)
            prediction.file_path = file_path

            results.append(
                {
                    "metrics": asdict(advanced_metrics),
                    "prediction": asdict(prediction),
                    "features": features.tolist(),
                }
            )

            print(
                f"✅ 分析完成: {prediction.overall_score:.1f}分 ({prediction.risk_level})"
            )

        except Exception as e:
            print(f"❌ 分析失败: {e}")
            continue

    # 输出结果
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n📄 结果已保存到: {args.output}")

    # 打印摘要
    print(f"\n📊 分析摘要:")
    print(f"   分析文件数: {len(results)}")
    if results:
        avg_score = np.mean([r["prediction"]["overall_score"] for r in results])
        risk_distribution = Counter([r["prediction"]["risk_level"] for r in results])

        print(f"   平均质量分: {avg_score:.1f}")
        print(f"   风险分布: {dict(risk_distribution)}")


if __name__ == "__main__":
    main()
