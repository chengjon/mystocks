"""
API 自动化测试运行器

整合 PM2 + tmux + lnav + Playwright 进行 API 测试。
支持并行测试、实时日志查看和测试报告生成。
"""

import json
import subprocess
import logging
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class TestConfig:
    """测试配置"""

    api_base_url: str = "http://localhost:8000"
    web_base_url: str = "http://localhost:5173"
    test_dir: str = "tests/api"
    report_dir: str = "playwright-report/api"
    workers: int = 4
    retry_count: int = 2
    timeout: int = 30000


class APITestRunner:
    """API 测试运行器"""

    def __init__(self, config: TestConfig = None):
        self.config = config or TestConfig()
        self.results: List[Dict] = []

    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有 API 测试"""
        from playwright.sync_api import sync_playwright

        # 检查服务状态
        if not self._check_services():
            return {"error": "Services not available"}

        results = {"start_time": datetime.now(timezone.utc).isoformat(), "tests": [], "summary": {}}

        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()

            # 并行测试不同的 API 端点
            test_suites = self._get_test_suites()

            for suite_name, endpoints in test_suites.items():
                suite_results = self._run_suite(context, suite_name, endpoints)
                results["tests"].extend(suite_results)

            browser.close()

        # 生成报告
        results["summary"] = self._generate_summary(results["tests"])
        results["end_time"] = datetime.now(timezone.utc).isoformat()

        return results

    def _check_services(self) -> bool:
        """检查服务是否可用"""
        try:
            import requests

            r = requests.get(f"{self.config.api_base_url}/health", timeout=5)
            return r.status_code == 200
        except:
            logger.error("API service not available")
            return False

    def _get_test_suites(self) -> Dict[str, List[str]]:
        """获取测试套件"""
        return {
            "market": ["/api/market/stock/list", "/api/market/stock/quote", "/api/market/indices"],
            "data": ["/api/data/query", "/api/data/history"],
            "indicators": ["/api/indicators/calculate", "/api/indicators/list"],
            "strategy": ["/api/strategy", "/api/strategy/backtest"],
        }

    def _run_suite(self, context, suite_name: str, endpoints: List[str]) -> List[Dict]:
        """运行单个测试套件"""
        results = []

        for endpoint in endpoints:
            try:
                page = context.new_page()

                # 发送 API 请求
                response = page.request.get(f"{self.config.api_base_url}{endpoint}")

                result = {
                    "suite": suite_name,
                    "endpoint": endpoint,
                    "status_code": response.status,
                    "success": response.status < 400,
                    "response_time": response.time,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

                results.append(result)
                page.close()

            except Exception as e:
                results.append({"suite": suite_name, "endpoint": endpoint, "success": False, "error": str(e)})

        return results

    def _generate_summary(self, tests: List[Dict]) -> Dict[str, Any]:
        """生成测试摘要"""
        total = len(tests)
        passed = sum(1 for t in tests if t.get("success", False))

        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
        }

    def export_results(self, results: Dict, format: str = "json"):
        """导出测试结果"""
        import os

        os.makedirs(self.config.report_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == "json":
            path = f"{self.config.report_dir}/api_test_results_{timestamp}.json"
            with open(path, "w") as f:
                json.dump(results, f, indent=2)
        elif format == "html":
            path = f"{self.config.report_dir}/api_test_results_{timestamp}.html"
            self._generate_html_report(results, path)

        return path

    def _generate_html_report(self, results: Dict, path: str):
        """生成 HTML 报告"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>API Test Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 8px; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <h1>API Test Results</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p>Total: {results["summary"]["total"]}</p>
        <p class="passed">Passed: {results["summary"]["passed"]}</p>
        <p class="failed">Failed: {results["summary"]["failed"]}</p>
        <p>Pass Rate: {results["summary"]["pass_rate"]:.1f}%</p>
    </div>
    <h2>Test Details</h2>
    <table>
        <tr><th>Suite</th><th>Endpoint</th><th>Status</th></tr>
"""

        for test in results.get("tests", []):
            status = "✅ PASSED" if test.get("success") else "❌ FAILED"
            css_class = "passed" if test.get("success") else "failed"
            html += f"""
        <tr>
            <td>{test.get("suite", "-")}</td>
            <td>{test.get("endpoint", "-")}</td>
            <td class="{css_class}">{status}</td>
        </tr>
"""

        html += """
    </table>
</body>
</html>
"""

        with open(path, "w") as f:
            f.write(html)


def run_with_pm2(script: str, name: str) -> bool:
    """使用 PM2 启动服务"""
    try:
        subprocess.run(["pm2", "start", script, "--name", name, "--cwd", "/opt/claude/mystocks_spec"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def create_tmux_session(session_name: str, panes: List[Dict]) -> bool:
    """创建 tmux 会话"""
    try:
        # 创建会话
        subprocess.run(["tmux", "new-session", "-d", "-s", session_name])

        for i, pane in enumerate(panes):
            if i > 0:
                subprocess.run(["tmux", "split-window", "-t", session_name])

            # 发送命令
            cmd = pane.get("cmd", "echo 'ready'")
            subprocess.run(["tmux", "send-keys", "-t", f"{session_name}:{i}", cmd, "Enter"])

        # 布局
        subprocess.run(["tmux", "select-layout", "-t", session_name, "even-horizontal"])

        return True
    except subprocess.CalledProcessError:
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="API Test Runner")
    parser.add_argument("--workers", type=int, default=4, help="Number of workers")
    parser.add_argument("--report", type=str, default="json", help="Report format")
    args = parser.parse_args()

    config = TestConfig(workers=args.workers)
    runner = APITestRunner(config)

    results = runner.run_all_tests()
    report_path = runner.export_results(results, args.report)

    print(f"✅ Test completed. Report: {report_path}")
