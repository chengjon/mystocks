"""测试日志和审计系统
Test Logging and Audit System

验证结构化日志记录、审计追踪、安全监控等功能的正确性。
Validates structured logging, audit trails, security monitoring functions.
"""

import asyncio
import logging
import os
import sys
import tempfile
from datetime import datetime
from unittest.mock import MagicMock


# Setup project path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.infrastructure.logging.audit_system import (
    AuditEvent,
    AuditManager,
    LogConfig,
    SecurityMonitor,
    StructuredLogger,
    get_audit_manager,
    get_security_monitor,
    get_structured_logger,
)


class MockDatabaseConnection:
    """模拟数据库连接"""

    def __init__(self):
        self.executed_queries = []
        self.fetch_results = []

    async def execute(self, query: str, *args):
        """模拟执行查询"""
        self.executed_queries.append((query, args))
        return "1"

    async def executemany(self, query: str, values: list):
        """模拟批量执行"""
        self.executed_queries.append((query, values))
        return len(values)

    async def fetch(self, query: str, *args):
        """模拟查询结果"""
        # 返回模拟的审计日志数据
        if "FROM audit_logs" in query:
            return [
                {
                    "id": "test-uuid-1",
                    "user_id": "user-uuid-1",
                    "action": "login",
                    "resource_type": "user",
                    "resource_id": "user-uuid-1",
                    "ip_address": "example.local",
                    "user_agent": "Mozilla/5.0",
                    "request_method": "POST",
                    "request_path": "/api/auth/login",
                    "status": "success",
                    "error_message": None,
                    "additional_data": '{"login_method": "password"}',
                    "created_at": datetime.now(),
                },
            ]
        return []

    async def fetchval(self, query: str, *args):
        """模拟单个值查询"""
        return 5  # 模拟删除的行数

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


async def test_structured_logger():
    """测试结构化日志记录器"""
    logger.info("🧪 测试结构化日志记录器...")

    # 创建临时日志文件
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".log", delete=False) as temp_file:
        temp_log_file = temp_file.name

    try:
        # 创建日志配置
        config = LogConfig(
            log_level="DEBUG",
            log_file=temp_log_file,
            enable_console=False,  # 禁用控制台输出避免干扰测试
            enable_structured=True,
        )

        # 创建日志记录器
        logger_instance = StructuredLogger(config)

        # 测试HTTP请求日志
        logger_instance.log_request(
            method="GET",
            path="/api/stocks/AAPL",
            status_code=200,
            duration=150.5,
            user_id="test-user-123",
        )

        # 测试数据库操作日志
        logger_instance.log_database_operation(
            operation="SELECT",
            table="stocks",
            record_count=100,
            duration=45.2,
            user_id="test-user-123",
        )

        # 测试安全事件日志
        logger_instance.log_security_event(
            event_type="failed_login",
            severity="medium",
            details={"ip_address": "example.local", "username": "testuser", "attempt_count": 3},
            user_id="test-user-123",
        )

        # 测试业务事件日志
        logger_instance.log_business_event(
            event_type="strategy_execution",
            details={"strategy_name": "SVM_Trend", "symbol": "AAPL", "pnl": 1250.50},
            user_id="test-user-123",
        )

        # 验证日志文件已创建并包含内容
        assert os.path.exists(temp_log_file), "日志文件未创建"

        with open(temp_log_file) as f:
            log_content = f.read()
            assert len(log_content) > 0, "日志文件为空"

            # 验证包含关键日志信息
            assert "HTTP Request" in log_content, "HTTP请求日志未记录"
            assert "Database Operation" in log_content, "数据库操作日志未记录"
            assert "Security Event" in log_content, "安全事件日志未记录"
            assert "Business Event" in log_content, "业务事件日志未记录"

        logger.info("✅ 结构化日志记录器测试通过")

    finally:
        # 清理临时文件
        if os.path.exists(temp_log_file):
            os.unlink(temp_log_file)


async def test_audit_manager():
    """测试审计管理器"""
    logger.info("🧪 测试审计管理器...")

    # 创建模拟数据库管理器
    mock_db_manager = MagicMock()
    mock_conn = MockDatabaseConnection()
    mock_db_manager.get_connection.return_value.__aenter__.return_value = mock_conn
    mock_db_manager.get_connection.return_value.__aexit__.return_value = None

    # 创建审计管理器
    audit_manager = AuditManager(mock_db_manager)

    # 启动审计工作进程
    await audit_manager.start_audit_worker()

    try:
        # 创建审计事件
        event = AuditEvent(
            event_type="user_action",
            user_id="test-user-123",
            action="create_strategy",
            resource_type="strategy",
            resource_id="strategy-456",
            ip_address="example.local",
            user_agent="Mozilla/5.0 (Test Browser)",
            status="success",
            details={"strategy_name": "Test Strategy", "strategy_type": "momentum"},
        )

        # 记录审计事件
        await audit_manager.log_audit_event(event)

        # 等待事件被处理
        await asyncio.sleep(0.1)

        # 验证事件已记录到数据库
        assert len(mock_conn.executed_queries) > 0, "审计事件未记录到数据库"

        # 查询审计日志
        logs = await audit_manager.get_audit_logs(user_id="test-user-123", limit=10)

        assert len(logs) > 0, "未查询到审计日志"
        assert logs[0]["action"] == "login", "审计日志内容不正确"

        # 测试清理旧日志
        deleted_count = await audit_manager.cleanup_old_audit_logs(days_to_keep=30)
        assert deleted_count >= 0, "清理审计日志失败"

        logger.info("✅ 审计管理器测试通过")

    finally:
        # 停止审计工作进程
        await audit_manager.stop_audit_worker()


