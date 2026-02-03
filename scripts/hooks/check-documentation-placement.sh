#!/bin/bash
#
# Pre-commit hook: Documentation placement check (建议模式)
#
# 功能：检查文档是否放在了正确的位置
# - 检测根目录下的.md文件
# - 检测中文文件名
# - 检测临时文档
# - 提供正确的移动建议（非强制）
# - 记录未采纳建议的情况到日志
#
# 使用方法：
#   正常模式: 建议模式（不阻止提交）
#   跳过检查: SKIP=documentation-check git commit
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
LOG_DIR="logs/docs-audit"
LOG_FILE="$LOG_DIR/placement-suggestions-$(date +%Y%m%d-%H%M%S).log"
SUGGESTIONS_COUNT=0

# 创建日志目录
mkdir -p "$LOG_DIR"

# 问题计数（仅用于显示，不作为退出依据）
ISSUES_FOUND=0

# 记录函数
log_suggestion() {
    local suggestion="$1"
    local file="$2"

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $file | $suggestion" >> "$LOG_FILE"
    SUGGESTIONS_COUNT=$((SUGGESTIONS_COUNT + 1))
}

echo -e "${BLUE}🔍 检查文档位置（建议模式）...${NC}"
echo -e "${BLUE}📋 建议日志: $LOG_FILE${NC}"
echo ""

# 检查根目录下的.md文件（应该移到docs/子目录）
# 允许的根目录文件：项目标识 + AI辅助工具必需文件
ROOT_MD_FILES=$(find . -maxdepth 1 -name "*.md" -type f \
    ! -name "README.md" \
    ! -name "CLAUDE.md" \
    ! -name "GEMINI.md" \
    ! -name "IFLOW.md" \
    ! -name "AGENTS.md" \
    ! -name "CHANGELOG.md" \
    2>/dev/null || true)
if [ -n "$ROOT_MD_FILES" ]; then
    echo -e "${YELLOW}⚠️  发现根目录下的.md文件（建议移到docs/子目录）：${NC}"
    echo "$ROOT_MD_FILES" | while read file; do
        filename=$(basename "$file")
        echo -e "  ${YELLOW}•${NC} $filename"

        # 分析文件内容，建议正确的分类
        if grep -q "API\|接口" "$file" 2>/dev/null; then
            suggestion="docs/api/"
            echo -e "    ${GREEN}建议${NC}: git mv $filename $suggestion"
            log_suggestion "根目录文档应移到API目录: $filename → $suggestion" "$file"
        elif grep -q "架构\|设计\|Architecture" "$file" 2>/dev/null; then
            suggestion="docs/architecture/"
            echo -e "    ${GREEN}建议${NC}: git mv $filename $suggestion"
            log_suggestion "根目录文档应移到架构目录: $filename → $suggestion" "$file"
        elif grep -q "测试\|Test\|质量" "$file" 2>/dev/null; then
            suggestion="docs/testing/"
            echo -e "    ${GREEN}建议${NC}: git mv $filename $suggestion"
            log_suggestion "根目录文档应移到测试目录: $filename → $suggestion" "$file"
        elif grep -q "部署\|运维\|监控\|Deploy" "$file" 2>/dev/null; then
            suggestion="docs/operations/"
            echo -e "    ${GREEN}建议${NC}: git mv $filename $suggestion"
            log_suggestion "根目录文档应移到运维目录: $filename → $suggestion" "$file"
        elif grep -q "报告\|Report\|分析" "$file" 2>/dev/null; then
            suggestion="docs/reports/"
            echo -e "    ${GREEN}建议${NC}: git mv $filename $suggestion"
            log_suggestion "根目录文档应移到报告目录: $filename → $suggestion" "$file"
        elif grep -q "指南\|Guide\|教程\|Quick" "$file" 2>/dev/null; then
            suggestion="docs/guides/"
            echo -e "    ${GREEN}建议${NC}: git mv $filename $suggestion"
            log_suggestion "根目录文档应移到指南目录: $filename → $suggestion" "$file"
        else
            suggestion="docs/overview/"
            echo -e "    ${GREEN}建议${NC}: git mv $filename $suggestion"
            log_suggestion "根目录文档应移到概览目录: $filename → $suggestion" "$file"
        fi
    done
    echo ""
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# 检查docs/根目录下的.md文件（应该移到8大分类）
DOCS_ROOT_MD=$(find docs/ -maxdepth 1 -name "*.md" -type f ! -name "INDEX.md" 2>/dev/null || true)
if [ -n "$DOCS_ROOT_MD" ]; then
    echo -e "${YELLOW}⚠️  发现docs/根目录下的.md文件（建议移到8大分类目录）：${NC}"
    echo "$DOCS_ROOT_MD" | while read file; do
        filename=$(basename "$file")
        echo -e "  ${YELLOW}•${NC} $filename"

        # 根据文件名建议分类
        case "$filename" in
            *API*|*api*|*接口*)
                suggestion="docs/api/"
                echo -e "    ${GREEN}建议${NC}: git mv docs/$filename $suggestion"
                log_suggestion "docs根目录文档应移到API目录: $filename → $suggestion" "$file"
                ;;
            *架构*|*设计*|*Architecture*)
                suggestion="docs/architecture/"
                echo -e "    ${GREEN}建议${NC}: git mv docs/$filename $suggestion"
                log_suggestion "docs根目录文档应移到架构目录: $filename → $suggestion" "$file"
                ;;
            *测试*|*Test*|*质量*)
                suggestion="docs/testing/"
                echo -e "    ${GREEN}建议${NC}: git mv docs/$filename $suggestion"
                log_suggestion "docs根目录文档应移到测试目录: $filename → $suggestion" "$file"
                ;;
            *部署*|*运维*|*监控*)
                suggestion="docs/operations/"
                echo -e "    ${GREEN}建议${NC}: git mv docs/$filename $suggestion"
                log_suggestion "docs根目录文档应移到运维目录: $filename → $suggestion" "$file"
                ;;
            *报告*|*Report*|*分析*)
                suggestion="docs/reports/"
                echo -e "    ${GREEN}建议${NC}: git mv docs/$filename $suggestion"
                log_suggestion "docs根目录文档应移到报告目录: $filename → $suggestion" "$file"
                ;;
            *指南*|*Guide*|*教程*)
                suggestion="docs/guides/"
                echo -e "    ${GREEN}建议${NC}: git mv docs/$filename $suggestion"
                log_suggestion "docs根目录文档应移到指南目录: $filename → $suggestion" "$file"
                ;;
            *)
                suggestion="docs/overview/"
                echo -e "    ${GREEN}建议${NC}: git mv docs/$filename $suggestion"
                log_suggestion "docs根目录文档应移到概览目录: $filename → $suggestion" "$file"
                ;;
        esac
    done
    echo ""
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# 检测中文文件名
CHINESE_FILENAME=$(find docs/ -name "*[\u4e00-\u9fa5]*.md" -type f \
    ! -path "docs/*/legacy-cn/*" \
    2>/dev/null || true)
