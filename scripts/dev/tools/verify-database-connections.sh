#!/bin/bash
# 数据库连接和网络环境验证脚本
# 用于在服务器恢复后验证数据库连接状态

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[DB-VERIFY]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[DB-VERIFY]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[DB-VERIFY]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[DB-VERIFY]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 网络连接测试
test_network_connectivity() {
    log_info "测试网络连接..."

    local server_ip="localhost"
    local ports=("5438" "6030" "3306")

    for port in "${ports[@]}"; do
        if nc -z -w5 "$server_ip" "$port" 2>/dev/null; then
            log_success "端口 $port 网络连接正常"
        else
            log_error "端口 $port 网络连接失败"
            return 1
        fi
    done

    log_success "网络连接测试完成"
    return 0
}

# PostgreSQL连接测试
test_postgresql_connection() {
    log_info "测试PostgreSQL连接..."

    python3 -c "
import psycopg2
import os
import sys

# 加载环境变量
os.chdir('$PROJECT_ROOT')
from dotenv import load_dotenv
load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv('POSTGRESQL_HOST'),
        port=os.getenv('POSTGRESQL_PORT'),
        database=os.getenv('POSTGRESQL_DATABASE'),
        user=os.getenv('POSTGRESQL_USER'),
        password=os.getenv('POSTGRESQL_PASSWORD')
    )

    # 测试基本查询
    cursor = conn.cursor()
    cursor.execute('SELECT version();')
    version = cursor.fetchone()
    cursor.close()
    conn.close()

    print('✅ PostgreSQL连接成功')
    print(f'   版本: {version[0][:50]}...')

except Exception as e:
    print(f'❌ PostgreSQL连接失败: {e}')
    sys.exit(1)
"
}

# TDengine连接测试
test_tdengine_connection() {
    log_info "测试TDengine连接..."

    python3 -c "
import taos
import os
import sys

# 加载环境变量
os.chdir('$PROJECT_ROOT')
from dotenv import load_dotenv
load_dotenv()

try:
    conn = taos.connect(
        host=os.getenv('TDENGINE_HOST'),
        port=int(os.getenv('TDENGINE_PORT', '6030')),
        user=os.getenv('TDENGINE_USER', 'root'),
        password=os.getenv('TDENGINE_PASSWORD'),
        database=os.getenv('TDENGINE_DATABASE')
    )

    # 测试基本查询
    cursor = conn.cursor()
    cursor.execute('SELECT server_version();')
    version = cursor.fetchone()
    cursor.close()
    conn.close()

    print('✅ TDengine连接成功')
    print(f'   版本: {version[0]}')

except Exception as e:
    print(f'❌ TDengine连接失败: {e}')
    sys.exit(1)
"
}

# MySQL连接测试
test_mysql_connection() {
    log_info "测试MySQL连接..."

    python3 -c "
import pymysql
import os
import sys

# 加载环境变量
os.chdir('$PROJECT_ROOT')
from dotenv import load_dotenv
load_dotenv()

try:
    conn = pymysql.connect(
        host=os.getenv('MYSQL_HOST'),
        port=int(os.getenv('MYSQL_PORT', '3306')),
        database=os.getenv('MYSQL_DATABASE'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD')
    )

    # 测试基本查询
    cursor = conn.cursor()
    cursor.execute('SELECT VERSION();')
    version = cursor.fetchone()
    cursor.close()
    conn.close()

    print('✅ MySQL连接成功')
    print(f'   版本: {version[0]}')

except Exception as e:
    print(f'❌ MySQL连接失败: {e}')
    sys.exit(1)
"
}

# Redis连接测试
test_redis_connection() {
    log_info "测试Redis连接..."

    python3 -c "
import redis
import os
import sys

# 加载环境变量
os.chdir('$PROJECT_ROOT')
from dotenv import load_dotenv
load_dotenv()

try:
    r = redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=int(os.getenv('REDIS_PORT', '6379')),
        password=os.getenv('REDIS_PASSWORD') or None,
        db=int(os.getenv('REDIS_DB', '1'))
    )

    # 测试连接
    r.ping()
    info = r.info('server')

    print('✅ Redis连接成功')
    print(f'   版本: {info[\"redis_version\"]}')

except Exception as e:
    print(f'❌ Redis连接失败: {e}')
    sys.exit(1)
"
}

# 服务端点测试
test_service_endpoints() {
    log_info "测试服务端点..."

    # 后端健康检查
    if curl -s --max-time 10 "http://localhost:8000/api/health" >/dev/null 2>&1; then
        log_success "后端服务端点正常"
    else
        log_error "后端服务端点无响应"
    fi

    # 前端服务检查
    if curl -s --max-time 10 "http://localhost:3001" >/dev/null 2>&1; then
        log_success "前端服务端点正常"
    else
        log_error "前端服务端点无响应"
    fi
}

