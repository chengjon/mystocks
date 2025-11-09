# MyStocks监控系统配置指南

**Feature**: 007 - 短期优化改进
**Phase**: 2 - Grafana监控配置
**完成日期**: 2025-10-16
**负责人**: JohnC & Claude

---

## 📋 概览

本文档说明如何配置MyStocks系统的Prometheus + Grafana监控体系。

### 监控架构

```
MyStocks Backend (port 8000)
    ↓ /api/metrics
Prometheus (port 9090)
    ↓ 数据存储和查询
Grafana (port 3001)
    ↓ 可视化
Alert Manager (port 9093)
    ↓ 告警通知
```

---

## 🚀 快速开始

### 前置要求

- Docker和Docker Compose已安装
- MyStocks Backend服务运行中
- 端口可用：9090 (Prometheus), 3001 (Grafana), 9093 (Alertmanager)

### 一键启动（推荐）

```bash
cd /opt/claude/mystocks_spec/monitoring
docker-compose up -d
```

### 访问地址

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
  - 默认用户名: admin
  - 默认密码: admin
- **Alertmanager**: http://localhost:9093

---

## 📦 组件安装

### 1. 安装Python依赖

```bash
cd /opt/claude/mystocks_spec
pip install prometheus-client
```

### 2. 验证Metrics端点

```bash
# 启动Backend服务
cd web/backend
python app/main.py

# 新终端测试metrics端点
curl http://localhost:8000/api/metrics
```

**预期输出**:
```
# HELP mystocks_http_requests_total Total HTTP requests
# TYPE mystocks_http_requests_total counter
mystocks_http_requests_total{endpoint="/api/system/health",method="GET",status="200"} 42.0
...
```

### 3. 使用Docker Compose启动监控栈

创建 `monitoring/docker-compose.yml`:

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: mystocks-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./prometheus/alerts:/etc/prometheus/alerts
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: unless-stopped
    networks:
      - mystocks-monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: mystocks-grafana
    ports:
      - "3001:3000"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    restart: unless-stopped
    networks:
      - mystocks-monitoring

  alertmanager:
    image: prom/alertmanager:latest
    container_name: mystocks-alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager/config.yml:/etc/alertmanager/config.yml
      - alertmanager-data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/config.yml'
    restart: unless-stopped
    networks:
      - mystocks-monitoring

networks:
  mystocks-monitoring:
    driver: bridge

volumes:
  prometheus-data:
  grafana-data:
  alertmanager-data:
```

### 4. 启动服务

```bash
cd /opt/claude/mystocks_spec/monitoring
docker-compose up -d
```

### 5. 验证服务状态

```bash
# 检查容器状态
docker-compose ps

# 预期输出:
# NAME                   STATUS
# mystocks-prometheus    Up
# mystocks-grafana       Up
# mystocks-alertmanager  Up
```

---

## 📊 Grafana配置

### 配置Prometheus数据源

1. 访问 http://localhost:3001
2. 登录（admin/admin）
3. 进入 Configuration → Data Sources
4. 点击 "Add data source"
5. 选择 "Prometheus"
6. 配置：
   - Name: `Prometheus`
   - URL: `http://prometheus:9090`
   - Access: `Server`
7. 点击 "Save & Test"

### 导入仪表板

**方法1: 使用JSON文件**

1. 进入 Dashboards → Import
2. 上传 `monitoring/grafana/dashboards/mystocks-overview.json`
3. 选择Prometheus数据源
4. 点击 "Import"

**方法2: 使用仪表板ID**

1. 进入 Dashboards → Import
2. 输入仪表板ID: `1860` (Node Exporter Full)
3. 点击 "Load"
4. 选择Prometheus数据源
5. 点击 "Import"

### 仪表板面板说明

**MyStocks System Overview** 仪表板包含6个面板：

1. **HTTP Requests per Second**
   - 每秒HTTP请求数
   - 按方法、端点、状态码分组

