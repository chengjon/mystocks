#!/bin/bash
# =================================
# MyStocks lnav配置安装脚本
# 支持开发/生产环境差异化配置
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
print_colored() {
    local color=$1
    local message=$2
    echo -e "${color}[INFO]${NC} $message"
}

print_success() {
    print_colored "$GREEN" "✅ $1"
}

print_warning() {
    print_colored "$YELLOW" "⚠️  $1"
}

print_error() {
    print_colored "$RED" "❌ $1"
}

print_header() {
    local title=$1
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}    $title${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# 检查lnav是否安装
check_lnav_installation() {
    print_header "lnav安装检查"
    
    if ! command -v lnav &> /dev/null; then
        print_error "lnav未安装"
        echo ""
        echo "安装命令:"
        echo "  Ubuntu/Debian: sudo apt-get install lnav"
        echo "  CentOS/RHEL:   sudo yum install lnav"
        echo "  macOS:         brew install lnav"
        echo "  源码安装:      https://lnav.org/downloads/"
        echo ""
        return 1
    fi
    
    local version=$(lnav -V 2>/dev/null | head -1 || echo "Unknown")
    print_success "lnav已安装: $version"
    
    return 0
}

# 创建lnav配置
create_lnav_config() {
    local env=$1
    
    print_header "创建lnav配置 ($env)"
    
    local config_dir="$HOME/.config/lnav"
    mkdir -p "$config_dir"
    
    case $env in
        development)
            create_development_config "$config_dir/formats.json"
            ;;
        production)
            create_production_config "$config_dir/formats.json"
            ;;
        *)
            print_error "未知环境: $env"
            exit 1
            ;;
    esac
    
    print_success "lnav配置创建完成: $config_dir/formats.json"
}

# 开发环境配置 (包含调试字段)
create_development_config() {
    local config_file=$1
    
    print_success "创建开发环境配置 (包含调试字段)"
    
    cat > "$config_file" << 'EOF'
{
    "mystocks_backend_logs": {
        "title": "MyStocks Backend Development Logs",
        "description": "开发环境日志格式，包含完整调试信息",
        "regex": {
            "std": {
                "pattern": "^(?<timestamp>\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}\\+\\d{4}) (?<level>\\w+) (?<logger>\\S+) (?<file>\\S+):(?<line>\\d+) (?<function>\\S+) - (?<message>.*)$"
            },
            "request": {
                "pattern": "^(?<timestamp>\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}\\+\\d{4}) \\[(?<level>\\w+)\\] request_id=(?<request_id>\\w+) duration=(?<duration>\\d+)ms path=(?<path>\\S+) status=(?<status>\\d+)(?: error=\"(?<error>[^\"]*)\")?"
            },
            "performance": {
                "pattern": "^(?<timestamp>\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}\\+\\d{4}) \\[(?<level>\\w+)\\] (?<component>\\S+) performance=(?<performance>\\d+)ms memory=(?<memory>\\d+)MB cpu=(?<cpu>\\d+)%"
            }
        },
        "level-field": "level",
        "level": {
            "DEBUG": 0,
            "INFO": 1,
            "SUCCESS": 2,
            "WARNING": 3,
            "ERROR": 4,
            "CRITICAL": 5
        },
        "field-coloring": {
            "level": {
                "ERROR": "red",
                "WARNING": "yellow",
                "INFO": "blue",
                "SUCCESS": "green",
                "DEBUG": "gray",
                "CRITICAL": "magenta"
            },
            "status": {
                "2xx": "green",
                "3xx": "yellow",
                "4xx": "orange",
                "5xx": "red"
            },
            "duration": {
                "0-100": "green",
                "101-500": "yellow",
                "501-1000": "orange",
                "1001-999999": "red"
            }
        },
        "sample": [
            "2024-12-19T10:30:45.123+0800 INFO MyStocksDataAccess data_access.py:123 save_data - 数据保存成功",
            "2024-12-19T10:30:46.456+0800 [INFO] request_id=abc123 duration=200ms path=/api/strategy status=200",
            "2024-12-19T10:30:47.789+0800 [ERROR] request_id=def456 duration=500ms path=/api/data status=500 error=\"Database connection failed\"",
            "2024-12-19T10:30:48.012+0800 [WARNING] performance cpu=85% memory=512MB api_service"
        ]
    },
    
    "mystocks_system_logs": {
        "title": "MyStocks System Logs",
        "description": "系统级日志 (PM2、数据库等)",
        "regex": {
            "pm2": {
                "pattern": "^(?<timestamp>\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}\\+\\d{4}) (?:\\[PM2\\] (?:Starting|Stopping|Restarting) (?<service>\\S+)|\\[(?:pm2\\|PM2)\\] (?<level>\\w+): (?<message>.*))$"
            },
            "database": {
                "pattern": "^(?<timestamp>\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}\\+\\d{4}) \\[(?<level>\\w+)\\] database=(?<database>\\S+) query_time=(?<query_time>\\d+)ms rows=(?<rows>\\d+) (?<message>.*)$"
            }
        },
        "level-field": "level",
        "sample": [
            "2024-12-19T10:30:45.123+0800 [PM2] Starting mystocks-backend",
            "2024-12-19T10:30:46.456+0800 [ERROR] database=postgresql query_time=500ms rows=0 Connection failed"
        ]
    },
    
    "mysql_query_logs": {
        "title": "MySQL Query Logs",
        "description": "MySQL慢查询日志格式",
        "regex": {
            "slow_query": {
                "pattern": "^(?<timestamp>\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}) Query_time=(?<query_time>\\d+\\.\\d+) Lock_time=(?<lock_time>\\d+\\.\\d+) Rows_sent=(?<rows_sent>\\d+) Rows_examined=(?<rows_examined>\\d+) \\S+ (?<query>.*)$"
            }
        },
        "level-field": "query_time",
        "sample": [
            "2024-12-19 10:30:45 Query_time=0.123456 Lock_time=0.000123 Rows_sent=1 Rows_examined=1234 SELECT * FROM users WHERE id = ?"
        ]
    }
}
EOF

    # 创建开发环境快捷查询
    cat > "${config_file%.json}_queries.json" << 'EOF'
{
    "dev_queries": {
        "title": "MyStocks Development Queries",
        "description": "开发环境常用查询模板",
        "queries": {
            "errors_last_hour": {
                "title": "最近一小时的错误日志",
                "sql": "SELECT timestamp, level, logger, file, message FROM log WHERE level = 'ERROR' AND timestamp > datetime('now', '-1 hour') ORDER BY timestamp DESC LIMIT 20"
            },
            "slow_requests": {
                "title": "慢请求 (>500ms)",
                "sql": "SELECT timestamp, request_id, duration, path, status, error FROM log WHERE duration > 500 ORDER BY duration DESC LIMIT 10"
            },
            "error_summary": {
                "title": "错误统计",
                "sql": "SELECT level, COUNT(*) as count FROM log GROUP BY level ORDER BY count DESC"
            },
            "performance_analysis": {
                "title": "性能分析",
                "sql": "SELECT path, AVG(duration) as avg_duration, COUNT(*) as request_count FROM log WHERE level IN ('INFO', 'WARNING', 'ERROR') GROUP BY path ORDER BY avg_duration DESC LIMIT 10"
            }
        }
    }
}
EOF

    print_success "开发环境配置包含: 调试字段、性能分析、SQL查询模板"
}

