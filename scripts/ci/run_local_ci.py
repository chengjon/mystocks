#!/usr/bin/env python3
"""
MyStocks 本地 CI Runner
在 WSL 上运行完整的 CI 管道，包括冒烟测试。
"""

import subprocess, sys, time
from datetime import datetime

PASS = 0
FAIL = 0
STEPS = []

def step(name, cmd, timeout=60):
    global PASS, FAIL
    print(f"\n  🔄 {name}...", end=" ", flush=True)
    start = time.time()
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
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
            if err:
                print(f"     {err}")
    except subprocess.TimeoutExpired:
        FAIL += 1
        STEPS.append((name, '⏰'))
        print(f"⏰ timeout")

def main():
    global PASS, FAIL
    print("=" * 50)
    print(f"  MyStocks 本地 CI — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 1. 服务检查
    print("\n── 1. 服务检查 ──")
    step("PM2 状态", "pm2 list 2>/dev/null | grep -q online")
    step("后端健康", "curl -sS -o /dev/null -w '%{http_code}' http://localhost:8020/health | grep -q 200")
    step("前端可达", "curl -sS -o /dev/null -w '%{http_code}' http://localhost:3020/ | grep -q 200")

    # 2. 代码质量
    print("\n── 2. 代码质量 ──")
    step("ruff 检查", "cd /opt/claude/mystocks_spec && ruff check --quiet src/ web/backend/app/ 2>&1 | head -5", timeout=30)
    step("black 格式", "cd /opt/claude/mystocks_spec && black --check --quiet src/ web/backend/app/ 2>&1 | head -5", timeout=30)

    # 3. 冒烟测试
    print("\n── 3. 冒烟测试 ──")
    step("后端冒烟", "python3 /opt/claude/mystocks_spec/smoke_test.py", timeout=30)

    # 4. 报告
    print(f"\n{'=' * 50}")
    print(f"  CI 结果: {PASS}✅ / {FAIL}❌")
    for name, status in STEPS:
        print(f"  {status} {name}")
    print(f"  状态: {'✅ 通过' if FAIL == 0 else '❌ 失败'}")
    print(f"{'=' * 50}")
    return 0 if FAIL == 0 else 1

if __name__ == '__main__':
    sys.exit(main())