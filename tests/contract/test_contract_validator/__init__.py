"""Compatibility wrapper for legacy contract validator split package."""

from __future__ import annotations

from tests.contract_support.validator_legacy import (
    ContractSpec,
    ContractTest,
    ContractTestValidator,
    ContractValidator,
    ContractViolation,
    ContractViolationType,
    DeprecationValidator,
    RequestValidator,
    SchemaValidator,
    ValidationLevel,
    ValidationResult,
    demo_contract_validator,
)

__all__ = [
    "ContractViolationType",
    "ValidationLevel",
    "ContractSpec",
    "ContractTest",
    "ContractViolation",
    "ValidationResult",
    "SchemaValidator",
    "RequestValidator",
    "DeprecationValidator",
    "ContractValidator",
    "ContractTestValidator",
    "demo_contract_validator",
]
