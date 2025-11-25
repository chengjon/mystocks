#!/usr/bin/env python3
"""
数据库安全检查脚本
检查代码中是否存在硬编码的敏感信息
"""
import os
import re
import glob
from typing import List, Dict, Tuple, Optional


class SecurityChecker:
    """数据库安全检查器"""

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.patterns = {
            "ip_address": r"\b(?!127\.0\.0\.1)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",  # 排除localhost IP
            "host_hardcode": r'host\s*=\s*[\'"][^\'"\s]+[\'"]',
            "user_hardcode": r'user\s*=\s*[\'"][^\'"\s]+[\'"]',
            "password_hardcode": r'password\s*=\s*[\'"][^\'"\s]+[\'"]',
            "port_hardcode": r"port\s*=\s*\d+",
            "connection_string": r'mysql\+pymysql://[^\'"\s]+',
            # 移除dsn_string模式，因为它会误报正常的f-string
        }

        # 排除的文件和目录
        self.exclude_patterns = [
            "*.pyc",
            "__pycache__",
            ".git",
            ".env",  # .env文件本身应该包含敏感信息
            "venv",
            "env",
            ".venv",
        ]

        # 允许的安全模式（这些不算安全漏洞）
        self.safe_patterns = [
            r"os\.getenv\(",  # 环境变量获取
            r"config\[",  # 从配置字典获取
            r"\.get\(",  # 字典get方法
            r"#.*",  # 注释
            r"localhost",  # localhost通常是安全的
            r"127\.0\.0\.1",  # 本地IP
            r'f".*{.*}.*"',  # f-string格式化字符串（使用变量）
            r"f'.*{.*}.*'",  # f-string格式化字符串（使用变量）
            r'r["\'].*["\']',  # 正则表达式字符串
            r"\b\d+\.\d+\.\d+\.\d+\b.*version",  # 版本号中IP格式
            r"https?://.*\d+\.\d+\.\d+\.\d+",  # URL中的版本号
            r"taosdata\.com.*\d+\.\d+\.\d+\.\d+",  # TDengine下载URL
        ]

    def is_excluded_file(self, file_path: str) -> bool:
        """检查文件是否应该被排除"""
        for pattern in self.exclude_patterns:
            if pattern in file_path:
                return True
        return False

    def is_safe_line(self, line: str) -> bool:
        """检查是否是安全的代码行"""
        for pattern in self.safe_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False

    def scan_file(self, file_path: str) -> List[Dict]:
        """扫描单个文件"""
        issues = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                # 跳过空行和注释
                if not line or line.startswith("#"):
                    continue

                # 检查是否是安全的代码行
                if self.is_safe_line(line):
                    continue

                # 检查各种敏感信息模式
                for pattern_name, pattern in self.patterns.items():
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        # 额外检查：如果是从环境变量获取，则跳过
                        if "getenv" in line or "os.environ" in line:
                            continue

                        issues.append(
                            {
                                "file": file_path,
                                "line": line_num,
                                "content": line,
                                "pattern": pattern_name,
                                "match": match.group(),
                                "type": (
                                    "warning"
                                    if pattern_name == "ip_address"
                                    else "error"
                                ),
                            }
                        )

        except Exception as e:
            print(f"Error scanning {file_path}: {e}")

        return issues

    def scan_directory(self, directory: Optional[str] = None) -> List[Dict]:
        """扫描目录中的所有Python文件"""
        if directory is None:
            directory = self.project_root

        all_issues = []

        # 查找所有Python文件
        python_files = []
        for root, dirs, files in os.walk(directory):
            # 排除特定目录
            dirs[:] = [
                d
                for d in dirs
                if not any(pattern in d for pattern in self.exclude_patterns)
            ]

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    if not self.is_excluded_file(file_path):
                        python_files.append(file_path)

        # 扫描每个文件
        for file_path in python_files:
            issues = self.scan_file(file_path)
            all_issues.extend(issues)

        return all_issues

    def generate_report(self, issues: List[Dict]) -> str:
        """生成安全检查报告"""
        if not issues:
            return "✅ 恭喜！未发现硬编码的敏感信息。"

        report = ["🔍 数据库安全检查报告", "=" * 50]

        # 按严重程度分组
        errors = [issue for issue in issues if issue["type"] == "error"]
        warnings = [issue for issue in issues if issue["type"] == "warning"]

        if errors:
            report.append(f"\n❌ 严重问题 ({len(errors)} 个)：")
            for issue in errors:
                report.append(f"  📁 {issue['file']}:{issue['line']}")
                report.append(f"     问题: {issue['pattern']} - {issue['match']}")
                report.append(f"     代码: {issue['content']}")
                report.append("")

        if warnings:
            report.append(f"\n⚠️  警告 ({len(warnings)} 个)：")
            for issue in warnings:
                report.append(f"  📁 {issue['file']}:{issue['line']}")
                report.append(f"     可能问题: {issue['pattern']} - {issue['match']}")
                report.append(f"     代码: {issue['content']}")
                report.append("")

        report.append("\n🛠️  修复建议：")
        report.append("1. 将所有敏感信息移至 .env 文件")
        report.append("2. 使用 os.getenv() 读取环境变量")
        report.append("3. 不要在代码中硬编码IP地址、用户名、密码")
        report.append("4. 确保 .env 文件已添加到 .gitignore")

        return "\n".join(report)


def main():
    """主函数"""
    # 获取项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)  # 上一级目录

    print("🔒 开始数据库安全检查...")
    print(f"📂 扫描目录: {project_root}")

    # 创建检查器并扫描
    checker = SecurityChecker(project_root)
    issues = checker.scan_directory()

    # 生成并显示报告
    report = checker.generate_report(issues)
    print(report)

    # 保存报告到文件
    report_file = os.path.join(current_dir, "security_check_report.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n📋 报告已保存到: {report_file}")

    # 返回退出码
    error_count = len([i for i in issues if i["type"] == "error"])
    return error_count


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
