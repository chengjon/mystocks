#!/bin/bash

# MyStocks 本地CI检查脚本
# 用于开发阶段的快速质量验证

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 检查Python环境
check_python() {
    log_info "检查Python环境..."

    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi

    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [[ "$PYTHON_VERSION" != "3.1"* ]] && [[ "$PYTHON_VERSION" != "3.2"* ]]; then
        log_warning "建议使用Python 3.12+, 当前版本: $PYTHON_VERSION"
    fi

    log_success "Python环境检查通过"
}

# 快速代码格式检查
check_code_format() {
    log_info "检查代码格式..."

    # 检查Black格式 (如果安装了)
    if command -v black &> /dev/null; then
        log_info "运行Black格式检查..."
        if ! black --check --quiet src/ web/backend/app/ 2>/dev/null; then
            log_error "代码格式不符合Black规范，请运行: black src/ web/backend/app/"
            log_info "或者运行: ./scripts/cicd_pipeline.sh --fix-format"
            exit 1
        fi
        log_success "Black格式检查通过"
    else
        log_warning "Black未安装，跳过格式检查"
    fi
}

# 快速类型检查 (简化版)
check_types_quick() {
    log_info "快速类型检查..."

    # 只检查关键文件，避免全量检查时间过长
    KEY_FILES=(
        "src/core/*.py"
        "src/data_access/*.py"
        "web/backend/app/main.py"
        "web/backend/app/core/*.py"
    )

    if command -v mypy &> /dev/null; then
        log_info "运行MyPy类型检查(快速模式)..."
        for pattern in "${KEY_FILES[@]}"; do
            if compgen -G "$pattern" > /dev/null; then
                if ! mypy --ignore-missing-imports --no-error-summary $pattern 2>/dev/null; then
                    log_warning "类型检查发现问题: $pattern (详细检查请运行完整CI)"
                fi
            fi
        done
        log_success "快速类型检查完成"
    else
        log_warning "MyPy未安装，跳过类型检查"
    fi
}

# 快速安全检查
check_security_quick() {
    log_info "快速安全检查..."

    if command -v bandit &> /dev/null; then
        log_info "运行Bandit安全检查(快速模式)..."

        # 只检查新增/修改的文件
        if git diff --cached --name-only | grep -E '\.py$' | head -5 | xargs bandit -r 2>/dev/null | grep -q "No issues identified"; then
            log_success "安全检查通过"
        else
            log_warning "发现潜在安全问题 (详细检查请运行完整CI)"
        fi
    else
        log_warning "Bandit未安装，跳过安全检查"
    fi
}

# 快速单元测试
run_unit_tests_quick() {
    log_info "运行快速单元测试..."

    if command -v pytest &> /dev/null; then
        log_info "运行核心单元测试..."

        # 只运行核心模块的单元测试，限制时间
        timeout 60 pytest tests/unit/test_*.py -x -q --tb=line --disable-warnings || {
            log_warning "单元测试失败 (详细测试请运行完整CI)"
            exit 1
        }

        log_success "快速单元测试通过"
    else
        log_warning "pytest未安装，跳过单元测试"
    fi
}

# 检查配置文件
check_config_files() {
    log_info "检查配置文件..."

    # 检查关键配置文件是否存在
    REQUIRED_FILES=(
        "pyproject.toml"
        "requirements.txt"
        "web/backend/requirements.txt"
    )

    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "缺少关键配置文件: $file"
            exit 1
        fi
    done

    log_success "配置文件检查通过"
}

# 检查量化策略文件 (MyStocks特色)
check_quantum_strategies() {
    log_info "检查量化策略文件..."

    # 检查策略目录结构
    if [ -d "src/strategies" ]; then
        STRATEGY_COUNT=$(find src/strategies -name "*.py" -type f | wc -l)
        log_info "发现 $STRATEGY_COUNT 个策略文件"

        # 简单语法检查
        if ! python3 -m py_compile src/strategies/*.py 2>/dev/null; then
            log_warning "策略文件语法检查失败"
        else
            log_success "策略文件语法检查通过"
        fi
    else
        log_warning "未发现策略目录"
    fi
}

# 主函数
main() {
    log_info "开始MyStocks本地CI检查..."
    START_TIME=$(date +%s)

    # 执行各项检查
    check_python
    check_config_files
    check_code_format
    check_types_quick
    check_security_quick
    check_quantum_strategies
    run_unit_tests_quick

    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))

    log_success "本地CI检查完成，耗时: ${DURATION}秒"
    log_info "💡 提示: 这是一个快速检查，要运行完整CI请执行: ./scripts/cicd_pipeline.sh"
}

# 如果脚本被直接运行，则执行主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main
fi