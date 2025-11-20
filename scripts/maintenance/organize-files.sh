#!/bin/bash
# 项目文件自动整理脚本
# 用法: ./scripts/maintenance/organize-files.sh [项目根目录] [--dry-run]

set -euo pipefail

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${1:-"$(cd "$SCRIPT_DIR/../.." && pwd)"}"
DRY_RUN="${2:-""}"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

log_dry_run() {
    echo -e "${CYAN}[DRY-RUN]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
项目文件自动整理工具

用法:
    $0 [选项] [项目根目录]

选项:
    -h, --help              显示此帮助信息
    -n, --dry-run           试运行模式，只显示将要执行的操作
    -v, --verbose           详细输出

参数:
    项目根目录              项目根目录路径（默认为当前目录的上上级）

示例:
    $0                      整理当前项目的文件
    $0 -n                   试运行模式
    $0 -v /path/to/project  详细整理指定项目

EOF
}

# 解析命令行参数
VERBOSE=false
DRY_RUN_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -n|--dry-run)
            DRY_RUN_MODE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
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

# 如果第二个参数是--dry-run
if [[ "${DRY_RUN:-}" == "--dry-run" ]]; then
    DRY_RUN_MODE=true
fi

# 检查项目根目录是否存在
if [[ ! -d "$PROJECT_ROOT" ]]; then
    log_error "项目根目录不存在: $PROJECT_ROOT"
    exit 1
fi

# 切换到项目根目录
cd "$PROJECT_ROOT"

# 创建目录函数
create_directory() {
    local dir="$1"
    if [[ ! -d "$dir" ]]; then
        if [[ $DRY_RUN_MODE == true ]]; then
            log_dry_run "创建目录: $dir"
        else
            mkdir -p "$dir"
            log_success "创建目录: $dir"
        fi
    fi
}

# 移动文件函数
move_file() {
    local source="$1"
    local target_dir="$2"
    local filename=$(basename "$source")
    
    if [[ ! -f "$source" ]]; then
        log_warning "文件不存在: $source"
        return 1
    fi
    
    create_directory "$target_dir"
    local target="$target_dir/$filename"
    
    # 处理文件名冲突
    local counter=1
    local base_name="${filename%.*}"
    local extension="${filename##*.}"
    
    if [[ "$base_name" == "$extension" ]]; then
        # 没有扩展名
        base_name="$filename"
        extension=""
    fi
    
    while [[ -e "$target" ]]; do
        if [[ -n "$extension" ]]; then
            target="$target_dir/${base_name}_${counter}.${extension}"
        else
            target="$target_dir/${base_name}_${counter}"
        fi
        counter=$((counter + 1))
    done
    
    if [[ $DRY_RUN_MODE == true ]]; then
        log_dry_run "移动文件: $source -> $target"
    else
        mv "$source" "$target"
        log_success "移动文件: $source -> $target"
    fi
}

# 文件类型分类规则
classify_file() {
    local filename="$1"
    
    # 获取文件扩展名
    local ext="${filename##*.}"
    
    # 临时文件
    if [[ "$filename" =~ \.(tmp|temp|cache|bak|backup)$ ]] || [[ "$filename" =~ ~$ ]]; then
        echo "temp"
        return 0
    fi
    
    # 日志文件
    if [[ "$filename" =~ \.log$ ]]; then
        echo "logs"
        return 0
    fi
    
    # 报告和分析文件
    if [[ "$filename" =~ (report|analysis|assessment|metrics)$ ]] && [[ "$filename" =~ \.(json|xml|html)$ ]]; then
        echo "reports"
        return 0
    fi
    
    # 测试覆盖率文件
    if [[ "$filename" =~ \.(coverage|htmlcov)$ ]]; then
        echo "reports/coverage"
        return 0
    fi
    
    # 文档文件（保留根目录特定文件）
    if [[ "$ext" =~ ^(md|rst|txt)$ ]]; then
        # 检查是否是根目录需要保留的文件
        case "$filename" in
            README.md|LICENSE|CHANGELOG.md|CONTRIBUTING.md)
                echo "keep_root"
                return 0
                ;;
        esac
        echo "docs"
        return 0
    fi
    
    # 脚本文件
    if [[ "$ext" =~ ^(sh|ps1|bat)$ ]]; then
        echo "scripts"
        return 0
    fi
    
    # Python相关文件
    if [[ "$ext" == "py" ]]; then
        # 检查是否是配置文件
        case "$filename" in
            setup.py|pyproject.toml|requirements*.txt|Pipfile|Makefile)
                echo "keep_root"
                return 0
                ;;
        esac
        # 其他Python文件可能在src或tools中，但不在根目录整理
        echo "keep_root"
        return 0
    fi
    
    # 配置文件
    if [[ "$ext" =~ ^(json|yaml|yml|ini|cfg|conf)$ ]]; then
        case "$filename" in
            package.json|tsconfig.json|jest.config.js|.eslintrc.*|.prettierrc|Dockerfile|docker-compose*.yml)
                echo "keep_root"
                return 0
                ;;
            *)
                echo "config"
                return 0
                ;;
        esac
    fi
    
    # 依赖文件
    if [[ "$filename" =~ ^(requirements.*\.txt|Pipfile.*|package-lock\.json|yarn\.lock)$ ]]; then
        echo "keep_root"
        return 0
    fi
    
    # 其他文件保留在根目录
    echo "keep_root"
}

