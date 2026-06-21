#!/usr/bin/env python3
"""
API Performance Benchmark Tool
Establishes performance baselines and identifies slow endpoints
"""

import asyncio
import json
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp


@dataclass
class BenchmarkResult:
    """Benchmark result for a single endpoint"""

    endpoint: str
    method: str
    workload_class: str = "business"
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

    def __init__(
        self,
        base_url: str,
        concurrent_users: int = 10,
        iterations: int = 100,
        default_headers: Optional[Dict[str, str]] = None,
        warmup_requests: int = 0,
    ):
        self.base_url = base_url.rstrip("/")
        self.concurrent_users = concurrent_users
        self.iterations = iterations
        self.default_headers = default_headers or {}
        self.warmup_requests = max(warmup_requests, 0)
        self.results: Dict[str, BenchmarkResult] = {}
        self.slow_threshold_ms = 300
        self.critical_threshold_ms = 500

    async def warmup_endpoint(
        self,
        session: aiohttp.ClientSession,
        endpoint: str,
        method: str = "GET",
        payload: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """Run non-measured warmup traffic for an endpoint."""
        for _ in range(self.warmup_requests):
            await self.benchmark_endpoint(session, endpoint, method, payload, headers)

    @staticmethod
    def _build_summary(results: List[BenchmarkResult]) -> Dict[str, Any]:
        if not results:
            return {
                "endpoint_count": 0,
                "overall_avg_ms": 0,
                "overall_p95_ms": 0,
            }

        return {
            "endpoint_count": len(results),
            "overall_avg_ms": round(statistics.mean(r.avg_response_time for r in results) * 1000, 2),
            "overall_p95_ms": round(statistics.mean(r.p95_response_time for r in results) * 1000, 2),
        }

    async def benchmark_endpoint(
        self,
        session: aiohttp.ClientSession,
        endpoint: str,
        method: str = "GET",
        payload: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> tuple[int, float]:
        """Benchmark a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.perf_counter()
        merged_headers = {**self.default_headers, **(headers or {})}

        try:
            if method == "GET":
                async with session.get(url, headers=merged_headers) as response:
                    await response.read()
                    status = response.status
            elif method == "POST":
                async with session.post(url, json=payload, headers=merged_headers) as response:
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
                headers = endpoint_config.get("headers")
                workload_class = str(endpoint_config.get("workload_class", "business")).strip() or "business"

                print(f"Benchmarking: {method} {endpoint}")

                result = BenchmarkResult(endpoint=endpoint, method=method, workload_class=workload_class)

                if self.warmup_requests:
                    print(f"  Warmup: {self.warmup_requests} request(s) excluded from metrics")
                    await self.warmup_endpoint(session, endpoint, method, payload, headers)

                semaphore = asyncio.Semaphore(max(self.concurrent_users, 1))

                async def run_once() -> tuple[int, float]:
                    async with semaphore:
                        return await self.benchmark_endpoint(session, endpoint, method, payload, headers)

                tasks = [run_once() for _ in range(self.iterations)]

                for outcome in await asyncio.gather(*tasks, return_exceptions=True):
                    result.total_requests += 1

                    if isinstance(outcome, Exception):
                        result.failed_requests += 1
                        continue

                    response_status, duration = outcome
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

    def generate_json_report(self) -> Dict[str, Any]:
        """Generate a machine-readable benchmark report."""
        endpoint_reports = []
        for result in sorted(self.results.values(), key=lambda item: item.p95_response_time, reverse=True):
            endpoint_reports.append(
                {
                    "endpoint": result.endpoint,
                    "method": result.method,
                    "workload_class": result.workload_class,
                    "total_requests": result.total_requests,
                    "successful_requests": result.successful_requests,
                    "failed_requests": result.failed_requests,
                    "avg_ms": round(result.avg_response_time * 1000, 2),
                    "median_ms": round(result.median_response_time * 1000, 2),
                    "p95_ms": round(result.p95_response_time * 1000, 2),
                    "p99_ms": round(result.p99_response_time * 1000, 2),
                    "min_ms": round(result.min_response_time * 1000, 2),
                    "max_ms": round(result.max_response_time * 1000, 2),
                    "requests_per_second": round(result.requests_per_second, 2),
                    "error_rate_percent": round(result.error_rate, 2),
                    "status_codes": result.status_codes,
                }
            )

        all_results = list(self.results.values())
        business_results = [result for result in all_results if result.workload_class == "business"]
        infrastructure_results = [result for result in all_results if result.workload_class == "infrastructure"]

        return {
            "generated_at": datetime.now().isoformat(),
            "base_url": self.base_url,
            "concurrent_users": self.concurrent_users,
            "iterations": self.iterations,
            "slo_status": self.get_slo_status(),
            "summary": self._build_summary(all_results),
            "workload_classes": {
                "business": self._build_summary(business_results),
                "infrastructure": self._build_summary(infrastructure_results),
            },
            "endpoints": endpoint_reports,
        }

    def save_report(self, filepath: str = "performance-benchmark-report.txt"):
        """Save report to file"""
        report = self.generate_report()
        with open(filepath, "w") as f:
            f.write(report)
        print(f"\nReport saved to: {filepath}")
        return report

    def save_json_report(self, filepath: str) -> Dict[str, Any]:
        """Save a JSON benchmark report."""
        report = self.generate_json_report()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"JSON report saved to: {filepath}")
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
            violating_latency = [
                f"{r.method} {r.endpoint} P95={r.p95_response_time * 1000:.1f}ms"
                for r in self.results.values()
                if r.p95_response_time * 1000 > slo_targets["p95_latency_ms"]
            ]
            violating_errors = [
                f"{r.method} {r.endpoint} error_rate={r.error_rate:.2f}%"
                for r in self.results.values()
                if r.error_rate > slo_targets["error_rate_percent"]
            ]

            if avg_p95 > slo_targets["p95_latency_ms"]:
                status["compliant"] = False
                status["violations"].append(
                    f"P95 latency ({avg_p95:.1f}ms) exceeds target ({slo_targets['p95_latency_ms']}ms)"
                )
            if violating_latency:
                status["compliant"] = False
                status["violations"].append(
                    "Endpoints exceeding P95 target: " + "; ".join(violating_latency)
                )

            if avg_error > slo_targets["error_rate_percent"]:
                status["compliant"] = False
                status["violations"].append(
                    f"Error rate ({avg_error:.2f}%) exceeds target ({slo_targets['error_rate_percent']}%)"
                )
            if violating_errors:
                status["compliant"] = False
                status["violations"].append(
                    "Endpoints exceeding error-rate target: " + "; ".join(violating_errors)
                )

        return status


def load_endpoints(default_base_url: str, endpoints_file: Optional[str]) -> List[Dict[str, Any]]:
    """Load endpoint configs from a JSON file or use the default benchmark set."""
    if not endpoints_file:
        return [
            {"endpoint": "/health", "method": "GET", "workload_class": "infrastructure"},
            {"endpoint": "/api/health/ready", "method": "GET", "workload_class": "infrastructure"},
            {"endpoint": "/api/csrf-token", "method": "GET", "workload_class": "infrastructure"},
            {"endpoint": "/api/socketio-status", "method": "GET", "workload_class": "infrastructure"},
            {"endpoint": "/api/v1/market/quotes", "method": "GET", "workload_class": "business"},
            {"endpoint": "/api/v2/market/lhb?limit=20", "method": "GET", "workload_class": "business"},
            {"endpoint": "/api/v1/strategy/strategies", "method": "GET", "workload_class": "business"},
            {"endpoint": "/metrics", "method": "GET", "workload_class": "infrastructure"},
        ]

    path = Path(endpoints_file)
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, list):
        raise ValueError(f"Expected a list of endpoint configs in {path}")
    return loaded


def load_headers(headers_file: Optional[str]) -> Dict[str, str]:
    """Load default request headers from a JSON file."""
    if not headers_file:
        return {}

    path = Path(headers_file)
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected an object of headers in {path}")
    return {str(key): str(value) for key, value in loaded.items()}


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="API Performance Benchmark")
    parser.add_argument("--url", default="http://localhost:8020", help="Base URL")
    parser.add_argument("--users", type=int, default=10, help="Concurrent users")
    parser.add_argument("--iterations", type=int, default=100, help="Iterations per endpoint")
    parser.add_argument("--output", default="performance-benchmark-report.txt", help="Output file")
    parser.add_argument("--json-output", default="", help="Optional JSON output file")
    parser.add_argument("--endpoints-file", default="", help="JSON file containing endpoint configs")
    parser.add_argument("--headers-file", default="", help="JSON file containing default request headers")
    parser.add_argument("--warmup-requests", type=int, default=0, help="Warmup requests per endpoint excluded from metrics")
    parser.add_argument("--fail-on-slo", action="store_true", help="Exit non-zero when the SLO check fails")

    args = parser.parse_args()

    endpoints = load_endpoints(args.url, args.endpoints_file or None)

    benchmark = PerformanceBenchmark(
        base_url=args.url,
        concurrent_users=args.users,
        iterations=args.iterations,
        default_headers=load_headers(args.headers_file or None),
        warmup_requests=args.warmup_requests,
    )

    await benchmark.run_benchmark(endpoints)
    benchmark.save_report(args.output)
    if args.json_output:
        benchmark.save_json_report(args.json_output)

    slo_status = benchmark.get_slo_status()
    print(f"\nSLO Status: {'COMPLIANT' if slo_status['compliant'] else 'NON-COMPLIANT'}")
    if slo_status["violations"]:
        for v in slo_status["violations"]:
            print(f"  - {v}")
    if args.fail_on_slo and not slo_status["compliant"]:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
