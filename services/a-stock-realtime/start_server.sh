#!/bin/bash

# MyStocks WebSocket服务器启动脚本

PROJECT_DIR="/tmp/a-stock-realtime"
PYTHON_CMD="python3"

echo "========================================"
echo "🚀 MyStocks A股实时行情WebSocket服务器"
echo "========================================"

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到python3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python版本: $PYTHON_VERSION"

# 检查依赖
echo ""
echo "📦 检查依赖..."
cd "$PROJECT_DIR" || exit 1

if [ ! -f "requirements.txt" ]; then
    echo "❌ 错误: 未找到requirements.txt"
    exit 1
fi

# 安装依赖（如果需要）
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📥 安装依赖..."
    pip3 install -q -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✅ 依赖安装成功"
    else
        echo "❌ 依赖安装失败"
        exit 1
    fi
else
    echo "✅ 依赖已安装"
fi

# 检查端口占用
PORT=8000
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口$PORT已被占用，尝试停止现有进程..."
    lsof -ti :$PORT | xargs kill -9 2>/dev/null
    sleep 1
    echo "✅ 已释放端口$PORT"
fi

# 启动服务器
echo ""
echo "========================================"
echo "🎯 启动WebSocket服务器"
echo "========================================"
echo ""
echo "📡 WebSocket端点: ws://localhost:8000/ws/market"
echo "🏥 健康检查: http://localhost:8000/health"
echo "📚 API文档: http://localhost:8000/docs"
echo ""
echo "💡 提示: 使用 'python3 test_client.py' 测试连接"
echo "⏹️  按 Ctrl+C 停止服务器"
echo ""
echo "========================================"
echo ""

cd "$PROJECT_DIR"
python3 websocket_server.py
