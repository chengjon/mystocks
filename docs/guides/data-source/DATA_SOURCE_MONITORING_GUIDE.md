# 数据源监控系统集成指南

> **版本**: v2.0
> **创建日期**: 2026-01-02
> **相关组件**: DataSourceManagerV2, Prometheus, Grafana

---

## 📊 概述

数据源监控系统为MyStocks的数据源管理V2提供了完整的可观测性，包括：

- **实时指标**: 数据源可用性、响应时间、成功率
- **健康监控**: 连续失败次数、质量评分、健康状态
- **调用统计**: 总调用次数、记录数分布、错误率
- **可视化仪表板**: Grafana仪表板展示所有关键指标

---

## 🎯 核心组件

### 1. Prometheus Metrics Exporter

**文件**: `src/monitoring/data_source_metrics.py`

**功能**:
- 定义10种Prometheus指标类型（Gauge, Counter, Histogram, Info）
- 提供便捷的更新接口
- 自动暴露`/metrics`端点给Prometheus抓取

**指标列表**:

| 指标名称 | 类型 | 标签 | 说明 |
|---------|------|------|------|
| `data_source_up` | Gauge | endpoint_name, source_name, data_category | 数据源可用性（1=可用，0=不可用） |
| `data_source_response_time_seconds` | Histogram | endpoint_name, source_name | 响应时间分布（p50/p95/p99） |
| `data_source_calls_total` | Counter | endpoint_name, source_name, status | 调用总次数（按成功/失败分类） |
| `data_source_record_count` | Histogram | endpoint_name, source_name | 返回记录数分布 |
| `data_source_success_rate` | Gauge | endpoint_name, source_name | 成功率（百分比） |
| `data_source_health_status` | Gauge | endpoint_name, source_name | 健康状态（3=健康，2=降级，1=失败，0=未知） |
| `data_source_quality_score` | Gauge | endpoint_name, source_name | 质量评分（0-10） |
| `data_source_consecutive_failures` | Gauge | endpoint_name, source_name | 连续失败次数 |
| `data_source_total_calls` | Gauge | endpoint_name, source_name | 总调用次数 |
| `data_source_info` | Info | endpoint_name, source_name | 数据源元数据 |

### 2. Grafana Dashboard

**文件**: `monitoring-stack/grafana-dashboards/data_source_monitoring.json`

**包含12个面板**:
1. 数据源可用性状态（Stat）
2. 数据源调用速率QPS（Time Series）
3. 数据源健康状态（Stat）
4. 数据源响应时间分布（Time Series - P50/P95/P99）
5. 数据源成功率趋势（Time Series）
6. 数据源质量评分（Stat）
7. 连续失败次数（Stat）
8. 总调用次数（Stat）
9. 数据源分布按来源（Pie Chart）
10. 数据源分布按分类（Donut Chart）
11. 数据源调用统计表（Table）
12. 数据源返回记录数热力图（Heatmap）

### 3. Metrics Server Startup Script

**文件**: `scripts/runtime/start_metrics_server.py`

**功能**:
- 启动Prometheus metrics HTTP服务器（端口8001）
- 从PostgreSQL注册表加载所有数据源
- 初始化所有数据源的metrics
- 持续暴露`/metrics`端点

---

## 🚀 快速开始

### Step 1: 启动Metrics服务器

**方法1: 直接运行**
```bash
cd /opt/claude/mystocks_spec
python scripts/runtime/start_metrics_server.py
```

**方法2: 后台运行**
```bash
nohup python scripts/runtime/start_metrics_server.py > var/log/metrics_server.log 2>&1 &
```

**方法3: 使用PM2管理（推荐）**
```bash
pm2 start scripts/runtime/start_metrics_server.py --name mystocks-metrics
pm2 save
```

**验证启动**:
```bash
# 检查端口
lsof -i :8001

# 查看metrics
curl http://localhost:8001/metrics

# 预期输出
# HELP data_source_up 数据源是否可用（1=可用，0=不可用）
# TYPE data_source_up gauge
data_source_up{data_category="DAILY_KLINE",endpoint_name="akshare.stock_zh_a_hist",source_name="akshare"} 1.0
...
```

### Step 2: 确认Prometheus已配置抓取

**检查配置文件**: `monitoring-stack/config/prometheus.yml`

**已包含的抓取任务**:
```yaml
- job_name: 'mystocks-data-sources'
  static_configs:
    - targets:
        - 'host.docker.internal:8001'  # 数据源指标服务器端口
      labels:
        service: 'mystocks-data-sources'
        component: 'data-source-manager'

  metrics_path: '/metrics'
  scrape_interval: 30s
```

**重启Prometheus（如需要）**:
```bash
cd /opt/claude/mystocks_spec/monitoring-stack
docker-compose restart prometheus
```

**验证抓取**:
1. 访问 Prometheus: http://localhost:9090
2. 进入 "Status" → "Targets"
3. 查找 `mystocks-data-sources` 任务
4. 确认状态为 "UP"

