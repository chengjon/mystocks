#!/bin/bash
# 项目目录结构检查脚本
# 用法: ./scripts/maintenance/check-structure.sh [项目根目录]

set -euo pipefail

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${1:-"$(cd "$SCRIPT_DIR/../.." && pwd)"}"
MAX_ROOT_FILES=15
MAX_ROOT_DIRS=20

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
项目目录结构检查工具

用法:
    $0 [选项] [项目根目录]

选项:
    -h, --help              显示此帮助信息
    -v, --verbose           详细输出
    -f, --fix               自动修复发现的问题
    -q, --quiet             静默模式，只显示错误

参数:
    项目根目录              项目根目录路径（默认为当前目录的上上级）

示例:
    $0                      检查当前项目的目录结构
    $0 -v /path/to/project  详细检查指定项目
    $0 -f                   检查并自动修复问题

EOF
}

# 解析命令行参数
VERBOSE=false
AUTO_FIX=false
QUIET=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -f|--fix)
            AUTO_FIX=true
            shift
            ;;
        -q|--quiet)
            QUIET=true
            shift
            ;;
        -*)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
        *)
            PROJECT_ROOT="$1"
            shift
            ;;
    esac
done

# 检查项目根目录是否存在
if [[ ! -d "$PROJECT_ROOT" ]]; then
    log_error "项目根目录不存在: $PROJECT_ROOT"
    exit 1
fi

# 切换到项目根目录
cd "$PROJECT_ROOT"

# 检查根目录文件数量
check_root_files() {
    local file_count
    file_count=$(find . -maxdepth 1 -type f | wc -l)

    if [[ $file_count -gt $MAX_ROOT_FILES ]]; then
        log_warning "根目录文件数量过多: $file_count 个文件 (建议不超过 $MAX_ROOT_FILES 个)"

        if [[ $VERBOSE == true ]]; then
            log_info "根目录文件列表:"
            find . -maxdepth 1 -type f -exec basename {} \; | sort
        fi

        return 1
    else
        log_success "根目录文件数量正常: $file_count 个文件"
        return 0
    fi
}

# 检查根目录目录数量
check_root_dirs() {
    local dir_count
    dir_count=$(find . -maxdepth 1 -type d | wc -l)

    if [[ $dir_count -gt $MAX_ROOT_DIRS ]]; then
        log_warning "根目录目录数量过多: $dir_count 个目录 (建议不超过 $MAX_ROOT_DIRS 个)"

        if [[ $VERBOSE == true ]]; then
            log_info "根目录目录列表:"
            find . -maxdepth 1 -type d -exec basename {} \; | sort
        fi

        return 1
    else
        log_success "根目录目录数量正常: $dir_count 个目录"
        return 0
    fi
}

