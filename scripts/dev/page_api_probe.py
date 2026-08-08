#!/usr/bin/env python3
"""MyStocks 全页面 API 数据探针。
读取 PAGE_ELEMENT_INDEX.md 中每个元素的 dataSource，
映射到后端 API 端点，并发探测，输出分层测试报告。
"""

import json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import requests

ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND = "http://localhost:8020"
MD_PATH = ROOT / "docs/references/PAGE_ELEMENT_INDEX.md"
REPORT_DIR = ROOT / "reports/test"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
TIMEOUT = 10
AUTH_HEADERS = {}  # populated by get_auth_token()


def get_auth_token() -> dict:
    """自动登录获取 JWT token (credentials from env, no hardcoded defaults)"""
    global AUTH_HEADERS
    if AUTH_HEADERS:
        return AUTH_HEADERS
    username = os.environ.get("MYSTOCKS_PROBE_USERNAME")
    password = os.environ.get("MYSTOCKS_PROBE_PASSWORD")
    if not username or not password:
        print("[probe] MYSTOCKS_PROBE_USERNAME / MYSTOCKS_PROBE_PASSWORD not set — skipping auth")
        return {}
    try:
        resp = requests.post(
            f"{BACKEND}/api/v1/auth/login",
            data={"username": username, "password": password},
            timeout=5,
        )
        if resp.status_code == 200:
            token = resp.json().get("data", {}).get("token", "")
            if token:
                AUTH_HEADERS = {"Authorization": f"Bearer {token}"}
                return AUTH_HEADERS
    except Exception:
        pass
    return {}


# ── 数据源模式 → API 端点映射 ──
DS_API_MAP = [
    # (regex pattern, API path, description)
    # 注：路由来自 openapi.json 实际注册端点验证
    (r"marketData\.(fundFlow|shanghai|shenzhen|chuangye|stocks|volume|northFund)", "/api/v1/market/quotes?symbol=000001", "市场行情"),
    (r"marketStatus|marketSentiment|market.*mood|marketOverview", "/api/v1/data/markets/overview", "市场状态"),
    (r"lhbData|龙虎榜|LHB", "/api/v1/market/lhb?limit=5", "龙虎榜"),
    (r"fundFlow|资金流向|flowData|capitalFlow", "/api/v1/market/fund-flow", "资金流向"),
    (r"heatmapOption|boardData|板块|sector|boards|industryData", "/api/v1/data/markets/overview", "板块/市场数据"),
    (r"conceptData|概念", "/api/v2/market/sector/fund-flow?sector_type=概念", "概念数据"),
    (r"blocktrade|大宗交易|blockTrade", "/api/v2/market/blocktrade?limit=5", "大宗交易"),
    (r"strategy|策略|strategies|activeStrategies", "/api/v1/strategy/strategies?status=active", "策略管理"),
    (r"backtest|回测|backtestData", "/api/v1/strategy/backtest/results", "回测引擎"),
    (r"gpuStatus|GPU|gpu", "/api/gpu/status", "GPU监控"),
    (r"indicatorList|指标|indicator.*registry|indicators", "/api/v1/indicators/registry", "指标注册"),
    (r"signal|信号|signals", "/api/v1/trade/signals", "交易信号"),
    (r"kline|K线|klineData|klineChart", "/api/v1/market/kline?stock_code=000001&period=daily&limit=5", "K线数据"),
    (r"position|持仓|position|仓位", "/api/v1/trade/positions", "持仓管理"),
    (r"trade|交易|trades", "/api/v1/trade/trades", "交易记录"),
    (r"risk|风险|riskMetrics|stopLoss|alerts", "/api/trading/risk/metrics", "风险管理"),
    (r"watchlist|自选|monitoring.*watchlist", "/api/v1/monitoring/watchlists", "自选管理"),
    (r"systemHealth|健康|health.*matrix|monitoring.*health", "/api/v1/system/health", "系统健康"),
    (r"stock|股票|stocks.*basic|screener", "/api/v1/data/stocks/basic", "股票基础"),
    (r"analysis|指标分析|advanced", "/api/v1/indicators/registry", "指标分析"),
    (r"announcement|公告|news", "/api/announcement/list", "公告"),
    (r"config|配置|dataSources|settings|datasource", "/api/v1/system/datasources", "系统配置"),
    (r"stressTest|压力测试", "/api/trading/risk/metrics", "压力测试"),
    (r"history|历史", "/api/v1/trade/trades", "交易历史"),
]


@dataclass
class ApiProbe:
    api: str
    description: str
    status_code: Optional[int] = None
    has_data: bool = False
    elapsed_ms: float = 0.0
    error: str = ""


@dataclass
class PageReport:
    page_id: str
    title: str
    element_count: int
    api_probes: list = field(default_factory=list)
    score: int = 100
    p0: int = 0
    p1: int = 0
    p2: int = 0
    p3: int = 0


def parse_elements() -> list[dict]:
    """解析 MD 文件提取所有页面和元素"""
    text = MD_PATH.read_text(encoding="utf-8")
    pages = []
    current_page = None
    current_title = ""
    current_rows = []
    skip_a1_detail = False

    for line in text.split("\n"):
        if line.startswith("## 二、A1"):
            skip_a1_detail = True
            continue
        if skip_a1_detail and line.startswith("## 三、B"):
            skip_a1_detail = False

        m = re.match(r"^###\s+(\w+)\s+(.+)$", line)
        if m and not skip_a1_detail:
            if current_page and current_rows:
                pages.append({"id": current_page, "title": current_title, "rows": current_rows})
            current_page = m.group(1)
            current_title = m.group(2).strip()
            current_rows = []
            continue

        if not skip_a1_detail and line.startswith("| ") and not line.startswith("| 编号"):
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 4 and re.match(r"^[A-Z]\d+-\d+$", parts[0]):
                ds = parts[3] if len(parts) > 3 else ""
                current_rows.append({"id": parts[0], "type": parts[1], "name": parts[2], "ds": ds})

    if current_page and current_rows:
        pages.append({"id": current_page, "title": current_title, "rows": current_rows})
    return pages


