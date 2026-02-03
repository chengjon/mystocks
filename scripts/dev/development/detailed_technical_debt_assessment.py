#!/usr/bin/env python3
"""
详细技术债务复杂度评估器
专门针对特定文件进行深入的技术债务分析
"""

import ast
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import radon.complexity as radon_cc


class DetailedTechnicalDebtAssessment:
    """详细技术债务评估器"""

    def __init__(self):
        self.project_root = Path.cwd()  # 使用当前工作目录
        self.assessment_results = {}

    def analyze_file_complexity(self, file_path: str) -> Dict[str, Any]:
        """
        分析单个文件的复杂度

        Args:
            file_path: 文件路径

        Returns:
            Dict[str, Any]: 复杂度分析结果
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 基础统计
            lines = content.split("\n")
            total_lines = len(lines)
            code_lines = len(
                [
                    line
                    for line in lines
                    if line.strip() and not line.strip().startswith("#")
                ]
            )
            comment_lines = len(
                [line for line in lines if line.strip().startswith("#")]
            )
            empty_lines = total_lines - code_lines - comment_lines

            # AST解析
            try:
                tree = ast.parse(content)

                # 统计类和函数
                classes = []
                functions = []
                imports = []

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_info = {
                            "name": node.name,
                            "line_start": node.lineno,
                            "line_end": node.end_lineno
                            if hasattr(node, "end_lineno")
                            else "unknown",
                            "methods": [
                                n.name
                                for n in node.body
                                if isinstance(n, ast.FunctionDef)
                            ],
                        }
                        classes.append(class_info)
                    elif isinstance(node, ast.FunctionDef):
                        func_info = {
                            "name": node.name,
                            "line_start": node.lineno,
                            "line_end": node.end_lineno
                            if hasattr(node, "end_lineno")
                            else "unknown",
                            "args": [arg.arg for arg in node.args.args],
                        }
                        functions.append(func_info)
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.append(f"import {alias.name}")
                        else:
                            module = node.module or ""
                            for alias in node.names:
                                imports.append(f"from {module} import {alias.name}")

            except SyntaxError as e:
                return {
                    "error": f"Syntax error: {e}",
                    "total_lines": total_lines,
                    "file_path": file_path,
                }

            # 使用radon计算圈复杂度
            try:
                cc_results = radon_cc.cc_visit(content)
                max_complexity = max(
                    [result.complexity for result in cc_results], default=0
                )
                avg_complexity = (
                    sum([result.complexity for result in cc_results]) / len(cc_results)
                    if cc_results
                    else 0
                )

                complex_functions = [
                    result for result in cc_results if result.complexity > 10
                ]

            except Exception:
                cc_results = []
                max_complexity = 0
                avg_complexity = 0
                complex_functions = []

            # 依赖分析
            dependencies = self._analyze_dependencies(file_path)

            # 测试覆盖率分析
            test_coverage = self._analyze_test_coverage(file_path)

            # 代码质量指标
            quality_metrics = {
                "maintainability_index": self._calculate_maintainability_index(
                    cc_results
                ),
                "documentation_ratio": self._calculate_documentation_ratio(
                    classes, functions
                ),
                "function_length_avg": self._calculate_avg_function_length(functions),
                "class_method_avg": len([f for f in functions if "." in f["name"]])
                / len(classes)
                if classes
                else 0,
            }

            return {
                "file_path": file_path,
                "file_size": {
                    "total_lines": total_lines,
                    "code_lines": code_lines,
                    "comment_lines": comment_lines,
                    "empty_lines": empty_lines,
                },
                "structure": {
                    "classes_count": len(classes),
                    "functions_count": len(functions),
                    "imports_count": len(imports),
                    "classes": classes,
                    "functions": functions,
                    "imports": imports,
                },
                "complexity": {
                    "max_complexity": max_complexity,
                    "avg_complexity": avg_complexity,
                    "complex_functions": len(complex_functions),
                    "complex_functions_detail": [
                        {
                            "name": result.name,
                            "complexity": result.complexity,
                            "line": result.lineno,
                        }
                        for result in complex_functions
                    ],
                },
                "dependencies": dependencies,
                "test_coverage": test_coverage,
                "quality_metrics": quality_metrics,
                "risk_assessment": self._assess_risks(
                    max_complexity, len(classes), len(functions), dependencies
                ),
            }

        except Exception as e:
            return {"file_path": file_path, "error": f"Analysis failed: {str(e)}"}

    def _analyze_dependencies(self, file_path: str) -> Dict[str, Any]:
        """分析文件依赖"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 解析导入语句
            tree = ast.parse(content)

            internal_deps = []  # 项目内部依赖
            external_deps = []  # 外部库依赖
            standard_deps = []  # 标准库依赖

            project_modules = self._get_project_modules()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith(
                            ("src.", "core.", "adapters.", "monitoring.")
                        ):
                            internal_deps.append(alias.name)
                        elif alias.name in [
                            "os",
                            "sys",
                            "json",
                            "time",
                            "datetime",
                            "pathlib",
                            "typing",
                            "collections",
                            "itertools",
                            "functools",
                        ]:
                            standard_deps.append(alias.name)
                        else:
                            external_deps.append(alias.name)

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if module.startswith(("src.", "core.", "adapters.", "monitoring.")):
                        internal_deps.append(module)
                    elif module in [
                        "os",
                        "sys",
                        "json",
                        "time",
                        "datetime",
                        "pathlib",
                        "typing",
                        "collections",
                        "itertools",
                        "functools",
                    ]:
                        standard_deps.append(module)
                    else:
                        external_deps.append(module)

            return {
                "internal_dependencies": list(set(internal_deps)),
                "external_dependencies": list(set(external_deps)),
                "standard_dependencies": list(set(standard_deps)),
                "total_dependencies": len(
                    set(internal_deps + external_deps + standard_deps)
                ),
            }

        except Exception as e:
            return {"error": f"Dependency analysis failed: {str(e)}"}

    def _get_project_modules(self) -> List[str]:
        """获取项目模块列表"""
        modules = []
        try:
            for root, dirs, files in os.walk(self.project_root):
                if "__pycache__" in root:
                    continue
                for file in files:
                    if file.endswith(".py") and not file.startswith("__"):
                        rel_path = os.path.relpath(
                            os.path.join(root, file), self.project_root
                        )
                        module_path = rel_path[:-3].replace(os.sep, ".")
                        modules.append(module_path)
        except Exception:
            pass
        return modules

    def _analyze_test_coverage(self, file_path: str) -> Dict[str, Any]:
        """分析测试覆盖率"""
        # 查找对应的测试文件
        file_path = Path(file_path).resolve()
        try:
            relative_path = file_path.relative_to(self.project_root)
        except ValueError:
            # 如果文件不在项目根目录下，使用文件名
            relative_path = file_path

        # 可能的测试文件路径
        test_patterns = [
            f"tests/test_{file_path.stem}.py",
            f"tests/{file_path.stem}_test.py",
            f"tests/{file_path.parent.name}/test_{file_path.stem}.py",
            f"tests/unit/{file_path.parent.name}/test_{file_path.stem}.py",
            f"tests/integration/{file_path.parent.name}/test_{file_path.stem}.py",
        ]

        test_files = []
        for pattern in test_patterns:
            test_path = self.project_root / pattern
            if test_path.exists():
                test_files.append(str(test_path))

        # 分析测试内容
        test_methods = []
        for test_file in test_files:
            try:
                with open(test_file, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name.startswith(
                        "test_"
                    ):
                        test_methods.append(
                            {"name": node.name, "file": test_file, "line": node.lineno}
                        )
            except Exception:
                continue

        return {
            "test_files_found": test_files,
            "test_methods_count": len(test_methods),
            "test_methods": test_methods[:10],  # 只显示前10个
            "coverage_estimate": "high"
            if len(test_methods) > 10
            else "medium"
            if len(test_methods) > 3
            else "low",
        }

    def _calculate_maintainability_index(self, cc_results) -> float:
        """计算可维护性指数"""
        try:
            if not cc_results:
                return 85.0  # 默认值

            total_complexity = sum(result.complexity for result in cc_results)
            avg_complexity = total_complexity / len(cc_results)

            # 简化的可维护性指数计算
            maintainability = max(0, 100 - (avg_complexity * 5))
            return min(100, maintainability)
        except Exception:
            return 50.0

    def _calculate_documentation_ratio(self, classes: List, functions: List) -> float:
        """计算文档覆盖率"""
        try:
            total_items = len(classes) + len(functions)
            if total_items == 0:
                return 0.0

            documented = 0
            for item in classes + functions:
                # 简化检查：如果类/函数名称暗示其功能，认为有一定文档价值
                if any(
                    keyword in item["name"].lower()
                    for keyword in ["test", "init", "main", "run"]
                ):
                    documented += 1

            return (documented / total_items) * 100
        except Exception:
            return 0.0

    def _calculate_avg_function_length(self, functions: List) -> float:
        """计算平均函数长度"""
        try:
            if not functions:
                return 0.0

            total_length = 0
            count = 0
            for func in functions:
                if func["line_end"] != "unknown":
                    length = func["line_end"] - func["line_start"] + 1
                    total_length += length
                    count += 1

            return total_length / count if count > 0 else 0.0
        except Exception:
            return 0.0

    def _assess_risks(
        self,
        max_complexity: int,
        class_count: int,
        function_count: int,
        dependencies: Dict,
    ) -> Dict[str, Any]:
        """评估重构风险"""
        risk_score = 0
        risks = []

        # 复杂度风险
        if max_complexity > 20:
            risk_score += 3
            risks.append("极高复杂度，需要立即重构")
        elif max_complexity > 15:
            risk_score += 2
            risks.append("高复杂度，建议重构")
        elif max_complexity > 10:
            risk_score += 1
            risks.append("中等复杂度，应考虑重构")

        # 结构风险
        if function_count > 50:
            risk_score += 2
            risks.append("函数过多，模块职责不清")
        elif function_count > 30:
            risk_score += 1
            risks.append("函数较多，可能需要拆分")

        if class_count > 10:
            risk_score += 2
            risks.append("类过多，设计可能复杂")

        # 依赖风险
        total_deps = dependencies.get("total_dependencies", 0)
        if total_deps > 15:
            risk_score += 2
            risks.append("依赖过多，耦合度高")
        elif total_deps > 10:
            risk_score += 1
            risks.append("依赖较多，需要关注耦合度")

        # 风险等级
        if risk_score >= 5:
            risk_level = "HIGH"
        elif risk_score >= 3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risks": risks,
            "refactoring_priority": "IMMEDIATE"
            if risk_level == "HIGH"
            else "HIGH"
            if risk_level == "MEDIUM"
            else "MEDIUM",
        }

    def generate_assessment_report(self, file_paths: List[str]) -> str:
        """生成评估报告"""
        report_lines = []
        report_lines.append("# 详细技术债务复杂度评估报告")
        report_lines.append("")
        report_lines.append(
            f"**评估时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        report_lines.append(f"**评估文件数**: {len(file_paths)}")
        report_lines.append("")

        for file_path in file_paths:
            print(f"分析文件: {file_path}")
            result = self.analyze_file_complexity(file_path)

            report_lines.append(f"## 📁 文件: {file_path}")
            report_lines.append("")

            if "error" in result:
                report_lines.append(f"❌ **分析错误**: {result['error']}")
                report_lines.append("")
                continue

            # 文件基本信息
            size_info = result["file_size"]
            report_lines.append("### 📊 文件规模")
            report_lines.append(f"- 总行数: {size_info['total_lines']:,}")
            report_lines.append(f"- 代码行数: {size_info['code_lines']:,}")
            report_lines.append(f"- 注释行数: {size_info['comment_lines']:,}")
            report_lines.append(f"- 空行数: {size_info['empty_lines']:,}")
            report_lines.append("")

            # 结构信息
            structure_info = result["structure"]
            report_lines.append("### 🏗️ 代码结构")
            report_lines.append(f"- 类数量: {structure_info['classes_count']}")
            report_lines.append(f"- 函数数量: {structure_info['functions_count']}")
            report_lines.append(f"- 导入数量: {structure_info['imports_count']}")
            report_lines.append("")

            if structure_info["classes"]:
                report_lines.append("**类列表**:")
                for cls in structure_info["classes"]:
                    report_lines.append(
                        f"- {cls['name']} (行 {cls['line_start']}-{cls['line_end']}, 方法: {len(cls['methods'])})"
                    )
                report_lines.append("")

            # 复杂度信息
            complexity_info = result["complexity"]
            report_lines.append("### ⚠️ 复杂度分析")
            report_lines.append(f"- 最高复杂度: {complexity_info['max_complexity']}")
            report_lines.append(
                f"- 平均复杂度: {complexity_info['avg_complexity']:.2f}"
            )
            report_lines.append(
                f"- 复杂函数数量: {complexity_info['complex_functions']}"
            )
            report_lines.append("")

            if complexity_info["complex_functions_detail"]:
                report_lines.append("**高复杂度函数** (复杂度 > 10):")
                for func in complexity_info["complex_functions_detail"][
                    :5
                ]:  # 只显示前5个
                    report_lines.append(
                        f"- {func['name']}: {func['complexity']} (行 {func['line']})"
                    )
                report_lines.append("")

            # 依赖信息
            dep_info = result["dependencies"]
            if "error" not in dep_info:
                report_lines.append("### 🔗 依赖分析")
                report_lines.append(f"- 总依赖数: {dep_info['total_dependencies']}")
                report_lines.append(
                    f"- 内部依赖: {len(dep_info['internal_dependencies'])}"
                )
                report_lines.append(
                    f"- 外部依赖: {len(dep_info['external_dependencies'])}"
                )
                report_lines.append(
                    f"- 标准库依赖: {len(dep_info['standard_dependencies'])}"
                )
                report_lines.append("")

            # 测试覆盖率
            test_info = result["test_coverage"]
            report_lines.append("### 🧪 测试覆盖率")
            report_lines.append(f"- 测试文件数量: {len(test_info['test_files_found'])}")
            report_lines.append(f"- 测试方法数量: {test_info['test_methods_count']}")
            report_lines.append(f"- 覆盖率估算: {test_info['coverage_estimate']}")
            report_lines.append("")

            # 质量指标
            quality_info = result["quality_metrics"]
            report_lines.append("### 📈 质量指标")
            report_lines.append(
                f"- 可维护性指数: {quality_info['maintainability_index']:.1f}/100"
            )
            report_lines.append(
                f"- 文档覆盖率: {quality_info['documentation_ratio']:.1f}%"
            )
            report_lines.append(
                f"- 平均函数长度: {quality_info['function_length_avg']:.1f} 行"
            )
            report_lines.append("")

            # 风险评估
            risk_info = result["risk_assessment"]
            report_lines.append("### 🚨 风险评估")
            report_lines.append(f"- 风险等级: **{risk_info['risk_level']}**")
            report_lines.append(f"- 风险评分: {risk_info['risk_score']}/10")
            report_lines.append(
                f"- 重构优先级: **{risk_info['refactoring_priority']}**"
            )
            report_lines.append("")

            if risk_info["risks"]:
                report_lines.append("**主要风险**:")
                for risk in risk_info["risks"]:
                    report_lines.append(f"- ⚠️ {risk}")
                report_lines.append("")

            report_lines.append("---")
            report_lines.append("")

        # 总结和建议
        report_lines.append("## 📋 总体评估和建议")
        report_lines.append("")

        return "\n".join(report_lines)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="详细技术债务复杂度评估")
    parser.add_argument(
        "--target", required=True, help="目标文件路径 (支持多个文件，用逗号分隔)"
    )
    parser.add_argument(
        "--output", help="输出报告路径 (默认: detailed_technical_debt_assessment.md)"
    )
    parser.add_argument("--detailed", action="store_true", help="生成详细报告")

    args = parser.parse_args()

    # 解析目标文件
    target_files = [f.strip() for f in args.target.split(",")]

    # 验证文件存在
    existing_files = []
    for file_path in target_files:
        if os.path.exists(file_path):
            existing_files.append(file_path)
        else:
            print(f"⚠️  文件不存在: {file_path}")

    if not existing_files:
        print("❌ 没有找到有效的目标文件")
        return 1

    # 执行分析
    assessor = DetailedTechnicalDebtAssessment()
    report = assessor.generate_assessment_report(existing_files)

    # 输出报告
    if args.output:
        output_path = args.output
    else:
        output_path = "detailed_technical_debt_assessment.md"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"✅ 详细技术债务评估报告已生成: {output_path}")
    print(f"📁 评估文件数: {len(existing_files)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
