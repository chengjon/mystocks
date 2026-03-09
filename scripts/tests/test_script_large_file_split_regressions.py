from __future__ import annotations

import importlib
from pathlib import Path


def _line_count(path: str) -> int:
    return sum(1 for _ in Path(path).read_text(encoding="utf-8").splitlines())


def test_validate_gitignore_test_module_stays_below_800_lines() -> None:
    assert _line_count("scripts/tests/test_validate_gitignore.py") < 800


def test_validate_gitignore_tail_helper_remains_importable() -> None:
    helper = importlib.import_module("scripts._test_validate_gitignore_tail")

    assert helper is not None
    assert callable(helper.TestMainFunction)
    assert callable(helper.TestIntegrationScenarios)


def test_check_api_health_v2_test_module_stays_below_800_lines() -> None:
    assert _line_count("scripts/tests/test_check_api_health_v2.py") < 800


def test_check_api_health_v2_tail_helper_remains_importable() -> None:
    helper = importlib.import_module("scripts._test_check_api_health_v2_tail")

    assert helper is not None
    assert callable(helper.TestMainFunction)
    assert callable(helper.TestIntegrationScenarios)
    assert callable(helper.TestEdgeCasesAndErrorHandling)
