#!/bin/bash

set -euo pipefail

if [ -f ".env" ]; then
    set -a
    # shellcheck disable=SC1091
    source ".env"
    set +a
fi

# 0. 清理残留进程
pm2 delete all > /dev/null 2>&1 || true

# 端口配置（由 .env 提供，不允许硬编码默认端口）
: "${BACKEND_PORT:?Missing BACKEND_PORT in .env}"
: "${FRONTEND_PORT:?Missing FRONTEND_PORT in .env}"
: "${FRONTEND_BACKUP_PORT:?Missing FRONTEND_BACKUP_PORT in .env}"

TARGET_BACKEND_PORT="${BACKEND_PORT}"
TARGET_FRONTEND_PORT="${FRONTEND_PORT}"
TARGET_FRONTEND_BACKUP_PORT="${FRONTEND_BACKUP_PORT}"

# 1. 启动服务
echo "--- Starting Services ---"
pm2 start ecosystem.test.config.js

# 2. 探测后端
MAX_RETRIES=20
for i in $(seq 1 $MAX_RETRIES); do
    if curl --noproxy '*' -s "http://localhost:${TARGET_BACKEND_PORT}/health" > /dev/null; then
        echo "Backend is READY"
        break
    fi
    sleep 2
done

# 3. 探测前端
FOUND_PORT=""
for i in $(seq 1 $MAX_RETRIES); do
    for port in "$TARGET_FRONTEND_PORT" "$TARGET_FRONTEND_BACKUP_PORT"; do
        if curl --noproxy '*' -s -f "http://localhost:${port}" > /dev/null; then
            FOUND_PORT=$port
            echo "Frontend FOUND on $FOUND_PORT"
            break 2
        fi
    done
    sleep 2
done

if [ -z "$FOUND_PORT" ]; then
    echo "Frontend Timeout"
    pm2 delete all
    exit 1
fi

# 暖机 (减少到 15s，因为后端已经稳定)
echo "Warming up for 15s..."
sleep 15

# 4. 运行测试
echo "--- Running Tests on http://localhost:$FOUND_PORT ---"
export BASE_URL="http://localhost:$FOUND_PORT"
PLAYWRIGHT_BIN="./node_modules/.bin/playwright"
PLAYWRIGHT_NODE_PATH="$(pwd)/node_modules"
PLAYWRIGHT_OUTPUT_DIR="/tmp/mystocks-playwright-results"

if [ ! -x "$PLAYWRIGHT_BIN" ]; then
    echo "Playwright binary missing: $PLAYWRIGHT_BIN"
    pm2 delete all || true
    exit 1
fi

if NODE_PATH="$PLAYWRIGHT_NODE_PATH" "$PLAYWRIGHT_BIN" test tests/navigation-consistency.spec.ts --config=playwright.config.ts --project=chromium --output="$PLAYWRIGHT_OUTPUT_DIR"; then
    TEST_EXIT_CODE=0
else
    TEST_EXIT_CODE=$?
fi

# 5. 清理
pm2 delete all || true
exit $TEST_EXIT_CODE
