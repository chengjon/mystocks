#!/bin/bash
# MyStocks Ralph-Wiggum测试循环管理脚本
# 版本: 1.0
# 创建日期: 2026-01-27

set -e

# 项目根目录
PROJECT_ROOT="/opt/claude/mystocks_spec"
cd "$PROJECT_ROOT"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_section() {
    echo -e "${BLUE}=== $1 ====${NC}"
}

# 配置
PM2_CONFIG_FILE="$PROJECT_ROOT/ecosystem.enhanced.config.js"
FRONTEND_PORT=3002
BACKEND_PORT=8000
TEST_LOG_DIR="$PROJECT_ROOT/tests/logs"
FRONTEND_LOG_DIR="$PROJECT_ROOT/web/frontend/logs"
BACKEND_LOG_DIR="$PROJECT_ROOT/web/backend/logs"

# 确保日志目录存在
mkdir -p "$TEST_LOG_DIR"
mkdir -p "$FRONTEND_LOG_DIR"
mkdir -p "$BACKEND_LOG_DIR"

# 步骤1: 启动PM2服务
start_pm2_services() {
    log_section "步骤1: 启动PM2服务"
    
    log_info "检查PM2是否已安装..."
    if ! command -v pm2 &> /dev/null; then
        log_error "PM2未安装，请先安装：npm install -g pm2"
        exit 1
    fi
    
    log_info "启动增强版PM2配置..."
    pm2 start "$PM2_CONFIG_FILE" || pm2 restart all
    
    # 等待服务启动
    log_info "等待服务启动（30秒）..."
    sleep 30
    
    # 检查服务状态
    log_info "检查服务状态..."
    pm2 list
    
    # 验证前端服务
    log_info "检查前端服务（端口 $FRONTEND_PORT）..."
    if curl -s "http://localhost:$FRONTEND_PORT" > /dev/null 2>&1; then
        log_info "✅ 前端服务运行正常"
    else
        log_error "❌ 前端服务无法访问"
        return 1
    fi
    
    # 验证后端服务
    log_info "检查后端服务（端口 $BACKEND_PORT）..."
    if curl -s "http://localhost:$BACKEND_PORT/health" > /dev/null 2>&1; then
        log_info "✅ 后端服务运行正常"
    else
        log_error "❌ 后端服务无法访问"
        return 1
    fi
}

# 步骤2: 创建tmux测试会话
create_test_session() {
    log_section "步骤2: 创建tmux测试会话"
    
    local SESSION_NAME="mystocks-test"
    
    # 检查会话是否已存在
    if tmux has-session -t $SESSION_NAME 2>/dev/null; then
        log_warn "会话 $SESSION_NAME 已存在，将删除后重建"
        tmux kill-session -t $SESSION_NAME 2>/dev/null || true
    fi
    
    # 创建测试会话
    log_info "创建测试会话: $SESSION_NAME"
    tmux new-session -d -s $SESSION_NAME -c "$PROJECT_ROOT"
    
    # 窗口1: PM2管理和状态
    tmux new-window -t $SESSION_NAME -n pm2 -c "$PROJECT_ROOT"
    tmux send-keys -t $SESSION_NAME:pm2.0 "echo 'PM2应用管理面板'; echo '执行: pm2 list'; echo '监控: pm2 monit'; echo '日志: pm2 logs'" C-m
    
    # 窗口2: Playwright测试执行
    tmux new-window -t $SESSION_NAME -n playwright -c "$PROJECT_ROOT"
    tmux send-keys -t $SESSION_NAME:playwright.0 "echo 'Playwright自动化测试'; echo '执行: npm run test:e2e'; echo '监控: 实时测试进度'" C-m
    
    # 窗口3: lnav日志分析
    tmux new-window -t $SESSION_NAME -n lnav -c "$PROJECT_ROOT"
    tmux send-keys -t $SESSION_NAME:lnav.0 "echo 'lnav日志分析面板'; echo '前端日志: $FRONTEND_LOG_DIR'; echo '后端日志: $BACKEND_LOG_DIR'; echo '测试日志: $TEST_LOG_DIR'" C-m
    tmux send-keys -t $SESSION_NAME:lnav.1 "echo '快速命令:'; echo '  lnav -c $FRONTEND_LOG_DIR/*'; echo '  lnav -c $BACKEND_LOG_DIR/*'; echo '  lnav -c $TEST_LOG_DIR/*'" C-m
    
    # 窗口4: Chrome MCP调试（如果可用）
    tmux new-window -t $SESSION_NAME -n debug -c "$PROJECT_ROOT"
    tmux send-keys -t $SESSION_NAME:debug.0 "echo 'Chrome DevTools MCP调试面板'; echo '功能: 深度调试 / 根因定位'; echo '命令: 链接到Chrome远程调试'" C-m
    
    # 窗口5: 数据库和Socket.IO监控
    tmux new-window -t $SESSION_NAME -n database -c "$PROJECT_ROOT"
    tmux send-keys -t $SESSION_NAME:database.0 "echo '数据库和Socket.IO监控'; echo 'TDengine: docker stats mystocks-tdengine'; echo 'PostgreSQL: docker stats mystocks-postgresql'; echo 'WebSocket: 检查Socket.IO连接'" C-m
    
    log_info "✅ 测试会话创建完成"
    log_info "会话包含以下窗口:"
    log_info "  1. PM2管理 - 应用进程管理"
    log_info "  2. Playwright测试 - 自动化测试执行"
    log_info "  3. lnav日志分析 - 实时日志分析"
    log_info "  4. Chrome调试 - 深度调试工具"
    log_info "  5. 数据库监控 - 数据库和WebSocket状态"
}

