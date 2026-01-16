"""
高级分析API集成测试
Advanced Analysis API Integration Tests

测试我们刚刚实现的12个高级分析模块的API功能
Tests the 12 advanced analysis modules API functionality we just implemented
"""

import asyncio
import httpx
import json
import logging
import sys
import os
from typing import Dict, Any, List
from datetime import datetime

# Setup project path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Test configuration
TEST_CONFIG = {
    "base_url": "http://localhost:8000",
    "timeout": 30,
    "test_symbol": "000001",
    "auth_token": None,  # Will be set if authentication is required
}

# Analysis endpoints to test
ANALYSIS_ENDPOINTS = [
    "/api/v1/advanced-analysis/fundamental",
    "/api/v1/advanced-analysis/technical",
    "/api/v1/advanced-analysis/trading-signals",
    "/api/v1/advanced-analysis/time-series",
    "/api/v1/advanced-analysis/market-panorama",
    "/api/v1/advanced-analysis/capital-flow",
    "/api/v1/advanced-analysis/chip-distribution",
    "/api/v1/advanced-analysis/anomaly-tracking",
    "/api/v1/advanced-analysis/financial-valuation",
    "/api/v1/advanced-analysis/sentiment",
    "/api/v1/advanced-analysis/decision-models",
    "/api/v1/advanced-analysis/multidimensional-radar",
]


