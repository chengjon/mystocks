#!/usr/bin/env python3
"""
BUG Reporter for MyStocks Project
Reports bugs to BUGer service and logs results
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BugReporter:
    """BUG Reporter client for BUGer service"""

    def __init__(self):
        self.api_url = os.getenv("BUGER_API_URL", "http://localhost:3003/api")
        self.api_key = os.getenv("BUGER_API_KEY", "sk_test_xyz123")
        self.project_id = os.getenv("PROJECT_ID", "mystocks")
        self.log_file = "bug_report_log.json"

    def report_bug(self, bug_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Report a single bug to BUGer service"""
        try:
            response = requests.post(
                f"{self.api_url}/bugs",
                json=bug_data,
                headers={"X-API-Key": self.api_key, "Content-Type": "application/json"},
                timeout=10,
            )

            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                bug_id = result.get("data", {}).get("bugId", "unknown")
                logger.info(f"✅ BUG上报成功: {bug_id}")
                return result
            else:
                logger.error(
                    f"❌ BUG上报失败: HTTP {response.status_code} - {response.text}"
                )
                return {
                    "success": False,
                    "error": response.text,
                    "status_code": response.status_code,
                }

        except requests.exceptions.ConnectionError:
            logger.warning("⚠️  无法连接到BUGer服务 (连接被拒绝或服务未运行)")
            return {
                "success": False,
                "error": "Connection refused - BUGer service not running",
            }
        except requests.exceptions.Timeout:
            logger.error("❌ 请求超时")
            return {"success": False, "error": "Request timeout"}
        except Exception as e:
            logger.error(f"❌ BUG上报异常: {str(e)}")
            return {"success": False, "error": str(e)}

    def report_bugs_batch(self, bugs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Report multiple bugs in batch"""
        try:
            response = requests.post(
                f"{self.api_url}/bugs/batch",
                json={"bugs": bugs},
                headers={"X-API-Key": self.api_key, "Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                summary = result.get("data", {}).get("summary", {})
                logger.info(
                    f'✅ 批量上报完成: {summary.get("successful", 0)}成功, {summary.get("failed", 0)}失败'
                )
                return result
            else:
                logger.error(f"❌ 批量上报失败: HTTP {response.status_code}")
                return {"success": False, "error": response.text}

        except requests.exceptions.ConnectionError:
            logger.warning("⚠️  无法连接到BUGer服务 (连接被拒绝或服务未运行)")
            return {
                "success": False,
                "error": "Connection refused - BUGer service not running",
            }
        except Exception as e:
            logger.error(f"❌ 批量上报异常: {str(e)}")
            return {"success": False, "error": str(e)}

    def format_bug(
        self,
        error_code: str,
        title: str,
        message: str,
        severity: str = "medium",
        stack_trace: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Format bug data for reporting"""
        return {
            "errorCode": error_code,
            "title": title,
            "message": message,
            "severity": severity,
            "stackTrace": stack_trace,
            "context": {
                "timestamp": datetime.now().isoformat(),
                "project": self.project_id,
                **(context or {}),
            },
        }

    def save_log(self, bugs: List[Dict[str, Any]], results: List[Dict[str, Any]]):
        """Save bug report log to file"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "project": self.project_id,
            "total_bugs": len(bugs),
            "bugs": bugs,
            "results": results,
        }

        log_path = f"/opt/claude/mystocks_spec/{self.log_file}"

        # Load existing logs
        existing_logs = []
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    existing_logs = json.load(f)
                    if not isinstance(existing_logs, list):
                        existing_logs = [existing_logs]
            except:
                existing_logs = []

        # Append new log
        existing_logs.append(log_data)

        # Save to file
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(existing_logs, f, indent=2, ensure_ascii=False)

        logger.info(f"📝 日志已保存到: {log_path}")


def main():
    """Main function to report bugs discovered in this session"""
    reporter = BugReporter()

    logger.info("=" * 60)
    logger.info("MyStocks BUG Reporter - Session 2025-10-30")
    logger.info("=" * 60)

    # Define bugs discovered in this session
    bugs = [
        reporter.format_bug(
            error_code="IMPORT_ERROR_001",
            title="缺少require_admin函数导致后端启动失败",
            message="在app.core.security模块中缺少require_admin函数，导致scheduled_jobs.py导入失败",
            severity="critical",
            stack_trace="""ImportError: cannot import name 'require_admin' from 'app.core.security'
File: /opt/claude/mystocks_spec/web/backend/app/api/scheduled_jobs.py:15
from app.core.security import get_current_user, User, require_admin""",
            context={
                "component": "backend",
                "module": "app.core.security",
                "file": "web/backend/app/core/security.py",
                "fix": "添加require_admin函数用于管理员权限验证",
                "status": "FIXED",
                "fix_commit": "Added require_admin function to security.py",
                "session": "2025-10-30",
                "bug_id": "BUG-NEW-003",
            },
        ),
        reporter.format_bug(
            error_code="MODULE_NOT_FOUND_001",
            title="缺少apscheduler依赖导致后端ImportError",
            message="scheduled_data_update.py需要apscheduler库，但环境中未安装该依赖",
            severity="critical",
            stack_trace="""ModuleNotFoundError: No module named 'apscheduler'
File: /opt/claude/mystocks_spec/web/backend/app/services/scheduled_data_update.py:20
from apscheduler.schedulers.background import BackgroundScheduler""",
            context={
                "component": "backend",
                "module": "app.services.scheduled_data_update",
                "file": "web/backend/app/services/scheduled_data_update.py",
                "fix": "pip install apscheduler",
                "status": "FIXED",
                "fix_command": "pip install apscheduler==3.11.0",
                "session": "2025-10-30",
                "bug_id": "BUG-NEW-004",
                "related_task": "Task 6: Scheduled Data Updates",
            },
        ),
    ]

    logger.info(f"\n📋 准备上报 {len(bugs)} 个BUG...\n")

    # Report bugs individually
    results = []
    for i, bug in enumerate(bugs, 1):
        logger.info(f'[{i}/{len(bugs)}] 上报BUG: {bug["errorCode"]} - {bug["title"]}')
        result = reporter.report_bug(bug)
        results.append(
            {"bug": bug, "result": result, "timestamp": datetime.now().isoformat()}
        )
        logger.info("")

    # Save log
    reporter.save_log(bugs, results)

    # Summary
    logger.info("=" * 60)
    logger.info("📊 上报总结")
    logger.info("=" * 60)
    successful = sum(
        1 for r in results if r["result"] and r["result"].get("success") != False
    )
    failed = len(results) - successful
    logger.info(f"总计: {len(bugs)} 个BUG")
    logger.info(f"成功: {successful} 个")
    logger.info(f"失败: {failed} 个")

    if failed > 0:
        logger.warning(f"\n⚠️  注意: {failed} 个BUG上报失败 (可能BUGer服务未运行)")
        logger.info("提示: 日志已保存到 bug_report_log.json，可在BUGer服务启动后重试")

    logger.info("=" * 60)

    return results


if __name__ == "__main__":
    main()
