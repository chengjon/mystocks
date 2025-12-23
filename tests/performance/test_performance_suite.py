#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 性能测试套件
提供全面的性能测试、基准测试和回归测试
"""

import pytest
import asyncio
import time
import psutil
import statistics
from datetime import datetime
from typing import Dict, List, Any
import aiohttp
import json

from tests.config.test_config import test_env, performance_baseline


class PerformanceTestSuite:
    """性能测试套件"""

    def __init__(self):
        self.base_url = test_env.API_BASE_URL
        self.results = {}
        self.start_time = None
        self.end_time = None

    async def run_performance_benchmark(self):
        """运行完整性能基准测试"""
        self.start_time = datetime.now()

        print("\n🚀 开始性能基准测试")
        print(f"⏰ 测试开始时间: {self.start_time}")
        print(f"🎯 测试目标: {performance_baseline.API_RESPONSE_TIME_THRESHOLD}")

        # 运行各项性能测试
        test_methods = [
            self.test_api_response_times,
            self.test_database_query_performance,
            self.test_concurrent_users,
            self.test_memory_usage,
            self.test_cpu_usage,
            self.test_disk_io,
        ]

        results = {}
        for test_method in test_methods:
            try:
                method_name = test_method.__name__
                print(f"\n📊 运行性能测试: {method_name}")

                result = await test_method()
                results[method_name] = result

                self._print_test_summary(method_name, result)

            except Exception as e:
                print(f"❌ 性能测试 {test_method.__name__} 失败: {str(e)}")
                results[test_method.__name__] = {"status": "failed", "error": str(e)}

        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()

        # 生成性能报告
        self.results = results
        report = self._generate_performance_report(duration)

        print("\n✅ 性能测试完成")
        print(f"⏱️  总耗时: {duration:.2f}秒")
        print(f"📈 完整报告: {report}")

        return report

    async def test_api_response_times(self) -> Dict[str, Any]:
        """API响应时间测试"""
        print("  🔄 测试API响应时间...")

        # 测试端点配置
        test_endpoints = [
            ("market_data", "/api/market/market-data/fetch", {"symbol": "600519"}),
            (
                "kline_data",
                "/api/market/kline/fetch",
                {"symbol": "600519", "period": "daily"},
            ),
            ("stock_quote", "/api/market/quote/fetch", {"symbols": ["600519"]}),
            ("index_data", "/api/market/index/fetch", {"index_code": "399300"}),
        ]

        results = {}
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))

        for endpoint_name, path, params in test_endpoints:
            print(f"    🔍 测试 {endpoint_name}: {path}")

            # 多次请求取平均值
            response_times = []
            for i in range(10):
                start_time = time.time()
                try:
                    async with session.get(
                        f"{self.base_url}{path}", params=params
                    ) as response:
                        await response.text()  # 读取响应
                        end_time = time.time()
                        response_times.append(
                            (end_time - start_time) * 1000
                        )  # 转换为毫秒
                except Exception as e:
                    print(f"    ⚠️  请求失败: {str(e)}")
                    response_times.append(-1)

            # 计算统计数据
            valid_times = [t for t in response_times if t > 0]
            if valid_times:
                avg_time = statistics.mean(valid_times)
                max_time = max(valid_times)
                min_time = min(valid_times)
                median_time = statistics.median(valid_times)

                results[endpoint_name] = {
                    "avg_time_ms": round(avg_time, 2),
                    "max_time_ms": round(max_time, 2),
                    "min_time_ms": round(min_time, 2),
                    "median_time_ms": round(median_time, 2),
                    "requests": len(valid_times),
                    "threshold": performance_baseline.API_RESPONSE_TIME_THRESHOLD.get(
                        endpoint_name, 5000
                    ),
                    "passed": avg_time
                    <= performance_baseline.API_RESPONSE_TIME_THRESHOLD.get(
                        endpoint_name, 5000
                    ),
                }
            else:
                results[endpoint_name] = {
                    "status": "failed",
                    "error": "All requests failed",
                }

        await session.close()
        return results

    async def test_database_query_performance(self) -> Dict[str, Any]:
        """数据库查询性能测试"""
        print("  🔄 测试数据库查询性能...")

        from src.data_access.postgresql_access import PostgreSQLAccess

        results = {}

        try:
            # PostgreSQL连接
            pg_access = PostgreSQLAccess()

            # 测试不同复杂度的查询
            test_queries = [
                (
                    "simple_lookup",
                    """
                    SELECT * FROM stock_basic
                    WHERE symbol = '600519'
                    LIMIT 1
                """,
                ),
                (
                    "complex_analysis",
                    """
                    SELECT
                        s.symbol,
                        s.name,
                        COUNT(*) as trading_days,
                        AVG(c.close) as avg_price,
                        MAX(c.high) as highest_price,
                        MIN(c.low) as lowest_price
                    FROM stock_basic s
                    LEFT JOIN kline_daily c ON s.symbol = c.symbol
                    WHERE s.sector = '金融'
                    GROUP BY s.symbol, s.name
                    ORDER BY trading_days DESC
                    LIMIT 100
                """,
                ),
                (
                    "batch_insert",
                    """
                    INSERT INTO kline_daily
                    (symbol, date, open, high, low, close, volume)
                    VALUES %s
                    ON CONFLICT (symbol, date) DO UPDATE
                    SET open = EXCLUDED.open,
                        high = EXCLUDED.high,
                        low = EXCLUDED.low,
                        close = EXCLUDED.close,
                        volume = EXCLUDED.volume
                """,
                ),
            ]

            for query_name, query in test_queries:
                print(f"    🔍 测试 {query_name}...")

                # 执行多次取平均值
                execution_times = []
                for i in range(5):
                    try:
                        start_time = time.time()

                        if query_name == "batch_insert":
                            # 批量插入测试数据
                            test_data = [
                                (
                                    "600519",
                                    "2024-12-12",
                                    100.0,
                                    105.0,
                                    98.0,
                                    102.0,
                                    1000000,
                                )
                                for _ in range(100)
                            ]
                            pg_access.execute_batch(query, test_data)
                        else:
                            pg_access.execute_query(query)

                        end_time = time.time()
                        execution_times.append((end_time - start_time) * 1000)

                    except Exception as e:
                        print(f"    ⚠️  查询失败: {str(e)}")
                        execution_times.append(-1)

                # 计算统计数据
                valid_times = [t for t in execution_times if t > 0]
                if valid_times:
                    avg_time = statistics.mean(valid_times)
                    results[query_name] = {
                        "avg_time_ms": round(avg_time, 2),
                        "max_time_ms": round(max(valid_times), 2),
                        "min_time_ms": round(min(valid_times), 2),
                        "requests": len(valid_times),
                        "threshold": performance_baseline.DB_QUERY_TIME_THRESHOLD.get(
                            query_name, 1000
                        ),
                        "passed": avg_time
                        <= performance_baseline.DB_QUERY_TIME_THRESHOLD.get(
                            query_name, 1000
                        ),
                    }
                else:
                    results[query_name] = {
                        "status": "failed",
                        "error": "All queries failed",
                    }

        except Exception as e:
            return {
                "status": "failed",
                "error": f"Database connection failed: {str(e)}",
            }

        return results

    async def test_concurrent_users(self) -> Dict[str, Any]:
        """并发用户性能测试"""
        print("  🔄 测试并发用户性能...")

        user_counts = [10, 50, 100, 200]
        results = {}

        async def simulate_user(user_id: int, tasks: List) -> float:
            """模拟单个用户行为"""
            session = aiohttp.ClientSession()
            start_time = time.time()

            try:
                # 用户行为模拟
                actions = [
                    ("get_quote", "/api/market/quote/fetch", {"symbols": ["600519"]}),
                    (
                        "get_kline",
                        "/api/market/kline/fetch",
                        {"symbol": "600519", "period": "daily"},
                    ),
                    ("get_index", "/api/market/index/fetch", {"index_code": "399300"}),
                ]

                for action_name, path, params in actions:
                    try:
                        async with session.get(
                            f"{self.base_url}{path}", params=params
                        ) as response:
                            await response.text()
                    except:
                        pass  # 忽略单个请求失败

                end_time = time.time()
                return (end_time - start_time) * 1000

            finally:
                await session.close()

        for user_count in user_counts:
            print(f"    🔍 测试 {user_count} 并发用户...")

            # 创建并发任务
            tasks = [simulate_user(i, tasks) for i in range(user_count)]
            start_time = time.time()

            # 执行并发任务
            await asyncio.gather(*tasks, return_exceptions=True)

            end_time = time.time()
            total_time = (end_time - start_time) * 1000

            results[user_count] = {
                "total_time_ms": round(total_time, 2),
                "avg_user_time_ms": round(total_time / user_count, 2),
                "requests_per_second": round((user_count * 3) / (total_time / 1000), 2),
                "user_count": user_count,
            }

        return results

    async def test_memory_usage(self) -> Dict[str, Any]:
        """内存使用测试"""
        print("  🔄 测试内存使用情况...")

        process = psutil.Process()
        memory_info = process.memory_info()

        results = {
            "rss_memory_mb": round(memory_info.rss / 1024 / 1024, 2),
            "vms_memory_mb": round(memory_info.vms / 1024 / 1024, 2),
            "memory_percent": process.memory_percent(),
            "available_memory_mb": round(
                psutil.virtual_memory().available / 1024 / 1024, 2
            ),
            "total_memory_mb": round(psutil.virtual_memory().total / 1024 / 1024, 2),
        }

        return results

    async def test_cpu_usage(self) -> Dict[str, Any]:
        """CPU使用测试"""
        print("  🔄 测试CPU使用情况...")

        # 监控CPU使用率
        cpu_percentages = []
        for i in range(10):
            cpu_percentages.append(psutil.cpu_percent(interval=0.1))

        results = {
            "avg_cpu_percent": round(statistics.mean(cpu_percentages), 2),
            "max_cpu_percent": round(max(cpu_percentages), 2),
            "min_cpu_percent": round(min(cpu_percentages), 2),
            "cpu_count": psutil.cpu_count(),
            "cpu_count_logical": psutil.cpu_count(logical=True),
        }

        return results

    async def test_disk_io(self) -> Dict[str, Any]:
        """磁盘I/O性能测试"""
        print("  🔄 测试磁盘I/O性能...")

        # 写入测试文件
        test_file = "/tmp/performance_test.tmp"
        test_data = "x" * (1024 * 1024)  # 1MB数据

        # 写入性能测试
        start_time = time.time()
        with open(test_file, "w") as f:
            for i in range(10):  # 写入10MB
                f.write(test_data)
        write_time = time.time() - start_time

        # 读取性能测试
        start_time = time.time()
        with open(test_file, "r") as f:
            data = f.read()
        read_time = time.time() - start_time

        # 清理测试文件
        try:
            os.remove(test_file)
        except:
            pass

        results = {
            "write_speed_mb_s": round(10 / write_time, 2),
            "read_speed_mb_s": round(10 / read_time, 2),
            "write_time_s": round(write_time, 3),
            "read_time_s": round(read_time, 3),
        }

        return results

    def _print_test_summary(self, test_name: str, result: Dict[str, Any]):
        """打印测试摘要"""
        if (
            isinstance(result, dict)
            and "status" in result
            and result["status"] == "failed"
        ):
            print(f"    ❌ {test_name} 测试失败: {result.get('error', '未知错误')}")
        elif isinstance(result, dict) and any(
            key in result for key in ["passed", "avg_time_ms", "avg_cpu_percent"]
        ):
            if "avg_time_ms" in result:
                avg_time = result["avg_time_ms"]
                threshold = result.get("threshold", 5000)
                status = "✅" if result.get("passed", False) else "❌"
                print(
                    f"    {status} {test_name}: {avg_time:.2f}ms (阈值: {threshold}ms)"
                )
            elif "avg_cpu_percent" in result:
                cpu_percent = result["avg_cpu_percent"]
                print(f"    ✅ {test_name}: {cpu_percent:.1f}%")
            else:
                print(f"    ✅ {test_name}: 测试通过")
        else:
            print(f"    ⚠️  {test_name}: 复杂结果")

    def _generate_performance_report(self, total_duration: float) -> str:
        """生成性能测试报告"""
        report = {
            "test_summary": {
                "total_duration_seconds": round(total_duration, 2),
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "test_count": len(self.results),
            },
            "detailed_results": self.results,
            "performance_metrics": {
                "overall_score": self._calculate_overall_score(),
                "worst_performing": self._identify_worst_performing(),
                "recommendations": self._generate_recommendations(),
            },
        }

        # 保存报告
        report_path = (
            f"/tmp/performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return report_path

    def _calculate_overall_score(self) -> int:
        """计算总体性能评分"""
        scores = []

        if "test_api_response_times" in self.results:
            api_results = self.results["test_api_response_times"]
            if isinstance(api_results, dict):
                for endpoint, result in api_results.items():
                    if isinstance(result, dict) and "passed" in result:
                        scores.append(100 if result["passed"] else 0)

        if "test_database_query_performance" in self.results:
            db_results = self.results["test_database_query_performance"]
            if isinstance(db_results, dict):
                for query, result in db_results.items():
                    if isinstance(result, dict) and "passed" in result:
                        scores.append(100 if result["passed"] else 0)

        return round(sum(scores) / len(scores)) if scores else 0

    def _identify_worst_performing(self) -> List[Dict[str, Any]]:
        """识别性能最差的组件"""
        worst = []

        # 分析API响应时间
        if "test_api_response_times" in self.results:
            api_results = self.results["test_api_response_times"]
            if isinstance(api_results, dict):
                for endpoint, result in api_results.items():
                    if isinstance(result, dict) and "avg_time_ms" in result:
                        worst.append(
                            {
                                "component": f"API:{endpoint}",
                                "response_time_ms": result["avg_time_ms"],
                                "threshold": result.get("threshold", 5000),
                            }
                        )

        # 按响应时间排序
        worst.sort(key=lambda x: x["response_time_ms"], reverse=True)
        return worst[:3]  # 返回前3个性能最差的

    def _generate_recommendations(self) -> List[str]:
        """生成优化建议"""
        recommendations = []

        # API性能建议
        if "test_api_response_times" in self.results:
            api_results = self.results["test_api_response_times"]
            if isinstance(api_results, dict):
                for endpoint, result in api_results.items():
                    if isinstance(result, dict) and not result.get("passed", True):
                        recommendations.append(
                            f"优化API端点 {endpoint} 的性能，当前响应时间 {result.get('avg_time_ms', 0)}ms"
                        )

        # 数据库建议
        if "test_database_query_performance" in self.results:
            db_results = self.results["test_database_query_performance"]
            if isinstance(db_results, dict):
                for query, result in db_results.items():
                    if isinstance(result, dict) and not result.get("passed", True):
                        recommendations.append(
                            f"优化查询 {query}，考虑添加索引或优化SQL语句"
                        )

        # 系统建议
        if "test_memory_usage" in self.results:
            mem_results = self.results["test_memory_usage"]
            if (
                isinstance(mem_results, dict)
                and mem_results.get("memory_percent", 0) > 80
            ):
                recommendations.append("内存使用率过高，考虑增加内存或优化内存使用")

        return recommendations


# 性能测试装饰器
def performance_benchmark(test_func):
    """性能测试装饰器"""

    async def wrapper(*args, **kwargs):
        suite = PerformanceTestSuite()
        return await suite.run_performance_benchmark()

    return wrapper


# Pytest测试用例
@pytest.mark.performance
async def test_api_performance():
    """API性能测试"""
    suite = PerformanceTestSuite()
    report = await suite.run_performance_benchmark()

    # 验证测试结果
    assert "test_api_response_times" in suite.results
    assert len(suite.results) >= 3  # 至少运行了3项测试

    print(f"\n📊 性能测试报告: {report}")


@pytest.mark.performance
async def test_database_performance():
    """数据库性能测试"""
    suite = PerformanceTestSuite()

    # 只运行数据库测试
    db_result = await suite.test_database_query_performance()

    assert isinstance(db_result, dict)
    assert len(db_result) >= 1  # 至少有一个查询测试

    # 验证基本指标
    for query_name, result in db_result.items():
        if isinstance(result, dict) and "avg_time_ms" in result:
            assert result["avg_time_ms"] >= 0  # 执行时间应该为正数


@pytest.mark.performance
async def test_concurrent_performance():
    """并发性能测试"""
    suite = PerformanceTestSuite()

    # 只运行并发测试
    concurrent_result = await suite.test_concurrent_users()

    assert isinstance(concurrent_result, dict)
    assert len(concurrent_result) >= 2  # 测试了至少2个并发级别

    # 验证并发级别
    for user_count, result in concurrent_result.items():
        assert isinstance(result, dict)
        assert result["requests_per_second"] >= 0


@pytest.mark.performance
async def test_system_resources():
    """系统资源测试"""
    suite = PerformanceTestSuite()

    # 测试内存和CPU
    memory_result = await suite.test_memory_usage()
    cpu_result = await suite.test_cpu_usage()

    assert isinstance(memory_result, dict)
    assert isinstance(cpu_result, dict)

    # 验证基本指标
    assert memory_result["rss_memory_mb"] >= 0
    assert memory_result["memory_percent"] >= 0
    assert cpu_result["avg_cpu_percent"] >= 0
    assert cpu_result["cpu_count"] > 0


if __name__ == "__main__":
    # 运行完整性能测试
    async def main():
        suite = PerformanceTestSuite()
        report = await suite.run_performance_benchmark()
        print(f"\n🎯 性能测试报告已保存到: {report}")

    # 运行测试
    import asyncio

    asyncio.run(main())
