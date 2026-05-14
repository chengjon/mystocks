"""Compatibility wrapper for the canonical contract generator support module."""

from __future__ import annotations

from tests.contract_support.contract_generator import (
    APISpec,
    ContractGenerator,
    ContractSourceType,
    FastAPIParser,
    MediaType,
    OpenAPISpecGenerator,
    Parameter,
    PathItem,
    Response,
    TypeAnalyzer,
    ValidationLevel,
    demo_contract_generator,
)

__all__ = [
    "APISpec",
    "ContractGenerator",
    "ContractSourceType",
    "FastAPIParser",
    "MediaType",
    "OpenAPISpecGenerator",
    "Parameter",
    "PathItem",
    "Response",
    "TypeAnalyzer",
    "ValidationLevel",
    "demo_contract_generator",
]
