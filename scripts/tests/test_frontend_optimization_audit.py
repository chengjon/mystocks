"""Tests for frontend optimization audit automation."""

from pathlib import Path

import pytest

from scripts.dev.frontend_optimization_audit import (
    extract_plan_rows,
    extract_router_page_map,
    match_api_pattern,
    validate_api_verification,
    validate_component_mapping,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTER_FILE = REPO_ROOT / "web/frontend/src/router/index.ts"
PLAN_FILE = REPO_ROOT / "docs/plans/frontend-page-optimization-list.md"


def test_extract_router_page_map_includes_strategy_parameters() -> None:
    routes = extract_router_page_map(ROUTER_FILE.read_text(encoding="utf-8"))

    assert "/strategy/parameters" in routes
    assert routes["/strategy/parameters"]["component_path"] == "artdeco-pages/strategy-tabs/StrategyParametersTab.vue"
    assert routes["/strategy/parameters"]["api"] == "/api/v1/strategy/strategies"


def test_extract_plan_rows_reads_34_records() -> None:
    rows = extract_plan_rows(PLAN_FILE.read_text(encoding="utf-8"))

    assert len(rows) == 34
    technical_row = next(item for item in rows if item["path"] == "/market/technical")
    assert technical_row["component_path"] == "artdeco-pages/market-tabs/MarketKLineTab.vue"
    assert technical_row["api_status"] == "verified"


def test_component_mapping_validation_passes_for_current_doc() -> None:
    routes = extract_router_page_map(ROUTER_FILE.read_text(encoding="utf-8"))
    rows = extract_plan_rows(PLAN_FILE.read_text(encoding="utf-8"))

    mismatches = validate_component_mapping(rows, routes)
    assert mismatches == []


@pytest.mark.parametrize(
    ("pattern", "available", "expected"),
    [
        ("/api/v1/market/kline", {"/api/v1/market/kline"}, True),
        ("/api/watchlist", {"/api/watchlist/"}, True),
        ("/api/v1/announcement", {"/api/v1/announcement/announcement/list"}, True),
        (
            "/api/v1/strategy/backtest*",
            {"/api/v1/strategy/backtest", "/api/v1/strategy/backtest/run"},
            True,
        ),
        ("/api/not-exists", {"/api/v1/market/kline"}, False),
    ],
)
def test_match_api_pattern(pattern: str, available: set[str], expected: bool) -> None:
    assert match_api_pattern(pattern, available) is expected


def test_validate_api_verification_only_checks_verified_rows() -> None:
    rows = [
        {"path": "/p1", "api": "/api/v1/market/kline", "api_status": "verified"},
        {"path": "/p2", "api": "/api/v1/not-found", "api_status": "pending"},
        {"path": "/p3", "api": "/api/v1/strategy/backtest*", "api_status": "verified"},
    ]
    backend_paths = {
        "/api/v1/market/kline",
        "/api/v1/strategy/backtest",
        "/api/v1/strategy/backtest/run",
    }

    issues = validate_api_verification(rows, backend_paths)
    assert issues == []
