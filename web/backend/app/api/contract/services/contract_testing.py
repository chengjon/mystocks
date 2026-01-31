"""
Pytest-based Contract Testing Utilities

Provides pytest fixtures and helpers for API contract testing.
"""

import logging
from typing import Any, Generator

import pytest
import yaml
from fastapi.testclient import TestClient

from .contract_validator import ContractValidator, ValidationResult

logger = logging.getLogger(__name__)


@pytest.fixture
def contract_validator() -> Generator[ContractValidator, None, None]:
    """
    Pytest fixture for ContractValidator.

    Loads OpenAPI spec from docs/api/openapi.yaml
    """
    spec_path = "docs/api/openapi.yaml"
    try:
        with open(spec_path, "r", encoding="utf-8") as f:
            spec = yaml.safe_load(f)
        validator = ContractValidator(spec)
        yield validator
    except FileNotFoundError:
        pytest.skip(f"OpenAPI spec not found at {spec_path}")


@pytest.fixture
def api_client() -> Generator[TestClient, None, None]:
    """
    Pytest fixture for FastAPI TestClient.

    Requires the app fixture to be defined elsewhere.
    """
    try:
        from app.main import app

        with TestClient(app) as client:
            yield client
    except ImportError:
        pytest.skip("FastAPI app not available")


class ContractTestMixin:
    """
    Mixin class for pytest test classes that need contract testing.

    Usage:
        class TestUserAPI(ContractTestMixin):
            @pytest.mark.contract_test
            def test_get_user_response_conforms_to_schema(self, api_client, contract_validator):
                response = api_client.get("/api/users/1")
                assert response.status_code == 200

                result = contract_validator.validate_response(
                    path="/api/users/{user_id}",
                    method="GET",
                    status_code="200",
                    response_data=response.json()
                )
                assert result.success, f"Contract violation: {result.errors}"
    """

    def validate_response_against_contract(
        self,
        client: TestClient,
        contract_validator: ContractValidator,
        method: str,
        path: str,
        status_code: str = "200",
        **request_kwargs,
    ) -> ValidationResult:
        """
        Make request and validate response against contract.

        Args:
            client: TestClient instance
            contract_validator: ContractValidator instance
            method: HTTP method
            path: API path
            status_code: Expected status code
            **request_kwargs: Additional arguments for client.request

        Returns:
            ValidationResult
        """
        # Make the request
        response = client.request(method, path, **request_kwargs)

        # Validate response
        if response.status_code == int(status_code):
            result = contract_validator.validate_response(
                path=path, method=method, status_code=status_code, response_data=response.json()
            )
        else:
            result = ValidationResult(
                success=False,
                errors=[f"Expected status {status_code}, got {response.status_code}"],
                schema_path=f"{method} {path}",
            )

        return result


def generate_contract_tests(spec_path: str = "docs/api/openapi.yaml") -> list:
    """
    Generate pytest test cases from OpenAPI specification.

    This function can be used to dynamically generate tests for all endpoints.

    Args:
        spec_path: Path to OpenAPI specification

    Returns:
        List of test case dictionaries
    """
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    validator = ContractValidator(spec)
    test_cases = []

    for endpoint in validator.get_endpoint_schema_paths():
        for status_code, schema in endpoint.get("responses", {}).items():
            test_cases.append(
                {
                    "test_name": f"test_{endpoint['method'].lower()}_{endpoint['path'].replace('/', '_')}_{status_code}_conforms",
                    "parametrize": [endpoint["path"], endpoint["method"], status_code],
                    "description": endpoint.get("description", ""),
                    "summary": endpoint.get("summary", ""),
                }
            )

    return test_cases


class ContractAssertionHelper:
    """
    Helper class for contract-related assertions.
    """

    @staticmethod
    def assert_response_conforms(
        validator: ContractValidator, path: str, method: str, status_code: str, response_data: Any, msg: str = ""
    ) -> None:
        """
        Assert that response data conforms to OpenAPI schema.

        Args:
            validator: ContractValidator instance
            path: API path
            method: HTTP method
            status_code: Response status code
            response_data: Response body to validate
            msg: Custom assertion message
        """
        result = validator.validate_response(path, method, status_code, response_data)

        if not result.success:
            error_msg = f"Contract violation for {method} {path} {status_code}:\n"
            error_msg += "\n".join(f"  - {e}" for e in result.errors)
            if msg:
                error_msg = f"{msg}\n{error_msg}"
            pytest.fail(error_msg)

    @staticmethod
    def assert_response_has_warnings(
        validator: ContractValidator,
        path: str,
        method: str,
        status_code: str,
        response_data: Any,
        max_warnings: int = 0,
    ) -> None:
        """
        Assert that response has no more than max_warnings warnings.

        Args:
            validator: ContractValidator instance
            path: API path
            method: HTTP method
            status_code: Response status code
            response_data: Response body to validate
            max_warnings: Maximum allowed warnings
        """
        result = validator.validate_response(path, method, status_code, response_data)

        if len(result.warnings) > max_warnings:
            pytest.fail(
                f"Too many warnings for {method} {path} {status_code}: "
                f"{len(result.warnings)} > {max_warnings}\n" + "\n".join(f"  - {w}" for w in result.warnings)
            )


# Pytest markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "contract: mark test as API contract test")
    config.addinivalue_line("markers", "contract_validation: mark test as contract validation test")


def contract_test(path: str, method: str, status_code: str = "200"):
    """
    Decorator to mark a test as a contract test.

    Usage:
        @contract_test(path="/api/users", method="GET", status_code="200")
        def test_users_endpoint():
            pass
    """
    return pytest.mark.contract(path=path, method=method, status_code=status_code)
