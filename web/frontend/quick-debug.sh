#!/bin/bash

# Vue 3 组件快速诊断脚本
# 用法: ./quick-debug.sh [组件文件路径]
# 示例: ./quick-debug.sh src/components/market/WencaiPanel.vue

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "=================================="
echo "  Vue 3 组件快速诊断工具"
echo "=================================="
echo ""

COMPONENT_PATH="${1:-}"

# 如果没有提供组件路径，进行通用检查
if [ -z "$COMPONENT_PATH" ]; then
    echo "未指定组件，执行通用检查..."
    echo ""
fi

# ========== 1. 构建检查 ==========
echo "1. 检查构建状态..."
echo "   运行: npm run build"
echo ""

BUILD_OUTPUT=$(npm run build 2>&1)
if echo "$BUILD_OUTPUT" | grep -qi "error"; then
    echo -e "${RED}❌ 构建失败${NC}"
    echo ""
    echo "错误详情："
    echo "$BUILD_OUTPUT" | grep -A 5 -i "error"
    echo ""
else
    echo -e "${GREEN}✅ 构建成功${NC}"
fi
echo ""

# ========== 2. 组件文件检查 ==========
if [ -n "$COMPONENT_PATH" ]; then
    echo "2. 检查组件文件: $COMPONENT_PATH"

    if [ -f "$COMPONENT_PATH" ]; then
        echo -e "${GREEN}✅ 文件存在${NC}"

        # 检查文件大小
        FILE_SIZE=$(stat -f%z "$COMPONENT_PATH" 2>/dev/null || stat -c%s "$COMPONENT_PATH" 2>/dev/null)
        echo "   文件大小: $FILE_SIZE bytes"

        # 检查是否为空
        if [ "$FILE_SIZE" -eq 0 ]; then
            echo -e "${RED}❌ 警告: 文件为空${NC}"
        fi
    else
        echo -e "${RED}❌ 文件不存在${NC}"
    fi
    echo ""

    # ========== 3. 图标导入检查 ==========
    if [ -f "$COMPONENT_PATH" ]; then
        echo "3. 检查 Element Plus 图标导入..."

        ICON_IMPORTS=$(grep "from '@element-plus/icons-vue'" "$COMPONENT_PATH" || true)

        if [ -n "$ICON_IMPORTS" ]; then
            echo "   发现图标导入："
            echo "   $ICON_IMPORTS"
            echo ""

            # 提取图标名称
            ICONS=$(echo "$ICON_IMPORTS" | sed -n 's/.*{\s*\(.*\)\s*}.*/\1/p' | tr ',' '\n')

            echo "   验证图标是否存在："
            while IFS= read -r icon; do
                icon=$(echo "$icon" | xargs)  # trim whitespace
                if [ -n "$icon" ]; then
                    if grep -q "\"$icon\"" node_modules/@element-plus/icons-vue/dist/index.js 2>/dev/null; then
                        echo -e "   ${GREEN}✅ $icon${NC}"
                    else
                        echo -e "   ${RED}❌ $icon (不存在!)${NC}"
                        echo "      建议替换为相似图标："

                        # 提供建议
                        case "$icon" in
                            History)
                                echo "      - Clock (时钟/历史)"
                                echo "      - Timer (计时器)"
                                ;;
                            Time)
                                echo "      - Clock"
                                echo "      - Timer"
                                ;;
                            *)
                                echo "      请查看 Element Plus 图标文档"
                                ;;
                        esac
                    fi
                fi
            done <<< "$ICONS"
        else
            echo "   未发现图标导入"
        fi
        echo ""
    fi
fi

# ========== 4. 服务状态检查 ==========
echo "4. 检查服务状态..."

# 检查前端服务
if curl -s http://localhost:3001 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 前端服务运行中${NC} (http://localhost:3001)"
else
    echo -e "${RED}❌ 前端服务未运行${NC}"
    echo "   启动命令: npm run dev"
fi