# 生成验证报告
generate_verification_report() {
    log_info "生成数据库连接验证报告..."

    local report_file="${PROJECT_ROOT}/test-reports/database-connection-report.md"

    cat > "$report_file" << EOF
# 数据库连接和网络环境验证报告

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
**验证服务器**: localhost

## 网络连接状态

### 端口连通性
- **PostgreSQL (5438)**: $(nc -z -w5 localhost 5438 2>/dev/null && echo "✅ 连通" || echo "❌ 不通")
- **TDengine (6030)**: $(nc -z -w5 localhost 6030 2>/dev/null && echo "✅ 连通" || echo "❌ 不通")
- **MySQL (3306)**: $(nc -z -w5 localhost 3306 2>/dev/null && echo "✅ 连通" || echo "❌ 不通")

## 数据库连接状态

### PostgreSQL连接
\`\`\`bash
$(python3 -c "
import psycopg2, os
os.chdir('$PROJECT_ROOT')
from dotenv import load_dotenv
load_dotenv()
try:
    conn = psycopg2.connect(host=os.getenv('POSTGRESQL_HOST'), port=os.getenv('POSTGRESQL_PORT'), database=os.getenv('POSTGRESQL_DATABASE'), user=os.getenv('POSTGRESQL_USER'), password=os.getenv('POSTGRESQL_PASSWORD'))
    cursor = conn.cursor()
    cursor.execute('SELECT version();')
    print('✅ 连接成功')
    print('版本信息:', cursor.fetchone()[0][:100])
    cursor.close()
    conn.close()
except Exception as e:
    print('❌ 连接失败:', str(e))
" 2>&1)
\`\`\`

### TDengine连接
\`\`\`bash
$(python3 -c "
import taos, os
os.chdir('$PROJECT_ROOT')
from dotenv import load_dotenv
load_dotenv()
try:
    conn = taos.connect(host=os.getenv('TDENGINE_HOST'), port=int(os.getenv('TDENGINE_PORT', '6030')), user=os.getenv('TDENGINE_USER', 'root'), password=os.getenv('TDENGINE_PASSWORD'), database=os.getenv('TDENGINE_DATABASE'))
    cursor = conn.cursor()
    cursor.execute('SELECT server_version();')
    print('✅ 连接成功')
    print('版本信息:', cursor.fetchone()[0])
    cursor.close()
    conn.close()
except Exception as e:
    print('❌ 连接失败:', str(e))
" 2>&1)
\`\`\`

## 环境变量配置

### 关键配置检查
- **POSTGRESQL_HOST**: $(grep POSTGRESQL_HOST .env | cut -d'=' -f2)
- **TDENGINE_HOST**: $(grep TDENGINE_HOST .env | cut -d'=' -f2)
- **MYSQL_HOST**: $(grep MYSQL_HOST .env | cut -d'=' -f2)
- **REDIS_HOST**: $(grep REDIS_HOST .env | cut -d'=' -f2)

## 服务状态

### 本地服务端点
- **后端API**: $(curl -s --max-time 5 "http://localhost:8000/api/health" >/dev/null 2>&1 && echo "✅ 运行中" || echo "❌ 未运行")
- **前端服务**: $(curl -s --max-time 5 "http://localhost:3001" >/dev/null 2>&1 && echo "✅ 运行中" || echo "❌ 未运行")

## 诊断建议

1. **如果网络连接失败**: 检查localhost服务器状态
2. **如果数据库连接失败**: 验证数据库服务是否启动
3. **如果认证失败**: 检查环境变量中的密码配置
4. **如果服务端点失败**: 确认本地服务已启动

## 下一步行动

- [ ] 修复网络连接问题
- [ ] 重启数据库服务
- [ ] 验证数据库用户权限
- [ ] 测试完整应用功能

---
*自动生成报告 - 数据库环境验证完成*
EOF

    log_success "验证报告已生成: $report_file"
}

# 主函数
main() {
    echo "🔍 MyStocks数据库连接和网络环境验证工具"
    echo "============================================="
    echo ""

    local all_passed=true

    # 测试网络连接
    if test_network_connectivity; then
        log_success "网络连接测试通过"
    else
        log_error "网络连接测试失败"
        all_passed=false
    fi

    echo ""

    # 测试PostgreSQL
    if test_postgresql_connection; then
        log_success "PostgreSQL测试通过"
    else
        log_error "PostgreSQL测试失败"
        all_passed=false
    fi

    echo ""

    # 测试TDengine
    if test_tdengine_connection; then
        log_success "TDengine测试通过"
    else
        log_error "TDengine测试失败"
        all_passed=false
    fi

    echo ""

    # 测试MySQL
    if test_mysql_connection; then
        log_success "MySQL测试通过"
    else
        log_error "MySQL测试失败"
        all_passed=false
    fi

    echo ""

    # 测试Redis
    if test_redis_connection; then
        log_success "Redis测试通过"
    else
        log_error "Redis测试失败"
        all_passed=false
    fi

    echo ""

    # 测试服务端点
    test_service_endpoints

    echo ""

    # 生成报告
    generate_verification_report

    echo ""
    if [ "$all_passed" = true ]; then
        log_success "🎉 所有数据库连接测试通过！"
        echo ""
        echo "✅ 数据库环境验证完成"
        echo "✅ 可以开始完整服务测试"
    else
        log_error "❌ 部分数据库连接测试失败"
        echo ""
        echo "⚠️  请检查数据库服务器状态"
        echo "🔧 运行此脚本重新验证: $0"
    fi
}

# 参数处理
if [ $# -eq 0 ]; then
    main
else
    case $1 in
        --network)
            test_network_connectivity
            ;;
        --postgres)
            test_postgresql_connection
            ;;
        --tdengine)
            test_tdengine_connection
            ;;
        --mysql)
            test_mysql_connection
            ;;
        --redis)
            test_redis_connection
            ;;
        --services)
            test_service_endpoints
            ;;
        --report)
            generate_verification_report
            ;;
        --help|-h)
            echo "数据库连接验证工具"
            echo ""
            echo "用法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  --network    测试网络连接"
            echo "  --postgres   测试PostgreSQL连接"
            echo "  --tdengine   测试TDengine连接"
            echo "  --mysql      测试MySQL连接"
            echo "  --redis      测试Redis连接"
            echo "  --services   测试服务端点"
            echo "  --report     生成验证报告"
            echo "  --help, -h   显示此帮助"
            echo ""
            echo "无参数运行完整测试"
            ;;
        *)
            log_error "未知参数: $1"
            echo "运行 '$0 --help' 查看帮助"
            exit 1
            ;;
    esac
fi