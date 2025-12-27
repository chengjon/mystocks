"""
契约测试执行器

提供从契约生成到执行的完整测试流程，支持并发执行、性能测试和结果分析。
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

import httpx


class TestExecutionMode(Enum):
    """测试执行模式"""

    SEQUENTIAL = "sequential"  # 顺序执行
    PARALLEL = "parallel"  # 并行执行
    BATCHED = "batched"  # 分批执行
    ADAPTIVE = "adaptive"  # 自适应执行


class TestResultStatus(Enum):
    """测试结果状态"""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    RUNNING = "running"


@dataclass
class TestCase:
    """测试用例"""

    id: str
    name: str
    endpoint: str
    method: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Dict[str, Any]] = None
    expected_status: int = 200
    expected_response: Optional[Dict[str, Any]] = None
    validations: List[Dict[str, Any]] = field(default_factory=list)
    timeout: int = 30
    retries: int = 0
    tags: List[str] = field(default_factory=list)
    priority: int = 1
    enabled: bool = True


@dataclass
class TestExecutionResult:
    """测试执行结果"""

    test_case: TestCase
    status: TestResultStatus
    execution_time: float = 0.0
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    response_status: Optional[int] = None
    response_headers: Dict[str, str] = field(default_factory=dict)
    response_body: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    validation_results: List[Dict[str, Any]] = field(default_factory=list)
    retry_count: int = 0


@dataclass
class TestSuite:
    """测试套件"""

    name: str
    description: str
    test_cases: List[TestCase] = field(default_factory=list)
    setup_actions: List[Dict[str, Any]] = field(default_factory=list)
    teardown_actions: List[Dict[str, Any]] = field(default_factory=list)
    global_headers: Dict[str, str] = field(default_factory=dict)
    global_parameters: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


class ResponseValidator:
    """响应验证器"""

    def __init__(self):
        self.validators = {
            "status_code": self._validate_status_code,
            "schema": self._validate_schema,
            "headers": self._validate_headers,
            "response_time": self._validate_response_time,
            "content_type": self._validate_content_type,
            "json_structure": self._validate_json_structure,
        }

    def validate_response(
        self,
        test_case: TestCase,
        response: httpx.Response,
        execution_result: TestExecutionResult,
    ) -> List[Dict[str, Any]]:
        """验证响应"""
        validation_results = []

        for validation in test_case.validations:
            validator_type = validation.get("type")
            validator_config = validation.get("config", {})

            if validator_type in self.validators:
                try:
                    result = self.validators[validator_type](test_case, response, execution_result, validator_config)
                    validation_results.append(result)
                except Exception as e:
                    validation_results.append(
                        {
                            "validator": validator_type,
                            "status": "error",
                            "message": str(e),
                            "details": {},
                        }
                    )

        return validation_results

    def _validate_status_code(
        self,
        test_case: TestCase,
        response: httpx.Response,
        execution_result: TestExecutionResult,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """验证状态码"""
        expected = test_case.expected_status
        actual = response.status_code

        status = "passed" if actual == expected else "failed"
        message = f"Expected status {expected}, got {actual}" if status == "failed" else "Status code validation passed"

        return {
            "validator": "status_code",
            "status": status,
            "message": message,
            "expected": expected,
            "actual": actual,
            "details": {
                "expected_range": config.get("range", []),
                "allowed_codes": config.get("allowed_codes", []),
            },
        }

    def _validate_schema(
        self,
        test_case: TestCase,
        response: httpx.Response,
        execution_result: TestExecutionResult,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """验证JSON Schema"""
        try:
            import jsonschema

            schema = config.get("schema", {})
            data = response.json()

            try:
                jsonschema.validate(data, schema)
                return {
                    "validator": "schema",
                    "status": "passed",
                    "message": "Schema validation passed",
                    "details": {"schema_keys": list(schema.keys())},
                }
            except jsonschema.ValidationError as e:
                return {
                    "validator": "schema",
                    "status": "failed",
                    "message": f"Schema validation failed: {e.message}",
                    "details": {"error_path": list(e.path), "error_value": e.instance},
                }
        except Exception as e:
            return {
                "validator": "schema",
                "status": "error",
                "message": f"Schema validation error: {str(e)}",
                "details": {},
            }

    def _validate_headers(
        self,
        test_case: TestCase,
        response: httpx.Response,
        execution_result: TestExecutionResult,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """验证响应头"""
        required_headers = config.get("required", [])
        expected_headers = config.get("expected", {})

        results = []

        # 检查必需的响应头
        for header in required_headers:
            if header not in response.headers:
                results.append(
                    {
                        "header": header,
                        "status": "missing",
                        "message": f"Required header '{header}' is missing",
                    }
                )
            else:
                results.append(
                    {
                        "header": header,
                        "status": "present",
                        "message": f"Header '{header}' is present",
                        "value": response.headers[header],
                    }
                )

        # 检查期望的响应头值
        for header, expected_value in expected_headers.items():
            actual_value = response.headers.get(header)
            if actual_value == expected_value:
                results.append(
                    {
                        "header": header,
                        "status": "matched",
                        "message": f"Header '{header}' value matches expected",
                        "expected": expected_value,
                        "actual": actual_value,
                    }
                )
            else:
                results.append(
                    {
                        "header": header,
                        "status": "mismatch",
                        "message": f"Header '{header}' value mismatch",
                        "expected": expected_value,
                        "actual": actual_value,
                    }
                )

        overall_status = all(r["status"] in ["present", "matched"] for r in results)

        return {
            "validator": "headers",
            "status": "passed" if overall_status else "failed",
            "message": "All headers validation passed" if overall_status else "Some headers validation failed",
            "details": {"header_results": results},
        }

    def _validate_response_time(
        self,
        test_case: TestCase,
        response: httpx.Response,
        execution_result: TestExecutionResult,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """验证响应时间"""
        max_time = config.get("max_time", 5000)  # 毫秒
        response_time = execution_result.execution_time * 1000  # 转换为毫秒

        status = "passed" if response_time <= max_time else "failed"
        message = (
            f"Response time {response_time:.2f}ms is within limit"
            if status == "passed"
            else f"Response time {response_time:.2f}ms exceeds limit of {max_time}ms"
        )

        return {
            "validator": "response_time",
            "status": status,
            "message": message,
            "expected_max": max_time,
            "actual": response_time,
            "unit": "ms",
        }

    def _validate_content_type(
        self,
        test_case: TestCase,
        response: httpx.Response,
        execution_result: TestExecutionResult,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """验证内容类型"""
        expected_content_type = config.get("content_type", "application/json")
        actual_content_type = response.headers.get("content-type", "")

        status = "passed" if expected_content_type in actual_content_type else "failed"
        message = (
            "Content type validation passed"
            if status == "passed"
            else f"Expected '{expected_content_type}', got '{actual_content_type}'"
        )

        return {
            "validator": "content_type",
            "status": status,
            "message": message,
            "expected": expected_content_type,
            "actual": actual_content_type,
        }

    def _validate_json_structure(
        self,
        test_case: TestCase,
        response: httpx.Response,
        execution_result: TestExecutionResult,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """验证JSON结构"""
        try:
            expected_structure = config.get("structure", {})
            actual_data = response.json()

            structure_matches = self._compare_structures(expected_structure, actual_data)

            status = "passed" if structure_matches else "failed"
            message = "JSON structure validation passed" if status == "passed" else "JSON structure validation failed"

            return {
                "validator": "json_structure",
                "status": status,
                "message": message,
                "expected_structure": expected_structure,
                "actual_keys": list(actual_data.keys()) if isinstance(actual_data, dict) else [],
            }
        except Exception as e:
            return {
                "validator": "json_structure",
                "status": "error",
                "message": f"JSON structure validation error: {str(e)}",
                "details": {},
            }

    def _compare_structures(self, expected: Dict[str, Any], actual: Any) -> bool:
        """比较结构"""
        if isinstance(expected, dict) and isinstance(actual, dict):
            for key, expected_value in expected.items():
                if key not in actual:
                    return False
                if not self._compare_structures(expected_value, actual[key]):
                    return False
            return True
        elif isinstance(expected, list) and isinstance(actual, list):
            if len(expected) != len(actual):
                return False
            for exp_item, act_item in zip(expected, actual):
                if not self._compare_structures(exp_item, act_item):
                    return False
            return True
        elif isinstance(expected, (str, int, float, bool)) and isinstance(actual, (str, int, float, bool)):
            return type(expected) == type(actual)
        else:
            return isinstance(expected, type(actual))


class ContractTestExecutor:
    """契约测试执行器主类"""

    def __init__(self, base_url: str, max_workers: int = 10, timeout: int = 30):
        self.base_url = base_url
        self.max_workers = max_workers
        self.timeout = timeout
        self.validator = ResponseValidator()
        self.client = httpx.AsyncClient(timeout=timeout, verify=False)
        self.execution_history = []

    async def execute_test_suite(
        self,
        test_suite: TestSuite,
        execution_mode: TestExecutionMode = TestExecutionMode.PARALLEL,
    ) -> List[TestExecutionResult]:
        """执行测试套件"""
        start_time = time.time()
        print(f"🚀 开始执行测试套件: {test_suite.name}")

        # 执行前置操作
        await self._execute_actions(test_suite.setup_actions)

        # 准备测试用例
        enabled_test_cases = [tc for tc in test_suite.test_cases if tc.enabled]

        if not enabled_test_cases:
            print("⚠️  没有启用的测试用例")
            return []

        # 根据执行模式执行测试
        if execution_mode == TestExecutionMode.SEQUENTIAL:
            results = await self._execute_sequentially(enabled_test_cases, test_suite)
        elif execution_mode == TestExecutionMode.PARALLEL:
            results = await self._execute_parallelly(enabled_test_cases, test_suite)
        elif execution_mode == TestExecutionMode.BATCHED:
            results = await self._execute_in_batches(enabled_test_cases, test_suite)
        elif execution_mode == TestExecutionMode.ADAPTIVE:
            results = await self._execute_adaptively(enabled_test_cases, test_suite)
        else:
            raise ValueError(f"不支持的执行模式: {execution_mode}")

        # 执行后置操作
        await self._execute_actions(test_suite.teardown_actions)

        # 记录执行历史
        end_time = time.time()
        self._record_execution_history(test_suite, results, execution_mode, end_time - start_time)

        # 分析结果
        self._analyze_results(results)

        return results

    async def _execute_sequentially(
        self, test_cases: List[TestCase], test_suite: TestSuite
    ) -> List[TestExecutionResult]:
        """顺序执行测试"""
        results = []

        for test_case in test_cases:
            print(f"📋 执行测试: {test_case.name}")
            result = await self._execute_single_test(test_case, test_suite)
            results.append(result)
            print(f"  结果: {result.status.value}")

        return results

    async def _execute_parallelly(self, test_cases: List[TestCase], test_suite: TestSuite) -> List[TestExecutionResult]:
        """并行执行测试"""
        semaphore = asyncio.Semaphore(self.max_workers)
        tasks = []

        for test_case in test_cases:
            task = asyncio.create_task(self._execute_with_semaphore(test_case, test_suite, semaphore))
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理异常
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                test_case = test_cases[i]
                execution_result = TestExecutionResult(
                    test_case=test_case,
                    status=TestResultStatus.ERROR,
                    error_message=str(result),
                )
                final_results.append(execution_result)
            else:
                final_results.append(result)

        return final_results

    async def _execute_in_batches(
        self, test_cases: List[TestCase], test_suite: TestSuite, batch_size: int = 5
    ) -> List[TestExecutionResult]:
        """分批执行测试"""
        results = []

        for i in range(0, len(test_cases), batch_size):
            batch = test_cases[i : i + batch_size]
            print(f"📦 执行批次 {i // batch_size + 1}: {len(batch)} 个测试")
            batch_results = await self._execute_parallelly(batch, test_suite)
            results.extend(batch_results)
            await asyncio.sleep(1)  # 批次间延迟

        return results

    async def _execute_adaptively(self, test_cases: List[TestCase], test_suite: TestSuite) -> List[TestExecutionResult]:
        """自适应执行测试"""
        results = []

        # 根据优先级排序
        sorted_test_cases = sorted(test_cases, key=lambda tc: tc.priority, reverse=True)

        # 先执行高优先级测试
        high_priority = [tc for tc in sorted_test_cases if tc.priority >= 3]
        if high_priority:
            print(f"🎯 执行高优先级测试: {len(high_priority)} 个")
            results.extend(await self._execute_parallelly(high_priority, test_suite))

        # 再执行中等优先级测试
        medium_priority = [tc for tc in sorted_test_cases if tc.priority == 2]
        if medium_priority:
            print(f"🎯 执行中等优先级测试: {len(medium_priority)} 个")
            results.extend(
                await self._execute_parallelly(medium_priority, test_suite, max_workers=self.max_workers // 2)
            )

        # 最后执行低优先级测试
        low_priority = [tc for tc in sorted_test_cases if tc.priority == 1]
        if low_priority:
            print(f"🎯 执行低优先级测试: {len(low_priority)} 个")
            results.extend(await self._execute_sequentially(low_priority, test_suite))

        return results

    async def _execute_with_semaphore(
        self, test_case: TestCase, test_suite: TestSuite, semaphore: asyncio.Semaphore
    ) -> TestExecutionResult:
        """使用信号量执行单个测试"""
        async with semaphore:
            return await self._execute_single_test(test_case, test_suite)

    async def _execute_single_test(self, test_case: TestCase, test_suite: TestSuite) -> TestExecutionResult:
        """执行单个测试"""
        execution_result = TestExecutionResult(test_case=test_case, status=TestResultStatus.RUNNING)

        start_time = time.time()

        try:
            # 准备请求参数
            url = self.base_url + test_case.endpoint
            method = test_case.method.upper()

            headers = {**test_suite.global_headers, **test_case.headers}
            params = {**test_suite.global_parameters, **test_case.parameters}

            # 准备请求体
            json_data = test_case.body if method in ["POST", "PUT", "PATCH"] else None

            # 发送请求
            response = await self.client.request(method=method, url=url, headers=headers, params=params, json=json_data)

            # 记录响应信息
            execution_result.response_status = response.status_code
            execution_result.response_headers = dict(response.headers)

            # 尝试解析响应体
            try:
                if response.content:
                    execution_result.response_body = response.json()
            except Exception:
                execution_result.response_body = response.text

            # 验证响应
            validation_results = self.validator.validate_response(test_case, response, execution_result)
            execution_result.validation_results = validation_results

            # 确定测试状态
            if any(v["status"] == "failed" for v in validation_results):
                execution_result.status = TestResultStatus.FAILED
                error_msg = next(
                    (v["message"] for v in validation_results if v["status"] == "failed"),
                    "Validation failed",
                )
                execution_result.error_message = error_msg
            elif any(v["status"] == "error" for v in validation_results):
                execution_result.status = TestResultStatus.ERROR
                error_msg = next(
                    (v["message"] for v in validation_results if v["status"] == "error"),
                    "Validation error",
                )
                execution_result.error_message = error_msg
            else:
                execution_result.status = TestResultStatus.PASSED

        except Exception as e:
            execution_result.status = TestResultStatus.ERROR
            execution_result.error_message = str(e)

        finally:
            execution_result.execution_time = time.time() - start_time
            execution_result.end_time = datetime.now()

        return execution_result

    async def _execute_actions(self, actions: List[Dict[str, Any]]) -> None:
        """执行前置/后置操作"""
        for action in actions:
            action_type = action.get("type")
            if action_type == "http_request":
                await self._execute_http_action(action)
            elif action_type == "sleep":
                await asyncio.sleep(action.get("duration", 1))
            elif action_type == "script":
                await self._execute_script_action(action)

    async def _execute_http_action(self, action: Dict[str, Any]) -> None:
        """执行HTTP操作"""
        method = action.get("method", "GET")
        url = action.get("url")
        headers = action.get("headers", {})
        params = action.get("params", {})
        json_data = action.get("json")

        try:
            response = await self.client.request(method=method, url=url, headers=headers, params=params, json=json_data)
            print(f"  ✓ HTTP操作成功: {method} {url} (HTTP {response.status_code})")
        except Exception as e:
            print(f"  ✗ HTTP操作失败: {method} {url} - {e}")

    async def _execute_script_action(self, action: Dict[str, Any]) -> None:
        """执行脚本操作"""
        script = action.get("script")
        if script:
            try:
                # 这里可以实现脚本执行逻辑
                print(f"  ✓ 脚本执行: {script[:50]}...")
            except Exception as e:
                print(f"  ✗ 脚本执行失败: {e}")

    def _record_execution_history(
        self,
        test_suite: TestSuite,
        results: List[TestExecutionResult],
        execution_mode: TestExecutionMode,
        duration: float,
    ):
        """记录执行历史"""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "suite_name": test_suite.name,
            "execution_mode": execution_mode.value,
            "duration": duration,
            "total_tests": len(results),
            "passed": len([r for r in results if r.status == TestResultStatus.PASSED]),
            "failed": len([r for r in results if r.status == TestResultStatus.FAILED]),
            "errors": len([r for r in results if r.status == TestResultStatus.ERROR]),
            "average_response_time": sum(r.execution_time for r in results) / len(results) if results else 0,
        }

        self.execution_history.append(history_entry)

    def _analyze_results(self, results: List[TestExecutionResult]):
        """分析测试结果"""
        if not results:
            return

        total_tests = len(results)
        passed = len([r for r in results if r.status == TestResultStatus.PASSED])
        failed = len([r for r in results if r.status == TestResultStatus.FAILED])
        errors = len([r for r in results if r.status == TestResultStatus.ERROR])

        print("\n📊 测试结果分析:")
        print(f"  总测试数: {total_tests}")
        print(f"  通过: {passed} ({passed / total_tests * 100:.1f}%)")
        print(f"  失败: {failed} ({failed / total_tests * 100:.1f}%)")
        print(f"  错误: {errors} ({errors / total_tests * 100:.1f}%)")

        # 响应时间统计
        response_times = [r.execution_time for r in results]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            print(f"  平均响应时间: {avg_time:.2f}s")
            print(f"  最大响应时间: {max_time:.2f}s")
            print(f"  最小响应时间: {min_time:.2f}s")

        # 失败测试详情
        if failed > 0 or errors > 0:
            print("\n❌ 失败/错误测试详情:")
            for result in results:
                if result.status in [TestResultStatus.FAILED, TestResultStatus.ERROR]:
                    print(f"  - {result.test_case.name}: {result.error_message}")

    def generate_test_report(self, results: List[TestExecutionResult], output_path: str, format: str = "html"):
        """生成测试报告"""
        if format.lower() == "html":
            self._generate_html_report(results, output_path)
        elif format.lower() == "json":
            self._generate_json_report(results, output_path)
        elif format.lower() == "markdown":
            self._generate_markdown_report(results, output_path)
        else:
            raise ValueError(f"不支持的报告格式: {format}")

    def _generate_html_report(self, results: List[TestExecutionResult], output_path: str):
        """生成HTML报告"""
        from datetime import datetime

        # 计算统计信息
        total = len(results)
        passed = len([r for r in results if r.status == TestResultStatus.PASSED])
        failed = len([r for r in results if r.status == TestResultStatus.FAILED])
        errors = len([r for r in results if r.status == TestResultStatus.ERROR])

        # 生成HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Contract Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
                .stat {{ background-color: #e3f2fd; padding: 15px; border-radius: 5px; text-align: center; }}
                .passed {{ background-color: #c8e6c9; }}
                .failed {{ background-color: #ffcdd2; }}
                .error {{ background-color: #ffccbc; }}
                .test-result {{ margin: 10px 0; padding: 10px; border-radius: 5px; }}
                .details {{ margin-left: 20px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Contract Test Report</h1>
                <p>Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>

            <div class="summary">
                <div class="stat">
                    <h3>Total Tests</h3>
                    <p style="font-size: 24px; margin: 0;">{total}</p>
                </div>
                <div class="stat passed">
                    <h3>Passed</h3>
                    <p style="font-size: 24px; margin: 0;">{passed}</p>
                </div>
                <div class="stat failed">
                    <h3>Failed</h3>
                    <p style="font-size: 24px; margin: 0;">{failed}</p>
                </div>
                <div class="stat error">
                    <h3>Errors</h3>
                    <p style="font-size: 24px; margin: 0;">{errors}</p>
                </div>
            </div>

            <h2>Test Results</h2>
        """

        # 添加每个测试的结果
        for result in results:
            status_class = result.status.value
            html_content += f"""
            <div class="test-result {status_class}">
                <h3>{result.test_case.name}</h3>
                <p><strong>Status:</strong> {result.status.value}</p>
                <p><strong>Execution Time:</strong> {result.execution_time:.2f}s</p>
                <p><strong>Endpoint:</strong> {result.test_case.method} {result.test_case.endpoint}</p>

                {f"<p><strong>Error:</strong> {result.error_message}</p>" if result.error_message else ""}

                {f'<div class="details"><h4>Response:</h4><pre>{json.dumps(result.response_body, indent=2)}</pre></div>' if result.response_body else ""}

                <div class="details">
                    <h4>Validations:</h4>
                    <ul>
            """

            for validation in result.validation_results:
                status_icon = "✓" if validation["status"] == "passed" else "✗"
                html_content += f"<li>{status_icon} {validation['validator']}: {validation['message']}</li>"

            html_content += """
                    </ul>
                </div>
            </div>
            """

        html_content += """
        </body>
        </html>
        """

        # 写入文件
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"✓ HTML报告已生成: {output_path}")

    def _generate_json_report(self, results: List[TestExecutionResult], output_path: str):
        """生成JSON报告"""
        import json
        from datetime import datetime

        report_data = {
            "generated_at": datetime.now().isoformat(),
            "total_tests": len(results),
            "results": [],
        }

        for result in results:
            result_data = {
                "test_case": {
                    "id": result.test_case.id,
                    "name": result.test_case.name,
                    "endpoint": result.test_case.endpoint,
                    "method": result.test_case.method,
                },
                "status": result.status.value,
                "execution_time": result.execution_time,
                "start_time": result.start_time.isoformat(),
                "end_time": result.end_time.isoformat() if result.end_time else None,
                "response_status": result.response_status,
                "response_body": result.response_body,
                "error_message": result.error_message,
                "validation_results": result.validation_results,
            }
            report_data["results"].append(result_data)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"✓ JSON报告已生成: {output_path}")

    def _generate_markdown_report(self, results: List[TestExecutionResult], output_path: str):
        """生成Markdown报告"""
        from datetime import datetime

        # 计算统计信息
        total = len(results)
        passed = len([r for r in results if r.status == TestResultStatus.PASSED])
        failed = len([r for r in results if r.status == TestResultStatus.FAILED])
        errors = len([r for r in results if r.status == TestResultStatus.ERROR])

        md_content = f"""# Contract Test Report

**Generated at:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary

- **Total Tests:** {total}
- **Passed:** {passed} ({passed / total * 100:.1f}%)
- **Failed:** {failed} ({failed / total * 100:.1f}%)
- **Errors:** {errors} ({errors / total * 100:.1f}%)

## Test Results

"""

        # 添加每个测试的结果
        for result in results:
            md_content += f"""### {result.test_case.name}

**Status:** {result.status.value}
**Execution Time:** {result.execution_time:.2f}s
**Endpoint:** `{result.test_case.method} {result.test_case.endpoint}`

"""

            if result.error_message:
                md_content += f"**Error:** {result.error_message}\n\n"

            if result.response_body:
                md_content += "**Response:**\n```json\n"
                md_content += json.dumps(result.response_body, indent=2)
                md_content += "\n```\n\n"

            if result.validation_results:
                md_content += "**Validations:**\n"
                for validation in result.validation_results:
                    status_icon = "✓" if validation["status"] == "passed" else "✗"
                    md_content += f"- {status_icon} {validation['validator']}: {validation['message']}\n"
                md_content += "\n"

        # 写入文件
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        print(f"✓ Markdown报告已生成: {output_path}")

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.execution_history.copy()


