#!/usr/bin/env python3
"""
Comprehensive BUG Submission Script
Submits all historical and new bugs to BUGer service
"""

import os
import sys
from datetime import datetime

# Add parent directory to path to import bug_reporter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bug_reporter import BugReporter


def collect_all_bugs():
    """Collect all bugs from knowledge base"""
    reporter = BugReporter()

    bugs = [
        # Historical bugs from BUG知识库.md
        # BUG-001: Dashboard API 500错误
        reporter.format_bug(
            error_code="SQL_COLUMN_NAME_ERROR",
            title="Dashboard API 500错误：SQL查询使用错误列名",
            message="GET /api/data/dashboard/summary返回500错误，SQL查询使用错误列名`date`，实际数据库列名为`trade_date`",
            severity="high",
            stack_trace="SQL Error: column 'date' does not exist\nFile: database.py:173-187",
            context={
                "component": "backend",
                "module": "database",
                "file": "database.py",
                "line": "173-187",
                "fix": "将SQL查询中的`date`改为`trade_date`",
                "fix_commit": "修复database.py第173-187行",
                "status": "FIXED",
                "session": "2025-10-27",
                "bug_id": "BUG-001",
                "discovery_date": "2025-10-27",
                "影响范围": "Dashboard页面数据加载",
            },
        ),
        # BUG-002: ECharts DOM尺寸错误
        reporter.format_bug(
            error_code="ECHARTS_DOM_SIZE_ERROR",
            title="ECharts DOM尺寸错误：在DOM尺寸为0时初始化",
            message='控制台报错"[ECharts] Can\'t get DOM width or height"，ECharts在DOM元素尺寸为0时初始化',
            severity="medium",
            stack_trace="[ECharts] Can't get DOM width or height. Check if the target element has appropriate dimensions.",
            context={
                "component": "frontend",
                "module": "ChartWrapper.vue",
                "file": "web/frontend/src/components/ChartWrapper.vue",
                "fix": "在ChartWrapper.vue中添加v-if条件判断和nextTick延迟初始化",
                "status": "FIXED",
                "session": "2025-10-27",
                "bug_id": "BUG-002",
                "discovery_date": "2025-10-27",
                "影响范围": "所有使用ECharts的图表组件",
            },
        ),
        # BUG-003: ChipRaceTable Props类型错误
        reporter.format_bug(
            error_code="PROPS_TYPE_MISMATCH_NUMBER",
            title="ChipRaceTable Props类型错误：期望Number收到String",
            message="Props验证失败，后端返回字符串类型，前端期望数字类型",
            severity="medium",
            stack_trace='[Vue warn]: Invalid prop: type check failed for prop "xxx". Expected Number, got String.',
            context={
                "component": "frontend",
                "module": "ChipRaceTable.vue",
                "file": "web/frontend/src/components/ChipRaceTable.vue",
                "fix": "使用Number()转换数据类型",
                "status": "FIXED",
                "session": "2025-10-27",
                "bug_id": "BUG-003",
                "discovery_date": "2025-10-27",
                "影响范围": "竞价抢筹表格显示",
            },
        ),
        # BUG-004: LongHuBangTable Props类型错误
        reporter.format_bug(
            error_code="PROPS_TYPE_MISMATCH_FLOAT",
            title="LongHuBangTable Props类型错误：期望Number收到String",
            message="Props验证失败，后端返回字符串类型，前端期望数字类型",
            severity="medium",
            stack_trace='[Vue warn]: Invalid prop: type check failed for prop "xxx". Expected Number, got String.',
            context={
                "component": "frontend",
                "module": "LongHuBangTable.vue",
                "file": "web/frontend/src/components/LongHuBangTable.vue",
                "fix": "使用parseFloat()转换数据类型",
                "status": "FIXED",
                "session": "2025-10-27",
                "bug_id": "BUG-004",
                "discovery_date": "2025-10-27",
                "影响范围": "龙虎榜表格显示",
            },
        ),
        # BUG-005: IndicatorLibrary ElTag类型验证错误
        reporter.format_bug(
            error_code="ELTAG_TYPE_VALIDATION_ERROR",
            title="IndicatorLibrary ElTag类型验证错误",
            message="ElTag组件type属性验证失败，传递了空字符串给type属性",
            severity="low",
            stack_trace='[Vue warn]: Invalid prop: custom validator check failed for prop "type".',
            context={
                "component": "frontend",
                "module": "IndicatorLibrary.vue",
                "file": "web/frontend/src/views/IndicatorLibrary.vue",
                "fix": "移除type绑定，使用默认值",
                "status": "FIXED",
                "session": "2025-10-27",
                "bug_id": "BUG-005",
                "discovery_date": "2025-10-27",
                "影响范围": "指标库页面标签显示",
            },
        ),
        # BUG-013: 前端服务端口配置错误
        reporter.format_bug(
            error_code="PORT_OCCUPIED_ERROR",
            title="前端服务端口配置错误：3000端口被占用",
            message="前端服务运行在3001端口而非要求的3000端口，3000端口被其他Node进程占用（PID: 98193）",
            severity="low",
            stack_trace="N/A - Configuration issue without stack trace",
            context={
                "component": "frontend",
                "module": "dev-server",
                "file": "package.json",
                "fix": "终止占用3000端口的进程，建议在package.json中固定端口配置",
                "status": "FIXED",
                "session": "2025-10-27",
                "bug_id": "BUG-013",
                "discovery_date": "2025-10-27",
                "影响范围": "前端访问",
            },
        ),
        # BUG-014: 路由路径不存在
        reporter.format_bug(
            error_code="ROUTE_NOT_FOUND_404",
            title="路由路径不存在：/stocks返回404",
            message="访问/stocks路径返回404错误，系统中不存在/stocks路径，正确路径是/watchlist",
            severity="low",
            stack_trace="N/A - Configuration issue without stack trace",
            context={
                "component": "frontend",
                "module": "router",
                "file": "web/frontend/src/router/index.js",
                "fix": "使用正确的路由路径/watchlist",
                "status": "FIXED",
                "session": "2025-10-27",
                "bug_id": "BUG-014",
                "discovery_date": "2025-10-27",
                "影响范围": "自选股页面访问",
            },
        ),
        # BUG-NEW-002: Dashboard资金流向面板显示零值
        reporter.format_bug(
            error_code="MOCK_DATA_NOT_REPLACED",
            title="Dashboard资金流向面板显示零值",
            message='Dashboard页面"资金流向"面板所有数值显示为零。根本原因：(1)前端使用硬编码mock数据 (2)API端点路径错误 (3)数据库有86条真实记录但未被使用',
            severity="high",
            stack_trace="N/A - Configuration issue without stack trace",
            context={
                "component": "frontend",
                "module": "Dashboard.vue",
                "file": "web/frontend/src/views/Dashboard.vue",
                "fix": "添加loadFundFlowData()函数调用真实API，移除硬编码mock数据，实现动态行业标准切换",
                "status": "FIXED",
                "session": "2025-10-30",
                "bug_id": "BUG-NEW-002",
                "discovery_date": "2025-10-30",
                "validation_method": "5层验证方法论",
                "新增代码": "72行 (新函数 + 状态管理 + UI增强)",
                "API端点": "GET /api/market/v3/fund-flow?industry_type={csrc|sw_l1|sw_l2}&limit=20",
                "影响范围": "Dashboard资金流向面板",
                "方法论价值": "首个成功应用5层验证方法论的BUG修复案例",
            },
        ),
        # BUG-NEW-003: 缺少require_admin函数 (from previous session)
        reporter.format_bug(
            error_code="IMPORT_ERROR_REQUIRE_ADMIN",
            title="缺少require_admin函数导致后端启动失败",
            message="在app.core.security模块中缺少require_admin函数，导致scheduled_jobs.py导入失败，后端应用无法启动",
            severity="critical",
            stack_trace="""ImportError: cannot import name 'require_admin' from 'app.core.security'
File: /opt/claude/mystocks_spec/web/backend/app/api/scheduled_jobs.py:15
from app.core.security import get_current_user, User, require_admin""",
            context={
                "component": "backend",
                "module": "app.core.security",
                "file": "web/backend/app/core/security.py",
                "line": "195-204",
                "fix": "添加require_admin函数用于管理员权限验证",
                "fix_commit": "2039e4d",
                "status": "FIXED",
                "session": "2025-10-30",
                "bug_id": "BUG-NEW-003",
                "discovery_date": "2025-10-30",
                "相关任务": "Task 6: Scheduled Data Updates",
            },
        ),
        # BUG-NEW-004: 缺少apscheduler依赖 (from previous session)
        reporter.format_bug(
            error_code="MODULE_NOT_FOUND_APSCHEDULER",
            title="缺少apscheduler依赖导致后端ImportError",
            message="scheduled_data_update.py需要apscheduler库，但环境中未安装该依赖，导致后端应用无法启动",
            severity="critical",
            stack_trace="""ModuleNotFoundError: No module named 'apscheduler'
File: /opt/claude/mystocks_spec/web/backend/app/services/scheduled_data_update.py:20
from apscheduler.schedulers.background import BackgroundScheduler""",
            context={
                "component": "backend",
                "module": "app.services.scheduled_data_update",
                "file": "web/backend/app/services/scheduled_data_update.py",
                "line": "20",
                "fix": "pip install apscheduler==3.11.0",
                "fix_command": "pip install apscheduler==3.11.0",
                "status": "FIXED",
                "session": "2025-10-30",
                "bug_id": "BUG-NEW-004",
                "discovery_date": "2025-10-30",
                "相关任务": "Task 6: Scheduled Data Updates",
            },
        ),
    ]

    return bugs


