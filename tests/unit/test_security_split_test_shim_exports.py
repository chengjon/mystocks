import importlib


def test_compliance_test_engine_shim_re_exports_composed_class():
    shim = importlib.import_module("tests.security.test_security_compliance.compliance_test_engine")
    methods_package = importlib.import_module("tests.security.test_security_compliance.compliance_test_engine_methods")
    part1 = importlib.import_module("tests.security.test_security_compliance.compliance_test_engine_methods.part1")
    part2 = importlib.import_module("tests.security.test_security_compliance.compliance_test_engine_methods.part2")

    engine_cls = shim.ComplianceTestEngine

    assert engine_cls is methods_package.ComplianceTestEngine
    assert issubclass(engine_cls, part1.ComplianceTestEngineCoreMixin)
    assert issubclass(engine_cls, part2.ComplianceTestEngineTestTransactionIntegrityMixin)


def test_security_vulnerability_scanner_shim_re_exports_composed_class():
    shim = importlib.import_module("tests.security.test_security_vulnerabilities.security_vulnerability_scanner")
    methods_package = importlib.import_module(
        "tests.security.test_security_vulnerabilities.security_vulnerability_scanner_methods"
    )
    part1 = importlib.import_module("tests.security.test_security_vulnerabilities.security_vulnerability_scanner_methods.part1")
    part2 = importlib.import_module("tests.security.test_security_vulnerabilities.security_vulnerability_scanner_methods.part2")
    part3 = importlib.import_module("tests.security.test_security_vulnerabilities.security_vulnerability_scanner_methods.part3")

    scanner_cls = shim.SecurityVulnerabilityScanner

    assert scanner_cls is methods_package.SecurityVulnerabilityScanner
    assert issubclass(scanner_cls, part1.SecurityVulnerabilityScannerCoreMixin)
    assert issubclass(scanner_cls, part2.SecurityVulnerabilityScannerDetectIdorVulnerabilityMixin)
    assert issubclass(scanner_cls, part3.SecurityVulnerabilityScannerHardeningMixin)
