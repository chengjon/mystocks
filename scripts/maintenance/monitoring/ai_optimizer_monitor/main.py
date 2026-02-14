#!/usr/bin/env python3
"""
AI测试优化器监控和反馈收集系统
实时监控工具使用情况、收集用户反馈、分析性能指标

功能:
1. 使用情况监控
2. 性能指标收集
3. 用户反馈管理
4. 趋势分析报告
5. 异常检测和告警

作者: MyStocks AI Team
版本: 1.0
日期: 2025-01-22
"""

import json
import time
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import argparse
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
MONITORING_DIR = PROJECT_ROOT / "monitoring_data"
MONITORING_DIR.mkdir(exist_ok=True)

# 数据库路径
DB_PATH = MONITORING_DIR / "ai_optimizer_monitor.db"

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI测试优化器监控和反馈收集系统")
    parser.add_argument("--daemon", "-d", action="store_true", help="运行监控守护进程")
    parser.add_argument(
        "--report", "-r", action="store_true", help="生成并显示每日报告"
    )
    parser.add_argument(
        "--usage-stats", "-u", type=int, default=7, help="获取最近N天的使用统计"
    )
    parser.add_argument(
        "--performance-stats", "-p", type=int, default=7, help="获取最近N天的性能统计"
    )
    parser.add_argument(
        "--check-anomalies", "-a", action="store_true", help="检查并报告异常"
    )
    parser.add_argument(
        "--feedback", "-f", action="store_true", help="显示用户反馈摘要"
    )

    args = parser.parse_args()

    try:
        monitor = AIOptimizerMonitor()

        if args.daemon:
            run_monitoring_daemon()
        elif args.report:
            logger.info("📊 生成每日监控报告")
            report = monitor.generate_daily_report()
            print(report)

            # 保存报告
            report_path = monitor.save_daily_report(report)
            print(f"\n📄 报告已保存: {report_path}")
        elif args.usage_stats:
            stats = monitor.get_usage_stats(args.usage_stats)
            print(f"📊 最近{args.usage_stats}天使用统计:")
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        elif args.performance_stats:
            stats = monitor.get_performance_stats(args.performance_stats)
            print(f"⚡ 最近{args.performance_stats}天性能统计:")
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        elif args.check_anomalies:
            anomalies = monitor.detect_anomalies()
            if anomalies:
                print(f"🚨 检测到 {len(anomalies)} 个异常:")
                for anomaly in anomalies:
                    print(f"  [{anomaly['severity'].upper()}] {anomaly['message']}")
            else:
                print("✅ 未检测到异常")
        elif args.feedback:
            feedback = monitor.get_feedback_summary()
            print("🗣️ 用户反馈摘要:")
            print(json.dumps(feedback, indent=2, ensure_ascii=False))
        else:
            print("请使用 --help 查看可用选项")
            return 1

    except Exception as e:
        logger.error(f"💥 监控系统发生异常: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


