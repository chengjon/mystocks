#!/bin/bash
# 日志轮转脚本 - 将旧日志移动到归档

LOG_DIR="/opt/claude/mystocks_spec/logs/app"
OLD_DIR="${LOG_DIR}/old"
ARCHIVE_DIR="/opt/claude/mystocks_spec/logs/archive"

echo "开始日志轮转..."
echo "日志目录: $LOG_DIR"
echo ""

mkdir -p "$OLD_DIR"
mkdir -p "$ARCHIVE_DIR"

# 移动超过7天的日志到old目录
find "$LOG_DIR" -maxdepth 1 -name "*.log" -type f -mtime +7 -print0 | while IFS= read -r -d '' logfile; do
    if [ -f "$logfile" ]; then
        echo "归档: $(basename "$logfile")"
        mv "$logfile" "$OLD_DIR/"
    fi
done

echo ""
echo "日志轮转完成"
echo "当前日志文件数: $(find "$LOG_DIR" -maxdepth 1 -name "*.log" -type f | wc -l)"
echo "归档日志文件数: $(find "$OLD_DIR" -maxdepth 1 -name "*.log" -type f | wc -l)"
