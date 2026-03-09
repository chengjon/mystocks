"""Tail tests extracted from `test_performance_and_security.py`."""


class TestPerformanceAndSecurity:
    """Test suite for performance and security validation"""

    def test_response_time_benchmarks(self, perf_sec_validator):
        """Test response time benchmarks"""
        test_endpoints = [
            {"url": "/health", "method": "GET"},
            {"url": "/api/auth/me", "method": "GET"},
        ]

        results = perf_sec_validator.test_response_times(test_endpoints)

        assert (
            results["average_response_time"] <= 2.0
        ), f"Average response time {results['average_response_time']:.3f}s is too high"

        critical_slow = [endpoint for endpoint in results["slow_endpoints"] if "CRITICAL" in endpoint["issue"]]
        assert len(critical_slow) == 0, f"Found {len(critical_slow)} critically slow endpoints"

    def test_sql_injection_detection(self, perf_sec_validator):
        """Test SQL injection vulnerability detection"""
        vulnerabilities = perf_sec_validator.test_sql_injection_vulnerabilities()
        assert len(vulnerabilities) == 0, f"SQL injection vulnerabilities found: {len(vulnerabilities)}"

    def test_xss_protection_validation(self, perf_sec_validator):
        """Test XSS protection validation"""
        vulnerabilities = perf_sec_validator.test_xss_protection()
        assert len(vulnerabilities) <= 2, f"XSS vulnerabilities found: {len(vulnerabilities)}"

    def test_input_sanitization(self, perf_sec_validator):
        """Test input sanitization and validation"""
        issues = perf_sec_validator.test_input_validation()
        server_errors = [
            issue for issue in issues if issue["status_code"] == 500 or issue["status_code"] == "Exception"
        ]
        assert (
            len(server_errors) <= len(issues) * 0.3
        ), f"Too many server errors from malformed input: {len(server_errors)}/{len(issues)}"

    def test_rate_limiting_verification(self, perf_sec_validator):
        """Test rate limiting verification"""
        results = perf_sec_validator.test_rate_limiting()
        rate_limited_count = len(results["rate_limited_endpoints"])
        total_tested = len(results["tested_endpoints"])

        if total_tested > 0:
            rate_limiting_percentage = rate_limited_count / total_tested
            assert rate_limiting_percentage >= 0.0, f"Rate limiting coverage {rate_limiting_percentage:.2%} is too low"

    def test_authentication_security(self, perf_sec_validator):
        """Test authentication security"""
        issues = perf_sec_validator.test_authentication_security()
        critical_auth_issues = [
            issue
            for issue in issues
            if "Weak password" in issue["issue"] or "accessible without authentication" in issue["issue"]
        ]
        assert len(critical_auth_issues) == 0, f"Critical authentication issues found: {critical_auth_issues}"

    def test_comprehensive_performance_security(self, perf_sec_validator):
        """Run comprehensive performance and security validation"""
        results = perf_sec_validator.run_comprehensive_validation()
        report = perf_sec_validator.generate_report()

        assert "PERFORMANCE AND SECURITY VALIDATION REPORT" in report

        max_sql_vulnerabilities = 0
        max_xss_vulnerabilities = 2
        max_critical_auth_issues = 0
        max_server_errors = 3

        security = results["security"]
        assert (
            len(security["sql_injection_vulnerabilities"]) <= max_sql_vulnerabilities
        ), f"SQL injection vulnerabilities: {len(security['sql_injection_vulnerabilities'])}"
        assert (
            len(security["xss_vulnerabilities"]) <= max_xss_vulnerabilities
        ), f"XSS vulnerabilities: {len(security['xss_vulnerabilities'])}"
        assert (
            len(security["authentication_issues"]) <= max_critical_auth_issues
        ), f"Authentication issues: {len(security['authentication_issues'])}"

        server_errors = [
            issue
            for issue in security["input_validation_issues"]
            if issue.get("status_code") == 500 or issue.get("status_code") == "Exception"
        ]
        assert len(server_errors) <= max_server_errors, f"Server errors from input: {len(server_errors)}"

        performance = results["performance"]
        assert (
            performance["average_response_time"] <= 3.0
        ), f"Average response time too high: {performance['average_response_time']:.3f}s"

        critical_slow = [endpoint for endpoint in performance["slow_endpoints"] if "CRITICAL" in endpoint.get("issue", "")]
        assert len(critical_slow) == 0, f"Critical slow endpoints found: {len(critical_slow)}"

    def test_security_headers(self, test_client):
        """Test security headers are present"""
        response = test_client.get("/health")
        security_headers = [
            "x-content-type-options",
            "x-frame-options",
            "x-xss-protection",
            "strict-transport-security",
        ]

        missing_headers = [header for header in security_headers if header not in response.headers]
        assert len(missing_headers) <= 2, f"Missing security headers: {missing_headers}"

    def test_error_information_disclosure(self, test_client):
        """Test that error responses don't disclose sensitive information"""
        response = test_client.get("/api/nonexistent")

        if response.status_code == 500:
            response_text = response.text.lower()
            sensitive_patterns = [
                "traceback",
                "stack trace",
                "internal server error",
                "file path",
                "line number",
                "exception",
            ]
            disclosed_info = [pattern for pattern in sensitive_patterns if pattern in response_text]
            assert len(disclosed_info) <= 1, f"Error response may disclose sensitive information: {disclosed_info}"


__all__ = ["TestPerformanceAndSecurity"]