# 步骤3: 运行Playwright测试
run_playwright_tests() {
    log_section "步骤3: 运行Playwright端到端测试"
    
    log_info "切换到Playwright测试窗口..."
    tmux select-window -t mystocks-test:playwright
    
    log_info "执行测试套件..."
    
    # 定义测试命令
    local test_command="cd $PROJECT_ROOT && npm run test:e2e"
    
    # 在tmux窗口中执行测试
    tmux send-keys -t mystocks-test:playwright.0 "$test_command" C-m
    
    log_info "测试正在执行中..."
    log_info "请查看tmux窗口2中的测试进度"
}

# 步骤4: lnav实时日志分析
lnav_log_analysis() {
    log_section "步骤4: lnav实时日志分析"
    
    log_info "切换到lnav日志分析窗口..."
    tmux select-window -t mystocks-test:lnav
    
    log_info "启动lnav日志分析..."
    
    # 启动lnav聚合分析
    local lnav_command="lnav -c '$FRONTEND_LOG_DIR/*' -c '$BACKEND_LOG_DIR/*' -c '$TEST_LOG_DIR/*'"
    
    tmux send-keys -t mystocks-test:lnav.2 "$lnav_command" C-m
    
    log_info "lnav正在分析日志..."
    log_info "支持的lnav命令:"
    log_info "  :filter-in <pattern> - 筛选日志"
    log_info "  :filter-out <pattern> - 排除日志"
    log_info "  :stats - 显示统计信息"
    log_info "  :db <sql> - 执行SQL查询"
    log_info "  :export-to-json - 导出JSON报告"
    log_info "  q - 退出lnav"
}

# 步骤5: 分析测试结果
analyze_test_results() {
    log_section "步骤5: 分析测试结果"
    
    log_info "等待测试完成..."
    read -p "测试完成后按回车继续分析... " -r
    
    log_info "收集测试结果..."
    
    # 查找测试报告
    local test_report_files=()
    test_report_files+=("$PROJECT_ROOT/playwright-report/index.html")
    test_report_files+=("$PROJECT_ROOT/test-results/*.json")
    
    local report_found=false
    for report_file in "${test_report_files[@]}"; do
        if [ -f "$report_file" ]; then
            log_info "✅ 找到测试报告: $report_file"
            report_found=true
            break
        fi
    done
    
    if [ "$report_found" = true ]; then
        log_info "分析测试结果..."
        # 提取关键指标
        if [ -f "$PROJECT_ROOT/test-results/mystocks-e2e-report.json" ]; then
            log_info "详细测试报告: $PROJECT_ROOT/test-results/mystocks-e2e-report.json"
            # 显示关键指标
            local passed=$(jq '.testSummary.passedTests // 0' "$PROJECT_ROOT/test-results/mystocks-e2e-report.json" 2>/dev/null || echo "0")
            local failed=$(jq '.testSummary.failedTests // 0' "$PROJECT_ROOT/test-results/mystocks-e2e-report.json" 2>/dev/null || echo "0")
            local pass_rate=$(jq '.testSummary.passRate // "0%"' "$PROJECT_ROOT/test-results/mystocks-e2e-report.json" 2>/dev/null || echo "0%")
            
            log_info "测试统计:"
            log_info "  通过: $passed"
            log_info "  失败: $failed"
            log_info "  通过率: $pass_rate"
        fi
    else
        log_warn "未找到测试报告，可能测试未完成或失败"
    fi
}

