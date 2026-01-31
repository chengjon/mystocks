"""
Contract Testing Framework for MyStocks API

Implements Dredd-like contract testing for OpenAPI specifications.
Verifies API implementations against OpenAPI/Swagger specifications.

Modules:
    - contract_engine: Core contract testing engine
    - spec_validator: OpenAPI specification validation
    - test_hooks: Pre/post hooks for test setup and cleanup
    - api_consistency_checker: API vs spec consistency verification
"""

from .api_consistency_checker import (
    APIConsistencyChecker,
    DiscrepancyReport,
    DiscrepancyType,
)
from .contract_engine import ContractTestEngine
from .report_generator import ContractTestReportGenerator
from .spec_validator import APIEndpoint, HTTPMethod, Parameter, SpecificationValidator
from .test_hooks import Hook, HookContext, HookType, TestHooksManager

__all__ = [
    "ContractTestEngine",
    "SpecificationValidator",
    "APIEndpoint",
    "HTTPMethod",
    "Parameter",
    "TestHooksManager",
    "HookContext",
    "HookType",
    "Hook",
    "APIConsistencyChecker",
    "DiscrepancyReport",
    "DiscrepancyType",
    "ContractTestReportGenerator",
]
