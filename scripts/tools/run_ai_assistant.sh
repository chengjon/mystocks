#!/bin/bash
# AI助手集成脚本
# Phase 4.2: 实施AI助手集成优化
# 配置AI助手访问测试结果和日志，实现智能化错误诊断和建议生成

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[AI助手]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[AI助手]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[AI助手]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[AI助手]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 检查Python环境
check_environment() {
    log_info "检查Python环境..."

    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi

    # 检查AI助手模块
    if [ ! -f "${SCRIPT_DIR}/ai_test_assistant.py" ]; then
        log_error "AI助手模块不存在: ${SCRIPT_DIR}/ai_test_assistant.py"
        exit 1
    fi

    log_success "环境检查通过"
}

# 运行AI分析
run_ai_analysis() {
    local output_file=$1

    log_info "开始AI智能分析..."

    # 设置Python路径
    export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"

    # 运行AI助手分析
    if python3 "${SCRIPT_DIR}/ai_test_assistant.py" --output "$output_file"; then
        log_success "AI分析完成"
        return 0
    else
        log_error "AI分析失败"
        return 1
    fi
}

# 生成快速诊断报告
generate_quick_diagnosis() {
    log_info "生成快速诊断报告..."

    local diagnosis_file="${PROJECT_ROOT}/test-reports/ai_quick_diagnosis.md"

    cat > "$diagnosis_file" << 'EOF'
# AI助手快速诊断报告

## 诊断时间
EOF
    echo "$(date '+%Y-%m-%d %H:%M:%S')" >> "$diagnosis_file"

    cat >> "$diagnosis_file" << 'EOF'

## 系统状态检查

### 服务状态
EOF

    # 检查常见服务状态
    if pgrep -f "vite" >/dev/null 2>&1; then
        echo "- ✅ 前端服务运行正常" >> "$diagnosis_file"
    else
        echo "- ❌ 前端服务未运行" >> "$diagnosis_file"
    fi

    if pgrep -f "uvicorn.*app.main" >/dev/null 2>&1; then
        echo "- ✅ 后端服务运行正常" >> "$diagnosis_file"
    else
        echo "- ❌ 后端服务未运行" >> "$diagnosis_file"
    fi

    # 检查端口占用
    cat >> "$diagnosis_file" << 'EOF'

### 端口占用检查
EOF

    for port in 3001 8000; do
        if lsof -i :$port >/dev/null 2>&1; then
            process=$(lsof -i :$port | tail -1 | awk '{print $1}')
            echo "- ✅ 端口 $port: 正常占用 ($process)" >> "$diagnosis_file"
        else
            echo "- ❌ 端口 $port: 未占用" >> "$diagnosis_file"
        fi
    done

    # 检查测试结果目录
    cat >> "$diagnosis_file" << 'EOF'

### 测试结果检查
EOF

    if [ -d "${PROJECT_ROOT}/test-reports" ]; then
        test_count=$(find "${PROJECT_ROOT}/test-reports" -name "*.log" -o -name "*.json" | wc -l)
        echo "- 📊 发现 $test_count 个测试结果文件" >> "$diagnosis_file"

        # 检查最新测试结果
        latest_file=$(find "${PROJECT_ROOT}/test-reports" -name "*.log" -o -name "*.json" | head -1)
        if [ -n "$latest_file" ]; then
            echo "- 📅 最新测试: $(basename "$latest_file") ($(date -r "$latest_file" '+%Y-%m-%d %H:%M:%S'))" >> "$diagnosis_file"
        fi
    else
        echo "- ⚠️ 测试结果目录不存在" >> "$diagnosis_file"
    fi

    cat >> "$diagnosis_file" << 'EOF'

## 常见问题诊断

### 1. 端口冲突问题
**现象**: "端口已被占用" 或 "Address already in use"
**解决**:
- 运行 `pkill -f "vite|uvicorn"` 清理进程
- 检查 `lsof -i :端口号` 查看占用情况
- 重启相关服务

### 2. 服务启动失败
**现象**: "服务启动失败" 或 "Connection refused"
**解决**:
- 检查配置文件正确性
- 验证依赖是否安装
- 查看详细错误日志

### 3. ESM兼容性问题
**现象**: "does not provide an export named"
**解决**:
- 检查 Vite 配置中的 `optimizeDeps.exclude`
- 验证 dayjs 等库的 ESM 支持
- 更新相关依赖版本

### 4. 性能问题
**现象**: 测试执行时间过长
**解决**:
- 检查系统资源使用情况
- 优化测试并发配置
- 减少测试数据量

## 推荐操作

1. **立即处理**: 解决所有红色❌标记的问题
2. **优先处理**: 关注橙色🟠高优先级问题
3. **持续监控**: 定期检查黄色⚠️警告项目
4. **预防措施**: 实施绿色✅的优化建议

EOF

    log_success "快速诊断报告已生成: $diagnosis_file"
}