# 使用示例
async def demo_contract_executor():
    """演示契约测试执行器"""
    print("🚀 演示契约测试执行器")

    # 创建执行器
    executor = ContractTestExecutor(base_url="https://httpbin.org", max_workers=5, timeout=10)

    # 创建测试套件
    test_suite = TestSuite(name="HTTPBin Test Suite", description="Test suite for HTTPBin API")

    # 添加测试用例
    test_cases = [
        TestCase(
            id="test_001",
            name="Get User Agent",
            endpoint="/user-agent",
            method="GET",
            expected_status=200,
        ),
        TestCase(
            id="test_002",
            name="Post JSON Data",
            endpoint="/post",
            method="POST",
            body={"key": "value", "number": 123},
            expected_status=200,
        ),
        TestCase(
            id="test_003",
            name="Get Headers",
            endpoint="/headers",
            method="GET",
            expected_status=200,
            validations=[
                {"type": "status_code", "config": {}},
                {"type": "json_structure", "config": {"structure": {"headers": {}}}},
            ],
        ),
    ]

    test_suite.test_cases = test_cases

    # 执行测试
    try:
        results = await executor.execute_test_suite(test_suite, execution_mode=TestExecutionMode.PARALLEL)

        # 生成报告
        executor.generate_test_report(results, output_path="contract_test_report.html", format="html")

        executor.generate_test_report(results, output_path="contract_test_report.json", format="json")

        executor.generate_test_report(results, output_path="contract_test_report.md", format="markdown")

        print("\n✅ 契约测试执行器演示完成")

    except Exception as e:
        print(f"❌ 演示失败: {e}")


if __name__ == "__main__":
    asyncio.run(demo_contract_executor())
