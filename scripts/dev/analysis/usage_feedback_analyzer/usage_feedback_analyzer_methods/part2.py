#!/usr/bin/env python3
"""AI测试优化器使用反馈分析器
收集、分析和报告AI测试优化器的使用情况，为工具改进提供数据支持

功能:
1. 使用数据收集和分析
2. 用户反馈趋势分析
3. 工具效果评估
4. 改进建议生成
5. 使用模式识别

作者: MyStocks AI Team
版本: 1.0
日期: 2025-01-22
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt


# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class UsageFeedbackAnalyzerGenerateUsageReportMixin:
    """UsageFeedbackAnalyzer 方法集 Part 2"""

    def generate_usage_report(self, days: int = 30) -> str:
        """生成使用反馈分析报告"""
        logger.info(f"📊 生成使用反馈分析报告 (最近{days}天)")

        # 收集数据
        usage_patterns = self.collect_usage_patterns(days)
        feedback_patterns = self.analyze_feedback_patterns(days)

        # 生成报告
        report = f"""# AI测试优化器使用反馈分析报告

**分析时间范围**: 最近{days}天
**报告生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 使用情况统计

### 整体使用概况
- **总使用次数**: {usage_patterns["basic_stats"]["total_usage"]}
- **成功率**: {usage_patterns["basic_stats"]["success_rate"]:.1f}%
- **平均执行时间**: {usage_patterns["basic_stats"]["avg_execution_time"]:.2f}秒

### 性能指标
- **平均CPU使用**: {usage_patterns["performance_stats"]["avg_cpu_usage"]:.1f}%
- **平均内存使用**: {usage_patterns["performance_stats"]["avg_memory_usage"]:.1f}MB
- **平均处理文件数**: {usage_patterns["performance_stats"]["avg_files_processed"]:.1f}

## 📈 使用趋势分析

### 趋势指标
{self._format_usage_trends(usage_patterns)}

### 使用高峰时段
{self._format_peak_times(usage_patterns["peak_usage_times"])}

### 命令使用频率
{self._format_command_frequency(usage_patterns["most_used_commands"])}

### 成功模式分析
{self._format_success_patterns(usage_patterns["success_patterns"])}

## 🗣️ 用户反馈分析

### 反馈概览
{self._format_feedback_overview(feedback_patterns["basic_stats"])}

### 反馈情绪分析
- **正面反馈**: {feedback_patterns["sentiment_analysis"]["positive_sentiment"]:.1f}%
- **中性反馈**: {feedback_patterns["sentiment_analysis"]["neutral_sentiment"]:.1f}%
- **负面反馈**: {feedback_patterns["sentiment_analysis"]["negative_sentiment"]:.1f}%
- **情绪趋势**: {feedback_patterns["sentiment_analysis"].get("sentiment_trend", "unknown")}

### 问题分类统计
{self._format_issue_categories(feedback_patterns["issue_categories"])}

### 改进领域识别
{self._format_improvement_areas(feedback_patterns["improvement_areas"])}

### 用户满意度
- **总体评分**: {feedback_patterns["user_satisfaction"]["overall_score"]:.1f}/5.0
- **满意度等级**: {feedback_patterns["user_satisfaction"]["satisfaction_level"]}
- **满意度趋势**: {feedback_patterns["user_satisfaction"]["satisfaction_trend"]}

## 💡 数据驱动的改进建议

### 高优先级改进
{self._generate_high_priority_recommendations(usage_patterns, feedback_patterns)}

### 中优先级改进
{self._generate_medium_priority_recommendations(usage_patterns, feedback_patterns)}

### 低优先级改进
{self._generate_low_priority_recommendations(usage_patterns, feedback_patterns)}

## 📋 行动计划

### 立即行动项 (1-2周)
1. 根据用户反馈优化高频问题
2. 改进使用高峰时段的性能表现
3. 完善最受关注功能的文档

### 短期计划 (1个月)
1. 实施识别出的改进措施
2. 建立用户反馈快速响应机制
3. 优化用户体验和使用流程

### 长期计划 (3个月)
1. 基于数据趋势规划功能发展
2. 建立持续的改进循环机制
3. 扩展工具的使用覆盖面

---

