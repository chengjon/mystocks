#!/usr/bin/env python3
"""
mystocks_spec 冒烟测试
验证 服务进程 / 登录 / 后端API(15个) / 前端页面(5个)
用例数: 23
运行: python3 smoke_test.py
"""

import subprocess, json, sys, time
from datetime import datetime

PASS = 0
FAIL = 0
REPORT = []

def check(label, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        REPORT.append(f"  ✅ {label}")
    else:
        FAIL += 1
        REPORT.append(f"  ❌ {label}: {detail}")

def api_test(label, method, url, headers=None, data=None, timeout=20):
    cmd = ['curl', '-sS', '-o', '/dev/null', '-w', '%{http_code}']
    if method == 'POST' and data:
        cmd += ['-d', data]
    if headers:
        for k, v in headers.items():
            cmd += ['-H', f'{k}: {v}']
    cmd += [url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip() == '200'

def main():
    global PASS, FAIL
    print("=" * 55)
    print(f"  mystocks_spec 冒烟测试 — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)

    # ── 1. 服务进程 ──
    r = subprocess.run(['pm2', 'list'], capture_output=True, text=True, timeout=10)
    check("Backend online", "mystocks-backend" in r.stdout and "online" in r.stdout)
    check("Frontend online", "mystocks-frontend" in r.stdout and "online" in r.stdout)

    # ── 2. 登录 ──
    r = subprocess.run(['curl', '-sS', '-X', 'POST', 'http://localhost:8020/api/v1/auth/login',
        '-d', 'username=admin&password=admin123'], capture_output=True, text=True, timeout=10)
    try:
        d = json.loads(r.stdout)
        token = d['data']['token']
        check("Auth login", bool(token))
    except Exception as e:
        check("Auth login", False, str(e))
        print("\n❌ 登录失败，终止测试")
        sys.exit(1)

    headers = {'Authorization': f'Bearer {token}'}
    BACKEND = 'http://localhost:8020'
    FRONTEND = 'http://localhost:3020'

    # ── 3. 后端 API (15个) ──
    apis = [
        ("Dashboard概览", f"{BACKEND}/api/dashboard/market-overview?limit=3"),
        ("实时行情",     f"{BACKEND}/api/v1/market/quotes?limit=3"),
        ("K线",          f"{BACKEND}/api/v1/market/kline?symbol=000001&interval=1d&limit=3"),
        ("龙虎榜",       f"{BACKEND}/api/v1/market/lhb?limit=3"),
        ("板块动向",     f"{BACKEND}/api/v2/market/sector/fund-flow?sector_type=%E8%A1%8C%E4%B8%9A"),
        ("概念动向",     f"{BACKEND}/api/v2/market/sector/fund-flow?sector_type=%E6%A6%82%E5%BF%B5"),
        ("资金流向",     f"{BACKEND}/api/akshare/market/fund-flow/hsgt-summary?start_date=2026-07-12&end_date=2026-07-12"),
        ("自选组合",     f"{BACKEND}/api/v1/monitoring/watchlists"),
        ("股票列表",     f"{BACKEND}/api/v1/data/stocks/basic?limit=3"),
        ("策略列表",     f"{BACKEND}/api/v1/strategy/strategies"),
        ("交易信号",     f"{BACKEND}/api/v1/trade/signals"),
        ("头寸",         f"{BACKEND}/api/v1/trade/positions"),
        ("健康检查",     f"{BACKEND}/api/health/ready"),
        ("股票详情",     f"{BACKEND}/api/v1/data/stocks/000001/detail"),
        ("技术指标",     f"{BACKEND}/api/v1/technical/000001/indicators"),
    ]

    for label, url in apis:
        ok = api_test(label, 'GET', url, headers=headers)
        check(f"API {label}", ok)

    # ── 4. 前端页面 (5个) ──
    pages = [
        ("首页",       f"{FRONTEND}/"),
        ("Dashboard",  f"{FRONTEND}/dashboard"),
        ("实时行情",    f"{FRONTEND}/market/realtime"),
        ("股票列表",    f"{FRONTEND}/stock"),
        ("股票详情",    f"{FRONTEND}/stock-detail/000001"),
    ]
    for name, url in pages:
        r = subprocess.run(['curl', '-sS', '-o', '/dev/null', '-w', '%{http_code}', url], capture_output=True, text=True, timeout=10)
        check(f"前端 {name}", r.stdout.strip() == '200')

    # ── 5. 报告 ──
    print(f"\n{'=' * 55}")
    for line in REPORT:
        print(line)
    print(f"\n{'=' * 55}")
    print(f"  通过: {PASS}/{PASS+FAIL}")
    print(f"  状态: {'✅ 冒烟通过' if FAIL == 0 else '❌ 冒烟失败'}")
    print(f"{'=' * 55}")
    return 0 if FAIL == 0 else 1

if __name__ == '__main__':
    sys.exit(main())