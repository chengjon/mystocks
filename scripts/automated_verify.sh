#!/bin/bash
# automated_verify.sh - 启动前端服务，运行验证，然后关闭服务

# 颜色配置
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🔍 启动自动化 Web 验证流程...${NC}"

# 1. 检查端口占用并清理
if lsof -i :3020 > /dev/null; then
    echo -e "${RED}⚠️  检测到 3020 端口已被占用，正在清理...${NC}"
    fuser -k 3020/tcp
    sleep 2
fi

# 2. 后台启动前端服务 (使用 dev:mock 模式以获得更稳定的测试数据，或者根据您的需求调整)
echo -e "${GREEN}🚀 正在启动前端开发服务器 (npm run dev)...${NC}"
cd web/frontend
nohup npm run dev > frontend_startup.log 2>&1 &
FRONTEND_PID=$!

# 3. 等待服务就绪
echo -e "${GREEN}⏳ 等待服务启动 (15秒)...${NC}"
sleep 15

# 检查服务是否存活
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}❌ 前端服务启动失败！查看日志:${NC}"
    cat frontend_startup.log
    exit 1
fi

# 简单的 HTTP 检查确保端口通了
if ! curl -s http://localhost:3020 > /dev/null; then
    echo -e "${RED}❌ 无法连接到 http://localhost:3020，服务可能未正确启动。${NC}"
    cat frontend_startup.log
    kill $FRONTEND_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✅ 前端服务已就绪。${NC}"

# 3.5 解析实际端口
# 从日志中提取 "Local:   http://localhost:3001/" 类似的行
ACTUAL_PORT=$(grep -oP 'Local:\s+http://localhost:\K\d+' frontend_startup.log | head -1)

if [ -z "$ACTUAL_PORT" ]; then
    echo -e "${RED}⚠️  无法从日志中提取端口，尝试默认端口 3020...${NC}"
    export FRONTEND_URL="http://localhost:3020"
else
    echo -e "${GREEN}🎯 检测到前端运行在端口: ${ACTUAL_PORT}${NC}"
    export FRONTEND_URL="http://localhost:${ACTUAL_PORT}"
fi

# 4. 运行验证脚本
echo -e "${GREEN}🧪 开始运行验证脚本...${NC}"
cd ../..
npm run verify:web-access
EXIT_CODE=$?

# 5. 清理与退出
echo -e "${GREEN}🧹正在关闭前端服务 (PID: $FRONTEND_PID)...${NC}"
kill $FRONTEND_PID 2>/dev/null
fuser -k 3020/tcp 2>/dev/null # 确保彻底杀死

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ 自动化验证流程成功完成！${NC}"
    exit 0
else
    echo -e "${RED}❌ 验证流程发现错误 (Exit Code: $EXIT_CODE)。${NC}"
    exit $EXIT_CODE
fi
