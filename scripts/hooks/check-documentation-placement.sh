#!/bin/bash
#
# Pre-commit hook: Documentation placement check
#
# 功能：检查文档是否放在了正确的位置
# - 检测根目录下的.md文件
# - 检测中文文件名
# - 检测临时文档
# - 提供正确的移动建议
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 问题计数
ISSUES_FOUND=0

echo -e "${BLUE}🔍 检查文档位置...${NC}"

# 检查根目录下的.md文件（应该移到docs/子目录）
ROOT_MD_FILES=$(find . -maxdepth 1 -name "*.md" -type f ! -name "README.md" ! -name "CLAUDE.md" ! -name "CHANGELOG.md" ! -name "AGENTS.md" 2>/dev/null || true)
if [ -n "$ROOT_MD_FILES" ]; then
    echo -e "${YELLOW}⚠️  发现根目录下的.md文件（应移到docs/子目录）：${NC}"
    echo "$ROOT_MD_FILES" | while read file; do
        filename=$(basename "$file")
        echo -e "  ${YELLOW}•${NC} $filename"

        # 分析文件内容，建议正确的分类
        if grep -q "API\|接口" "$file" 2>/dev/null; then
            echo -e "    ${GREEN}建议${NC}: git mv $filename docs/api/"
        elif grep -q "架构\|设计\|Architecture" "$file" 2>/dev/null; then
            echo -e "    ${GREEN}建议${NC}: git mv $filename docs/architecture/"
        elif grep -q "测试\|Test\|质量" "$file" 2>/dev/null; then
            echo -e "    ${GREEN}建议${NC}: git mv $filename docs/testing/"
        elif grep -q "部署\|运维\|监控\|Deploy" "$file" 2>/dev/null; then
            echo -e "    ${GREEN}建议${NC}: git mv $filename docs/operations/"
        elif grep -q "报告\|Report\|分析" "$file" 2>/dev/null; then
            echo -e "    ${GREEN}建议${NC}: git mv $filename docs/reports/"
        elif grep -q "指南\|Guide\|教程\|Quick" "$file" 2>/dev/null; then
            echo -e "    ${GREEN}建议${NC}: git mv $filename docs/guides/"
        else
            echo -e "    ${GREEN}建议${NC}: git mv $filename docs/overview/"
        fi
    done
    echo ""
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# 检查docs/根目录下的.md文件（应该移到8大分类）
DOCS_ROOT_MD=$(find docs/ -maxdepth 1 -name "*.md" -type f ! -name "INDEX.md" 2>/dev/null || true)
if [ -n "$DOCS_ROOT_MD" ]; then
    echo -e "${YELLOW}⚠️  发现docs/根目录下的.md文件（应移到8大分类目录）：${NC}"
    echo "$DOCS_ROOT_MD" | while read file; do
        filename=$(basename "$file")
        echo -e "  ${YELLOW}•${NC} $filename"

        # 根据文件名建议分类
        case "$filename" in
            *API*|*api*|*接口*)
                echo -e "    ${GREEN}建议${NC}: git mv docs/$filename docs/api/"
                ;;
            *架构*|*设计*|*Architecture*)
                echo -e "    ${GREEN}建议${NC}: git mv docs/$filename docs/architecture/"
                ;;
            *测试*|*Test*|*质量*)
                echo -e "    ${GREEN}建议${NC}: git mv docs/$filename docs/testing/"
                ;;
            *部署*|*运维*|*监控*)
                echo -e "    ${GREEN}建议${NC}: git mv docs/$filename docs/operations/"
                ;;
            *报告*|*Report*|*分析*)
                echo -e "    ${GREEN}建议${NC}: git mv docs/$filename docs/reports/"
                ;;
            *指南*|*Guide*|*教程*)
                echo -e "    ${GREEN}建议${NC}: git mv docs/$filename docs/guides/"
                ;;
            *)
                echo -e "    ${GREEN}建议${NC}: git mv docs/$filename docs/overview/"
                ;;
        esac
    done
    echo ""
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# 检测中文文件名
CHINESE_FILENAME=$(find docs/ -name "*[\u4e00-\u9fa5]*.md" -type f 2>/dev/null || true)
if [ -n "$CHINESE_FILENAME" ]; then
    echo -e "${YELLOW}⚠️  发现中文文件名（建议使用英文或拼音）：${NC}"
    echo "$CHINESE_FILENAME" | while read file; do
        echo -e "  ${YELLOW}•${NC} $file"

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
        echo -e "  ${YELLOW}•${NC} $file (${MAX_DEPTH}层)"
        echo -e "    ${GREEN}建议${NC}: 扁平化目录结构"
    done
    echo ""
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# 显示帮助信息
if [ $ISSUES_FOUND -gt 0 ]; then
    echo -e "${RED}❌ 发现 $ISSUES_FOUND 个文档位置问题${NC}"
    echo ""
    echo -e "${BLUE}📖 查看详细指引：${NC}"
    echo -e "  ${GREEN}docs/guides/DOCUMENTATION_WORKFLOW_GUIDE.md${NC}"
    echo ""
    echo -e "${BLUE}🔧 自动修复工具：${NC}"
    echo -e "  python scripts/tools/docs_check.py --fix-empty-dirs"
    echo -e "  python scripts/tools/docs_indexer.py --categories"
    echo ""
    echo -e "${YELLOW}💡 提示：使用以下命令忽略检查${NC}"
    echo -e "  SKIP=documentation-check git commit"
    echo ""
else
    echo -e "${GREEN}✅ 文档位置检查通过！${NC}"
fi

exit 0
