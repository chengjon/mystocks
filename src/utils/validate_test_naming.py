#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# 功能：验证测试文件命名规范是否符合pytest约定
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：1.0.0
# 依赖：无外部依赖
# 注意事项：
#   - 检查所有测试文件是否以test_开头
#   - 统计符合/不符合pytest规范的文件
#   - 提供修复建议
# 版权：MyStocks Project © 2025
"""

from pathlib import Path
from typing import List, Dict


class TestNamingValidator:
    """测试文件命名规范验证器"""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.compliant_files: List[Path] = []
        self.non_compliant_files: List[Path] = []
        self.ignored_dirs = {
            ".git",
            "node_modules",
            "venv",
            ".venv",
            "env",
            "__pycache__",
            ".pytest_cache",
            "htmlcov",
        }

    def find_all_test_files(self) -> List[Path]:
        """查找所有测试文件（包含'test'关键字的.py文件）"""
        test_files = []

        # 排除的文件名模式（业务代码，不是测试）
        excluded_patterns = [
            "validate_test_naming.py",  # 验证工具本身
            "backtest_engine.py",  # 回测引擎业务代码
            "test_monitoring_with_redis.py",  # 监控数据生成脚本
        ]

        for py_file in self.root_dir.rglob("*.py"):
            # 跳过忽略目录
            if any(ignored in py_file.parts for ignored in self.ignored_dirs):
                continue

            # 跳过排除的文件
            if py_file.name in excluded_patterns:
                continue

            # 检查文件名是否包含'test'
            if "test" in py_file.name.lower():
                test_files.append(py_file)

        return test_files

    def validate_file_naming(self, file_path: Path) -> bool:
        """验证单个文件是否符合pytest命名规范"""
        filename = file_path.name

        # pytest规范: 测试文件必须以test_开头或以_test.py结尾
        # 推荐: 统一使用test_开头
        if filename.startswith("test_") and filename.endswith(".py"):
            return True

        return False

    def validate_all(self) -> Dict:
        """验证所有测试文件"""
        test_files = self.find_all_test_files()

        for test_file in test_files:
            if self.validate_file_naming(test_file):
                self.compliant_files.append(test_file)
            else:
                self.non_compliant_files.append(test_file)

        return {
            "total": len(test_files),
            "compliant": len(self.compliant_files),
            "non_compliant": len(self.non_compliant_files),
            "compliance_rate": ((len(self.compliant_files) / len(test_files) * 100) if test_files else 100.0),
        }

    def suggest_rename(self, file_path: Path) -> str:
        """为不符合规范的文件建议新名称"""
        filename = file_path.name

        # 移除.py后缀
        name_without_ext = filename[:-3]

        # 如果以_test结尾,转换为test_开头
        if name_without_ext.endswith("_test"):
            base_name = name_without_ext[:-5]  # 移除_test
            return f"test_{base_name}.py"

        # 如果包含test但不符合规范
        if "test" in name_without_ext.lower():
            # 尝试提取test之后的部分
            parts = name_without_ext.split("_")
            if "test" in parts:
                # 找到test的位置
                test_index = parts.index("test")
                # 重组为test_开头
                remaining = (
                    "_".join(parts[test_index + 1 :]) if test_index + 1 < len(parts) else "_".join(parts[:test_index])
                )
                return f"test_{remaining}.py" if remaining else f"test_{name_without_ext}.py"

        # 默认直接加test_前缀
        return f"test_{name_without_ext}.py"

    def generate_report(self) -> str:
        """生成验证报告"""
        stats = self.validate_all()

        report = []
        report.append("\n" + "=" * 80)
        report.append("测试文件命名规范验证报告")
        report.append("=" * 80 + "\n")

        # 统计信息
        report.append("📊 统计信息:")
        report.append(f"  - 总测试文件数: {stats['total']}")
        report.append(f"  - ✅ 符合规范: {stats['compliant']} 个")
        report.append(f"  - ❌ 不符合规范: {stats['non_compliant']} 个")
        report.append(f"  - 📈 合规率: {stats['compliance_rate']:.1f}%\n")

        # 符合规范的文件（仅显示前10个）
        if self.compliant_files:
            report.append("✅ 符合规范的文件 (前10个):")
            for i, file_path in enumerate(self.compliant_files[:10], 1):
                report.append(f"  {i}. {file_path.relative_to(self.root_dir)}")
            if len(self.compliant_files) > 10:
                report.append(f"  ... 还有 {len(self.compliant_files) - 10} 个文件")
            report.append("")

        # 不符合规范的文件及修复建议
        if self.non_compliant_files:
            report.append("❌ 不符合规范的文件及修复建议:")
            for i, file_path in enumerate(self.non_compliant_files, 1):
                suggested_name = self.suggest_rename(file_path)
                rel_path = file_path.relative_to(self.root_dir)
                report.append(f"  {i}. {rel_path}")
                report.append(f"     建议: {file_path.parent}/{suggested_name}")
                report.append(f"     命令: git mv {rel_path} {file_path.parent}/{suggested_name}")
            report.append("")

        # 验收标准
        report.append("=" * 80)
        report.append("验收标准检查")
        report.append("=" * 80)

        checks = [
            ("所有测试文件以test_开头", stats["non_compliant"] == 0),
            ("合规率 ≥ 95%", stats["compliance_rate"] >= 95.0),
        ]

        all_passed = True
        for check_name, passed in checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            report.append(f"{status} - {check_name}")
            if not passed:
                all_passed = False

        report.append("")

        # 总结
        if all_passed:
            report.append("🎉 所有验收标准通过！测试文件命名规范符合pytest要求。")
        else:
            report.append("⚠️  部分验收标准未通过，请根据建议修复不符合规范的文件。")

        report.append("=" * 80 + "\n")

        return "\n".join(report)


def main():
    """主函数"""
    print("\n启动测试文件命名规范验证...\n")

    validator = TestNamingValidator()
    report = validator.generate_report()

    print(report)

    # 返回退出码
    stats = {
        "total": len(validator.compliant_files) + len(validator.non_compliant_files),
        "compliant": len(validator.compliant_files),
        "non_compliant": len(validator.non_compliant_files),
    }

    if stats["non_compliant"] > 0:
        return 1
    else:
        return 0


if __name__ == "__main__":
    exit(main())
