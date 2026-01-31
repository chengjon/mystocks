#!/bin/bash
# 生产部署验证脚本
# 用于验证HTML5 History模式迁移的生产环境部署

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
DOMAIN=${1:-"http://localhost:3020"}
TIMEOUT=5
MAX_RETRIES=3

# 打印函数
print_header() {
    echo -e "\n${GREEN}════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  $1${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${NC}ℹ️  $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 未安装，请先安装"
        exit 1
    fi
}

# 测试URL
test_url() {
    local url=$1
    local expected_status=$2
    local description=$3
    
    for i in $(seq 1 $MAX_RETRIES); do
        status=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$url")
        
        if [ "$status" -eq "$expected_status" ]; then
            print_success "$description: HTTP $status"
            return 0
        else
            if [ $i -lt $MAX_RETRIES ]; then
                print_info "重试 $i/$MAX_RETRIES..."
                sleep 1
            fi
        fi
    done
    
    print_error "$description: HTTP $status (预期: $expected_status)"
    return 1
}

# 主函数
main() {
    print_header "🚀 MyStocks 生产部署验证"
    
    # 检查依赖
    check_command "curl"
    check_command "jq"
    
    # 配置验证
    TOTAL_CHECKS=0
    PASSED_CHECKS=0
    
    # ========================================
    # 1. 健康检查端点验证
    # ========================================
    print_header "1️⃣  健康检查端点验证"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if test_url "${DOMAIN}/health" 200 "健康检查端点"; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    fi
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if test_url "${DOMAIN}/ready" 200 "就绪检查端点"; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    fi
    
    # 验证健康检查响应格式
    print_info "验证健康检查响应格式..."
    health_response=$(curl -s "$DOMAIN/health" --max-time $TIMEOUT)
    if echo "$health_response" | jq -e '.status == "healthy"' &> /dev/null; then
        print_success "健康检查响应格式正确"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        print_error "健康检查响应格式不正确"
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    # ========================================
    # 2. 路由功能验证
    # ========================================
    print_header "2️⃣ 路由功能验证"
    
    ROUTES=(
        "/:首页"
        "/dashboard:仪表板"
        "/market/realtime:实时行情"
        "/risk/alerts:风险告警"
        "/strategy/management:策略管理"
        "/trading/signals:交易信号"
        "/system/monitoring:系统监控"
    )
    
    for route_info in "${ROUTES[@]}"; do
        route="${route_info%%:*}"
        description="${route_info##*:}"
        
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
        if test_url "${DOMAIN}${route}" 200 "$description"; then
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        fi
    done
    
    # ========================================
    # 3. 安全头验证
    # ========================================
    print_header "3️⃣ 安全头验证"
    
    SECURITY_HEADERS=(
        "X-Frame-Options:点击劫持防护"
        "X-Content-Type-Options:MIME类型嗅探防护"
        "X-XSS-Protection:XSS防护"
        "Content-Security-Policy:内容安全策略"
        "Referrer-Policy:Referer策略"
    )
    
    for header_info in "${SECURITY_HEADERS[@]}"; do
        header_name="${header_info%%:*}"
        description="${header_info##*:}"
        
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
        if curl -s -I "$DOMAIN/" --max-time $TIMEOUT | grep -q "$header_name"; then
            print_success "$description ($header_name)"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            print_warning "$description ($header_name) 未找到"
        fi
    done
    
    # ========================================
    # 4. 静态资源验证
    # ========================================
    print_header "4️⃣ 静态资源验证"
    
    print_info "检查 index.html..."
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if test_url "$DOMAIN/" 200 "index.html加载"; then
        # 检查Cache-Control头
        cache_control=$(curl -s -I "$DOMAIN/" --max-time $TIMEOUT | grep -i "cache-control" || echo "")
        if echo "$cache_control" | grep -qi "no-store"; then
            print_success "index.html 禁用缓存（正确）"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            print_warning "index.html 缓存策略可能不正确"
        fi
    fi
    
    # ========================================
    # 5. 浏览器兼容性验证
    # ========================================
    print_header "5️⃣ 浏览器兼容性验证"
    
    print_info "检查 User-Agent 处理..."
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    # 模拟不同浏览器测试
    user_agents=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64):Chrome"
        "Mozilla/5.0 (Macintosh; Intel Mac OS X):Firefox"
        "Mozilla/5.0 (Windows NT 10.0; Trident/7.0):IE11"
    )
    
    chrome_tested=false
    for ua in "${user_agents[@]}"; do
        browser=$(echo $ua | cut -d: -f2)
        status=$(curl -s -o /dev/null -w "%{http_code}" -A "User-Agent: $ua" "$DOMAIN/" --max-time $TIMEOUT)
        
        if [ "$status" -eq 200 ]; then
            if [ "$browser" = "Chrome" ] && [ "$chrome_tested" = false ]; then
                print_success "$browser 兼容性测试通过"
                PASSED_CHECKS=$((PASSED_CHECKS + 1))
                chrome_tested=true
            fi
        fi
    done
    
    # ========================================
    # 6. HTML5 History模式验证
    # ========================================
    print_header "6️⃣ HTML5 History模式验证"
    
    print_info "检查URL格式（应该无#符号）..."
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    # 检查页面源代码中是否使用History模式
    page_content=$(curl -s "$DOMAIN/" --max-time $TIMEOUT)
    if echo "$page_content" | grep -q "createWebHistory"; then
        print_success "路由模式: HTML5 History"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    elif echo "$page_content" | grep -q "createWebHashHistory"; then
        print_warning "路由模式: Hash模式（可能触发降级）"
    else
        print_info "无法从HTML源码确定路由模式"
    fi
    
    # ========================================
    # 7. 性能指标验证
    # ========================================
    print_header "7️⃣ 性能指标验证"
    
    print_info "检查响应时间..."
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    response_time=$(curl -s -o /dev/null -w "%{time_total}" "$DOMAIN/" --max-time $TIMEOUT)
    response_time_ms=$(echo "$response_time * 1000" | bc)
    
    if [ "$(echo "$response_time < 1.0" | bc)" -eq 1 ]; then
        print_success "响应时间: ${response_time_ms}ms (优秀 < 1000ms)"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    elif [ "$(echo "$response_time < 3.0" | bc)" -eq 1 ]; then
        print_warning "响应时间: ${response_time_ms}ms (可接受 < 3000ms)"
    else
        print_error "响应时间: ${response_time_ms}ms (需要优化 > 3000ms)"
    fi
    
    # ========================================
    # 8. 配置文件语法验证
    # ========================================
    print_header "8️⃣ 配置文件语法验证"
    
    # Nginx配置验证（如果可用）
    if [ -f "config/nginx-history-mode.conf" ]; then
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
        print_info "验证Nginx配置语法..."
        
        # 检查配置是否存在基本语法错误
        if grep -q "server {" "config/nginx-history-mode.conf" && \
           grep -q "listen 80;" "config/nginx-history-mode.conf"; then
            print_success "Nginx配置基本语法正确"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            print_error "Nginx配置可能存在语法错误"
        fi
    fi
    
    # Apache配置验证（如果可用）
    if [ -f "config/apache-history-mode.conf" ]; then
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
        print_info "验证Apache配置基本结构..."
        
        if grep -q "<Location" "config/apache-history-mode.conf" && \
           grep -q "Header always set" "config/apache-history-mode.conf"; then
            print_success "Apache配置基本结构正确"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            print_error "Apache配置可能存在语法错误"
        fi
    fi
    
    # ========================================
    # 最终报告
    # ========================================
    print_header "📊 验证结果总结"
    
    PASS_RATE=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
    
    echo "总检查项: $TOTAL_CHECKS"
    echo "通过检查: $PASSED_CHECKS"
    echo "失败检查: $((TOTAL_CHECKS - PASSED_CHECKS))"
    echo "通过率: ${PASS_RATE}%"
    echo ""
    
    if [ $PASSED_CHECKS -eq $TOTAL_CHECKS ]; then
        print_success "🎉 所有检查通过！部署验证成功。"
        echo ""
        echo "✅ 生产环境已就绪，可以安全部署HTML5 History模式。"
        return 0
    elif [ $PASS_RATE -ge 80 ]; then
        print_warning "⚠️  大部分检查通过（${PASS_RATE}%），但仍有少量问题需要关注。"
        echo ""
        echo "建议：修复失败项后再进行生产部署，或根据风险评估决定是否继续。"
        return 0
    else
        print_error "❌ 检查通过率过低（${PASS_RATE}%），请修复问题后再部署。"
        return 1
    fi
}

# 执行主函数
main "$@"
