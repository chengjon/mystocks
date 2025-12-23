"""Dummy SecurityVulnerabilityScanner for testing purposes."""


class SecurityVulnerabilityScanner:
    def run_comprehensive_security_scan(self) -> dict:
        return {"vulnerabilities_found": 0, "report": "clean"}
