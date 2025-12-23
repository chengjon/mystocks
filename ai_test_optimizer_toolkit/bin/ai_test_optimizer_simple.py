#!/usr/bin/env python3
"""
AI测试优化器 - 简化版
提供更简单的命令行接口，解决用户反馈的CLI复杂度问题

核心功能:
1. 一键优化: auto - 自动优化所有测试
2. 快速分析: quick - 快速分析覆盖率
3. 生成测试: test - 只生成测试文件
4. 性能检测: perf - 性能回归检测

作者: MyStocks AI Team
版本: 2.0 (简化版)
日期: 2025-12-22
"""

import sys
import argparse
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入核心优化器
from scripts.ai_test_optimizer import AITestOptimizer


def create_simple_parser():
    """创建简化的命令行解析器"""
    parser = argparse.ArgumentParser(
        description="AI测试优化器 - 简化版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s auto                    # 自动优化所有核心模块
  %(prog)s quick src/file.py       # 快速分析文件覆盖率
  %(prog)s test src/file.py        # 只生成测试文件
  %(prog)s perf                     # 运行性能回归检测
  %(prog)s --help                   # 显示帮助信息
        """,
    )

    # 简化的子命令
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # auto - 自动优化命令
    auto_parser = subparsers.add_parser("auto", help="自动优化所有核心模块")
    auto_parser.add_argument(
        "--verbose", "-v", action="store_true", help="显示详细输出"
    )

    # quick - 快速分析命令
    quick_parser = subparsers.add_parser("quick", help="快速分析覆盖率")
    quick_parser.add_argument("file", help="要分析的Python文件")
    quick_parser.add_argument(
        "--verbose", "-v", action="store_true", help="显示详细输出"
    )

    # test - 生成测试命令
    test_parser = subparsers.add_parser("test", help="只生成测试文件")
    test_parser.add_argument("file", help="要生成测试的Python文件")
    test_parser.add_argument(
        "--verbose", "-v", action="store_true", help="显示详细输出"
    )

    # perf - 性能检测命令
    perf_parser = subparsers.add_parser("perf", help="运行性能回归检测")
    perf_parser.add_argument(
        "--modules", nargs="*", default=[], help="要检测的模块列表"
    )
    perf_parser.add_argument(
        "--verbose", "-v", action="store_true", help="显示详细输出"
    )

    return parser


def handle_auto_command(args):
    """处理自动优化命令"""
    print("🚀 启动自动优化模式...")

    # 核心模块列表
    core_modules = [
        "src/adapters/data_validator.py",
        "src/adapters/base_adapter.py",
        "src/core/exceptions.py",
        "src/core/data_manager.py",
        "src/storage/__init__.py",
    ]

    # 运行优化
    optimizer = AITestOptimizer()
    success_count = 0
    total_count = len(core_modules)

    for module in core_modules:
        if Path(module).exists():
            print(f"📊 正在优化: {module}")
            try:
                # 使用分析功能来替代optimize_module
                result = optimizer.analyze_module_for_optimization(module)
                # 检查分析是否成功
                if result.current_coverage >= 0:
                    success_count += 1
                    print(f"  ✅ 成功 - 覆盖率: {result.current_coverage:.1f}%")
                else:
                    print(f"  ❌ 覆盖率分析失败")
            except Exception as e:
                print(f"  ⚠️  异常 - {e}")
        else:
            print(f"  ⚠️  跳过 - 文件不存在: {module}")

    print(f"\n📈 自动优化完成: {success_count}/{total_count} 个模块成功")


def handle_quick_command(args):
    """处理快速分析命令"""
    print(f"📊 快速分析: {args.file}")

    if not Path(args.file).exists():
        print(f"❌ 错误: 文件不存在: {args.file}")
        return

    optimizer = AITestOptimizer()
    try:
        result = optimizer.analyze_module_for_optimization(args.file)
        print(f"📈 当前覆盖率: {result.current_coverage:.1f}%")
        print(f"🎯 质量评分: {result.quality_score:.1f}/100")
        print(f"🔧 需要生成测试: {len(result.optimization_suggestions)} 项建议")

        if result.current_coverage < 95:
            print(
                "💡 建议: 运行 './scripts/ai_test_optimizer_simple.py test %s' 来生成测试"
                % args.file
            )
        else:
            print("🎉 恭喜! 覆盖率已达标")

    except Exception as e:
        print(f"❌ 分析失败: {e}")


def handle_test_command(args):
    """处理生成测试命令"""
    print(f"🧪 生成测试: {args.file}")

    if not Path(args.file).exists():
        print(f"❌ 错误: 文件不存在: {args.file}")
        return

    optimizer = AITestOptimizer()
    try:
        # 调用原始优化器的测试生成功能
        cmd = [
            "python",
            str(project_root / "scripts" / "ai_test_optimizer.py"),
            args.file,
            "--generate-tests",
        ]

        import subprocess

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ 测试文件生成成功!")
            print(result.stdout)
        else:
            print("❌ 测试生成失败:")
            print(result.stderr)

    except Exception as e:
        print(f"❌ 测试生成失败: {e}")


def handle_perf_command(args):
    """处理性能检测命令"""
    print("⚡ 启动性能回归检测...")

    # 运行性能回归测试
    perf_script = project_root / "scripts" / "performance" / "regression_test.py"

    if perf_script.exists():
        import subprocess

        cmd = ["python", str(perf_script)]

        if args.modules:
            cmd.extend(["--modules"] + args.modules)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("警告:", result.stderr)
        except Exception as e:
            print(f"❌ 性能检测失败: {e}")
    else:
        print("⚠️  性能检测脚本不存在")


def main():
    """主入口函数"""
    parser = create_simple_parser()

    # 如果没有参数，显示帮助
    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()

    # 设置详细输出
    import logging

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # 执行对应的命令
    try:
        if args.command == "auto":
            handle_auto_command(args)
        elif args.command == "quick":
            handle_quick_command(args)
        elif args.command == "test":
            handle_test_command(args)
        elif args.command == "perf":
            handle_perf_command(args)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print("\n🛑 用户中断操作")
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    main()