2. **HTTP Request Duration (95th percentile)**
   - HTTP请求延迟（95分位）
   - 按方法和端点分组

3. **Database Connections**
   - 数据库连接数（活跃/空闲）
   - 监控MySQL, PostgreSQL, TDengine, Redis

4. **Cache Hit Rate**
   - 缓存命中率（百分比）
   - 计算公式: hits / (hits + misses) * 100

5. **API Health Status**
   - API健康状态
   - 1=健康, 0=不健康

6. **Data Source Availability**
   - 数据源可用性
   - 监控TDX, AkShare, Financial, BaoStock

---

## 🔔 告警配置

### 告警规则说明

已配置的告警规则（`prometheus/alerts/mystocks-alerts.yml`）：

#### API告警

1. **HighAPILatency** (warning)
   - 触发条件: 95分位响应时间 > 500ms，持续2分钟
   - 说明: API响应时间过高

2. **HighAPIErrorRate** (critical)
   - 触发条件: 5xx错误率 > 5%，持续2分钟
   - 说明: API错误率过高

#### 数据库告警

3. **HighDatabaseConnections** (warning)
   - 触发条件: 活跃连接数 > 50，持续5分钟
   - 说明: 数据库连接数过高

4. **DatabaseDown** (critical)
   - 触发条件: 数据库健康检查失败，持续1分钟
   - 说明: 数据库服务不可用

#### 服务告警

5. **BackendDown** (critical)
   - 触发条件: Backend服务无法访问，持续1分钟
   - 说明: Backend服务宕机

6. **APIHealthCheckFailed** (warning)
   - 触发条件: API健康检查失败，持续2分钟
   - 说明: API健康检查失败

#### 数据源告警

7. **DataSourceUnavailable** (warning)
   - 触发条件: 数据源不可用，持续5分钟
   - 说明: 数据源连接失败

#### 缓存告警

8. **LowCacheHitRate** (info)
   - 触发条件: 缓存命中率 < 50%，持续10分钟
   - 说明: 缓存效率较低

### 配置告警通知

编辑 `monitoring/alertmanager/config.yml`:

```yaml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default-receiver'

receivers:
  - name: 'default-receiver'
    email_configs:
      - to: 'admin@example.com'
        from: 'alertmanager@example.com'
        smarthost: 'smtp.example.com:587'
        auth_username: 'alertmanager@example.com'
        auth_password: 'password'

  - name: 'webhook-receiver'
    webhook_configs:
      - url: 'http://localhost:5001/webhook'
```

重启Alertmanager:
```bash
docker-compose restart alertmanager
```

---

## 📈 使用指南

### 日常监控

**查看实时指标**:
1. 打开Grafana仪表板
2. 查看各面板实时数据
3. 调整时间范围（右上角）

**查看历史数据**:
1. 在Prometheus中执行PromQL查询
2. 例如: `rate(mystocks_http_requests_total[5m])`

**检查告警**:
1. 访问 http://localhost:9093 (Alertmanager)
2. 查看当前触发的告警
3. 确认或静默告警

### 常用PromQL查询

**HTTP请求率**:
```promql
rate(mystocks_http_requests_total[5m])
```

**平均响应时间**:
```promql
rate(mystocks_http_request_duration_seconds_sum[5m]) / rate(mystocks_http_request_duration_seconds_count[5m])
```

**错误率**:
```promql
rate(mystocks_http_requests_total{status=~"5.."}[5m]) / rate(mystocks_http_requests_total[5m])
```

**数据库连接总数**:
```promql
mystocks_db_connections_active + mystocks_db_connections_idle
```

**缓存命中率**:
```promql
rate(mystocks_cache_hits_total[5m]) / (rate(mystocks_cache_hits_total[5m]) + rate(mystocks_cache_misses_total[5m]))
```

---

## 🔧 高级配置

### 自定义指标

在Backend代码中添加自定义指标：

