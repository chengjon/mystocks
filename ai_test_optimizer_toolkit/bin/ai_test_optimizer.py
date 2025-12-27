#!/usr/bin/env python3
"""
AI智能测试优化器
复用现有测试基础设施，提供智能测试生成和优化功能

核心功能:
1. 基于现有generate_tests.py的增强测试生成
2. 利用classifier.py的智能模块分析
3. 集成性能回归检测和覆盖率优化建议
4. 自动测试质量评估和改进建议

作者: MyStocks AI Team
版本: 1.0
日期: 2025-01-22
"""

import ast
import json
import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import argparse
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入现有工具
try:
    from scripts.dev.generate_tests import TestGenerator
    from scripts.analysis.classifier import ModuleClassifier, create_category_report

    sys.path.insert(0, str(project_root / "scripts" / "analysis"))
    from models import ModuleMetadata, CategoryEnum
except ImportError as e:
    logger.warning(f"无法导入现有工具: {e}")
    TestGenerator = None
    ModuleClassifier = None


@dataclass
class TestOptimizationResult:
    """测试优化结果"""

    module_name: str
    current_coverage: float
    target_coverage: float
    optimization_suggestions: List[str]
    generated_tests: List[str]
    quality_score: float
    performance_baseline: Optional[Dict] = None


@dataclass
class CoverageGap:
    """覆盖率缺口分析"""

    uncovered_lines: List[int]
    uncovered_functions: List[str]
    uncovered_branches: List[str]
    complexity_issues: List[str]