# 生产环境配置 (精简字段，专注性能)
create_production_config() {
    local config_file=$1
    
    print_success "创建生产环境配置 (精简字段，专注性能)"
    
    cat > "$config_file" << 'EOF'
{
    "mystocks_backend_logs": {
        "title": "MyStocks Backend Production Logs",
        "description": "生产环境日志格式，专注于性能和错误监控",
        "regex": {
            "std": {
                "pattern": "^(?<timestamp>\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}\\+\\d{4}) \\[(?<level>\\w+)\\] (?<message>.*)$"
            },
            "request": {
                "pattern": "^(?<timestamp>\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}\\+\\d{4}) \\[(?<level>\\w+)\\] request_id=(?<request_id>\\w+) duration=(?<duration>\\d+)ms path=(?<path>\\S+) status=(?<status>\\d+)(?: error=\"(?<error>[^\"]*)\")?"
            }
        },
        "level-field": "level",
        "level": {
            "INFO": 1,
            "WARNING": 3,
            "ERROR": 4,
            "CRITICAL": 5
        },
        "field-coloring": {
            "level": {
                "ERROR": "red",
                "WARNING": "yellow",
                "INFO": "blue",
                "CRITICAL": "magenta"
            },
            "status": {
                "2xx": "green",
                "3xx": "yellow",
                "4xx": "orange",
                "5xx": "red"
            },
            "duration": {
                "0-100": "green",
                "101-500": "yellow",
                "501-1000": "orange",
                "1001-999999": "red"
            }
        },
        "sample": [
            "2024-12-19T10:30:46.456+0800 [INFO] request_id=abc123 duration=200ms path=/api/strategy status=200",
            "2024-12-19T10:30:47.789+0800 [ERROR] request_id=def456 duration=500ms path=/api/data status=500 error=\"Database connection failed\""
        ]
    },
    
    "mystocks_pm2_logs": {
        "title": "PM2 Process Logs",
        "description": "PM2进程管理日志",
        "regex": {
            "pm2": {
                "pattern": "^(?<timestamp>\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}\\+\\d{4}) \\[PM2\\] (?<message>.*)$"
            }
        },
        "sample": [
            "2024-12-19T10:30:45.123+0800 [PM2] Starting mystocks-backend"
        ]
    }
}
EOF

    # 创建生产环境快捷查询 (仅性能相关)
    cat > "${config_file%.json}_queries.json" << 'EOF'
{
    "prod_queries": {
        "title": "MyStocks Production Queries",
        "description": "生产环境常用查询模板 (性能焦点)",
        "queries": {
            "error_rate": {
                "title": "错误率统计",
                "sql": "SELECT level, COUNT(*) as count FROM log WHERE timestamp > datetime('now', '-1 hour') GROUP BY level"
            },
            "slow_requests": {
                "title": "慢请求 (>1s)",
                "sql": "SELECT timestamp, request_id, duration, path FROM log WHERE duration > 1000 ORDER BY duration DESC LIMIT 10"
            },
            "service_health": {
                "title": "服务健康状态",
                "sql": "SELECT status, COUNT(*) as count FROM log WHERE timestamp > datetime('now', '-30 minutes') GROUP BY status"
            }
        }
    }
}
EOF

    print_success "生产环境配置包含: 性能监控、错误率、简化查询"
}