# 步骤6: 生成问题报告
generate_issue_report() {
    log_section "步骤6: 生成问题报告"
    
    log_info "收集测试中发现的问题..."
    
    local issue_report_file="$PROJECT_ROOT/tests/logs/test-issue-report-$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$issue_report_file" << EOF
# MyStocks测试问题报告

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
**测试循环次数**: $(date +%s)

## 测试范围

- 登录用户认证
- 实时行情
- 历史数据
- 技术分析
- 自选股管理

## 发现的问题

$(if [ -f "$PROJECT_ROOT/test-results/mystocks-e2e-report.json" ]; then
    jq -r '.issues[] | "- \(.severity | ascii_upcase) | .description"' "$PROJECT_ROOT/test-results/mystocks-e2e-report.json" 2>/dev/null || echo "无问题发现"
else
    echo "无问题发现"
fi)

## 建议的修复

根据测试结果，请按以下顺序修复问题：

1. **Critical级别问题** - 立即修复，影响核心功能
2. **High级别问题** - 优先修复，影响用户体验
3. **Medium级别问题** - 计划修复，影响次要功能
4. **Low级别问题** - 逐步修复，优化或改进

## 下一步

修复完成后，请重新运行测试循环：
EOF
    
    log_info "✅ 问题报告已生成: $issue_report_file"
    
    # 更新前端启动指南
    if [ -f "$PROJECT_ROOT/docs/guides/WEB_FRONTEND_STARTUP_GUIDE.md" ]; then
        log_info "更新前端启动指南..."
        # 在文件末尾添加测试问题记录
        cat >> "$PROJECT_ROOT/docs/guides/WEB_FRONTEND_STARTUP_GUIDE.md" << EOF

## 测试问题记录

### $(date '+%Y-%m-%d')

$(cat "$issue_report_file")
EOF
    fi
    
    # 更新前端JS修复报告
    if [ -f "$PROJECT_ROOT/docs/reports/FRONTEND_JS_SYNTAX_FIX_REPORT.md" ]; then
        log_info "更新前端JS修复报告..."
        cat >> "$PROJECT_ROOT/docs/reports/FRONTEND_JS_SYNTAX_FIX_REPORT.md" << EOF

## 测试问题 $(date '+%Y%m%d_%H%M%S')

### 发现的问题

- 测试范围: 登录、实时行情、历史数据、技术分析、自选股
- 测试工具: Playwright (TypeScript)
- 辅助工具: Chrome DevTools MCP
- 测试方法: PM2管理 + tmux会话 + lnav日志分析

### 测试结果

详细报告: $issue_report_file

### 建议修复

见下方问题报告中的详细建议。

EOF
    fi
}

# 步骤7: 询问是否重新测试
ask_retest() {
    log_section "步骤7: 询问是否重新测试"
    
    echo ""
    log_info "测试循环已完成，请选择下一步操作："
    echo "  1) 修复发现的问题，然后重新测试"
    echo "  2) 查看详细测试报告"
    echo "  3) 退出测试循环"
    echo ""
    
    read -p "请选择 (1/2/3): " -r choice
    
    case "$choice" in
        1)
            log_info "准备修复问题..."
            log_info "请修复问题后，重新运行本脚本"
            log_info "命令: $0"
            exit 0
            ;;
        2)
            if [ -f "$PROJECT_ROOT/playwright-report/index.html" ]; then
                log_info "打开测试报告..."
                open "$PROJECT_ROOT/playwright-report/index.html" 2>/dev/null || \
                xdg-open "$PROJECT_ROOT/playwright-report/index.html" 2>/dev/null || \
                echo "请手动打开: $PROJECT_ROOT/playwright-report/index.html"
            else
                log_warn "测试报告不存在"
            fi
            ask_retest
            ;;
        3)
            log_info "退出测试循环"
            exit 0
            ;;
        *)
            log_error "无效选择，请重新运行脚本"
            exit 1
            ;;
    esac
}

# 主函数
main() {
    echo ""
    log_info "🚀 MyStocks Ralph-Wiggum测试循环开始"
    echo ""
    
    # 步骤1: 启动PM2服务
    start_pm2_services
    if [ $? -ne 0 ]; then
        log_error "PM2服务启动失败，请检查配置"
        exit 1
    fi
    
    # 步骤2: 创建tmux测试会话
    create_test_session
    
    # 步骤3: 运行Playwright测试
    run_playwright_tests
    
    # 步骤4: lnav实时日志分析
    lnav_log_analysis
    
    # 步骤5: 分析测试结果
    analyze_test_results
    
    # 步骤6: 生成问题报告
    generate_issue_report
    
    # 步骤7: 询问是否重新测试
    ask_retest
}

# 执行主函数
main