### Step 3: 导入Grafana仪表板

**方法1: 通过UI导入**
1. 访问 Grafana: http://localhost:3000
2. 登录（admin / mystocks2025）
3. 点击 "+" → "Import"
4. 上传JSON文件: `monitoring-stack/grafana-dashboards/data_source_monitoring.json`
5. 点击 "Import"

**方法2: 自动 provisioning（推荐）**

配置文件已存在于 `monitoring-stack/provisioning/dashboards/`，Grafana会自动加载。

**验证导入**:
1. 访问 Grafana: http://localhost:3000
2. 点击 "Dashboards" → "Manage"
3. 查找 "MyStocks 数据源监控仪表板"
4. 打开仪表板查看指标

### Step 4: 在代码中使用metrics

**示例1: 记录数据源调用**
```python
from src.monitoring.data_source_metrics import update_call_metrics
import time

# 调用数据源
start_time = time.time()
try:
    data = fetch_data_from_api("akshare", "stock_zh_a_hist", symbol="000001")
    response_time = time.time() - start_time

    # 记录成功调用
    update_call_metrics(
        endpoint_name="akshare.stock_zh_a_hist",
        source_name="akshare",
        data_category="DAILY_KLINE",
        success=True,
        response_time=response_time,
        record_count=len(data)
    )
except Exception as e:
    response_time = time.time() - start_time

    # 记录失败调用
    update_call_metrics(
        endpoint_name="akshare.stock_zh_a_hist",
        source_name="akshare",
        data_category="DAILY_KLINE",
        success=False,
        response_time=response_time,
        error_msg=str(e)
    )
```

**示例2: 更新健康状态**
```python
from src.monitoring.data_source_metrics import update_health_metrics

# 健康检查后更新状态
def perform_health_check(endpoint_name):
    result = check_api_health(endpoint_name)

    update_health_metrics(
        endpoint_name=endpoint_name,
        source_name="akshare",
        data_category="DAILY_KLINE",
        health_status=result['health_status'],  # healthy/degraded/failed/unknown
        quality_score=result['quality_score'],  # 0-10
        success_rate=result['success_rate'],    # 0-100
        consecutive_failures=result['consecutive_failures'],
        total_calls=result['total_calls']
    )
```

**示例3: 批量更新（从注册表）**
```python
from src.monitoring.data_source_metrics import update_all_from_registry
from src.core.data_source_manager_v2 import DataSourceManagerV2

manager = DataSourceManagerV2()

# 获取所有数据源
registry_dict = manager.registry

# 批量更新所有metrics
update_all_from_registry(registry_dict)
```

---

## 📋 监控指标说明

### 关键指标解读

#### 1. 数据源可用性 (`data_source_up`)

**值**:
- `1` - 数据源可用
- `0` - 数据源不可用

**监控**: 应该始终为1，如果为0说明数据源出现问题

**告警建议**: 连续3次抓取为0时触发告警

#### 2. 响应时间分布 (`data_source_response_time_seconds`)

**关键分位数**:
- P50 (中位数): 50%的调用在这个时间内完成
- P95: 95%的调用在这个时间内完成
- P99: 99%的调用在这个时间内完成

**正常范围**:
- Mock数据: < 0.1秒
- 本地数据库: < 0.5秒
- 外部API: 1-5秒（取决于网络和数据量）

**告警建议**: P95 > 10秒时触发告警

#### 3. 成功率 (`data_source_success_rate`)

**值**: 0-100%

**正常范围**: > 95%

**告警建议**:
- 警告: < 95%
- 严重: < 80%

#### 4. 连续失败次数 (`data_source_consecutive_failures`)

**值**: 非负整数

**告警建议**:
- 警告: >= 3
- 严重: >= 5

#### 5. 健康状态 (`data_source_health_status`)

**值映射**:
- `3` = healthy（健康）
- `2` = degraded（降级）
- `1` = failed（失败）
- `0` = unknown（未知）

**告警建议**: 状态为1（failed）时立即告警

#### 6. 质量评分 (`data_source_quality_score`)

**值**: 0-10

**评分标准**:
- `9-10`: 优秀（快速、稳定、数据完整）
- `7-8`: 良好
- `5-6`: 一般
- `0-4`: 差（需要优化或替换）

---

## 🔍 故障排查

### 问题1: Metrics服务器无法启动

**症状**: `Address already in use`

**解决**:
```bash
# 查找占用端口的进程
lsof -i :8001

# 杀死进程
kill -9 <PID>

# 或使用其他端口
METRICS_PORT=8002 python scripts/runtime/start_metrics_server.py
```

### 问题2: Prometheus无法抓取metrics

**症状**: Prometheus Targets页面显示 `mystocks-data-sources` 为 `DOWN`

**排查步骤**:

1. **确认metrics服务器正在运行**
   ```bash
   curl http://localhost:8001/metrics
   ```

