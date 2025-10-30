#!/bin/bash

# 前端开发服务器启动脚本
# 功能: 自动尝试端口3000->3001->3002，如果全部被占用则报警

echo "========================================"
echo "🚀 启动MyStocks前端开发服务器"
echo "========================================"
echo ""

# 定义允许的端口列表
PORTS=(3000 3001 3002)
SELECTED_PORT=""

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 1  # 端口被占用
    else
        return 0  # 端口可用
    fi
}

# 遍历端口列表查找可用端口
echo "🔍 检查可用端口..."
for port in "${PORTS[@]}"; do
    if check_port $port; then
        SELECTED_PORT=$port
        echo "✅ 端口 $port 可用"
        break
    else
        echo "⚠️  端口 $port 已被占用"
    fi
done

# 如果没有找到可用端口，报警并退出
if [ -z "$SELECTED_PORT" ]; then
    echo ""
    echo "========================================" >&2
    echo "❌ 错误: 所有端口都被占用！" >&2
    echo "========================================" >&2
    echo "" >&2
    echo "已尝试的端口: ${PORTS[*]}" >&2
    echo "" >&2
    echo "请执行以下操作之一:" >&2
    echo "  1. 释放占用的端口:" >&2
    for port in "${PORTS[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
            PID=$(lsof -Pi :$port -sTCP:LISTEN -t)
            echo "     端口 $port 被PID $PID 占用，可执行: kill $PID" >&2
        fi
    done
    echo "  2. 修改 vite.config.js 中的 port 配置" >&2
    echo "  3. 等待其他服务释放端口后重试" >&2
    echo "" >&2
    echo "========================================" >&2
    exit 1
fi

# 使用找到的端口启动服务
echo ""
echo "✅ 使用端口: $SELECTED_PORT"
echo ""

# 临时修改环境变量指定端口
export VITE_PORT=$SELECTED_PORT

# 启动Vite开发服务器
echo "🚀 启动Vite开发服务器..."
echo ""
npm run dev -- --port $SELECTED_PORT --host 0.0.0.0
