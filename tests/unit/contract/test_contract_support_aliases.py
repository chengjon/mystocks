from __future__ import annotations


def test_contract_test_engine_legacy_module_reexports_canonical_engine() -> None:
    from tests.contract.contract_engine import ContractTestEngine as legacy_engine
    from tests.contract_support.engine import ContractTestEngine as canonical_engine

    assert legacy_engine is canonical_engine
