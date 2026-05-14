#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 契约测试框架
提供 API 契约测试、服务间集成测试和接口一致性验证
"""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .contract_engine import ContractTestEngine
    from .contract_validator import ContractValidator
    from .models import ContractTestCase, ContractTestConfig, ContractTestSuite
    from .report_generator import ContractTestReportGenerator
    from .test_executor import ContractTestExecutor

__all__ = [
    "ContractTestEngine",
    "ContractValidator",
    "ContractTestExecutor",
    "ContractTestReportGenerator",
    "ContractTestConfig",
    "ContractTestSuite",
    "ContractTestCase",
]

_EXPORTS = {
    "ContractTestEngine": (".contract_engine", "ContractTestEngine"),
    "ContractValidator": (".contract_validator", "ContractValidator"),
    "ContractTestExecutor": (".test_executor", "ContractTestExecutor"),
    "ContractTestReportGenerator": (".report_generator", "ContractTestReportGenerator"),
    "ContractTestConfig": (".models", "ContractTestConfig"),
    "ContractTestSuite": (".models", "ContractTestSuite"),
    "ContractTestCase": (".models", "ContractTestCase"),
}


def __getattr__(name: str) -> Any:
    """Load compatibility exports lazily to avoid contract_support import cycles."""
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name, attribute_name = _EXPORTS[name]
    value = getattr(import_module(module_name, package=__name__), attribute_name)
    globals()[name] = value
    return value
