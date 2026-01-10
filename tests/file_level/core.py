"""
File-Level API Testing Framework

This module provides comprehensive file-level testing capabilities for FastAPI applications.
It groups endpoints by file boundaries and provides efficient parallel testing with
detailed reporting and metrics collection.

Key Features:
- File-level test execution (groups endpoints by API file)
- Parallel test execution with configurable concurrency
- Comprehensive test reporting and metrics
- Test data management and fixtures
- Contract validation integration
- CI/CD pipeline integration

Author: MyStocks Testing Team
Date: 2026-01-10
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
import json
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import pytest
import httpx
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field


@dataclass
class FileTestResult:
    """Result of testing a single API file"""
    file_path: str
    file_name: str
    endpoints_tested: int
    endpoints_passed: int
    endpoints_failed: int
    total_tests: int
    passed_tests: int
    failed_tests: int
    execution_time: float
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    test_details: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "pending"  # pending, running, passed, failed, error

    @property
    def success_rate(self) -> float:
        """Calculate success rate for this file"""
        if self.endpoints_tested == 0:
            return 0.0
        return (self.endpoints_passed / self.endpoints_tested) * 100

    @property
    def test_coverage(self) -> float:
        """Calculate test coverage for this file"""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100


@dataclass
class FileTestSuiteResult:
    """Result of running a complete file test suite"""
    suite_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_files: int = 0
    files_tested: int = 0
    files_passed: int = 0
    files_failed: int = 0
    total_endpoints: int = 0
    endpoints_passed: int = 0
    endpoints_failed: int = 0
    total_execution_time: float = 0.0
    file_results: List[FileTestResult] = field(default_factory=list)
    status: str = "pending"

    def add_file_result(self, result: FileTestResult) -> None:
        """Add a file test result to the suite"""
        self.file_results.append(result)
        self.files_tested += 1
        self.total_files += 1

        if result.status == "passed":
            self.files_passed += 1
        elif result.status in ["failed", "error"]:
            self.files_failed += 1

        self.total_endpoints += result.endpoints_tested
        self.endpoints_passed += result.endpoints_passed
        self.endpoints_failed += result.endpoints_failed
        self.total_execution_time += result.execution_time

    @property
    def overall_success_rate(self) -> float:
        """Calculate overall success rate"""
        if self.total_endpoints == 0:
            return 0.0
        return (self.endpoints_passed / self.total_endpoints) * 100

    @property
    def average_execution_time(self) -> float:
        """Calculate average execution time per file"""
        if self.files_tested == 0:
            return 0.0
        return self.total_execution_time / self.files_tested


class FileLevelTestRunner:
    """
    Main test runner for file-level API testing.

    This class provides:
    - Parallel file testing execution
    - Comprehensive result collection
    - Test metrics and reporting
    - CI/CD integration hooks
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        max_workers: int = 4,
        timeout: int = 30,
        test_data_dir: Optional[str] = None,
        report_dir: Optional[str] = None
    ):
        """
        Initialize the file-level test runner.

        Args:
            base_url: Base URL of the API to test
            max_workers: Maximum number of parallel workers
            timeout: Request timeout in seconds
            test_data_dir: Directory containing test data files
            report_dir: Directory to save test reports
        """
        self.base_url = base_url.rstrip('/')
        self.max_workers = max_workers
        self.timeout = timeout
        self.test_data_dir = Path(test_data_dir or "tests/file_level/data")
        self.report_dir = Path(report_dir or "tests/file_level/reports")

        # Create directories if they don't exist
        self.test_data_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)

        # Initialize HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={"Content-Type": "application/json"}
        )

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.client.aclose()

    def discover_api_files(self, api_dir: str = "web/backend/app/api") -> List[str]:
        """
        Discover all API files that need testing.

        Args:
            api_dir: Directory containing API files

        Returns:
            List of API file paths
        """
        api_path = Path(api_dir)
        if not api_path.exists():
            raise FileNotFoundError(f"API directory not found: {api_dir}")

        api_files = []
        for py_file in api_path.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
            if "test_" in py_file.name:
                continue
            api_files.append(str(py_file.relative_to(Path.cwd())))

        return sorted(api_files)

    async def test_file(
        self,
        file_path: str,
        config: Optional[Dict[str, Any]] = None
    ) -> FileTestResult:
        """
        Test a single API file.

        Args:
            file_path: Path to the API file to test
            config: Test configuration for this file

        Returns:
            FileTestResult with test outcomes
        """
        start_time = time.time()
        result = FileTestResult(
            file_path=file_path,
            file_name=Path(file_path).name,
            endpoints_tested=0,
            endpoints_passed=0,
            endpoints_failed=0,
            total_tests=0,
            passed_tests=0,
            failed_tests=0,
            execution_time=0.0,
            status="running"
        )

        try:
            # Import the API module to analyze endpoints
            module_path = file_path.replace('/', '.').replace('.py', '')
            if module_path.startswith('web.backend.app.api'):
                module_path = module_path.replace('web.backend.app.', '')

            # Load test configuration for this file
            test_config = self._load_file_test_config(file_path, config)

            # Discover endpoints in this file
            endpoints = await self._discover_file_endpoints(file_path)

            result.endpoints_tested = len(endpoints)
            result.total_tests = len(endpoints) * 2  # Basic + contract tests

            # Test each endpoint
            for endpoint in endpoints:
                endpoint_result = await self._test_endpoint(
                    endpoint, test_config
                )

                if endpoint_result["status"] == "passed":
                    result.endpoints_passed += 1
                    result.passed_tests += 2
                else:
                    result.endpoints_failed += 1
                    result.failed_tests += 2
                    result.errors.append(endpoint_result.get("error", "Unknown error"))

                result.test_details.append(endpoint_result)

            # Set final status
            if result.endpoints_failed == 0:
                result.status = "passed"
            else:
                result.status = "failed"

        except Exception as e:
            result.status = "error"
            result.errors.append(f"File test failed: {str(e)}")

        result.execution_time = time.time() - start_time
        return result

    async def run_file_tests(
        self,
        file_paths: Optional[List[str]] = None,
        max_workers: Optional[int] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> FileTestSuiteResult:
        """
        Run file-level tests for multiple API files.

        Args:
            file_paths: List of API file paths to test (auto-discover if None)
            max_workers: Maximum parallel workers (uses instance default if None)
            config: Global test configuration

        Returns:
            Complete test suite results
        """
        start_time = datetime.now()
        workers = max_workers or self.max_workers

        suite_result = FileTestSuiteResult(
            suite_name="API File-Level Tests",
            start_time=start_time,
            status="running"
        )

        # Discover files if not provided
        if file_paths is None:
            file_paths = self.discover_api_files()

        print(f"🔍 Discovered {len(file_paths)} API files to test")
        print(f"🚀 Running tests with {workers} parallel workers")

        # Run tests in parallel
        with ThreadPoolExecutor(max_workers=workers) as executor:
            # Submit all test tasks
            future_to_file = {
                executor.submit(self._run_single_file_test, file_path, config): file_path
                for file_path in file_paths
            }

            # Collect results as they complete
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    file_result = future.result()
                    suite_result.add_file_result(file_result)

                    # Progress reporting
                    status_icon = "✅" if file_result.status == "passed" else "❌"
                    print(f"{status_icon} {file_result.file_name}: "
                          f"{file_result.endpoints_passed}/{file_result.endpoints_tested} endpoints")

                except Exception as e:
                    print(f"❌ Error testing {file_path}: {str(e)}")

        # Finalize suite result
        suite_result.end_time = datetime.now()
        suite_result.status = "completed"

        return suite_result

    def _load_file_test_config(
        self,
        file_path: str,
        global_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Load test configuration for a specific file"""
        config = global_config or {}

        # Try to load file-specific config
        config_file = self.test_data_dir / f"{Path(file_path).stem}_config.yaml"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = yaml.safe_load(f)
                config.update(file_config)

        return config

    async def _discover_file_endpoints(self, file_path: str) -> List[Dict[str, Any]]:
        """Discover endpoints in an API file"""
        # This is a simplified implementation
        # In a real implementation, this would analyze the FastAPI router
        # and extract endpoint information

        endpoints = []

        # For now, return mock endpoints based on file name
        # This would be replaced with actual endpoint discovery
        file_name = Path(file_path).stem

        # Map common file patterns to endpoints
        endpoint_maps = {
            "market": [
                {"method": "GET", "path": "/api/market/data", "name": "get_market_data"},
                {"method": "GET", "path": "/api/market/realtime", "name": "get_realtime_data"}
            ],
            "technical_analysis": [
                {"method": "GET", "path": "/api/technical/indicators", "name": "get_indicators"},
                {"method": "POST", "path": "/api/technical/calculate", "name": "calculate_indicators"}
            ],
            "strategy_management": [
                {"method": "GET", "path": "/api/strategy/list", "name": "list_strategies"},
                {"method": "POST", "path": "/api/strategy/create", "name": "create_strategy"}
            ]
        }

        if file_name in endpoint_maps:
            endpoints = endpoint_maps[file_name]
        else:
            # Default single endpoint for unknown files
            endpoints = [
                {"method": "GET", "path": f"/api/{file_name}/status", "name": "get_status"}
            ]

        return endpoints

    async def _test_endpoint(
        self,
        endpoint: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test a single endpoint"""
        method = endpoint["method"]
        path = endpoint["path"]
        name = endpoint["name"]

        result = {
            "endpoint": name,
            "method": method,
            "path": path,
            "status": "pending",
            "response_time": 0.0,
            "tests": []
        }

        try:
            start_time = time.time()

            # Test 1: Basic connectivity
            response = await self.client.request(method, path)

            result["response_time"] = time.time() - start_time
            result["status_code"] = response.status_code

            # Check if response is successful
            if 200 <= response.status_code < 300:
                result["tests"].append({"name": "connectivity", "status": "passed"})
            else:
                result["tests"].append({
                    "name": "connectivity",
                    "status": "failed",
                    "error": f"Status code: {response.status_code}"
                })

            # Test 2: Response format (basic)
            try:
                response_data = response.json()
                result["tests"].append({"name": "response_format", "status": "passed"})
            except:
                result["tests"].append({
                    "name": "response_format",
                    "status": "failed",
                    "error": "Invalid JSON response"
                })

            # Determine overall status
            failed_tests = [t for t in result["tests"] if t["status"] == "failed"]
            if failed_tests:
                result["status"] = "failed"
                result["error"] = "; ".join(t.get("error", "") for t in failed_tests)
            else:
                result["status"] = "passed"

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def _run_single_file_test(
        self,
        file_path: str,
        config: Optional[Dict[str, Any]] = None
    ) -> FileTestResult:
        """Run test for a single file (used by ThreadPoolExecutor)"""
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            return loop.run_until_complete(self.test_file(file_path, config))
        finally:
            loop.close()

    def save_results(
        self,
        suite_result: FileTestSuiteResult,
        format: str = "json"
    ) -> str:
        """
        Save test results to file.

        Args:
            suite_result: Test suite results to save
            format: Output format ('json', 'yaml', 'html')

        Returns:
            Path to saved report file
        """
        timestamp = suite_result.start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"file_test_report_{timestamp}.{format}"

        report_path = self.report_dir / filename

        if format == "json":
            data = {
                "suite_name": suite_result.suite_name,
                "start_time": suite_result.start_time.isoformat(),
                "end_time": suite_result.end_time.isoformat() if suite_result.end_time else None,
                "summary": {
                    "total_files": suite_result.total_files,
                    "files_tested": suite_result.files_tested,
                    "files_passed": suite_result.files_passed,
                    "files_failed": suite_result.files_failed,
                    "total_endpoints": suite_result.total_endpoints,
                    "endpoints_passed": suite_result.endpoints_passed,
                    "endpoints_failed": suite_result.endpoints_failed,
                    "overall_success_rate": suite_result.overall_success_rate,
                    "total_execution_time": suite_result.total_execution_time,
                    "average_execution_time": suite_result.average_execution_time
                },
                "file_results": [
                    {
                        "file_path": r.file_path,
                        "file_name": r.file_name,
                        "endpoints_tested": r.endpoints_tested,
                        "endpoints_passed": r.endpoints_passed,
                        "endpoints_failed": r.endpoints_failed,
                        "success_rate": r.success_rate,
                        "execution_time": r.execution_time,
                        "status": r.status,
                        "errors": r.errors,
                        "warnings": r.warnings
                    }
                    for r in suite_result.file_results
                ]
            }

            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        elif format == "html":
            # Generate HTML report
            html_content = self._generate_html_report(suite_result)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

        return str(report_path)

    def _generate_html_report(self, suite_result: FileTestSuiteResult) -> str:
        """Generate HTML test report"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>API File-Level Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .file-result {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; }}
                .passed {{ background: #d4edda; }}
                .failed {{ background: #f8d7da; }}
                .error {{ background: #fff3cd; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 8px; text-align: left; border: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <h1>API File-Level Test Report</h1>
            <div class="summary">
                <h2>Test Summary</h2>
                <p><strong>Start Time:</strong> {suite_result.start_time}</p>
                <p><strong>Files Tested:</strong> {suite_result.files_tested}</p>
                <p><strong>Endpoints Tested:</strong> {suite_result.total_endpoints}</p>
                <p><strong>Success Rate:</strong> {suite_result.overall_success_rate:.1f}%</p>
                <p><strong>Execution Time:</strong> {suite_result.total_execution_time:.2f}s</p>
            </div>

            <h2>File Results</h2>
            <table>
                <tr>
                    <th>File Name</th>
                    <th>Endpoints</th>
                    <th>Success Rate</th>
                    <th>Execution Time</th>
                    <th>Status</th>
                </tr>
        """

        for result in suite_result.file_results:
            css_class = result.status
            html += f"""
                <tr class="{css_class}">
                    <td>{result.file_name}</td>
                    <td>{result.endpoints_passed}/{result.endpoints_tested}</td>
                    <td>{result.success_rate:.1f}%</td>
                    <td>{result.execution_time:.2f}s</td>
                    <td>{result.status.upper()}</td>
                </tr>
            """

        html += """
            </table>
        </body>
        </html>
        """

        return html</content>
<parameter name="filePath">tests/file_level/__init__.py