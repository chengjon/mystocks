#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
契约测试引擎
负责发现、解析和执行契约测试的核心组件
"""

import json
import logging
import yaml
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import asdict

from .models import (
    ContractTestSuite,
    ContractTestCase,
    ContractTestConfig,
    TestCategory,
    ContractType,
    TestStatus,
)
from .contract_validator import ContractValidator
from .test_executor import ContractTestExecutor

logger = logging.getLogger(__name__)


class ContractTestEngine:
    """契约测试引擎"""

    def __init__(self, config: Optional[ContractTestConfig] = None):
        self.config = config or ContractTestConfig()
        self.validator = ContractValidator(self.config)
        self.executor = ContractTestExecutor(self.config)
        self.test_suites: Dict[str, ContractTestSuite] = {}

        # 初始化
        self._initialize()

    def _initialize(self):
        """初始化引擎"""
        logger.info("初始化契约测试引擎")

        # 创建测试数据目录
        test_data_dir = Path(self.config.test_data_path)
        test_data_dir.mkdir(parents=True, exist_ok=True)

        # 创建报告目录
        report_dir = Path(self.config.report_output_path)
        report_dir.mkdir(parents=True, exist_ok=True)

        # 加载 OpenAPI 规范
        if self.config.openapi_spec_path:
            self._load_openapi_spec()

    def _load_openapi_spec(self):
        """加载 OpenAPI 规范"""
        try:
            spec_path = Path(self.config.openapi_spec_path)
            if spec_path.exists():
                with open(spec_path, "r", encoding="utf-8") as f:
                    if spec_path.suffix.lower() == ".json":
                        self.openapi_spec = json.load(f)
                    else:
                        self.openapi_spec = yaml.safe_load(f)
                logger.info(f"成功加载 OpenAPI 规范: {spec_path}")
            else:
                logger.warning(f"OpenAPI 规范文件不存在: {spec_path}")
        except Exception as e:
            logger.error(f"加载 OpenAPI 规范失败: {e}")

    def discover_tests_from_openapi(self) -> List[ContractTestCase]:
        """从 OpenAPI 规范发现测试用例"""
        test_cases = []

        if not hasattr(self, "openapi_spec"):
            logger.warning("OpenAPI 规范未加载，无法自动发现测试用例")
            return test_cases

        try:
            paths = self.openapi_spec.get("paths", {})
            for path, path_item in paths.items():
                for method, operation in path_item.items():
                    if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                        test_case = self._create_test_case_from_operation(
                            path, method, operation
                        )
                        if test_case:
                            test_cases.append(test_case)

            logger.info(f"从 OpenAPI 规范自动发现 {len(test_cases)} 个测试用例")
        except Exception as e:
            logger.error(f"从 OpenAPI 规范发现测试用例失败: {e}")

        return test_cases

    def _create_test_case_from_operation(
        self, path: str, method: str, operation: Dict
    ) -> Optional[ContractTestCase]:
        """从 OpenAPI 操作创建测试用例"""
        try:
            # 基本信息
            test_case = ContractTestCase(
                name=f"{method.upper()} {path}",
                description=operation.get("description", ""),
                endpoint=path,
                method=method.upper(),
                category=self._determine_category(path, method),
                contract_type=ContractType.OPENAPI,
            )

            # 解析参数
            parameters = operation.get("parameters", [])
            for param in parameters:
                if param.get("in") == "query":
                    test_case.params[param["name"]] = param.get("default", "")
                elif param.get("in") == "header":
                    test_case.headers[param["name"]] = param.get("default", "")

            # 解析请求体
            if "requestBody" in operation:
                request_body = operation["requestBody"]
                content = request_body.get("content", {})
                if "application/json" in content:
                    schema = content["application/json"].get("schema", {})
                    test_case.body = self._generate_mock_data_from_schema(schema)

            # 解析响应
            responses = operation.get("responses", {})
            if "200" in responses:
                success_response = responses["200"]
                content = success_response.get("content", {})
                if "application/json" in content:
                    schema = content["application/json"].get("schema", {})
                    test_case.expected_response = self._generate_mock_data_from_schema(
                        schema
                    )

            # 设置验证规则
            test_case.validation_rules = [
                self._create_validation_rule_from_spec(path, method)
            ]

            return test_case

        except Exception as e:
            logger.error(f"创建测试用例失败: {e}")
            return None

    def _determine_category(self, path: str, method: str) -> TestCategory:
        """根据路径和方法确定测试类别"""
        if "/auth" in path or "/login" in path or "/register" in path:
            return TestCategory.AUTHENTICATION
        elif "/market" in path or "/data" in path:
            return TestCategory.BUSINESS_LOGIC
        elif "/admin" in path or "/system" in path:
            return TestCategory.SECURITY
        else:
            return TestCategory.VALIDATION

    def _create_validation_rule_from_spec(
        self, path: str, method: str
    ) -> Dict[str, Any]:
        """从规范创建验证规则"""
        from .models import ValidationRuleFactory

        rules = []

        # 基本状态码验证
        rules.append(ValidationRuleFactory.create_status_code_rule(200))

        # 响应时间验证
        if path.startswith("/api/market"):
            rules.append(ValidationRuleFactory.create_response_time_rule(2000))
        else:
            rules.append(ValidationRuleFactory.create_response_time_rule(1000))

        # JWT 验证（如果是受保护的端点）
        if self.config.enable_auth_tests and any(
            auth_path in path for auth_path in ["/api/", "/auth/", "/admin/"]
        ):
            rules.append(ValidationRuleFactory.create_jwt_validation_rule())

        return {"type": "composite", "rules": rules}

    def _generate_mock_data_from_schema(self, schema: Dict) -> Dict[str, Any]:
        """从模式生成模拟数据"""
        mock_data = {}

        def generate_mock_for_type(prop_schema: Dict) -> Any:
            prop_type = prop_schema.get("type")

            if prop_type == "string":
                format_type = prop_schema.get("format")
                if format_type == "date-time":
                    return "2024-12-12T00:00:00Z"
                elif format_type == "date":
                    return "2024-12-12"
                else:
                    return "mock_string"

            elif prop_type == "integer":
                return 1

            elif prop_type == "number":
                return 1.0

            elif prop_type == "boolean":
                return True

            elif prop_type == "array":
                items = prop_schema.get("items", {})
                return [generate_mock_for_type(items)]

            elif prop_type == "object":
                properties = prop_schema.get("properties", {})
                result = {}
                for key, prop_schema in properties.items():
                    result[key] = generate_mock_for_type(prop_schema)
                return result

            return None

        properties = schema.get("properties", {})
        for key, prop_schema in properties.items():
            mock_data[key] = generate_mock_for_type(prop_schema)

        return mock_data

    def load_test_suite_from_file(self, file_path: str) -> Optional[ContractTestSuite]:
        """从文件加载测试套件"""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"测试套件文件不存在: {file_path}")
                return None

            with open(path, "r", encoding="utf-8") as f:
                if path.suffix.lower() == ".json":
                    data = json.load(f)
                else:
                    data = yaml.safe_load(f)

            suite = ContractTestSuite(
                id=data.get("id", ""),
                name=data.get("name", ""),
                description=data.get("description", ""),
            )

            # 加载测试用例
            for case_data in data.get("test_cases", []):
                test_case = ContractTestCase(
                    id=case_data.get("id", ""),
                    name=case_data.get("name", ""),
                    description=case_data.get("description", ""),
                    endpoint=case_data.get("endpoint", ""),
                    method=case_data.get("method", "GET"),
                    category=TestCategory(case_data.get("category", "validation")),
                    contract_type=ContractType(
                        case_data.get("contract_type", "openapi")
                    ),
                    expected_status=case_data.get("expected_status", 200),
                    headers=case_data.get("headers", {}),
                    params=case_data.get("params", {}),
                    body=case_data.get("body"),
                    expected_response=case_data.get("expected_response", {}),
                    validation_rules=case_data.get("validation_rules", []),
                    tags=case_data.get("tags", []),
                    priority=case_data.get("priority", 1),
                    enabled=case_data.get("enabled", True),
                )
                suite.test_cases.append(test_case)

            logger.info(
                f"成功加载测试套件: {suite.name} ({len(suite.test_cases)} 个测试用例)"
            )
            return suite

        except Exception as e:
            logger.error(f"加载测试套件失败: {e}")
            return None

    def save_test_suite_to_file(self, suite: ContractTestSuite, file_path: str):
        """保存测试套件到文件"""
        try:
            # 转换为字典
            suite_dict = asdict(suite)
            # 移除不可序列化的字段
            suite_dict.pop("start_time", None)
            suite_dict.pop("end_time", None)

            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                if path.suffix.lower() == ".json":
                    json.dump(suite_dict, f, ensure_ascii=False, indent=2)
                else:
                    yaml.dump(
                        suite_dict, f, default_flow_style=False, allow_unicode=True
                    )

            logger.info(f"保存测试套件成功: {file_path}")

        except Exception as e:
            logger.error(f"保存测试套件失败: {e}")

    def create_default_suite(self) -> ContractTestSuite:
        """创建默认测试套件"""
        suite = ContractTestSuite(
            name="MyStocks API 契约测试",
            description="MyStocks 平台 API 契约测试套件",
            config=self.config,
            parallel_execution=True,
            max_workers=4,
            stop_on_failure=False,
            tags=["api", "contract", "my-stocks"],
        )

        # 添加基础测试用例
        suite.test_cases.extend(self._create_default_test_cases())

        return suite

    def _create_default_test_cases(self) -> List[ContractTestCase]:
        """创建默认测试用例"""
        test_cases = []

        # 健康检查测试
        health_case = ContractTestCase(
            name="健康检查",
            description="验证 API 健康检查端点",
            endpoint="/api/health",
            method="GET",
            category=TestCategory.VALIDATION,
            contract_type=ContractType.OPENAPI,
            expected_status=200,
            expected_response={"status": "healthy"},
            validation_rules=[
                {
                    "type": "composite",
                    "rules": [
                        self._create_validation_rule_from_spec("/api/health", "GET")
                    ],
                }
            ],
        )
        test_cases.append(health_case)

        # 认证测试
        auth_case = ContractTestCase(
            name="用户登录",
            description="验证用户登录功能",
            endpoint="/api/v1/auth/login",
            method="POST",
            category=TestCategory.AUTHENTICATION,
            contract_type=ContractType.OPENAPI,
            expected_status=200,
            body={"username": "test_user", "password": "TestPassword123!"},
            validation_rules=[
                {
                    "type": "composite",
                    "rules": [
                        ValidationRuleFactory.create_status_code_rule(200),
                        ValidationRuleFactory.create_jwt_validation_rule(),
                        ValidationRuleFactory.create_response_time_rule(2000),
                    ],
                }
            ],
        )
        test_cases.append(auth_case)

        # 市场数据测试
        market_case = ContractTestCase(
            name="获取市场数据",
            description="验证市场数据获取功能",
            endpoint="/api/market/market-data/fetch",
            method="POST",
            category=TestCategory.BUSINESS_LOGIC,
            contract_type=ContractType.OPENAPI,
            expected_status=200,
            body={
                "symbols": ["600519", "600036"],
                "fields": ["price", "change", "volume"],
            },
            validation_rules=[
                {
                    "type": "composite",
                    "rules": [
                        ValidationRuleFactory.create_status_code_rule(200),
                        ValidationRuleFactory.create_response_time_rule(3000),
                        {
                            "type": "schema",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "data": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "symbol": {"type": "string"},
                                                "price": {"type": "number"},
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    ],
                }
            ],
        )
        test_cases.append(market_case)

        return test_cases

    async def execute_test_suite(self, suite: ContractTestSuite) -> ContractTestSuite:
        """执行测试套件"""
        logger.info(f"开始执行测试套件: {suite.name}")

        suite.start_time = datetime.now()
        suite.status = TestStatus.RUNNING
        suite.total_cases = len(suite.test_cases)

        try:
            # 验证测试套件
            validation_result = self.validator.validate_suite(suite)
            if not validation_result.valid:
                logger.error(f"测试套件验证失败: {validation_result.errors}")
                suite.status = TestStatus.ERROR
                return suite

            # 执行测试
            results = await self.executor.execute_suite(suite)

            # 更新套件状态
            suite.end_time = datetime.now()
            suite.total_duration = (suite.end_time - suite.start_time).total_seconds()

            # 统计结果
            suite.passed_cases = sum(
                1 for r in results if r.status == TestStatus.PASSED
            )
            suite.failed_cases = sum(
                1 for r in results if r.status == TestStatus.FAILED
            )
            suite.skipped_cases = sum(
                1 for r in results if r.status == TestStatus.SKIPPED
            )
            suite.error_cases = sum(1 for r in results if r.status == TestStatus.ERROR)

            if suite.failed_cases == 0 and suite.error_cases == 0:
                suite.status = TestStatus.PASSED
            else:
                suite.status = TestStatus.FAILED

            logger.info(f"测试套件执行完成: {suite.name}")
            logger.info(
                f"结果统计: {suite.passed_cases} 通过, {suite.failed_cases} 失败, "
                f"{suite.skipped_cases} 跳过, {suite.error_cases} 错误"
            )

        except Exception as e:
            logger.error(f"执行测试套件失败: {e}")
            suite.status = TestStatus.ERROR
            suite.end_time = datetime.now()
            suite.error_message = str(e)

        return suite

    async def discover_and_execute(self) -> Dict[str, ContractTestSuite]:
        """发现并执行所有契约测试"""
        logger.info("开始发现和执行所有契约测试")

        suites = {}

        # 1. 自动从 OpenAPI 规范发现测试
        openapi_tests = self.discover_tests_from_openapi()
        if openapi_tests:
            auto_suite = ContractTestSuite(
                name="自动发现的 API 测试",
                description="从 OpenAPI 规范自动生成的测试用例",
                test_cases=openapi_tests,
                config=self.config,
            )
            suites["openapi_auto"] = await self.execute_test_suite(auto_suite)

        # 2. 加载默认测试套件
        default_suite = self.create_default_suite()
        suites["default"] = await self.execute_test_suite(default_suite)

        # 3. 加载文件中的测试套件
        test_files = Path(self.config.test_data_path).glob("*.yaml")
        test_files = list(test_files) + list(
            Path(self.config.test_data_path).glob("*.json")
        )

        for test_file in test_files:
            suite = self.load_test_suite_from_file(str(test_file))
            if suite:
                suite_name = test_file.stem
                suites[suite_name] = await self.execute_test_suite(suite)

        logger.info(f"完成所有契约测试执行，共处理 {len(suites)} 个测试套件")
        return suites
