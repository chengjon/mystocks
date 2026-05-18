"""
API Documentation Validation Tests

This test suite validates that API documentation is complete and accurate:
- OpenAPI/Swagger documentation completeness
- All endpoints have proper descriptions
- Request/response examples are provided
- Authentication requirements are documented
- Error responses are documented

Version: 1.0.0
Date: 2025-12-03
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.main import app


TECH_DEBT_BASELINE_FILE = Path(__file__).resolve().parents[3] / "reports" / "analysis" / "tech-debt-baseline.json"
DOCUMENTATION_BASELINE_KEY = "backend_api_documentation"
FLOAT_TOLERANCE = 1e-12
NON_CONTRACT_ROUTE_PATHS = {"/api/docs", "/api/redoc"}
JSON_SUCCESS_EXAMPLE_MEDIA_TYPE = "application/json"


def load_documentation_baseline() -> Dict[str, Any]:
    """加载 API 文档债务基线，确保测试按“不得劣化”口径执行。"""
    payload = json.loads(TECH_DEBT_BASELINE_FILE.read_text(encoding="utf-8"))
    baseline = payload.get(DOCUMENTATION_BASELINE_KEY)
    if not isinstance(baseline, dict):
        raise AssertionError(f"Missing {DOCUMENTATION_BASELINE_KEY} in {TECH_DEBT_BASELINE_FILE}")
    return baseline


class APIDocumentationValidator:
    """Comprehensive API documentation validation"""

    def __init__(self, client: TestClient):
        self.client = client
        self.openapi_schema = None
        self.validation_results: Dict[str, Any] = {
            "summary": {
                "total_endpoints": 0,
                "documented_endpoints": 0,
                "endpoints_with_examples": 0,
                "endpoints_with_errors": 0,
                "total_issues": 0,
            },
            "endpoint_results": [],
            "global_issues": [],
        }

    def get_openapi_schema(self) -> Optional[Dict[str, Any]]:
        """Fetch the OpenAPI schema"""
        if not self.openapi_schema:
            response = self.client.get("/openapi.json")
            if response.status_code == 200:
                self.openapi_schema = response.json()
            else:
                raise Exception(f"Could not fetch OpenAPI schema: {response.status_code}")
        return self.openapi_schema

    @staticmethod
    def _has_openapi_type(schema_fragment: Dict[str, Any]) -> bool:
        """OpenAPI 3.1 may express types via type/ref/composition keywords."""
        return any(key in schema_fragment for key in ("type", "$ref", "anyOf", "oneOf", "allOf"))

    @classmethod
    def _has_openapi_description(
        cls,
        schema_fragment: Dict[str, Any],
        schemas: Dict[str, Dict[str, Any]],
        visited_refs: Optional[set[str]] = None,
    ) -> bool:
        """Descriptions may live on the property itself or on a referenced schema."""
        if not isinstance(schema_fragment, dict):
            return False

        if schema_fragment.get("description"):
            return True

        visited = visited_refs or set()
        ref = schema_fragment.get("$ref")
        if isinstance(ref, str):
            ref_name = ref.rsplit("/", 1)[-1]
            if ref_name in visited:
                return False
            referenced_schema = schemas.get(ref_name)
            if referenced_schema and cls._has_openapi_description(
                referenced_schema,
                schemas,
                visited | {ref_name},
            ):
                return True

        for composition_key in ("allOf", "oneOf", "anyOf"):
            for nested_fragment in schema_fragment.get(composition_key, []):
                if cls._has_openapi_description(nested_fragment, schemas, visited):
                    return True

        return False

    def validate_openapi_completeness(self) -> Dict[str, Any]:
        """Validate OpenAPI schema completeness"""
        issues = []

        try:
            schema = self.get_openapi_schema()

            # Check required OpenAPI fields
            required_fields = ["openapi", "info", "paths"]
            for field in required_fields:
                if field not in schema:
                    issues.append(f"Missing required OpenAPI field: {field}")

            # Check info section
            if "info" in schema:
                info = schema["info"]
                required_info_fields = ["title", "version", "description"]
                for field in required_info_fields:
                    if field not in info:
                        issues.append(f"Missing required info field: {field}")

                # Check description length
                if "description" in info and len(info["description"]) < 50:
                    issues.append("API description is too brief (should be at least 50 characters)")

            # Check for servers section
            if "servers" not in schema or not schema["servers"]:
                issues.append("Missing servers section in OpenAPI schema")

            # Check for components/schemas
            if "components" not in schema or "schemas" not in schema.get("components", {}):
                issues.append("Missing components/schemas section")

        except Exception as e:
            issues.append(f"Error validating OpenAPI schema: {str(e)}")

        return {"compliance": len(issues) == 0, "issues": issues}

    def validate_endpoint_documentation(self) -> List[Dict[str, Any]]:
        """Validate documentation for all endpoints"""
        endpoint_results = []
        schema = self.get_openapi_schema()

        for route in app.routes:
            if isinstance(route, APIRoute):
                if route.path in NON_CONTRACT_ROUTE_PATHS:
                    continue
                endpoint_result = self._validate_single_endpoint(route, schema)
                endpoint_results.append(endpoint_result)

        return endpoint_results

    @staticmethod
    def _openapi_path_for_route(route_path: str) -> str:
        """Normalize FastAPI path convertors to the OpenAPI path-template form."""
        return re.sub(r"\{([^}:]+):[^}]+\}", r"{\1}", route_path)

    def find_success_json_response_example_gaps(self) -> List[Dict[str, str]]:
        """Return JSON success responses that still miss an explicit OpenAPI example.

        Prometheus/OpenMetrics `text/plain` endpoints are intentionally excluded here.
        Their contract is validated separately by route-specific tests.
        """

        schema = self.get_openapi_schema()
        missing_examples: List[Dict[str, str]] = []

        for path, path_item in schema.get("paths", {}).items():
            for method, method_spec in path_item.items():
                responses = method_spec.get("responses", {})
                for status_code, response_spec in responses.items():
                    if not status_code.startswith("2") or status_code == "204":
                        continue

                    content = response_spec.get("content", {})
                    json_content = content.get(JSON_SUCCESS_EXAMPLE_MEDIA_TYPE)
                    if not isinstance(json_content, dict):
                        continue

                    if "example" not in json_content and "examples" not in json_content:
                        missing_examples.append(
                            {
                                "method": method.upper(),
                                "path": path,
                                "status_code": status_code,
                            }
                        )

        return missing_examples

    def _validate_single_endpoint(self, route: APIRoute, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate documentation for a single endpoint"""
        endpoint_result = {
            "path": route.path,
            "methods": list(route.methods),
            "documentation": {
                "has_summary": False,
                "has_description": False,
                "has_tags": False,
                "has_parameters": False,
                "has_request_body": False,
                "has_responses": False,
                "has_examples": False,
                "has_error_responses": False,
            },
            "issues": [],
        }

        try:
            # Find endpoint in OpenAPI schema
            openapi_path = self._openapi_path_for_route(route.path)
            path_item = schema.get("paths", {}).get(openapi_path, {})
            if not path_item:
                endpoint_result["issues"].append("Endpoint not found in OpenAPI schema")
                return endpoint_result

            for method in route.methods:
                if method.lower() in ["get", "post", "put", "delete", "patch"]:
                    method_spec = path_item.get(method.lower(), {})
                    if method_spec:
                        self._validate_method_documentation(method_spec, endpoint_result, method)

        except Exception as e:
            endpoint_result["issues"].append(f"Error validating endpoint: {str(e)}")

        return endpoint_result

    def _validate_method_documentation(self, method_spec: Dict[str, Any], endpoint_result: Dict[str, Any], method: str):
        """Validate documentation for a specific HTTP method"""
        # Check summary
        if "summary" in method_spec and method_spec["summary"]:
            endpoint_result["documentation"]["has_summary"] = True
        else:
            endpoint_result["issues"].append(f"Missing summary for {method.upper()}")

        # Check description
        if "description" in method_spec and method_spec["description"]:
            endpoint_result["documentation"]["has_description"] = True
            # Check description quality
            if len(method_spec["description"]) < 20:
                endpoint_result["issues"].append(f"Description too brief for {method.upper()}")
        else:
            endpoint_result["issues"].append(f"Missing description for {method.upper()}")

        # Check tags
        if "tags" in method_spec and method_spec["tags"]:
            endpoint_result["documentation"]["has_tags"] = True
        else:
            endpoint_result["issues"].append(f"Missing tags for {method.upper()}")

        # Check parameters
        if "parameters" in method_spec and method_spec["parameters"]:
            endpoint_result["documentation"]["has_parameters"] = True
            self._validate_parameters(method_spec["parameters"], endpoint_result, method)

        # Check request body
        if "requestBody" in method_spec and method_spec["requestBody"]:
            endpoint_result["documentation"]["has_request_body"] = True
            self._validate_request_body(method_spec["requestBody"], endpoint_result, method)

        # Check responses
        if "responses" in method_spec and method_spec["responses"]:
            endpoint_result["documentation"]["has_responses"] = True
            self._validate_responses(method_spec["responses"], endpoint_result, method)

    def _validate_parameters(
        self,
        parameters: List[Dict[str, Any]],
        endpoint_result: Dict[str, Any],
        method: str,
    ):
        """Validate parameter documentation"""
        for param in parameters:
            required_param_fields = ["name", "in", "schema"]
            for field in required_param_fields:
                if field not in param:
                    endpoint_result["issues"].append(f"Parameter missing {field} for {method.upper()}")

            # Check parameter description
            if "description" not in param or not param["description"]:
                endpoint_result["issues"].append(
                    f"Parameter {param.get('name', 'unknown')} missing description for {method.upper()}"
                )

    def _validate_request_body(self, request_body: Dict[str, Any], endpoint_result: Dict[str, Any], method: str):
        """Validate request body documentation"""
        if "content" not in request_body:
            endpoint_result["issues"].append(f"Request body missing content specification for {method.upper()}")
            return

        content = request_body["content"]
        supported_content_types = [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
        ]
        matching_content_type = next((content_type for content_type in supported_content_types if content_type in content), None)
        if matching_content_type is None:
            endpoint_result["issues"].append(f"Request body missing supported content type for {method.upper()}")
            return

        request_content = content[matching_content_type]
        if "schema" not in request_content:
            endpoint_result["issues"].append(f"Request body missing schema for {method.upper()}")

        # Check for examples
        if "example" in request_content or "examples" in request_content:
            endpoint_result["documentation"]["has_examples"] = True
        else:
            endpoint_result["issues"].append(f"Request body missing example for {method.upper()}")

    def _validate_responses(self, responses: Dict[str, Any], endpoint_result: Dict[str, Any], method: str):
        """Validate response documentation"""
        has_success_response = False
        has_error_response = False
        has_response_examples = False

        for status_code, response_spec in responses.items():
            # Check success responses
            if status_code.startswith("2"):
                has_success_response = True
                if "description" not in response_spec or not response_spec["description"]:
                    endpoint_result["issues"].append(
                        f"Success response {status_code} missing description for {method.upper()}"
                    )

                # Check for content examples
                if "content" in response_spec:
                    content = response_spec["content"]
                    for content_spec in content.values():
                        if isinstance(content_spec, dict) and (
                            "example" in content_spec or "examples" in content_spec
                        ):
                            has_response_examples = True
                            break

            # Check error responses
            elif status_code.startswith("4") or status_code.startswith("5"):
                has_error_response = True
                if "description" not in response_spec or not response_spec["description"]:
                    endpoint_result["issues"].append(
                        f"Error response {status_code} missing description for {method.upper()}"
                    )

        if not has_success_response:
            endpoint_result["issues"].append(f"Missing success response for {method.upper()}")

        if has_error_response:
            endpoint_result["documentation"]["has_error_responses"] = True
        else:
            endpoint_result["issues"].append(f"Missing error response documentation for {method.upper()}")

        if has_response_examples:
            endpoint_result["documentation"]["has_examples"] = True

    def validate_authentication_documentation(self) -> List[str]:
        """Validate authentication documentation"""
        issues = []

        try:
            schema = self.get_openapi_schema()

            # Check for security schemes
            if "components" not in schema or "securitySchemes" not in schema.get("components", {}):
                issues.append("Missing security schemes documentation")
                return issues

            security_schemes = schema["components"]["securitySchemes"]

            # Check for Bearer token authentication
            if "Bearer" not in security_schemes:
                issues.append("Missing Bearer token authentication scheme")
            else:
                bearer_scheme = security_schemes["Bearer"]
                required_bearer_fields = ["type", "scheme"]
                for field in required_bearer_fields:
                    if field not in bearer_scheme:
                        issues.append(f"Bearer scheme missing field: {field}")

            # Check for global security requirement
            if "security" not in schema:
                issues.append("Missing global security requirement")
            else:
                security_reqs = schema["security"]
                if not any("Bearer" in req for req in security_reqs):
                    issues.append("Global security doesn't reference Bearer scheme")

        except Exception as e:
            issues.append(f"Error validating authentication documentation: {str(e)}")

        return issues

    def validate_schema_definitions(self) -> List[str]:
        """Validate schema definitions"""
        issues = []

        try:
            schema = self.get_openapi_schema()

            if "components" not in schema or "schemas" not in schema.get("components", {}):
                issues.append("Missing schema definitions")
                return issues

            schemas = schema["components"]["schemas"]

            for schema_name, schema_def in schemas.items():
                # Check for required fields
                if not self._has_openapi_type(schema_def):
                    issues.append(f"Schema {schema_name} missing type")

                # Check for description
                if not self._has_openapi_description(schema_def, schemas):
                    issues.append(f"Schema {schema_name} missing description")

                # Check for properties
                if schema_def.get("type") == "object":
                    if "properties" not in schema_def:
                        issues.append(f"Object schema {schema_name} missing properties")
                    else:
                        properties = schema_def["properties"]
                        for prop_name, prop_def in properties.items():
                            if not self._has_openapi_type(prop_def):
                                issues.append(f"Property {prop_name} in {schema_name} missing type")
                            if not self._has_openapi_description(prop_def, schemas):
                                issues.append(f"Property {prop_name} in {schema_name} missing description")

        except Exception as e:
            issues.append(f"Error validating schema definitions: {str(e)}")

        return issues

    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run all documentation validations"""
        # OpenAPI completeness
        openapi_result = self.validate_openapi_completeness()
        self.validation_results["global_issues"].extend(openapi_result["issues"])

        # Endpoint documentation
        endpoint_results = self.validate_endpoint_documentation()
        self.validation_results["endpoint_results"] = endpoint_results

        # Authentication documentation
        auth_issues = self.validate_authentication_documentation()
        self.validation_results["global_issues"].extend(auth_issues)

        # Schema definitions
        schema_issues = self.validate_schema_definitions()
        self.validation_results["global_issues"].extend(schema_issues)

        # Calculate summary statistics
        self.validation_results["summary"]["total_endpoints"] = len(endpoint_results)
        self.validation_results["summary"]["documented_endpoints"] = sum(
            1 for ep in endpoint_results if any(ep["documentation"].values()) and len(ep["issues"]) == 0
        )
        self.validation_results["summary"]["endpoints_with_examples"] = sum(
            1 for ep in endpoint_results if ep["documentation"]["has_examples"]
        )
        self.validation_results["summary"]["endpoints_with_errors"] = sum(
            1 for ep in endpoint_results if ep["documentation"]["has_error_responses"]
        )
        self.validation_results["summary"]["total_issues"] = len(self.validation_results["global_issues"]) + sum(
            len(ep["issues"]) for ep in endpoint_results
        )

        return self.validation_results

    def generate_report(self) -> str:
        """Generate detailed documentation validation report"""
        report = []
        report.append("=" * 80)
        report.append("API DOCUMENTATION VALIDATION REPORT")
        report.append("=" * 80)

        summary = self.validation_results["summary"]
        report.append(f"Total Endpoints: {summary['total_endpoints']}")
        report.append(f"Fully Documented: {summary['documented_endpoints']}")
        report.append(f"With Examples: {summary['endpoints_with_examples']}")
        report.append(f"With Error Responses: {summary['endpoints_with_errors']}")
        report.append(f"Total Issues: {summary['total_issues']}")
        report.append("")

        # Global issues
        if self.validation_results["global_issues"]:
            report.append("GLOBAL ISSUES:")
            report.append("-" * 40)
            for issue in self.validation_results["global_issues"]:
                report.append(f"  ❌ {issue}")
            report.append("")

        # Endpoint-specific issues
        for endpoint_result in self.validation_results["endpoint_results"]:
            if endpoint_result["issues"]:
                report.append(f"ENDPOINT: {endpoint_result['path']}")
                report.append(f"Methods: {', '.join(endpoint_result['methods'])}")
                report.append("-" * 40)

                for issue in endpoint_result["issues"]:
                    report.append(f"  ❌ {issue}")

                # Show documentation status
                doc_status = endpoint_result["documentation"]
                if any(doc_status.values()):
                    report.append("  Documentation Status:")
                    for key, value in doc_status.items():
                        status_icon = "✅" if value else "❌"
                        report.append(f"    {status_icon} {key.replace('_', ' ').title()}")

                report.append("")

        return "\n".join(report)


@pytest.fixture
def documentation_validator(test_client):
    """Create API documentation validator instance"""
    return APIDocumentationValidator(test_client)


class TestAPIDocumentationValidation:
    """Test suite for API documentation validation"""

    def test_openapi_schema_completeness(self, documentation_validator):
        """Test that OpenAPI schema is complete and valid"""
        result = documentation_validator.validate_openapi_completeness()

        assert result["compliance"], f"OpenAPI schema issues: {result['issues']}"

    def test_endpoint_documentation_completeness(self, documentation_validator):
        """Test that all endpoints have complete documentation"""
        baseline = load_documentation_baseline()
        results = documentation_validator.validate_endpoint_documentation()

        # Calculate documentation coverage
        total_methods = sum(len(ep["methods"]) for ep in results)
        documented_methods = sum(
            len(
                [
                    m
                    for m in ep["methods"]
                    if ep["documentation"]["has_summary"] and ep["documentation"]["has_description"]
                ]
            )
            for ep in results
        )

        if total_methods > 0:
            documentation_coverage = documented_methods / total_methods
            assert (
                documentation_coverage + FLOAT_TOLERANCE >= baseline["documented_percentage"]
            ), (
                f"Documentation coverage {documentation_coverage:.2%} regressed below baseline "
                f"{baseline['documented_percentage']:.2%}"
            )

    def test_request_response_examples(self, documentation_validator):
        """Test that endpoints have request/response examples"""
        baseline = load_documentation_baseline()
        results = documentation_validator.validate_endpoint_documentation()

        endpoints_with_examples = sum(1 for ep in results if ep["documentation"]["has_examples"])

        total_endpoints = len(results)
        assert endpoints_with_examples > 0, "OpenAPI schema should contain at least one documented request/response example"
        if total_endpoints > 0:
            example_coverage = endpoints_with_examples / total_endpoints
            assert endpoints_with_examples >= baseline["endpoints_with_examples"], (
                f"Endpoints with examples {endpoints_with_examples} regressed below baseline "
                f"{baseline['endpoints_with_examples']}"
            )
            assert example_coverage + FLOAT_TOLERANCE >= baseline["example_percentage"], (
                f"Example coverage {example_coverage:.2%} regressed below baseline "
                f"{baseline['example_percentage']:.2%}"
            )

    def test_success_json_responses_have_examples(self, documentation_validator):
        """JSON 成功响应必须提供 example；Prometheus 文本端点不计入该口径。"""
        missing_examples = documentation_validator.find_success_json_response_example_gaps()

        assert not missing_examples, (
            "JSON success responses missing examples: "
            f"{missing_examples}"
        )

    def test_error_response_documentation(self, documentation_validator):
        """Test that endpoints document error responses"""
        baseline = load_documentation_baseline()
        results = documentation_validator.validate_endpoint_documentation()

        endpoints_with_errors = sum(1 for ep in results if ep["documentation"]["has_error_responses"])

        total_endpoints = len(results)
        if total_endpoints > 0:
            error_doc_coverage = endpoints_with_errors / total_endpoints
            assert (
                endpoints_with_errors >= baseline["endpoints_with_errors"]
            ), (
                f"Endpoints with error documentation {endpoints_with_errors} regressed below baseline "
                f"{baseline['endpoints_with_errors']}"
            )
            assert (
                error_doc_coverage + FLOAT_TOLERANCE >= baseline["error_response_percentage"]
            ), (
                f"Error response documentation coverage {error_doc_coverage:.2%} regressed below baseline "
                f"{baseline['error_response_percentage']:.2%}"
            )

    def test_authentication_documentation(self, documentation_validator):
        """Test that authentication is properly documented"""
        issues = documentation_validator.validate_authentication_documentation()

        assert not issues, f"Authentication documentation issues: {issues}"

    def test_schema_definition_completeness(self, documentation_validator):
        """Test that schema definitions are complete"""
        baseline = load_documentation_baseline()
        issues = documentation_validator.validate_schema_definitions()

        assert len(issues) <= baseline["schema_issue_count"], (
            f"Schema definition issues {len(issues)} exceed baseline {baseline['schema_issue_count']}: {issues}"
        )

    def test_comprehensive_documentation_validation(self, documentation_validator):
        """Run comprehensive documentation validation"""
        baseline = load_documentation_baseline()
        results = documentation_validator.run_comprehensive_validation()

        # Generate and print report
        report = documentation_validator.generate_report()
        print(f"\n{report}")

        # Quality thresholds
        total_endpoints = results["summary"]["total_endpoints"]
        if total_endpoints == 0:
            pytest.skip("No endpoints found to validate")

        # Calculate percentages
        documented_percentage = results["summary"]["documented_endpoints"] / total_endpoints
        example_percentage = results["summary"]["endpoints_with_examples"] / total_endpoints
        error_doc_percentage = results["summary"]["endpoints_with_errors"] / total_endpoints

        # Stage A 技术债治理：冻结当前文档质量基线，后续仅允许改善或持平。
        assert results["summary"]["documented_endpoints"] >= baseline["documented_endpoints"], (
            f"Documented endpoints {results['summary']['documented_endpoints']} regressed below baseline "
            f"{baseline['documented_endpoints']}"
        )
        assert (
            documented_percentage + FLOAT_TOLERANCE >= baseline["documented_percentage"]
        ), (
            f"Documentation coverage {documented_percentage:.2%} regressed below baseline "
            f"{baseline['documented_percentage']:.2%}"
        )

        assert (
            results["summary"]["endpoints_with_examples"] >= baseline["endpoints_with_examples"]
        ), (
            f"Endpoints with examples {results['summary']['endpoints_with_examples']} regressed below baseline "
            f"{baseline['endpoints_with_examples']}"
        )
        assert (
            example_percentage + FLOAT_TOLERANCE >= baseline["example_percentage"]
        ), (
            f"Example coverage {example_percentage:.2%} regressed below baseline "
            f"{baseline['example_percentage']:.2%}"
        )

        assert (
            results["summary"]["endpoints_with_errors"] >= baseline["endpoints_with_errors"]
        ), (
            f"Endpoints with error documentation {results['summary']['endpoints_with_errors']} regressed below baseline "
            f"{baseline['endpoints_with_errors']}"
        )
        assert (
            error_doc_percentage + FLOAT_TOLERANCE >= baseline["error_response_percentage"]
        ), (
            f"Error response documentation {error_doc_percentage:.2%} regressed below baseline "
            f"{baseline['error_response_percentage']:.2%}"
        )

        assert (
            results["summary"]["total_issues"] <= baseline["total_issues"]
        ), (
            f"Documentation issues {results['summary']['total_issues']} exceed baseline "
            f"{baseline['total_issues']}"
        )

    def test_swagger_ui_accessibility(self, test_client):
        """Test that Swagger UI is accessible"""
        response = test_client.get("/api/docs")
        assert response.status_code == 200, "Swagger UI should be accessible"

    def test_openapi_json_accessibility(self, test_client):
        """Test that OpenAPI JSON is accessible and valid"""
        response = test_client.get("/openapi.json")
        assert response.status_code == 200, "OpenAPI JSON should be accessible"

        # Try to parse the JSON
        try:
            data = response.json()
            assert isinstance(data, dict), "OpenAPI JSON should be a valid JSON object"
            assert "openapi" in data, "OpenAPI JSON should contain 'openapi' field"
            assert "paths" in data, "OpenAPI JSON should contain 'paths' field"
        except json.JSONDecodeError:
            pytest.fail("OpenAPI JSON is not valid JSON")

    def test_redoc_accessibility(self, test_client):
        """Test that ReDoc is accessible"""
        response = test_client.get("/api/redoc")
        assert response.status_code == 200, "ReDoc should be accessible"

    def test_docs_ui_routes_are_excluded_from_contract_validation(self, documentation_validator):
        """Swagger/ReDoc UI 路由不属于 OpenAPI 契约端点，不应计入文档债。"""
        results = documentation_validator.validate_endpoint_documentation()
        validated_paths = {item["path"] for item in results}

        assert "/api/docs" not in validated_paths
        assert "/api/redoc" not in validated_paths

    def test_monitoring_related_schemas_have_types_and_descriptions(self, documentation_validator):
        """监控/告警高频 schema 不应再出现字段类型或描述缺失。"""
        issues = documentation_validator.validate_schema_definitions()
        target_schemas = {
            "AlertRuleCreate",
            "AlertRuleUpdate",
            "AlertRuleResponse",
            "AlertRecordResponse",
            "RealtimeMonitoringResponse",
            "DragonTigerListResponse",
            "MonitoringSummaryResponse",
            "SignalHistoryResponse",
            "SignalQualityReportResponse",
            "StrategyRealtimeMonitoringResponse",
        }

        target_issues = [
            issue
            for issue in issues
            if any(
                issue.startswith(f"Schema {schema} ")
                or f" in {schema} " in issue
                for schema in target_schemas
            )
        ]

        assert not target_issues, f"Monitoring-related schema issues remain: {target_issues}"

    def test_misc_contract_schemas_have_descriptions_and_explicit_types(self, documentation_validator):
        """剩余高频契约 schema 应补齐字段描述，并清理 Any 造成的类型缺失。"""
        issues = documentation_validator.validate_schema_definitions()
        target_schemas = {
            "AllIndicatorsResponse",
            "AuditLogResponse",
            "CalculationResponse",
            "IndicatorInfo",
            "LogQueryResponse",
            "OptimizationResponse",
            "SentimentResponse",
            "StrategyParameter",
            "SystemLog",
            "TaskResponse",
            "TaskStatistics",
            "TechnicalIndicatorResponse",
        }

        target_issues = [
            issue
            for issue in issues
            if any(
                issue.startswith(f"Schema {schema} ")
                or f" in {schema} " in issue
                for schema in target_schemas
            )
        ]

        assert not target_issues, f"Misc contract schema issues remain: {target_issues}"

    def test_next_wave_contract_schemas_have_descriptions(self, documentation_validator):
        """下一批高频 schema 不应继续缺少对象或字段描述。"""
        issues = documentation_validator.validate_schema_definitions()
        target_schemas = {
            "AddStrategyRequest",
            "AlertRecordsResponse",
            "BacktestResult",
            "CalculationRequest",
            "ChipRaceResponse",
            "ConnectionTestRequest",
            "ConnectionTestResponse",
            "LongHuBangResponse",
            "MessageResponse",
            "MonitoringControlRequest",
            "StrategyConfig",
            "StrategyCreateRequest",
            "TaskConfig",
            "User",
        }

        target_issues = [
            issue
            for issue in issues
            if any(
                issue.startswith(f"Schema {schema} ")
                or f" in {schema} " in issue
                for schema in target_schemas
            )
        ]

        assert not target_issues, f"Next-wave schema issues remain: {target_issues}"

    def test_autogenerated_contract_schemas_have_descriptions(self, documentation_validator):
        """自动生成的登录/校验/统一响应 schema 也必须满足契约描述要求。"""
        issues = documentation_validator.validate_schema_definitions()
        target_schemas = {
            "Body_compat_login_api_auth_login_post",
            "Body_login_for_access_token_api_v1_auth_login_post",
            "HTTPValidationError",
            "StockQuote",
            "UnifiedResponse_Dict_str__Any__",
            "UnifiedResponse_HealthScoreWithRiskResponse_",
            "UnifiedResponse_List_AlertResponse__",
            "UnifiedResponse_List_AlertRuleResponse__",
            "UnifiedResponse_List_HealthScoreResponse__",
            "UnifiedResponse_List_HealthScoreWithRiskResponse__",
            "UnifiedResponse_List_RebalanceSuggestionResponse__",
            "UnifiedResponse_List_WatchlistResponse__",
            "UnifiedResponse_List_WatchlistStockResponse__",
            "UnifiedResponse_MarketOverview_",
            "UnifiedResponse_MarketRegimeResponse_",
            "UnifiedResponse_NoneType_",
            "UnifiedResponse_PortfolioAnalysisResponse_",
            "UnifiedResponse_PortfolioSummaryResponse_",
            "UnifiedResponse_WatchlistResponse_",
            "UnifiedResponse_WatchlistStockResponse_",
            "ValidationError",
        }

        target_issues = [
            issue
            for issue in issues
            if any(
                issue.startswith(f"Schema {schema} ")
                or f" in {schema} " in issue
                for schema in target_schemas
            )
        ]

        assert not target_issues, f"Autogenerated schema issues remain: {target_issues}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
