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

from .contract_engine import ContractTestEngine
from .spec_validator import SpecificationValidator, APIEndpoint, HTTPMethod, Parameter
from .test_hooks import TestHooksManager, HookContext, HookType, Hook
from .api_consistency_checker import APIConsistencyChecker, DiscrepancyReport, DiscrepancyType
from .report_generator import ContractTestReportGenerator

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
