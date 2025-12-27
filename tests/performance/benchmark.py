#!/usr/bin/env python3
"""
API Performance Benchmark Tool
Establishes performance baselines and identifies slow endpoints
"""

import asyncio
import aiohttp
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class BenchmarkResult:
    """Benchmark result for a single endpoint"""

    endpoint: str
    method: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: List[float] = field(default_factory=list)
    status_codes: Dict[int, int] = field(default_factory=dict)

    @property
    def avg_response_time(self) -> float:
        return statistics.mean(self.response_times) if self.response_times else 0

    @property
    def median_response_time(self) -> float:
        return statistics.median(self.response_times) if self.response_times else 0

    @property
    def p95_response_time(self) -> float:
        if len(self.response_times) < 2:
            return 0
        sorted_times = sorted(self.response_times)
        idx = int(len(sorted_times) * 0.95)
        return sorted_times[min(idx, len(sorted_times) - 1)]

    @property
    def p99_response_time(self) -> float:
        if len(self.response_times) < 2:
            return 0
        sorted_times = sorted(self.response_times)
        idx = int(len(sorted_times) * 0.99)
        return sorted_times[min(idx, len(sorted_times) - 1)]

    @property
    def min_response_time(self) -> float:
        return min(self.response_times) if self.response_times else 0

    @property
    def max_response_time(self) -> float:
        return max(self.response_times) if self.response_times else 0

    @property
    def requests_per_second(self) -> float:
        return self.successful_requests / sum(self.response_times) if self.response_times else 0

    @property
    def error_rate(self) -> float:
        return self.failed_requests / self.total_requests * 100 if self.total_requests > 0 else 0


