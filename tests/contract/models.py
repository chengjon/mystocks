#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
契约测试数据模型
定义契约测试的配置、套件和用例模型
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime
import uuid


class TestCategory(Enum):
    """测试类别枚举"""

    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    BUSINESS_LOGIC = "business_logic"
    INTEGRATION = "integration"
    SECURITY = "security"
    PERFORMANCE = "performance"
    ERROR_HANDLING = "error_handling"


class ContractType(Enum):
    """契约类型枚举"""

    OPENAPI = "openapi"
    INTERFACE = "interface"
    DATA_SCHEMA = "data_schema"
    BEHAVIORAL = "behavioral"


class TestStatus(Enum):
    """测试状态枚举"""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class ContractTestConfig:
    """契约测试配置"""

    # 基础配置
    api_base_url: str = "http://localhost:8000"
    openapi_spec_path: Optional[str] = None
    contract_version: str = "1.0.0"

    # 测试配置
    test_timeout: int = 30  # 秒
    max_retries: int = 3
    retry_delay: int = 1

    # 安全配置
    enable_security_tests: bool = True
    enable_auth_tests: bool = True

    # 性能配置
    performance_threshold: Dict[str, float] = field(
        default_factory=lambda: {
            "response_time_ms": 1000,
            "cpu_usage_percent": 80,
            "memory_usage_mb": 512,
        }
    )

    # 数据配置
    test_data_path: str = "tests/contract/test_data"
    mock_data_enabled: bool = True

    # 报告配置
    report_format: str = "json"
    report_output_path: str = "reports/contract"

    # 集成配置
    database_connection: Optional[Dict[str, str]] = None
    external_apis: Dict[str, str] = field(default_factory=dict)


@dataclass
class ContractTestCase:
    """契约测试用例"""

    # 基础信息
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    category: TestCategory = TestCategory.VALIDATION
    contract_type: ContractType = ContractType.OPENAPI

    # 测试数据
    endpoint: str = ""
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    body: Optional[Dict[str, Any]] = None
    expected_status: int = 200

    # 预期结果
    expected_response: Dict[str, Any] = field(default_factory=dict)
    expected_error: Optional[Dict[str, Any]] = None

    # 验证规则
    validation_rules: List[Dict[str, Any]] = field(default_factory=list)

    # 元数据
    tags: List[str] = field(default_factory=list)
    priority: int = 1
    enabled: bool = True
    skip_conditions: List[str] = field(default_factory=list)

    # 执行信息
    status: TestStatus = TestStatus.PENDING
    duration: float = 0.0
    error_message: Optional[str] = None
    request_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ContractTestSuite:
    """契约测试套件"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""

    # 测试用例
    test_cases: List[ContractTestCase] = field(default_factory=list)

    # 套件配置
    config: ContractTestConfig = field(default_factory=ContractTestConfig)

    # 执行配置
    parallel_execution: bool = False
    max_workers: int = 4
    stop_on_failure: bool = False

    # 元数据
    tags: List[str] = field(default_factory=list)
    owner: str = ""
    version: str = "1.0.0"

    # 执行结果
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: TestStatus = TestStatus.PENDING
    total_cases: int = 0
    passed_cases: int = 0
    failed_cases: int = 0
    skipped_cases: int = 0
    error_cases: int = 0
    total_duration: float = 0.0


@dataclass
class TestExecutionResult:
    """测试执行结果"""

    test_case: ContractTestCase
    status: TestStatus
    duration: float
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    validation_results: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContractTestReport:
    """契约测试报告"""

    suite: ContractTestSuite
    results: List[TestExecutionResult]
    summary: Dict[str, Any] = field(default_factory=dict)

    # 报告元数据
    generated_at: datetime = field(default_factory=datetime.now)
    report_version: str = "1.0.0"

    # 统计信息
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    error_tests: int = 0
    success_rate: float = 0.0

    # 详细统计
    category_stats: Dict[str, Dict[str, int]] = field(default_factory=dict)
    performance_stats: Dict[str, Dict[str, float]] = field(default_factory=dict)

    # 建议
    recommendations: List[str] = field(default_factory=list)


# 验证规则工厂
class ValidationRuleFactory:
    """验证规则工厂"""

    @staticmethod
    def create_status_code_rule(expected_status: int) -> Dict[str, Any]:
        """创建状态码验证规则"""
        return {
            "type": "status_code",
            "expected": expected_status,
            "operator": "equals",
        }

    @staticmethod
    def create_schema_validation_rule(schema: Dict[str, Any]) -> Dict[str, Any]:
        """创建模式验证规则"""
        return {"type": "schema", "schema": schema}

    @staticmethod
    def create_response_time_rule(max_ms: int) -> Dict[str, Any]:
        """创建响应时间验证规则"""
        return {"type": "response_time", "max_ms": max_ms, "operator": "less_than"}

    @staticmethod
    def create_header_validation_rule(headers: Dict[str, str]) -> Dict[str, Any]:
        """创建头部验证规则"""
        return {"type": "headers", "expected_headers": headers}

    @staticmethod
    def create_jwt_validation_rule() -> Dict[str, Any]:
        """创建JWT验证规则"""
        return {"type": "jwt_token", "check_expiry": True, "check_signature": True}

    @staticmethod
    def create_csrf_validation_rule() -> Dict[str, Any]:
        """创建CSRF验证规则"""
        return {"type": "csrf_token", "check_header": True, "check_cookie": True}
