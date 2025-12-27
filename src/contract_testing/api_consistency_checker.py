"""
API Consistency Checker

Verifies that actual API implementation matches OpenAPI specification.
Compares expected vs actual endpoints, parameters, responses, etc.

Task 12.3 Implementation: API consistency verification
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from .spec_validator import SpecificationValidator

logger = logging.getLogger(__name__)


class DiscrepancyType(str, Enum):
    """Types of discrepancies between spec and implementation"""

    MISSING_ENDPOINT = "missing_endpoint"
    EXTRA_ENDPOINT = "extra_endpoint"
    PARAMETER_MISMATCH = "parameter_mismatch"
    MISSING_PARAMETER = "missing_parameter"
    EXTRA_PARAMETER = "extra_parameter"
    RESPONSE_CODE_MISMATCH = "response_code_mismatch"
    MISSING_RESPONSE_CODE = "missing_response_code"
    EXTRA_RESPONSE_CODE = "extra_response_code"
    SECURITY_MISMATCH = "security_mismatch"
    STATUS_CODE_DOCUMENTATION = "status_code_documentation"


@dataclass
class DiscrepancyReport:
    """Report of a single discrepancy"""

    type: DiscrepancyType
    endpoint_method: str
    endpoint_path: str
    severity: str  # critical, warning, info
    description: str
    expected: Optional[str] = None
    actual: Optional[str] = None
    suggestion: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "type": self.type.value,
            "endpoint_method": self.endpoint_method,
            "endpoint_path": self.endpoint_path,
            "severity": self.severity,
            "description": self.description,
            "expected": self.expected,
            "actual": self.actual,
            "suggestion": self.suggestion,
        }


class APIConsistencyChecker:
    """
    Checks consistency between OpenAPI specification and actual API implementation.

    Identifies missing endpoints, parameter mismatches, response code discrepancies, etc.
    """

    def __init__(self, spec_validator: SpecificationValidator):
        """
        Initialize consistency checker

        Args:
            spec_validator: SpecificationValidator instance with loaded spec
        """
        self.spec_validator = spec_validator
        self.spec_endpoints = spec_validator.get_all_endpoints()
        self.api_endpoints: Dict[str, Dict] = {}
        self.discrepancies: List[DiscrepancyReport] = []

    def register_api_endpoint(
        self,
        method: str,
        path: str,
        parameters: Optional[List[str]] = None,
        response_codes: Optional[List[int]] = None,
        description: str = "",
    ) -> None:
        """
        Register an actual API endpoint for comparison

        Args:
            method: HTTP method
            path: URL path
            parameters: List of parameter names
            response_codes: List of supported response codes
            description: Endpoint description
        """
        key = f"{method.upper()} {path}"
        self.api_endpoints[key] = {
            "method": method.upper(),
            "path": path,
            "parameters": set(parameters or []),
            "response_codes": set(response_codes or []),
            "description": description,
        }

    def scan_api_documentation(self, endpoint_docs: Dict[str, Dict]) -> None:
        """
        Scan API documentation and register endpoints

        Args:
            endpoint_docs: Dictionary of endpoint documentation
        """
        for endpoint_key, doc in endpoint_docs.items():
            try:
                method, path = endpoint_key.split(" ", 1)
                self.register_api_endpoint(
                    method=method,
                    path=path,
                    parameters=doc.get("parameters", []),
                    response_codes=doc.get("response_codes", []),
                    description=doc.get("description", ""),
                )
            except Exception as e:
                logger.warning(f"⚠️  Failed to register endpoint {endpoint_key}: {e}")

    def check_consistency(self) -> List[DiscrepancyReport]:
        """
        Check consistency between specification and API

        Returns:
            List of discrepancy reports
        """
        self.discrepancies = []

        logger.info("🔍 Checking API consistency...")

        # Check for missing endpoints (in API but not in spec)
        self._check_missing_spec_endpoints()

        # Check for extra endpoints (in API but not in spec)
        self._check_extra_api_endpoints()

        # Check for parameter mismatches
        self._check_parameter_consistency()

        # Check for response code mismatches
        self._check_response_code_consistency()

        logger.info(f"✅ Consistency check complete: {len(self.discrepancies)} discrepancies found")
        return self.discrepancies

    def _check_missing_spec_endpoints(self) -> None:
        """Check for endpoints in spec but not in API"""
        spec_keys = {f"{ep.method.value.upper()} {ep.path}" for ep in self.spec_endpoints}
        api_keys = set(self.api_endpoints.keys())

        missing = spec_keys - api_keys
        for endpoint_key in missing:
            method, path = endpoint_key.split(" ", 1)

            report = DiscrepancyReport(
                type=DiscrepancyType.MISSING_ENDPOINT,
                endpoint_method=method,
                endpoint_path=path,
                severity="critical",
                description=f"Endpoint not implemented: {endpoint_key}",
                expected=endpoint_key,
                actual="Not found",
                suggestion=f"Implement {method} {path} as specified in OpenAPI",
            )
            self.discrepancies.append(report)
            logger.warning(f"⚠️  Missing endpoint: {endpoint_key}")

    def _check_extra_api_endpoints(self) -> None:
        """Check for endpoints in API but not in spec"""
        spec_keys = {f"{ep.method.value.upper()} {ep.path}" for ep in self.spec_endpoints}
        api_keys = set(self.api_endpoints.keys())

        extra = api_keys - spec_keys
        for endpoint_key in extra:
            method, path = endpoint_key.split(" ", 1)

            report = DiscrepancyReport(
                type=DiscrepancyType.EXTRA_ENDPOINT,
                endpoint_method=method,
                endpoint_path=path,
                severity="warning",
                description=f"Endpoint not documented in spec: {endpoint_key}",
                actual=endpoint_key,
                expected="Not documented",
                suggestion=f"Add {method} {path} to OpenAPI specification",
            )
            self.discrepancies.append(report)
            logger.info(f"ℹ️  Extra endpoint: {endpoint_key}")

    def _check_parameter_consistency(self) -> None:
        """Check for parameter discrepancies"""
        for endpoint in self.spec_endpoints:
            spec_key = f"{endpoint.method.value.upper()} {endpoint.path}"

            if spec_key not in self.api_endpoints:
                continue

            api_endpoint = self.api_endpoints[spec_key]
            spec_params = {p.name for p in endpoint.parameters}
            api_params = api_endpoint["parameters"]

            # Check for missing parameters
            missing_params = spec_params - api_params
            for param in missing_params:
                param_spec = next((p for p in endpoint.parameters if p.name == param), None)
                if param_spec and param_spec.required:
                    report = DiscrepancyReport(
                        type=DiscrepancyType.MISSING_PARAMETER,
                        endpoint_method=endpoint.method.value.upper(),
                        endpoint_path=endpoint.path,
                        severity="critical",
                        description=f"Required parameter '{param}' not found in API",
                        expected=param,
                        actual="Not found",
                        suggestion=f"Add '{param}' parameter to {spec_key}",
                    )
                    self.discrepancies.append(report)
                    logger.warning(f"⚠️  Missing parameter: {param} in {spec_key}")

            # Check for extra parameters
            extra_params = api_params - spec_params
            for param in extra_params:
                report = DiscrepancyReport(
                    type=DiscrepancyType.EXTRA_PARAMETER,
                    endpoint_method=endpoint.method.value.upper(),
                    endpoint_path=endpoint.path,
                    severity="info",
                    description=f"Undocumented parameter '{param}' found in API",
                    actual=param,
                    expected="Not documented",
                    suggestion=f"Document '{param}' in OpenAPI specification for {spec_key}",
                )
                self.discrepancies.append(report)
                logger.info(f"ℹ️  Extra parameter: {param} in {spec_key}")

    def _check_response_code_consistency(self) -> None:
        """Check for response code discrepancies"""
        for endpoint in self.spec_endpoints:
            spec_key = f"{endpoint.method.value.upper()} {endpoint.path}"

            if spec_key not in self.api_endpoints:
                continue

            api_endpoint = self.api_endpoints[spec_key]
            spec_codes = set(endpoint.responses.keys())
            api_codes = api_endpoint["response_codes"]

            # Check for missing response codes
            missing_codes = spec_codes - api_codes
            for code in missing_codes:
                report = DiscrepancyReport(
                    type=DiscrepancyType.MISSING_RESPONSE_CODE,
                    endpoint_method=endpoint.method.value.upper(),
                    endpoint_path=endpoint.path,
                    severity="warning",
                    description=f"Response code {code} not returned by API",
                    expected=str(code),
                    actual="Not returned",
                    suggestion=f"Ensure {code} response is handled in {spec_key}",
                )
                self.discrepancies.append(report)
                logger.warning(f"⚠️  Missing response code: {code} in {spec_key}")

            # Check for extra response codes
            extra_codes = api_codes - spec_codes
            for code in extra_codes:
                report = DiscrepancyReport(
                    type=DiscrepancyType.EXTRA_RESPONSE_CODE,
                    endpoint_method=endpoint.method.value.upper(),
                    endpoint_path=endpoint.path,
                    severity="info",
                    description=f"Response code {code} not documented in spec",
                    actual=str(code),
                    expected="Not documented",
                    suggestion=f"Document response code {code} in OpenAPI specification",
                )
                self.discrepancies.append(report)
                logger.info(f"ℹ️  Extra response code: {code} in {spec_key}")

    def get_critical_issues(self) -> List[DiscrepancyReport]:
        """Get critical discrepancies only"""
        return [d for d in self.discrepancies if d.severity == "critical"]

    def get_warnings(self) -> List[DiscrepancyReport]:
        """Get warning-level discrepancies"""
        return [d for d in self.discrepancies if d.severity == "warning"]

    def get_info(self) -> List[DiscrepancyReport]:
        """Get informational discrepancies"""
        return [d for d in self.discrepancies if d.severity == "info"]

    def get_summary(self) -> Dict:
        """Get summary of consistency check"""
        return {
            "spec_endpoints": len(self.spec_endpoints),
            "api_endpoints": len(self.api_endpoints),
            "total_discrepancies": len(self.discrepancies),
            "critical_issues": len(self.get_critical_issues()),
            "warnings": len(self.get_warnings()),
            "info": len(self.get_info()),
            "consistency_score": self._calculate_consistency_score(),
        }

    def _calculate_consistency_score(self) -> float:
        """
        Calculate API consistency score (0-100)

        Returns:
            Score from 0 to 100
        """
        if not self.spec_endpoints:
            return 0.0

        len(self.spec_endpoints)
        critical = len(self.get_critical_issues())
        warnings = len(self.get_warnings())

        # Score calculation: 100 - (critical_weight + warning_weight)
        score = 100.0 - (critical * 10.0 + warnings * 2.0)
        return max(0.0, min(100.0, score))

    def export_report(self, output_path: str) -> None:
        """Export consistency check report"""
        import json

        report = {
            "summary": self.get_summary(),
            "critical_issues": [d.to_dict() for d in self.get_critical_issues()],
            "warnings": [d.to_dict() for d in self.get_warnings()],
            "info": [d.to_dict() for d in self.get_info()],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info(f"✅ Exported consistency report to {output_path}")
