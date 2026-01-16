#!/bin/bash

# MyStocks CI/CD 月度优化审查脚本
# 基于监控数据生成优化报告和建议

set -e

# 配置
MONTH=$(date +%Y-%m)
REPORT_DIR="reports/cicd-optimization/${MONTH}"
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"
PROMETHEUS_URL="${PROMETHEUS_URL:-http://localhost:9090}"

# 创建报告目录
mkdir -p "$REPORT_DIR"

log_info() {
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo "[WARNING] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 获取GitHub Actions统计数据
collect_github_actions_stats() {
    log_info "收集GitHub Actions统计数据..."

    # 获取最近30天的workflow运行数据
    if command -v gh &> /dev/null; then
        # 工作流成功率
        gh run list --limit 100 --json conclusion,createdAt > "$REPORT_DIR/gh_runs.json"

        # 工作流运行时间
        gh run list --limit 50 --json name,runNumber,duration > "$REPORT_DIR/gh_durations.json"
    else
        log_warning "GitHub CLI未安装，跳过GitHub Actions数据收集"
        echo '{"workflows": []}' > "$REPORT_DIR/gh_runs.json"
        echo '{"durations": []}' > "$REPORT_DIR/gh_durations.json"
    fi
}

# 获取Prometheus监控数据
collect_prometheus_metrics() {
    log_info "收集Prometheus监控数据..."

    python3 -c "
import requests
import json
import sys
from datetime import datetime, timedelta

PROMETHEUS_URL = '${PROMETHEUS_URL}'

def query_metric(query, days=30):
    '''查询指标数据'''
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)

    try:
        response = requests.get(f'{PROMETHEUS_URL}/api/v1/query_range', params={
            'query': query,
            'start': start_time.timestamp(),
            'end': end_time.timestamp(),
            'step': '3600'  # 1小时
        }, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f'查询失败 {query}: {e}', file=sys.stderr)
        return {'data': {'result': []}}

# 收集关键指标
metrics = {}

# CI/CD相关指标
try:
    # 假设有自定义指标，如果没有则跳过
    metrics['build_duration'] = query_metric('cicd_build_duration_seconds', 30)
    metrics['test_duration'] = query_metric('cicd_test_duration_seconds', 30)
    metrics['deployment_success'] = query_metric('cicd_deployment_success_total', 30)
except:
    pass

# 系统性能指标
metrics['api_response_time'] = query_metric('histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))', 30)
metrics['error_rate'] = query_metric('rate(http_requests_total{status_code=~\"5..\"}[5m]) / rate(http_requests_total[5m]) * 100', 30)
metrics['cpu_usage'] = query_metric('system_cpu_usage_percent', 30)
metrics['memory_usage'] = query_metric('system_memory_usage_percent', 30)

# 保存指标数据
with open('${REPORT_DIR}/prometheus_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2, default=str)

print('Prometheus数据收集完成')
" 2>/dev/null || log_warning "Prometheus数据收集失败"
}

# 分析性能趋势
analyze_performance_trends() {
    log_info "分析性能趋势..."

    python3 -c "
import json
import statistics
from datetime import datetime

# 读取数据
try:
    with open('${REPORT_DIR}/prometheus_metrics.json', 'r') as f:
        metrics = json.load(f)
except FileNotFoundError:
    print('无监控数据，跳过趋势分析')
    exit(0)

analysis = {}

# 分析API响应时间趋势
if metrics.get('api_response_time', {}).get('data', {}).get('result'):
    response_times = []
    for result in metrics['api_response_time']['data']['result']:
        if result.get('values'):
            response_times.extend([float(v[1]) for v in result['values'] if v[1] and str(v[1]) != 'nan'])

    if response_times:
        avg_response = statistics.mean(response_times)
        max_response = max(response_times)
        p95_response = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max_response

        analysis['api_performance'] = {
            'avg_response_time': avg_response,
            'max_response_time': max_response,
            'p95_response_time': p95_response,
            'degradation_detected': avg_response > 2.0  # 超过2秒算性能下降
        }

# 分析错误率趋势
if metrics.get('error_rate', {}).get('data', {}).get('result'):
    error_rates = []
    for result in metrics['error_rate']['data']['result']:
        if result.get('values'):
            error_rates.extend([float(v[1]) for v in result['values'] if v[1] and str(v[1]) != 'nan'])

    if error_rates:
        avg_error_rate = statistics.mean(error_rates)
        max_error_rate = max(error_rates)

        analysis['error_trends'] = {
            'avg_error_rate': avg_error_rate,
            'max_error_rate': max_error_rate,
            'high_error_detected': avg_error_rate > 5.0  # 超过5%算高错误率
        }

# 保存分析结果
with open('${REPORT_DIR}/performance_analysis.json', 'w') as f:
    json.dump(analysis, f, indent=2)

print('性能趋势分析完成')
" 2>/dev/null || log_warning "性能分析失败"
}

# 生成优化建议
generate_optimization_recommendations() {
    log_info "生成优化建议..."

    python3 -c "
import json
import os

recommendations = []

# 读取分析结果
analysis_file = '${REPORT_DIR}/performance_analysis.json'
if os.path.exists(analysis_file):
    try:
        with open(analysis_file, 'r') as f:
            analysis = json.load(f)

        # 基于API性能生成建议
        if 'api_performance' in analysis:
            perf = analysis['api_performance']
            if perf.get('degradation_detected', False):
                recommendations.append({
                    'category': '性能优化',
                    'priority': 'high',
                    'title': 'API响应时间需要优化',
                    'description': f'平均响应时间 {perf[\"avg_response_time\"]:.2f}s 超过2秒目标',
                    'actions': [
                        '优化数据库查询，添加适当索引',
                        '实现API响应缓存',
                        '检查网络延迟和带宽',
                        '考虑使用CDN加速静态资源'
                    ]
                })

        # 基于错误率生成建议
        if 'error_trends' in analysis:
            errors = analysis['error_trends']
            if errors.get('high_error_detected', False):
                recommendations.append({
                    'category': '稳定性优化',
                    'priority': 'high',
                    'title': '系统错误率需要降低',
                    'description': f'平均错误率 {errors[\"avg_error_rate\"]:.2f}% 超过5%阈值',
                    'actions': [
                        '加强错误处理和异常捕获',
                        '优化数据库连接池配置',
                        '增加重试机制和熔断器',
                        '进行压力测试验证系统承载能力'
                    ]
                })

    except Exception as e:
        print(f'读取分析结果失败: {e}')

# CI/CD流程优化建议
recommendations.extend([
    {
        'category': 'CI/CD优化',
        'priority': 'medium',
        'title': '考虑并行化测试执行',
        'description': '当前测试顺序执行可能耗时较长',
        'actions': [
            '将单元测试和集成测试并行执行',
            '使用矩阵策略分发到多个runner',
            '优化测试数据准备和清理',
            '考虑使用测试分片加速执行'
        ]
    },
    {
        'category': '资源优化',
        'priority': 'low',
        'title': '定期清理CI/CD缓存',
        'description': 'Docker层缓存和依赖缓存可能占用过多空间',
        'actions': [
            '设置自动缓存清理策略',
            '定期清理未使用的Docker镜像',
            '优化GitHub Actions缓存配置'
        ]
    }
])

# 保存建议
with open('${REPORT_DIR}/optimization_recommendations.json', 'w') as f:
    json.dump(recommendations, f, indent=2)

print(f'生成了 {len(recommendations)} 条优化建议')
" 2>/dev/null || log_warning "生成优化建议失败"
}

# 生成月度报告
generate_monthly_report() {
    log_info "生成月度优化报告..."

    python3 -c "
import json
import os
from datetime import datetime

report_data = {
    'report_month': '${MONTH}',
    'generated_at': datetime.now().isoformat(),
    'summary': {},
    'recommendations': [],
    'metrics': {}
}

# 读取各种数据
try:
    # 性能分析
    if os.path.exists('${REPORT_DIR}/performance_analysis.json'):
        with open('${REPORT_DIR}/performance_analysis.json', 'r') as f:
            report_data['metrics']['performance'] = json.load(f)

    # 优化建议
    if os.path.exists('${REPORT_DIR}/optimization_recommendations.json'):
        with open('${REPORT_DIR}/optimization_recommendations.json', 'r') as f:
            report_data['recommendations'] = json.load(f)

    # 计算汇总信息
    high_priority = len([r for r in report_data['recommendations'] if r.get('priority') == 'high'])
    medium_priority = len([r for r in report_data['recommendations'] if r.get('priority') == 'medium'])
    low_priority = len([r for r in report_data['recommendations'] if r.get('priority') == 'low'])

    report_data['summary'] = {
        'total_recommendations': len(report_data['recommendations']),
        'high_priority': high_priority,
        'medium_priority': medium_priority,
        'low_priority': low_priority,
        'performance_issues': len([r for r in report_data['recommendations'] if r.get('category') == '性能优化']),
        'stability_issues': len([r for r in report_data['recommendations'] if r.get('category') == '稳定性优化'])
    }

except Exception as e:
    print(f'生成报告时出错: {e}')

# 生成Markdown报告
markdown_report = f'''# MyStocks CI/CD 月度优化报告

**报告月份**: {report_data['report_month']}
**生成时间**: {report_data['generated_at'][:19].replace('T', ' ')}

## 📊 执行总结

- **总建议数**: {report_data['summary'].get('total_recommendations', 0)}
- **高优先级**: {report_data['summary'].get('high_priority', 0)}
- **中优先级**: {report_data['summary'].get('medium_priority', 0)}
- **低优先级**: {report_data['summary'].get('low_priority', 0)}

## 🔍 性能分析

'''

# 添加性能指标
if 'performance' in report_data.get('metrics', {}):
    perf = report_data['metrics']['performance']
    if 'api_performance' in perf:
        api_perf = perf['api_performance']
        markdown_report += f'''### API性能指标
- 平均响应时间: {api_perf.get('avg_response_time', 0):.2f}秒
- 95th百分位: {api_perf.get('p95_response_time', 0):.2f}秒
- 最大响应时间: {api_perf.get('max_response_time', 0):.2f}秒
- 性能状态: {'⚠️ 需要优化' if api_perf.get('degradation_detected', False) else '✅ 正常'}

'''

    if 'error_trends' in perf:
        err_trends = perf['error_trends']
        markdown_report += f'''### 错误率分析
- 平均错误率: {err_trends.get('avg_error_rate', 0):.2f}%
- 最高错误率: {err_trends.get('max_error_rate', 0):.2f}%
- 稳定性状态: {'⚠️ 需要改进' if err_trends.get('high_error_detected', False) else '✅ 稳定'}

'''

# 添加优化建议
markdown_report += '''## 💡 优化建议

'''

for i, rec in enumerate(report_data.get('recommendations', []), 1):
    priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(rec.get('priority'), '⚪')
    markdown_report += f'''### {i}. {priority_icon} {rec.get('title', '')}

**优先级**: {rec.get('priority', '').upper()}
**类别**: {rec.get('category', '')}

{rec.get('description', '')}

**建议措施**:
'''
    for action in rec.get('actions', []):
        markdown_report += f'''- {action}
'''

    markdown_report += '''
'''

# 添加执行计划
markdown_report += '''## 📅 执行计划

### 本月重点任务
1. **高优先级建议**: 立即执行，安排专人负责
2. **中优先级建议**: 本月内完成，纳入Sprint计划
3. **低优先级建议**: 视情况排期，持续改进

### 跟踪机制
- 建立优化任务跟踪表
- 每周review进展
- 月末评估优化效果

## 📞 联系方式

如有问题请联系：
- **DevOps团队**: devops@mystocks.local
- **技术负责人**: tech-lead@mystocks.local

---
*此报告由自动化脚本生成，如有疑问请查看详细数据文件*
'''

# 保存Markdown报告
with open('${REPORT_DIR}/monthly_optimization_report.md', 'w', encoding='utf-8') as f:
    f.write(markdown_report)

# 保存完整JSON数据
with open('${REPORT_DIR}/monthly_report_data.json', 'w', encoding='utf-8') as f:
    json.dump(report_data, f, indent=2, ensure_ascii=False)

print('月度优化报告生成完成')
" 2>/dev/null || log_warning "生成月度报告失败"
}

# 发送报告通知
send_report_notification() {
    log_info "发送报告通知..."

    if [ -f "${REPORT_DIR}/monthly_optimization_report.md" ]; then
        # 这里可以集成各种通知方式

        # 示例：发送到Slack或企业微信
        # curl -X POST "$WEBHOOK_URL" \
        #      -H "Content-Type: application/json" \
        #      -d "{\"text\": \"MyStocks ${MONTH} CI/CD优化报告已生成\"}"

        log_success "报告通知发送完成"
    else
        log_warning "报告文件不存在，跳过通知"
    fi
}

# 主函数
main() {
    log_info "开始MyStocks CI/CD月度优化审查..."
    log_info "报告月份: $MONTH"
    log_info "报告目录: $REPORT_DIR"

    # 执行各阶段
    collect_github_actions_stats
    collect_prometheus_metrics
    analyze_performance_trends
    generate_optimization_recommendations
    generate_monthly_report
    send_report_notification

    log_success "CI/CD月度优化审查完成"
    log_info "报告位置: $REPORT_DIR"
    log_info "查看报告: cat $REPORT_DIR/monthly_optimization_report.md"
}

# 如果脚本被直接运行，则执行主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main
fi