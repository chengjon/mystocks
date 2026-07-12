#!/usr/bin/env python3
"""
MyStocks 本地 CI Runner
基于 smoke_test.py + 现有管道，叠加冒烟测试。

用法:
  python3 scripts/ci/run_local_ci.py          # 完整管道
  python3 scripts/ci/run_local_ci.py --quick  # 仅冒烟测试
"""

import subprocess, sys, os, time
from datetime import datetime

PASS = 0
FAIL = 0
STEPS = []

def run_step(name, command, timeout=60):
    global PASS, FAIL
    print(f"  🔄 {name}...", end=" ", flush=True)
    start = time.time()
    try:
        r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        elapsed = time.time() - start
        if r.returncode == 0:
            PASS += 1
            STEPS.append((name, '✅'))
            print(f"✅ ({elapsed:.1f}s)")
        else:
            FAIL += 1
            STEPS.append((name, '❌'))
            print(f"❌ ({elapsed:.1f}s)")
            err = r.stderr.strip()[:200] if r.stderr else r.stdout.strip()[:200]
            if err: print(f"     {err}")
    except subprocess.TimeoutExpired:
        FAIL += 1
        STEPS.append((name, '⏰'))
        print(f"⏰ timeout")

def main():
    global PASS, FAIL
    quick = '--quick' in sys.argv
    print("=" * 50)
    print(f"  MyStocks 本地 CI — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  {'快速模式(仅冒烟)' if quick else '完整管道'}")
    print("=" * 50)

    # 1. 服务检查
    print("\n── 1. 服务检查 ──")
    run_step("PM2 状态", "pm2 list 2>/dev/null | grep -q online")
    run_step("后端健康", "curl -sS -o /dev/null -w '%{http_code}' http://localhost:8020/health | grep -q 200")
    run_step("前端可达", "curl -sS -o /dev/null -w '%{http_code}' http://localhost:3020/ | grep -q 200")

    if not quick:
        # 2. 复用现有 CI 管道步骤
        print("\n── 2. CI 管道 (tests/ci/run_pipeline.py) ──")
        run_step("ruff lint", "cd /opt/claude/mystocks_spec && ruff check --quiet src/ web/backend/app/", 30)
        run_step("ruff format", "cd /opt/claude/mystocks_spec && ruff format --check --quiet src/ web/backend/app/", 30)
        run_step("单元测试", "cd /opt/claude/mystocks_spec && python3 -m pytest tests/unit -x --tb=short -q 2>&1 | tail -3", 60)

    # 3. 冒烟测试
    print(f"\n── 3. 冒烟测试 ──")
    run_step("冒烟测试", "cd /opt/claude/mystocks_spec && python3 smoke_test.py", 30)

    # 报告
    print(f"\n{'=' * 50}")
    print(f"  CI 结果: {PASS}✅ / {FAIL}❌")
    for name, status in STEPS:
        print(f"  {status} {name}")
    print(f"  状态: {'✅ 通过' if FAIL == 0 else '❌ 失败'}")
    print(f"  提示: 完整管道运行 python3 tests/ci/run_pipeline.py")
    print(f"{'=' * 50}")
    return 0 if FAIL == 0 else 1

if __name__ == '__main__':
    sys.exit(main())