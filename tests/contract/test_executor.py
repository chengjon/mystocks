#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
契约测试执行器
负责执行契约测试用例和管理测试执行流程
"""

import asyncio
import aiohttp
import logging
import time
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin

from .models import (
    ContractTestSuite,
    ContractTestCase,
    ContractTestConfig,
    TestCategory,
    TestStatus,
    TestExecutionResult,
)
from .contract_validator import ContractValidator

logger = logging.getLogger(__name__)


class ContractTestExecutor:
    """契约测试执行器"""

    def __init__(self, config: ContractTestConfig):
        self.config = config
        self.validator = ContractValidator(config)
        self.session: Optional[aiohttp.ClientSession] = None
        self.results: List[TestExecutionResult] = []

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.cleanup()

    async def initialize(self):
        """初始化执行器"""
        logger.info("初始化契约测试执行器")

        # 创建 aiohttp 会话
        timeout = aiohttp.ClientTimeout(total=self.config.test_timeout)
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=30, ttl_dns_cache=300, use_dns_cache=True)

        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "MyStocks-Contract-Test/1.0",
            },
        )

    async def cleanup(self):
        """清理执行器"""
        if self.session:
            await self.session.close()
        logger.info("契约测试执行器已清理")

    async def execute_suite(self, suite: ContractTestSuite) -> List[TestExecutionResult]:
        """执行测试套件"""
        self.results = []

        if suite.parallel_execution:
            await self._execute_parallel(suite)
        else:
            await self._execute_sequential(suite)

        return self.results

    async def _execute_parallel(self, suite: ContractTestSuite):
        """并行执行测试用例"""
        logger.info(f"并行执行测试套件: {suite.name} (并发数: {suite.max_workers})")

        # 创建并发任务
        tasks = []
        for test_case in suite.test_cases:
            if test_case.enabled:
                task = asyncio.create_task(
                    self._execute_test_case_with_retry(test_case),
                    name=f"test_{test_case.name}",
                )
                tasks.append(task)

                # 限制并发数
                if len(tasks) >= suite.max_workers:
                    # 等待当前批次完成
                    batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                    results = self._process_batch_results(batch_results)
                    self.results.extend(results)
                    tasks = []

        # 执行剩余任务
        if tasks:
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            results = self._process_batch_results(batch_results)
            self.results.extend(results)

    async def _execute_sequential(self, suite: ContractTestSuite):
        """顺序执行测试用例"""
        logger.info(f"顺序执行测试套件: {suite.name}")

        for test_case in suite.test_cases:
            if test_case.enabled:
                try:
                    result = await self._execute_test_case_with_retry(test_case)
                    self.results.append(result)
                except Exception as e:
                    logger.error(f"执行测试用例 {test_case.name} 时发生异常: {e}")
                    error_result = TestExecutionResult(
                        test_case=test_case,
                        status=TestStatus.ERROR,
                        duration=0.0,
                        error_message=str(e),
                    )
                    self.results.append(error_result)

    async def _execute_test_case_with_retry(self, test_case: ContractTestCase) -> TestExecutionResult:
        """执行测试用例（带重试机制）"""
        last_error = None

        for attempt in range(self.config.max_retries + 1):
            try:
                result = await self._execute_test_case(test_case)

                if result.status == TestStatus.PASSED:
                    return result

                # 如果不是最后一次尝试，等待后重试
                if attempt < self.config.max_retries:
                    await asyncio.sleep(self.config.retry_delay)
                    last_error = result.error_message
                    continue

                return result

            except Exception as e:
                last_error = str(e)
                logger.warning(f"测试用例 {test_case.name} 第 {attempt + 1} 次执行失败: {e}")

                if attempt < self.config.max_retries:
                    await asyncio.sleep(self.config.retry_delay)

        # 所有重试都失败
        return TestExecutionResult(
            test_case=test_case,
            status=TestStatus.FAILED,
            duration=0.0,
            error_message=f"所有重试都失败: {last_error}",
        )

    async def _execute_test_case(self, test_case: ContractTestCase) -> TestExecutionResult:
        """执行单个测试用例"""
        start_time = time.time()

        try:
            # 检查跳过条件
            if await self._should_skip_test(test_case):
                return TestExecutionResult(test_case=test_case, status=TestStatus.SKIPPED, duration=0.0)

            # 准备请求
            request_data = await self._prepare_request(test_case)

            # 执行请求
            response, response_time = await self._make_request(test_case.method, test_case.endpoint, request_data)

            # 解析响应
            response_data = await self._parse_response(response)

            # 记录请求 ID
            request_id = response_data.get("request_id") or response.headers.get("X-Request-ID")
            test_case.request_id = request_id

            # 验证响应
            validation_result = self.validator.validate_response_data(response_data, test_case)

            # 收集性能指标
            performance_metrics = self._collect_performance_metrics(response, response_time, test_case)

            # 确定测试状态
            if validation_result.is_valid():
                status = TestStatus.PASSED
            else:
                status = TestStatus.FAILED
                error_message = "; ".join(validation_result.errors[:3])  # 只显示前3个错误

            # 生成验证结果摘要
            validation_results = [
                {
                    "rule": rule.get("type", "unknown"),
                    "valid": True,
                    "message": "验证通过",
                }
                for rule in test_case.validation_rules
            ]

            # 添加验证失败的详细信息
            for error in validation_result.errors:
                validation_results.append({"rule": "general", "valid": False, "message": error})

            duration = time.time() - start_time

            return TestExecutionResult(
                test_case=test_case,
                status=status,
                duration=duration,
                response_data=response_data,
                error_message=error_message,
                validation_results=validation_results,
                performance_metrics=performance_metrics,
            )

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"执行测试用例 {test_case.name} 时发生异常: {e}")

            return TestExecutionResult(
                test_case=test_case,
                status=TestStatus.ERROR,
                duration=duration,
                error_message=str(e),
            )

    async def _should_skip_test(self, test_case: ContractTestCase) -> bool:
        """检查是否应该跳过测试"""
        # 检查跳过条件
        for condition in test_case.skip_conditions:
            if condition.lower() == "offline" and not await self._check_network_connectivity():
                logger.info(f"跳过测试 {test_case.name}: 网络离线")
                return True

            if condition.lower() == "maintenance" and await self._check_maintenance_mode():
                logger.info(f"跳过测试 {test_case.name}: 维护模式")
                return True

        # 检查特定类别的跳过条件
        if test_case.category == TestCategory.SECURITY and not self.config.enable_security_tests:
            logger.info(f"跳过安全测试: {test_case.name}")
            return True

        if test_case.category == TestCategory.AUTHENTICATION and not self.config.enable_auth_tests:
            logger.info(f"跳过认证测试: {test_case.name}")
            return True

        return False

    async def _check_network_connectivity(self) -> bool:
        """检查网络连接"""
        try:
            async with self.session.get(f"{self.config.api_base_url}/api/health", timeout=5) as response:
                return response.status == 200
        except:
            return False

    async def _check_maintenance_mode(self) -> bool:
        """检查维护模式"""
        try:
            async with self.session.get(f"{self.config.api_base_url}/api/system/maintenance", timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("maintenance_mode", False)
                return False
        except:
            return False

    async def _prepare_request(self, test_case: ContractTestCase) -> Dict[str, Any]:
        """准备请求数据"""
        request_data = {}

        # 构建查询参数
        if test_case.params:
            request_data["params"] = test_case.params.copy()

        # 构建请求头
        headers = {}
        headers.update(test_case.headers)

        # 添加认证头（如果需要）
        if test_case.category == TestCategory.AUTHENTICATION:
            # 可以在这里添加预认证逻辑
            pass

        # 设置内容类型
        if test_case.body:
            headers["Content-Type"] = "application/json"

        # 添加 CSRF 保护
        if test_case.method.upper() in ["POST", "PUT", "PATCH", "DELETE"]:
            csrf_token = await self._get_csrf_token()
            if csrf_token:
                headers["X-CSRF-Token"] = csrf_token

        request_data["headers"] = headers

        # 构建请求体
        if test_case.body:
            request_data["json"] = test_case.body

        return request_data

    async def _get_csrf_token(self) -> Optional[str]:
        """获取 CSRF token"""
        try:
            # 可以从 cookie 中获取
            # 或者从专门的 endpoint 获取
            return None  # 简化实现
        except Exception:
            return None

    async def _make_request(
        self, method: str, endpoint: str, request_data: Dict[str, Any]
    ) -> tuple[aiohttp.ClientResponse, float]:
        """执行 HTTP 请求"""
        start_time = time.time()

        # 构建 URL
        url = urljoin(self.config.api_base_url, endpoint)

        # 准备请求参数
        kwargs = {}
        if "headers" in request_data:
            kwargs["headers"] = request_data["headers"]
        if "params" in request_data:
            kwargs["params"] = request_data["params"]
        if "json" in request_data:
            kwargs["json"] = request_data["json"]

        # 执行请求
        async with self.session.request(method, url, **kwargs) as response:
            await response.text()  # 读取响应体以保持连接
            response_time = time.time() - start_time

            return response, response_time

    async def _parse_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """解析响应数据"""
        try:
            content_type = response.headers.get("Content-Type", "")

            if "application/json" in content_type:
                return await response.json()
            elif "text/" in content_type:
                text = await response.text()
                return {
                    "raw_response": text,
                    "status_code": response.status,
                    "headers": dict(response.headers),
                }
            else:
                return {
                    "status_code": response.status,
                    "headers": dict(response.headers),
                    "content_type": content_type,
                }

        except Exception as e:
            logger.error(f"解析响应失败: {e}")
            return {
                "status_code": response.status,
                "error": str(e),
                "headers": dict(response.headers),
            }

    def _collect_performance_metrics(
        self,
        response: aiohttp.ClientResponse,
        response_time: float,
        test_case: ContractTestCase,
    ) -> Dict[str, Any]:
        """收集性能指标"""
        metrics = {
            "response_time_ms": round(response_time * 1000, 2),
            "status_code": response.status,
            "content_length": len(await response.read()) if response else 0,
        }

        # 根据测试类别添加特定指标
        if test_case.category == TestCategory.PERFORMANCE:
            # 计算响应时间评分
            threshold = self.config.performance_threshold.get("response_time_ms", 1000)
            if response_time * 1000 <= threshold:
                metrics["performance_score"] = 100
            else:
                metrics["performance_score"] = max(0, 100 - (response_time * 1000 - threshold) / threshold * 100)

        return metrics

    def _process_batch_results(self, batch_results: List) -> List[TestExecutionResult]:
        """处理批次执行结果"""
        results = []

        for result in batch_results:
            if isinstance(result, TestExecutionResult):
                results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"批次执行中发生异常: {result}")
                # 可以创建一个错误结果或记录到日志
            else:
                logger.warning(f"意外的结果类型: {type(result)}")

        return results

    async def execute_single_test(self, test_case: ContractTestCase) -> TestExecutionResult:
        """执行单个测试用例（独立方法）"""
        return await self._execute_test_case_with_retry(test_case)

    def get_statistics(self) -> Dict[str, Any]:
        """获取执行统计信息"""
        if not self.results:
            return {}

        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAILED)
        skipped = sum(1 for r in self.results if r.status == TestStatus.SKIPPED)
        error = sum(1 for r in self.results if r.status == TestStatus.ERROR)

        # 计算平均响应时间
        response_times = [r.performance_metrics.get("response_time_ms", 0) for r in self.results]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        # 按类别统计
        category_stats = {}
        for result in self.results:
            category = result.test_case.category.value
            if category not in category_stats:
                category_stats[category] = {"total": 0, "passed": 0, "failed": 0}
            category_stats[category]["total"] += 1
            if result.status == TestStatus.PASSED:
                category_stats[category]["passed"] += 1
            elif result.status in [TestStatus.FAILED, TestStatus.ERROR]:
                category_stats[category]["failed"] += 1

        return {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": failed,
            "skipped_tests": skipped,
            "error_tests": error,
            "success_rate": round((passed / total) * 100, 2) if total > 0 else 0,
            "average_response_time_ms": round(avg_response_time, 2),
            "category_statistics": category_stats,
        }
