#!/usr/bin/env python3
"""
自动化数据清洗调度器

功能:
1. 每日收盘后自动验证K线数据
2. 每周检查行业数据质量
3. 自动修复adj_factor缺失值
4. 生成清洗报告并告警

用法:
    # 启动调度器（后台运行）
    nohup python scripts/data_cleaning/auto_clean_scheduler.py > logs/auto_clean.log 2>&1 &

    # 测试单次执行
    python scripts/data_cleaning/auto_clean_scheduler.py --test

    # 设置日志级别
    python scripts/data_cleaning/auto_clean_scheduler.py --log-level DEBUG
"""

import argparse
import logging
import sys
import schedule
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

# 添加项目根目录
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.data_cleaning.verify_db_data import DatabaseVerifier


class AutoCleanScheduler:
    """自动化数据清洗调度器"""

    def __init__(self, log_level: str = "INFO"):
        """
        初始化调度器

        参数:
            log_level: 日志级别
        """
        # 配置日志
        log_format = "%(asctime)s - %(levelname)s - %(message)s"
        logging.basicConfig(
            level=getattr(logging, log_level),
            format=log_format,
            handlers=[logging.StreamHandler(), logging.FileHandler("logs/auto_clean.log", encoding="utf-8")],
        )

        self.logger = logging.getLogger(__name__)

        # 确保日志目录存在
        Path("logs").mkdir(exist_ok=True)
        Path("reports/data_cleaning").mkdir(parents=True, exist_ok=True)

        # 初始化验证器
        self.verifier = DatabaseVerifier()

        # 统计信息
        self.stats = {
            "start_time": datetime.now().isoformat(),
            "kline_checks": 0,
            "industry_checks": 0,
            "auto_fixes": 0,
            "alerts": 0,
        }

    def daily_kline_check(self) -> Dict:
        """
        每日检查K线数据

        返回:
            检查结果字典
        """
        self.logger.info("=" * 60)
        self.logger.info("执行每日K线数据检查...")
        self.logger.info("=" * 60)

        result = {
            "timestamp": datetime.now().isoformat(),
            "check_type": "daily_kline",
            "tables_checked": [],
            "issues_found": [],
            "auto_fixes": 0,
        }

        tables_to_check = ["stocks_daily", "stocks_weekly", "stocks_monthly"]

        for table in tables_to_check:
            self.logger.info(f"\n检查表: {table}")

            try:
                # 检查adj_factor
                adj_result = self.verifier.check_adj_factor(table)
                result["tables_checked"].append({"table": table, "adj_factor": adj_result})

                # 判断是否需要自动修复
                if adj_result["valid_percent"] < 95:
                    self.logger.warning(
                        f"⚠️ {table} adj_factor有效率为{adj_result['valid_percent']:.2f}%，自动修复中..."
                    )

                    fix_result = self.verifier.fix_adj_factor(table, default_value=1.0, dry_run=False)

                    result["auto_fixes"] += fix_result["fixed_count"]
                    result["issues_found"].append(
                        {
                            "table": table,
                            "issue": "adj_factor_incomplete",
                            "severity": "WARNING",
                            "fixed": fix_result["fixed_count"],
                        }
                    )

                    self.logger.info(f"✅ 已修复{fix_result['fixed_count']}条记录")

                    # 记录告警
                    self._send_alert(
                        f"K线数据自动修复: {table}",
                        f"adj_factor有效率{adj_result['valid_percent']:.2f}%，"
                        f"已自动修复{fix_result['fixed_count']}条记录",
                    )
                else:
                    self.logger.info(f"✅ {table} adj_factor完整率: {adj_result['valid_percent']:.2f}%")

                # 检查K线结构
                structure_result = self.verifier.check_kline_structure(table)
                result["tables_checked"][-1]["structure"] = structure_result

                if not structure_result["has_all_required"]:
                    self.logger.error(f"❌ {table} 缺少必需列: {structure_result['missing_columns']}")

                    result["issues_found"].append(
                        {
                            "table": table,
                            "issue": "missing_columns",
                            "severity": "ERROR",
                            "details": structure_result["missing_columns"],
                        }
                    )

                    self._send_alert(f"K线数据结构异常: {table}", f"缺少必需列: {structure_result['missing_columns']}")

            except Exception as e:
                self.logger.error(f"检查 {table} 失败: {e}")
                result["issues_found"].append(
                    {"table": table, "issue": "check_failed", "severity": "ERROR", "error": str(e)}
                )

        # 更新统计
        self.stats["kline_checks"] += 1

        # 生成报告
        self._save_daily_report(result)

        return result

    def weekly_industry_check(self) -> Dict:
        """
        每周检查行业数据

        返回:
            检查结果字典
        """
        self.logger.info("=" * 60)
        self.logger.info("执行每周行业数据检查...")
        self.logger.info("=" * 60)

        result = {
            "timestamp": datetime.now().isoformat(),
            "check_type": "weekly_industry",
            "tables_checked": [],
            "issues_found": [],
            "auto_fixes": 0,
        }

        tables_to_check = ["stocks_basic"]

        for table in tables_to_check:
            self.logger.info(f"\n检查表: {table}")

            try:
                # 检查行业数据
                industry_result = self.verifier.check_industry_data(table)
                result["tables_checked"].append({"table": table, "industry_data": industry_result})

                dirty_percent = industry_result["dirty_percent"]

                if dirty_percent > 0:
                    self.logger.warning(
                        f"⚠️ {table} 脏数据率: {dirty_percent:.2f}% "
                        f"({industry_result['dirty_rows']}/{industry_result['total_rows']})"
                    )

                    # 如果脏数据超过10%，仅告警不自动修复
                    if dirty_percent > 10:
                        self.logger.error(f"❌ 脏数据率过高({dirty_percent:.2f}%)，需要人工审核")

                        result["issues_found"].append(
                            {
                                "table": table,
                                "issue": "high_dirty_rate",
                                "severity": "CRITICAL",
                                "dirty_rate": dirty_percent,
                                "dirty_rows": industry_result["dirty_rows"],
                            }
                        )

                        self._send_alert(
                            f"行业数据质量问题: {table}",
                            f"脏数据率{dirty_percent:.2f}%，需要人工审核（{industry_result['dirty_rows']}条记录）",
                        )
                    else:
                        # 脏数据率较低，自动清洗
                        self.logger.info("脏数据率较低，自动清洗中...")

                        clean_result = self.verifier.clean_industry_data(table, dry_run=False)

                        result["auto_fixes"] += clean_result["fixed_count"]
                        result["issues_found"].append(
                            {
                                "table": table,
                                "issue": "dirty_industry_data",
                                "severity": "WARNING",
                                "dirty_rate": dirty_percent,
                                "fixed": clean_result["fixed_count"],
                            }
                        )

                        self.logger.info(f"✅ 已清洗{clean_result['fixed_count']}条记录")

                        self._send_alert(
                            f"行业数据自动清洗: {table}",
                            f"脏数据率{dirty_percent:.2f}%，已自动清洗{clean_result['fixed_count']}条记录",
                        )
                else:
                    self.logger.info("✅ 行业数据完整，无需清洗")

            except Exception as e:
                self.logger.error(f"检查 {table} 失败: {e}")
                result["issues_found"].append(
                    {"table": table, "issue": "check_failed", "severity": "ERROR", "error": str(e)}
                )

        # 更新统计
        self.stats["industry_checks"] += 1

        # 生成报告
        self._save_weekly_report(result)

        return result

    def _send_alert(self, title: str, message: str):
        """
        发送告警

        参数:
            title: 告警标题
            message: 告警内容
        """
        self.stats["alerts"] += 1

        # 这里可以集成邮件、钉钉、企业微信等告警方式
        # 目前仅记录到日志
        self.logger.warning(f"🔔 告警: [{title}] {message}")

    def _save_daily_report(self, result: Dict):
        """保存每日报告"""
        timestamp = datetime.now().strftime("%Y%m%d")
        report_path = Path(f"reports/data_cleaning/daily_{timestamp}.json")

        try:
            import json

            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            self.logger.info(f"每日报告已保存: {report_path}")

        except Exception as e:
            self.logger.error(f"保存每日报告失败: {e}")

    def _save_weekly_report(self, result: Dict):
        """保存每周报告"""
        timestamp = datetime.now().strftime("%Y%W")
        report_path = Path(f"reports/data_cleaning/weekly_{timestamp}.json")

        try:
            import json

            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            self.logger.info(f"每周报告已保存: {report_path}")

        except Exception as e:
            self.logger.error(f"保存每周报告失败: {e}")

    def generate_summary(self) -> Dict:
        """生成统计摘要"""
        summary = self.stats.copy()
        summary["end_time"] = datetime.now().isoformat()

        duration = datetime.fromisoformat(summary["end_time"]) - datetime.fromisoformat(summary["start_time"])

        summary["duration_seconds"] = duration.total_seconds()
        summary["duration_formatted"] = str(duration)

        return summary

    def run(self):
        """启动调度器"""
        self.logger.info("=" * 60)
        self.logger.info("自动化清洗调度器已启动")
        self.logger.info("=" * 60)

        # 注册定时任务
        schedule.every().day.at("16:00").do(self.daily_kline_check)
        schedule.every().monday.at("09:00").do(self.weekly_industry_check)

        self.logger.info("已注册定时任务:")
        self.logger.info("  - 每日 16:00: K线数据检查")
        self.logger.info("  - 每周一 09:00: 行业数据检查")
        self.logger.info("")

        # 启动时执行一次检查（可选）
        # self.daily_kline_check()

        self.logger.info("调度器运行中，按 Ctrl+C 停止...")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            self.logger.info("\n" + "=" * 60)
            self.logger.info("调度器已停止")
            self.logger.info("=" * 60)

            # 输出统计摘要
            summary = self.generate_summary()
            self.logger.info("统计摘要:")
            self.logger.info(f"  运行时长: {summary['duration_formatted']}")
            self.logger.info(f"  K线检查次数: {summary['kline_checks']}")
            self.logger.info(f"  行业检查次数: {summary['industry_checks']}")
            self.logger.info(f"  自动修复次数: {summary['auto_fixes']}")
            self.logger.info(f"  告警次数: {summary['alerts']}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="自动化数据清洗调度器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 启动调度器（后台运行）
  nohup python auto_clean_scheduler.py > logs/auto_clean.log 2>&1 &

  # 测试单次K线检查
  python auto_clean_scheduler.py --test-kline

  # 测试单次行业检查
  python auto_clean_scheduler.py --test-industry

  # 设置日志级别
  python auto_clean_scheduler.py --log-level DEBUG
        """,
    )

    parser.add_argument("--test-kline", action="store_true", help="测试单次K线检查")
    parser.add_argument("--test-industry", action="store_true", help="测试单次行业检查")
    parser.add_argument(
        "--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="日志级别"
    )

    args = parser.parse_args()

    # 初始化调度器
    scheduler = AutoCleanScheduler(log_level=args.log_level)

    # 测试模式
    if args.test_kline:
        result = scheduler.daily_kline_check()
        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)
        return

    if args.test_industry:
        result = scheduler.weekly_industry_check()
        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)
        return

    # 正常模式：启动调度器
    scheduler.run()


if __name__ == "__main__":
    main()
