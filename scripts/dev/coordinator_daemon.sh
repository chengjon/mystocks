#!/bin/bash
# coordinator_daemon.sh - 智能协调器守护进程

set -e

COORDINATOR_SCRIPT="scripts/dev/smart_coordinator.py"
CLIS_DIR="CLIS"
LOG_FILE="CLIS/main/coordinator.log"
PID_FILE="CLIS/main/.coordinator_pid"
INTERVAL=300  # 5分钟执行一次

echo "🤖 启动智能协调器守护进程..."
echo "扫描间隔: ${INTERVAL}秒"

# 写入PID
echo $$ > "$PID_FILE"

# 守护循环
while true; do
    echo "" >> "$LOG_FILE"
    echo "🤖 协调器执行时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"

    # 执行协调
    python "$COORDINATOR_SCRIPT" --auto --clis-dir "$CLIS_DIR" >> "$LOG_FILE" 2>&1

    echo "⏰ 下次执行: $(date -d "+${INTERVAL}seconds" '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"

    # 等待下次执行
    sleep "$INTERVAL"
done
