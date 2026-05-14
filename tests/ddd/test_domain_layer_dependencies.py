"""DDD layer dependency guardrails."""

from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOMAIN_ROOT = PROJECT_ROOT / "src" / "domain"


def _imported_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)

    return modules


def test_domain_layer_does_not_import_outer_layers() -> None:
    violations: list[str] = []
    blocked_prefixes = ("src.application", "src.infrastructure")

    for path in DOMAIN_ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue

        for module in _imported_modules(path):
            if module in blocked_prefixes or module.startswith(tuple(f"{prefix}." for prefix in blocked_prefixes)):
                rel_path = path.relative_to(PROJECT_ROOT)
                violations.append(f"{rel_path}: {module}")

    assert violations == []


def test_infrastructure_concurrency_exception_maps_to_portfolio_domain_exception() -> None:
    from src.domain.portfolio.exceptions import PortfolioConcurrencyException
    from src.infrastructure.persistence.exceptions import ConcurrencyException

    assert issubclass(ConcurrencyException, PortfolioConcurrencyException)

    error = ConcurrencyException("stale version", entity_type="Portfolio", entity_id="p-1")

    assert error.entity_type == "Portfolio"
    assert error.entity_id == "p-1"
    assert str(error) == "Concurrency conflict for Portfolio p-1: stale version"


def test_application_incremental_calculator_import_path_remains_compatible() -> None:
    from src.application.services.performance_optimizer import IncrementalCalculator as ApplicationIncrementalCalculator
    from src.domain.portfolio.service.incremental_calculator import IncrementalCalculator as DomainIncrementalCalculator

    assert ApplicationIncrementalCalculator is DomainIncrementalCalculator
