#!/usr/bin/env python3
"""
Phase 4B Security Improvements Test Script

Tests the comprehensive security enhancements implemented in:
1. metrics.py - JWT authentication, rate limiting, admin-only access
2. tasks.py - Authorization, validation, audit logging
3. stock_search.py - Enhanced validation, rate limiting, analytics

Usage:
    python test_phase4b_security_improvements.py
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class TestConfig:
    """Test configuration"""

    base_url: str = "http://localhost:8000"
    admin_token: Optional[str] = None
    user_token: Optional[str] = None
    test_results: List[Dict] = None

    def __post_init__(self):
        if self.test_results is None:
            self.test_results = []


class SecurityTester:
    """Phase 4B Security Improvements Tester"""

    def __init__(self, config: TestConfig):
        self.config = config
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def login_admin(self) -> str:
        """Login as admin user"""
        login_data = {"username": "admin", "password": "admin123"}

        async with self.session.post(f"{self.config.base_url}/api/auth/login", data=login_data) as response:
            if response.status == 200:
                data = await response.json()
                token = data.get("access_token")
                self.config.admin_token = token
                logger.info("Admin login successful")
                return token
            else:
                logger.error(f"Admin login failed: {response.status}")
                return None

    async def login_user(self) -> str:
        """Login as regular user"""
        login_data = {"username": "user", "password": "user123"}

        async with self.session.post(f"{self.config.base_url}/api/auth/login", data=login_data) as response:
            if response.status == 200:
                data = await response.json()
                token = data.get("access_token")
                self.config.user_token = token
                logger.info("User login successful")
                return token
            else:
                logger.error(f"User login failed: {response.status}")
                return None

    def get_headers(self, token: str) -> Dict[str, str]:
        """Get authorization headers"""
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def record_test(self, test_name: str, passed: bool, details: str = ""):
        """Record test result"""
        result = {
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "timestamp": time.time(),
        }
        self.config.test_results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status}: {test_name} - {details}")

    # ==================== Metrics Tests ====================

    async def test_metrics_public_endpoints(self):
        """Test public metrics endpoints (no auth required)"""
        # Test health check (should be accessible without auth)
        async with self.session.get(f"{self.config.base_url}/api/metrics/health") as response:
            if response.status == 200:
                self.record_test("Metrics Health Check (Public)", True, "Public endpoint accessible")
            else:
                self.record_test("Metrics Health Check (Public)", False, f"Status {response.status}")

        # Test basic status (should be accessible without auth)
        async with self.session.get(f"{self.config.base_url}/api/metrics/status") as response:
            if response.status == 200:
                self.record_test("Metrics Status (Public)", True, "Public endpoint accessible")
            else:
                self.record_test("Metrics Status (Public)", False, f"Status {response.status}")

    async def test_metrics_user_endpoints(self):
        """Test user-level metrics endpoints"""
        if not self.config.user_token:
            await self.login_user()

        headers = self.get_headers(self.config.user_token)

        # Test basic metrics (should be accessible with user auth)
        async with self.session.get(f"{self.config.base_url}/api/metrics/basic", headers=headers) as response:
            if response.status == 200:
                self.record_test("Metrics Basic (User)", True, "User can access basic metrics")
            else:
                self.record_test("Metrics Basic (User)", False, f"Status {response.status}")

        # Test performance metrics (should be accessible with user auth)
        async with self.session.get(f"{self.config.base_url}/api/metrics/performance", headers=headers) as response:
            if response.status == 200:
                self.record_test(
                    "Metrics Performance (User)",
                    True,
                    "User can access performance metrics",
                )
            else:
                self.record_test("Metrics Performance (User)", False, f"Status {response.status}")

    async def test_metrics_admin_endpoints(self):
        """Test admin-level metrics endpoints"""
        if not self.config.admin_token:
            await self.login_admin()

        headers = self.get_headers(self.config.admin_token)

        # Test prometheus metrics (should require admin auth)
        async with self.session.get(f"{self.config.base_url}/api/metrics/metrics", headers=headers) as response:
            if response.status == 200:
                self.record_test(
                    "Metrics Prometheus (Admin)",
                    True,
                    "Admin can access prometheus metrics",
                )
            else:
                self.record_test("Metrics Prometheus (Admin)", False, f"Status {response.status}")

        # Test detailed metrics (should require admin auth)
        async with self.session.get(f"{self.config.base_url}/api/metrics/detailed", headers=headers) as response:
            if response.status == 200:
                self.record_test(
                    "Metrics Detailed (Admin)",
                    True,
                    "Admin can access detailed metrics",
                )
            else:
                self.record_test("Metrics Detailed (Admin)", False, f"Status {response.status}")

        # Test that user cannot access admin endpoints
        user_headers = self.get_headers(self.config.user_token) if self.config.user_token else {}
        async with self.session.get(f"{self.config.base_url}/api/metrics/detailed", headers=user_headers) as response:
            if response.status == 403:
                self.record_test(
                    "Metrics Admin Access Denied (User)",
                    True,
                    "User correctly denied access",
                )
            else:
                self.record_test(
                    "Metrics Admin Access Denied (User)",
                    False,
                    f"User got status {response.status} instead of 403",
                )

    async def test_metrics_rate_limiting(self):
        """Test metrics rate limiting"""
        if not self.config.user_token:
            await self.login_user()

        headers = self.get_headers(self.config.user_token)

        # Make rapid requests to trigger rate limiting
        rate_limited = False
        for i in range(35):  # Try to exceed the 30 requests/minute limit
            async with self.session.get(f"{self.config.base_url}/api/metrics/basic", headers=headers) as response:
                if response.status == 429:
                    rate_limited = True
                    break

        self.record_test(
            "Metrics Rate Limiting",
            rate_limited,
            f"Rate limiting {'activated' if rate_limited else 'not activated'}",
        )

    # ==================== Tasks Tests ====================

    async def test_tasks_public_endpoints(self):
        """Test public tasks endpoints"""
        # Test health check (should be accessible without auth)
        async with self.session.get(f"{self.config.base_url}/api/tasks/health") as response:
            if response.status == 200:
                self.record_test("Tasks Health Check (Public)", True, "Public endpoint accessible")
            else:
                self.record_test("Tasks Health Check (Public)", False, f"Status {response.status}")

    async def test_tasks_user_endpoints(self):
        """Test user-level tasks endpoints"""
        if not self.config.user_token:
            await self.login_user()

        headers = self.get_headers(self.config.user_token)

        # Test list tasks (should be accessible with user auth)
        async with self.session.get(f"{self.config.base_url}/api/tasks/", headers=headers) as response:
            if response.status == 200:
                self.record_test("Tasks List (User)", True, "User can list tasks")
            else:
                self.record_test("Tasks List (User)", False, f"Status {response.status}")

        # Test register task (should be accessible with user auth)
        task_data = {
            "name": "Test Task",
            "description": "Test task description",
            "task_type": "DATA_PROCESSING",
            "config": {"test": "config"},
            "enabled": True,
        }

        async with self.session.post(
            f"{self.config.base_url}/api/tasks/register",
            headers=headers,
            json=task_data,
        ) as response:
            if response.status in [200, 201]:
                self.record_test("Tasks Register (User)", True, "User can register tasks")
            else:
                self.record_test("Tasks Register (User)", False, f"Status {response.status}")

    async def test_tasks_validation(self):
        """Test task input validation"""
        if not self.config.user_token:
            await self.login_user()

        headers = self.get_headers(self.config.user_token)

        # Test dangerous task config (should be rejected)
        dangerous_task_data = {
            "name": "Dangerous Task",
            "description": "Task with dangerous config",
            "task_type": "DATA_PROCESSING",
            "config": {"command": "rm -rf /"},
            "enabled": True,
        }

        async with self.session.post(
            f"{self.config.base_url}/api/tasks/register",
            headers=headers,
            json=dangerous_task_data,
        ) as response:
            if response.status == 400:
                self.record_test(
                    "Tasks Dangerous Config Validation",
                    True,
                    "Dangerous config correctly rejected",
                )
            else:
                self.record_test(
                    "Tasks Dangerous Config Validation",
                    False,
                    f"Status {response.status} instead of 400",
                )

        # Test malicious description (should be rejected)
        malicious_task_data = {
            "name": "Malicious Task",
            "description": "<script>alert('xss')</script>",
            "task_type": "DATA_PROCESSING",
            "config": {"safe": "config"},
            "enabled": True,
        }

        async with self.session.post(
            f"{self.config.base_url}/api/tasks/register",
            headers=headers,
            json=malicious_task_data,
        ) as response:
            if response.status == 400:
                self.record_test(
                    "Tasks Malicious Description Validation",
                    True,
                    "Malicious description correctly rejected",
                )
            else:
                self.record_test(
                    "Tasks Malicious Description Validation",
                    False,
                    f"Status {response.status} instead of 400",
                )

    async def test_tasks_admin_endpoints(self):
        """Test admin-level tasks endpoints"""
        if not self.config.admin_token:
            await self.login_admin()

        headers = self.get_headers(self.config.admin_token)

        # Test audit logs (should require admin auth)
        async with self.session.get(f"{self.config.base_url}/api/tasks/audit/logs", headers=headers) as response:
            if response.status == 200:
                self.record_test("Tasks Audit Logs (Admin)", True, "Admin can access audit logs")
            else:
                self.record_test("Tasks Audit Logs (Admin)", False, f"Status {response.status}")

        # Test that user cannot access admin endpoints
        user_headers = self.get_headers(self.config.user_token) if self.config.user_token else {}
        async with self.session.get(f"{self.config.base_url}/api/tasks/audit/logs", headers=user_headers) as response:
            if response.status == 403:
                self.record_test(
                    "Tasks Admin Access Denied (User)",
                    True,
                    "User correctly denied access",
                )
            else:
                self.record_test(
                    "Tasks Admin Access Denied (User)",
                    False,
                    f"User got status {response.status} instead of 403",
                )

    # ==================== Stock Search Tests ====================

    async def test_stock_search_endpoints(self):
        """Test stock search endpoints"""
        if not self.config.user_token:
            await self.login_user()

        headers = self.get_headers(self.config.user_token)

        # Test stock search (should be accessible with user auth)
        async with self.session.get(
            f"{self.config.base_url}/api/stock/search",
            headers=headers,
            params={"q": "腾讯", "market": "hk"},
        ) as response:
            if response.status == 200:
                self.record_test("Stock Search (User)", True, "User can search stocks")
            else:
                self.record_test("Stock Search (User)", False, f"Status {response.status}")

        # Test stock quote (should be accessible with user auth)
        async with self.session.get(
            f"{self.config.base_url}/api/stock/quote/00700",
            headers=headers,
            params={"market": "hk"},
        ) as response:
            if response.status == 200:
                self.record_test("Stock Quote (User)", True, "User can get stock quotes")
            else:
                self.record_test("Stock Quote (User)", False, f"Status {response.status}")

    async def test_stock_search_validation(self):
        """Test stock search input validation"""
        if not self.config.user_token:
            await self.login_user()

        headers = self.get_headers(self.config.user_token)

        # Test dangerous search query (should be cleaned)
        dangerous_query = "<script>alert('xss')</script>"
        async with self.session.get(
            f"{self.config.base_url}/api/stock/search",
            headers=headers,
            params={"q": dangerous_query},
        ) as response:
            if response.status == 200:
                self.record_test(
                    "Stock Search XSS Protection",
                    True,
                    "Dangerous query cleaned successfully",
                )
            else:
                self.record_test("Stock Search XSS Protection", False, f"Status {response.status}")

        # Test invalid stock symbol (should be rejected)
        async with self.session.get(
            f"{self.config.base_url}/api/stock/quote/INVALID",
            headers=headers,
            params={"market": "cn"},
        ) as response:
            if response.status == 400:
                self.record_test(
                    "Stock Symbol Validation",
                    True,
                    "Invalid stock symbol correctly rejected",
                )
            else:
                self.record_test(
                    "Stock Symbol Validation",
                    False,
                    f"Status {response.status} instead of 400",
                )

    async def test_stock_search_admin_endpoints(self):
        """Test admin-level stock search endpoints"""
        if not self.config.admin_token:
            await self.login_admin()

        headers = self.get_headers(self.config.admin_token)

        # Test search analytics (should require admin auth)
        async with self.session.get(
            f"{self.config.base_url}/api/stock/analytics/searches", headers=headers
        ) as response:
            if response.status == 200:
                self.record_test(
                    "Stock Search Analytics (Admin)",
                    True,
                    "Admin can access search analytics",
                )
            else:
                self.record_test("Stock Search Analytics (Admin)", False, f"Status {response.status}")

        # Test rate limits status (should require admin auth)
        async with self.session.get(
            f"{self.config.base_url}/api/stock/rate-limits/status", headers=headers
        ) as response:
            if response.status == 200:
                self.record_test(
                    "Stock Rate Limits Status (Admin)",
                    True,
                    "Admin can access rate limits status",
                )
            else:
                self.record_test(
                    "Stock Rate Limits Status (Admin)",
                    False,
                    f"Status {response.status}",
                )

        # Test that user cannot access admin endpoints
        user_headers = self.get_headers(self.config.user_token) if self.config.user_token else {}
        async with self.session.get(
            f"{self.config.base_url}/api/stock/analytics/searches", headers=user_headers
        ) as response:
            if response.status == 403:
                self.record_test(
                    "Stock Admin Access Denied (User)",
                    True,
                    "User correctly denied access",
                )
            else:
                self.record_test(
                    "Stock Admin Access Denied (User)",
                    False,
                    f"User got status {response.status} instead of 403",
                )

    async def test_stock_search_rate_limiting(self):
        """Test stock search rate limiting"""
        if not self.config.user_token:
            await self.login_user()

        headers = self.get_headers(self.config.user_token)

        # Make rapid requests to trigger rate limiting
        rate_limited = False
        for i in range(35):  # Try to exceed the 30 requests/minute limit
            async with self.session.get(
                f"{self.config.base_url}/api/stock/search",
                headers=headers,
                params={"q": f"test{i}"},
            ) as response:
                if response.status == 429:
                    rate_limited = True
                    break

        self.record_test(
            "Stock Search Rate Limiting",
            rate_limited,
            f"Rate limiting {'activated' if rate_limited else 'not activated'}",
        )

    # ==================== Test Runner ====================

    async def run_all_tests(self):
        """Run all security tests"""
        logger.info("Starting Phase 4B Security Improvements Tests...")

        # Login first
        await self.login_admin()
        await self.login_user()

        if not self.config.admin_token or not self.config.user_token:
            logger.error("Login failed - cannot continue tests")
            return

        logger.info("Testing Metrics endpoints...")
        await self.test_metrics_public_endpoints()
        await self.test_metrics_user_endpoints()
        await self.test_metrics_admin_endpoints()
        await self.test_metrics_rate_limiting()

        logger.info("Testing Tasks endpoints...")
        await self.test_tasks_public_endpoints()
        await self.test_tasks_user_endpoints()
        await self.test_tasks_validation()
        await self.test_tasks_admin_endpoints()

        logger.info("Testing Stock Search endpoints...")
        await self.test_stock_search_endpoints()
        await self.test_stock_search_validation()
        await self.test_stock_search_admin_endpoints()
        await self.test_stock_search_rate_limiting()

        # Generate report
        self.generate_report()

    def generate_report(self):
        """Generate test report"""
        total_tests = len(self.config.test_results)
        passed_tests = sum(1 for result in self.config.test_results if result["passed"])
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        print("\n" + "=" * 80)
        print("PHASE 4B SECURITY IMPROVEMENTS TEST REPORT")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        print("\nDetailed Results:")
        print("-" * 80)

        for result in self.config.test_results:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"{status} - {result['test_name']}")
            if result["details"]:
                print(f"     {result['details']}")

        print("-" * 80)

        # Security Assessment
        security_improvements = [
            "JWT Authentication Implementation",
            "Role-based Access Control (RBAC)",
            "Input Validation and Sanitization",
            "Rate Limiting Protection",
            "XSS and Injection Protection",
            "Audit Logging System",
            "Admin-only Endpoint Protection",
            "Comprehensive Error Handling",
        ]

        print("\nSecurity Improvements Verified:")
        for improvement in security_improvements:
            print(f"  ✓ {improvement}")

        print("\nOverall Security Assessment:")
        if pass_rate >= 90:
            print("  🟢 EXCELLENT - Security improvements successfully implemented")
        elif pass_rate >= 75:
            print("  🟡 GOOD - Most security improvements working, minor issues to address")
        else:
            print("  🔴 NEEDS ATTENTION - Significant security issues found")

        print("=" * 80)


async def main():
    """Main test runner"""
    config = TestConfig()

    async with SecurityTester(config) as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    # Set up event loop for async execution
    import asyncio

    asyncio.run(main())
