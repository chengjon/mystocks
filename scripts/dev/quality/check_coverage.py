#!/usr/bin/env python3
"""
本地测试覆盖率检查脚本
模拟CI/CD环境中的覆盖率检查
用于开发阶段的质量保证
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class CoverageChecker:
    """测试覆盖率检查器"""

    def __init__(self):
        self.results = {}
        self.thresholds = {
            "src.adapters.base_adapter": 95.0,
            "src.adapters.data_validator": 90.0,
            "src.core.exceptions": 95.0,
            "src.core.config": 95.0,
        }

    def run_coverage_tests(self) -> Dict[str, float]:
        """运行覆盖率测试并获取结果"""
        print("🔍 开始运行Phase 6测试覆盖率检查...")

        # 定义测试套件
        test_suites = [
            ("src.adapters.base_adapter", "scripts/tests/test_base_adapter_simple.py"),
            (
                "src.adapters.data_validator",
                "scripts/tests/test_data_validator_phase6.py",
            ),
            ("src.core.exceptions", "scripts/tests/test_exceptions_simple.py"),
        ]

        results = {}

        for module, test_file in test_suites:
            print(f"\n📊 测试模块: {module}")

            try:
                # 运行测试并生成覆盖率报告
                cmd = [
                    "python",
                    "-m",
                    "pytest",
                    test_file,
                    f"--cov={module}",
                    "--cov-report=json:reports/coverage/coverage.json",
                    "--cov-report=term-missing",
                    "--tb=no",
                    "-q",
                ]

                result = subprocess.run(
                    cmd, capture_output=True, text=True, cwd=project_root
                )

                if result.returncode == 0:
                    # 解析覆盖率结果
                    coverage = self._parse_coverage_json(
                        f"{module.replace('.', '/')}/.coverage"
                    )
                    if coverage:
                        results[module] = coverage
                        print(f"✅ {module}: {coverage:.1f}% 覆盖率")
                    else:
                        print(f"⚠️  {module}: 无法获取覆盖率数据")
                else:
                    print(f"❌ {module}: 测试执行失败")
                    print(f"错误输出: {result.stderr[:200]}...")

            except Exception as e:
                print(f"❌ {module}: 执行异常 - {e}")

        return results

    def _parse_coverage_json(self, coverage_file: str) -> float:
        """解析coverage.json文件"""
        try:
            coverage_path = project_root / coverage_file
            if coverage_path.exists():
                with open(coverage_path, "r") as f:
                    data = json.load(f)
                    return data["totals"]["percent_covered"]
        except Exception:
            # 尝试其他可能的文件位置
            alternative_paths = [
                project_root / "reports" / "coverage" / "coverage.json",
                project_root / "coverage.json",
                project_root / ".coverage.json",
                coverage_path,
            ]

            for alt_path in alternative_paths:
                if alt_path.exists():
                    try:
                        with open(alt_path, "r") as f:
                            data = json.load(f)
                            return data["totals"]["percent_covered"]
                    except:
                        continue

        except Exception as e:
            print(f"解析覆盖率文件失败: {e}")
        return 0.0

    def check_thresholds(self, results: Dict[str, float]) -> Tuple[bool, List[str]]:
        """检查覆盖率是否满足阈值要求"""
        print("\n🎯 检查覆盖率阈值...")

        all_passed = True
        messages = []

        for module, coverage in results.items():
            threshold = self.thresholds.get(module, 0.0)

            if coverage >= threshold:
                messages.append(
                    f"✅ {module}: {coverage:.1f}% ≥ {threshold:.1f}% (通过)"
                )
            else:
                messages.append(
                    f"❌ {module}: {coverage:.1f}% < {threshold:.1f}% (失败)"
                )
                all_passed = False

        return all_passed, messages

    def generate_report(
        self, results: Dict[str, float], check_passed: bool, messages: List[str]
    ) -> str:
        """生成覆盖率报告"""
        report = []
        report.append("=" * 60)
        report.append("📊 Phase 6 测试覆盖率报告")
        report.append("=" * 60)
        report.append(f"检查时间: {self._get_current_time()}")
        report.append("")

        # 总体状态
        status = "✅ 通过" if check_passed else "❌ 失败"
        report.append(f"总体状态: {status}")
        report.append("")

        # 详细结果
        report.append("📈 模块覆盖率详情:")
        report.append("-" * 30)

        for module, coverage in results.items():
            threshold = self.thresholds.get(module, 0.0)
            status = "✅" if coverage >= threshold else "❌"
            module_name = module.split(".")[-1]
            report.append(
                f"  {status} {module_name:<20} {coverage:6.1f}% (目标: {threshold:.1f}%)"
            )

        report.append("")
        report.append("📋 详细信息:")
        report.append("-" * 30)

        for message in messages:
            report.append(f"  {message}")

        # 统计信息
        if results:
            avg_coverage = sum(results.values()) / len(results)
            report.append("")
            report.append(f"📊 平均覆盖率: {avg_coverage:.1f}%")
            report.append(f"📊 测试模块数: {len(results)}")

        # 建议
        report.append("")
        report.append("💡 建议:")
        if check_passed:
            report.append("  ✅ 所有模块都达到了覆盖率目标")
            report.append("  ✅ 可以继续开发新功能或重构")
        else:
            report.append("  ❌ 需要提升覆盖率到目标值")
            report.append("  ❌ 建议优先处理失败的模块")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)

    def _get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def run(self) -> bool:
        """运行完整的覆盖率检查流程"""
        print("🚀 启动Phase 6测试覆盖率检查...")

        # 运行测试
        results = self.run_coverage_tests()

        if not results:
            print("❌ 没有获取到任何覆盖率数据")
            return False

        # 检查阈值
        check_passed, messages = self.check_thresholds(results)

        # 生成报告
        report = self.generate_report(results, check_passed, messages)
        print("\n" + report)

        # 保存报告到文件
        report_file = project_root / "coverage_report.txt"
        try:
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"\n📄 报告已保存到: {report_file}")
        except Exception as e:
            print(f"⚠️  保存报告失败: {e}")

        return check_passed


def main():
    """主函数"""
    checker = CoverageChecker()

    try:
        success = checker.run()

        if success:
            print("\n🎉 Phase 6 测试覆盖率检查通过!")
            sys.exit(0)
        else:
            print("\n⚠️  Phase 6 测试覆盖率检查未通过，请提升覆盖率后重试")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️  用户中断检查")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 检查过程中发生异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
