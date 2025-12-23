#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
契约验证器
负责验证契约测试配置、测试用例和测试数据的合法性
"""

import json
import logging
import re
from typing import Dict, List, Any
from datetime import datetime
from urllib.parse import urlparse

from .models import (
    ContractTestSuite,
    ContractTestCase,
    ContractTestConfig,
    TestCategory,
)

logger = logging.getLogger(__name__)


class ContractValidationResult:
    """契约验证结果"""

    def __init__(self, valid: bool = True):
        self.valid = valid
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.infos: List[str] = []

    def add_error(self, message: str):
        """添加错误信息"""
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str):
        """添加警告信息"""
        self.warnings.append(message)

    def add_info(self, message: str):
        """添加信息"""
        self.infos.append(message)

    def is_valid(self) -> bool:
        """验证是否通过"""
        return self.valid


class ContractValidator:
    """契约验证器"""

    def __init__(self, config: ContractTestConfig):
        self.config = config
        self._validate_config()

    def _validate_config(self):
        """验证配置"""
        result = ContractValidationResult()

        # 验证 API URL
        if not self.config.api_base_url:
            result.add_error("API 基础 URL 不能为空")

        try:
            parsed = urlparse(self.config.api_base_url)
            if not parsed.scheme or not parsed.netloc:
                result.add_error("API 基础 URL 格式不正确")
        except Exception as e:
            result.add_error(f"API 基础 URL 解析失败: {e}")

        # 验证超时配置
        if self.config.test_timeout <= 0:
            result.add_error("测试超时时间必须大于 0")

        if self.config.max_retries < 0:
            result.add_error("最大重试次数不能为负数")

        if self.config.retry_delay < 0:
            result.add_error("重试延迟不能为负数")

        # 验证性能阈值
        if self.config.performance_threshold.get("response_time_ms", 0) <= 0:
            result.add_warning("响应时间阈值应大于 0")

        if self.config.performance_threshold.get("cpu_usage_percent", 0) <= 0:
            result.add_warning("CPU 使用率阈值应大于 0")

        if not result.is_valid():
            logger.error(f"配置验证失败: {result.errors}")

    def validate_suite(self, suite: ContractTestSuite) -> ContractValidationResult:
        """验证测试套件"""
        result = ContractValidationResult()

        # 基础信息验证
        if not suite.name:
            result.add_error("测试套件名称不能为空")

        if not suite.test_cases:
            result.add_warning("测试套件没有测试用例")

        # 验证测试用例
        for i, test_case in enumerate(suite.test_cases):
            case_result = self.validate_test_case(test_case)
            if not case_result.is_valid():
                result.add_error(f"测试用例 {i + 1} ({test_case.name}) 验证失败:")
                for error in case_result.errors:
                    result.add_error(f"  - {error}")

        # 验证并行执行配置
        if suite.parallel_execution and suite.max_workers <= 0:
            result.add_error("并行执行时最大工作线程数必须大于 0")

        # 套件统计
        if result.is_valid():
            result.add_info(
                f"测试套件验证通过: {suite.name} ({len(suite.test_cases)} 个测试用例)"
            )
        else:
            logger.error(f"测试套件 {suite.name} 验证失败")

        return result

    def validate_test_case(
        self, test_case: ContractTestCase
    ) -> ContractValidationResult:
        """验证测试用例"""
        result = ContractValidationResult()

        # 基础信息验证
        if not test_case.name:
            result.add_error("测试用例名称不能为空")

        if not test_case.endpoint:
            result.add_error("测试用例端点不能为空")

        # HTTP 方法验证
        valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        if test_case.method.upper() not in valid_methods:
            result.add_error(
                f"HTTP 方法 '{test_case.method}' 无效，必须是: {', '.join(valid_methods)}"
            )

        # 端点格式验证
        endpoint_result = self._validate_endpoint(test_case.endpoint)
        if not endpoint_result.is_valid():
            result.add_error(f"端点格式验证失败: {endpoint_result.errors}")

        # 请求参数验证
        if test_case.params:
            param_result = self._validate_params(test_case.params)
            if not param_result.is_valid():
                result.errors.extend(param_result.errors)

        # 请求体验证
        if test_case.body:
            body_result = self._validate_request_body(test_case.body, test_case.method)
            if not body_result.is_valid():
                result.errors.extend(body_result.errors)

        # 验证规则验证
        if test_case.validation_rules:
            rule_result = self._validate_validation_rules(test_case.validation_rules)
            if not rule_result.is_valid():
                result.errors.extend(rule_result.errors)

        # JWT 相关验证
        if test_case.category == TestCategory.AUTHENTICATION:
            auth_result = self._validate_authentication_case(test_case)
            if not auth_result.is_valid():
                result.errors.extend(auth_result.errors)

        # 性能相关验证
        if test_case.category == TestCategory.PERFORMANCE:
            perf_result = self._validate_performance_case(test_case)
            if not perf_result.is_valid():
                result.errors.extend(perf_result.errors)

        # 标签验证
        if test_case.tags:
            for tag in test_case.tags:
                if not re.match(r"^[a-zA-Z0-9_-]+$", tag):
                    result.add_error(
                        f"标签 '{tag}' 包含非法字符，只能使用字母、数字、下划线和连字符"
                    )

        # 优先级验证
        if not (1 <= test_case.priority <= 10):
            result.add_error(f"优先级 {test_case.priority} 必须在 1-10 之间")

        return result

    def _validate_endpoint(self, endpoint: str) -> ContractValidationResult:
        """验证端点格式"""
        result = ContractValidationResult()

        if not endpoint.startswith("/"):
            result.add_error("端点必须以 '/' 开头")

        # 验证端点中的变量
        if "{" in endpoint or "}" in endpoint:
            variables = re.findall(r"\{([^}]+)\}", endpoint)
            for var in variables:
                if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", var):
                    result.add_error(f"端点变量 '{var}' 格式不正确")

        # 检查常见错误
        if "//" in endpoint:
            result.add_warning("端点中包含连续的斜杠 '//'")

        return result

    def _validate_params(self, params: Dict[str, Any]) -> ContractValidationResult:
        """验证请求参数"""
        result = ContractValidationResult()

        for key, value in params.items():
            # 参数名验证
            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", key):
                result.add_error(f"参数名 '{key}' 格式不正确")

            # 参数值验证
            if value is not None:
                if isinstance(value, str):
                    # 长度限制
                    if len(value) > 1000:
                        result.add_warning(f"参数 '{key}' 值过长 ({len(value)} 字符)")

                    # 检查潜在的 SQL 注入
                    sql_keywords = [
                        "select",
                        "insert",
                        "update",
                        "delete",
                        "drop",
                        "union",
                        "script",
                    ]
                    if any(keyword in value.lower() for keyword in sql_keywords):
                        result.add_warning(f"参数 '{key}' 值可能包含 SQL 注入风险")

                elif isinstance(value, (int, float)):
                    # 数值范围检查
                    if isinstance(value, int) and abs(value) > 2**31:
                        result.add_warning(f"参数 '{key}' 数值过大 ({value})")

                elif isinstance(value, list):
                    # 列表长度检查
                    if len(value) > 100:
                        result.add_warning(f"参数 '{key}' 列表过长 ({len(value)} 项)")

        return result

    def _validate_request_body(
        self, body: Dict[str, Any], method: str
    ) -> ContractValidationResult:
        """验证请求体"""
        result = ContractValidationResult()

        # 只有 POST、PUT、PATCH 方法可以有请求体
        if method.upper() not in ["POST", "PUT", "PATCH"]:
            result.add_error(f"HTTP 方法 '{method}' 不应该有请求体")

        # 递归验证请求体结构
        self._validate_object_structure(body, "body", result)

        return result

    def _validate_object_structure(
        self, obj: Any, path: str, result: ContractValidationResult
    ):
        """递归验证对象结构"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", key):
                    result.add_error(f"对象键 '{key}' 格式不正确 (路径: {path})")

                # 递归验证嵌套对象
                nested_path = f"{path}.{key}" if path else key
                self._validate_object_structure(value, nested_path, result)

        elif isinstance(obj, list):
            if len(obj) > 1000:
                result.add_warning(f"数组过长 ({len(obj)} 项) (路径: {path})")

            # 验证数组元素
            for i, item in enumerate(obj):
                item_path = f"{path}[{i}]"
                self._validate_object_structure(item, item_path, result)

    def _validate_validation_rules(
        self, rules: List[Dict[str, Any]]
    ) -> ContractValidationResult:
        """验证验证规则"""
        result = ContractValidationResult()

        valid_rule_types = [
            "status_code",
            "schema",
            "response_time",
            "headers",
            "jwt_token",
            "csrf_token",
            "composite",
        ]

        for i, rule in enumerate(rules):
            rule_type = rule.get("type")

            if not rule_type:
                result.add_error(f"规则 {i + 1} 缺少类型")

            if rule_type not in valid_rule_types:
                result.add_error(f"规则 {i + 1} 的类型 '{rule_type}' 无效")

            # 验证特定规则类型
            if rule_type == "status_code":
                expected = rule.get("expected")
                if expected is None or not isinstance(expected, int):
                    result.add_error(f"规则 {i + 1} 的 expected 值无效")

            elif rule_type == "schema":
                schema = rule.get("schema")
                if not isinstance(schema, dict):
                    result.add_error(f"规则 {i + 1} 的 schema 必须是对象")

            elif rule_type == "response_time":
                max_ms = rule.get("max_ms")
                if max_ms is None or not isinstance(max_ms, (int, float)):
                    result.add_error(f"规则 {i + 1} 的 max_ms 值无效")

            elif rule_type == "headers":
                headers = rule.get("expected_headers")
                if headers is None or not isinstance(headers, dict):
                    result.add_error(f"规则 {i + 1} 的 expected_headers 必须是对象")

        return result

    def _validate_authentication_case(
        self, test_case: ContractTestCase
    ) -> ContractValidationResult:
        """验证认证相关测试用例"""
        result = ContractValidationResult()

        # 检查是否包含必要的认证头
        if not test_case.headers:
            result.add_warning("认证测试通常需要包含认证头")

        # 检查 JWT 验证规则
        jwt_rules = [
            rule
            for rule in test_case.validation_rules
            if rule.get("type") == "jwt_token"
        ]

        if jwt_rules and test_case.method.upper() == "GET":
            result.add_warning("JWT 验证通常用于需要认证的请求")

        # 检查登录测试的特殊要求
        if "/login" in test_case.endpoint:
            body = test_case.body or {}
            if "username" not in body:
                result.add_warning("登录测试应该包含 username 字段")

            if "password" not in body:
                result.add_warning("登录测试应该包含 password 字段")

        return result

    def _validate_performance_case(
        self, test_case: ContractTestCase
    ) -> ContractValidationResult:
        """验证性能相关测试用例"""
        result = ContractValidationResult()

        # 检查性能验证规则
        perf_rules = [
            rule
            for rule in test_case.validation_rules
            if rule.get("type") == "response_time"
        ]

        if not perf_rules:
            result.add_warning("性能测试应该包含响应时间验证规则")

        # 检查并发测试配置
        if test_case.params.get("concurrency"):
            concurrency = test_case.params["concurrency"]
            if not isinstance(concurrency, int) or concurrency <= 0:
                result.add_error("并发数必须是正整数")

        return result

    def validate_response_data(
        self, response: Dict[str, Any], test_case: ContractTestCase
    ) -> ContractValidationResult:
        """验证响应数据"""
        result = ContractValidationResult()

        # 检查响应基本结构
        if not isinstance(response, dict):
            result.add_error("响应必须是对象")
            return result

        # 检查成功响应格式
        if test_case.expected_status == 200:
            if "success" not in response:
                result.add_warning("成功响应应该包含 success 字段")

            if "data" not in response:
                result.add_warning("成功响应应该包含 data 字段")

        # 检查错误响应格式
        if test_case.expected_status >= 400:
            if "error" not in response:
                result.add_warning("错误响应应该包含 error 字段")

            if "message" not in response:
                result.add_warning("错误响应应该包含 message 字段")

        # 检查时间戳
        if "timestamp" in response:
            try:
                timestamp = response["timestamp"]
                if isinstance(timestamp, str):
                    datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                elif isinstance(timestamp, (int, float)):
                    # Unix timestamp
                    datetime.fromtimestamp(timestamp)
            except (ValueError, TypeError):
                result.add_warning("timestamp 字段格式不正确")

        # 检查请求 ID
        if "request_id" in response:
            request_id = response["request_id"]
            if not isinstance(request_id, str) or len(request_id) < 8:
                result.add_warning("request_id 应该是有效的字符串")

        # 应用验证规则
        for rule in test_case.validation_rules:
            rule_result = self._apply_validation_rule(response, rule)
            if not rule_result.is_valid():
                result.errors.extend(rule_result.errors)

        return result

    def _apply_validation_rule(
        self, response: Dict[str, Any], rule: Dict[str, Any]
    ) -> ContractValidationResult:
        """应用验证规则"""
        result = ContractValidationResult()
        rule_type = rule.get("type")

        try:
            if rule_type == "status_code":
                expected = rule.get("expected")
                actual = response.get("status_code")  # 假设响应包含状态码
                if actual != expected:
                    result.add_error(f"状态码验证失败: 期望 {expected}, 实际 {actual}")

            elif rule_type == "schema":
                schema = rule.get("schema")
                if not self._validate_schema(response, schema):
                    result.add_error("模式验证失败")

            elif rule_type == "response_time":
                max_ms = rule.get("max_ms")
                # 假设响应包含响应时间信息
                response_time = response.get("response_time_ms")
                if response_time and response_time > max_ms:
                    result.add_error(f"响应时间过长: {response_time}ms > {max_ms}ms")

            elif rule_type == "headers":
                expected_headers = rule.get("expected_headers")
                for key, expected_value in expected_headers.items():
                    actual_value = response.get(key)
                    if actual_value != expected_value:
                        result.add_error(
                            f"头部验证失败 {key}: 期望 {expected_value}, 实际 {actual_value}"
                        )

            elif rule_type == "jwt_token":
                # JWT 验证逻辑
                if rule.get("check_expiry"):
                    token = response.get("token")
                    if token:
                        if self._is_jwt_expired(token):
                            result.add_error("JWT token 已过期")

            elif rule_type == "composite":
                # 复合规则
                sub_rules = rule.get("rules", [])
                for sub_rule in sub_rules:
                    sub_result = self._apply_validation_rule(response, sub_rule)
                    if not sub_result.is_valid():
                        result.errors.extend(sub_result.errors)

        except Exception as e:
            result.add_error(f"验证规则执行失败: {e}")

        return result

    def _validate_schema(self, data: Any, schema: Dict[str, Any]) -> bool:
        """验证数据是否符合模式"""
        try:
            if schema.get("type") == "object":
                properties = schema.get("properties", {})
                if not isinstance(data, dict):
                    return False

                for key, prop_schema in properties.items():
                    if key not in data:
                        if prop_schema.get("required", False):
                            return False
                        continue

                    if not self._validate_schema(data[key], prop_schema):
                        return False

            elif schema.get("type") == "array":
                items = schema.get("items", {})
                if not isinstance(data, list):
                    return False

                for item in data:
                    if not self._validate_schema(item, items):
                        return False

            elif schema.get("type") == "string":
                if not isinstance(data, str):
                    return False

            elif schema.get("type") == "integer":
                if not isinstance(data, int):
                    return False

            elif schema.get("type") == "number":
                if not isinstance(data, (int, float)):
                    return False

            elif schema.get("type") == "boolean":
                if not isinstance(data, bool):
                    return False

            return True

        except Exception:
            return False

    def _is_jwt_expired(self, token: str) -> bool:
        """检查 JWT token 是否过期"""
        try:
            # 简化的 JWT 验证
            parts = token.split(".")
            if len(parts) != 3:
                return True

            # 解码 payload（不验证签名）
            import base64

            payload = json.loads(
                base64.urlsafe_b64decode(parts[1] + "=" * (4 - len(parts[1]) % 4))
            )
            exp = payload.get("exp")

            if exp:
                import time

                return exp < time.time()

            return False

        except Exception:
            return True
