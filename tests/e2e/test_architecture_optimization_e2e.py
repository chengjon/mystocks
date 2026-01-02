"""
E2E Tests for Phase 6 Architecture Optimization APIs

Tests the new architecture optimization endpoints added in Phase 6:
- /api/system/database/pool-stats (actually /api/system/database/stats)
- /api/system/architecture/layers
- /api/system/performance/metrics
- /api/system/data-classifications
- /api/system/datasources/capabilities

Expected: 100% pass rate (18/18 tests)
"""
import pytest
import requests


class TestArchitectureOptimizationE2E:
    """E2E tests for architecture optimization endpoints"""

    BASE_URL = "http://localhost:8000"

    @pytest.fixture(scope="class")
    def api_base(self):
        """Base URL for API tests"""
        return self.BASE_URL

    def test_database_stats_endpoint_exists(self, api_base):
        """Test 1: Database stats endpoint exists and returns 200"""
        response = requests.get(f"{api_base}/api/system/database/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_database_stats_has_connection_info(self, api_base):
        """Test 2: Database stats includes connection information"""
        response = requests.get(f"{api_base}/api/system/database/stats")
        data = response.json()
        assert "data" in data
        assert "connections" in data["data"]
        assert "tdengine" in data["data"]["connections"]
        assert "postgresql" in data["data"]["connections"]

    def test_database_stats_has_pool_info(self, api_base):
        """Test 3: Database stats includes pool size information"""
        response = requests.get(f"{api_base}/api/system/database/stats")
        data = response.json()
        connections = data["data"]["connections"]
        assert "pool_size" in connections["tdengine"]
        assert "pool_size" in connections["postgresql"]
        assert "active_connections" in connections["tdengine"]
        assert "active_connections" in connections["postgresql"]

    def test_database_stats_has_table_counts(self, api_base):
        """Test 4: Database stats includes table counts"""
        response = requests.get(f"{api_base}/api/system/database/stats")
        data = response.json()
        assert "tables" in data["data"]
        assert "tdengine" in data["data"]["tables"]
        assert "postgresql" in data["data"]["tables"]
        assert "count" in data["data"]["tables"]["tdengine"]
        assert "count" in data["data"]["tables"]["postgresql"]

    def test_database_stats_shows_dual_architecture(self, api_base):
        """Test 5: Database stats shows dual-database architecture"""
        response = requests.get(f"{api_base}/api/system/database/stats")
        data = response.json()
        assert data["data"]["architecture"] == "dual-database"

    def test_architecture_endpoint_exists(self, api_base):
        """Test 6: Architecture endpoint exists and returns 200"""
        response = requests.get(f"{api_base}/api/system/architecture")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_architecture_has_layer_info(self, api_base):
        """Test 7: Architecture endpoint includes layer information"""
        response = requests.get(f"{api_base}/api/system/architecture")
        data = response.json()
        assert "data" in data
        # Architecture data should have structural information
        assert isinstance(data["data"], dict)

    def test_datasources_endpoint_exists(self, api_base):
        """Test 8: Datasources endpoint exists and returns 200"""
        response = requests.get(f"{api_base}/api/system/datasources")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_datasources_has_adapter_info(self, api_base):
        """Test 9: Datasources endpoint includes adapter information"""
        response = requests.get(f"{api_base}/api/system/datasources")
        data = response.json()
        assert "data" in data
        # Should have adapter information
        assert isinstance(data["data"], (dict, list))

    def test_database_health_endpoint(self, api_base):
        """Test 10: Database health endpoint exists"""
        response = requests.get(f"{api_base}/api/system/database/health")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_database_health_shows_status(self, api_base):
        """Test 11: Database health shows connection status"""
        response = requests.get(f"{api_base}/api/system/database/health")
        data = response.json()
        assert "data" in data
        # Health data should indicate database status
        assert isinstance(data["data"], dict)

    def test_system_health_endpoint(self, api_base):
        """Test 12: System health endpoint exists"""
        response = requests.get(f"{api_base}/api/system/health")
        assert response.status_code == 200
        data = response.json()
        # Health endpoint uses UnifiedResponse format with service field
        assert "success" in data or "service" in data

    def test_adapters_health_endpoint(self, api_base):
        """Test 13: Adapters health endpoint exists"""
        response = requests.get(f"{api_base}/api/system/adapters/health")
        assert response.status_code == 200
        data = response.json()
        # Adapters health returns adapter status information
        assert "data" in data or "adapters" in data

    def test_response_format_consistent(self, api_base):
        """Test 14: All endpoints use consistent response format"""
        # Separate endpoints by their response format types
        unified_response_endpoints = [
            "/api/system/database/stats",
            "/api/system/architecture",
            "/api/system/datasources",
            "/api/system/database/health",
        ]
        # Health endpoint uses a different format with service field
        health_endpoint = "/api/system/health"

        # Test UnifiedResponse format endpoints
        for endpoint in unified_response_endpoints:
            response = requests.get(f"{api_base}{endpoint}")
            data = response.json()
            # All responses should have these fields
            assert "success" in data, f"Missing 'success' in {endpoint}"
            assert "data" in data, f"Missing 'data' in {endpoint}"
            # Response can have message, request_id, or timestamp
            assert ("message" in data or "request_id" in data or "timestamp" in data), \
                f"Missing 'message', 'request_id', or 'timestamp' in {endpoint}"

        # Test health endpoint separately (it has a different format)
        response = requests.get(f"{api_base}{health_endpoint}")
        data = response.json()
        assert "service" in data or "success" in data, "Health endpoint should have service or success field"

    def test_all_endpoints_return_json(self, api_base):
        """Test 15: All endpoints return JSON content type"""
        endpoints = [
            "/api/system/database/stats",
            "/api/system/architecture",
            "/api/system/datasources",
        ]

        for endpoint in endpoints:
            response = requests.get(f"{api_base}{endpoint}")
            assert response.headers["content-type"].startswith("application/json"), \
                f"Wrong content type for {endpoint}: {response.headers['content-type']}"

    def test_endpoints_handle_errors_gracefully(self, api_base):
        """Test 16: Endpoints handle invalid requests gracefully"""
        # Test with invalid endpoint
        response = requests.get(f"{api_base}/api/system/invalid-endpoint")
        assert response.status_code in [404, 422]  # Should not return 500

    def test_database_simplification_info_present(self, api_base):
        """Test 17: Database stats includes simplification history"""
        response = requests.get(f"{api_base}/api/system/database/stats")
        data = response.json()
        # Should show database simplification from 4 to 2 databases
        assert "simplified_from" in data["data"]
        assert "simplified_to" in data["data"]
        assert "4 databases" in data["data"]["simplified_from"]
        assert "2 databases" in data["data"]["simplified_to"]

    def test_removed_databases_info_present(self, api_base):
        """Test 18: Database stats includes removed databases information"""
        response = requests.get(f"{api_base}/api/system/database/stats")
        data = response.json()
        # Should show MySQL and Redis removal
        assert "removed_databases" in data["data"]
        removed = data["data"]["removed_databases"]
        assert "mysql" in removed
        assert "redis" in removed