def main():
    """Main submission workflow"""
    reporter = BugReporter()

    print("=" * 70)
    print("MyStocks BUG Complete Knowledge Base Submission to BUGer")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("")

    # Collect all bugs
    print("📋 Collecting all bugs from knowledge base...")
    bugs = collect_all_bugs()
    print(f"✅ Total bugs collected: {len(bugs)}")
    print("")

    # Display summary
    print("📊 BUG Summary:")
    print("-" * 70)
    for i, bug in enumerate(bugs, 1):
        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢",
        }.get(bug["severity"], "⚪")
        print(f"{i:2d}. {severity_emoji} [{bug['context']['bug_id']}] {bug['title']}")
    print("-" * 70)
    print("")

    # Submit bugs individually
    print("🚀 Starting bug submission...")
    print("")

    results = []
    for i, bug in enumerate(bugs, 1):
        bug_id = bug["context"].get("bug_id", "UNKNOWN")
        print(f"[{i}/{len(bugs)}] Submitting {bug_id}: {bug['title'][:50]}...")

        result = reporter.report_bug(bug)
        results.append(
            {"bug": bug, "result": result, "timestamp": datetime.now().isoformat()}
        )

        if result and result.get("success") != False:
            buger_id = result.get("data", {}).get("bugId", "N/A")
            print(f"     ✅ Success! BUGer ID: {buger_id}")
        else:
            error = result.get("error", "Unknown error") if result else "No response"
            print(f"     ❌ Failed: {error}")
        print("")

    # Save comprehensive log
    print("📝 Saving submission log...")
    reporter.save_log(bugs, results)
    print("")

    # Summary statistics
    print("=" * 70)
    print("📊 Submission Summary")
    print("=" * 70)

    successful = sum(
        1 for r in results if r["result"] and r["result"].get("success") != False
    )
    failed = len(results) - successful

    print(f"Total bugs:      {len(bugs)}")
    print(f"✅ Successful:   {successful}")
    print(f"❌ Failed:       {failed}")

    if failed > 0:
        print("")
        print("⚠️  Some bugs failed to submit (likely BUGer service not running)")
        print("   Logs saved to: bug_report_log.json")
        print("   You can retry submission after BUGer service is started")

    print("=" * 70)
    print("")
    print("✅ All bugs have been processed!")
    print("   Log file: /opt/claude/mystocks_spec/bug_report_log.json")
    print("")

    return results


if __name__ == "__main__":
    main()
