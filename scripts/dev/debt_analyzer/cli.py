"""技术负债分析器 - CLI 入口"""

import logging


logger = logging.getLogger(__name__)


async def main_async():  # Renamed to main_async
    """主函数"""
    analyzer = TechnicalDebtAnalyzer()
    results = await analyzer.analyze_all()  # Await the async analysis

    # 生成报告
    report_file = "/opt/claude/mystocks_spec/technical_debt_assessment_report.md"

    async with aiofiles.open(
        report_file,
        "w",
        encoding="utf-8",
    ) as f:  # Use aiofiles for writing
        await f.write("# MyStocks 技术负债评估报告\n\n")
        await f.write(f"**评估日期**: {results['analysis_summary']['analysis_date']}\n")
        await f.write(f"**技术负债评分**: {results['technical_debt_score']}/100\n\n")

        # 总体概况
        await f.write("## 📊 总体概况\n\n")
        summary = results["analysis_summary"]
        await f.write(f"- **问题总数**: {summary['total_issues']}\n")
        await f.write(f"- **代码文件数**: {summary['project_stats']['python_files']}\n")
        await f.write(
            f"- **总代码行数**: {summary['project_stats']['total_lines']:,}\n",
        )
        await f.write(
            f"- **Python文件数**: {summary['project_stats']['python_files']}\n\n",
        )

        # 按类别统计
        await f.write("## 📋 问题分类统计\n\n")
        for category, count in summary["categories"].items():
            severity_info = []
            for issue in results["detailed_issues"][category]:
                severity = issue.get("severity", "unknown")
                # Avoid re-calculating severity counts, get them from summary if available
                # or process the detailed_issues list once per category
                if severity not in [s[0] for s in severity_info]:
                    severity_count = sum(
                        1 for i in results["detailed_issues"][category] if i.get("severity") == severity
                    )
                    severity_info.append((severity, severity_count))

            await f.write(f"### {category.replace('_', ' ').title()}\n")
            await f.write(f"- 总数: {count}\n")
            for severity, count in severity_info:
                await f.write(f"- {severity}: {count}\n")
            await f.write("\n")

        # 优先行动
        await f.write("## 🚨 优先处理行动\n\n")
        for i, action in enumerate(results["priority_actions"][:5], 1):
            await f.write(
                f"{i}. **{action['priority'].upper()}** - {action['description']}\n",
            )
            await f.write(f"   - 文件: `{action['file']}`\n")
            await f.write(f"   - 类别: {action['category']}\n\n")

        # 优化建议
        await f.write("## 💡 优化建议\n\n")
        for rec in results["recommendations"]:
            await f.write(f"### {rec['title']} ({rec['priority'].upper()})\n")
            await f.write(f"{rec['description']}\n\n")
            await f.write("**行动建议**:\n")
            for action in rec["actions"]:
                await f.write(f"- {action}\n")
            await f.write("\n")

        # 详细问题列表
        await f.write("## 📝 详细问题列表\n\n")
        for category, issues in results["detailed_issues"].items():
            if issues:
                await f.write(f"### {category.replace('_', ' ').title()}\n\n")
                for issue in issues[:20]:  # 只显示前20个问题
                    await f.write(f"- **文件**: `{issue.get('file', 'N/A')}`\n")
                    await f.write(
                        f"  - **问题**: {issue.get('issue', issue.get('category', 'unknown'))}\n",
                    )
                    await f.write(
                        f"  - **严重程度**: {issue.get('severity', 'unknown')}\n\n",
                    )

                if len(issues) > 20:
                    await f.write(f"*... 还有{len(issues) - 20}个类似问题*\n\n")

        await f.write("---\n")
        await f.write("*本报告由iFlow CLI自动生成 - 技术负债分析器 v1.0*\n")

    logger.info(f"技术负债评估报告已生成: {report_file}")

    # 输出到控制台
    print(f"\n{'=' * 60}")
    print("🔍 MyStocks 技术负债评估报告")
    print(f"{'=' * 60}")
    print(f"📊 技术负债评分: {results['technical_debt_score']}/100")
    print(f"📋 问题总数: {results['analysis_summary']['total_issues']}")
    print(
        f"🐍 Python文件: {results['analysis_summary']['project_stats']['python_files']}",
    )
    print(
        f"📄 总代码行: {results['analysis_summary']['project_stats']['total_lines']:,}",
    )
    print(f"{'=' * 60}")
    print(f"📝 详细报告: {report_file}")
    print(f"{'=' * 60}\n")

    return results


