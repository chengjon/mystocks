#!/bin/bash
# Oh My OpenCode 配置切换脚本
# 用法: ./switch-omo-config.sh [google|alternative|optimized|noco]

set -e

CONFIG_DIR="$HOME/.config/opencode"
ACTIVE_CONFIG="$CONFIG_DIR/oh-my-opencode.json"
GOOGLE_CONFIG="$CONFIG_DIR/oh-my-opencode.google.json"
ALTERNATIVE_CONFIG="$CONFIG_DIR/oh-my-opencode.alternative.json"
OPTIMIZED_CONFIG="$CONFIG_DIR/oh-my-opencode.optimized.json"
NOCO_CONFIG="$CONFIG_DIR/oh-my-opencode.noco.json"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 显示当前配置
show_current() {
    if [ -L "$ACTIVE_CONFIG" ]; then
        target=$(readlink "$ACTIVE_CONFIG")
        profile=$(basename "$target" | sed 's/oh-my-opencode\.\(.*\)\.json/\1/')
        echo -e "${GREEN}当前配置:${NC} ${profile:-默认}"
        echo -e "${BLUE}配置文件:${NC} $target"
    elif [ -f "$ACTIVE_CONFIG" ]; then
        profile=$(jq -r '.profile // "自定义"' "$ACTIVE_CONFIG" 2>/dev/null)
        echo -e "${GREEN}当前配置:${NC} ${profile:-默认}"
        echo -e "${BLUE}配置文件:${NC} $ACTIVE_CONFIG (直接文件)"
    else
        echo -e "${RED}未找到配置文件${NC}"
    fi
}

# 切换到 Google 配置
switch_google() {
    echo -e "${BLUE}切换到 Google Antigravity 配置...${NC}"
    backup_current
    ln -sf "$GOOGLE_CONFIG" "$ACTIVE_CONFIG"
    echo -e "${GREEN}✓ 已切换到 Google Antigravity 配置${NC}"
    show_models
}

# 切换到替代模型配置
switch_alternative() {
    echo -e "${BLUE}切换到替代模型配置 (GLM/DeepSeek/MiniMax)...${NC}"
    backup_current
    ln -sf "$ALTERNATIVE_CONFIG" "$ACTIVE_CONFIG"
    echo -e "${GREEN}✓ 已切换到替代模型配置${NC}"
    show_models
}

# 切换到优化配置
switch_optimized() {
    echo -e "${BLUE}切换到优化配置 (optimized)...${NC}"
    backup_current
    ln -sf "$OPTIMIZED_CONFIG" "$ACTIVE_CONFIG"
    echo -e "${GREEN}✓ 已切换到优化配置${NC}"
    show_models
}

# 切换到 noco 配置
switch_noco() {
    echo -e "${BLUE}切换到 NoCodeX 配置 (7个专业代理)...${NC}"
    backup_current
    if [ ! -f "$NOCO_CONFIG" ]; then
        echo -e "${RED}错误: noco 配置文件不存在${NC}"
        echo -e "${YELLOW}请先创建配置文件: $NOCO_CONFIG${NC}"
        exit 1
    fi
    ln -sf "$NOCO_CONFIG" "$ACTIVE_CONFIG"
    echo -e "${GREEN}✓ 已切换到 NoCodeX 配置${NC}"
    show_models
}

# 备份当前配置
backup_current() {
    if [ -f "$ACTIVE_CONFIG" ] && [ ! -L "$ACTIVE_CONFIG" ]; then
        backup="$CONFIG_DIR/oh-my-opencode.backup.$(date +%Y%m%d_%H%M%S).json"
        cp "$ACTIVE_CONFIG" "$backup"
        echo -e "${YELLOW}已备份原配置到: $backup${NC}"
    fi
}

# 显示当前配置的模型列表
show_models() {
    echo -e "\n${BLUE}当前代理模型配置:${NC}"
    if command -v jq &> /dev/null; then
        jq -r '.oh_my_opencode.agents | to_entries[] | "  \(.key): \(.value.model)"' "$ACTIVE_CONFIG" 2>/dev/null || echo "  无法解析模型配置"
    else
        echo "  (安装 jq 以查看详细信息: sudo apt install jq)"
    fi
    echo -e "\n${BLUE}MCP 服务器:${NC}"
    if command -v jq &> /dev/null; then
        jq -r '.mcp | to_entries[] | select(.value.enabled == true) | "  \(.key)"' "$ACTIVE_CONFIG" 2>/dev/null | sed 's/^/  ✓ /' || echo "  无启用的 MCP"
    else
        echo "  (安装 jq 以查看详细信息: sudo apt install jq)"
    fi
    echo ""
}

# 显示帮助信息
show_help() {
    echo "Oh My OpenCode 配置切换脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  google        切换到 Google Antigravity 模型配置"
    echo "  alternative   切换到替代模型配置 (GLM/DeepSeek/MiniMax)"
    echo "  optimized     切换到优化配置 (optimized-custom-api)"
    echo "  noco          切换到 NoCodeX 配置 (7个专业代理)"
    echo "  status        显示当前配置"
    echo "  help          显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 google         # 使用 Google 模型"
    echo "  $0 alternative    # 使用 GLM/DeepSeek 等模型"
    echo "  $0 noco          # 使用 NoCodeX 7个专业代理配置"
    echo "  $0 status         # 查看当前配置"
}

# 主逻辑
main() {
    case "${1:-}" in
        google)
            switch_google
            ;;
        alternative|alt)
            switch_alternative
            ;;
        optimized|opt)
            switch_optimized
            ;;
        noco)
            switch_noco
            ;;
        status|"")
            show_current
            show_models
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}错误: 未知选项 '$1'${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
