#!/bin/bash

# 0. 清理残留进程
pm2 delete all > /dev/null 2>&1

# 端口配置（与 .env 一致）
TARGET_BACKEND_PORT="${BACKEND_PORT:-8020}"
TARGET_FRONTEND_PORT="${FRONTEND_PORT:-3020}"
TARGET_FRONTEND_BACKUP_PORT="${FRONTEND_BACKUP_PORT:-3021}"

# 1. 启动服务
echo "--- Starting Services ---"
pm2 start ecosystem.test.config.js

# 2. 探测后端
MAX_RETRIES=20
for i in $(seq 1 $MAX_RETRIES); do
    if curl -s "http://localhost:${TARGET_BACKEND_PORT}/health" > /dev/null; then
        echo "Backend is READY"
        break
    fi
    sleep 2
done

# 3. 探测前端
FOUND_PORT=""
for i in $(seq 1 $MAX_RETRIES); do
    for port in "$TARGET_FRONTEND_PORT" "$TARGET_FRONTEND_BACKUP_PORT"; do
        if curl -s -f http://localhost:$port > /dev/null; then
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
npx playwright test tests/navigation-consistency.spec.ts --config=playwright.config.ts --project=chromium

TEST_EXIT_CODE=$?

# 5. 清理
pm2 delete all
exit $TEST_EXIT_CODE