def main():
    """主函数"""
    analyzer = TechnicalDebtAnalyzer()
    results = analyzer.analyze_all()

    # 生成报告
    report_file = "/opt/claude/mystocks_spec/technical_debt_assessment_report.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# MyStocks 技术负债评估报告\n\n")
        f.write(f"**评估日期**: {results['analysis_summary']['analysis_date']}\n")
        f.write(f"**技术负债评分**: {results['technical_debt_score']}/100\n\n")

        # 总体概况
        f.write("## 📊 总体概况\n\n")
        summary = results["analysis_summary"]
        f.write(f"- **问题总数**: {summary['total_issues']}\n")
        f.write(f"- **代码文件数**: {summary['project_stats']['python_files']}\n")
        f.write(f"- **总代码行数**: {summary['project_stats']['total_lines']:,}\n")
        f.write(f"- **Python文件数**: {summary['project_stats']['python_files']}\n\n")

        # 按类别统计
        f.write("## 📋 问题分类统计\n\n")
        for category, count in summary["categories"].items():
            severity_info = []
            for issue in results["detailed_issues"][category]:
                severity = issue.get("severity", "unknown")
                if severity not in [s[0] for s in severity_info]:
                    severity_count = sum(
                        1 for i in results["detailed_issues"][category] if i.get("severity") == severity
                    )
                    severity_info.append((severity, severity_count))

            f.write(f"### {category.replace('_', ' ').title()}\n")
            f.write(f"- 总数: {count}\n")
            for severity, count in severity_info:
                f.write(f"- {severity}: {count}\n")
            f.write("\n")

        # 优先行动
        f.write("## 🚨 优先处理行动\n\n")
        for i, action in enumerate(results["priority_actions"][:5], 1):
            f.write(
                f"{i}. **{action['priority'].upper()}** - {action['description']}\n",
            )
            f.write(f"   - 文件: `{action['file']}`\n")
            f.write(f"   - 类别: {action['category']}\n\n")

        # 优化建议
        f.write("## 💡 优化建议\n\n")
        for rec in results["recommendations"]:
            f.write(f"### {rec['title']} ({rec['priority'].upper()})\n")
            f.write(f"{rec['description']}\n\n")
            f.write("**行动建议**:\n")
            for action in rec["actions"]:
                f.write(f"- {action}\n")
            f.write("\n")

        # 详细问题列表
        f.write("## 📝 详细问题列表\n\n")
        for category, issues in results["detailed_issues"].items():
            if issues:
                f.write(f"### {category.replace('_', ' ').title()}\n\n")
                for issue in issues[:20]:  # 只显示前20个问题
                    f.write(f"- **文件**: `{issue.get('file', 'N/A')}`\n")
                    f.write(
                        f"  - **问题**: {issue.get('issue', issue.get('category', 'unknown'))}\n",
                    )
                    f.write(f"  - **严重程度**: {issue.get('severity', 'unknown')}\n\n")

                if len(issues) > 20:
                    f.write(f"*... 还有{len(issues) - 20}个类似问题*\n\n")

        f.write("---\n")
        f.write("*本报告由iFlow CLI自动生成 - 技术负债分析器 v1.0*\n")

    logger.info(f"技术负债评估报告已生成: {report_file}")

    # 输出到控制台
    print(f"\n{'=' * 60}")
    print("🔍 MyStocks 技术负债评估报告")
    print(f"{'=' * 60}")
    print(f"📊 技术负债评分: {results['technical_debt_score']}/100")
    print(f"📋 问题总数: {results['analysis_summary']['total_issues']}")
    print(
        f"🐍 Python文件: {results['analysis_summary']['project_stats']['python_files']}",
    )
    print(
        f"📄 总代码行: {results['analysis_summary']['project_stats']['total_lines']:,}",
    )
    print(f"{'=' * 60}")
    print(f"📝 详细报告: {report_file}")
    print(f"{'=' * 60}\n")

    return results


if __name__ == "__main__":
    main()
