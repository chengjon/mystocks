"""Compatibility wrapper for canonical contract support models."""

from __future__ import annotations

from tests.contract_support.models import (
    ContractTestCase,
    ContractTestConfig,
    ContractTestReport,
    ContractTestSuite,
    ContractType,
    TestCategory,
    TestExecutionResult,
    TestStatus,
    ValidationRuleFactory,
)

__all__ = [
    "ContractTestCase",
    "ContractTestConfig",
    "ContractTestReport",
    "ContractTestSuite",
    "ContractType",
    "TestCategory",
    "TestExecutionResult",
    "TestStatus",
    "ValidationRuleFactory",
]
