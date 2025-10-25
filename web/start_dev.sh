#!/bin/bash

# MyStocks Web 开发环境启动脚本

echo "🚀 启动 MyStocks Web 开发环境..."
echo "=================================="

# 检查Python和Node.js是否安装
echo "📋 检查环境依赖..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装 Python 3.8+"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js 16+"
    exit 1
fi

echo "✅ 环境依赖检查通过"

# 安装后端依赖
echo "📦 安装后端依赖..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

# 启动后端服务
echo "🔧 启动后端服务..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 安装前端依赖并启动
echo "🎨 安装前端依赖..."
cd ../frontend
npm install

# 启动前端服务
echo "🎨 启动前端服务..."
npm run dev &
FRONTEND_PID=$!

echo "=================================="
echo "✅ 服务启动成功！"
echo ""
echo "🌐 前端地址: http://localhost:3000"
echo "📚 API文档: http://localhost:8000/api/docs"
echo ""
echo "🔑 默认登录账户："
echo "   管理员: admin / admin123"
echo "   用户: user / user123"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo "=================================="

# 等待用户中断
trap 'echo "🛑 正在停止服务..."; kill $BACKEND_PID $FRONTEND_PID; exit' INT
wait