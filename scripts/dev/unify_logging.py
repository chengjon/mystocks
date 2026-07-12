#!/usr/bin/env python3
"""日志系统统一化脚本

将项目中的print()语句替换为logging调用
建立统一的日志标准和配置
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional


class LoggingUnifier:
    """日志统一化工具"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.src_dir = self.project_root / "src"
        self.stats = {
            "files_processed": 0,
            "print_statements_found": 0,
            "print_statements_replaced": 0,
            "files_with_logging": 0,
            "issues_found": 0,
        }

    def analyze_print_usage(self) -> Dict[str, any]:
        """分析print语句使用情况"""
        print("🔍 分析项目中的print语句使用情况...")

        print_patterns = [
            r"print\([^)]*\)",  # 基本print语句
            r'print\s*\([^)]*f[\'"][^\'"]*[\'"]',  # f-string print
        ]

        analysis = {
            "total_prints": 0,
            "by_file": {},
            "by_directory": {},
            "common_patterns": {},
            "problematic_cases": [],
        }

        # 遍历所有Python文件
        for py_file in self.src_dir.rglob("*.py"):
            if py_file.is_file() and not any(skip in str(py_file) for skip in ["__pycache__", ".pytest_cache"]):
                try:
                    with open(py_file, encoding="utf-8") as f:
                        content = f.read()

                    file_prints = 0
                    file_issues = []

                    # 查找所有print语句
                    lines = content.split("\n")
                    for i, line in enumerate(lines, 1):
                        for pattern in print_patterns:
                            matches = re.finditer(pattern, line)
                            for match in matches:
                                file_prints += 1

                                # 分析问题
                                self._analyze_print_statement(
                                    line,
                                    i,
                                    py_file,
                                    file_issues,
                                )

                    if file_prints > 0:
                        analysis["by_file"][str(py_file)] = file_prints
                        analysis["total_prints"] += file_prints

                        # 按目录统计
                        parent_dir = py_file.parent.name
                        analysis["by_directory"][parent_dir] = analysis["by_directory"].get(parent_dir, 0) + file_prints

                        if file_issues:
                            analysis["problematic_cases"].extend(file_issues)

                except Exception as e:
                    print(f"⚠️  处理文件失败 {py_file}: {e}")

        return analysis

    def _analyze_print_statement(
        self,
        line: str,
        line_num: int,
        file_path: Path,
        issues: List[str],
    ):
        """分析单个print语句的问题"""
        # 检查调试相关print
        if any(debug_word in line.lower() for debug_word in ["debug", "测试", "test", "暂时", "temp"]):
            issues.append(f"{file_path}:{line_num} - 调试print语句")

        # 检查敏感信息
        if any(sensitive_word in line.lower() for sensitive_word in ["password", "secret", "key", "token"]):
            issues.append(f"{file_path}:{line_num} - 可能包含敏感信息的print")

        # 检查重复的print模式
        if 'print("="*50)' in line or 'print("-"*50)' in line:
            issues.append(f"{file_path}:{line_num} - 装饰性print语句")

    def generate_logging_import(self) -> str:
        """生成logging导入语句"""
        return """# 统一日志配置
import logging
from typing import Optional

# 获取或创建logger
logger = logging.getLogger(__name__)

# 确保日志配置已设置
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
"""

    def replace_print_with_logging(
        self,
        file_path: Path,
        dry_run: bool = False,
    ) -> bool:
        """将print语句替换为logging调用"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content
            modified = False

            # 检查是否已有logging导入
            has_logging_import = "import logging" in content

            # 添加logging导入（如果需要）
            if not has_logging_import and "print(" in content:
                # 在文件开头添加logging导入
                lines = content.split("\n")
                import_index = 0

                # 找到合适的位置插入import
                for i, line in enumerate(lines):
                    if line.startswith("import ") or line.startswith("from "):
                        import_index = i + 1
                    elif line.startswith("#") and i == 0:
                        import_index = 1
                        break

                lines.insert(import_index, self.generate_logging_import())
                content = "\n".join(lines)
                modified = True
                has_logging_import = True

            if "print(" not in content:
                return False

            # 替换print语句
            patterns_replacements = [
                # 替换简单的print语句
                (r'print\("([^"]+)"\)', r'logger.info(r"\1")'),
                (r"print\('([^']+)'\)", r'logger.info(r"\1")'),
                # 替换f-string print
                (r'print\(f"([^"]+)"\)', r'logger.info(f"\1")'),
                (r"print\(f'([^']+)'\)", r'logger.info(f"\1")'),
                # 替换带参数的print
                (r"print\(([^f][^)]+)\)", r"logger.info(str(\1))"),
            ]

            for pattern, replacement in patterns_replacements:
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    content = new_content
                    modified = True

            # 检查日志级别
            content = self._adjust_log_levels(content)

            if modified and not dry_run:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                print(f"✅ 更新文件: {file_path}")

            self.stats["files_processed"] += 1
            if modified:
                self.stats["print_statements_replaced"] += original_content.count(
                    "print(",
                )
                self.stats["files_with_logging"] += 1

            return modified

        except Exception as e:
            print(f"❌ 处理文件失败 {file_path}: {e}")
            return False

    def _adjust_log_levels(self, content: str) -> str:
        """调整日志级别"""
        # 根据内容调整日志级别
        level_adjustments = [
            # 错误信息
            (
                r"logger\.info\((.*(?:error|错误|失败|异常|exception|错误).*?)\)",
                r"logger.error(\1)",
            ),
            (r"logger\.info\((.*(?:warning|警告|warn).*?)\)", r"logger.warning(\1)"),
            # 调试信息
            (
                r"logger\.info\((.*(?:debug|调试|测试|test|debug).*?)\)",
                r"logger.debug(\1)",
            ),
            # 成功信息
            (
                r"logger\.info\((.*(?:✓|✅|success|成功|完成|complete).*?)\)",
                r"logger.info(\1)",
            ),
            # 进度信息保持info
        ]

        for pattern, replacement in level_adjustments:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

        return content

    def create_logging_config(self):
        """创建统一的日志配置文件"""
        config_file = self.project_root / "src" / "utils" / "logging_config.py"

        config_content = '''"""
