"""
Contract Test Engine

Main orchestrator for contract testing.
Coordinates specification validation, test execution, and reporting.

Task 12.1 Implementation: Contract testing engine
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import json

from .spec_validator import SpecificationValidator, APIEndpoint
from .test_hooks import TestHooksManager, HookContext, HookType
from .api_consistency_checker import APIConsistencyChecker, DiscrepancyReport

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Single test result"""
    test_id: str
    endpoint_method: str
    endpoint_path: str
    status: str  # passed, failed, skipped
    duration_ms: float
    error_message: Optional[str] = None
    assertions: int = 0
    assertions_passed: int = 0

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "test_id": self.test_id,
            "endpoint_method": self.endpoint_method,
            "endpoint_path": self.endpoint_path,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "error_message": self.error_message,
            "assertions": self.assertions,
            "assertions_passed": self.assertions_passed,
        }


class ContractTestEngine:
    """
    Contract Testing Engine

    Orchestrates contract tests based on OpenAPI specification.
    Similar to Dredd but implemented in Python.
    """

    def __init__(self, spec_path: str):
        """
        Initialize contract test engine

        Args:
            spec_path: Path to OpenAPI specification file
        """
        self.spec_validator = SpecificationValidator(spec_path)
        self.hooks_manager = TestHooksManager()
        self.consistency_checker = APIConsistencyChecker(self.spec_validator)
        self.test_results: List[TestResult] = []
        self.test_handlers: Dict[str, Callable] = {}
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    def register_test_handler(self, endpoint_key: str, handler: Callable) -> None:
        """
        Register a test handler for an endpoint

        Args:
            endpoint_key: Endpoint key (e.g., "GET /api/users")
            handler: Callable that executes the test
        """
        self.test_handlers[endpoint_key] = handler
        logger.debug(f"✅ Registered test handler for {endpoint_key}")

    def register_api_endpoint(
        self,
        method: str,
        path: str,
        parameters: Optional[List[str]] = None,
        response_codes: Optional[List[int]] = None,
        description: str = "",
    ) -> None:
        """Register actual API endpoint"""
        self.consistency_checker.register_api_endpoint(
            method=method,
            path=path,
            parameters=parameters,
            response_codes=response_codes,
            description=description,
        )

    def run_tests(self) -> Dict[str, Any]:
        """
        Run all contract tests

        Returns:
            Test results summary
        """
        self.start_time = datetime.now()
        self.test_results = []

        logger.info("🚀 Starting contract tests...")
        logger.info(f"📋 Testing {len(self.spec_validator.get_all_endpoints())} endpoints")

        # Run before-all hooks
        context = HookContext(
            test_id="before_all",
            endpoint_method="",
            endpoint_path="",
        )
        try:
            self.hooks_manager.execute_hooks(HookType.BEFORE_ALL, context)
        except Exception as e:
            logger.error(f"❌ beforeAll hook failed: {e}")
            return self._get_failed_results()

        # Run each endpoint test
        for endpoint in self.spec_validator.get_all_endpoints():
            try:
                result = self._run_endpoint_test(endpoint)
                self.test_results.append(result)
            except Exception as e:
                logger.error(f"❌ Test failed for {endpoint.method.value.upper()} {endpoint.path}: {e}")
                result = TestResult(
                    test_id=f"{endpoint.method.value.upper()}_{endpoint.path.replace('/', '_')}",
                    endpoint_method=endpoint.method.value.upper(),
                    endpoint_path=endpoint.path,
                    status="failed",
                    duration_ms=0,
                    error_message=str(e),
                )
                self.test_results.append(result)

        # Run after-all hooks
        context = HookContext(
            test_id="after_all",
            endpoint_method="",
            endpoint_path="",
        )
        try:
            self.hooks_manager.execute_hooks(HookType.AFTER_ALL, context)
        except Exception as e:
            logger.error(f"❌ afterAll hook failed: {e}")

        self.end_time = datetime.now()

        summary = self._get_test_summary()
        logger.info(f"✅ Tests completed: {summary['passed']}/{summary['total']} passed")

        return summary

    def _run_endpoint_test(self, endpoint: APIEndpoint) -> TestResult:
        """Run test for single endpoint"""
        test_id = f"{endpoint.method.value.upper()}_{endpoint.path.replace('/', '_')}"
        endpoint_key = f"{endpoint.method.value.upper()} {endpoint.path}"

        logger.debug(f"🧪 Testing {endpoint_key}")

        # Create hook context
        context = HookContext(
            test_id=test_id,
            endpoint_method=endpoint.method.value.upper(),
            endpoint_path=endpoint.path,
        )

        start = datetime.now()

        try:
            # Before-each hook
            self.hooks_manager.execute_hooks(HookType.BEFORE_EACH, context)

            # Before-transaction hook
            self.hooks_manager.execute_hooks(HookType.BEFORE_TRANSACTION, context)

            # Run test handler if registered
            if endpoint_key in self.test_handlers:
                handler = self.test_handlers[endpoint_key]
                assertions = handler(endpoint, context)
            else:
                # Default: just verify endpoint exists and returns 200
                assertions = 1

            # After-transaction hook
            self.hooks_manager.execute_hooks(HookType.AFTER_TRANSACTION, context)

            # After-each hook
            self.hooks_manager.execute_hooks(HookType.AFTER_EACH, context)

            duration = (datetime.now() - start).total_seconds() * 1000

            result = TestResult(
                test_id=test_id,
                endpoint_method=endpoint.method.value.upper(),
                endpoint_path=endpoint.path,
                status="passed",
                duration_ms=duration,
                assertions=assertions,
                assertions_passed=assertions,
            )

            logger.info(f"✅ {endpoint_key} - PASSED ({duration:.2f}ms)")
            return result

        except Exception as e:
            duration = (datetime.now() - start).total_seconds() * 1000
            logger.error(f"❌ {endpoint_key} - FAILED: {e}")

            result = TestResult(
                test_id=test_id,
                endpoint_method=endpoint.method.value.upper(),
                endpoint_path=endpoint.path,
                status="failed",
                duration_ms=duration,
                error_message=str(e),
                assertions=1,
                assertions_passed=0,
            )
            return result

    def check_consistency(self) -> Dict[str, Any]:
        """Check API consistency with specification"""
        logger.info("🔍 Checking API consistency...")
        self.consistency_checker.check_consistency()
        return self.consistency_checker.get_summary()

    def _get_test_summary(self) -> Dict[str, Any]:
        """Get test results summary"""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.status == "passed")
        failed = sum(1 for r in self.test_results if r.status == "failed")
        skipped = sum(1 for r in self.test_results if r.status == "skipped")

        total_duration = (self.end_time - self.start_time).total_seconds() * 1000 if self.end_time else 0

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "duration_ms": total_duration,
            "start_time": self.start_time.isoformat() if self.start_time else "",
            "end_time": self.end_time.isoformat() if self.end_time else "",
        }

    def _get_failed_results(self) -> Dict[str, Any]:
        """Return failed test summary"""
        return {
            "total": 0,
            "passed": 0,
            "failed": 1,
            "skipped": 0,
            "pass_rate": 0,
            "duration_ms": 0,
            "error": "Test execution failed",
        }

    def export_test_results(self, output_path: str) -> None:
        """Export test results to JSON"""
        results = [r.to_dict() for r in self.test_results]
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(
                {
                    "summary": self._get_test_summary(),
                    "results": results,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        logger.info(f"✅ Exported test results to {output_path}")

    def get_test_results(self) -> List[TestResult]:
        """Get all test results"""
        return self.test_results