if [ -n "$CHINESE_FILENAME" ]; then
    echo -e "${YELLOW}⚠️  发现中文文件名（建议使用英文或拼音）：${NC}"
    echo "$CHINESE_FILENAME" | while read file; do
        echo -e "  ${YELLOW}•${NC} $file"

        # 记录建议到日志
        log_suggestion "中文文件名建议改为kebab-case: $file" "$file"

        # 提供重命名建议
        dirname=$(dirname "$file")
        basename=$(basename "$file" .md)

        # 转换为拼音建议（简单示例）
        echo -e "    ${GREEN}建议${NC}: 重命名为 kebab-case"
        echo -e "    ${GREEN}示例${NC}: 'API文档.md' → 'api-documentation.md'"
        echo -e "    ${GREEN}示例${NC}: '问财集成.md' → 'wencai-integration.md'"
    done
    echo ""
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# 检测临时文件名（TEMP、TMP、DRAFT等）
TEMP_FILES=$(find docs/ -iname "*temp*.md" -o -iname "*tmp*.md" -o -iname "*draft*.md" -o -iname "*backup*.md" 2>/dev/null || true)
if [ -n "$TEMP_FILES" ]; then
    echo -e "${YELLOW}⚠️  发现临时文件（应删除或重命名）：${NC}"
    echo "$TEMP_FILES" | while read file; do
        echo -e "  ${YELLOW}•${NC} $file"
        echo -e "    ${GREEN}建议${NC}: git rm $file （如果是临时文件）"
        echo -e "    ${GREEN}建议${NC}: 重命名并移到合适位置（如果是正式文档）"
    done
    echo ""
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# 检测深层嵌套（>3层）
DEEP_FILES=$(find docs/ -name "*.md" -type f | awk -F/ '{print NF-1}' | sort -rn | head -1)
MAX_DEPTH=${DEEP_FILES:-0}
if [ "$MAX_DEPTH" -gt 3 ]; then
    echo -e "${YELLOW}⚠️  发现深层嵌套文档（超过3层）：${NC}"
    find docs/ -name "*.md" -type f | awk -F/ '{if (NF-1 > 3) print $0}' | head -5 | while read file; do
        depth=$(echo "$file" | tr '/' '\n' | wc -l)
        depth=$((depth - 1))
        echo -e "  ${YELLOW}•${NC} $file (${depth}层)"

        # 记录建议到日志
        log_suggestion "文档嵌套过深(${depth}层),建议扁平化: $file" "$file"

        echo -e "    ${GREEN}建议${NC}: 扁平化目录结构"
    done
    echo ""
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# 总结（建议模式：始终返回0）
echo ""
echo -e "${BLUE}📊 检查总结：${NC}"
echo -e "  - 发现问题: $ISSUES_FOUND 个"
echo -e "  - 建议数量: $SUGGESTIONS_COUNT 条"
echo -e "  - 建议日志: $LOG_FILE"
echo ""
echo -e "${GREEN}✅ 文档位置检查完成（建议模式，不阻止提交）${NC}"
echo -e "${YELLOW}💡 提示：这些建议不会被强制执行，但会被记录到日志中${NC}"
echo ""

exit 0
