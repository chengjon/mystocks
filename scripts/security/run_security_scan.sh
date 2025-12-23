#!/bin/bash
# MyStocks项目安全扫描执行脚本
# 集成多种安全扫描工具，提供全面的安全检测

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_ROOT/venv_security"

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

# 创建安全扫描虚拟环境
setup_security_environment() {
    log_info "设置安全扫描环境..."

    # 创建虚拟环境
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        log_success "创建安全扫描虚拟环境"
    fi

    # 激活虚拟环境
    source "$VENV_DIR/bin/activate"

    # 升级pip
    pip install --upgrade pip

    # 安装安全工具
    if [ -f "$PROJECT_ROOT/requirements-security.txt" ]; then
        pip install -r "$PROJECT_ROOT/requirements-security.txt"
        log_success "安装安全扫描工具完成"
    else
        log_error "安全工具依赖文件不存在: requirements-security.txt"
        exit 1
    fi
}

# 检查必要工具
check_security_tools() {
    log_info "检查安全扫描工具..."

    local tools=("bandit" "safety" "pip-audit")
    local missing_tools=()

    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done

    if [ ${#missing_tools[@]} -gt 0 ]; then
        log_error "缺少安全扫描工具: ${missing_tools[*]}"
        log_info "尝试安装缺少的工具..."
        setup_security_environment
    else
        log_success "所有安全扫描工具已安装"
    fi
}

# 运行Bandit代码安全分析
run_bandit_scan() {
    log_info "运行Bandit代码安全分析..."

    local output_file="$PROJECT_ROOT/logs/security/bandit_report.json"
    mkdir -p "$(dirname "$output_file")"

    if bandit -r "$PROJECT_ROOT/src" \
              --exclude "*/test*,*/tests,*/__pycache__,*/venv/*,*/node_modules/*" \
              --format json \
              --output "$output_file" \
              --quiet; then
        log_success "Bandit扫描完成"
    else
        log_warning "Bandit扫描发现问题"
    fi
}

# 运行Safety依赖漏洞扫描
run_safety_scan() {
    log_info "运行Safety依赖漏洞扫描..."

    local output_file="$PROJECT_ROOT/logs/security/safety_report.json"
    mkdir -p "$(dirname "$output_file")"

    if safety check --json --full-report --output "$output_file"; then
        log_success "Safety扫描完成 - 未发现已知漏洞"
    else
        log_warning "Safety扫描发现依赖漏洞"
    fi
}

# 运行pip-audit包安全审计
run_pip_audit_scan() {
    log_info "运行pip-audit包安全审计..."

    local output_file="$PROJECT_ROOT/logs/security/pip_audit_report.json"
    mkdir -p "$(dirname "$output_file")"

    if pip-audit --format=json --local --output "$output_file"; then
        log_success "pip-audit扫描完成 - 未发现包安全漏洞"
    else
        log_warning "pip-audit扫描发现包安全漏洞"
    fi
}

# 运行综合安全扫描
run_comprehensive_security_scan() {
    log_info "开始运行综合安全扫描..."

    local scanner_script="$SCRIPT_DIR/security_scanner.py"

    if [ -f "$scanner_script" ]; then
        python3 "$scanner_script" --project-root "$PROJECT_ROOT" --quiet
        log_success "综合安全扫描完成"
    else
        log_error "安全扫描脚本不存在: $scanner_script"
        return 1
    fi
}

# 生成安全报告摘要
generate_security_summary() {
    log_info "生成安全报告摘要..."

    local log_dir="$PROJECT_ROOT/logs/security"
    local summary_file="$log_dir/security_summary_$(date +%Y%m%d_%H%M%S).txt"

    echo "MyStocks项目安全扫描摘要报告" > "$summary_file"
    echo "生成时间: $(date)" >> "$summary_file"
    echo "======================================" >> "$summary_file"
    echo "" >> "$summary_file"

    # 扫描HTML报告
    local html_reports=($(find "$log_dir" -name "security_report_*.html" -type f 2>/dev/null | sort -r | head -1))
    if [ ${#html_reports[@]} -gt 0 ]; then
        echo "最新HTML安全报告:" >> "$summary_file"
        echo "  - ${html_reports[0]}" >> "$summary_file"
    fi

    # 扫描JSON报告
    local json_reports=($(find "$log_dir" -name "security_scan_*.json" -type f 2>/dev/null | sort -r | head -1))
    if [ ${#json_reports[@]} -gt 0 ]; then
        echo "最新JSON安全报告:" >> "$summary_file"
        echo "  - ${json_reports[0]}" >> "$summary_file"
    fi

    # 显示摘要
    echo "" >> "$summary_file"
    echo "请查看上述报告文件获取详细的安全扫描结果。" >> "$summary_file"

    log_success "安全报告摘要已生成: $summary_file"
    cat "$summary_file"
}

# 显示帮助信息
show_help() {
    echo "MyStocks项目安全扫描执行脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --setup          设置安全扫描环境"
    echo "  --check          检查安全工具"
    echo "  --bandit         运行Bandit代码安全分析"
    echo "  --safety         运行Safety依赖漏洞扫描"
    echo "  --pip-audit      运行pip-audit包安全审计"
    echo "  --full           运行所有安全扫描"
    echo "  --summary        生成安全报告摘要"
    echo "  --help           显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --full                    # 运行完整安全扫描"
    echo "  $0 --bandit --safety         # 只运行特定工具"
    echo "  $0 --setup                   # 设置环境"
}

# 主函数
main() {
    local mode="$1"

    case "$mode" in
        --setup)
            setup_security_environment
            ;;
        --check)
            check_security_tools
            ;;
        --bandit)
            check_security_tools
            run_bandit_scan
            ;;
        --safety)
            check_security_tools
            run_safety_scan
            ;;
        --pip-audit)
            check_security_tools
            run_pip_audit_scan
            ;;
        --full)
            check_security_tools
            run_comprehensive_security_scan
            generate_security_summary
            ;;
        --summary)
            generate_security_summary
            ;;
        --help|*)
            show_help
            ;;
    esac
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