class AITestOptimizer:
    """AI智能测试优化器"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.project_root = Path(__file__).parent.parent
        self.test_generator = TestGenerator if TestGenerator else None
        self.classifier = ModuleClassifier if ModuleClassifier else None

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置文件"""
        default_config = {
            "coverage_target": 95.0,
            "performance_threshold": 1.1,
            "complexity_limit": 10,
            "test_generation_mode": "comprehensive",
            "optimization_strategies": [
                "missing_branch_coverage",
                "exception_path_testing",
                "performance_testing",
                "integration_testing",
            ],
        }

        if config_path and Path(config_path).exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"配置文件加载失败: {e}")

        return default_config

    def analyze_module_for_optimization(
        self, source_file: str
    ) -> TestOptimizationResult:
        """分析模块并生成优化建议"""
        logger.info(f"🔍 分析模块: {source_file}")

        # 1. 基础模块信息
        module_info = self._extract_module_info(source_file)

        # 2. 当前覆盖率分析
        current_coverage = self._get_current_coverage(source_file)

        # 3. 覆盖率缺口分析
        coverage_gaps = self._analyze_coverage_gaps(source_file)

        # 4. 生成优化建议
        suggestions = self._generate_optimization_suggestions(
            module_info, coverage_gaps, current_coverage
        )

        # 5. 生成改进测试
        generated_tests = self._generate_improved_tests(source_file, coverage_gaps)

        # 6. 质量评分
        quality_score = self._calculate_quality_score(
            module_info, current_coverage, coverage_gaps
        )

        # 7. 性能基准（如果适用）
        performance_baseline = self._establish_performance_baseline(source_file)

        return TestOptimizationResult(
            module_name=module_info.get("name", Path(source_file).stem),
            current_coverage=current_coverage,
            target_coverage=self.config["coverage_target"],
            optimization_suggestions=suggestions,
            generated_tests=generated_tests,
            quality_score=quality_score,
            performance_baseline=performance_baseline,
        )

    def _extract_module_info(self, source_file: str) -> Dict:
        """提取模块基础信息"""
        try:
            with open(source_file, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            classes = []
            functions = []
            complexity_issues = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [
                        n.name for n in node.body if isinstance(n, ast.FunctionDef)
                    ]
                    classes.append(
                        {
                            "name": node.name,
                            "methods": methods,
                            "base_classes": [
                                base.id for base in node.bases if hasattr(base, "id")
                            ],
                            "line_number": node.lineno,
                        }
                    )
                elif isinstance(node, ast.FunctionDef):
                    functions.append(
                        {
                            "name": node.name,
                            "args": len(node.args.args),
                            "line_number": node.lineno,
                            "complexity": self._calculate_function_complexity(node),
                        }
                    )

            # 识别复杂度问题
            for func in functions:
                if func["complexity"] > self.config["complexity_limit"]:
                    complexity_issues.append(
                        f"函数 {func['name']} 复杂度过高 ({func['complexity']})"
                    )

            return {
                "name": Path(source_file).stem,
                "classes": classes,
                "functions": functions,
                "complexity_issues": complexity_issues,
                "total_lines": len(content.splitlines()),
                "docstring": ast.get_docstring(tree),
            }

        except Exception as e:
            logger.error(f"模块信息提取失败: {e}")
            return {"name": Path(source_file).stem, "error": str(e)}

    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """计算函数复杂度（简化版圈复杂度）"""
        complexity = 1  # 基础复杂度

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.With)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _get_current_coverage(self, source_file: str) -> float:
        """获取当前测试覆盖率"""
        try:
            module_name = self._get_module_name_from_path(source_file)

            # 构建测试文件路径模式
            test_patterns = self._find_test_patterns(source_file)

            # 运行覆盖率测试
            cmd = [
                "python",
                "-m",
                "pytest",
                "--cov",
                module_name,
                "--cov-report=json",
                "--cov-report=term-missing",
                "--tb=no",
                "-q",
            ]

            # 添加测试文件模式
            if test_patterns:
                cmd.extend(test_patterns)

            # 设置PYTHONPATH确保能找到项目模块
            env = os.environ.copy()
            env["PYTHONPATH"] = str(self.project_root)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=60,
                env=env,
            )

            # 解析覆盖率结果
            coverage_data = None
            coverage_file = Path("coverage.json")

            if coverage_file.exists():
                try:
                    with open(coverage_file, "r") as f:
                        coverage_data = json.load(f)

                    # 验证数据格式
                    if not isinstance(coverage_data, dict):
                        logger.warning(
                            f"覆盖率数据格式错误: 期望dict，实际{type(coverage_data)}"
                        )
                        return 0.0

                    # 尝试查找特定文件的覆盖率
                    for file_info in coverage_data.get("files", []):
                        if not isinstance(file_info, dict):
                            continue

                        relative_path = file_info.get("relative_path", "")
                        if source_file.endswith(relative_path):
                            summary = file_info.get("summary", {})
                            if isinstance(summary, dict):
                                return summary.get("percent_covered", 0.0)

                    # 如果没有找到特定文件，返回整体覆盖率
                    totals = coverage_data.get("totals")
                    if isinstance(totals, dict):
                        return totals.get("percent_covered", 0.0)

                except json.JSONDecodeError as e:
                    logger.warning(f"覆盖率JSON解析失败: {e}")
                except Exception as e:
                    logger.warning(f"覆盖率数据处理失败: {e}")

        except Exception as e:
            logger.warning(f"覆盖率获取失败: {e}")

        return 0.0

    def _get_module_name_from_path(self, source_file: str) -> str:
        """从文件路径获取模块名"""
        path_parts = Path(source_file).parts

        # 处理src目录下的文件
        if "src" in path_parts:
            src_index = path_parts.index("src")
            module_parts = list(path_parts[src_index:])

            # 移除.py扩展名
            if module_parts and module_parts[-1].endswith(".py"):
                module_parts[-1] = module_parts[-1][:-3]

            return ".".join(module_parts)

        # 其他情况返回文件名（不含扩展名）
        return Path(source_file).stem

    def _find_test_patterns(self, source_file: str) -> List[str]:
        """找到对应的测试文件模式"""
        source_path = Path(source_file)
        patterns = []

        # 获取源文件名（不含扩展名）
        source_name = source_path.stem

        # 查找可能的测试文件位置
        test_locations = [
            f"tests/unit/**/test_{source_name}.py",
            f"tests/**/test_{source_name}.py",
            f"scripts/tests/test_{source_name}.py",
            f"test_{source_name}.py",
        ]

        # 如果是src目录下的文件，添加特定模式
        if "src" in source_path.parts:
            src_index = source_path.parts.index("src")
            relative_parts = source_path.parts[src_index + 1 :]  # 去掉src

            # 构建测试路径模式
            for i in range(len(relative_parts)):
                test_path = "tests/" + "/".join(relative_parts[: i + 1])
                patterns.append(f"{test_path}/test_{source_name}.py")

        # 检查实际存在的测试文件
        existing_patterns = []
        for pattern in test_locations + patterns:
            # 这里不进行文件检查，直接返回模式，让pytest来处理
            existing_patterns.append(pattern)

        return existing_patterns

    def _analyze_coverage_gaps(self, source_file: str) -> CoverageGap:
        """分析覆盖率缺口"""
        try:
            module_info = self._extract_module_info(source_file)

            uncovered_lines = []
            uncovered_functions = []
            uncovered_branches = []
            complexity_issues = module_info.get("complexity_issues", [])

            # 分析未覆盖的函数
            for func in module_info.get("functions", []):
                # 简单启发式：假设私有函数和复杂函数可能覆盖不足
                if func["name"].startswith("_") or func["complexity"] > 5:
                    uncovered_functions.append(func["name"])

            # 分析未覆盖的分支（基于复杂函数）
            for func in module_info.get("functions", []):
                if func["complexity"] > 3:
                    uncovered_branches.append(
                        f"{func['name']} (复杂度: {func['complexity']})"
                    )

            return CoverageGap(
                uncovered_lines=uncovered_lines,
                uncovered_functions=uncovered_functions,
                uncovered_branches=uncovered_branches,
                complexity_issues=complexity_issues,
            )

        except Exception as e:
            logger.error(f"覆盖率缺口分析失败: {e}")
            return CoverageGap([], [], [], [])

    def _generate_optimization_suggestions(
        self, module_info: Dict, gaps: CoverageGap, current_coverage: float
    ) -> List[str]:
        """生成优化建议"""
        suggestions = []

        # 覆盖率建议
        if current_coverage < self.config["coverage_target"]:
            suggestions.append(
                f"🎯 覆盖率需要提升 {self.config['coverage_target'] - current_coverage:.1f}% 到达目标"
            )

        # 函数覆盖建议
        if gaps.uncovered_functions:
            suggestions.append(
                f"📝 添加以下函数的测试: {', '.join(gaps.uncovered_functions[:3])}"
            )
            if len(gaps.uncovered_functions) > 3:
                suggestions.append(
                    f"   ...以及另外 {len(gaps.uncovered_functions) - 3} 个函数"
                )

        # 分支覆盖建议
        if gaps.uncovered_branches:
            suggestions.append(
                f"🔀 增加分支测试覆盖: {len(gaps.uncovered_branches)} 个复杂分支"
            )

        # 复杂度建议
        if gaps.complexity_issues:
            suggestions.append(
                f"⚠️  处理复杂度问题: {'; '.join(gaps.complexity_issues[:2])}"
            )

        # 异常处理建议
        classes = module_info.get("classes", [])
        if classes:
            suggestions.append("🚨 增加异常处理测试路径")

        # 性能测试建议
        functions = module_info.get("functions", [])
        if any(func["args"] > 3 for func in functions):
            suggestions.append("⚡ 添加性能基准测试")

        # 集成测试建议
        if len(classes) > 1 or len(functions) > 5:
            suggestions.append("🔗 考虑添加集成测试")

        return suggestions

    def _generate_improved_tests(
        self, source_file: str, gaps: CoverageGap
    ) -> List[str]:
        """生成改进的测试代码"""
        generated_tests = []

        try:
            module_info = self._extract_module_info(source_file)
            module_name = module_info.get("name", "test_module")

            # 为未覆盖的函数生成测试
            for func_name in gaps.uncovered_functions[:5]:  # 限制数量
                test_code = self._generate_function_test(module_name, func_name)
                generated_tests.append(test_code)

            # 为复杂分支生成测试
            for branch_info in gaps.uncovered_branches[:3]:  # 限制数量
                test_code = self._generate_branch_test(module_name, branch_info)
                generated_tests.append(test_code)

            # 生成异常测试
            if module_info.get("classes"):
                exception_test = self._generate_exception_test(module_name)
                generated_tests.append(exception_test)

        except Exception as e:
            logger.error(f"测试生成失败: {e}")

        return generated_tests

    def _generate_function_test(self, module_name: str, func_name: str) -> str:
        """为特定函数生成测试"""
        return f'''
    def test_{func_name}_comprehensive(self):
        """测试 {func_name} 函数 - AI生成优化测试"""
        # TODO: 根据函数具体逻辑实现以下测试场景

        # 1. 正常输入测试
        normal_result = {module_name}.{func_name}(/* 正常参数 */)
        assert normal_result is not None

        # 2. 边界值测试
        boundary_result = {module_name}.{func_name}(/* 边界参数 */)
        assert boundary_result is not None

        # 3. 异常输入测试
        with pytest.raises((ValueError, TypeError)):
            {module_name}.{func_name}(/* 异常参数 */)

        # 4. 性能基准测试
        start_time = time.time()
        for _ in range(1000):
            {module_name}.{func_name}(/* 标准参数 */)
        duration = time.time() - start_time
        assert duration < 1.0  # 应在1秒内完成1000次调用
'''

    def _generate_branch_test(self, module_name: str, branch_info: str) -> str:
        """为复杂分支生成测试"""
        func_name = branch_info.split("(")[0].strip()

        return f'''
    def test_{func_name}_branch_coverage(self):
        """测试 {func_name} 分支覆盖 - AI生成优化测试"""
        # TODO: 根据分支条件设计测试用例

        # 测试所有条件分支
        test_cases = [
            # case 1: 条件为真
            {{'condition': True, 'expected': 'result1'}},
            # case 2: 条件为假
            {{'condition': False, 'expected': 'result2'}},
            # case 3: 边界条件
            {{'condition': None, 'expected': 'result3'}},
        ]

        for case in test_cases:
            result = {module_name}.{func_name}(case['condition'])
            assert result == case['expected'], f"分支测试失败: {{case}}"
'''

    def _generate_exception_test(self, module_name: str) -> str:
        """生成异常处理测试"""
        return f'''
    def test_{module_name}_exception_handling(self):
        """测试 {module_name} 异常处理 - AI生成优化测试"""
        # TODO: 测试各种异常场景

        # 1. 输入验证异常
        with pytest.raises(ValueError):
            # 触发输入验证错误
            pass

        # 2. 资源不可用异常
        with pytest.raises(ConnectionError):
            # 触发连接错误
            pass

        # 3. 权限异常
        with pytest.raises(PermissionError):
            # 触发权限错误
            pass

        # 4. 异常恢复测试
        try:
            # 可能失败的操作
            result = {module_name}.risky_operation()
        except ExpectedException as e:
            # 验证异常处理正确
            assert e.error_code == "EXPECTED_CODE"
            # 验证系统状态正常
            assert {module_name}.is_healthy()
'''

    def _calculate_quality_score(
        self, module_info: Dict, coverage: float, gaps: CoverageGap
    ) -> float:
        """计算测试质量评分"""
        score = 0.0

        # 覆盖率权重 (40%)
        coverage_score = (coverage / 100.0) * 40
        score += min(coverage_score, 40)

        # 复杂度权重 (20%)
        complexity_issues = len(gaps.complexity_issues)
        complexity_score = max(0, 20 - complexity_issues * 2)
        score += complexity_score

        # 函数覆盖权重 (20%)
        total_functions = len(module_info.get("functions", []))
        uncovered_functions = len(gaps.uncovered_functions)
        if total_functions > 0:
            function_score = (
                (total_functions - uncovered_functions) / total_functions
            ) * 20
            score += function_score

        # 分支覆盖权重 (10%)
        total_branches = len(
            [f for f in module_info.get("functions", []) if f["complexity"] > 1]
        )
        uncovered_branches = len(gaps.uncovered_branches)
        if total_branches > 0:
            branch_score = ((total_branches - uncovered_branches) / total_branches) * 10
            score += branch_score

        # 文档权重 (10%)
        if module_info.get("docstring"):
            score += 10

        return min(100.0, score)

    def _establish_performance_baseline(self, source_file: str) -> Optional[Dict]:
        """建立性能基准"""
        try:
            module_info = self._extract_module_info(source_file)
            functions = module_info.get("functions", [])

            if not functions:
                return None

            baseline = {}

            # 为主要函数建立性能基准
            for func in functions[:3]:  # 限制数量
                if not func["name"].startswith("_"):  # 跳过私有函数
                    baseline[func["name"]] = {
                        "target_ops_per_second": 1000,  # 目标：1000次操作/秒
                        "max_memory_mb": 10,  # 最大内存使用：10MB
                        "max_duration_ms": 100,  # 最大持续时间：100ms
                    }

            return baseline

        except Exception as e:
            logger.warning(f"性能基准建立失败: {e}")
            return None

    def optimize_batch_modules(
        self, source_files: List[str]
    ) -> List[TestOptimizationResult]:
        """批量优化多个模块"""
        logger.info(f"🚀 开始批量优化 {len(source_files)} 个模块")

        results = []

        for source_file in source_files:
            try:
                result = self.analyze_module_for_optimization(source_file)
                results.append(result)
                logger.info(
                    f"✅ 完成 {source_file}: 质量 {result.quality_score:.1f}/100"
                )
            except Exception as e:
                logger.error(f"❌ 优化失败 {source_file}: {e}")

        return results

    def generate_optimization_report(
        self, results: List[TestOptimizationResult]
    ) -> str:
        """生成优化报告"""
        report = []
        report.append("# AI测试优化报告")
        report.append(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"分析模块数: {len(results)}")
        report.append("")

        # 总体统计
        avg_coverage = (
            sum(r.current_coverage for r in results) / len(results) if results else 0
        )
        avg_quality = (
            sum(r.quality_score for r in results) / len(results) if results else 0
        )

        report.append("## 📊 总体统计")
        report.append(f"- 平均覆盖率: {avg_coverage:.1f}%")
        report.append(f"- 平均质量评分: {avg_quality:.1f}/100")
        report.append(
            f"- 需要优化的模块: {sum(1 for r in results if r.current_coverage < self.config['coverage_target'])}"
        )
        report.append("")

        # 详细结果
        report.append("## 📋 详细优化建议")

        for result in results:
            report.append(f"### {result.module_name}")
            report.append(f"- **当前覆盖率**: {result.current_coverage:.1f}%")
            report.append(f"- **目标覆盖率**: {result.target_coverage:.1f}%")
            report.append(f"- **质量评分**: {result.quality_score:.1f}/100")

            if result.optimization_suggestions:
                report.append("- **优化建议**:")
                for suggestion in result.optimization_suggestions:
                    report.append(f"  - {suggestion}")

            if result.generated_tests:
                report.append(f"- **生成测试数**: {len(result.generated_tests)}")

            report.append("")

        # 优先级排序
        sorted_results = sorted(results, key=lambda r: r.current_coverage)

        report.append("## 🎯 优化优先级")
        report.append("按覆盖率排序（最低优先级最高）:")

        for i, result in enumerate(sorted_results[:5], 1):
            report.append(f"{i}. {result.module_name}: {result.current_coverage:.1f}%")

        return "\n".join(report)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AI智能测试优化器 - 自动分析和改进测试覆盖率"
    )
    parser.add_argument(
        "source_files",
        nargs="+",
        help="源代码文件路径 (支持通配符，如: src/adapters/*.py)",
    )
    parser.add_argument("--config", "-c", help="配置文件路径 (JSON格式)")
    parser.add_argument(
        "--output", "-o", default="test_optimization_report.md", help="输出报告文件路径"
    )
    parser.add_argument(
        "--generate-tests", "-g", action="store_true", help="生成改进的测试代码文件"
    )
    parser.add_argument("--batch", "-b", action="store_true", help="批量处理模式")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出模式")

    args = parser.parse_args()

    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # 初始化优化器
        optimizer = AITestOptimizer(args.config)

        # 扩展文件列表
        source_files = []
        for pattern in args.source_files:
            if "*" in pattern or "?" in pattern:
                source_files.extend(Path().glob(pattern))
            else:
                source_files.append(Path(pattern))

        # 过滤Python文件
        source_files = [
            str(f) for f in source_files if f.suffix == ".py" and f.exists()
        ]

        if not source_files:
            print("❌ 未找到有效的Python文件")
            return 1

        logger.info(f"📁 找到 {len(source_files)} 个文件进行分析")

        # 执行优化分析
        if args.batch:
            results = optimizer.optimize_batch_modules(source_files)
        else:
            results = [
                optimizer.analyze_module_for_optimization(str(f)) for f in source_files
            ]

        # 生成报告
        report = optimizer.generate_optimization_report(results)

        # 保存报告
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"✅ 优化报告已生成: {args.output}")

        # 生成测试文件（如果需要）
        if args.generate_tests:
            test_dir = Path("ai_generated_tests")
            test_dir.mkdir(exist_ok=True)

            for result in results:
                if result.generated_tests:
                    test_file = test_dir / f"test_{result.module_name}_optimized.py"
                    with open(test_file, "w", encoding="utf-8") as f:
                        f.write(f'''
"""
AI优化的测试套件: {result.module_name}
生成时间: {time.strftime("%Y-%m-%d %H:%M:%S")}
当前覆盖率: {result.current_coverage:.1f}%
目标覆盖率: {result.target_coverage:.1f}%
"""

import pytest
import time
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from {result.module_name} import *
except ImportError as e:
    pytest.skip(f"无法导入 {{result.module_name}}: {{e}}", allow_module_level=True)

class Test{result.module_name.title()}Optimized:
    """AI优化的测试套件"""

{"".join(result.generated_tests)}
''')
                    print(f"✅ 生成测试文件: {test_file}")

        # 输出摘要
        print("\n📊 优化摘要:")
        print(f"- 分析文件: {len(results)} 个")
        print(
            f"- 平均覆盖率: {sum(r.current_coverage for r in results) / len(results):.1f}%"
        )
        print(
            f"- 需要改进: {sum(1 for r in results if r.current_coverage < optimizer.config['coverage_target'])} 个"
        )

        return 0

    except KeyboardInterrupt:
        print("\n⏹️  用户中断操作")
        return 1
    except Exception as e:
        logger.error(f"💥 优化过程中发生异常: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