class PerformanceBenchmark:
    """API Performance Benchmark Tool"""

    def __init__(self, base_url: str, concurrent_users: int = 10, iterations: int = 100):
        self.base_url = base_url.rstrip("/")
        self.concurrent_users = concurrent_users
        self.iterations = iterations
        self.results: Dict[str, BenchmarkResult] = {}
        self.slow_threshold_ms = 300
        self.critical_threshold_ms = 500

    async def benchmark_endpoint(
        self,
        session: aiohttp.ClientSession,
        endpoint: str,
        method: str = "GET",
        payload: Optional[Dict] = None,
    ) -> float:
        """Benchmark a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.perf_counter()

        try:
            if method == "GET":
                async with session.get(url) as response:
                    await response.read()
                    status = response.status
            elif method == "POST":
                async with session.post(url, json=payload) as response:
                    await response.read()
                    status = response.status
            else:
                raise ValueError(f"Unsupported method: {method}")

            duration = time.perf_counter() - start_time
            return status, duration

        except Exception:
            duration = time.perf_counter() - start_time
            return 500, duration

    async def run_benchmark(
        self,
        endpoints: List[Dict[str, Any]],
    ) -> Dict[str, BenchmarkResult]:
        """Run performance benchmark"""
        print(f"\n{'='*60}")
        print("Performance Benchmark Started")
        print(f"Base URL: {self.base_url}")
        print(f"Concurrent Users: {self.concurrent_users}")
        print(f"Iterations per endpoint: {self.iterations}")
        print(f"{'='*60}\n")

        async with aiohttp.ClientSession() as session:
            for endpoint_config in endpoints:
                endpoint = endpoint_config["endpoint"]
                method = endpoint_config.get("method", "GET")
                payload = endpoint_config.get("payload")

                print(f"Benchmarking: {method} {endpoint}")

                result = BenchmarkResult(endpoint=endpoint, method=method)

                tasks = []
                for _ in range(self.iterations):
                    tasks.append(self.benchmark_endpoint(session, endpoint, method, payload))

                for status, duration in await asyncio.gather(*tasks, return_exceptions=True):
                    if isinstance(status, Exception):
                        result.failed_requests += 1
                        result.response_times.append(0)
                    else:
                        result.total_requests += 1
                        response_status, duration = status
                        result.response_times.append(duration)

                        result.status_codes[response_status] = result.status_codes.get(response_status, 0) + 1

                        if 200 <= response_status < 300:
                            result.successful_requests += 1
                        else:
                            result.failed_requests += 1

                self.results[endpoint] = result

                status_icon = "✓" if result.error_rate < 1 else "⚠"
                print(
                    f"  {status_icon} Requests: {result.total_requests}, "
                    f"Avg: {result.avg_response_time*1000:.1f}ms, "
                    f"P95: {result.p95_response_time*1000:.1f}ms, "
                    f"Error: {result.error_rate:.1f}%"
                )

        return self.results

    def generate_report(self) -> str:
        """Generate benchmark report"""
        report = []
        report.append(f"\n{'='*60}")
        report.append("Performance Benchmark Report")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"{'='*60}\n")

        sorted_results = sorted(self.results.values(), key=lambda x: x.p95_response_time, reverse=True)

        slow_endpoints = []
        critical_endpoints = []

        report.append("Endpoint Performance Summary:")
        report.append("-" * 100)
        report.append(
            f"{'Endpoint':<40} {'Method':<8} {'Avg(ms)':<12} {'P95(ms)':<12} {'P99(ms)':<12} {'RPS':<10} {'Errors':<8} {'Status'}"
        )
        report.append("-" * 100)

        for result in sorted_results:
            p95_ms = result.p95_response_time * 1000
            p99_ms = result.p99_response_time * 1000
            avg_ms = result.avg_response_time * 1000

            if p95_ms > self.critical_threshold_ms:
                status = "🔴 CRITICAL"
                critical_endpoints.append(result)
            elif p95_ms > self.slow_threshold_ms:
                status = "🟡 SLOW"
                slow_endpoints.append(result)
            else:
                status = "🟢 OK"

            report.append(
                f"{result.endpoint:<40} {result.method:<8} "
                f"{avg_ms:<12.1f} {p95_ms:<12.1f} {p99_ms:<12.1f} "
                f"{result.requests_per_second:<10.1f} {result.error_rate:<8.1f}% {status}"
            )

        report.append("-" * 100)

        if slow_endpoints:
            report.append(f"\n🟡 Slow Endpoints ({len(slow_endpoints)}):")
            for result in slow_endpoints:
                report.append(f"  - {result.method} {result.endpoint} (P95: {result.p95_response_time*1000:.1f}ms)")

        if critical_endpoints:
            report.append(f"\n🔴 Critical Endpoints ({len(critical_endpoints)}):")
            for result in critical_endpoints:
                report.append(f"  - {result.method} {result.endpoint} (P95: {result.p95_response_time*1000:.1f}ms)")

        report.append("\n" + "=" * 60)
        report.append("Recommendations:")
        report.append("=" * 60)

        if critical_endpoints:
            report.append("1. IMMEDIATE ACTION REQUIRED for critical endpoints:")
            for result in critical_endpoints:
                report.append(f"   - Optimize {result.endpoint} (current P95: {result.p95_response_time*1000:.1f}ms)")
                if result.p95_response_time > 1.0:
                    report.append("     * Consider adding caching")
                    report.append("     * Review database queries")
                if result.error_rate > 1:
                    report.append("     * Check error logs for root cause")

        if slow_endpoints:
            report.append("\n2. Performance improvements needed:")
            for result in slow_endpoints:
                report.append(f"   - {result.endpoint} (current P95: {result.p95_response_time*1000:.1f}ms)")

        overall_avg = statistics.mean(r.avg_response_time for r in self.results.values()) * 1000
        overall_p95 = statistics.mean(r.p95_response_time for r in self.results.values()) * 1000

        report.append("\nOverall Metrics:")
        report.append(f"  - Average Response Time: {overall_avg:.1f}ms")
        report.append(f"  - Average P95 Response Time: {overall_p95:.1f}ms")
        report.append(f"  - Total Endpoints Tested: {len(self.results)}")
        report.append(f"  - Endpoints Meeting SLA: {len(self.results) - len(critical_endpoints) - len(slow_endpoints)}")

        return "\n".join(report)

    def save_report(self, filepath: str = "performance-benchmark-report.txt"):
        """Save report to file"""
        report = self.generate_report()
        with open(filepath, "w") as f:
            f.write(report)
        print(f"\nReport saved to: {filepath}")
        return report

    def get_slo_status(self) -> Dict[str, Any]:
        """Check SLO compliance"""
        slo_targets = {
            "p95_latency_ms": 300,
            "error_rate_percent": 0.1,
            "availability_percent": 99.9,
        }

        status = {
            "timestamp": datetime.now().isoformat(),
            "targets": {},
            "compliant": True,
            "violations": [],
        }

        if self.results:
            avg_p95 = statistics.mean(r.p95_response_time for r in self.results.values()) * 1000
            avg_error = statistics.mean(r.error_rate for r in self.results.values())

            if avg_p95 > slo_targets["p95_latency_ms"]:
                status["compliant"] = False
                status["violations"].append(
                    f"P95 latency ({avg_p95:.1f}ms) exceeds target ({slo_targets['p95_latency_ms']}ms)"
                )

            if avg_error > slo_targets["error_rate_percent"]:
                status["compliant"] = False
                status["violations"].append(
                    f"Error rate ({avg_error:.2f}%) exceeds target ({slo_targets['error_rate_percent']}%)"
                )

        return status


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="API Performance Benchmark")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL")
    parser.add_argument("--users", type=int, default=10, help="Concurrent users")
    parser.add_argument("--iterations", type=int, default=100, help="Iterations per endpoint")
    parser.add_argument("--output", default="performance-benchmark-report.txt", help="Output file")

    args = parser.parse_args()

    endpoints = [
        {"endpoint": "/health", "method": "GET"},
        {"endpoint": "/api/v1/market/overview", "method": "GET"},
        {"endpoint": "/api/v1/stock/000001/quote", "method": "GET"},
        {"endpoint": "/api/v1/stock/000001/kline", "method": "GET", "payload": {"period": "day"}},
        {"endpoint": "/api/v1/market/fund-flow", "method": "GET"},
        {"endpoint": "/api/v1/market/dragon-tiger", "method": "GET"},
        {"endpoint": "/api/v1/portfolio", "method": "GET"},
        {"endpoint": "/api/v1/risk/positions", "method": "GET"},
    ]

    benchmark = PerformanceBenchmark(
        base_url=args.url,
        concurrent_users=args.users,
        iterations=args.iterations,
    )

    await benchmark.run_benchmark(endpoints)
    benchmark.save_report(args.output)

    slo_status = benchmark.get_slo_status()
    print(f"\nSLO Status: {'COMPLIANT' if slo_status['compliant'] else 'NON-COMPLIANT'}")
    if slo_status["violations"]:
        for v in slo_status["violations"]:
            print(f"  - {v}")


if __name__ == "__main__":
    asyncio.run(main())