*报告由AI测试优化器使用反馈分析系统自动生成*
"""

        return report

    def _format_usage_trends(self, patterns: Dict) -> str:
        """格式化使用趋势"""
        if "trend" in patterns:
            trend = patterns["trend"]
            if "growth_rate" in patterns:
                growth = patterns["growth_rate"]
                return f"- **趋势**: {trend.title()}\n- **增长率**: {growth:.1f}%"
        return "- **趋势**: 稳定\n- **增长率**: 0%"

    def _format_peak_times(self, peak_times: List[Dict]) -> str:
        """格式化高峰时段"""
        lines = ["| 时段 | 使用次数 | 描述 |", "|------|----------|--------|"]
        for peak in peak_times:
            lines.append(
                f"| {peak['time']} | {peak['usage_count']} | {peak['description']} |",
            )
        return "\n".join(lines)

    def _format_command_frequency(self, commands: Dict) -> str:
        """格式化命令频率"""
        lines = ["| 命令 | 使用次数 | 平均时间 |", "|------|----------|----------|"]
        for cmd, data in commands.get("detailed", {}).items():
            avg_time = data.get("avg_time", 0)
            lines.append(f"| {cmd} | {data['count']} | {avg_time:.2f}秒 |")
        return "\n".join(lines)

    def _format_success_patterns(self, patterns: Dict) -> str:
        """格式化成功模式"""
        lines = [f"- **总体成功率**: {patterns['overall_rate']:.1f}%"]

        if "by_time_of_day" in patterns:
            lines.append("\n### 按时段成功率")
            for period, rate in patterns["by_time_of_day"].items():
                period_names = {
                    "morning": "早晨",
                    "afternoon": "下午",
                    "evening": "晚上",
                }
                lines.append(f"- **{period_names.get(period, period)}**: {rate:.1f}%")

        return "\n".join(lines)

    def _format_feedback_overview(self, feedback_stats: Dict) -> str:
        """格式化反馈概览"""
        if not feedback_stats.get("feedback_by_type"):
            return "- 暂无反馈数据"

        lines = []
        total_feedback = sum(item["count"] for item in feedback_stats["feedback_by_type"])
        lines.append(f"- **总反馈数**: {total_feedback}")

        for feedback in feedback_stats["feedback_by_type"]:
            lines.append(
                f"- **{feedback['type']} ({feedback['category']}): {feedback['count']} 条",
            )
            if feedback["avg_rating"]:
                lines.append(f"  - 平均评分: {feedback['avg_rating']:.1f}⭐")

        return "\n".join(lines)

    def _format_issue_categories(self, issues: Dict) -> str:
        """格式化问题分类"""
        if not issues:
            return "- 暂无问题报告"

        lines = []
        for issue_type, count in issues.items():
            lines.append(f"- **{issue_type}**: {count} 个问题")

        return "\n".join(lines)

    def _format_improvement_areas(self, areas: List[Dict]) -> str:
        """格式化改进领域"""
        lines = []
        for i, area in enumerate(areas, 1):
            lines.append(
                f"{i}. **{area['area']}** (优先级: {area['priority']}, 影响: {area['impact']})",
            )

        return "\n".join(lines)

    def _generate_high_priority_recommendations(
        self,
        usage_patterns: Dict,
        feedback_patterns: Dict,
    ) -> List[str]:
        """生成高优先级改进建议"""
        recommendations = []

        # 基于使用情况
        if usage_patterns["basic_stats"]["success_rate"] < 85:
            recommendations.append("🔧 优先解决成功率低的问题，提升工具稳定性")

        if usage_patterns["basic_stats"]["avg_execution_time"] > 5:
            recommendations.append("⚡ 优化工具性能，减少平均执行时间")

        # 基于用户反馈
        if feedback_patterns["sentiment_analysis"]["negative_sentiment"] > 10:
            recommendations.append("🚨 立即解决用户负面反馈，改善用户体验")

        if feedback_patterns["issue_categories"].get("performance_issues", 0) > 20:
            recommendations.append("💰 重点解决性能问题，这是用户最关注的问题")

        return recommendations

    def _generate_medium_priority_recommendations(
        self,
        usage_patterns: Dict,
        feedback_patterns: Dict,
    ) -> List[str]:
        """生成中优先级改进建议"""
        recommendations = []

        if usage_patterns["performance_stats"]["avg_memory_usage"] > 200:
            recommendations.append("💾 优化内存使用效率")

        if feedback_patterns["issue_categories"].get("usability_issues", 0) > 10:
            recommendations.append("🖱️ 改进用户界面和使用体验")

        return recommendations

    def _generate_low_priority_recommendations(
        self,
        usage_patterns: Dict,
        feedback_patterns: Dict,
    ) -> List[str]:
        """生成低优先级改进建议"""
        recommendations = []

        if usage_patterns["basic_stats"]["total_usage"] > 100:
            recommendations.append("📈 考虑功能扩展以满足更多用户需求")

        if feedback_patterns["sentiment_analysis"]["positive_sentiment"] > 80:
            recommendations.append("🎉 继续保持用户满意度，定期收集反馈")

        return recommendations

    def save_analysis_report(self, report: str) -> Path:
        """保存分析报告"""
        today = datetime.now().strftime("%Y-%m-%d")
        report_path = self.analysis_dir / f"usage_feedback_analysis_{today}.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        return report_path

    def create_visual_charts(self, days: int = 30) -> None:
        """创建可视化图表"""
        try:
            # 收集数据
            usage_patterns = self.collect_usage_patterns(days)
            feedback_patterns = self.analyze_feedback_patterns(days)

            # 设置中文字体
            plt.rcParams["font.sans-serif"] = [
                "SimHei",
                "DejaVu Sans",
                "Arial Unicode MS",
            ]
            plt.rcParams["axes.unicode_minus"] = False

            # 创建图表
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

            # 图1: 使用趋势
            if "daily_usage" in usage_patterns["basic_stats"]:
                daily_data = usage_patterns["basic_stats"]["daily_usage"]
                dates = list(daily_data.keys())[-14:]  # 最近14天
                counts = list(daily_data.values())[-14:]

                ax1.plot(
                    dates,
                    counts,
                    marker="o",
                    linewidth=2,
                    markersize=8,
                    color="#2E86AB",
                )
                ax1.set_title("使用趋势 (最近14天)")
                ax1.set_xlabel("日期")
                ax1.set_ylabel("使用次数")
                ax1.tick_params(axis="x", rotation=45)
                ax1.grid(True, alpha=0.3)

            # 图2: 反馈分布
            if "rating_distribution" in feedback_patterns["basic_stats"]:
                ratings = list(
                    feedback_patterns["basic_stats"]["rating_distribution"].keys(),
                )
                counts = list(
                    feedback_patterns["basic_stats"]["rating_distribution"].values(),
                )
                colors = ["#FF6B6B", "#4ECDC4", "#FFD700", "#87CEEB", "#F0E68C"]

                bars = ax2.bar(ratings, counts, color=colors)
                ax2.set_title("用户评分分布")
                ax2.set_xlabel("评分")
                ax2.set_ylabel("反馈数量")

                # 添加数值标签
                for bar, count in zip(bars, counts):
                    height = bar.get_height()
                    ax2.text(
                        bar.get_x() + bar.get_width() / 2,
                        height + 1,
                        str(count),
                        ha="center",
                        va="bottom",
                    )

            # 图3: 成功率分布
            if "by_time_of_day" in usage_patterns["success_patterns"]:
                periods = list(
                    usage_patterns["success_patterns"]["by_time_of_day"].keys(),
                )
                rates = list(
                    usage_patterns["success_patterns"]["by_time_of_day"].values(),
                )

                colors = ["#90EE90", "#FFB6C1", "#FFDAB9"]
                bars = ax3.bar(periods, rates, color=colors)
                ax3.set_title("不同时段成功率")
                ax3.set_xlabel("时段")
                ax3.set_ylabel("成功率(%)")

                for bar, rate in zip(bars, rates):
                    height = bar.get_height()
                    ax3.text(
                        bar.get_x() + bar.get_width() / 2,
                        height + 1,
                        f"{rate:.1f}%",
                        ha="center",
                        va="bottom",
                    )

            # 图4: 问题类型分布
            if "issue_categories" in feedback_patterns["issue_categories"]:
                categories = list(feedback_patterns["issue_categories"].keys())
                counts = list(feedback_patterns["issue_categories"].values())

                bars = ax4.barh(categories, counts, color="#FF9999")
                ax4.set_title("问题类型分布")
                ax4.set_xlabel("问题数量")

                for bar, count in zip(bars, counts):
                    width = bar.get_width()
                    ax4.text(
                        width + 0.5,
                        bar.get_y() + bar.get_height() / 2,
                        str(count),
                        ha="left",
                        va="center",
                    )

            plt.tight_layout()

            # 保存图表
            chart_path = self.analysis_dir / f"usage_feedback_charts_{datetime.now().strftime('%Y-%m-%d')}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches="tight")
            logger.info(f"📊 可视化图表已保存: {chart_path}")

            return chart_path

        except Exception as e:
            logger.error(f"创建可视化图表失败: {e}")
            return None
