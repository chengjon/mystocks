#!/usr/bin/env python3
"""
测试报告生成工具
生成综合测试报告包括覆盖率、性能和质量指标
"""

import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path


class TestReportGenerator:
    """测试报告生成器"""

    def __init__(self, report_dir="test_reports"):
        self.report_dir = Path(report_dir)
        self.report_data = {
            "generated_at": datetime.now().isoformat(),
            "summary": {},
            "unit_tests": {},
            "integration_tests": {},
            "performance_tests": {},
            "coverage": {},
        }

    def parse_junit_xml(self, xml_file):
        """解析JUnit XML报告"""
        if not xml_file.exists():
            return None

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # 提取测试统计
            return {
                "total": int(root.attrib.get("tests", 0)),
                "passed": int(root.attrib.get("tests", 0))
                - int(root.attrib.get("failures", 0))
                - int(root.attrib.get("errors", 0)),
                "failed": int(root.attrib.get("failures", 0)),
                "errors": int(root.attrib.get("errors", 0)),
                "skipped": int(root.attrib.get("skipped", 0)),
                "time": float(root.attrib.get("time", 0.0)),
            }
        except Exception as e:
            print(f"Error parsing {xml_file}: {e}")
            return None

    def parse_coverage_xml(self, xml_file):
        """解析覆盖率XML报告"""
        if not xml_file.exists():
            return None

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # 提取覆盖率统计
            coverage_elem = root.find(".//coverage")
            if coverage_elem is not None:
                line_rate = float(coverage_elem.attrib.get("line-rate", 0.0))
                branch_rate = float(coverage_elem.attrib.get("branch-rate", 0.0))

                return {
                    "line_coverage": line_rate * 100,
                    "branch_coverage": branch_rate * 100,
                    "overall_coverage": ((line_rate + branch_rate) / 2) * 100,
                }
        except Exception as e:
            print(f"Error parsing coverage {xml_file}: {e}")
            return None

        return None

    def collect_test_results(self):
        """收集所有测试结果"""
        # 单元测试
        unit_xml = self.report_dir / "unit_tests.xml"
        if unit_xml.exists():
            self.report_data["unit_tests"] = self.parse_junit_xml(unit_xml)

        # 集成测试
        integration_xml = self.report_dir / "integration_tests.xml"
        if integration_xml.exists():
            self.report_data["integration_tests"] = self.parse_junit_xml(
                integration_xml
            )

        # 性能测试
        performance_xml = self.report_dir / "performance_tests.xml"
        if performance_xml.exists():
            self.report_data["performance_tests"] = self.parse_junit_xml(
                performance_xml
            )

        # 覆盖率
        coverage_xml = self.report_dir / "coverage" / "coverage.xml"
        if coverage_xml.exists():
            self.report_data["coverage"] = self.parse_coverage_xml(coverage_xml)

    def calculate_summary(self):
        """计算总体摘要"""
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_errors = 0

        for test_type in ["unit_tests", "integration_tests", "performance_tests"]:
            if self.report_data[test_type]:
                total_tests += self.report_data[test_type]["total"]
                total_passed += self.report_data[test_type]["passed"]
                total_failed += self.report_data[test_type]["failed"]
                total_errors += self.report_data[test_type]["errors"]

        self.report_data["summary"] = {
            "total_tests": total_tests,
            "passed": total_passed,
            "failed": total_failed,
            "errors": total_errors,
            "success_rate": (
                (total_passed / total_tests * 100) if total_tests > 0 else 0
            ),
        }

    def generate_markdown_report(self):
        """生成Markdown格式报告"""
        report = []
        report.append("# GPU API系统测试报告\n")
        report.append(f"**生成时间**: {self.report_data['generated_at']}\n")
        report.append("---\n\n")

        # 总体摘要
        report.append("## 📊 测试总体摘要\n")
        summary = self.report_data["summary"]
        report.append(f"- **总测试数**: {summary.get('total_tests', 0)}\n")
        report.append(f"- **通过**: {summary.get('passed', 0)} ✅\n")
        report.append(f"- **失败**: {summary.get('failed', 0)} ❌\n")
        report.append(f"- **错误**: {summary.get('errors', 0)} ⚠️\n")
        report.append(f"- **成功率**: {summary.get('success_rate', 0):.2f}%\n\n")

        # 单元测试
        if self.report_data["unit_tests"]:
            report.append("## 🧪 单元测试\n")
            unit = self.report_data["unit_tests"]
            report.append(f"- 总数: {unit['total']}\n")
            report.append(f"- 通过: {unit['passed']}\n")
            report.append(f"- 失败: {unit['failed']}\n")
            report.append(f"- 执行时间: {unit['time']:.2f}秒\n\n")

        # 集成测试
        if self.report_data["integration_tests"]:
            report.append("## 🔗 集成测试\n")
            integration = self.report_data["integration_tests"]
            report.append(f"- 总数: {integration['total']}\n")
            report.append(f"- 通过: {integration['passed']}\n")
            report.append(f"- 失败: {integration['failed']}\n")
            report.append(f"- 执行时间: {integration['time']:.2f}秒\n\n")

        # 性能测试
        if self.report_data["performance_tests"]:
            report.append("## ⚡ 性能测试\n")
            performance = self.report_data["performance_tests"]
            report.append(f"- 总数: {performance['total']}\n")
            report.append(f"- 通过: {performance['passed']}\n")
            report.append(f"- 失败: {performance['failed']}\n")
            report.append(f"- 执行时间: {performance['time']:.2f}秒\n\n")

        # 代码覆盖率
        if self.report_data["coverage"]:
            report.append("## 📈 代码覆盖率\n")
            coverage = self.report_data["coverage"]
            report.append(f"- **行覆盖率**: {coverage.get('line_coverage', 0):.2f}%\n")
            report.append(
                f"- **分支覆盖率**: {coverage.get('branch_coverage', 0):.2f}%\n"
            )
            report.append(
                f"- **总体覆盖率**: {coverage.get('overall_coverage', 0):.2f}%\n\n"
            )

            # 覆盖率评级
            overall = coverage.get("overall_coverage", 0)
            if overall >= 80:
                report.append("**评级**: ⭐⭐⭐⭐⭐ 优秀\n\n")
            elif overall >= 70:
                report.append("**评级**: ⭐⭐⭐⭐ 良好\n\n")
            elif overall >= 60:
                report.append("**评级**: ⭐⭐⭐ 中等\n\n")
            else:
                report.append("**评级**: ⭐⭐ 需改进\n\n")

        # 建议
        report.append("## 💡 建议\n")
        if summary.get("success_rate", 0) < 100:
            report.append("- ⚠️ 存在失败的测试用例，请及时修复\n")
        if (
            self.report_data["coverage"]
            and self.report_data["coverage"].get("overall_coverage", 0) < 80
        ):
            report.append("- 📈 代码覆盖率低于80%，建议补充测试用例\n")
        if summary.get("success_rate", 0) >= 100:
            report.append("- ✅ 所有测试通过，代码质量良好\n")

        report.append("\n---\n")
        report.append("*报告由GPU API测试系统自动生成*\n")

        return "".join(report)

    def save_json_report(self, filename="test_report.json"):
        """保存JSON格式报告"""
        output_file = self.report_dir / filename
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.report_data, f, indent=2, ensure_ascii=False)
        print(f"JSON报告已保存: {output_file}")

    def save_markdown_report(self, filename="test_report.md"):
        """保存Markdown格式报告"""
        output_file = self.report_dir / filename
        markdown_content = self.generate_markdown_report()
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"Markdown报告已保存: {output_file}")

    def generate_reports(self):
        """生成所有格式的报告"""
        print("开始收集测试结果...")
        self.collect_test_results()

        print("计算测试摘要...")
        self.calculate_summary()

        print("生成报告...")
        self.save_json_report()
        self.save_markdown_report()

        # 打印摘要到控制台
        print("\n" + "=" * 60)
        print("测试报告摘要")
        print("=" * 60)
        print(self.generate_markdown_report())


def main():
    """主函数"""
    generator = TestReportGenerator()
    generator.generate_reports()


if __name__ == "__main__":
    main()