# 执行整理操作
organize_files() {
    log_info "开始整理项目文件..."
    
    # 创建基本目录结构
    local dirs=(
        "temp/cache"
        "logs/app"
        "reports/metrics"
        "reports/analysis"
        "reports/coverage"
        "docs/guides"
        "scripts/dev"
        "scripts/deploy"
        "scripts/maintenance"
        "data/raw"
        "data/processed"
        "config"
    )
    
    for dir in "${dirs[@]}"; do
        create_directory "$dir"
    done
    
    # 统计信息
    local total_files=0
    local moved_files=0
    local kept_files=0
    
    # 处理根目录文件
    while IFS= read -r -d '' file; do
        local filename
        filename=$(basename "$file")
        total_files=$((total_files + 1))
        
        # 获取文件分类
        local category
        category=$(classify_file "$filename")
        
        case "$category" in
            "keep_root")
                kept_files=$((kept_files + 1))
                if [[ $VERBOSE == true ]]; then
                    log_info "保留在根目录: $filename"
                fi
                ;;
            *)
                move_file "$file" "$category"
                moved_files=$((moved_files + 1))
                ;;
        esac
        
    done < <(find . -maxdepth 1 -type f -print0)
    
    # 特殊处理：移动深层的临时文件
    find . -mindepth 2 -maxdepth 2 -name "*.tmp" -o -name "*.temp" -o -name "*.cache" | while read -r file; do
        move_file "$file" "temp/cache"
        moved_files=$((moved_files + 1))
    done
    
    # 移动深层的日志文件
    find . -mindepth 2 -maxdepth 3 -name "*.log" | while read -r file; do
        move_file "$file" "logs/app"
        moved_files=$((moved_files + 1))
    done
    
    # 输出统计信息
    echo ""
    log_info "整理完成统计:"
    log_info "  总文件数: $total_files"
    log_info "  移动文件数: $moved_files"
    log_info "  保留文件数: $kept_files"
    
    if [[ $DRY_RUN_MODE == true ]]; then
        log_warning "这是试运行模式，没有实际移动文件"
    fi
}

# 清理空目录
clean_empty_dirs() {
    log_info "清理空目录..."
    
    # 查找并删除空目录（排除隐藏目录）
    find . -mindepth 1 -type d -empty -not -path './.*' | while read -r dir; do
        if [[ $DRY_RUN_MODE == true ]]; then
            log_dry_run "删除空目录: $dir"
        else
            rmdir "$dir" 2>/dev/null || true
            log_success "删除空目录: $dir"
        fi
    done
}

# 生成整理报告
generate_organization_report() {
    local report_file="file-organization-report.txt"
    {
        echo "项目文件整理报告"
        echo "==================="
        echo "生成时间: $(date)"
        echo "项目路径: $PROJECT_ROOT"
        echo "模式: $([[ $DRY_RUN_MODE == true ]] && echo "试运行" || echo "实际执行")"
        echo ""
        
        echo "目录结构:"
        tree -L 3 -I '__pycache__|*.pyc|node_modules|.git' . || find . -type d | head -20
        echo ""
        
        echo "文件分类统计:"
        find . -type f -exec sh -c '
            ext="${1##*.}"
            if [[ "$1" == */* ]]; then
                dir="${1%/*}"
            else
                dir="."
            fi
            echo "$dir|$ext"
        ' _ {} \; | sort | uniq -c | sort -nr | head -20
        
    } > "$report_file"
    
    log_success "整理报告已生成: $report_file"
}

# 主函数
main() {
    log_info "开始项目文件整理..."
    log_info "项目根目录: $PROJECT_ROOT"
    
    if [[ $DRY_RUN_MODE == true ]]; then
        log_warning "试运行模式：只显示操作，不实际执行"
    fi
    
    # 执行整理
    organize_files
    clean_empty_dirs
    generate_organization_report
    
    # 输出建议
    echo ""
    if [[ $DRY_RUN_MODE == false ]]; then
        log_success "文件整理完成！"
        log_info "建议下一步操作:"
        log_info "  1. 检查移动的文件是否正确"
        log_info "  2. 更新配置文件中的路径"
        log_info "  3. 运行测试确保功能正常"
        log_info "  4. 提交更改到版本控制系统"
    else
        log_info "试运行完成，使用实际参数重新运行以执行整理"
    fi
}

# 执行主函数
main