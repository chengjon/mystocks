"""
连接池压力测试 - Phase 3 Task 19
验证PostgreSQL和TDengine连接池在1000并发场景下的性能和稳定性

运行方式:
    python tests/stress_test_connection_pools.py
"""

import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import structlog

from app.core.database import get_postgresql_engine
from app.core.tdengine_manager import get_tdengine_manager

logger = structlog.get_logger()


class StressTestResults:
    """压力测试结果统计"""

    def __init__(self, test_name: str):
        self.test_name = test_name
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.response_times: List[float] = []
        self.errors: List[str] = []
        self.start_time = None
        self.end_time = None

    def add_success(self, response_time: float):
        """记录成功请求"""
        self.successful_requests += 1
        self.response_times.append(response_time)

    def add_failure(self, error: str):
        """记录失败请求"""
        self.failed_requests += 1
        self.errors.append(error)

    def get_summary(self) -> Dict[str, Any]:
        """获取测试摘要"""
        duration = self.end_time - self.start_time if self.end_time else 0

        summary = {
            "test_name": self.test_name,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": round(
                (
                    (self.successful_requests / self.total_requests * 100)
                    if self.total_requests > 0
                    else 0
                ),
                2,
            ),
            "total_duration_seconds": round(duration, 2),
            "requests_per_second": round(
                self.total_requests / duration if duration > 0 else 0, 2
            ),
        }

        if self.response_times:
            summary.update(
                {
                    "min_response_time_ms": round(min(self.response_times) * 1000, 2),
                    "max_response_time_ms": round(max(self.response_times) * 1000, 2),
                    "avg_response_time_ms": round(
                        statistics.mean(self.response_times) * 1000, 2
                    ),
                    "median_response_time_ms": round(
                        statistics.median(self.response_times) * 1000, 2
                    ),
                    "p95_response_time_ms": (
                        round(
                            statistics.quantiles(self.response_times, n=20)[18] * 1000,
                            2,
                        )
                        if len(self.response_times) >= 20
                        else 0
                    ),
                    "p99_response_time_ms": (
                        round(
                            statistics.quantiles(self.response_times, n=100)[98] * 1000,
                            2,
                        )
                        if len(self.response_times) >= 100
                        else 0
                    ),
                }
            )

        if self.errors:
            # 统计错误类型
            error_counts = {}
            for error in self.errors[:10]:  # 只显示前10个错误
                error_counts[error] = error_counts.get(error, 0) + 1
            summary["top_errors"] = error_counts

        return summary

    def print_summary(self):
        """打印测试摘要"""
        summary = self.get_summary()

        print(f"\n{'=' * 80}")
        print(f"压力测试结果: {summary['test_name']}")
        print(f"{'=' * 80}")
        print(f"总请求数: {summary['total_requests']}")
        print(
            f"成功请求: {summary['successful_requests']} ({summary['success_rate']}%)"
        )
        print(f"失败请求: {summary['failed_requests']}")
        print(f"总耗时: {summary['total_duration_seconds']} 秒")
        print(f"QPS (请求/秒): {summary['requests_per_second']}")

        if "min_response_time_ms" in summary:
            print(f"\n响应时间统计 (毫秒):")
            print(f"  最小: {summary['min_response_time_ms']}")
            print(f"  平均: {summary['avg_response_time_ms']}")
            print(f"  中位数: {summary['median_response_time_ms']}")
            print(f"  最大: {summary['max_response_time_ms']}")
            if summary.get("p95_response_time_ms"):
                print(f"  P95: {summary['p95_response_time_ms']}")
            if summary.get("p99_response_time_ms"):
                print(f"  P99: {summary['p99_response_time_ms']}")

        if "top_errors" in summary and summary["top_errors"]:
            print(f"\n错误统计 (前10个):")
            for error, count in summary["top_errors"].items():
                print(f"  {error}: {count} 次")

        print(f"{'=' * 80}\n")


def postgresql_connection_test():
    """PostgreSQL单次连接测试"""
    start_time = time.time()
    try:
        engine = get_postgresql_engine()
        with engine.connect() as conn:
            # 执行简单查询
            result = conn.execute(
                "SELECT 1 as test"
            )  # Changed from text() to direct string
            result.fetchone()
        response_time = time.time() - start_time
        return True, response_time, None
    except Exception as e:
        response_time = time.time() - start_time
        return False, response_time, str(e)


def tdengine_connection_test():
    """TDengine单次连接测试"""
    start_time = time.time()
    try:
        tdengine_mgr = get_tdengine_manager()
        # 执行健康检查
        if tdengine_mgr.health_check():
            response_time = time.time() - start_time
            return True, response_time, None
        else:
            response_time = time.time() - start_time
            return False, response_time, "Health check failed"
    except Exception as e:
        response_time = time.time() - start_time
        return False, response_time, str(e)


