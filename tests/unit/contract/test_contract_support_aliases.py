from __future__ import annotations


def test_contract_test_engine_legacy_module_reexports_canonical_engine() -> None:
    from tests.contract.contract_engine import ContractTestEngine as legacy_engine
    from tests.contract_support.engine import ContractTestEngine as canonical_engine

    assert legacy_engine is canonical_engine


def test_legacy_contract_support_modules_reexport_canonical_modules() -> None:
    from tests.contract.contract_generator import ContractGenerator as legacy_generator
    from tests.contract.contract_test_executor import ContractTestExecutor as legacy_contract_executor
    from tests.contract.contract_validator import ContractValidator as legacy_validator
    from tests.contract.executor import ContractTestExecutor as legacy_executor
    from tests.contract.models import ContractTestCase as legacy_case
    from tests.contract.report_generator import ContractTestReportGenerator as legacy_report_generator
    from tests.contract.reverse_contract_generator import ReverseContractGenerator as legacy_reverse_generator
    from tests.contract.test_contract_validator import ContractValidator as legacy_split_validator
    from tests.contract.test_contract_validator.contract_violation_type import (
        ContractViolationType as legacy_violation_type,
    )
    from tests.contract_support.contract_generator import ContractGenerator as canonical_generator
    from tests.contract_support.contract_test_executor import ContractTestExecutor as canonical_contract_executor
    from tests.contract_support.executor import ContractTestExecutor as canonical_executor
    from tests.contract_support.models import ContractTestCase as canonical_case
    from tests.contract_support.report_generator import ContractTestReportGenerator as canonical_report_generator
    from tests.contract_support.reverse_contract_generator import ReverseContractGenerator as canonical_reverse_generator
    from tests.contract_support.validator import ContractValidator as canonical_validator
    from tests.contract_support.validator_legacy import ContractValidator as canonical_split_validator
    from tests.contract_support.validator_legacy.contract_violation_type import (
        ContractViolationType as canonical_violation_type,
    )

    assert legacy_generator is canonical_generator
    assert legacy_contract_executor is canonical_contract_executor
    assert legacy_validator is canonical_validator
    assert legacy_executor is canonical_executor
    assert legacy_case is canonical_case
    assert legacy_report_generator is canonical_report_generator
    assert legacy_reverse_generator is canonical_reverse_generator
    assert legacy_split_validator is canonical_split_validator
    assert legacy_violation_type is canonical_violation_type
