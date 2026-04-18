import importlib


def test_security_compliance_utils_imports_split_symbols():
    package = importlib.import_module("tests.security.test_security_compliance")
    utils = importlib.import_module("tests.security.test_security_compliance.utils")

    assert utils.ComplianceTestEngine is package.ComplianceTestEngine
    assert utils.ComplianceStandard is package.ComplianceStandard
    assert utils.ComplianceReport is package.ComplianceReport
    assert utils.ComplianceLevel is package.ComplianceLevel


def test_security_vulnerability_utils_imports_split_scanner():
    package = importlib.import_module("tests.security.test_security_vulnerabilities")
    utils = importlib.import_module("tests.security.test_security_vulnerabilities.utils")

    assert utils.SecurityVulnerabilityScanner is package.SecurityVulnerabilityScanner
