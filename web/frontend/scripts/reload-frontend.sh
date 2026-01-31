#!/bin/bash
# PM2优雅重启脚本 - 零停机部署
# 用法: ./scripts/reload-frontend.sh

set -e

echo "🔄 优雅重启前端服务..."

# 检查PM2进程是否存在
if pm2 describe mystocks-frontend-prod >/dev/null 2>&1; then
  echo "✅ 进程存在，执行reload（零停机）"
  pm2 reload mystocks-frontend-prod
else
  echo "⚠️  进程不存在，执行start"
  pm2 start ecosystem.config.js --only mystocks-frontend
fi

echo "✅ 前端服务已更新"
pm2 logs mystocks-frontend-prod --lines 10 --nostream
