#!/usr/bin/env python3
"""
AI Test Optimizer Toolkit - 主CLI工具
统一入口点，提供完整的智能测试优化功能
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import yaml

# 添加工具包路径
toolkit_root = Path(__file__).parent.parent
sys.path.insert(0, str(toolkit_root))


class AIToolkitCLI:
    """AI工具包命令行接口"""

    def __init__(self):
        self.toolkit_root = toolkit_root
        self.config = self._load_config()
        self.verbose = False

    def _load_config(self) -> Dict:
        """加载配置文件"""
        config_path = self.toolkit_root / "config" / "ai_toolkit_config.yaml"

        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"⚠️ 配置文件加载失败: {e}")
                return {}
        else:
            print("⚠️ 配置文件不存在，使用默认配置")
            return {}

    def _get_script_path(self, script_name: str) -> Optional[Path]:
        """获取脚本路径"""
        script_path = self.toolkit_root / "bin" / script_name
        if script_path.exists():
            return script_path
        else:
            print(f"❌ 脚本不存在: {script_name}")
            return None

    def _run_script(self, script_path: Path, args: List[str] = None) -> bool:
        """运行脚本"""
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)

        try:
            if self.verbose:
                print(f"🔧 执行命令: {' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            if self.verbose or result.stdout:
                print(result.stdout)

            if result.stderr and self.verbose:
                print("⚠️ 错误输出:", result.stderr)

            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ 脚本执行失败: {e}")
            if self.verbose and e.stdout:
                print("输出:", e.stdout)
            if self.verbose and e.stderr:
                print("错误:", e.stderr)
            return False
        except Exception as e:
            print(f"❌ 执行异常: {e}")
            return False

    def analyze(self, paths: List[str]) -> bool:
        """分析代码质量"""
        print("🔍 开始代码质量分析...")

        script_path = self._get_script_path("smart_ai_analyzer.py")
        if not script_path:
            return False

        return self._run_script(script_path, paths)

    def optimize(self, mode: str = "auto") -> bool:
        """智能测试优化"""
        print(f"🧪 开始智能测试优化 (模式: {mode})...")

        script_path = self._get_script_path("ai_test_optimizer_simple.py")
        if not script_path:
            return False

        args = [mode]
        return self._run_script(script_path, args)

    def coverage(self, threshold: Optional[int] = None) -> bool:
        """检查测试覆盖率"""
        print("📊 开始覆盖率分析...")

        script_path = self.toolkit_root / "plugins" / "quality" / "check_coverage.py"
        if not script_path.exists():
            print("❌ 覆盖率检查脚本不存在")
            return False

        args = []
        if threshold:
            args.extend(["--threshold", str(threshold)])

        return self._run_script(script_path, args)

    def security(self) -> bool:
        """安全扫描"""
        print("🔒 开始安全扫描...")

        # 使用bandit进行安全扫描
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "bandit",
                    "-r",
                    "src/",
                    "scripts/",
                    "-f",
                    "json",
                    "-o",
                    "security_report.json",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            print("✅ 安全扫描完成")
            print("📋 报告保存至: security_report.json")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ 安全扫描失败: {e}")
            return False
        except FileNotFoundError:
            print("❌ bandit未安装，请运行: pip install bandit")
            return False

    def performance(self) -> bool:
        """性能回归测试"""
        print("⚡ 开始性能回归测试...")

        script_path = (
            self.toolkit_root / "plugins" / "performance" / "regression_test.py"
        )
        if not script_path.exists():
            print("❌ 性能测试脚本不存在")
            return False

        return self._run_script(script_path)

    def monitor(self, action: str = "status") -> bool:
        """监控和分析"""
        print(f"📈 开始{action}...")

        if action == "status":
            script_path = (
                self.toolkit_root / "plugins" / "monitoring" / "ai_optimizer_monitor.py"
            )
        elif action == "analyze":
            script_path = (
                self.toolkit_root
                / "plugins"
                / "analysis"
                / "usage_feedback_analyzer.py"
            )
        else:
            print(f"❌ 未知的监控操作: {action}")
            return False

        if not script_path.exists():
            print(f"❌ 监控脚本不存在: {script_path}")
            return False

        args = ["--generate-report"] if action == "analyze" else []
        return self._run_script(script_path, args)

    def batch_analyze(self, directory: str, pattern: str = "*.py") -> bool:
        """批量分析目录"""
        print(f"📁 开始批量分析: {directory}/{pattern}")

        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"❌ 目录不存在: {directory}")
            return False

        # 查找所有Python文件
        python_files = list(dir_path.glob(pattern))
        if not python_files:
            print("⚠️ 未找到匹配的文件")
            return True

        print(f"📋 找到 {len(python_files)} 个文件")

        # 分批处理，避免命令行过长
        batch_size = 20
        success_count = 0

        for i in range(0, len(python_files), batch_size):
            batch = python_files[i : i + batch_size]
            print(
                f"🔧 处理批次 {i // batch_size + 1}/{(len(python_files) - 1) // batch_size + 1}"
            )

            if self.analyze([str(f) for f in batch]):
                success_count += 1
            else:
                print(f"⚠️ 批次 {i // batch_size + 1} 处理失败")

        print(
            f"✅ 批量分析完成: {success_count}/{(len(python_files) - 1) // batch_size + 1} 批次成功"
        )
        return success_count > 0

    def generate_report(self, format_type: str = "html") -> bool:
        """生成综合报告"""
        print(f"📊 生成{format_type}格式报告...")

        report_data = {
            "timestamp": str(Path.cwd()),
            "toolkit_version": "2.0.0",
            "analysis_summary": {},
            "coverage_summary": {},
            "security_summary": {},
            "performance_summary": {},
        }

        try:
            # 收集分析报告
            analysis_dir = Path("smart_analysis_reports")
            if analysis_dir.exists():
                reports = list(analysis_dir.glob("*.md"))
                report_data["analysis_summary"]["total_reports"] = len(reports)
                report_data["analysis_summary"]["reports"] = [r.name for r in reports]

            # 保存报告
            report_path = Path("toolkit_comprehensive_report.json")
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

            print(f"✅ 报告生成完成: {report_path}")
            return True

        except Exception as e:
            print(f"❌ 报告生成失败: {e}")
            return False

    def health_check(self) -> bool:
        """健康检查"""
        print("🏥 执行工具包健康检查...")

        health_script = self.toolkit_root / "health_check.py"
        if health_script.exists():
            return self._run_script(health_script)
        else:
            print("⚠️ 健康检查脚本不存在")
            return False

    def create_parser(self) -> argparse.ArgumentParser:
        """创建命令行解析器"""
        parser = argparse.ArgumentParser(
            prog="ai-toolkit",
            description="AI Test Optimizer Toolkit - 专业级智能测试优化工具",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例用法:
  ai-toolkit analyze src/core/config.py              # 分析单个文件
  ai-toolkit analyze src/ --batch                   # 批量分析目录
  ai-toolkit optimize auto                         # 自动优化模式
  ai-toolkit coverage --threshold 80               # 检查覆盖率(80%阈值)
  ai-toolkit security                              # 安全扫描
  ai-toolkit performance                           # 性能测试
  ai-toolkit monitor status                        # 监控状态
  ai-toolkit report --format html                 # 生成HTML报告
            """,
        )

        parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
        parser.add_argument(
            "--version", action="version", version="AI Test Optimizer Toolkit 2.0.0"
        )

        subparsers = parser.add_subparsers(dest="command", help="可用命令")

        # analyze 命令
        analyze_parser = subparsers.add_parser("analyze", help="代码质量分析")
        analyze_parser.add_argument("paths", nargs="+", help="要分析的文件或目录路径")
        analyze_parser.add_argument("--batch", action="store_true", help="批量模式")

        # optimize 命令
        optimize_parser = subparsers.add_parser("optimize", help="智能测试优化")
        optimize_parser.add_argument(
            "mode",
            nargs="?",
            choices=["auto", "quick", "test", "perf"],
            default="auto",
            help="优化模式",
        )

        # coverage 命令
        coverage_parser = subparsers.add_parser("coverage", help="测试覆盖率检查")
        coverage_parser.add_argument("--threshold", type=int, help="覆盖率阈值(百分比)")

        # security 命令
        subparsers.add_parser("security", help="安全扫描")

        # performance 命令
        subparsers.add_parser("performance", help="性能回归测试")

        # monitor 命令
        monitor_parser = subparsers.add_parser("monitor", help="监控和分析")
        monitor_parser.add_argument(
            "action",
            nargs="?",
            choices=["status", "analyze"],
            default="status",
            help="监控操作",
        )

        # report 命令
        report_parser = subparsers.add_parser("report", help="生成报告")
        report_parser.add_argument(
            "--format",
            choices=["json", "html", "markdown"],
            default="html",
            help="报告格式",
        )

        # health 命令
        subparsers.add_parser("health", help="健康检查")

        return parser

    def run(self, args: List[str] = None) -> bool:
        """运行CLI"""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)

        self.verbose = parsed_args.verbose

        if not parsed_args.command:
            parser.print_help()
            return False

        # 执行命令
        if parsed_args.command == "analyze":
            if (
                parsed_args.batch
                and len(parsed_args.paths) == 1
                and Path(parsed_args.paths[0]).is_dir()
            ):
                return self.batch_analyze(parsed_args.paths[0])
            else:
                return self.analyze(parsed_args.paths)

        elif parsed_args.command == "optimize":
            return self.optimize(parsed_args.mode)

        elif parsed_args.command == "coverage":
            return self.coverage(parsed_args.threshold)

        elif parsed_args.command == "security":
            return self.security()

        elif parsed_args.command == "performance":
            return self.performance()

        elif parsed_args.command == "monitor":
            return self.monitor(parsed_args.action)

        elif parsed_args.command == "report":
            return self.generate_report(parsed_args.format)

        elif parsed_args.command == "health":
            return self.health_check()

        else:
            print(f"❌ 未知命令: {parsed_args.command}")
            return False


def main():
    """主入口函数"""
    try:
        cli = AIToolkitCLI()
        success = cli.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 未预期的错误: {e}")
        if "--verbose" in sys.argv:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
