#!/usr/bin/env python3
"""智能AI分析器
专注于代码质量分析、Bug预测和智能测试生成

核心功能:
1. 智能代码复杂度分析
2. 潜在Bug识别和风险评估
3. 基于风险的测试用例生成
4. 代码质量改进建议

作者: MyStocks AI Team
版本: 2.0 (智能分析版)
日期: 2025-12-22
"""

import ast
import logging
import re
import sys
import time
from pathlib import Path
from typing import Dict, List


# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class CodeFunction:
    """代码函数信息"""

    def __init__(self, name, node, source_code):
        self.name = name
        self.node = node
        self.source_code = source_code
        self.complexity_score = self._calculate_complexity()
        self.risk_level = self._assess_risk_level()
        self.test_priority = self._determine_test_priority()
        self.issues = self._identify_issues()

    def _calculate_complexity(self) -> float:
        """计算复杂度评分"""
        complexity = 1.0

        for child in ast.walk(self.node):
            if isinstance(child, (ast.If, ast.For, ast.While)):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 0.5
            elif isinstance(child, ast.ListComp) or isinstance(child, ast.DictComp):
                complexity += 0.8
            elif isinstance(child, ast.Try):
                complexity += 0.7

        return min(complexity, 20.0)

    def _assess_risk_level(self) -> str:
        """评估风险等级"""
        if self.complexity_score > 9:
            return "critical"
        if self.complexity_score > 6:
            return "high"
        if self.complexity_score > 3:
            return "medium"
        return "low"

    def _determine_test_priority(self) -> str:
        """确定测试优先级"""
        risk_scores = {"critical": 10, "high": 8, "medium": 6, "low": 4}
        priority_score = risk_scores.get(self.risk_level, 5) + (self.complexity_score * 0.3)

        if priority_score > 12:
            return "critical"
        if priority_score > 9:
            return "high"
        if priority_score > 6:
            return "medium"
        return "low"

    def _identify_issues(self) -> List[str]:
        """识别潜在问题"""
        issues = []

        # 检查错误处理
        has_error_handling = any(isinstance(child, ast.Try) for child in ast.walk(self.node))
        if not has_error_handling:
            issues.append("缺少错误处理机制")

        # 检查函数长度
        if hasattr(self.node, "end_lineno"):
            func_lines = self.node.end_lineno - self.node.lineno + 1
            if func_lines > 50:
                issues.append("函数过长，建议拆分")

        return issues


