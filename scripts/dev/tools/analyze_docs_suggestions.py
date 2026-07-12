#!/usr/bin/env python3
"""文档建议采纳情况分析工具

功能：
1. 分析文档建议日志
2. 统计未采纳建议
3. 生成采纳率报告
4. 识别常见问题模式

使用方法：
    python scripts/tools/analyze_docs_suggestions.py
    python scripts/tools/analyze_docs_suggestions.py --days 7
    python scripts/tools/analyze_docs_tools/analyze_docs_suggestions.py --author
"""

import argparse
import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List


class DocsSuggestionAnalyzer:
    """文档建议分析器"""

    def __init__(self, log_dir: str = "var/log/docs-audit"):
        self.log_dir = Path(log_dir)
        self.suggestions = defaultdict(list)
        self.file_issues = defaultdict(int)

    def load_logs(self, days: int = 30) -> None:
        """加载指定天数内的日志"""
        cutoff_date = datetime.now() - timedelta(days=days)

        if not self.log_dir.exists():
            print(f"⚠️  日志目录不存在: {self.log_dir}")
            return

        print(f"📂 加载日志文件（最近{days}天）...")

        log_files = sorted(
            self.log_dir.glob("placement-suggestions-*.log"),
            reverse=True,
        )

        loaded_count = 0
        for log_file in log_files:
            file_date = self._parse_date(log_file)
            if file_date and file_date >= cutoff_date:
                self._parse_log_file(log_file)
                loaded_count += 1

        print(f"  ✅ 加载了 {loaded_count} 个日志文件")

    def _parse_date(self, log_file: Path) -> datetime | None:
        """从文件名解析日期"""
        match = re.search(r"(\d{8})-(\d{6})-(\d{6})", log_file.stem)
        if match:
            try:
                return datetime.strptime(match.group(0), "%Y%m%d-%H%M%S")
            except ValueError:
                return None
        return None

    def _parse_log_file(self, log_file: Path) -> None:
        """解析单个日志文件"""
        try:
            with open(log_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    # 解析日志格式
                    # [2026-01-20 10:30:15] file | suggestion
                    match = re.match(r"\[([\d-]+\s+[\d:]+)\]\s+(.+?)\s*\|\s*(.+)", line)
                    if match:
                        timestamp_str = match.group(1)
                        file_suggestion = match.group(2)

                        # 分离文件和建议
                        parts = file_suggestion.split(" | ", 1)
                        if len(parts) >= 1:
                            file = parts[0].strip()
                            suggestion = parts[1].strip() if len(parts) > 1 else ""

                            # 提取关键信息
                            issue_type = self._classify_suggestion(suggestion)

                            self.suggestions[file].append(
                                {
                                    "timestamp": timestamp_str,
                                    "file": file,
                                    "suggestion": suggestion,
                                    "issue_type": issue_type,
                                    "log_file": log_file.name,
                                }
                            )
                            self.file_issues[file] += 1

        except Exception as e:
            print(f"  ⚠️  无法读取日志文件 {log_file}: {e}")

    def _classify_suggestion(self, suggestion: str) -> str:
        """分类建议类型"""
        suggestion_lower = suggestion.lower()

        if "移到" in suggestion or "mv" in suggestion:
            if "api" in suggestion_lower:
                return "位置-建议-API"
            if "架构" in suggestion_lower:
                return "位置-建议-架构"
            if "指南" in suggestion_lower:
                return "位置-建议-指南"
            if "报告" in suggestion_lower:
                return "位置-建议-报告"
            if "测试" in suggestion_lower:
                return "位置-建议-测试"
            if "运维" in suggestion_lower or "监控" in suggestion_lower:
                return "位置-建议-运维"
            return "位置-建议-其他"
        if "kebab-case" in suggestion or "重命名" in suggestion:
            return "命名-建议"
        if "删除" in suggestion or "临时文件" in suggestion:
            return "清理-建议"
        if "扁平化" in suggestion or "嵌套" in suggestion:
            return "结构-建议"
        return "其他-建议"

    def generate_report(self, output_path: str = None) -> None:
        """生成分析报告"""
        if not self.suggestions:
            print("📭 暂无建议日志记录")
            return

        # 统计信息
        total_suggestions = sum(len(v) for v in self.suggestions.values())
        unique_files = len(self.suggestions)

        print("\n" + "=" * 80)
        print("📊 文档建议采纳情况分析".center(80))
        print("=" * 80)
        print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"分析文件数: {unique_files}")
        print(f"总建议数: {total_suggestions}")
        print()

        # 按文件类型统计
        file_type_stats = defaultdict(int)
        for file in self.suggestions.keys():
            if file.startswith("./"):
                file_type_stats["根目录"] += 1
            elif file.startswith("docs/"):
                file_type_stats["docs目录"] += 1

        print("📂 文件位置分布:")
        for file_type, count in sorted(file_type_stats.items()):
            percentage = (count / unique_files * 100) if unique_files > 0 else 0
            print(f"  - {file_type}: {count} 个文件 ({percentage:.1f}%)")
        print()

        # 按问题类型统计
        issue_type_stats = defaultdict(int)
        for suggestions in self.suggestions.values():
            for suggestion in suggestions:
                issue_type_stats[suggestion["issue_type"]] += 1

        print("🏷️ 建议类型分布:")
        for issue_type, count in sorted(issue_type_stats.items(), key=lambda x: -x[1]):
            print(f"  - {issue_type}: {count} 条")
        print()

        # 未采纳建议最多的文件（可能是顽固问题）
        print("🔝 建议未采纳次数TOP10:")
        sorted_files = sorted(
            self.file_issues.items(),
            key=lambda x: -x[1],
        )[:10]
        for i, (file, count) in enumerate(sorted_files, 1):
            print(f"  {i}. {file}: {count} 次未采纳")

        # 持久化文件（跨多次提交）
        persistent_files = [(file, count) for file, count in self.file_issues.items() if count >= 3]
        if persistent_files:
            print("\n🔄 持久问题文件（≥3次未采纳）:")
            for file, count in sorted(persistent_files, key=lambda x: -x[1]):
                print(f"  - {file}: {count} 次")

        # 生成文本报告
        if output_path:
            self._save_report(output_path)

    def _save_report(self, output_path: str) -> None:
        """保存报告到文件"""
        report_path = Path(output_path)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# 文档建议采纳情况分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## 📊 总体统计\n\n")
            total_suggestions = sum(len(v) for v in self.suggestions.values())
            unique_files = len(self.suggestions)

            f.write(f"- **分析文件数**: {unique_files}\n")
            f.write(f"- **总建议数**: {total_suggestions}\n")
            f.write(f"- **日志目录**: {self.log_dir}\n\n")

            # 按问题类型
            f.write("## 🏷️ 建议类型统计\n\n")
            issue_type_stats = defaultdict(int)
            for suggestions in self.suggestions.values():
                for suggestion in suggestions:
                    issue_type_stats[suggestion["issue_type"]] += 1

            for issue_type, count in sorted(issue_type_stats.items()):
                percentage = (count / total_suggestions * 100) if total_suggestions > 0 else 0
                f.write(f"- **{issue_type}**: {count} ({percentage:.1f}%)\n")

            # 未采纳建议TOP10
            f.write("\n## 🔝 未采纳建议TOP10\n\n")
            sorted_files = sorted(
                self.file_issues.items(),
                key=lambda x: -x[1],
            )[:10]
            for i, (file, count) in enumerate(sorted_files, 1):
                f.write(f"{i}. {file}: {count} 次\n")

        print(f"✅ 报告已保存到: {report_path}")

    def suggest_fixes(self) -> List[str]:
        """生成改进建议"""
        suggestions = []

        # 分析未采纳建议最多的文件
        persistent_files = [(file, count) for file, count in self.file_issues.items() if count >= 3]

        if persistent_files:
            suggestions.append("🔧 重点关注以下文件（多次未采纳建议）:")
            for file, count in persistent_files[:5]:
                suggestions.append(f"   - {file}: {count} 次")

        # 分析常见问题模式
        if self.suggestions:
            issue_type_stats = defaultdict(int)
            for suggestions in self.suggestions.values():
                for suggestion in suggestions:
                    issue_type_stats[suggestion["issue_type"]] += 1

            if issue_type_stats:
                top_issue = max(issue_type_stats.items(), key=lambda x: x[1])
                suggestions.append(f"\n🎯 最常见问题: {top_issue[0]} ({top_issue[1]}次)")

        return suggestions


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="文档建议采纳情况分析工具",
    )
    parser.add_argument("--days", type=int, default=30, help="分析最近N天的日志（默认30天）")
    parser.add_argument("--output", help="保存报告文件路径")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    # 创建分析器
    analyzer = DocsSuggestionAnalyzer()

    # 加载日志
    analyzer.load_logs(args.days)

    # 生成报告
    analyzer.generate_report(args.output)

    # 生成改进建议（如果有）
    if args.verbose:
        suggestions = analyzer.suggest_fixes()
        if suggestions:
            print("\n💡 改进建议:")
            for suggestion in suggestions:
                print(suggestion)


if __name__ == "__main__":
    main()
