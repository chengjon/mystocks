import importlib


def test_contract_test_validator_legacy_alias_points_to_contract_validator():
    package = importlib.import_module("tests.contract.test_contract_validator")

    assert package.ContractTestValidator is package.ContractValidator


def test_security_compliance_tester_legacy_alias_points_to_compliance_test_engine():
    package = importlib.import_module("tests.security.test_security_compliance")

    assert package.SecurityComplianceTester is package.ComplianceTestEngine
