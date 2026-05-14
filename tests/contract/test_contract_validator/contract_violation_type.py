"""Compatibility wrapper for canonical legacy contract validator types."""

from __future__ import annotations

from tests.contract_support.validator_legacy.contract_violation_type import (
    ContractSpec,
    ContractTest,
    ContractViolation,
    ContractViolationType,
    DeprecationValidator,
    RequestValidator,
    SchemaValidator,
    ValidationLevel,
    ValidationResult,
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
]
