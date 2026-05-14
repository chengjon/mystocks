"""Compatibility wrapper for the canonical legacy contract validator."""

from __future__ import annotations

from tests.contract_support.validator_legacy.contract_validator import (
    ContractValidator,
    demo_contract_validator,
)

__all__ = ["ContractValidator", "demo_contract_validator"]
