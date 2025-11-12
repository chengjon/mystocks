"""
Comprehensive test suite for Contract Testing Framework

Tests all contract testing components including:
- Specification validation
- Test hook management
- API consistency checking
- Contract test engine
- Report generation

Task 12: Contract Testing (契约测试) - Test Suite
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.contract_testing import (
    SpecificationValidator,
    TestHooksManager,
    HookContext,
    HookType,
    APIConsistencyChecker,
    ContractTestEngine,
    ContractTestReportGenerator,
)


class TestSpecificationValidator:
    """Test OpenAPI specification validation"""

    @pytest.fixture
    def sample_openapi_spec(self):
        """Create a sample OpenAPI specification"""
        return {
            "openapi": "3.1.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0",
            },
            "paths": {
                "/api/users": {
                    "get": {
                        "summary": "List users",
                        "parameters": [
                            {
                                "name": "skip",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "integer"},
                            }
                        ],
                        "responses": {
                            "200": {"description": "User list"},
                            "400": {"description": "Bad request"},
                        },
                    },
                    "post": {
                        "summary": "Create user",
                        "requestBody": {"required": True},
                        "responses": {
                            "201": {"description": "Created"},
                        },
                    },
                },
                "/api/users/{id}": {
                    "get": {
                        "summary": "Get user by ID",
                        "parameters": [
                            {
                                "name": "id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {
                            "200": {"description": "User found"},
                            "404": {"description": "Not found"},
                        },
                    },
                },
            },
        }

    def test_initialization(self):
        """Test validator initialization"""
        validator = SpecificationValidator()
        assert validator.spec == {}
        assert validator.endpoints == []
        assert validator.version == ""

    def test_load_spec_from_dict(self, sample_openapi_spec):
        """Test loading specification from dictionary"""
        validator = SpecificationValidator()
        validator.spec = sample_openapi_spec
        validator._validate_spec_structure()
        validator._extract_metadata()
        validator._parse_endpoints()

        assert validator.title == "Test API"
        assert validator.version == "1.0.0"
        assert len(validator.endpoints) == 3  # 2 GET + 1 POST

    def test_parse_endpoints(self, sample_openapi_spec):
        """Test endpoint parsing"""
        validator = SpecificationValidator()
        validator.spec = sample_openapi_spec
        validator._validate_spec_structure()
        validator._extract_metadata()
        validator._parse_endpoints()

        endpoints = validator.get_all_endpoints()
        assert len(endpoints) == 3

        # Check GET /api/users
        get_users = validator.get_endpoint("GET", "/api/users")
        assert get_users is not None
        assert get_users.summary == "List users"
        assert len(get_users.parameters) == 1

    def test_spec_summary(self, sample_openapi_spec):
        """Test specification summary"""
        validator = SpecificationValidator()
        validator.spec = sample_openapi_spec
        validator._validate_spec_structure()
        validator._extract_metadata()
        validator._parse_endpoints()

        summary = validator.get_summary()
        assert summary["title"] == "Test API"
        assert summary["total_endpoints"] == 3

    def test_invalid_spec_structure(self):
        """Test validation of invalid spec"""
        validator = SpecificationValidator()
        validator.spec = {}

        with pytest.raises(ValueError):
            validator._validate_spec_structure()

    def test_export_endpoints(self, sample_openapi_spec):
        """Test exporting endpoints to JSON"""
        with tempfile.TemporaryDirectory() as tmpdir:
            validator = SpecificationValidator()
            validator.spec = sample_openapi_spec
            validator._validate_spec_structure()
            validator._extract_metadata()
            validator._parse_endpoints()

            output_path = os.path.join(tmpdir, "endpoints.json")
            validator.export_endpoints_json(output_path)

            assert os.path.exists(output_path)
            with open(output_path) as f:
                data = json.load(f)
                assert len(data) == 3


class TestTestHooksManager:
    """Test hook management"""

    def test_initialization(self):
        """Test hooks manager initialization"""
        manager = TestHooksManager()
        assert len(manager.hooks) == len(HookType)
        assert manager.hook_execution_log == []

    def test_register_before_all_hook(self):
        """Test registering beforeAll hook"""
        manager = TestHooksManager()
        handler = MagicMock()

        manager.before_all(handler, name="setup_hook", description="Setup test data")

        hooks = manager.get_hooks_by_type(HookType.BEFORE_ALL)
        assert len(hooks) == 1
        assert hooks[0].name == "setup_hook"

    def test_hook_execution(self):
        """Test hook execution"""
        manager = TestHooksManager()
        handler = MagicMock()

        manager.register_hook(HookType.BEFORE_EACH, handler)

        context = HookContext(
            test_id="test_1",
            endpoint_method="GET",
            endpoint_path="/api/users",
        )

        manager.execute_hooks(HookType.BEFORE_EACH, context)
        handler.assert_called_once()

    def test_hook_execution_log(self):
        """Test hook execution logging"""
        manager = TestHooksManager()

        def dummy_handler(ctx):
            pass

        manager.before_all(dummy_handler, name="test_hook")

        context = HookContext(
            test_id="test_1",
            endpoint_method="GET",
            endpoint_path="/api/users",
        )

        manager.execute_hooks(HookType.BEFORE_ALL, context)

        log = manager.get_execution_log()
        assert len(log) == 1
        assert log[0]["hook_type"] == HookType.BEFORE_ALL.value
        assert log[0]["success"] is True

    def test_hook_failure_logging(self):
        """Test logging of hook failures"""
        manager = TestHooksManager()

        def failing_handler(ctx):
            raise ValueError("Hook failed intentionally")

        manager.before_each(failing_handler, name="failing_hook")

        context = HookContext(
            test_id="test_1",
            endpoint_method="GET",
            endpoint_path="/api/users",
        )

        with pytest.raises(ValueError):
            manager.execute_hooks(HookType.BEFORE_EACH, context)

        log = manager.get_execution_log()
        assert len(log) == 1
        assert log[0]["success"] is False
        assert "Hook failed intentionally" in log[0]["error"]

    def test_hook_priority_ordering(self):
        """Test that hooks execute in priority order"""
        manager = TestHooksManager()
        execution_order = []

        def first_handler(ctx):
            execution_order.append(1)

        def second_handler(ctx):
            execution_order.append(2)

        # Register with different priorities
        manager.register_hook(HookType.BEFORE_ALL, second_handler, priority=0)
        manager.register_hook(HookType.BEFORE_ALL, first_handler, priority=1)

        context = HookContext(
            test_id="test_1",
            endpoint_method="GET",
            endpoint_path="/api/users",
        )

        manager.execute_hooks(HookType.BEFORE_ALL, context)

        # Higher priority should execute first
        assert execution_order == [1, 2]

    def test_clear_hooks(self):
        """Test clearing all hooks"""
        manager = TestHooksManager()
        manager.before_all(MagicMock())
        manager.before_each(MagicMock())

        assert len(manager.get_hooks_by_type(HookType.BEFORE_ALL)) == 1
        assert len(manager.get_hooks_by_type(HookType.BEFORE_EACH)) == 1

        manager.clear_hooks()

        assert len(manager.get_hooks_by_type(HookType.BEFORE_ALL)) == 0
        assert len(manager.get_hooks_by_type(HookType.BEFORE_EACH)) == 0


class TestAPIConsistencyChecker:
    """Test API consistency verification"""

    @pytest.fixture
    def validator_with_spec(self):
        """Create validator with sample spec"""
        spec = {
            "openapi": "3.1.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/api/users": {
                    "get": {
                        "parameters": [
                            {"name": "limit", "in": "query", "schema": {"type": "integer"}}
                        ],
                        "responses": {"200": {}, "400": {}},
                    }
                }
            },
        }
        validator = SpecificationValidator()
        validator.spec = spec
        validator._validate_spec_structure()
        validator._extract_metadata()
        validator._parse_endpoints()
        return validator

    def test_initialization(self, validator_with_spec):
        """Test consistency checker initialization"""
        checker = APIConsistencyChecker(validator_with_spec)
        assert checker.api_endpoints == {}
        assert checker.discrepancies == []

    def test_register_api_endpoint(self, validator_with_spec):
        """Test registering API endpoint"""
        checker = APIConsistencyChecker(validator_with_spec)
        checker.register_api_endpoint(
            method="GET",
            path="/api/users",
            parameters=["limit"],
            response_codes=[200, 400],
        )

        assert "GET /api/users" in checker.api_endpoints

    def test_missing_endpoint_detection(self, validator_with_spec):
        """Test detection of missing endpoints"""
        checker = APIConsistencyChecker(validator_with_spec)
        # Register only partial endpoints
        checker.register_api_endpoint(
            method="POST",
            path="/api/users",
            response_codes=[201],
        )

        discrepancies = checker.check_consistency()

        # Should detect GET /api/users as missing from implementation
        missing = [d for d in discrepancies if d.type.value == "missing_endpoint"]
        assert len(missing) > 0

    def test_extra_endpoint_detection(self, validator_with_spec):
        """Test detection of extra endpoints"""
        checker = APIConsistencyChecker(validator_with_spec)
        # Register extra endpoint not in spec
        checker.register_api_endpoint(
            method="DELETE",
            path="/api/users",
            response_codes=[204],
        )

        discrepancies = checker.check_consistency()

        # Should detect DELETE /api/users as extra
        extra = [d for d in discrepancies if d.type.value == "extra_endpoint"]
        assert len(extra) > 0

    def test_consistency_score(self, validator_with_spec):
        """Test consistency score calculation"""
        checker = APIConsistencyChecker(validator_with_spec)
        checker.register_api_endpoint(
            method="GET",
            path="/api/users",
            parameters=["limit"],
            response_codes=[200, 400],
        )

        summary = checker.get_summary()
        assert 0 <= summary["consistency_score"] <= 100

    def test_export_report(self, validator_with_spec):
        """Test exporting consistency report"""
        with tempfile.TemporaryDirectory() as tmpdir:
            checker = APIConsistencyChecker(validator_with_spec)
            checker.register_api_endpoint(
                method="GET",
                path="/api/users",
                parameters=["limit"],
                response_codes=[200, 400],
            )
            checker.check_consistency()

            output_path = os.path.join(tmpdir, "report.json")
            checker.export_report(output_path)

            assert os.path.exists(output_path)


class TestContractTestEngine:
    """Test contract test engine"""

    @pytest.fixture
    def temp_spec_file(self):
        """Create temporary spec file"""
        spec = {
            "openapi": "3.1.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/api/health": {
                    "get": {
                        "summary": "Health check",
                        "responses": {"200": {}},
                    }
                }
            },
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(spec, f)
            return f.name

    def test_engine_initialization(self, temp_spec_file):
        """Test engine initialization"""
        try:
            engine = ContractTestEngine(temp_spec_file)
            assert engine.spec_validator is not None
            assert engine.hooks_manager is not None
            assert engine.test_results == []
        finally:
            os.unlink(temp_spec_file)

    def test_register_test_handler(self, temp_spec_file):
        """Test registering test handler"""
        try:
            engine = ContractTestEngine(temp_spec_file)
            handler = MagicMock(return_value=1)

            engine.register_test_handler("GET /api/health", handler)

            assert "GET /api/health" in engine.test_handlers
        finally:
            os.unlink(temp_spec_file)

    def test_run_tests(self, temp_spec_file):
        """Test running contract tests"""
        try:
            engine = ContractTestEngine(temp_spec_file)
            handler = MagicMock(return_value=1)
            engine.register_test_handler("GET /api/health", handler)

            summary = engine.run_tests()

            assert summary["total"] > 0
            assert "passed" in summary
            assert "failed" in summary
        finally:
            os.unlink(temp_spec_file)

    def test_export_results(self, temp_spec_file):
        """Test exporting test results"""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                engine = ContractTestEngine(temp_spec_file)
                engine.run_tests()

                output_path = os.path.join(tmpdir, "results.json")
                engine.export_test_results(output_path)

                assert os.path.exists(output_path)
        finally:
            os.unlink(temp_spec_file)


class TestContractTestReportGenerator:
    """Test report generation"""

    def test_initialization(self):
        """Test report generator initialization"""
        generator = ContractTestReportGenerator()
        assert generator.test_results == []
        assert generator.consistency_summary == {}

    def test_add_test_results(self):
        """Test adding test results"""
        generator = ContractTestReportGenerator()
        results = [
            {"status": "passed", "endpoint_method": "GET", "endpoint_path": "/api/users"},
            {"status": "failed", "endpoint_method": "POST", "endpoint_path": "/api/users"},
        ]

        generator.add_test_results(results)
        assert len(generator.test_results) == 2

    def test_generate_json_report(self):
        """Test JSON report generation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ContractTestReportGenerator()
            generator.add_test_results([
                {"status": "passed", "endpoint_method": "GET", "endpoint_path": "/api/users"}
            ])

            output_path = os.path.join(tmpdir, "report.json")
            generator.generate_json_report(output_path)

            assert os.path.exists(output_path)
            with open(output_path) as f:
                data = json.load(f)
                assert "test_results" in data

    def test_generate_markdown_report(self):
        """Test Markdown report generation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ContractTestReportGenerator()
            generator.add_test_results([
                {"status": "passed", "endpoint_method": "GET", "endpoint_path": "/api/users"}
            ])

            output_path = os.path.join(tmpdir, "report.md")
            generator.generate_markdown_report(output_path)

            assert os.path.exists(output_path)
            with open(output_path) as f:
                content = f.read()
                assert "Contract Test Report" in content

    def test_generate_html_report(self):
        """Test HTML report generation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ContractTestReportGenerator()
            generator.add_test_results([
                {"status": "passed", "endpoint_method": "GET", "endpoint_path": "/api/users"}
            ])

            output_path = os.path.join(tmpdir, "report.html")
            generator.generate_html_report(output_path)

            assert os.path.exists(output_path)
            with open(output_path) as f:
                content = f.read()
                assert "<html>" in content.lower()

    def test_generate_all_reports(self):
        """Test generating all report formats"""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ContractTestReportGenerator()
            generator.add_test_results([
                {"status": "passed", "endpoint_method": "GET", "endpoint_path": "/api/users"}
            ])

            generator.generate_all_reports(tmpdir)

            # Check that all report files were created
            files = os.listdir(tmpdir)
            assert any(f.endswith('.json') for f in files)
            assert any(f.endswith('.md') for f in files)
            assert any(f.endswith('.html') for f in files)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
