#!/usr/bin/env python3
"""# 功能：本地P0质量门禁检查脚本
# 用法：python scripts/quality_gate/p0_quality_check.py
# 作用：在提交前本地运行质量检查，避免CI失败
# 作者：Claude (基于P0优先级任务)
# 创建日期：2026-01-03
# 版本：1.0.0
"""

import logging
import subprocess
import sys
from pathlib import Path


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class QualityCheckResult:
    """质量检查结果"""

    def __init__(self, name: str, passed: bool, message: str = ""):
        self.name = name
        self.passed = passed
        self.message = message


def run_command(command: list, description: str) -> tuple[bool, str]:
    """运行命令并返回结果

    Args:
        command: 命令列表
        description: 命令描述

    Returns:
        (success, output): 是否成功和输出

    """
    logger.info(f"🔍 {description}...")
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=300,
        )

        success = result.returncode == 0
        output = result.stdout + result.stderr

        return success, output

    except subprocess.TimeoutExpired:
        logger.error(f"⏰ {description} 超时")
        return False, "检查超时"
    except Exception as e:
        logger.error(f"❌ {description} 失败: {e}")
        return False, str(e)


def check_pylint_errors() -> QualityCheckResult:
    """检查Pylint Error级别问题"""
    success, output = run_command(
        [
            "pylint",
            "src/",
            "--rcfile=.pylintrc",
            "--errors-only",
            "--disable=import-error,no-member",
            "--output-format=colorized",
        ],
        "Pylint Error级别检查",
    )

    if success:
        return QualityCheckResult("Pylint Errors", True, "✅ 无Error级别问题")
    return QualityCheckResult(
        "Pylint Errors",
        False,
        "❌ 发现Error级别问题\n💡 修复: pylint src/ --errors-only --disable=import-error,no-member",
    )


def check_black_formatting() -> QualityCheckResult:
    """检查Black格式化"""
    success, output = run_command(
        ["black", "--check", "--diff", "--line-length=120", "src/"],
        "Black格式检查",
    )

    if success:
        return QualityCheckResult("代码格式化", True, "✅ 格式符合规范")
    return QualityCheckResult(
        "代码格式化",
        False,
        "❌ 格式不符合规范\n💡 修复: black src/ --line-length=120",
    )


def check_isort_imports() -> QualityCheckResult:
    """检查isort导入排序"""
    success, output = run_command(
        ["isort", "--check-only", "--diff", "src/"],
        "isort导入检查",
    )

    if success:
        return QualityCheckResult("导入排序", True, "✅ 导入排序正确")
    return QualityCheckResult(
        "导入排序",
        False,
        "❌ 导入排序不符合规范\n💡 修复: isort src/",
    )


def check_bandit_security() -> QualityCheckResult:
    """检查Bandit安全问题"""
    success, output = run_command(
        ["bandit", "-r", "src/", "-c", "config/.security.yml", "-ll"],
        "Bandit安全扫描",
    )

    if success:
        return QualityCheckResult("安全扫描", True, "✅ 无安全问题")
    return QualityCheckResult(
        "安全扫描",
        False,
        "❌ 发现安全问题\n💡 检查: bandit -r src/ -c config/.security.yml",
    )


def check_safety_dependencies() -> QualityCheckResult:
    """检查Safety依赖安全"""
    success, output = run_command(
        ["safety", "check", "--json"],
        "Safety依赖检查",
    )

    if success:
        return QualityCheckResult("依赖安全", True, "✅ 无依赖漏洞")
    return QualityCheckResult(
        "依赖安全",
        False,
        "❌ 发现依赖漏洞\n💡 更新: pip install --upgrade <package>",
    )


def check_python_syntax() -> QualityCheckResult:
    """检查Python语法"""
    logger.info("🔍 Python语法检查...")

    try:
        # 检查所有Python文件
        python_files = list(Path("src/").rglob("*.py"))
        errors = []

        for py_file in python_files:
            try:
                with open(py_file, encoding="utf-8") as f:
                    compile(f.read(), py_file, "exec")
            except SyntaxError as e:
                errors.append(f"{py_file}: {e}")

        if errors:
            return QualityCheckResult(
                "Python语法",
                False,
                f"❌ 发现语法错误\n{''.join(errors)}",
            )
        return QualityCheckResult("Python语法", True, "✅ 语法正确")

    except Exception as e:
        return QualityCheckResult(
            "Python语法",
            False,
            f"❌ 检查失败: {e}",
        )


def print_summary(results: list[QualityCheckResult]):
    """打印检查摘要"""
    print("\n" + "=" * 60)
    print("P0质量门禁检查报告")
    print("=" * 60)
    print(f"\n检查时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    print("检查结果:")
    print("-" * 60)

    passed_count = 0
    failed_count = 0

    for result in results:
        status = "✅ 通过" if result.passed else "❌ 失败"
        print(f"{result.name:20s} | {status}")
        if result.message:
            print(f"  {result.message}")

        if result.passed:
            passed_count += 1
        else:
            failed_count += 1

    print("-" * 60)
    print(f"\n总计: {passed_count} 通过, {failed_count} 失败")

    if failed_count == 0:
        print("\n✅ **所有检查通过，代码质量符合P0标准**")
        print("\n🚀 可以安全提交代码！")
    else:
        print("\n❌ **部分检查失败，请修复后重新提交**")
        print("\n💡 修复建议：")
        print("   1. 查看上述失败检查的详细信息")
        print("   2. 运行建议的修复命令")
        print("   3. 重新运行此脚本验证")
        print("\n🔄 快速修复命令：")
        print("   # 格式化代码")
        print("   black src/ --line-length=120")
        print("   isort src/")
        print("\n   # 检查问题")
        print("   pylint src/ --errors-only --disable=import-error,no-member")
        print("   bandit -r src/ -c config/.security.yml")

    print("\n" + "=" * 60)


def main():
    """主函数"""
    print("\n🔍 P0质量门禁本地检查")
    print("=" * 60)

    # 检查是否在项目根目录
    if not Path("src/").exists():
        logger.error("❌ 请在项目根目录运行此脚本")
        return 1

    # 运行所有检查
    results = [
        check_pylint_errors(),
        check_black_formatting(),
        check_isort_imports(),
        check_bandit_security(),
        check_safety_dependencies(),
        check_python_syntax(),
    ]

    # 打印摘要
    print_summary(results)

    # 返回退出码
    failed_count = sum(1 for r in results if not r.passed)
    return 1 if failed_count > 0 else 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n⏹️ 用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 检查失败: {e}", exc_info=True)
        sys.exit(1)