# 检查后端服务
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 后端服务运行中${NC} (http://localhost:8000)"
else
    echo -e "${YELLOW}⚠️  后端服务可能未运行${NC}"
    echo "   检查命令: ps aux | grep uvicorn"
fi
echo ""

# ========== 5. 依赖检查 ==========
echo "5. 检查关键依赖..."

if [ -f "package.json" ]; then
    # 检查 Element Plus
    if grep -q "\"element-plus\"" package.json; then
        EP_VERSION=$(npm list element-plus 2>/dev/null | grep "element-plus@" | head -1 | awk '{print $2}')
        echo -e "${GREEN}✅ element-plus${NC} $EP_VERSION"
    else
        echo -e "${RED}❌ element-plus 未安装${NC}"
    fi

    # 检查 Element Plus Icons
    if grep -q "\"@element-plus/icons-vue\"" package.json; then
        ICON_VERSION=$(npm list @element-plus/icons-vue 2>/dev/null | grep "@element-plus/icons-vue@" | head -1 | awk '{print $2}')
        echo -e "${GREEN}✅ @element-plus/icons-vue${NC} $ICON_VERSION"
    else
        echo -e "${RED}❌ @element-plus/icons-vue 未安装${NC}"
    fi

    # 检查 Vue
    if grep -q "\"vue\"" package.json; then
        VUE_VERSION=$(npm list vue 2>/dev/null | grep " vue@" | head -1 | awk '{print $2}')
        echo -e "${GREEN}✅ vue${NC} $VUE_VERSION"
    else
        echo -e "${RED}❌ vue 未安装${NC}"
    fi
else
    echo -e "${RED}❌ 未找到 package.json${NC}"
fi
echo ""

# ========== 6. 路由配置检查 ==========
if [ -n "$COMPONENT_PATH" ]; then
    echo "6. 检查路由配置..."

    COMPONENT_NAME=$(basename "$COMPONENT_PATH" .vue)

    if [ -f "src/router/index.js" ]; then
        if grep -q "$COMPONENT_NAME" src/router/index.js; then
            echo -e "${GREEN}✅ 路由中找到该组件${NC}"
            echo "   路由配置："
            grep -A 3 -B 1 "$COMPONENT_NAME" src/router/index.js | head -6
        else
            echo -e "${YELLOW}⚠️  路由中未找到该组件${NC}"
        fi
    else
        echo -e "${RED}❌ 未找到 src/router/index.js${NC}"
    fi
    echo ""
fi

# ========== 7. 常见错误模式检查 ==========
if [ -n "$COMPONENT_PATH" ] && [ -f "$COMPONENT_PATH" ]; then
    echo "7. 检查常见错误模式..."

    ERRORS=0

    # 检查硬编码URL
    HARDCODED_URLS=$(grep -n "http://localhost" "$COMPONENT_PATH" | grep -v "// " || true)
    if [ -n "$HARDCODED_URLS" ]; then
        echo -e "${YELLOW}⚠️  发现硬编码URL:${NC}"
        echo "$HARDCODED_URLS"
        echo "   建议: 使用 API_ENDPOINTS 配置"
        ERRORS=$((ERRORS + 1))
    fi

    # 检查console.log (生产环境应移除)
    CONSOLE_LOGS=$(grep -n "console.log" "$COMPONENT_PATH" | wc -l)
    if [ "$CONSOLE_LOGS" -gt 5 ]; then
        echo -e "${YELLOW}⚠️  发现 $CONSOLE_LOGS 个 console.log${NC}"
        echo "   建议: 生产环境前移除调试日志"
        ERRORS=$((ERRORS + 1))
    fi

    if [ "$ERRORS" -eq 0 ]; then
        echo -e "${GREEN}✅ 未发现常见错误模式${NC}"
    fi
    echo ""
fi

# ========== 8. 建议 ==========
echo "=================================="
echo "  诊断完成"
echo "=================================="
echo ""
echo "常用修复命令："
echo ""
echo "  # 硬刷新浏览器"
echo "  Ctrl + Shift + R (Windows/Linux)"
echo "  Cmd + Shift + R (Mac)"
echo ""
echo "  # 清除缓存重新安装"
echo "  rm -rf node_modules package-lock.json && npm install"
echo ""
echo "  # 重启开发服务器"
echo "  npm run dev"
echo ""
echo "  # 查看实时日志"
echo "  tail -f /tmp/frontend.log"
echo ""
echo "更多帮助请查看:"
echo "  - VUE_DEBUGGING_GUIDE.md (详细调试指南)"
echo "  - QUICK_REFERENCE.md (快速参考手册)"
echo ""
