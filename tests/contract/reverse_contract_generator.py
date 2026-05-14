"""Compatibility wrapper for the canonical reverse contract generator."""

from __future__ import annotations

from tests.contract_support.reverse_contract_generator import (
    Endpoint,
    HTTPScanner,
    OpenAPIScraper,
    ReverseContractGenerator,
    ScanResult,
    ScannerType,
    SwaggerUIParser,
    WebScraper,
    demo_reverse_contract_generator,
)

__all__ = [
    "Endpoint",
    "HTTPScanner",
    "OpenAPIScraper",
    "ReverseContractGenerator",
    "ScanResult",
    "ScannerType",
    "SwaggerUIParser",
    "WebScraper",
    "demo_reverse_contract_generator",
]
