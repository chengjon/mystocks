from __future__ import annotations

from tests.api.file_tests import conftest as file_tests_conftest


def test_contract_specs_are_marked_as_historical_snapshots() -> None:
    specs = file_tests_conftest.contract_specs.__wrapped__()

    market_spec = specs["market-data"]
    assert market_spec["_meta"]["source_type"] == "historical_snapshot"
    assert market_spec["_meta"]["is_contract_truth"] is False
    assert "runtime OpenAPI" in market_spec["_meta"]["usage_note"]
