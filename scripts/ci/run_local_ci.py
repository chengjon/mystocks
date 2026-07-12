#!/usr/bin/env python3
"""
MyStocks 本地 CI Runner
本轮修改文件验证 + 冒烟测试。

用法:
  python3 scripts/ci/run_local_ci.py          # 本轮修改文件 + 冒烟测试
  python3 scripts/ci/run_local_ci.py --quick  # 仅服务检查 + 冒烟测试
"""

import subprocess
import sys
import time
from datetime import datetime

PASS = 0
FAIL = 0
STEPS = []
MODIFIED_FILES = [
    "smoke_test.py",
    "scripts/ci/run_local_ci.py",
    "src/adapters/akshare/misc_data/get_futures_index_daily.py",
    "src/adapters/akshare/stock_daily.py",
    "src/adapters/sina_finance_adapter.py",
    "src/data_access/postgresql_access.py",
    "web/backend/app/api/akshare_market/fund_flow.py",
    "web/backend/app/api/akshare_market/sse.py",
    "web/backend/app/api/dashboard_data_source.py",
    "web/backend/app/api/data/stocks.py",
    "web/backend/app/api/market/market_data_request.py",
    "web/backend/app/core/database.py",
    "web/backend/app/quotes_payload.py",
]


def run_step(name, command, timeout=60):
    global PASS, FAIL
    print(f"  🔄 {name}...", end=" ", flush=True)
    start = time.time()
    try:
        r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        elapsed = time.time() - start
        if r.returncode == 0:
            PASS += 1
            STEPS.append((name, "✅"))
            print(f"✅ ({elapsed:.1f}s)")
        else:
            FAIL += 1
            STEPS.append((name, "❌"))
            print(f"❌ ({elapsed:.1f}s)")
            err = r.stderr.strip()[:200] if r.stderr else r.stdout.strip()[:200]
            if err:
                print(f"     {err}")
    except subprocess.TimeoutExpired:
        FAIL += 1
        STEPS.append((name, "⏰"))
        print("⏰ timeout")


def main():
    global PASS, FAIL
    quick = "--quick" in sys.argv
    print("=" * 50)
    print(f"  MyStocks 本地 CI — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  {'快速模式(服务+冒烟)' if quick else '本轮修改文件+冒烟'}")
    print("=" * 50)

    # 1. 服务检查
    print("\n── 1. 服务检查 ──")
    run_step("PM2 状态", "pm2 list 2>/dev/null | grep -q online")
    run_step("后端健康", "curl -sS -o /dev/null -w '%{http_code}' http://localhost:8020/health | grep -q 200")
    run_step("前端可达", "curl -sS -o /dev/null -w '%{http_code}' http://localhost:3020/ | grep -q 200")

    if not quick:
        # 2. ruff 检查本轮修改的文件
        print("\n── 2. ruff 检查 (本轮修改) ──")
        for f in MODIFIED_FILES:
            run_step(f.split("/")[-1], f"cd /opt/claude/mystocks_spec && ruff check -q {f}")

        # 3. ruff format 检查本轮修改的文件
        print("\n── 3. ruff format (本轮修改) ──")
        for f in MODIFIED_FILES:
            run_step(f.split("/")[-1], f"cd /opt/claude/mystocks_spec && ruff format --check -q {f}")

    # 4. 冒烟测试
    print("\n── 4. 冒烟测试 ──")
    run_step("冒烟测试", "cd /opt/claude/mystocks_spec && python3 smoke_test.py")

    # 报告
    print(f"\n{'=' * 50}")
    print(f"  CI 结果: {PASS}✅ / {FAIL}❌")
    for name, status in STEPS:
        print(f"  {status} {name}")
    print(f"  状态: {'✅ 通过' if FAIL == 0 else '❌ 失败'}")
    print(f"{'=' * 50}")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
