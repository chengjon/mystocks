#!/usr/bin/env python3
"""# 功能：验证.gitignore配置是否正确排除应忽略的文件
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：1.0.0
# 依赖：无外部依赖
# 注意事项：
#   - 检查git status中不应出现的文件类型
#   - 验证.env.example等例外文件可见
#   - 提供清理建议
# 版权：MyStocks Project © 2025
"""

import re
import subprocess
from pathlib import Path
from typing import List


class GitIgnoreValidator:
    """Git忽略规则验证器"""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)

        # 应该被忽略的文件模式
        self.should_be_ignored = {
            "__pycache__": r"__pycache__/",
            "*.pyc": r".*\.pyc$",
            "*.log": r".*\.log$",
            ".env": r"\.env$",
            "*.swp": r".*\.swp$",
            "*.swo": r".*\.swo$",
            "node_modules": r"node_modules/",
            ".idea": r"\.idea/",
            ".vscode": r"\.vscode/",
            ".DS_Store": r"\.DS_Store$",
            "Thumbs.db": r"Thumbs\.db$",
        }

        # 应该可见的文件（排除规则）
        self.should_be_visible = [
            ".env.example",
            "temp/README.md",
            "data/backups/.gitkeep",
        ]

        self.issues = []
        self.warnings = []
        self.successes = []

    def run_git_command(self, args: List[str]) -> str:
        """执行git命令"""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return ""

    def get_untracked_files(self) -> List[str]:
        """获取未跟踪的文件列表"""
        output = self.run_git_command(["status", "--short", "--untracked-files=all"])
        untracked = []

        for line in output.split("\n"):
            if line.startswith("??"):
                file_path = line[3:].strip()
                untracked.append(file_path)

        return untracked

    def check_ignored_patterns(self):
        """检查应该被忽略的文件模式"""
        untracked = self.get_untracked_files()

        for pattern_name, pattern_regex in self.should_be_ignored.items():
            found_violations = []

            for file_path in untracked:
                if re.search(pattern_regex, file_path):
                    found_violations.append(file_path)

            if found_violations:
                self.issues.append(
                    {
                        "type": "NOT_IGNORED",
                        "pattern": pattern_name,
                        "files": found_violations[:5],  # 只显示前5个
                        "total": len(found_violations),
                    },
                )
            else:
                self.successes.append(f"✅ {pattern_name} - 已正确忽略")

    def check_exception_files(self):
        """检查排除规则文件是否可见"""
        for file_path in self.should_be_visible:
            full_path = self.root_dir / file_path

            if not full_path.exists():
                self.warnings.append(f"⚠️  {file_path} - 文件不存在（可选）")
                continue

            # 检查文件是否被忽略
            result = self.run_git_command(["check-ignore", file_path])

            if result.strip():
                self.issues.append(
                    {
                        "type": "WRONGLY_IGNORED",
                        "file": file_path,
                        "message": "应该可见但被忽略",
                    },
                )
            else:
                self.successes.append(f"✅ {file_path} - 正确可见")

    def check_gitignore_exists(self) -> bool:
        """检查.gitignore文件是否存在"""
        gitignore_files = [
            self.root_dir / ".gitignore",
            self.root_dir / "web" / "frontend" / ".gitignore",
        ]

        all_exist = True
        for gitignore_path in gitignore_files:
            if gitignore_path.exists():
                self.successes.append(
                    f"✅ {gitignore_path.relative_to(self.root_dir)} - 存在",
                )
            else:
                self.issues.append(
                    {
                        "type": "MISSING_GITIGNORE",
                        "file": str(gitignore_path.relative_to(self.root_dir)),
                        "message": ".gitignore文件缺失",
                    },
                )
                all_exist = False

        return all_exist

    def generate_cleanup_commands(self) -> List[str]:
        """生成清理命令"""
        commands = []

        for issue in self.issues:
            if issue["type"] == "NOT_IGNORED":
                pattern = issue["pattern"]

                if pattern == "__pycache__":
                    commands.append("# 清理Python缓存")
                    commands.append(
                        "find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null",
                    )
                    commands.append("find . -type f -name '*.pyc' -delete")
                elif pattern == "*.log":
                    commands.append("# 清理日志文件")
                    commands.append("find . -type f -name '*.log' -delete")
                elif pattern == "node_modules":
                    commands.append(
                        "# 清理Node.js依赖（谨慎使用，可能需要重新npm install）",
                    )
                    commands.append(
                        "# find . -type d -name 'node_modules' -exec rm -rf {} +",
                    )

        return commands

    def generate_report(self) -> str:
        """生成验证报告"""
        report = []
        report.append("\n" + "=" * 80)
        report.append(".gitignore配置验证报告")
        report.append("=" * 80 + "\n")

        # 检查.gitignore文件是否存在
        self.check_gitignore_exists()

        # 检查应被忽略的文件
        self.check_ignored_patterns()

        # 检查排除规则文件
        self.check_exception_files()

        # 统计
        report.append("📊 验证统计:")
        report.append(f"  - ✅ 通过检查: {len(self.successes)} 项")
        report.append(f"  - ❌ 发现问题: {len(self.issues)} 项")
        report.append(f"  - ⚠️  警告: {len(self.warnings)} 项\n")

        # 成功项（只显示前10个）
        if self.successes:
            report.append("✅ 通过的检查:")
            for success in self.successes[:10]:
                report.append(f"  {success}")
            if len(self.successes) > 10:
                report.append(f"  ... 还有 {len(self.successes) - 10} 项通过")
            report.append("")

        # 问题详情
        if self.issues:
            report.append("❌ 发现的问题:")
            for i, issue in enumerate(self.issues, 1):
                if issue["type"] == "NOT_IGNORED":
                    report.append(f"\n  {i}. {issue['pattern']} 文件未被正确忽略")
                    report.append(f"     发现 {issue['total']} 个文件 (显示前5个):")
                    for file in issue["files"]:
                        report.append(f"       - {file}")
                elif issue["type"] == "WRONGLY_IGNORED" or issue["type"] == "MISSING_GITIGNORE":
                    report.append(f"\n  {i}. {issue['file']} - {issue['message']}")
            report.append("")

        # 警告
        if self.warnings:
            report.append("⚠️  警告:")
            for warning in self.warnings:
                report.append(f"  {warning}")
            report.append("")

        # 清理建议
        cleanup_commands = self.generate_cleanup_commands()
        if cleanup_commands:
            report.append("🧹 清理建议:")
            for cmd in cleanup_commands:
                report.append(f"  {cmd}")
            report.append("")

        # 验收标准
        report.append("=" * 80)
        report.append("验收标准检查 (SC-005)")
        report.append("=" * 80)

        checks = [
            (
                "git status不显示__pycache__目录",
                not any(i["type"] == "NOT_IGNORED" and i["pattern"] == "__pycache__" for i in self.issues),
            ),
            (
                "git status不显示*.pyc文件",
                not any(i["type"] == "NOT_IGNORED" and i["pattern"] == "*.pyc" for i in self.issues),
            ),
            (
                "git status不显示*.log文件",
                not any(i["type"] == "NOT_IGNORED" and i["pattern"] == "*.log" for i in self.issues),
            ),
            (
                "git status不显示.env文件",
                not any(i["type"] == "NOT_IGNORED" and i["pattern"] == ".env" for i in self.issues),
            ),
            (
                ".gitignore文件存在",
                not any(i["type"] == "MISSING_GITIGNORE" for i in self.issues),
            ),
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
            report.append("🎉 所有验收标准通过！.gitignore配置正确。")
        else:
            report.append("⚠️  部分验收标准未通过，请执行上述清理建议或更新.gitignore。")

        report.append("=" * 80 + "\n")

        return "\n".join(report)


def main():
    """主函数"""
    print("\n启动.gitignore配置验证...\n")

    validator = GitIgnoreValidator()
    report = validator.generate_report()

    print(report)

    # 返回退出码
    if len(validator.issues) > 0:
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
