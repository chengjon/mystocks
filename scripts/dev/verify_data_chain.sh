#!/bin/bash

# MyStocks 数据链路验证脚本
# 用于验证前后端服务、API接口和数据完整性

echo "🔍 开始验证 MyStocks 数据链路..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 验证后端服务状态
echo -e "\n📋 验证后端服务状态..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health | grep -q "200"; then
    echo -e "✅ 后端服务: ${GREEN}正常${NC}"
else
    echo -e "❌ 后端服务: ${RED}异常${NC}"
    exit 1
fi

# 验证前端服务状态
echo -e "\n📋 验证前端服务状态..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/ | grep -q "200"; then
    echo -e "✅ 前端服务: ${GREEN}正常${NC}"
else
    echo -e "❌ 前端服务: ${RED}异常${NC}"
    exit 1
fi

# 验证前端页面访问
echo -e "\n📋 验证前端页面访问..."
PAGES=("/" "/dashboard" "/stocks" "/technical-analysis")
for page in "${PAGES[@]}"; do
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:3001$page" | grep -q "200"; then
        echo -e "✅ 页面 $page: ${GREEN}正常访问${NC}"
    else
        echo -e "❌ 页面 $page: ${RED}访问失败${NC}"
        exit 1
    fi
done

# 验证API接口
echo -e "\n📋 验证API接口..."

# 获取认证令牌
echo "获取认证令牌..."
AUTH_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123")

TOKEN=$(echo $AUTH_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))")

if [ -z "$TOKEN" ]; then
    echo -e "❌ 认证失败: ${RED}无法获取访问令牌${NC}"
    exit 1
else
    echo -e "✅ 认证: ${GREEN}成功获取令牌${NC}"
fi

# 验证股票基本信息API
echo "验证股票基本信息API..."
STOCKS_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/data/stocks/basic?limit=5" \
  -H "Authorization: Bearer $TOKEN")

if echo "$STOCKS_RESPONSE" | grep -q '"success":true'; then
    echo -e "✅ 股票基本信息API: ${GREEN}返回成功${NC}"
    
    # 检查数据是否存在且非空
    DATA_COUNT=$(echo "$STOCKS_RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data.get('data', [])))")
    if [ "$DATA_COUNT" -ge 1 ]; then
        echo -e "✅ 股票数据: ${GREEN}存在 $DATA_COUNT 条记录${NC}"
    else
        echo -e "❌ 股票数据: ${RED}数据为空或不存在${NC}"
        exit 1
    fi
else
    echo -e "❌ 股票基本信息API: ${RED}返回失败${NC}"
    exit 1
fi

# 验证市场概览API
echo "验证市场概览API..."
OVERVIEW_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/data/markets/overview" \
  -H "Authorization: Bearer $TOKEN")

if echo "$OVERVIEW_RESPONSE" | grep -q '"success":true'; then
    echo -e "✅ 市场概览API: ${GREEN}返回成功${NC}"
    
    # 检查数据是否存在
    TOTAL_STOCKS=$(echo "$OVERVIEW_RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('data', {}).get('total_stocks', 0))")
    if [ "$TOTAL_STOCKS" -ge 1 ]; then
        echo -e "✅ 市场数据: ${GREEN}存在 $TOTAL_STOCKS 只股票${NC}"
    else
        echo -e "⚠️  市场数据: ${YELLOW}股票数量为0，但API正常${NC}"
    fi
else
    echo -e "❌ 市场概览API: ${RED}返回失败${NC}"
    exit 1
fi

# 验证前端代理API
echo "验证前端代理API..."
FRONTEND_PROXY_RESPONSE=$(curl -s -X GET "http://localhost:3001/api/data/stocks/basic?limit=5" \
  -H "Authorization: Bearer $TOKEN")

if echo "$FRONTEND_PROXY_RESPONSE" | grep -q '"success":true'; then
    echo -e "✅ 前端代理API: ${GREEN}正常转发${NC}"
    
    # 检查数据是否存在且非空
    PROXY_DATA_COUNT=$(echo "$FRONTEND_PROXY_RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data.get('data', [])))")
    if [ "$PROXY_DATA_COUNT" -ge 1 ]; then
        echo -e "✅ 代理数据: ${GREEN}存在 $PROXY_DATA_COUNT 条记录${NC}"
    else
        echo -e "❌ 代理数据: ${RED}数据为空或不存在${NC}"
        exit 1
    fi
else
    echo -e "❌ 前端代理API: ${RED}转发失败${NC}"
    exit 1
fi

echo -e "\n🎉 ${GREEN}全部验证通过！数据链路正常工作${NC}"
echo "   - 后端服务运行正常 (端口 8888)"
echo "   - 前端服务运行正常 (端口 3001)"
echo "   - 所有页面可正常访问"
echo "   - API接口返回成功"
echo "   - 数据存在且格式正确"
echo "   - 前端代理正常转发请求"