```python
from app.api.metrics import Counter, Histogram, Gauge

# 定义新指标
custom_metric = Counter(
    'mystocks_custom_metric_total',
    'Custom metric description',
    ['label1', 'label2']
)

# 使用指标
custom_metric.labels(label1='value1', label2='value2').inc()
```

### 添加新面板

1. 在Grafana中创建新面板
2. 编写PromQL查询
3. 配置可视化选项
4. 导出仪表板JSON
5. 保存到 `monitoring/grafana/dashboards/`

### 集成第三方Exporter

**Node Exporter** (系统指标):
```bash
docker run -d \
  --name=node-exporter \
  --net="host" \
  --pid="host" \
  -v "/:/host:ro,rslave" \
  prom/node-exporter:latest \
  --path.rootfs=/host
```

**MySQL Exporter**:
```bash
docker run -d \
  --name=mysql-exporter \
  -p 9104:9104 \
  -e DATA_SOURCE_NAME="user:password@(localhost:3306)/" \
  prom/mysqld-exporter:latest
```

---

## 🐛 故障排查

### 问题1: Prometheus无法采集指标

**症状**: Prometheus Target显示"Down"

**排查步骤**:
1. 检查Backend服务是否运行: `curl http://localhost:8000/api/metrics`
2. 检查Prometheus配置: `docker exec mystocks-prometheus cat /etc/prometheus/prometheus.yml`
3. 查看Prometheus日志: `docker logs mystocks-prometheus`
4. 验证网络连接: `docker exec mystocks-prometheus wget -O- http://host.docker.internal:8000/api/metrics`

**解决方案**:
```yaml
# 修改prometheus.yml中的targets
scrape_configs:
  - job_name: 'mystocks-backend'
    static_configs:
      - targets: ['host.docker.internal:8000']  # Docker for Mac/Windows
      # - targets: ['172.17.0.1:8000']  # Docker on Linux
```

### 问题2: Grafana无法连接Prometheus

**症状**: Data source测试失败

**排查步骤**:
1. 检查Prometheus是否运行: `docker ps | grep prometheus`
2. 测试连接: `docker exec mystocks-grafana wget -O- http://prometheus:9090`
3. 检查Docker网络: `docker network inspect mystocks-monitoring_mystocks-monitoring`

**解决方案**:
- 确保Prometheus和Grafana在同一网络
- 使用容器名称而非localhost

### 问题3: 告警未触发

**症状**: 符合条件但没有收到告警

**排查步骤**:
1. 检查告警规则: 访问 http://localhost:9090/alerts
2. 检查Alertmanager状态: `docker logs mystocks-alertmanager`
3. 验证告警规则语法: `promtool check rules alerts/mystocks-alerts.yml`

---

## ✅ 验收标准

### Phase 2成功标准

| 标准 | 要求 | 验证方法 | 状态 |
|------|------|---------|------|
| **Metrics端点** | /api/metrics可访问 | curl测试 | ✅ |
| **Prometheus运行** | 可访问9090端口 | 浏览器访问 | 🔄 待验证 |
| **Grafana运行** | 可访问3001端口 | 浏览器访问 | 🔄 待验证 |
| **仪表板配置** | 3个核心面板 | Grafana查看 | ✅ |
| **告警规则** | 8条规则配置 | Prometheus查看 | ✅ |

---

## 📚 参考资源

**官方文档**:
- [Prometheus文档](https://prometheus.io/docs/)
- [Grafana文档](https://grafana.com/docs/)
- [prometheus-client文档](https://github.com/prometheus/client_python)

**已配置文件**:
- `web/backend/app/api/metrics.py` - Metrics端点
- `monitoring/prometheus/prometheus.yml` - Prometheus配置
- `monitoring/prometheus/alerts/mystocks-alerts.yml` - 告警规则
- `monitoring/grafana/dashboards/mystocks-overview.json` - Grafana仪表板

---

**文档版本**: 1.0
**创建日期**: 2025-10-16
**负责人**: JohnC & Claude
**项目**: MyStocks v2.1+ 短期优化改进 - Phase 2