def match_api(ds: str) -> Optional[tuple]:
    """匹配数据源到 API 端点"""
    if not ds or ds in ("—", "静态", "子组件内部数据"):
        return None
    for pattern, api, desc in DS_API_MAP:
        if re.search(pattern, ds, re.IGNORECASE):
            return (api, desc)
    return None


def probe_api(api: str, desc: str) -> ApiProbe:
    """探测单个 API"""
    p = ApiProbe(api=api, description=desc)
    url = urljoin(BACKEND, api) if not api.startswith("http") else api
    t0 = time.monotonic()
    try:
        headers = get_auth_token()  # 带 JWT 认证
        resp = requests.get(url, timeout=TIMEOUT, headers=headers)
        p.elapsed_ms = round((time.monotonic() - t0) * 1000, 1)
        p.status_code = resp.status_code
        if resp.status_code == 200:
            body = resp.json()
            if isinstance(body, list):
                p.has_data = len(body) > 0
            elif isinstance(body, dict):
                data = body.get("data", body)
                p.has_data = bool(data) and (not isinstance(data, list) or len(data) > 0)
    except requests.RequestException as e:
        p.elapsed_ms = round((time.monotonic() - t0) * 1000, 1)
        p.error = str(e)[:80]
    return p


def classify(p: ApiProbe) -> int:
    """P0=1, P1=2, P2=3, P3=4, OK=0"""
    if p.status_code is None:
        return 1  # P0: no response
    if p.status_code >= 500:
        return 1  # P0
    if p.status_code == 404:
        return 2  # P1: endpoint missing
    if p.status_code == 401:
        return 3  # P2: needs auth (endpoint exists, skip scoring)
    if not p.has_data:
        return 2  # P1: empty data
    return 0  # OK


def main():
    pages = parse_elements()
    print(f"Parsed {len(pages)} pages")

    # 收集所有唯一 API
    seen_apis = {}
    for pg in pages:
        for r in pg["rows"]:
            m = match_api(r["ds"])
            if m:
                api, desc = m
                key = api
                if key not in seen_apis:
                    seen_apis[key] = (api, desc)

    print(f"Unique APIs to probe: {len(seen_apis)}")

    # 并发探测
    results = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(probe_api, api, desc): api for api, desc in seen_apis.values()}
        for f in as_completed(futures):
            api = futures[f]
            results[api] = f.result()

    # 按页面汇总
    page_reports = []
    global_p0 = global_p1 = global_p2 = global_p3 = 0
    total_apis_probed = 0

    for pg in pages:
        report = PageReport(page_id=pg["id"], title=pg["title"], element_count=len(pg["rows"]))
        page_apis = set()
        for r in pg["rows"]:
            m = match_api(r["ds"])
            if m:
                api = m[0]
                if api not in page_apis:
                    page_apis.add(api)
                    probe = results.get(api)
                    if probe:
                        report.api_probes.append(probe)
                        cls = classify(probe)
                        if cls == 1:
                            report.p0 += 1
                            report.score -= 10
                        elif cls == 2:
                            report.p1 += 1
                            report.score -= 5
                        elif cls == 3:
                            report.p2 += 1  # 401 auth — P2, don't deduct score
                        else:
                            total_apis_probed += 1
        report.score = max(0, report.score)
        global_p0 += report.p0
        global_p1 += report.p1
        global_p2 += report.p2
        global_p3 += report.p3
        page_reports.append(report)

    # ── 终端输出 ──
    print()
    print("=" * 70)
    print("  MyStocks 全页面 API 数据探针报告")
    print("=" * 70)
    fails = [r for r in page_reports if r.score < 100]
    for r in page_reports:
        icon = "✅" if r.score == 100 else "❌" if r.score < 70 else "⚠️"
        detail = f"{len(r.api_probes)} APIs"
        flags = []
        if r.p0: flags.append(f"P0×{r.p0}")
        if r.p1: flags.append(f"P1×{r.p1}")
        if r.p2: flags.append(f"P2×{r.p2}")
        if flags:
            detail += " " + " ".join(flags)
        print(f"  {icon} {r.page_id:4s} {r.title[:16]:16s} score={r.score:>3}  {detail}")

    print()
    total_pages = len(page_reports)
    healthy = sum(1 for r in page_reports if r.score == 100)
    print(f"  总计: {total_pages} 页 | 健康: {healthy} | P0: {global_p0} | P1: {global_p1} | P2: {global_p2}")
    print("=" * 70)

    # ── JSON 报告 ──
    report_json = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_pages": total_pages,
        "healthy_pages": healthy,
        "P0": global_p0,
        "P1": global_p1,
        "P2": global_p2,
        "P3": global_p3,
        "unique_apis_probed": len(seen_apis),
        "pages": [
            {
                "id": r.page_id,
                "title": r.title,
                "score": r.score,
                "elements": r.element_count,
                "api_count": len(r.api_probes),
                "p0": r.p0,
                "p1": r.p1,
                "failing_apis": [
                    {"api": p.api, "status": p.status_code, "error": p.error}
                    for p in r.api_probes
                    if classify(p) > 0
                ],
            }
            for r in page_reports
        ],
    }
    json_path = REPORT_DIR / f"global-api-probe-{time.strftime('%Y%m%d')}.json"
    json_path.write_text(json.dumps(report_json, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nJSON report → {json_path}")

    sys.exit(0 if global_p0 == 0 else 1)


if __name__ == "__main__":
    main()