MyStocks 统一日志配置

提供统一的日志配置和管理
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""

    # 颜色代码
    COLORS = {
        'DEBUG': '\\033[36m',    # 青色
        'INFO': '\\033[32m',     # 绿色
        'WARNING': '\\033[33m',  # 黄色
        'ERROR': '\\033[31m',    # 红色
        'CRITICAL': '\\033[35m', # 紫色
        'RESET': '\\033[0m'      # 重置
    }

    def format(self, record):
        # 添加颜色
        if hasattr(record, 'levelname'):
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"

        return super().format(record)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    use_colors: bool = True
) -> None:
    """
    设置项目日志配置

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径 (可选)
        use_colors: 是否使用彩色输出
    """

    # 根环境变量
    log_level = os.getenv('LOG_LEVEL', level)

    # 创建根logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # 清除现有handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 控制台handler
    console_handler = logging.StreamHandler(sys.stdout)

    # 格式化器
    if use_colors and sys.stdout.isatty():
        formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(console_handler)

    # 文件handler (如果指定)
    if log_file:
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    获取logger实例

    Args:
        name: logger名称，通常使用 __name__

    Returns:
        配置好的logger实例
    """
    return logging.getLogger(name)


# 默认配置
if not logging.getLogger().handlers:
    setup_logging()

# 导出的便捷函数
def log_info(message: str, logger_name: Optional[str] = None):
    """记录INFO级别日志"""
    if logger_name:
        logging.getLogger(logger_name).info(message)
    else:
        logging.getLogger(__info__).info(message)


def log_error(message: str, logger_name: Optional[str] = None):
    """记录ERROR级别日志"""
    if logger_name:
        logging.getLogger(logger_name).error(message)
    else:
        logging.getLogger(__info__).error(message)


def log_warning(message: str, logger_name: Optional[str] = None):
    """记录WARNING级别日志"""
    if logger_name:
        logging.getLogger(logger_name).warning(message)
    else:
        logging.getLogger(__info__).warning(message)


def log_debug(message: str, logger_name: Optional[str] = None):
    """记录DEBUG级别日志"""
    if logger_name:
        logging.getLogger(logger_name).debug(message)
    else:
        logging.getLogger(__info__).debug(message)
'''

        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(config_content)

        print(f"✅ 创建日志配置文件: {config_file}")

    def run_unification(self, dry_run: bool = False, target_file: Optional[str] = None):
        """运行日志统一化"""
        print("🚀 开始日志系统统一化...")

        # 创建日志配置
        self.create_logging_config()

        if target_file:
            # 处理单个文件
            file_path = Path(target_file)
            if file_path.exists():
                self.replace_print_with_logging(file_path, dry_run)
            else:
                print(f"❌ 文件不存在: {target_file}")
        else:
            # 处理所有文件
            print("📁 处理所有Python文件...")

            for py_file in self.src_dir.rglob("*.py"):
                if py_file.is_file() and not any(skip in str(py_file) for skip in ["__pycache__", ".pytest_cache"]):
                    try:
                        self.replace_print_with_logging(py_file, dry_run)
                    except Exception as e:
                        print(f"⚠️  处理文件失败 {py_file}: {e}")
                        self.stats["issues_found"] += 1

        # 输出统计信息
        self._print_stats(dry_run)

    def _print_stats(self, dry_run: bool):
        """打印统计信息"""
        mode = "模拟" if dry_run else "实际"
        print(f"\n📊 日志统一化统计 ({mode}模式):")
        print(f"  处理文件数: {self.stats['files_processed']}")
        print(f"  替换print语句: {self.stats['print_statements_replaced']}")
        print(f"  添加日志配置的文件: {self.stats['files_with_logging']}")
        print(f"  发现问题数: {self.stats['issues_found']}")

        if not dry_run:
            print("\n✅ 日志统一化完成!")
            print("\n📋 后续建议:")
            print("1. 检查替换后的日志级别是否合适")
            print("2. 运行测试确保功能正常")
            print("3. 提交更改前运行代码质量检查")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="MyStocks 日志系统统一化工具")
    parser.add_argument(
        "--project-root",
        default=".",
        help="项目根目录路径 (默认: 当前目录)",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="模拟运行，不修改文件",
    )
    parser.add_argument("--file", "-f", help="只处理指定文件")
    parser.add_argument("--analyze", "-a", action="store_true", help="只分析，不修改")

    args = parser.parse_args()

    try:
        unifier = LoggingUnifier(args.project_root)

        if args.analyze:
            # 只分析
            analysis = unifier.analyze_print_usage()
            print("\n📊 分析结果:")
            print(f"  总print语句: {analysis['total_prints']}")
            print(f"  涉及文件数: {len(analysis['by_file'])}")

            print("\n📁 按目录分布:")
            for dir_name, count in sorted(
                analysis["by_directory"].items(),
                key=lambda x: x[1],
                reverse=True,
            ):
                print(f"  {dir_name}: {count}")

            if analysis["problematic_cases"]:
                print("\n⚠️  发现的问题:")
                for issue in analysis["problematic_cases"][:10]:  # 只显示前10个
                    print(f"  {issue}")
        else:
            # 执行统一化
            unifier.run_unification(args.dry_run, args.file)

        return 0

    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
