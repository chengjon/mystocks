"""
Scheduled Data Update Service
定时数据更新服务

Purpose: 定时采集资金流向数据 (证监会行业 + 申万行业)
Schedule: 每个交易日 15:30 自动执行
Technology: APScheduler (BackgroundScheduler)

Features:
- 支持多种行业分类同��更新 (csrc, sw_l1, sw_l2)
- 失败自动重试机制 (最多3次)
- 完整的日志记录
- 异常告警 (可扩展邮件/Webhook)
- 支持手动触发
"""

import logging
from datetime import datetime, time
from typing import List, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from web.backend.app.jobs.crawl_fund_flow import FundFlowCrawler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/tmp/scheduled_data_update.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ScheduledDataUpdateService:
    """定时数据更新服务"""

    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
        self.crawler = FundFlowCrawler()
        self.max_retries = 3
        self.industry_types = ["csrc", "sw_l1", "sw_l2"]

    def update_fund_flow_data(self, retry_count: int = 0) -> Dict[str, int]:
        """
        更新资金流向数据

        Args:
            retry_count: 当前重试次数

        Returns:
            每个行业类型保存的记录数
        """
        logger.info(
            f"Starting scheduled fund flow data update (attempt {retry_count + 1}/{self.max_retries})"
        )

        try:
            results = self.crawler.run_daily_crawler(industry_types=self.industry_types)

            # 检查是否所有数据源都成功
            total_records = sum(results.values())
            failed_sources = [k for k, v in results.items() if v == 0]

            if total_records == 0:
                # 所有数据源失败
                logger.error("All data sources failed!")
                if retry_count < self.max_retries - 1:
                    logger.info(
                        f"Retrying in 5 minutes... (attempt {retry_count + 2}/{self.max_retries})"
                    )
                    # 5分钟后重试
                    self.scheduler.add_job(
                        self.update_fund_flow_data,
                        "date",
                        run_date=datetime.now().replace(second=0, microsecond=0)
                        + pd.Timedelta(minutes=5),
                        args=[retry_count + 1],
                        id=f"retry_{retry_count + 1}",
                        replace_existing=True,
                    )
                else:
                    logger.error("Max retries reached. Sending alert...")
                    self._send_alert(
                        "critical",
                        "Fund Flow Data Update Failed",
                        f"All {self.max_retries} attempts failed. Manual intervention required.",
                    )
                return results

            elif failed_sources:
                # 部分数据源失败
                logger.warning(f"Partial failure: {failed_sources} returned 0 records")
                self._send_alert(
                    "warning",
                    "Fund Flow Data Update Partial Failure",
                    f"Failed sources: {', '.join(failed_sources)}\n"
                    f"Successful: {[k for k, v in results.items() if v > 0]}\n"
                    f"Total records: {total_records}",
                )
            else:
                # 全部成功
                logger.info(
                    f"✅ All data sources updated successfully! Total records: {total_records}"
                )
                logger.info(f"Breakdown: {results}")

            return results

        except Exception as e:
            logger.error(f"Unexpected error during data update: {e}", exc_info=True)
            if retry_count < self.max_retries - 1:
                logger.info(
                    f"Retrying in 5 minutes... (attempt {retry_count + 2}/{self.max_retries})"
                )
                import pandas as pd

                self.scheduler.add_job(
                    self.update_fund_flow_data,
                    "date",
                    run_date=datetime.now() + pd.Timedelta(minutes=5),
                    args=[retry_count + 1],
                    id=f"retry_{retry_count + 1}",
                    replace_existing=True,
                )
            else:
                self._send_alert(
                    "critical",
                    "Fund Flow Data Update Exception",
                    f"Exception: {str(e)}\nMax retries reached.",
                )
            return {}

    def _send_alert(self, level: str, title: str, message: str):
        """
        发送告警

        Args:
            level: 告警级别 (info/warning/critical)
            title: 告警标题
            message: 告警内容

        Note: 当前仅记录日志,可扩展为邮件/Webhook/Slack等
        """
        logger.log(
            (
                logging.CRITICAL
                if level == "critical"
                else logging.WARNING if level == "warning" else logging.INFO
            ),
            f"ALERT [{level.upper()}] {title}: {message}",
        )

        # TODO: 扩展为实际的告警机制
        # 示例:
        # - 发送邮件: self._send_email(title, message)
        # - Webhook: requests.post(WEBHOOK_URL, json={'title': title, 'message': message})
        # - Slack: slack_client.chat_postMessage(channel='#alerts', text=f'{title}\n{message}')

    def start(self):
        """启动定时任务调度器"""
        # 添加每日15:30的定时任务
        self.scheduler.add_job(
            self.update_fund_flow_data,
            CronTrigger(
                day_of_week="mon-fri",  # 仅工作日
                hour=15,
                minute=30,
                timezone="Asia/Shanghai",
            ),
            id="daily_fund_flow_update",
            name="Daily Fund Flow Data Update",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info("✅ Scheduled Data Update Service started")
        logger.info("Schedule: Monday-Friday 15:30 (Asia/Shanghai)")
        logger.info(f"Industry types: {', '.join(self.industry_types)}")
        logger.info(f"Max retries: {self.max_retries}")

    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown(wait=True)
        logger.info("Scheduled Data Update Service stopped")

    def trigger_manual_update(self) -> Dict[str, int]:
        """手动触发数据更新"""
        logger.info("Manual update triggered")
        return self.update_fund_flow_data()

    def get_next_run_time(self) -> str:
        """获取下次执行时间"""
        job = self.scheduler.get_job("daily_fund_flow_update")
        if job:
            return job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
        return "N/A"

    def get_job_status(self) -> Dict[str, Any]:
        """获取任务状态"""
        job = self.scheduler.get_job("daily_fund_flow_update")
        if not job:
            return {"status": "not_scheduled"}

        return {
            "status": "active",
            "job_id": job.id,
            "job_name": job.name,
            "next_run_time": (
                job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
                if job.next_run_time
                else None
            ),
            "trigger": str(job.trigger),
            "industry_types": self.industry_types,
            "max_retries": self.max_retries,
        }


# 全局实例
scheduler_service = ScheduledDataUpdateService()


def main():
    """主函数: 测试定时任务服务"""
    import time

    logger.info("=" * 60)
    logger.info("Testing Scheduled Data Update Service")
    logger.info("=" * 60)

    # 启动服务
    scheduler_service.start()

    # 显示任务状态
    status = scheduler_service.get_job_status()
    logger.info(f"\nJob Status: {status}")

    # 获取下次执行时间
    next_run = scheduler_service.get_next_run_time()
    logger.info(f"Next scheduled run: {next_run}")

    # 提示是否手动触发
    logger.info("\nOptions:")
    logger.info("1. Press Enter to trigger manual update")
    logger.info("2. Press Ctrl+C to exit")

    try:
        input()
        logger.info("\n" + "=" * 60)
        logger.info("Manual Update Triggered")
        logger.info("=" * 60)
        results = scheduler_service.trigger_manual_update()
        logger.info(f"\nUpdate Results: {results}")
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
    finally:
        scheduler_service.stop()


if __name__ == "__main__":
    main()