async def test_security_monitor():
    """测试安全监控器"""
    logger.info("🧪 测试安全监控器...")

    # 创建模拟审计管理器
    mock_audit_manager = MagicMock()

    # 创建安全监控器
    security_monitor = SecurityMonitor(mock_audit_manager)

    # 测试失败登录记录
    security_monitor.record_failed_login(ip_address="example.local", username="testuser")

    # 记录多次失败登录
    for _ in range(4):
        security_monitor.record_failed_login(ip_address="example.local", username="testuser")

    # 记录可疑活动
    security_monitor.record_suspicious_activity(
        activity_type="unusual_trading_pattern",
        details={"symbol": "AAPL", "volume": 1000000, "frequency": "high"},
        ip_address="example.local",
        user_id="test-user-123",
    )

    # 获取安全报告
    report = security_monitor.get_security_report()

    # 验证报告内容
    assert "failed_login_attempts" in report, "安全报告缺少失败登录信息"
    assert "example.local" in report["failed_login_attempts"], "未记录失败登录IP"
    assert report["failed_login_attempts"]["example.local"] >= 5, "失败登录次数记录不正确"

    assert "suspicious_activities" in report, "安全报告缺少可疑活动信息"
    assert len(report["suspicious_activities"]) >= 2, "可疑活动记录不完整"  # 暴力破解 + 异常交易

    assert "total_suspicious_events" in report, "安全报告缺少事件总数"
    assert report["total_suspicious_events"] >= 2, "可疑事件总数不正确"

    logger.info("✅ 安全监控器测试通过")


async def test_singleton_instances():
    """测试单例模式实例"""
    logger.info("🧪 测试单例模式实例...")

    # 测试日志记录器单例
    logger1 = get_structured_logger()
    logger2 = get_structured_logger()
    assert logger1 is logger2, "日志记录器单例模式失败"

    # 测试审计管理器单例
    audit_mgr1 = get_audit_manager()
    audit_mgr2 = get_audit_manager()
    assert audit_mgr1 is audit_mgr2, "审计管理器单例模式失败"

    # 测试安全监控器单例
    sec_mon1 = get_security_monitor()
    sec_mon2 = get_security_monitor()
    assert sec_mon1 is sec_mon2, "安全监控器单例模式失败"

    logger.info("✅ 单例模式实例测试通过")


async def test_context_variables():
    """测试上下文变量"""
    logger.info("🧪 测试上下文变量...")

    from src.infrastructure.logging.audit_system import request_id_var, session_id_var, user_id_var

    # 设置上下文变量
    request_token = request_id_var.set("test-request-123")
    user_token = user_id_var.set("test-user-456")
    session_token = session_id_var.set("test-session-789")

    try:
        # 验证上下文变量
        assert request_id_var.get() == "test-request-123", "请求ID上下文变量设置失败"
        assert user_id_var.get() == "test-user-456", "用户ID上下文变量设置失败"
        assert session_id_var.get() == "test-session-789", "会话ID上下文变量设置失败"

        # 测试在协程中的继承
        async def test_context_inheritance():
            # 子协程应该继承父协程的上下文
            assert request_id_var.get() == "test-request-123", "上下文变量未正确继承"
            return True

        result = await test_context_inheritance()
        assert result, "上下文变量继承测试失败"

    finally:
        # 清理上下文变量
        request_id_var.reset(request_token)
        user_id_var.reset(user_token)
        session_id_var.reset(session_token)

    logger.info("✅ 上下文变量测试通过")


async def run_all_tests():
    """运行所有测试"""
    logger.info("🚀 运行日志和审计系统完整测试套件...")

    results = []

    # 测试1: 结构化日志记录器
    logger.info("\n" + "=" * 50)
    logger.info("TEST 1: 结构化日志记录器")
    logger.info("=" * 50)
    result1 = await test_structured_logger()
    results.append(("Structured Logger", result1))

    # 测试2: 审计管理器
    logger.info("\n" + "=" * 50)
    logger.info("TEST 2: 审计管理器")
    logger.info("=" * 50)
    result2 = await test_audit_manager()
    results.append(("Audit Manager", result2))

    # 测试3: 安全监控器
    logger.info("\n" + "=" * 50)
    logger.info("TEST 3: 安全监控器")
    logger.info("=" * 50)
    result3 = await test_security_monitor()
    results.append(("Security Monitor", result3))

    # 测试4: 单例模式实例
    logger.info("\n" + "=" * 50)
    logger.info("TEST 4: 单例模式实例")
    logger.info("=" * 50)
    result4 = await test_singleton_instances()
    results.append(("Singleton Instances", result4))

    # 测试5: 上下文变量
    logger.info("\n" + "=" * 50)
    logger.info("TEST 5: 上下文变量")
    logger.info("=" * 50)
    result5 = await test_context_variables()
    results.append(("Context Variables", result5))

    # 总结
    logger.info("\n" + "=" * 50)
    logger.info("📊 测试结果汇总")
    logger.info("=" * 50)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info("%s: %s", test_name, status)
        if success:
            passed += 1

    logger.info("总体: %d/%d 测试通过", passed, total)

    if passed == total:
        logger.info("🎉 所有测试通过! 日志和审计系统已准备就绪。")
        logger.info("系统提供结构化日志记录、审计追踪、安全监控等企业级功能。")
        return True
    logger.warning("⚠️ 某些测试失败。请检查实现。")
    return False


if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # 运行测试
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