def run_concurrent_test(
    test_func, num_requests: int, max_workers: int, test_name: str
) -> StressTestResults:
    """
    运行并发测试

    Args:
        test_func: 测试函数
        num_requests: 请求总数
        max_workers: 最大并发线程数
        test_name: 测试名称

    Returns:
        StressTestResults: 测试结果
    """
    results = StressTestResults(test_name)
    results.total_requests = num_requests
    results.start_time = time.time()

    print(f"\n开始测试: {test_name}")
    print(f"总请求数: {num_requests}, 并发线程: {max_workers}")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        futures = [executor.submit(test_func) for _ in range(num_requests)]

        # 收集结果
        completed = 0
        for future in as_completed(futures):
            completed += 1
            if completed % 100 == 0:
                print(
                    f"  进度: {completed}/{num_requests} ({completed/num_requests*100:.1f}%)"
                )

            try:
                success, response_time, error = future.result()
                if success:
                    results.add_success(response_time)
                else:
                    results.add_failure(error or "Unknown error")
            except Exception as e:
                results.add_failure(f"Future exception: {str(e)}")

    results.end_time = time.time()
    return results


def test_postgresql_stress(num_requests: int = 1000, max_workers: int = 100):
    """
    PostgreSQL压力测试

    Args:
        num_requests: 总请求数
        max_workers: 最大并发线程数
    """
    return run_concurrent_test(
        postgresql_connection_test,
        num_requests,
        max_workers,
        f"PostgreSQL压力测试 ({num_requests}请求, {max_workers}并发)",
    )


def test_tdengine_stress(num_requests: int = 1000, max_workers: int = 100):
    """
    TDengine压力测试

    Args:
        num_requests: 总请求数
        max_workers: 最大并发线程数
    """
    return run_concurrent_test(
        tdengine_connection_test,
        num_requests,
        max_workers,
        f"TDengine压力测试 ({num_requests}请求, {max_workers}并发)",
    )


def test_mixed_workload(num_requests: int = 1000, max_workers: int = 100):
    """
    混合负载测试（PostgreSQL + TDengine）

    Args:
        num_requests: 总请求数
        max_workers: 最大并发线程数
    """

    def mixed_test():
        # 50%概率选择PostgreSQL，50%选择TDengine
        if threading.current_thread().ident % 2 == 0:
            return postgresql_connection_test()
        else:
            return tdengine_connection_test()

    return run_concurrent_test(
        mixed_test,
        num_requests,
        max_workers,
        f"混合负载测试 ({num_requests}请求, {max_workers}并发)",
    )


def main():
    """主测试函数"""
    print("=" * 80)
    print("Phase 3 Task 19: 连接池压力测试")
    print("=" * 80)

    # 测试场景1: PostgreSQL - 1000请求, 100并发
    print("\n场景1: PostgreSQL压力测试")
    pg_results_1 = test_postgresql_stress(num_requests=1000, max_workers=100)
    pg_results_1.print_summary()

    # 测试场景2: PostgreSQL - 2000请求, 200并发
    print("\n场景2: PostgreSQL高并发测试")
    pg_results_2 = test_postgresql_stress(num_requests=2000, max_workers=200)
    pg_results_2.print_summary()

    # 测试场景3: TDengine - 1000请求, 100并发
    print("\n场景3: TDengine压力测试")
    td_results_1 = test_tdengine_stress(num_requests=1000, max_workers=100)
    td_results_1.print_summary()

    # 测试场景4: 混合负载 - 1000请求, 100并发
    print("\n场景4: 混合负载测试")
    mixed_results = test_mixed_workload(num_requests=1000, max_workers=100)
    mixed_results.print_summary()

    # 获取连接池统计
    print("\n" + "=" * 80)
    print("连接池最终统计")
    print("=" * 80)

    try:
        # PostgreSQL统计
        pg_engine = get_postgresql_engine()
        pool = pg_engine.pool
        print(f"\nPostgreSQL连接池:")
        print(f"  Pool Size: {pool.size()}")
        print(f"  Active Connections: {pool.checkedout()}")
        print(f"  Idle Connections: {pool.checkedin()}")
        print(f"  Overflow: {pool.overflow()}")
    except Exception as e:
        print(f"  无法获取PostgreSQL统计: {e}")

    try:
        # TDengine统计
        tdengine_mgr = get_tdengine_manager()
        td_stats = tdengine_mgr.get_pool_stats()
        if td_stats:
            print(f"\nTDengine连接池:")
            print(f"  Pool Size: {td_stats.get('pool_size', 0)}")
            print(f"  Active Connections: {td_stats.get('active_connections', 0)}")
            print(f"  Idle Connections: {td_stats.get('idle_connections', 0)}")
            print(f"  Total Created: {td_stats.get('total_created', 0)}")
            print(f"  Total Closed: {td_stats.get('total_closed', 0)}")
            print(f"  Connection Requests: {td_stats.get('connection_requests', 0)}")
            print(f"  Connection Timeouts: {td_stats.get('connection_timeouts', 0)}")
            print(f"  Connection Errors: {td_stats.get('connection_errors', 0)}")
    except Exception as e:
        print(f"  无法获取TDengine统计: {e}")

    print("\n" + "=" * 80)
    print("压力测试完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
