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


class ContractValidator:
    """契约验证器主类"""

    def __init__(self, base_url: str = None, openapi_spec_path: str = None):
        self.base_url = base_url or "http://localhost:8000"
        self.openapi_spec_path = openapi_spec_path
        self.contract_spec = None

        # 初始化验证器
        self.schema_validator = SchemaValidator()
        self.request_validator = RequestValidator()
        self.deprecation_validator = DeprecationValidator()

        # 缓存
        self.validation_cache = {}
        self.test_cache = {}

        # 加载OpenAPI规范
        if self.openapi_spec_path:
            self.load_openapi_spec(self.openapi_spec_path)

    def load_openapi_spec(self, spec_path: str):
        """加载OpenAPI规范"""
        try:
            with open(spec_path, "r", encoding="utf-8") as f:
                if spec_path.endswith(".json"):
                    spec = json.load(f)
                else:
                    spec = yaml.safe_load(f)

            self.contract_spec = ContractSpec(
                name=spec.get("info", {}).get("title", "Unknown API"),
                version=spec.get("info", {}).get("version", "1.0.0"),
                openapi_spec=spec,
                base_url=self.base_url,
                metadata=spec.get("info", {}),
            )

            # 缓存编译后的模式
            self._cache_schemas(spec)

            logger.info("成功加载OpenAPI规范: {self.contract_spec.name} v{self.contract_spec.version}")

        except Exception as e:
            logger.error("加载OpenAPI规范失败: %(e)s")
            raise

    def _cache_schemas(self, spec: Dict[str, Any]):
        """缓存模式定义"""
        if "components" in spec and "schemas" in spec["components"]:
            for schema_name, schema in spec["components"]["schemas"].items():
                self.schema_validator.cache_schema(schema_name, schema)

    def generate_contract_tests(self) -> List[ContractTest]:
        """从OpenAPI规范生成契约测试用例"""
        if not self.contract_spec:
            raise ValueError("未加载OpenAPI规范")

        tests = []
        spec = self.contract_spec.openapi_spec

        # 遍历所有路径
        for path, path_item in spec.get("paths", {}).items():
            for method, operation in path_item.items():
                if method.lower() in ["get", "post", "put", "delete", "patch"]:
                    # 为每个操作生成测试用例
                    test_cases = self._generate_test_cases_for_operation(path, method, operation)
                    tests.extend(test_cases)

        logger.info("生成了 {len(tests)} 个契约测试用例")
        return tests

    def _generate_test_cases_for_operation(
        self, path: str, method: str, operation: Dict[str, Any]
    ) -> List[ContractTest]:
        """为操作生成测试用例"""
        tests = []

        # 基本测试用例
        test = ContractTest(
            id=f"{method.upper()}_{path.replace('/', '_').replace('{', '').replace('}', '')}",
            name=f"Test {method.upper()} {path}",
            endpoint=path,
            method=method.upper(),
            expected_status=operation.get("responses", {}).get("default", {}).get("statusCode", 200),
            expected_headers=operation.get("responses", {}).get("200", {}).get("headers"),
            priority="high" if method.upper() in ["POST", "PUT", "DELETE"] else "medium",
            tags=operation.get("tags", ["default"]),
            metadata={
                "operation_id": operation.get("operationId"),
                "description": operation.get("description", ""),
                "deprecated": operation.get("deprecated", False),
            },
        )

        # 如果有请求体，生成数据模型测试
        if "requestBody" in operation:
            test.test_data = self._generate_request_test_data(operation["requestBody"])

        tests.append(test)

        # 生成参数化测试
        if "parameters" in operation:
            param_tests = self._generate_parameter_tests(path, method, operation)
            tests.extend(param_tests)

        # 生成边界值测试
        boundary_tests = self._generate_boundary_tests(path, method, operation)
        tests.extend(boundary_tests)

        return tests

    def _generate_request_test_data(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """生成请求测试数据"""
        # 简化实现，实际应该根据schema生成测试数据
        content = request_body.get("content", {})
        if "application/json" in content:
            schema = content["application/json"].get("schema", {})
            return self._generate_test_data_from_schema(schema)

        return {"test": "data"}

    def _generate_test_data_from_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """从schema生成测试数据"""
        # 简化的测试数据生成
        test_data = {}

        if schema.get("type") == "object" and "properties" in schema:
            for prop, prop_schema in schema["properties"].items():
                if prop_schema.get("type") == "string":
                    test_data[prop] = "test_string"
                elif prop_schema.get("type") == "integer":
                    test_data[prop] = 1
                elif prop_schema.get("type") == "number":
                    test_data[prop] = 1.0
                elif prop_schema.get("type") == "boolean":
                    test_data[prop] = True
                elif prop_schema.get("type") == "array":
                    test_data[prop] = []
                elif prop_schema.get("type") == "object":
                    test_data[prop] = {}

        return test_data

    def _generate_parameter_tests(self, path: str, method: str, operation: Dict[str, Any]) -> List[ContractTest]:
        """生成参数化测试"""
        tests = []
        parameters = operation.get("parameters", [])

        # 简化实现：为每个参数生成测试
        for param in parameters:
            test = ContractTest(
                id=f"{method.upper()}_{path.replace('/', '_')}_{param['name']}_param",
                name=f"Test {method.upper()} {path} - Parameter {param['name']}",
                endpoint=path,
                method=method.upper(),
                expected_status=200,
                priority="medium",
                tags=operation.get("tags", ["default"]),
                metadata={
                    "parameter_name": param["name"],
                    "parameter_in": param.get("in", "query"),
                    "required": param.get("required", False),
                },
            )
            tests.append(test)

        return tests

    def _generate_boundary_tests(self, path: str, method: str, operation: Dict[str, Any]) -> List[ContractTest]:
        """生成边界值测试"""
        tests = []

        # 简化实现：生成一些边界测试
        boundary_test = ContractTest(
            id=f"{method.upper()}_{path.replace('/', '_')}_boundary",
            name=f"Test {method.upper()} {path} - Boundary Values",
            endpoint=path,
            method=method.upper(),
            expected_status=400,  # 边界测试通常期望错误响应
            priority="low",
            tags=operation.get("tags", ["default"]),
            metadata={"test_type": "boundary"},
        )
        tests.append(boundary_test)

        return tests

    def run_contract_validation(
        self,
        tests: List[ContractTest] = None,
        validation_level: ValidationLevel = ValidationLevel.STRICT,
    ) -> ValidationResult:
        """运行契约验证"""
        start_time = time.time()

        if not self.contract_spec:
            raise ValueError("未加载OpenAPI规范")

        if tests is None:
            tests = self.generate_contract_tests()

        violations = []
        test_results = []
        coverage_metrics = {
            "total_endpoints": 0,
            "tested_endpoints": 0,
            "total_operations": 0,
            "tested_operations": 0,
        }

        # 统计覆盖率
        spec = self.contract_spec.openapi_spec
        coverage_metrics["total_endpoints"] = len(spec.get("paths", {}))
        coverage_metrics["total_operations"] = sum(
            len([m for m in path.keys() if m.lower() in ["get", "post", "put", "delete", "patch"]])
            for path in spec.get("paths", {}).values()
        )

        # 执行测试
        for test in tests:
            result = self._run_single_test(test, validation_level)
            test_results.append(result)

            # 收集违规
            if result.get("violations"):
                violations.extend(result["violations"])

            # 更新覆盖率
            if result.get("executed", False):
                coverage_metrics["tested_endpoints"] += 1
                coverage_metrics["tested_operations"] += 1

        execution_time = time.time() - start_time

        # 生成总结
        summary = self._generate_summary(test_results, violations)

        return ValidationResult(
            contract_spec=self.contract_spec,
            test_results=test_results,
            violations=violations,
            execution_time=execution_time,
            coverage_metrics=coverage_metrics,
            summary=summary,
            timestamp=datetime.now(),
        )

    def _run_single_test(self, test: ContractTest, validation_level: ValidationLevel) -> Dict[str, Any]:
        """执行单个测试"""
        result = {
            "test_id": test.id,
            "test_name": test.name,
            "endpoint": test.endpoint,
            "method": test.method,
            "executed": False,
            "passed": False,
            "start_time": datetime.now(),
            "end_time": None,
            "duration": 0,
            "violations": [],
            "error": None,
        }

        try:
            # 验证端点存在
            endpoint_violations = self.request_validator.validate_endpoint_exists(
                self.base_url, test.endpoint, test.method
            )
            result["violations"].extend(endpoint_violations)

            if endpoint_violations:
                result["end_time"] = datetime.now()
                result["duration"] = (result["end_time"] - result["start_time"]).total_seconds()
                return result

            # 构建URL
            url = urljoin(self.base_url, test.endpoint)

            # 执行请求
            response, request_violations = self.request_validator.validate_request(
                url=url,
                method=test.method,
                data=test.test_data,
                headers={"Content-Type": "application/json"},
            )

            result["violations"].extend(request_violations)

            if response is None:
                result["error"] = "Request failed"
                result["end_time"] = datetime.now()
                result["duration"] = (result["end_time"] - result["start_time"]).total_seconds()
                return result

            # 验证响应
            response_violations = self._validate_response(response, test, validation_level)
            result["violations"].extend(response_violations)

            # 检查是否通过
            has_critical_violations = any(v.severity == "error" for v in result["violations"])
            result["passed"] = not has_critical_violations
            result["executed"] = True

        except Exception as e:
            result["error"] = str(e)
            logger.error("测试执行失败 {test.id}: %(e)s")

        finally:
            result["end_time"] = datetime.now()
            result["duration"] = (result["end_time"] - result["start_time"]).total_seconds()

        return result

    def _validate_response(
        self,
        response: requests.Response,
        test: ContractTest,
        validation_level: ValidationLevel,
    ) -> List[ContractViolation]:
        """验证响应"""
        violations = []

        # 验证状态码
        status_violations = self.schema_validator.validate_response_status(response.status_code, test.expected_status)
        violations.extend(status_violations)

        # 验证响应头
        if test.expected_headers:
            header_violations = self.schema_validator.validate_headers(response.headers, test.expected_headers)
            violations.extend(header_violations)

        # 验证内容类型
        content_type_violations = self.request_validator.validate_content_type(response, "application/json")
        violations.extend(content_type_violations)

        # 验证模式（如果定义了）
        spec = self.contract_spec.openapi_spec
        path_key = test.endpoint
        method_key = test.method.lower()

        if path_key in spec.get("paths", {}) and method_key in spec["paths"][path_key]:
            operation = spec["paths"][path_key][method_key]

            # 验证响应模式
            if "responses" in operation:
                for status_code, response_spec in operation["responses"].items():
                    if str(response.status_code) == str(status_code):
                        if "content" in response_spec and "application/json" in response_spec["content"]:
                            schema = response_spec["content"]["application/json"].get("schema", {})
                            if schema:
                                try:
                                    validate(instance=response.json(), schema=schema)
                                except ValidationError as e:
                                    violations.append(
                                        ContractViolation(
                                            violation_type=ContractViolationType.INVALID_RESPONSE,
                                            severity="error",
                                            message=f"响应模式验证失败: {e.message}",
                                            endpoint=test.endpoint,
                                            method=test.method,
                                            expected=schema,
                                            actual=response.json(),
                                            suggestion="响应数据不符合API契约定义的模式",
                                            location="response.schema",
                                            test_id=test.id,
                                        )
                                    )

        return violations

    def _generate_summary(
        self, test_results: List[Dict[str, Any]], violations: List[ContractViolation]
    ) -> Dict[str, Any]:
        """生成总结"""
        total_tests = len(test_results)
        passed_tests = sum(1 for r in test_results if r.get("passed", False))
        executed_tests = sum(1 for r in test_results if r.get("executed", False))

        # 按违规类型统计
        violation_counts = defaultdict(int)
        for violation in violations:
            violation_counts[violation.violation_type.value] += 1

        # 按严重程度统计
        severity_counts = defaultdict(int)
        for violation in violations:
            severity_counts[violation.severity] += 1

        return {
            "total_tests": total_tests,
            "executed_tests": executed_tests,
            "passed_tests": passed_tests,
            "failed_tests": executed_tests - passed_tests,
            "pass_rate": passed_tests / executed_tests if executed_tests > 0 else 0,
            "execution_rate": executed_tests / total_tests if total_tests > 0 else 0,
            "total_violations": len(violations),
            "violation_counts": dict(violation_counts),
            "severity_counts": dict(severity_counts),
            "avg_test_duration": (
                sum(r.get("duration", 0) for r in test_results) / executed_tests if executed_tests > 0 else 0
            ),
        }

    def generate_validation_report(
        self,
        validation_result: ValidationResult,
        output_path: str,
        format: str = "html",
    ):
        """生成验证报告"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == "html":
            self._generate_html_report(validation_result, output_path)
        elif format == "json":
            self._generate_json_report(validation_result, output_path)
        elif format == "markdown":
            self._generate_markdown_report(validation_result, output_path)

        logger.info("验证报告已生成: %(output_path)s")

    def _generate_html_report(self, validation_result: ValidationResult, output_path: Path):
        """生成HTML报告"""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>API契约验证报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; margin-bottom: 20px; }
        .summary { background-color: #e8f4f8; padding: 15px; margin-bottom: 20px; }
        .test-results { margin-bottom: 20px; }
        .violation { background-color: #ffebee; padding: 10px; margin: 5px 0; border-left: 4px solid #f44336; }
        .warning { background-color: #fff3cd; border-left-color: #ffc107; }
        .error { background-color: #f8d7da; border-left-color: #dc3545; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>API契约验证报告</h1>
        <p><strong>API名称:</strong> {contract_name}</p>
        <p><strong>版本:</strong> {version}</p>
        <p><strong>验证时间:</strong> {timestamp}</p>
        <p><strong>执行时间:</strong> {execution_time:.2f}秒</p>
    </div>

    <div class="summary">
        <h2>验证总结</h2>
        <table>
            <tr><td>总测试数:</td><td>{total_tests}</td></tr>
            <tr><td>已执行测试:</td><td>{executed_tests}</td></tr>
            <tr><td>通过测试:</td><td>{passed_tests}</td></tr>
            <tr><td>失败测试:</td><td>{failed_tests}</td></tr>
            <tr><td>通过率:</td><td>{pass_rate:.2%}</td></tr>
            <tr><td>覆盖率:</td><td>{coverage_rate:.2%}</td></tr>
        </table>
    </div>

    <div class="violations">
        <h2>违规详情</h2>
        {violations_html}
    </div>

    <div class="test-results">
        <h2>测试结果</h2>
        {test_results_html}
    </div>
</body>
</html>
        """

        summary = validation_result.summary
        violations_html = ""
        for violation in validation_result.violations:
            severity_class = "error" if violation.severity == "error" else "warning"
            violations_html += f"""
            <div class="violation {severity_class}">
                <strong>{violation.violation_type.value}</strong> - {violation.severity}
                <p>{violation.message}</p>
                <p><strong>端点:</strong> {violation.endpoint} {violation.method}</p>
                <p><strong>建议:</strong> {violation.suggestion}</p>
                <p><small>时间: {violation.timestamp}</small></p>
            </div>
            """

        test_results_html = ""
        for result in validation_result.test_results:
            status = "✅ 通过" if result.get("passed") else "❌ 失败"
            test_results_html += f"""
            <tr>
                <td>{result.get("test_name", "N/A")}</td>
                <td>{result.get("method", "N/A")}</td>
                <td>{result.get("endpoint", "N/A")}</td>
                <td>{status}</td>
                <td>{result.get("duration", 0):.2f}s</td>
            </tr>
            """

        coverage_rate = (
            validation_result.coverage_metrics["tested_operations"]
            / validation_result.coverage_metrics["total_operations"]
            if validation_result.coverage_metrics["total_operations"] > 0
            else 0
        )

        html_content = html_template.format(
            contract_name=validation_result.contract_spec.name,
            version=validation_result.contract_spec.version,
            timestamp=validation_result.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            execution_time=validation_result.execution_time,
            total_tests=summary["total_tests"],
            executed_tests=summary["executed_tests"],
            passed_tests=summary["passed_tests"],
            failed_tests=summary["failed_tests"],
            pass_rate=summary["pass_rate"],
            coverage_rate=coverage_rate,
            violations_html=violations_html or "<p>无违规</p>",
            test_results_html=test_results_html,
        )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    def _generate_json_report(self, validation_result: ValidationResult, output_path: Path):
        """生成JSON报告"""
        report = {
            "metadata": {
                "contract_name": validation_result.contract_spec.name,
                "version": validation_result.contract_spec.version,
                "timestamp": validation_result.timestamp.isoformat(),
                "execution_time": validation_result.execution_time,
            },
            "summary": validation_result.summary,
            "coverage_metrics": validation_result.coverage_metrics,
            "violations": [
                {
                    "type": v.violation_type.value,
                    "severity": v.severity,
                    "message": v.message,
                    "endpoint": v.endpoint,
                    "method": v.method,
                    "timestamp": v.timestamp.isoformat(),
                    "test_id": v.test_id,
                }
                for v in validation_result.violations
            ],
            "test_results": validation_result.test_results,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    def _generate_markdown_report(self, validation_result: ValidationResult, output_path: Path):
        """生成Markdown报告"""
        md_content = f"""# API契约验证报告

## 基本信息
- **API名称**: {validation_result.contract_spec.name}
- **版本**: {validation_result.contract_spec.version}
- **验证时间**: {validation_result.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
- **执行时间**: {validation_result.execution_time:.2f}秒

## 验证总结

| 指标 | 数值 |
|------|------|
| 总测试数 | {validation_result.summary["total_tests"]} |
| 已执行测试 | {validation_result.summary["executed_tests"]} |
| 通过测试 | {validation_result.summary["passed_tests"]} |
| 失败测试 | {validation_result.summary["failed_tests"]} |
| 通过率 | {validation_result.summary["pass_rate"]:.2%} |

## 覆盖率

| 指标 | 数值 |
|------|------|
| 总端点数 | {validation_result.coverage_metrics["total_endpoints"]} |
| 已测试端点 | {validation_result.coverage_metrics["tested_endpoints"]} |
| 总操作数 | {validation_result.coverage_metrics["total_operations"]} |
| 已测试操作 | {validation_result.coverage_metrics["tested_operations"]} |

## 违规统计

### 按类型统计
"""

        for violation_type, count in validation_result.summary["violation_counts"].items():
            md_content += f"- {violation_type}: {count}\\n"

        md_content += "\\n### 按严重程度统计\\n"
        for severity, count in validation_result.summary["severity_counts"].items():
            md_content += f"- {severity}: {count}\\n"

        md_content += """
## 违规详情

"""
        for violation in validation_result.violations:
            md_content += f"""
### {violation.violation_type.value} - {violation.severity}

- **端点**: {violation.endpoint} {violation.method}
- **消息**: {violation.message}
- **建议**: {violation.suggestion}
- **时间**: {violation.timestamp.strftime("%Y-%m-%d %H:%M:%S")}

"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_content)


# 使用示例
def demo_contract_validator():
    """演示契约验证器功能"""
    print("🚀 演示契约验证器功能")

    # 创建示例OpenAPI规范
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "测试API",
            "version": "1.0.0",
            "description": "用于测试的API",
        },
        "servers": [{"url": "http://localhost:8000", "description": "开发服务器"}],
        "paths": {
            "/users": {
                "get": {
                    "summary": "获取用户列表",
                    "operationId": "getUsers",
                    "responses": {
                        "200": {
                            "description": "用户列表",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "integer"},
                                                "name": {"type": "string"},
                                                "email": {"type": "string"},
                                            },
                                        },
                                    }
                                }
                            },
                        }
                    },
                },
                "post": {
                    "summary": "创建用户",
                    "operationId": "createUser",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["name", "email"],
                                    "properties": {
                                        "name": {"type": "string"},
                                        "email": {"type": "string", "format": "email"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {"201": {"description": "用户创建成功"}},
                },
            }
        },
    }

    # 保存OpenAPI规范
    with open("test_openapi.json", "w") as f:
        json.dump(openapi_spec, f, indent=2)

    # 创建契约验证器
    validator = ContractValidator(base_url="http://localhost:8000")
    validator.load_openapi_spec("test_openapi.json")

    # 生成测试用例
    tests = validator.generate_contract_tests()
    print(f"生成了 {len(tests)} 个测试用例")

    # 运行验证
    print("开始运行契约验证...")
    validation_result = validator.run_contract_validation(tests=tests, validation_level=ValidationLevel.STRICT)

    # 显示结果
    summary = validation_result.summary
    print("\\n📊 验证结果:")
    print(f"总测试数: {summary['total_tests']}")
    print(f"已执行: {summary['executed_tests']}")
    print(f"通过: {summary['passed_tests']}")
    print(f"失败: {summary['failed_tests']}")
    print(f"通过率: {summary['pass_rate']:.2%}")

    print("\\n📈 覆盖率:")
    print(
        f"端点覆盖: {validation_result.coverage_metrics['tested_endpoints']}/{validation_result.coverage_metrics['total_endpoints']}"
    )
    print(
        f"操作覆盖: {validation_result.coverage_metrics['tested_operations']}/{validation_result.coverage_metrics['total_operations']}"
    )

    print(f"\\n⚠️ 违规数量: {len(validation_result.violations)}")
    for violation in validation_result.violations[:3]:  # 只显示前3个
        print(f"  - {violation.violation_type.value}: {violation.message}")

    # 生成报告
    validator.generate_validation_report(validation_result, "contract_validation_report.html", "html")
    validator.generate_validation_report(validation_result, "contract_validation_report.json", "json")
    validator.generate_validation_report(validation_result, "contract_validation_report.md", "markdown")

    print("\\n📄 报告已生成:")
    print("  - contract_validation_report.html")
    print("  - contract_validation_report.json")
    print("  - contract_validation_report.md")

    # 清理
    os.remove("test_openapi.json")


if __name__ == "__main__":
    demo_contract_validator()