# 验证配置
validate_config() {
    print_header "验证lnav配置"
    
    local config_file="$HOME/.config/lnav/formats.json"
    
    if [ ! -f "$config_file" ]; then
        print_error "配置文件不存在: $config_file"
        return 1
    fi
    
    # 验证JSON格式
    if command -v jq &> /dev/null; then
        if ! jq empty "$config_file" 2>/dev/null; then
            print_error "JSON格式验证失败"
            return 1
        fi
        print_success "JSON格式验证通过"
    else
        print_warning "jq未安装，跳过JSON格式验证"
    fi
    
    # 测试lnav配置
    if ! lnav -c ":quit" "$config_file" 2>/dev/null; then
        print_warning "lnav配置测试失败"
    else
        print_success "lnav配置测试通过"
    fi
    
    print_success "配置验证完成"
}

# 显示使用指南
show_usage_guide() {
    print_header "lnav使用指南"
    
    echo -e "${GREEN}基本操作:${NC}"
    echo -e "  ${CYAN}lnav $LOG_DIR${NC}                    # 启动lnav并监控日志"
    echo -e "  ${CYAN}lnav $LOG_DIR/*.log${NC}             # 监控多个日志文件"
    echo -e "  ${CYAN}lnav -t $LOG_DIR${NC}                # 进入时间旅行模式"
    echo ""
    
    echo -e "${GREEN}过滤和搜索:${NC}"
    echo -e "  ${CYAN}:filter-in ERROR${NC}                # 过滤错误日志"
    echo -e "  ${CYAN}:filter-in -v INFO${NC}              # 过滤掉INFO日志"
    echo -e "  ${CYAN}:search /request_id=abc${NC}         # 搜索特定request_id"
    echo ""
    
    echo -e "${GREEN}SQL查询 (开发环境):${NC}"
    echo -e "  ${CYAN}:sql-query SELECT COUNT(*) FROM log WHERE level='ERROR'${NC}  # 错误计数"
    echo -e "  ${CYAN}:sql-query SELECT path, AVG(duration) FROM log GROUP BY path${NC}  # 平均响应时间"
    echo ""
    
    echo -e "${GREEN}统计和图表:${NC}"
    echo -e "  ${CYAN}:stats${NC}                          # 显示日志统计信息"
    echo -e "  ${CYAN}:histogram -f duration${NC}          # 响应时间分布图"
    echo -e "  ${CYAN}:timeline${NC}                       # 时间轴视图"
    echo ""
    
    echo -e "${GREEN}其他功能:${NC}"
    echo -e "  ${CYAN}:quit${NC}                           # 退出lnav"
    echo -e "  ${CYAN}:help${NC}                           # 显示帮助"
    echo -e "  ${CYAN}:toggle-fullscreen${NC}              # 切换全屏模式"
    echo ""
}

# 显示帮助信息
show_help() {
    print_header "MyStocks lnav配置安装器 v2.0"
    
    echo "用法: $0 [环境] [选项]"
    echo ""
    echo "环境:"
    echo "  development              开发环境 (默认)"
    echo "  production              生产环境"
    echo ""
    echo "选项:"
    echo "  --validate              仅验证配置，不安装"
    echo "  --guide                 显示使用指南"
    echo "  --help                  显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 development          # 安装开发环境配置"
    echo "  $0 production           # 安装生产环境配置"
    echo "  $0 --validate           # 验证现有配置"
    echo "  $0 --guide              # 显示使用指南"
    echo ""
}

# 主函数
main() {
    local env="development"
    local validate_only=false
    local show_guide=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            development|production)
                env="$1"
                shift
                ;;
            --validate)
                validate_only=true
                shift
                ;;
            --guide)
                show_guide=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 显示标题
    print_header "MyStocks lnav配置安装器 v2.0"
    echo ""
    
    if [ "$show_guide" = true ]; then
        show_usage_guide
        exit 0
    fi
    
    # 检查lnav安装
    if ! check_lnav_installation; then
        exit 1
    fi
    
    if [ "$validate_only" = true ]; then
        validate_config
        exit 0
    fi
    
    # 创建配置
    create_lnav_config "$env"
    
    # 验证配置
    validate_config
    
    # 显示使用指南
    show_usage_guide
    
    print_success "lnav配置安装完成！"
}

# 脚本入口
main "$@"
