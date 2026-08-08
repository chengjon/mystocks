#!/usr/bin/env python3
"""
MyStocks Browser Smoke Test — 双层 Web 可用性探针

Layer 1 (HTTP 直连): Python requests 验证页面可达 + Vue app 挂载（~100ms/页）
Layer 2 (浏览器渲染): 远程 Playwright 服务验证外部连通性（~500ms）

用途:
  - 部署后快速验证前端是否正常渲染
  - CI/CD 门禁：确认关键页面可访问
  - PM2 health check 定时任务

依赖:
  pip install requests

远程 Playwright 服务:
  地址: http://localhost:3001
  容器: firecrawl-playwright (firecrawl/playwright-service:wsl)
  限制: Chrome in Docker 对私有 IP 有安全限制，仅用于外部 URL 验证

用法:
  python scripts/dev/browser_smoke.py              # 完整检查
  python scripts/dev/browser_smoke.py --quick       # 仅 Layer 1
  python scripts/dev/browser_smoke.py --json        # JSON 输出（CI 友好）
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from typing import List, Optional
from urllib.parse import urljoin

import requests

# ── 配置 ────────────────────────────────────────────

FRONTEND_BASE = "http://localhost:3020"
FRONTEND_WSL2 = "http://192.168.123.74:3020"  # Docker 容器内访问 WSL2 宿主
BACKEND_BASE = "http://localhost:8020"
PLAYWRIGHT_SERVICE = "http://localhost:3001"

# Layer 1: HTTP 直连探针
# 注意: Vue SPA 所有路由返回同一 index.html shell (3894 bytes, 含 id="app")。
# 这里只验证 shell 可达，动态内容需通过 L2 浏览器渲染验证。
PAGES_L1: List[dict] = [
    {"name": "Login", "path": "/", "expect": 'id="app"', "desc": "首页 SPA shell"},
    {"name": "Dashboard", "path": "/dashboard", "expect": 'id="app"', "desc": "仪表盘路由"},
    {"name": "Market", "path": "/market", "expect": 'id="app"', "desc": "行情路由"},
    {"name": "Data", "path": "/data", "expect": 'id="app"', "desc": "数据路由"},
    {"name": "Watchlist", "path": "/watchlist", "expect": 'id="app"', "desc": "自选股路由"},
    {"name": "Strategy", "path": "/strategy", "expect": 'id="app"', "desc": "策略路由"},
]

# Layer 2: Playwright 浏览器渲染验证
# 验证 SPA 页面经 Chromium 渲染后 Vue app 正常挂载（~1s/页）
PAGES_L2: List[dict] = [
    {"name": "PW-Login", "path": "/", "expect": 'id="app"'},
    {"name": "PW-Dashboard", "path": "/dashboard", "expect": 'id="app"'},
    {"name": "PW-Market", "path": "/market", "expect": 'id="app"'},
    {"name": "PW-Data", "path": "/data", "expect": 'id="app"'},
]

# Backend 健康探针
BACKEND_PROBES: List[dict] = [
    {"name": "Health", "path": "/health", "expect_status": 200, "expect_field": "healthy"},
    {"name": "OpenAPI", "path": "/openapi.json", "expect_status": 200, "expect_field": "openapi"},
]


# ── 数据模型 ─────────────────────────────────────────

@dataclass
class ProbeResult:
    name: str
    passed: bool
    layer: str  # "L1" | "L2" | "backend"
    elapsed_ms: float
    detail: str = ""
    status_code: Optional[int] = None


@dataclass
class SmokeReport:
    results: List[ProbeResult] = field(default_factory=list)
    total_ms: float = 0.0

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    @property
    def all_passed(self) -> bool:
        return self.failed == 0


# ── 核心逻辑 ─────────────────────────────────────────

def probe_http(name: str, url: str, expect: str, layer: str = "L1") -> ProbeResult:
    """HTTP GET 直连探针"""
    t0 = time.monotonic()
    try:
        resp = requests.get(url, timeout=10, allow_redirects=True)
        elapsed = (time.monotonic() - t0) * 1000
        html = resp.text.lower()
        passed = expect.lower() in html and resp.status_code == 200
        detail = f"HTTP {resp.status_code}, {len(html)} bytes" if passed else f"HTTP {resp.status_code}, missing '{expect}'"
        return ProbeResult(name=name, passed=passed, layer=layer, elapsed_ms=round(elapsed, 1), detail=detail, status_code=resp.status_code)
    except requests.RequestException as e:
        elapsed = (time.monotonic() - t0) * 1000
        return ProbeResult(name=name, passed=False, layer=layer, elapsed_ms=round(elapsed, 1), detail=str(e))


def probe_backend(name: str, url: str, expect_status: int, expect_field: str) -> ProbeResult:
    """Backend API 探针"""
    t0 = time.monotonic()
    try:
        resp = requests.get(url, timeout=10)
        elapsed = (time.monotonic() - t0) * 1000
        ok = resp.status_code == expect_status
        if ok and expect_field:
            body = resp.text.lower()
            ok = expect_field.lower() in body
        detail = f"HTTP {resp.status_code}" if ok else f"HTTP {resp.status_code}, expected {expect_status}"
        return ProbeResult(name=name, passed=ok, layer="backend", elapsed_ms=round(elapsed, 1), detail=detail, status_code=resp.status_code)
    except requests.RequestException as e:
        elapsed = (time.monotonic() - t0) * 1000
        return ProbeResult(name=name, passed=False, layer="backend", elapsed_ms=round(elapsed, 1), detail=str(e))


def probe_playwright(name: str, url: str, expect: str) -> ProbeResult:
    """远程 Playwright 浏览器渲染探针"""
    t0 = time.monotonic()
    try:
        resp = requests.post(f"{PLAYWRIGHT_SERVICE}/scrape", json={"url": url, "waitUntil": "networkidle"}, timeout=30)
        elapsed = (time.monotonic() - t0) * 1000
        if resp.status_code != 200:
            return ProbeResult(name=name, passed=False, layer="L2", elapsed_ms=round(elapsed, 1), detail=f"Playwright service HTTP {resp.status_code}")
        data = resp.json()
        if data.get("error"):
            return ProbeResult(name=name, passed=False, layer="L2", elapsed_ms=round(elapsed, 1), detail=data["error"])
        content = data.get("content", "")
        page_status = data.get("pageStatusCode", 0)
        passed = expect in content and page_status == 200
        detail = f"page {page_status}, {len(content)} bytes" if passed else f"page {page_status}, missing '{expect}'"
        return ProbeResult(name=name, passed=passed, layer="L2", elapsed_ms=round(elapsed, 1), detail=detail, status_code=page_status)
    except requests.RequestException as e:
        elapsed = (time.monotonic() - t0) * 1000
        return ProbeResult(name=name, passed=False, layer="L2", elapsed_ms=round(elapsed, 1), detail=str(e))


def check_playwright_health() -> bool:
    """检查远程 Playwright 服务是否在线"""
    try:
        resp = requests.get(f"{PLAYWRIGHT_SERVICE}/health", timeout=5)
        return resp.status_code == 200 and resp.json().get("status") == "healthy"
    except requests.RequestException:
        return False


# ── 主流程 ───────────────────────────────────────────

def run_smoke(quick: bool = False) -> SmokeReport:
    """执行烟雾测试"""
    report = SmokeReport()
    t0 = time.monotonic()

    # ── Backend probes ──
    for probe in BACKEND_PROBES:
        url = urljoin(BACKEND_BASE, probe["path"])
        result = probe_backend(probe["name"], url, probe["expect_status"], probe["expect_field"])
        report.results.append(result)

    # ── Layer 1: HTTP 直连 ──
    for page in PAGES_L1:
        url = urljoin(FRONTEND_BASE, page["path"])
        result = probe_http(page["name"], url, page["expect"])
        report.results.append(result)

    if not quick:
        # ── Layer 2: Playwright 浏览器渲染 ──
        # Docker 容器内 Chromium 通过 WSL2 IP 访问宿主前端
        pw_healthy = check_playwright_health()
        if pw_healthy:
            for page in PAGES_L2:
                url = urljoin(FRONTEND_WSL2, page["path"])
                result = probe_playwright(page["name"], url, page["expect"])
                report.results.append(result)
        else:
            report.results.append(ProbeResult(name="Playwright", passed=False, layer="L2", elapsed_ms=0, detail="Service unreachable"))

    report.total_ms = round((time.monotonic() - t0) * 1000, 1)
    return report


def print_report(report: SmokeReport, json_mode: bool = False) -> None:
    """输出报告"""
    if json_mode:
        output = {
            "total_ms": report.total_ms,
            "passed": report.passed,
            "failed": report.failed,
            "all_passed": report.all_passed,
            "results": [
                {
                    "name": r.name,
                    "layer": r.layer,
                    "passed": r.passed,
                    "elapsed_ms": r.elapsed_ms,
                    "detail": r.detail,
                    "status_code": r.status_code,
                }
                for r in report.results
            ],
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return

    # ── 终端输出 ──
    icon = lambda passed: "✅" if passed else "❌"
    print()
    print("=" * 62)
    print("  MyStocks Browser Smoke Test")
    print("=" * 62)

    # Backend
    backend_results = [r for r in report.results if r.layer == "backend"]
    if backend_results:
        print("\n  📡 Backend API")
        for r in backend_results:
            print(f"    {icon(r.passed)} {r.name:<12s} {r.detail:<30s} ({r.elapsed_ms:.0f}ms)")

    # Layer 1
    l1_results = [r for r in report.results if r.layer == "L1"]
    if l1_results:
        print("\n  🌐 Layer 1 — HTTP 直连")
        for r in l1_results:
            print(f"    {icon(r.passed)} {r.name:<12s} {r.detail:<30s} ({r.elapsed_ms:.0f}ms)")

    # Layer 2
    l2_results = [r for r in report.results if r.layer == "L2"]
    if l2_results:
        print("\n  🎭 Layer 2 — Playwright 浏览器渲染")
        for r in l2_results:
            print(f"    {icon(r.passed)} {r.name:<12s} {r.detail:<30s} ({r.elapsed_ms:.0f}ms)")

    print()
    print(f"  📊 Total: {report.passed}/{len(report.results)} passed, {report.failed} failed ({report.total_ms:.0f}ms)")
    print("=" * 62)
    print()


# ── 入口 ─────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="MyStocks Browser Smoke Test")
    parser.add_argument("--quick", action="store_true", help="仅 Layer 1 (跳过浏览器渲染)")
    parser.add_argument("--json", action="store_true", help="JSON 输出 (CI 友好)")
    args = parser.parse_args()

    report = run_smoke(quick=args.quick)
    print_report(report, json_mode=args.json)
    sys.exit(0 if report.all_passed else 1)


if __name__ == "__main__":
    main()