# 生成测试优化建议
generate_optimization_suggestions() {
    log_info "生成测试优化建议..."

    local suggestions_file="${PROJECT_ROOT}/test-reports/ai_optimization_suggestions.md"

    cat > "$suggestions_file" << 'EOF'
# AI助手测试优化建议

## 生成时间
EOF
    echo "$(date '+%Y-%m-%d %H:%M:%S')" >> "$suggestions_file"

    cat >> "$suggestions_file" << 'EOF'

## 优化建议清单

### 🔴 高优先级优化

#### 1. 环境稳定性优化
**问题**: 测试环境不稳定，经常出现端口冲突和服务启动失败
**建议**:
- 实现自动端口清理和分配机制
- 添加服务健康检查和自动重启
- 创建环境初始化和清理脚本
- 实现测试间的隔离机制

#### 2. 配置管理优化
**问题**: 配置分散，容易出现不一致
**建议**:
- 统一配置文件格式（YAML）
- 实现配置验证机制
- 添加环境变量管理
- 创建配置文档和模板

### 🟡 中优先级优化

#### 3. 测试执行效率
**问题**: 测试执行时间长，影响开发效率
**建议**:
- 实现测试并行执行
- 添加测试结果缓存
- 优化测试数据准备
- 实现增量测试策略

#### 4. 错误诊断改进
**问题**: 错误信息不够详细，难以快速定位问题
**建议**:
- 增强日志记录和格式化
- 添加错误上下文信息
- 实现错误模式识别
- 创建诊断工具链

### 🟢 低优先级优化

#### 5. 监控和报告
**问题**: 测试结果缺乏可视化和趋势分析
**建议**:
- 集成测试指标收集
- 添加Grafana仪表板
- 实现邮件/Slack通知
- 生成HTML测试报告

#### 6. 自动化程度
**问题**: 部分流程仍需手动干预
**建议**:
- 实现一键测试执行
- 添加自动环境部署
- 创建CI/CD模板
- 实现智能重试机制

## 实施路线图

### Phase 1: 基础优化 (1-2周)
- [ ] 修复所有高优先级问题
- [ ] 实现环境稳定化
- [ ] 统一配置管理

### Phase 2: 效率提升 (2-3周)
- [ ] 优化测试执行效率
- [ ] 增强错误诊断能力
- [ ] 实现基本监控

### Phase 3: 智能化 (3-4周)
- [ ] 实现AI辅助诊断
- [ ] 添加预测性优化
- [ ] 完善自动化流程

### Phase 4: 持续改进 (持续)
- [ ] 定期审查和优化
- [ ] 跟踪效果指标
- [ ] 技术栈升级

## 成功指标

- **环境稳定性**: 端口冲突率 < 5%
- **测试成功率**: > 95%
- **执行效率**: 平均测试时间减少 30%
- **诊断效率**: 问题定位时间减少 50%
- **自动化程度**: 手动干预减少 80%

EOF

    log_success "测试优化建议已生成: $suggestions_file"
}

# 集成到测试流程
integrate_with_test_flow() {
    log_info "集成AI助手到测试流程..."

    # 创建钩子脚本
    local hook_script="${PROJECT_ROOT}/scripts/hooks/post_test_ai_analysis.sh"

    mkdir -p "${PROJECT_ROOT}/scripts/hooks"

    cat > "$hook_script" << 'EOF'
#!/bin/bash
# 测试后AI分析钩子脚本
# 在测试执行完成后自动运行AI分析

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔍 运行测试后AI分析..."

# 运行AI助手分析
if python3 "${PROJECT_ROOT}/scripts/tools/ai_test_assistant.py" --output "${PROJECT_ROOT}/test-reports/ai_post_test_analysis_$(date +%Y%m%d_%H%M%S).md"; then
    echo "✅ AI分析完成"
else
    echo "❌ AI分析失败"
fi

echo "📊 查看完整报告: ${PROJECT_ROOT}/test-reports/"
EOF

    chmod +x "$hook_script"

    log_success "AI分析钩子已创建: $hook_script"
}

# 显示使用说明
show_usage() {
    cat << EOF
AI助手集成工具

用法:
    $0 [选项]

选项:
    --analyze, -a        运行完整AI分析
    --quick-diagnosis    生成快速诊断报告
    --optimization       生成优化建议
    --integrate          集成到测试流程
    --help, -h           显示此帮助信息

示例:
    $0 --analyze                    # 运行完整AI分析
    $0 --quick-diagnosis            # 生成快速诊断
    $0 --optimization               # 生成优化建议
    $0 --integrate                  # 集成到测试流程

输出文件:
    分析报告: test-reports/ai_analysis_*.md
    诊断报告: test-reports/ai_quick_diagnosis.md
    优化建议: test-reports/ai_optimization_suggestions.md
    钩子脚本: scripts/hooks/post_test_ai_analysis.sh
EOF
}

# 主函数
main() {
    echo "🤖 MyStocks AI测试助手集成工具"
    echo "=================================="
    echo "Phase 4.2: 实施AI助手集成优化"
    echo ""

    # 默认操作
    if [ $# -eq 0 ]; then
        log_info "无参数指定，默认运行快速诊断"
        check_environment
        generate_quick_diagnosis
        exit 0
    fi

    # 参数处理
    while [[ $# -gt 0 ]]; do
        case $1 in
            --analyze|-a)
                check_environment
                run_ai_analysis "${PROJECT_ROOT}/test-reports/ai_analysis_$(date +%Y%m%d_%H%M%S).md"
                shift
                ;;
            --quick-diagnosis)
                generate_quick_diagnosis
                shift
                ;;
            --optimization)
                generate_optimization_suggestions
                shift
                ;;
            --integrate)
                integrate_with_test_flow
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    echo ""
    log_success "AI助手集成操作完成! 🎉"
    echo ""
    echo "📋 可用功能:"
    echo "  • 智能错误诊断和修复建议"
    echo "  • 测试优化推荐"
    echo "  • 自动化分析报告生成"
    echo "  • 持续监控和改进建议"
    echo ""
    echo "🚀 下一步: 运行 './scripts/test-runner/run-orchestration.sh' 体验完整AI增强测试流程"
}

main "$@"