#!/bin/bash
# 服务启动测试脚本
# 测试前端和后端在mock模式下能否正常启动

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔍 MyStocks服务启动测试 (Mock模式)"
echo "====================================="

# 设置环境变量为mock模式
export USE_MOCK_DATA=true
export TIMESERIES_DATA_SOURCE=mock
export RELATIONAL_DATA_SOURCE=mock
export BUSINESS_DATA_SOURCE=mock

echo "📝 环境变量设置:"
echo "  USE_MOCK_DATA: $USE_MOCK_DATA"
echo "  TIMESERIES_DATA_SOURCE: $TIMESERIES_DATA_SOURCE"
echo "  RELATIONAL_DATA_SOURCE: $RELATIONAL_DATA_SOURCE"
echo "  BUSINESS_DATA_SOURCE: $BUSINESS_DATA_SOURCE"

echo ""
echo "🚀 启动后端服务 (Mock模式)..."

# 启动后端服务在后台
cd "$PROJECT_ROOT/web/backend"
python run_server.py &
BACKEND_PID=$!

echo "✅ 后端启动命令已执行 (PID: $BACKEND_PID)"

# 等待几秒让后端启动
sleep 5

# 测试后端健康检查
echo ""
echo "🏥 测试后端健康检查..."
if curl -s --max-time 5 "http://localhost:8000/api/health" >/dev/null 2>&1; then
    echo "✅ 后端服务健康检查通过"
else
    echo "❌ 后端服务健康检查失败"
fi

echo ""
echo "🚀 启动前端服务..."

# 启动前端服务在后台
cd "$PROJECT_ROOT/web/frontend"
npm run dev -- --port 3001 &
FRONTEND_PID=$!

echo "✅ 前端启动命令已执行 (PID: $FRONTEND_PID)"

# 等待几秒让前端启动
sleep 10

# 测试前端服务
echo ""
echo "🏥 测试前端服务..."
if curl -s --max-time 5 "http://localhost:3001" >/dev/null 2>&1; then
    echo "✅ 前端服务启动成功"
else
    echo "❌ 前端服务启动失败"
fi

echo ""
echo "🧹 清理测试进程..."

# 停止服务
kill $BACKEND_PID 2>/dev/null || true
kill $FRONTEND_PID 2>/dev/null || true

# 等待进程停止
sleep 3

# 检查是否有残留进程
if ps -p $BACKEND_PID >/dev/null 2>&1; then
    echo "⚠️  后端进程仍在运行，强制终止"
    kill -9 $BACKEND_PID 2>/dev/null || true
fi

if ps -p $FRONTEND_PID >/dev/null 2>&1; then
    echo "⚠️  前端进程仍在运行，强制终止"
    kill -9 $FRONTEND_PID 2>/dev/null || true
fi

echo ""
echo "✅ 服务启动测试完成"