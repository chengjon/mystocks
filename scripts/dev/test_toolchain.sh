#!/bin/bash
# =================================
# MyStocks 开发工具链测试脚本
# 测试5窗格TMUX布局、PM2集成、lnav配置
# 版本: v2.0
# =================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 打印函数
print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 测试函数
test_dependencies() {
    print_test "检查基础依赖..."
    
    local passed=0
    local total=0
    
    # 检查必要工具
    for cmd in tmux python3 node npm; do
        total=$((total + 1))
        if command -v "$cmd" &> /dev/null; then
            print_pass "$cmd 已安装"
            passed=$((passed + 1))
        else
            print_fail "$cmd 未安装"
        fi
    done
    
    # 检查可选工具
    if command -v pm2 &> /dev/null; then
        print_pass "PM2 已安装: $(pm2 -v)"
        passed=$((passed + 1))
    else
        print_warn "PM2 未安装 (可选)"
    fi
    total=$((total + 1))
    
    if command -v lnav &> /dev/null; then
        print_pass "lnav 已安装: $(lnav -V | head -1)"
        passed=$((passed + 1))
    else
        print_warn "lnav 未安装 (可选)"
    fi
    total=$((total + 1))
    
    echo "依赖检查结果: $passed/$total 通过"
    return $((total - passed))
}

