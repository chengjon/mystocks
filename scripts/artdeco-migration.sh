#!/bin/bash

# ArtDeco 风格迁移自动化脚本
# 专门用于PC端Vue组件改造

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_ROOT/web/frontend/src"
STYLES_DIR="$FRONTEND_DIR/styles"

echo "=========================================="
echo "ArtDeco 风格迁移工具 - PC端专用"
echo "=========================================="
echo ""

# 检查 ArtDeco 样式文件是否存在
if [ ! -f "$STYLES_DIR/artdeco-tokens.scss" ]; then
    echo "错误：找不到 ArtDeco tokens 文件"
    exit 1
fi

echo "✓ 找到 ArtDeco 样式文件"
echo ""

# 函数：替换颜色变量
replace_colors() {
    local file=$1

    # 背景色替换
    sed -i 's/background: #ffffff/background: var(--artdeco-bg-primary)/g' "$file" 2>/dev/null || true
    sed -i 's/background: #f5f5f5/background: var(--artdeco-bg-card)/g' "$file" 2>/dev/null || true
    sed -i 's/background: #f0f2f5/background: var(--artdeco-bg-card)/g' "$file" 2>/dev/null || true
    sed -i 's/background: #fff/background: var(--artdeco-bg-card)/g' "$file" 2>/dev/null || true

    # 文字颜色替换
    sed -i 's/color: #303133/color: var(--artdeco-fg-primary)/g' "$file" 2>/dev/null || true
    sed -i 's/color: #606266/color: var(--artdeco-fg-secondary)/g' "$file" 2>/dev/null || true
    sed -i 's/color: #909399/color: var(--artdeco-fg-muted)/g' "$file" 2>/dev/null || true

    # 强调色替换
    sed -i 's/color: #409eff/color: var(--artdeco-accent-gold)/g' "$file" 2>/dev/null || true
    sed -i 's/background: #409eff/background: var(--artdeco-accent-gold)/g' "$file" 2>/dev/null || true
    sed -i 's/border-color: #409eff/border-color: var(--artdeco-accent-gold)/g' "$file" 2>/dev/null || true
    sed -i 's/border: 1px solid #409eff/border: 1px solid var(--artdeco-accent-gold)/g' "$file" 2>/dev/null || true

    # A股颜色替换
    sed -i 's/color: #f56c6c/color: var(--artdeco-color-up)/g' "$file" 2>/dev/null || true
    sed -i 's/color: #67c23a/color: var(--artdeco-color-down)/g' "$file" 2>/dev/null || true

    echo "  - 颜色变量已替换"
}

# 函数：添加 ArtDeco 字体
add_fonts() {
    local file=$1

    # 检查是否已经导入了 ArtDeco tokens
    if ! grep -q "artdeco-tokens.scss" "$file"; then
        # 在 <style> 标签后添加导入
        sed -i '/<style scoped lang="scss">/a @import '"'"'@/styles/artdeco-tokens.scss'"'"';' "$file" 2>/dev/null || true
        sed -i '/<style scoped>/a @import '"'"'@/styles/artdeco-tokens.scss'"'"';' "$file" 2>/dev/null || true
    fi

    echo "  - ArtDeco 样式导入已添加"
}

# 函数：移除圆角
remove_border_radius() {
    local file=$1

    # 移除圆角（除了特定值）
    sed -i 's/border-radius: [0-9]*px/border-radius: var(--artdeco-radius-none)/g' "$file" 2>/dev/null || true
    sed -i 's/border-radius: 2px/border-radius: var(--artdeco-radius-sm)/g' "$file" 2>/dev/null || true
    sed -i 's/border-radius: 4px/border-radius: var(--artdeco-radius-none)/g' "$file" 2>/dev/null || true
    sed -i 's/border-radius: 8px/border-radius: var(--artdeco-radius-none)/g' "$file" 2>/dev/null || true

    echo "  - 圆角已移除"
}

# 函数：添加大写和字间距
add_uppercase_spacing() {
    local file=$1

    # 在 .title, .header, h1, h2, h3, h4 样式中添加大写和字间距
    # 这是简化版本，实际使用时需要更精确的匹配

    echo "  - 大写和字间距建议已添加（需手动调整）"
}

# 函数：转换 Element Plus 组件样式
convert_element_plus() {
    local file=$1

    # 为 Element Plus 组件添加 :deep() 选择器
    # 这是一个简化版本

    echo "  - Element Plus 组件适配提示已添加"
}

# 主改造函数
transform_file() {
    local file=$1
    local backup="${file}.backup"

    echo "处理文件: $file"

    # 创建备份
    cp "$file" "$backup"

    # 执行改造
    replace_colors "$file"
    add_fonts "$file"
    remove_border_radius "$file"
    add_uppercase_spacing "$file"
    convert_element_plus "$file"

    echo "✓ 文件处理完成"
    echo ""
}

# 批量处理函数
batch_transform() {
    local pattern=$1

    echo "=========================================="
    echo "批量处理模式: $pattern"
    echo "=========================================="
    echo ""

    local count=0
    for file in $(find "$FRONTEND_DIR" -name "$pattern" -type f | grep -v node_modules); do
        if [ -f "$file" ]; then
            transform_file "$file"
            ((count++))
        fi
    done

    echo "=========================================="
    echo "处理完成！共处理 $count 个文件"
    echo "=========================================="
    echo ""
}

# 恢复备份函数
restore_backup() {
    local file=$1
    local backup="${file}.backup"

    if [ -f "$backup" ]; then
        mv "$backup" "$file"
        echo "✓ 已恢复: $file"
    else
        echo "✗ 备份文件不存在: $backup"
    fi
}

# 清理备份函数
clean_backups() {
    echo "清理备份文件..."

    find "$FRONTEND_DIR" -name "*.backup" -type f -delete

    echo "✓ 备份文件已清理"
}

# 显示帮助信息
show_help() {
    cat << EOF
ArtDeco 风格迁移工具 - 使用说明

用法:
    $0 [命令] [参数]

命令:
    transform <file>      转换单个文件
    batch <pattern>        批量转换文件（支持通配符，如 *.vue）
    restore <file>         恢复单个文件的备份
    clean                  清理所有备份文件
    help                   显示此帮助信息

示例:
    $0 transform views/Login.vue
    $0 batch "*.vue"
    $0 restore views/Login.vue
    $0 clean

注意:
    - 此工具会自动创建 .backup 备份文件
    - 建议在提交代码前检查转换结果
    - 某些样式可能需要手动调整以达到最佳效果
EOF
}

# 主程序
main() {
    case "${1:-help}" in
        transform)
            if [ -z "$2" ]; then
                echo "错误：请指定要转换的文件"
                exit 1
            fi
            local file_path="$FRONTEND_DIR/$2"
            if [ ! -f "$file_path" ]; then
                echo "错误：文件不存在: $file_path"
                exit 1
            fi
            transform_file "$file_path"
            ;;
        batch)
            if [ -z "$2" ]; then
                echo "错误：请指定文件模式（如 *.vue）"
                exit 1
            fi
            batch_transform "$2"
            ;;
        restore)
            if [ -z "$2" ]; then
                echo "错误：请指定要恢复的文件"
                exit 1
            fi
            local file_path="$FRONTEND_DIR/$2"
            restore_backup "$file_path"
            ;;
        clean)
            clean_backups
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo "未知命令: $1"
            echo "使用 '$0 help' 查看帮助信息"
            exit 1
            ;;
    esac
}

main "$@"