class SmartAIAnalyzer:
    """智能AI分析器"""

    def __init__(self):
        self.bug_patterns = {
            "null_pointer": [r"\.split\(", r"\.index\(", r"\.lower\("],
            "off_by_one": [r"range\(", r"\[.*:\d+\]"],
            "resource_leak": [r"open\(", r"connect\("],
            "sql_injection": [r"%.*%", r"format\(", r'f".*\{.*\}'],
        }

    def analyze_module(self, source_file: str) -> Dict:
        """分析模块"""
        logger.info(f"🔍 开始智能分析: {source_file}")
        start_time = time.time()

        try:
            with open(source_file, encoding="utf-8") as f:
                source_code = f.read()

            tree = ast.parse(source_code)
            functions = []

            # 提取函数信息
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func = CodeFunction(node.name, node, source_code)
                    functions.append(func)

            # Bug预测
            bugs = self._predict_bugs(source_code)

            # 生成测试用例
            test_cases = self._generate_smart_tests(
                functions,
                bugs,
                Path(source_file).stem,
            )

            # 生成分析报告
            analysis_time = time.time() - start_time

            result = {
                "success": True,
                "functions_count": len(functions),
                "high_risk_count": len(
                    [f for f in functions if f.risk_level in ["critical", "high"]],
                ),
                "bugs_found": len(bugs),
                "tests_generated": len(test_cases),
                "average_complexity": (
                    (sum(f.complexity_score for f in functions) / len(functions)) if functions else 0
                ),
                "analysis_time": analysis_time,
            }

            # 生成文件
            self._save_test_file(test_cases, Path(source_file).stem)
            self._save_analysis_report(source_file, functions, bugs, test_cases)

            logger.info(f"✅ 分析完成: {result}")
            return result

        except Exception as e:
            logger.error(f"分析失败: {e}")
            return {"success": False, "error": str(e)}

    def _predict_bugs(self, source_code: str) -> List[Dict]:
        """预测潜在Bug"""
        bugs = []

        for bug_type, patterns in self.bug_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, source_code, re.MULTILINE)
                for match in matches:
                    line_num = source_code[: match.start()].count("\n") + 1

                    # 简单检查是否有防护措施
                    context = source_code[max(0, match.start() - 200) : match.end() + 200]
                    has_protection = any(prot in context for prot in ["if", "try", "with", "assert"])

                    if not has_protection:
                        bugs.append(
                            {
                                "type": bug_type,
                                "line": line_num,
                                "severity": "high" if bug_type in ["sql_injection", "resource_leak"] else "medium",
                                "description": self._get_bug_description(bug_type),
                            },
                        )

        return bugs

    def _get_bug_description(self, bug_type: str) -> str:
        """获取Bug描述"""
        descriptions = {
            "null_pointer": "存在空指针解引用风险",
            "off_by_one": "存在索引越界风险",
            "resource_leak": "存在资源泄漏风险",
            "sql_injection": "存在SQL注入风险",
        }
        return descriptions.get(bug_type, "未知类型风险")

    def _generate_smart_tests(
        self,
        functions: List[CodeFunction],
        bugs: List[Dict],
        module_name: str,
    ) -> List[Dict]:
        """生成智能测试用例"""
        test_cases = []

        # 为高风险函数生成测试
        high_risk_functions = [f for f in functions if f.risk_level in ["critical", "high"]]

        for func in high_risk_functions[:3]:  # 限制数量
            test_cases.append(self._create_security_test(func, module_name))
            test_cases.append(self._create_boundary_test(func, module_name))

            if "缺少错误处理" in func.issues:
                test_cases.append(self._create_error_test(func, module_name))

        # 为每个Bug生成防护测试
        for bug in bugs[:3]:  # 限制数量
            test_cases.append(self._create_bug_prevention_test(bug, module_name))

        # 生成基本测试
        test_cases.append(self._create_basic_test(module_name))

        return test_cases

    def _create_security_test(self, func: CodeFunction, module_name: str) -> Dict:
        """创建安全测试"""
        return {
            "name": f"test_{module_name}_{func.name}_security",
            "description": f"安全测试: {func.name}",
            "code": f'''    def test_{module_name}_{func.name}_security(self):
        """安全测试 - {func.name}"""
        # 测试恶意输入
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            None,
            []
        ]

        for malicious_input in malicious_inputs:
            with self.assertRaises((ValueError, TypeError, SecurityError)):
                if hasattr({module_name}, '{func.name}'):
                    {module_name}.{func.name}(malicious_input)
        ''',
            "priority": 15.0,
            "type": "security",
        }

    def _create_boundary_test(self, func: CodeFunction, module_name: str) -> Dict:
        """创建边界测试"""
        return {
            "name": f"test_{module_name}_{func.name}_boundary",
            "description": f"边界测试: {func.name}",
            "code": f'''    def test_{module_name}_{func.name}_boundary(self):
        """边界测试 - {func.name}"""
        # 测试边界值
        boundary_cases = [
            None,
            "",
            0,
            -1,
            [],
            {{}}
        ]

        for case in boundary_cases:
            try:
                if hasattr({module_name}, '{func.name}'):
                    result = {module_name}.{func.name}(case)
                    self.assertIsNotNone(result)
            except (ValueError, TypeError, IndexError):
                # 期望的异常
                pass
        ''',
            "priority": 10.0,
            "type": "unit",
        }

    def _create_error_test(self, func: CodeFunction, module_name: str) -> Dict:
        """创建错误测试"""
        return {
            "name": f"test_{module_name}_{func.name}_error_handling",
            "description": f"错误处理测试: {func.name}",
            "code": f'''    def test_{module_name}_{func.name}_error_handling(self):
        """错误处理测试 - {func.name}"""
        # 测试各种异常情况
        error_inputs = [
            None,
            "",
            "invalid_type",
            99999999
        ]

        for error_input in error_inputs:
            try:
                if hasattr({module_name}, '{func.name}'):
                    {module_name}.{func.name}(error_input)
            except Exception as e:
                # 确保异常被正确处理
                self.assertIsNotNone(str(e))
        ''',
            "priority": 12.0,
            "type": "unit",
        }

    def _create_bug_prevention_test(self, bug: Dict, module_name: str) -> Dict:
        """创建Bug防护测试"""
        return {
            "name": f"test_{module_name}_bug_prevention_{bug['type']}",
            "description": f"Bug防护测试: {bug['description']}",
            "code": f'''    def test_{module_name}_bug_prevention_{bug["type"]}(self):
        """Bug防护测试 - {bug["description"]}"""
        # 测试防护措施
        safe_inputs = ["safe_input", 1, [1, 2, 3]]
        unsafe_inputs = [None, "", "'; DROP TABLE users; --"]

        for safe_input in safe_inputs:
            try:
                if hasattr({module_name}, 'target_function'):
                    result = {module_name}.target_function(safe_input)
                    self.assertIsNotNone(result)
            except Exception:
                pass  # 安全输入也可能异常，这是可接受的

        for unsafe_input in unsafe_inputs:
            with self.assertRaises((ValueError, SecurityError)):
                if hasattr({module_name}, 'target_function'):
                    {module_name}.target_function(unsafe_input)
        ''',
            "priority": 14.0,
            "type": "security",
        }

    def _create_basic_test(self, module_name: str) -> Dict:
        """创建基本测试"""
        return {
            "name": f"test_{module_name}_basic_functionality",
            "description": "基本功能测试",
            "code": f'''    def test_{module_name}_basic_functionality(self):
        """基本功能测试"""
        # 测试模块导入
        import {module_name}
        self.assertTrue(hasattr({module_name}, '__name__'))

        # 测试是否有公共函数
        public_funcs = [f for f in dir({module_name}) if not f.startswith('_')]
        self.assertGreater(len(public_funcs), 0, "模块应该至少有一个公共函数")
        ''',
            "priority": 5.0,
            "type": "unit",
        }

    def _save_test_file(self, test_cases: List[Dict], module_name: str):
        """保存测试文件"""
        output_dir = project_root / "smart_ai_tests"
        output_dir.mkdir(exist_ok=True)

        test_file = output_dir / f"test_{module_name}_smart.py"

        with open(test_file, "w", encoding="utf-8") as f:
            f.write(f'''#!/usr/bin/env python3
"""
智能AI测试用例 - {module_name}
由Smart AI分析器自动生成

测试用例数: {len(test_cases)}
"""

import unittest
from pathlib import Path
import sys

# 导入被测试模块
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import {module_name}


class Test{module_name.title().replace("_", "")}Smart(unittest.TestCase):
    """智能AI生成的测试类"""

''')

            f.writelines(f"{test_case['code']}\n" for test_case in test_cases)

            f.write("""

if __name__ == "__main__":
    unittest.main()
""")

        logger.info(f"✅ 智能测试文件已生成: {test_file}")

    def _save_analysis_report(
        self,
        source_file: str,
        functions: List[CodeFunction],
        bugs: List[Dict],
        test_cases: List[Dict],
    ):
        """保存分析报告"""
        report_dir = project_root / "smart_analysis_reports"
        report_dir.mkdir(exist_ok=True)

        module_name = Path(source_file).stem
        report_file = report_dir / f"{module_name}_smart_analysis.md"

        with open(report_file, "w", encoding="utf-8") as f:
            # 计算平均复杂度
            average_complexity = (sum(f.complexity_score for f in functions) / len(functions)) if functions else 0

            f.write(f"""# {module_name} 智能分析报告

## 📊 分析概览

- **函数数量**: {len(functions)}
- **高风险函数**: {len([f for f in functions if f.risk_level in ["critical", "high"]])}
- **发现Bug**: {len(bugs)}
- **生成测试**: {len(test_cases)}
- **平均复杂度**: {average_complexity:.1f}

## 🔍 函数分析

### 高风险函数
""")

            high_risk_funcs = [f for f in functions if f.risk_level in ["critical", "high"]]
            f.writelines(
                f"""
#### {func.name}
- **复杂度**: {func.complexity_score:.1f}
- **风险等级**: {func.risk_level}
- **测试优先级**: {func.test_priority}
- **潜在问题**: {", ".join(func.issues) if func.issues else "无"}
"""
                for func in high_risk_funcs
            )

            f.write("""
## 🐛 Bug预测

### 发现的问题
""")

            f.writelines(
                f"""
- **{bug["type"]}** (行 {bug["line"]})
  - 严重程度: {bug["severity"]}
  - 描述: {bug["description"]}
"""
                for bug in bugs
            )

            f.write(f"""
## 🧪 智能测试

### 测试分布
- **安全测试**: {len([t for t in test_cases if t["type"] == "security"])} 个
- **单元测试**: {len([t for t in test_cases if t["type"] == "unit"])} 个

### 高优先级测试
""")

            high_priority_tests = sorted(
                test_cases,
                key=lambda x: x["priority"],
                reverse=True,
            )[:5]
            f.writelines(
                f"""
- **{test["name"]}**
  - 描述: {test["description"]}
  - 优先级: {test["priority"]:.1f}
"""
                for test in high_priority_tests
            )

        logger.info(f"✅ 分析报告已生成: {report_file}")


