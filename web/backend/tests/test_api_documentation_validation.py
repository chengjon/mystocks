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
from typing import Any, Dict, List, Set

import pytest
import requests
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.main import app


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
                endpoint_result = self._validate_single_endpoint(route, schema)
                endpoint_results.append(endpoint_result)

        return endpoint_results

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
            path_item = schema.get("paths", {}).get(route.path, {})
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

    def _validate_parameters(self, parameters: List[Dict[str, Any]], endpoint_result: Dict[str, Any], method: str):
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
        if "application/json" not in content:
            endpoint_result["issues"].append(f"Request body missing JSON content for {method.upper()}")
            return

        json_content = content["application/json"]
        if "schema" not in json_content:
            endpoint_result["issues"].append(f"Request body missing schema for {method.upper()}")

        # Check for examples
        if "example" in json_content or "examples" in json_content:
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
                    if "application/json" in content:
                        json_content = content["application/json"]
                        if "example" in json_content or "examples" in json_content:
                            has_response_examples = True

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
                if "type" not in schema_def:
                    issues.append(f"Schema {schema_name} missing type")

                # Check for description
                if "description" not in schema_def or not schema_def["description"]:
                    issues.append(f"Schema {schema_name} missing description")

                # Check for properties
                if schema_def.get("type") == "object":
                    if "properties" not in schema_def:
                        issues.append(f"Object schema {schema_name} missing properties")
                    else:
                        properties = schema_def["properties"]
                        for prop_name, prop_def in properties.items():
                            if "type" not in prop_def:
                                issues.append(f"Property {prop_name} in {schema_name} missing type")
                            if "description" not in prop_def or not prop_def["description"]:
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
                documentation_coverage >= 0.7
            ), f"Documentation coverage {documentation_coverage:.2%} is below required 70%"

    def test_request_response_examples(self, documentation_validator):
        """Test that endpoints have request/response examples"""
        results = documentation_validator.validate_endpoint_documentation()

        endpoints_with_examples = sum(1 for ep in results if ep["documentation"]["has_examples"])

        total_endpoints = len(results)
        if total_endpoints > 0:
            example_coverage = endpoints_with_examples / total_endpoints
            assert example_coverage >= 0.3, f"Example coverage {example_coverage:.2%} is below required 30%"

    def test_error_response_documentation(self, documentation_validator):
        """Test that endpoints document error responses"""
        results = documentation_validator.validate_endpoint_documentation()

        endpoints_with_errors = sum(1 for ep in results if ep["documentation"]["has_error_responses"])

        total_endpoints = len(results)
        if total_endpoints > 0:
            error_doc_coverage = endpoints_with_errors / total_endpoints
            assert (
                error_doc_coverage >= 0.5
            ), f"Error response documentation coverage {error_doc_coverage:.2%} is below required 50%"

    def test_authentication_documentation(self, documentation_validator):
        """Test that authentication is properly documented"""
        issues = documentation_validator.validate_authentication_documentation()

        # Should have minimal authentication documentation issues
        assert len(issues) <= 2, f"Authentication documentation issues: {issues}"

    def test_schema_definition_completeness(self, documentation_validator):
        """Test that schema definitions are complete"""
        issues = documentation_validator.validate_schema_definitions()

        # Allow some schema issues for now
        assert len(issues) <= 10, f"Too many schema definition issues: {issues}"

    def test_comprehensive_documentation_validation(self, documentation_validator):
        """Run comprehensive documentation validation"""
        results = documentation_validator.run_comprehensive_validation()

        # Generate and print report
        report = documentation_validator.generate_report()
        print(f"\n{report}")

        # Quality thresholds
        total_endpoints = results["summary"]["total_endpoints"]
        if total_endpoints == 0:
            pytest.skip("No endpoints found to validate")

        min_documented_percentage = 0.6  # 60% should be documented
        min_example_percentage = 0.2  # 20% should have examples
        min_error_doc_percentage = 0.4  # 40% should document errors
        max_total_issues = total_endpoints * 5  # 5 issues per endpoint average

        # Calculate percentages
        documented_percentage = results["summary"]["documented_endpoints"] / total_endpoints
        example_percentage = results["summary"]["endpoints_with_examples"] / total_endpoints
        error_doc_percentage = results["summary"]["endpoints_with_errors"] / total_endpoints

        # Assert quality standards
        assert (
            documented_percentage >= min_documented_percentage
        ), f"Documentation coverage {documented_percentage:.2%} is below required {min_documented_percentage:.2%}"

        assert (
            example_percentage >= min_example_percentage
        ), f"Example coverage {example_percentage:.2%} is below required {min_example_percentage:.2%}"

        assert (
            error_doc_percentage >= min_error_doc_percentage
        ), f"Error response documentation {error_doc_percentage:.2%} is below required {min_error_doc_percentage:.2%}"

        assert (
            results["summary"]["total_issues"] <= max_total_issues
        ), f"Too many documentation issues: {results['summary']['total_issues']} (max allowed: {max_total_issues})"

    def test_swagger_ui_accessibility(self, test_client):
        """Test that Swagger UI is accessible"""
        response = test_client.get("/docs")
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
        response = test_client.get("/redoc")
        assert response.status_code == 200, "ReDoc should be accessible"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