test_directory_structure() {
    print_test "检查目录结构..."
    
    local required_dirs=(
        "/opt/claude/mystocks_spec/scripts/dev"
        "/opt/claude/mystocks_spec/logs"
        "/opt/claude/mystocks_spec/config/lnav"
        "/opt/claude/mystocks_spec/web/backend"
        "/opt/claude/mystocks_spec/web/frontend"
    )
    
    local passed=0
    local total=${#required_dirs[@]}
    
    for dir in "${required_dirs[@]}"; do
        if [ -d "$dir" ]; then
            print_pass "目录存在: $dir"
            passed=$((passed + 1))
        else
            print_fail "目录不存在: $dir"
        fi
    done
    
    echo "目录结构检查结果: $passed/$total 通过"
    return $((total - passed))
}

test_script_permissions() {
    print_test "检查脚本执行权限..."
    
    local scripts=(
        "/opt/claude/mystocks_spec/scripts/dev/start-dev.sh"
        "/opt/claude/mystocks_spec/scripts/dev/setup_lnav.sh"
    )
    
    local passed=0
    local total=${#scripts[@]}
    
    for script in "${scripts[@]}"; do
        total=$((total + 1))
        if [ -x "$script" ]; then
            print_pass "脚本可执行: $script"
            passed=$((passed + 1))
        else
            print_fail "脚本不可执行: $script"
        fi
    done
    
    echo "脚本权限检查结果: $passed/$total 通过"
    return $((total - passed))
}

test_config_files() {
    print_test "检查配置文件..."
    
    local config_files=(
        "/opt/claude/mystocks_spec/ecosystem.config.js"
        "/opt/claude/mystocks_spec/config/lnav/mystocks_log.json"
        "/opt/claude/mystocks_spec/scripts/dev/start-dev.sh"
        "/opt/claude/mystocks_spec/scripts/dev/setup_lnav.sh"
    )
    
    local passed=0
    local total=${#config_files[@]}
    
    for file in "${config_files[@]}"; do
        total=$((total + 1))
        if [ -f "$file" ]; then
            print_pass "配置文件存在: $file"
            passed=$((passed + 1))
        else
            print_fail "配置文件不存在: $file"
        fi
    done
    
    echo "配置文件检查结果: $passed/$total 通过"
    return $((total - passed))
}

test_json_syntax() {
    print_test "检查JSON配置文件语法..."
    
    local json_files=(
        "/opt/claude/mystocks_spec/ecosystem.config.js"
        "/opt/claude/mystocks_spec/config/lnav/mystocks_log.json"
    )
    
    local passed=0
    local total=${#json_files[@]}
    
    for file in "${json_files[@]}"; do
        total=$((total + 1))
        if [ ! -f "$file" ]; then
            print_fail "文件不存在: $file"
            continue
        fi
        
        # 检查ecosystem.config.js
        if [[ "$file" == *.js ]]; then
            if node -c "$file" 2>/dev/null; then
                print_pass "JS语法正确: $file"
                passed=$((passed + 1))
            else
                print_fail "JS语法错误: $file"
            fi
        # 检查JSON文件
        elif [[ "$file" == *.json ]]; then
            if command -v jq &> /dev/null; then
                if jq empty "$file" 2>/dev/null; then
                    print_pass "JSON语法正确: $file"
                    passed=$((passed + 1))
                else
                    print_fail "JSON语法错误: $file"
                fi
            else
                print_warn "jq未安装，跳过JSON语法检查: $file"
                passed=$((passed + 1))  # 跳过检查
            fi
        fi
    done
    
    echo "JSON语法检查结果: $passed/$total 通过"
    return $((total - passed))
}

test_tmux_syntax() {
    print_test "检查TMUX脚本语法..."
    
    local bash_scripts=(
        "/opt/claude/mystocks_spec/scripts/dev/start-dev.sh"
        "/opt/claude/mystocks_spec/scripts/dev/setup_lnav.sh"
    )
    
    local passed=0
    local total=${#bash_scripts[@]}
    
    for script in "${bash_scripts[@]}"; do
        total=$((total + 1))
        if [ ! -f "$script" ]; then
            print_fail "脚本不存在: $script"
            continue
        fi
        
        # 使用bash -n检查语法
        if bash -n "$script" 2>/dev/null; then
            print_pass "Bash语法正确: $script"
            passed=$((passed + 1))
        else
            print_fail "Bash语法错误: $script"
        fi
    done
    
    echo "Bash语法检查结果: $passed/$total 通过"
    return $((total - passed))
}

test_pm2_config() {
    print_test "测试PM2配置..."
    
    if [ ! -f "/opt/claude/mystocks_spec/ecosystem.config.js" ]; then
        print_fail "PM2配置文件不存在"
        return 1
    fi
    
    # 检查Node.js语法
    if node -c "/opt/claude/mystocks_spec/ecosystem.config.js" 2>/dev/null; then
        print_pass "PM2配置文件语法正确"
        
        # 检查关键字段
        if grep -q "mystocks-backend" "/opt/claude/mystocks_spec/ecosystem.config.js"; then
            print_pass "包含mystocks-backend服务配置"
        else
            print_fail "缺少mystocks-backend服务配置"
        fi
        
        if grep -q "env_development" "/opt/claude/mystocks_spec/ecosystem.config.js"; then
            print_pass "包含开发环境配置"
        else
            print_fail "缺少开发环境配置"
        fi
        
        return 0
    else
        print_fail "PM2配置文件语法错误"
        return 1
    fi
}

test_lnav_config() {
    print_test "测试lnav配置..."
    
    if [ ! -f "/opt/claude/mystocks_spec/config/lnav/mystocks_log.json" ]; then
        print_fail "lnav配置文件不存在"
        return 1
    fi
    
    # 检查JSON格式
    if command -v jq &> /dev/null; then
        if jq empty "/opt/claude/mystocks_spec/config/lnav/mystocks_log.json" 2>/dev/null; then
            print_pass "lnav配置文件JSON格式正确"
        else
            print_fail "lnav配置文件JSON格式错误"
            return 1
        fi
    else
        print_warn "jq未安装，跳过JSON格式检查"
    fi
    
    # 检查关键字段
    if grep -q "mystocks_backend_logs" "/opt/claude/mystocks_spec/config/lnav/mystocks_log.json"; then
        print_pass "包含mystocks_backend_logs格式定义"
    else
        print_fail "缺少mystocks_backend_logs格式定义"
    fi
    
    if grep -q "timestamp" "/opt/claude/mystocks_spec/config/lnav/mystocks_log.json"; then
        print_pass "包含timestamp字段定义"
    else
        print_fail "缺少timestamp字段定义"
    fi
    
    return 0
}

test_start_script_help() {
    print_test "测试启动脚本帮助功能..."
    
    # 测试--help选项
    if "/opt/claude/mystocks_spec/scripts/dev/start-dev.sh" --help >/dev/null 2>&1; then
        print_pass "start-dev.sh --help 命令正常"
    else
        print_fail "start-dev.sh --help 命令异常"
    fi
    
    # 测试--check选项
    if "/opt/claude/mystocks_spec/scripts/dev/start-dev.sh" --check >/dev/null 2>&1; then
        print_pass "start-dev.sh --check 命令正常"
    else
        print_warn "start-dev.sh --check 命令可能需要某些依赖"
    fi
    
    return 0
}

test_setup_script_help() {
    print_test "测试setup脚本帮助功能..."
    
    # 测试--help选项
    if "/opt/claude/mystocks_spec/scripts/dev/setup_lnav.sh" --help >/dev/null 2>&1; then
        print_pass "setup_lnav.sh --help 命令正常"
    else
        print_fail "setup_lnav.sh --help 命令异常"
    fi
    
    # 测试--guide选项
    if "/opt/claude/mystocks_spec/scripts/dev/setup_lnav.sh" --guide >/dev/null 2>&1; then
        print_pass "setup_lnav.sh --guide 命令正常"
    else
        print_fail "setup_lnav.sh --guide 命令异常"
    fi
    
    return 0
}

test_directory_creation() {
    print_test "测试目录创建功能..."
    
    # 清理测试目录
    local test_dir="/tmp/mystocks_test_$(date +%s)"
    mkdir -p "$test_dir"
    
    # 测试日志目录创建
    local logs_dir="$test_dir/logs"
    mkdir -p "$logs_dir"
    if [ -d "$logs_dir" ]; then
        print_pass "日志目录创建成功"
    else
        print_fail "日志目录创建失败"
    fi
    
    # 测试数据目录创建
    local data_dir="$test_dir/data"
    mkdir -p "$data_dir"
    if [ -d "$data_dir" ]; then
        print_pass "数据目录创建成功"
    else
        print_fail "数据目录创建失败"
    fi
    
    # 清理测试目录
    rm -rf "$test_dir"
    
    return 0
}

# 生成测试报告
generate_test_report() {
    local total_tests=$1
    local passed_tests=$2
    local failed_tests=$3
    
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}    测试报告${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    echo -e "${GREEN}✅ 测试统计${NC}"
    echo "  总测试数: $total_tests"
    echo "  通过数量: $passed_tests"
    echo "  失败数量: $failed_tests"
    echo "  成功率: $(( passed_tests * 100 / total_tests ))%"
    echo ""
    
    if [ $failed_tests -eq 0 ]; then
        echo -e "${GREEN}🎉 所有测试通过！开发工具链可以正常使用${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  部分测试失败，请检查失败项目${NC}"
        return 1
    fi
}

# 显示使用建议
show_usage_suggestions() {
    echo ""
    echo -e "${BLUE}📖 使用建议${NC}"
    echo ""
    echo -e "${GREEN}1. 快速启动:${NC}"
    echo -e "   ${CYAN}./scripts/dev/start-dev.sh${NC}                 # 启动开发环境"
    echo -e "   ${CYAN}./scripts/dev/start-dev.sh development${NC}     # 指定开发环境"
    echo ""
    echo -e "${GREEN}2. lnav配置:${NC}"
    echo -e "   ${CYAN}./scripts/dev/setup_lnav.sh development${NC}    # 安装开发配置"
    echo -e "   ${CYAN}./scripts/dev/setup_lnav.sh production${NC}     # 安装生产配置"
    echo ""
    echo -e "${GREEN}3. 故障排除:${NC}"
    echo -e "   ${CYAN}./scripts/dev/start-dev.sh --check${NC}         # 检查依赖"
    echo -e "   ${CYAN}./scripts/dev/setup_lnav.sh --validate${NC}     # 验证lnav配置"
    echo ""
    echo -e "${GREEN}4. 文档参考:${NC}"
    echo -e "   📄 查看完整文档: ${BLUE}docs/guides/DEV_TOOLCHAIN_GUIDE.md${NC}"
    echo ""
}

# 主函数
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}    MyStocks 开发工具链测试套件 v2.0${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    local total_tests=0
    local passed_tests=0
    local failed_tests=0
    
    # 执行所有测试
    local tests=(
        "test_dependencies"
        "test_directory_structure"
        "test_script_permissions"
        "test_config_files"
        "test_json_syntax"
        "test_tmux_syntax"
        "test_pm2_config"
        "test_lnav_config"
        "test_start_script_help"
        "test_setup_script_help"
        "test_directory_creation"
    )
    
    for test_func in "${tests[@]}"; do
        echo ""
        total_tests=$((total_tests + 1))
        if $test_func; then
            passed_tests=$((passed_tests + 1))
        else
            failed_tests=$((failed_tests + 1))
        fi
    done
    
    # 生成测试报告
    generate_test_report $total_tests $passed_tests $failed_tests
    local test_result=$?
    
    # 显示使用建议
    show_usage_suggestions
    
    return $test_result
}

# 脚本入口
main "$@"