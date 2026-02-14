#!/usr/bin/env python3
"""
AI测试优化器使用反馈分析器
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

import sys
import sqlite3
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import argparse
import logging
import matplotlib.pyplot as plt

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI测试优化器使用反馈分析工具")
    parser.add_argument("--days", "-d", type=int, default=30, help="分析最近N天的数据")
    parser.add_argument(
        "--usage-only", "-u", action="store_true", help="只分析使用数据，不包括反馈"
    )
    parser.add_argument(
        "--feedback-only", "-f", action="store_true", help="只分析反馈数据，不包括使用"
    )
    parser.add_argument("--report", "-r", action="store_true", help="生成分析报告")
    parser.add_argument("--charts", "-c", action="store_true", help="生成可视化图表")

    args = parser.parse_args()

    try:
        analyzer = UsageFeedbackAnalyzer()

        if args.usage_only and args.feedback_only:
            print("❌ 不能同时指定 --usage-only 和 --feedback-only")
            return 1

        if args.usage_only or not args.feedback_only:
            print("📊 分析使用数据...")
            usage_patterns = analyzer.collect_usage_patterns(args.days)
            print("✅ 使用数据分析完成")

        if args.feedback_only or not args.usage_only:
            print("📝 分析用户反馈...")
            feedback_patterns = analyzer.analyze_feedback_patterns(args.days)
            print("✅ 反馈分析完成")

        if args.report or not (args.usage_only or args.feedback_only):
            print("📄 生成分析报告...")
            report = analyzer.generate_usage_report(args.days)
            report_path = analyzer.save_analysis_report(report)
            print(f"✅ 分析报告已生成: {report_path}")

            # 显示报告摘要
            print("\n📊 报告摘要:")
            if "basic_stats" in usage_patterns:
                print(f"  - 总使用次数: {usage_patterns['basic_stats']['total_usage']}")
                print(
                    f"  - 成功率: {usage_patterns['basic_stats']['success_rate']:.1f}%"
                )
                print(
                    f"  - 平均执行时间: {usage_patterns['basic_stats']['avg_execution_time']:.2f}秒"
                )

            if "basic_stats" in feedback_patterns:
                total_feedback = sum(
                    item["count"]
                    for item in feedback_patterns["basic_stats"].get(
                        "feedback_by_type", []
                    )
                )
                print(f"  - 总反馈数: {total_feedback}")

        if args.charts:
            print("📊 生成可视化图表...")
            chart_path = analyzer.create_visual_charts(args.days)
            if chart_path:
                print(f"✅ 可视化图表已生成: {chart_path}")

    except KeyboardInterrupt:
        print("\n⏹️  分析已取消")
    except Exception as e:
        logger.error(f"💥 分析过程中发生异常: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