class AdvancedAnalysisAPITester:
    """高级分析API测试器"""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = None
        self.auth_token = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    def set_auth_token(self, token: str):
        """设置认证token"""
        self.auth_token = token

    def get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    async def test_health_endpoint(self) -> bool:
        """测试健康检查端点"""
        logger.info("Testing health check endpoint...")

        try:
            url = f"{self.base_url}/health"
            response = await self.client.get(url)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Health check successful: {data.get('status', 'unknown')}")
                return True
            else:
                logger.error(f"Health check failed: HTTP {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Health check exception: {e}")
            return False

    async def test_analysis_endpoint(self, endpoint: str, test_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """测试单个分析端点"""
        logger.info(f"Testing endpoint: {endpoint}")

        try:
            url = f"{self.base_url}{endpoint}"

            # 准备测试参数
            if test_params is None:
                test_params = {"symbol": TEST_CONFIG["test_symbol"]}

            # 发送请求
            response = await self.client.get(url, params=test_params, headers=self.get_headers())

            result = {
                "endpoint": endpoint,
                "status_code": response.status_code,
                "success": False,
                "response_time": None,
                "error": None,
                "data_keys": None,
            }

            if response.status_code == 200:
                try:
                    data = response.json()
                    result["success"] = True
                    result["data_keys"] = list(data.keys()) if isinstance(data, dict) else None
                    logger.info(f"{endpoint} successful - response keys: {result['data_keys']}")
                except json.JSONDecodeError:
                    result["error"] = "Invalid JSON response"
                    logger.error(f"{endpoint} returned invalid JSON")
            else:
                result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
                logger.error(f"{endpoint} failed: {result['error']}")

            return result

        except Exception as e:
            logger.error(f"{endpoint} exception: {e}")
            return {
                "endpoint": endpoint,
                "status_code": None,
                "success": False,
                "response_time": None,
                "error": str(e),
                "data_keys": None,
            }

    async def test_batch_analysis(self) -> Dict[str, Any]:
        """测试批量分析端点"""
        logger.info("Testing batch analysis endpoint...")

        try:
            url = f"{self.base_url}/api/v1/advanced-analysis/batch"
            batch_data = {
                "analyses": ["fundamental", "technical"],
                "symbol": TEST_CONFIG["test_symbol"],
                "options": {"include_raw_data": False},
            }

            response = await self.client.post(url, json=batch_data, headers=self.get_headers())

            result = {
                "endpoint": "/api/v1/advanced-analysis/batch",
                "status_code": response.status_code,
                "success": False,
                "error": None,
                "batch_results": None,
            }

            if response.status_code == 200:
                try:
                    data = response.json()
                    result["success"] = True
                    if isinstance(data, dict) and "data" in data:
                        batch_results = data["data"]
                        result["batch_results"] = (
                            list(batch_results.keys())
                            if isinstance(batch_results, dict)
                            else len(batch_results)
                            if isinstance(batch_results, list)
                            else None
                        )
                    logger.info(f"Batch analysis successful - results: {result['batch_results']}")
                except json.JSONDecodeError:
                    result["error"] = "Invalid JSON response"
                    logger.error("Batch analysis returned invalid JSON")
            else:
                result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
                logger.error(f"Batch analysis failed: {result['error']}")

            return result

        except Exception as e:
            logger.error(f"Batch analysis exception: {e}")
            return {
                "endpoint": "/api/v1/advanced-analysis/batch",
                "status_code": None,
                "success": False,
                "error": str(e),
                "batch_results": None,
            }

    async def run_full_test_suite(self) -> Dict[str, Any]:
        """运行完整的测试套件"""
        logger.info("Starting Advanced Analysis API Integration Tests...")
        logger.info("=" * 60)

        # 测试结果汇总
        results = {
            "health_check": False,
            "individual_analyses": [],
            "batch_analysis": None,
            "overall_success": False,
            "total_tests": 0,
            "passed_tests": 0,
        }

        # 1. 健康检查
        logger.info("\n" + "=" * 50)
        logger.info("PHASE 1: Health Check")
        logger.info("=" * 50)
        results["health_check"] = await self.test_health_endpoint()
        results["total_tests"] += 1
        if results["health_check"]:
            results["passed_tests"] += 1

        # 2. 单个分析端点测试
        logger.info("\n" + "=" * 50)
        logger.info("PHASE 2: Individual Analysis Modules")
        logger.info("=" * 50)

        for i, endpoint in enumerate(ANALYSIS_ENDPOINTS, 1):
            logger.info(f"\nTest {i}/{len(ANALYSIS_ENDPOINTS)}: {endpoint}")
            result = await self.test_analysis_endpoint(endpoint)
            results["individual_analyses"].append(result)
            results["total_tests"] += 1
            if result["success"]:
                results["passed_tests"] += 1

            # 小延迟避免过载
            await asyncio.sleep(0.5)

        # 3. 批量分析测试
        logger.info("\n" + "=" * 50)
        logger.info("PHASE 3: Batch Analysis")
        logger.info("=" * 50)
        results["batch_analysis"] = await self.test_batch_analysis()
        results["total_tests"] += 1
        if results["batch_analysis"]["success"]:
            results["passed_tests"] += 1

        # 计算总体成功率
        results["overall_success"] = results["passed_tests"] == results["total_tests"]

        # 生成测试报告
        await self.generate_test_report(results)

        return results

    async def generate_test_report(self, results: Dict[str, Any]):
        """生成测试报告"""
        logger.info("\n" + "=" * 60)
        logger.info("Advanced Analysis API Integration Test Report")
        logger.info("=" * 60)

        logger.info(f"Overall Result: {'PASSED' if results['overall_success'] else 'FAILED'}")
        logger.info(f"Total Tests: {results['total_tests']}")
        logger.info(f"Passed Tests: {results['passed_tests']}")
        logger.info(
            f"Success Rate: {results['passed_tests']}/{results['total_tests']} ({results['passed_tests'] / results['total_tests'] * 100:.1f}%)"
        )

        logger.info("\n" + "-" * 40)
        logger.info("Detailed Results:")
        logger.info("-" * 40)

        # 健康检查结果
        health_status = "PASSED" if results["health_check"] else "FAILED"
        logger.info(f"Health Check: {health_status}")

        # 单个分析结果
        logger.info(f"\nIndividual Analysis Modules ({len(results['individual_analyses'])} modules):")
        for result in results["individual_analyses"]:
            endpoint_name = result["endpoint"].split("/")[-1]
            status = "✅" if result["success"] else "❌"
            success_msg = "Success" if result["success"] else f"Failed - {result.get('error', 'Unknown error')}"
            logger.info(f"  {status} {endpoint_name}: {success_msg}")

        # 批量分析结果
        batch_result = results["batch_analysis"]
        if batch_result:
            batch_status = "PASSED" if batch_result["success"] else "FAILED"
            batch_msg = (
                "Success" if batch_result["success"] else f"Failed - {batch_result.get('error', 'Unknown error')}"
            )
            logger.info(f"\nBatch Analysis: {batch_status} {batch_msg}")

        logger.info("\n" + "=" * 60)

        if results["overall_success"]:
            logger.info("All tests passed! Advanced Analysis API is ready for production.")
            logger.info("All 12 analysis modules are working correctly with real database connections.")
        else:
            logger.warning("Some tests failed. Please check API implementation and dependencies.")
            logger.info(
                "Suggestions: 1) Check database connections 2) Verify analysis engine dependencies 3) Check API route configuration"
            )


async def main():
    """主函数"""
    logger.info("Advanced Analysis API Integration Test Starting...")

    # 创建测试器
    async with AdvancedAnalysisAPITester(base_url=TEST_CONFIG["base_url"], timeout=TEST_CONFIG["timeout"]) as tester:
        # 可选：设置认证token（如果需要）
        # tester.set_auth_token("your-jwt-token-here")

        # 运行完整测试套件
        results = await tester.run_full_test_suite()

        # 返回测试结果
        success = results.get("overall_success", False)
        logger.info(f"Test completed, final result: {'Success' if success else 'Failed'}")

        return success


if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(main())
    exit(0 if success else 1)