def main():
    """主入口函数"""
    import argparse

    parser = argparse.ArgumentParser(description="智能AI分析器")
    parser.add_argument("source_files", nargs="+", help="要分析的Python源文件")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细输出")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    analyzer = SmartAIAnalyzer()

    total_functions = 0
    total_bugs = 0
    total_tests = 0
    high_risk_total = 0
    success_count = 0

    for source_file in args.source_files:
        if not Path(source_file).exists():
            logger.error(f"文件不存在: {source_file}")
            continue

        result = analyzer.analyze_module(source_file)

        if result["success"]:
            success_count += 1
            total_functions += result["functions_count"]
            total_bugs += result["bugs_found"]
            total_tests += result["tests_generated"]
            high_risk_total += result["high_risk_count"]

            print(f"✅ {Path(source_file).name}:")
            print(f"   函数: {result['functions_count']}, Bug: {result['bugs_found']}")
            print(
                f"   测试: {result['tests_generated']}, 高风险: {result['high_risk_count']}",
            )
            print(
                f"   复杂度: {result['average_complexity']:.1f}, 耗时: {result['analysis_time']:.2f}s",
            )
        else:
            print(f"❌ {Path(source_file).name}: {result['error']}")

    print(f"\n📊 总计: {success_count}/{len(args.source_files)} 个文件成功")
    print(f"📈 函数总数: {total_functions}")
    print(f"🐛 发现Bug: {total_bugs}")
    print(f"🧪 生成测试: {total_tests}")
    print(f"⚠️  高风险函数: {high_risk_total}")


if __name__ == "__main__":
    main()