2. **从Prometheus容器内部测试**
   ```bash
   docker exec -it mystocks-prometheus sh
   wget -O- http://host.docker.internal:8001/metrics
   ```

3. **检查Docker网络配置**
   - Linux Docker: 需要使用 `localhost:8001` 而不是 `host.docker.internal:8001`
   - 修改 `monitoring-stack/config/prometheus.yml`

4. **查看Prometheus日志**
   ```bash
   docker logs mystocks-prometheus -f
   ```

### 问题3: Grafana仪表板没有数据

**症状**: 仪表板导入成功但所有面板显示 "No data"

**排查步骤**:

1. **确认Prometheus有数据**
   - 访问 http://localhost:9090
   - 执行查询: `up{job="mystocks-data-sources"}`
   - 应该看到数据

2. **检查Grafana数据源配置**
   - Configuration → Data Sources → Prometheus
   - 确认URL正确: `http://prometheus:9090`
   - 点击 "Test" 应该显示 "Data source is working"

3. **检查仪表板时间范围**
   - 确保选择了正确的时间范围（如 "Last 1 hour"）
   - 点击仪表板右上角的刷新按钮

---

## 📈 最佳实践

### 1. 生产环境部署

**使用PM2管理metrics服务器**
```bash
pm2 start scripts/runtime/start_metrics_server.py \
  --name mystocks-metrics \
  --max-memory-restart 200M \
  --restart-delay 5000

pm2 save
pm2 startup
```

**配置自动重启**
```bash
# 监控metrics服务器
pm2 monit

# 查看日志
pm2 logs mystocks-metrics
```

### 2. 与DataSourceManagerV2集成

**DataSourceManagerV2已内置监控集成**:

```python
from src.core.data_source_manager_v2 import DataSourceManagerV2

manager = DataSourceManagerV2()

# 每次调用会自动记录metrics
data = manager.get_stock_daily(symbol="000001")

# 自动更新:
# - data_source_calls_total
# - data_source_response_time_seconds
# - data_source_record_count
# - data_source_up
```

**手动健康检查**:
```python
# 检查所有数据源
health = manager.health_check()

# 查看结果
print(f"总计: {health['total']}")
print(f"健康: {health['healthy']}")
print(f"异常: {health['unhealthy']}")
```

### 3. 定期更新健康状态

**创建定时任务**:
```bash
# 添加到crontab
crontab -e

# 每5分钟检查一次
*/5 * * * * cd /opt/claude/mystocks_spec && python -c "
from src.core.data_source_manager_v2 import DataSourceManagerV2
from src.monitoring.data_source_metrics import update_all_from_registry

manager = DataSourceManagerV2()
health = manager.health_check()
print(f'健康检查完成: {health[\"healthy\"]}/{health[\"total\"]} 健康')
"
```

---

## 🎓 进阶使用

### 自定义Grafana仪表板

**创建新面板**:
1. 打开仪表板编辑模式
2. 添加新查询
3. 使用PromQL查询指标

**常用PromQL查询**:

```promql
# 查看所有数据源的可用性
data_source_up

# 查看响应时间的P95
histogram_quantile(0.95, rate(data_source_response_time_seconds_bucket[5m]))

# 查看成功率
data_source_success_rate > 95

# 查看调用速率
rate(data_source_calls_total[5m])

# 查看错误率
rate(data_source_calls_total{status="failure"}[5m]) / rate(data_source_calls_total[5m])
```

### 配置告警

**在Prometheus中配置告警规则**:

文件: `monitoring-stack/config/rules/data_source_alerts.yml`

```yaml
groups:
  - name: data_source_alerts
    interval: 30s
    rules:
      # 数据源不可用告警
      - alert: DataSourceDown
        expr: data_source_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "数据源 {{ $labels.endpoint_name }} 不可用"
          description: "数据源 {{ $labels.endpoint_name }} 已经连续1分钟不可用"

      # 成功率低告警
      - alert: LowSuccessRate
        expr: data_source_success_rate < 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "数据源 {{ $labels.endpoint_name }} 成功率低"
          description: "成功率 {{ $value }}% 低于80%"

      # 响应时间长告警
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(data_source_response_time_seconds_bucket[5m])) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "数据源 {{ $labels.endpoint_name }} 响应慢"
          description: "P95响应时间 {{ $value }}秒 超过10秒"
```

---

## 📚 相关文档

- **数据源管理V2设计文档**: `docs/architecture/DATA_SOURCE_MANAGEMENT_V2.md`
- **实施报告**: `docs/reports/DATA_SOURCE_V2_IMPLEMENTATION_REPORT.md`
- **Prometheus配置**: `monitoring-stack/config/prometheus.yml`
- **Grafana仪表板**: `monitoring-stack/grafana-dashboards/data_source_monitoring.json`

---

## 🔗 快速链接

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **Metrics端点**: http://localhost:8001/metrics（服务器启动后）

---

**文档版本**: v1.0
**最后更新**: 2026-01-02
**维护者**: Main CLI