# 检查必需文件
check_required_files() {
    local required_files=("README.md" ".gitignore")
    local missing_files=()

    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            missing_files+=("$file")
        fi
    done

    if [[ ${#missing_files[@]} -gt 0 ]]; then
        log_warning "缺少必需文件: ${missing_files[*]}"
        return 1
    else
        log_success "必需文件检查通过"
        return 0
    fi
}

# 检查标准目录结构
check_standard_dirs() {
    local standard_dirs=("src" "docs" "tests" "scripts")
    local missing_dirs=()

    for dir in "${standard_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            missing_dirs+=("$dir")
        fi
    done

    if [[ ${#missing_dirs[@]} -gt 0 ]]; then
        log_warning "缺少标准目录: ${missing_dirs[*]}"
        return 1
    else
        log_success "标准目录结构检查通过"
        return 0
    fi
}

# 检查文件分类
check_file_classification() {
    local issues=0

    # 检查文档文件是否在正确位置
    while IFS= read -r -d '' file; do
        local basename_file
        basename_file=$(basename "$file")

        # 跳过根目录的必需文档文件
        # 包含：项目标识 + 版本控制 + AI辅助工具配置文件
        if [[ "$basename_file" =~ ^(README\.md|LICENSE|CHANGELOG\.md|CLAUDE\.md|GEMINI\.md|IFLOW\.md|AGENTS\.md|\.gitattributes|\.pre-commit-config\.yaml|\.mcp\.json)$ ]]; then
            continue
        fi

        # 其他.md文件应该在docs目录
        if [[ "$basename_file" =~ \.md$ ]] && [[ "$file" != *"/docs/"* ]]; then
            log_warning "文档文件位置不当: $file (建议移到docs目录)"
            issues=$((issues + 1))
        fi

        # 日志文件应该在logs目录
        if [[ "$basename_file" =~ \.log$ ]] && [[ "$file" != *"/logs/"* ]]; then
            log_warning "日志文件位置不当: $file (建议移到logs目录)"
            issues=$((issues + 1))
        fi

    done < <(find . -maxdepth 1 -type f -print0)

    if [[ $issues -gt 0 ]]; then
        log_warning "发现 $issues 个文件分类问题"
        return 1
    else
        log_success "文件分类检查通过"
        return 0
    fi
}

# 自动修复问题
auto_fix_issues() {
    log_info "开始自动修复目录结构问题..."

    # 创建必要的目录
    local dirs_to_create=("temp" "logs" "reports" "data")
    for dir in "${dirs_to_create[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log_success "创建目录: $dir"
        fi
    done

    # 移动临时文件
    local temp_patterns=("*.tmp" "*.temp" "*.cache")
    for pattern in "${temp_patterns[@]}"; do
        while IFS= read -r -d '' file; do
            if [[ -f "$file" ]]; then
                mv "$file" "temp/" 2>/dev/null || true
                log_info "移动临时文件: $file -> temp/"
            fi
        done < <(find . -maxdepth 1 -name "$pattern" -print0)
    done

    # 移动日志文件
    while IFS= read -r -d '' file; do
        if [[ -f "$file" && "$file" != *"/logs/"* ]]; then
            mv "$file" "logs/" 2>/dev/null || true
            log_info "移动日志文件: $file -> logs/"
        fi
    done < <(find . -maxdepth 1 -name "*.log" -print0)

    # 移动报告文件
    local report_patterns=("*report*.json" "*analysis*.json" "*.coverage")
    for pattern in "${report_patterns[@]}"; do
        while IFS= read -r -d '' file; do
            if [[ -f "$file" ]]; then
                mv "$file" "reports/" 2>/dev/null || true
                log_info "移动报告文件: $file -> reports/"
            fi
        done < <(find . -maxdepth 1 -name "$pattern" -print0)
    done

    # 移动文档文件（保留根目录的必需文件）
    while IFS= read -r -d '' file; do
        local basename_file
        basename_file=$(basename "$file")

        if [[ ! "$basename_file" =~ ^(README\.md|LICENSE|CHANGELOG\.md|CLAUDE\.md|GEMINI\.md|IFLOW\.md|AGENTS\.md|\.gitattributes|\.pre-commit-config\.yaml|\.mcp\.json)$ ]]; then
            mkdir -p "docs"
            mv "$file" "docs/" 2>/dev/null || true
            log_info "移动文档文件: $file -> docs/"
        fi
    done < <(find . -maxdepth 1 -name "*.md" -print0)

    # 移动脚本文件
    while IFS= read -r -d '' file; do
        local basename_file
        basename_file=$(basename "$file")

        if [[ "$basename_file" =~ \.(sh|ps1|bat)$ ]] && [[ "$file" != *"/scripts/"* ]]; then
            mkdir -p "scripts"
            mv "$file" "scripts/" 2>/dev/null || true
            log_info "移动脚本文件: $file -> scripts/"
        fi
    done < <(find . -maxdepth 1 -name "*.sh" -print0)

    log_success "自动修复完成"
}

# 生成报告
generate_report() {
    local report_file="directory-structure-report.txt"
    {
        echo "项目目录结构检查报告"
        echo "========================="
        echo "生成时间: $(date)"
        echo "项目路径: $PROJECT_ROOT"
        echo ""

        echo "根目录文件统计:"
        find . -maxdepth 1 -type f | wc -l
        echo ""

        echo "根目录目录统计:"
        find . -maxdepth 1 -type d | wc -l
        echo ""

        echo "按文件类型统计:"
        find . -maxdepth 1 -type f -exec basename {} \; | sed 's/.*\.//' | sort | uniq -c | sort -nr
        echo ""

        echo "大文件列表 (>1MB):"
        find . -maxdepth 1 -type f -size +1M -exec ls -lh {} \; | awk '{print $5, $9}'

    } > "$report_file"

    log_success "报告已生成: $report_file"
}

# 主函数
main() {
    log_info "开始检查项目目录结构..."
    log_info "项目根目录: $PROJECT_ROOT"

    local exit_code=0

    # 执行各项检查
    check_required_files || exit_code=1
    check_root_files || exit_code=1
    check_root_dirs || exit_code=1
    check_standard_dirs || exit_code=1
    check_file_classification || exit_code=1

    # 生成报告
    generate_report

    # 自动修复（如果启用）
    if [[ $AUTO_FIX == true ]]; then
        auto_fix_issues
    fi

    # 输出总结
    echo ""
    if [[ $exit_code -eq 0 ]]; then
        log_success "目录结构检查通过！"
    else
        log_warning "发现一些目录结构问题"
        log_info "可以使用 -f 选项自动修复，或参考 PROJECT_DIRECTORY_STANDARD.md 手动修复"
    fi

    if [[ $QUIET == false ]]; then
        log_info "详细报告请查看: directory-structure-report.txt"
    fi

    return $exit_code
}

# 执行主函数
main
