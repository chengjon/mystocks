"""
契约测试验证器

提供基于OpenAPI规范的API契约验证、一致性检查和冲突检测功能。
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin, urlparse

import httpx
import requests
import yaml
from jsonschema import SchemaError, ValidationError, validate

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContractViolationType(Enum):
    """契约违规类型枚举"""

    MISSING_ENDPOINT = "missing_endpoint"
    INVALID_REQUEST = "invalid_request"
    INVALID_RESPONSE = "invalid_response"
    SCHEMA_MISMATCH = "schema_mismatch"
    RESPONSE_STATUS_MISMATCH = "response_status_mismatch"
    RESPONSE_TIME_VIOLATION = "response_time_violation"
    SECURITY_VIOLATION = "security_violation"
    HEADER_MISMATCH = "header_mismatch"
    CONTENT_TYPE_MISMATCH = "content_type_mismatch"
    DEPRECATION_VIOLATION = "deprecation_violation"


class ValidationLevel(Enum):
    """验证级别枚举"""

    STRICT = "strict"
    WARNING = "warning"
    IGNORE = "ignore"


@dataclass
class ContractSpec:
    """契约规范"""

    name: str
    version: str
    openapi_spec: Dict[str, Any]
    base_url: str
    authentication: Dict[str, Any] = field(default_factory=dict)
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    custom_validators: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContractTest:
    """契约测试用例"""

    id: str
    name: str
    endpoint: str
    method: str
    request_data: Optional[Dict[str, Any]] = None
    expected_response: Optional[Dict[str, Any]] = None
    expected_status: int = 200
    expected_headers: Optional[Dict[str, str]] = None
    test_data: Optional[Dict[str, Any]] = None
    priority: str = "medium"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContractViolation:
    """契约违规"""

    violation_type: ContractViolationType
    severity: str
    message: str
    endpoint: str
    method: str
    expected: Any
    actual: Any
    suggestion: str
    location: str
    timestamp: datetime = field(default_factory=datetime.now)
    test_id: Optional[str] = None


@dataclass
class ValidationResult:
    """验证结果"""

    contract_spec: ContractSpec
    test_results: List[Dict[str, Any]]
    violations: List[ContractViolation]
    execution_time: float
    coverage_metrics: Dict[str, float]
    summary: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


class SchemaValidator:
    """模式验证器"""

    def __init__(self):
        self.compiled_schemas = {}

    def validate_request_schema(self, request_data: Dict[str, Any], schema: Dict[str, Any]) -> List[ContractViolation]:
        """验证请求模式"""
        violations = []
        try:
            validate(instance=request_data, schema=schema)
        except ValidationError as e:
            violations.append(
                ContractViolation(
                    violation_type=ContractViolationType.INVALID_REQUEST,
                    severity="error",
                    message=f"请求模式验证失败: {e.message}",
                    endpoint="N/A",
                    method="N/A",
                    expected=schema,
                    actual=request_data,
                    suggestion="请检查请求数据是否符合API契约定义的模式",
                    location="request.schema",
                    test_id="schema_validation",
                )
            )
        except SchemaError as e:
            violations.append(
                ContractViolation(
                    violation_type=ContractViolationType.SCHEMA_MISMATCH,
                    severity="error",
                    message=f"请求模式定义错误: {e.message}",
                    endpoint="N/A",
                    method="N/A",
                    expected=schema,
                    actual=request_data,
                    suggestion="请检查API契约中的模式定义",
                    location="request.schema.definition",
                    test_id="schema_definition",
                )
            )

        return violations

    def validate_response_schema(self, response_data: Any, schema: Dict[str, Any]) -> List[ContractViolation]:
        """验证响应模式"""
        violations = []
        try:
            validate(instance=response_data, schema=schema)
        except ValidationError as e:
            violations.append(
                ContractViolation(
                    violation_type=ContractViolationType.INVALID_RESPONSE,
                    severity="error",
                    message=f"响应模式验证失败: {e.message}",
                    endpoint="N/A",
                    method="N/A",
                    expected=schema,
                    actual=response_data,
                    suggestion="请检查响应数据是否符合API契约定义的模式",
                    location="response.schema",
                    test_id="response_schema_validation",
                )
            )

        return violations

    def validate_response_status(
        self, actual_status: int, expected_status: Union[int, List[int]]
    ) -> List[ContractViolation]:
        """验证响应状态码"""
        violations = []

        if isinstance(expected_status, list):
            if actual_status not in expected_status:
                violations.append(
                    ContractViolation(
                        violation_type=ContractViolationType.RESPONSE_STATUS_MISMATCH,
                        severity="error",
                        message=f"期望状态码 {expected_status}，实际 {actual_status}",
                        endpoint="N/A",
                        method="N/A",
                        expected=expected_status,
                        actual=actual_status,
                        suggestion=f"此API端点应该返回状态码之一: {expected_status}",
                        location="response.status",
                        test_id="status_validation",
                    )
                )
        else:
            if actual_status != expected_status:
                violations.append(
                    ContractViolation(
                        violation_type=ContractViolationType.RESPONSE_STATUS_MISMATCH,
                        severity="error",
                        message=f"期望状态码 {expected_status}，实际 {actual_status}",
                        endpoint="N/A",
                        method="N/A",
                        expected=expected_status,
                        actual=actual_status,
                        suggestion=f"此API端点应该返回状态码: {expected_status}",
                        location="response.status",
                        test_id="status_validation",
                    )
                )

        return violations

    def validate_headers(
        self, actual_headers: Dict[str, str], expected_headers: Dict[str, str]
    ) -> List[ContractViolation]:
        """验证响应头"""
        violations = []

        for key, expected_value in expected_headers.items():
            if key not in actual_headers:
                violations.append(
                    ContractViolation(
                        violation_type=ContractViolationType.HEADER_MISMATCH,
                        severity="warning",
                        message=f"缺少响应头: {key}",
                        endpoint="N/A",
                        method="N/A",
                        expected=expected_headers,
                        actual=actual_headers,
                        suggestion=f"API响应应包含头字段: {key}",
                        location="response.headers",
                        test_id="header_validation",
                    )
                )
            elif expected_value != "*":  # * 表示任意值
                if actual_headers[key] != expected_value:
                    violations.append(
                        ContractViolation(
                            violation_type=ContractViolationType.HEADER_MISMATCH,
                            severity="warning",
                            message=f"响应头 {key} 值不匹配，期望 '{expected_value}'，实际 '{actual_headers[key]}'",
                            endpoint="N/A",
                            method="N/A",
                            expected=expected_value,
                            actual=actual_headers[key],
                            suggestion=f"响应头 {key} 应该值为: {expected_value}",
                            location="response.headers",
                            test_id="header_value_validation",
                        )
                    )

        return violations

    @lru_cache(maxsize=100)
    def get_compiled_schema(self, schema_key: str) -> Optional[Dict[str, Any]]:
        """获取编译后的模式"""
        return self.compiled_schemas.get(schema_key)

    def cache_schema(self, schema_key: str, schema: Dict[str, Any]):
        """缓存模式"""
        self.compiled_schemas[schema_key] = schema


class RequestValidator:
    """请求验证器"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = httpx.Client(timeout=timeout)

    def validate_endpoint_exists(self, base_url: str, endpoint: str, method: str) -> List[ContractViolation]:
        """验证端点是否存在"""
        violations = []

        url = urljoin(base_url, endpoint)
        try:
            # 使用HEAD方法检查端点是否存在
            response = self.session.head(url, follow_redirects=True)

            if response.status_code >= 400:
                violations.append(
                    ContractViolation(
                        violation_type=ContractViolationType.MISSING_ENDPOINT,
                        severity="error",
                        message=f"端点不存在或不可访问: {method} {url}",
                        endpoint=endpoint,
                        method=method,
                        expected=200,
                        actual=response.status_code,
                        suggestion=f"请检查API文档中的端点路径是否正确: {endpoint}",
                        location="endpoint.existence",
                        test_id="endpoint_validation",
                    )
                )
        except Exception as e:
            violations.append(
                ContractViolation(
                    violation_type=ContractViolationType.MISSING_ENDPOINT,
                    severity="error",
                    message=f"无法验证端点: {str(e)}",
                    endpoint=endpoint,
                    method=method,
                    expected="successful_request",
                    actual="failed_request",
                    suggestion=f"请检查API服务是否正常运行: {base_url}",
                    location="endpoint.connectivity",
                    test_id="endpoint_connectivity",
                )
            )

        return violations

    def validate_request(
        self,
        url: str,
        method: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Tuple[requests.Response, List[ContractViolation]]:
        """执行请求并验证"""
        violations = []

        start_time = time.time()
        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=params,
                json=data,
                follow_redirects=True,
            )

            response_time = time.time() - start_time

            # 检查响应时间
            if response_time > 5:  # 超过5秒警告
                violations.append(
                    ContractViolation(
                        violation_type=ContractViolationType.RESPONSE_TIME_VIOLATION,
                        severity="warning",
                        message=f"响应时间过长: {response_time:.2f}s",
                        endpoint=urlparse(url).path,
                        method=method,
                        expected="<5s",
                        actual=response_time,
                        suggestion="请优化API性能或增加超时时间",
                        location="response.time",
                        test_id="response_time_validation",
                    )
                )

            return response, violations

        except Exception as e:
            response_time = time.time() - start_time
            violations.append(
                ContractViolation(
                    violation_type=ContractViolationType.INVALID_REQUEST,
                    severity="error",
                    message=f"请求执行失败: {str(e)}",
                    endpoint=urlparse(url).path,
                    method=method,
                    expected="successful_request",
                    actual="failed_request",
                    suggestion=f"请检查请求参数和网络连接: {url}",
                    location="request.execution",
                    test_id="request_execution",
                )
            )
            return None, violations

    def validate_content_type(self, response: requests.Response, expected_content_type: str) -> List[ContractViolation]:
        """验证内容类型"""
        violations = []

        actual_content_type = response.headers.get("content-type", "").split(";")[0]

        if expected_content_type not in actual_content_type:
            violations.append(
                ContractViolation(
                    violation_type=ContractViolationType.CONTENT_TYPE_MISMATCH,
                    severity="warning",
                    message=f"内容类型不匹配，期望 '{expected_content_type}'，实际 '{actual_content_type}'",
                    endpoint=urlparse(response.url).path,
                    method="GET",  # 这里需要根据实际情况设置
                    expected=expected_content_type,
                    actual=actual_content_type,
                    suggestion=f"API应返回内容类型: {expected_content_type}",
                    location="response.content_type",
                    test_id="content_type_validation",
                )
            )

        return violations

    def validate_security_headers(
        self, response: requests.Response, required_headers: List[str]
    ) -> List[ContractViolation]:
        """验证安全头"""
        violations = []

        for header in required_headers:
            if header not in response.headers:
                violations.append(
                    ContractViolation(
                        violation_type=ContractViolationType.SECURITY_VIOLATION,
                        severity="warning",
                        message=f"缺少安全头: {header}",
                        endpoint=urlparse(response.url).path,
                        method="GET",
                        expected=f"header_present: {header}",
                        actual=f"header_missing: {header}",
                        suggestion=f"API应包含安全头: {header}",
                        location="response.security_headers",
                        test_id="security_header_validation",
                    )
                )

        return violations


class DeprecationValidator:
    """弃用验证器"""

    def __init__(self):
        self.deprecation_annotations = {}

    def mark_endpoint_deprecated(self, endpoint: str, method: str, deprecation_info: Dict[str, Any]):
        """标记端点为弃用"""
        key = f"{method.upper()} {endpoint}"
        self.deprecation_annotations[key] = deprecation_info

    def validate_deprecation_usage(self, endpoint: str, method: str) -> List[ContractViolation]:
        """验证弃用使用"""
        violations = []

        key = f"{method.upper()} {endpoint}"
        if key in self.deprecation_annotations:
            deprecation_info = self.deprecation_annotations[key]

            violations.append(
                ContractViolation(
                    violation_type=ContractViolationType.DEPRECATION_VIOLATION,
                    severity="warning",
                    message=f"使用了弃用的端点: {key}",
                    endpoint=endpoint,
                    method=method,
                    expected="updated_endpoint",
                    actual="deprecated_endpoint",
                    suggestion=deprecation_info.get("alternative", "请使用替代端点"),
                    location="endpoint.deprecation",
                    test_id="deprecation_validation",
                )
            )

        return violations


