# MyStocks 监控栈部署指南

本监控栈用于展示 Phase 2.4 实现的健康检查和性能指标。

## 📊 监控架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Grafana (3000)                          │
│              ┌─────────────────────────────┐               │
│              │   MyStocks Dashboards     │               │
│              └─────────────────────────────┘               │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                 Prometheus (9090)                          │
│           ┌─────────────────────────────┐                   │
│           │   Pull /metrics endpoint    │                   │
│           └─────────────────────────────┘                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              MyStocks FastAPI (8020)                        │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  /api/metrics     - Prometheus 指标导出              │   │
│   │  /api/system/health    - 系统健康检查              │   │
│   │  /api/monitoring/health - 监控服务健康检查         │   │
│   │  /api/trade/health       - 交易服务健康检查         │   │
│   │  /api/*/health           - 各组件健康检查            │   │
│   └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 快速启动

### 前置要求
- Docker 和 Docker Compose 已安装
- MyStocks FastAPI 后端运行在 `http://localhost:8020`

### 启动监控栈

```bash
cd /opt/claude/mystocks_spec-data-db-audit/config/monitoring-stack

# 创建数据目录
mkdir -p data/{prometheus,grafana,alertmanager}

# 启动服务
docker-compose up -d
```

### 访问地址

| 服务 | 地址 | 凭凭 |
|------|------|------|
| Grafana | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9090 | - |
| AlertManager | http://localhost:9093 | - |

## 📈 可用指标

### 系统指标
- `mystocks_http_requests_total` - HTTP 请求总数
- `mystocks_http_request_duration_seconds` - 请求延迟
- `mystocks_process_cpu_usage_percentage` - CPU 使用率
- `mystocks_process_memory_usage_bytes` - 内存使用量

### 数据库指标
- `mystocks_db_connections_active` - 活跃连接数
- `mystocks_db_connections_idle` - 空闲连接数
- `mystocks_db_query_duration_seconds` - 查询延迟
- `mystocks_db_slow_queries_total` - 慢查询计数

### 缓存指标
- `mystocks_cache_hits_total` - 缓存命中数
- `mystocks_cache_misses_total` - 缓存未命中数
- `mystocks_cache_hit_rate` - 缓存命中率
- `mystocks_cache_memory_usage_bytes` - 缓存内存使用

### 业务指标
- `mystocks_market_data_points_processed` - 市场数据处理量
- `mystocks_trade_orders_total` - 交易订单数
- `mystocks_user_active_sessions` - 活跃用户会话
- `mystocks_alerts_active` - 活跃告警数

### 健康状态指标
- `mystocks_health_status` - 组件健康状态 (1=健康, 0=不健康)
- `mystocks_dependency_availability` - 数据源可用性 (%)

## 🔧 配置说明

### Prometheus 抓取配置

Prometheus 每 15 秒抓取一次指标，配置文件位于 `config/prometheus.yml`：

```yaml
scrape_configs:
  - job_name: 'mystocks-backend'
    static_configs:
      - targets: ['host.docker.internal:8020']
    metrics_path: '/api/metrics'
```

### 健康检查端点

| 端点 | 组件 | 健康状态 |
|------|------|----------|
| `/api/system/health` | 系统核心 | ✅ |
| `/api/monitoring/health` | 监控服务 | ✅ |
| `/api/trade/health` | 交易服务 | ✅ |
| `/api/technical/health` | 技术分析 | ✅ |
| `/api/announcement/health` | 公告监控 | ✅ |
| `/api/multi_source/health` | 多数据源 | ✅ |
| `/api/market/health` | 市场数据 | ✅ |
| `/api/wencai/health` | 问财API | ✅ |
| `/api/tasks/health` | 任务管理 | ✅ |
| `/metrics/health` | Prometheus导出器 | ✅ |

## 📊 仪表板说明

### 1. MyStocks 系统监控概览

展示系统的整体运行状态，包括：
- 后端服务健康状态
- API 请求速率和响应延迟
- 内存和 CPU 使用情况
- 数据库连接池状态
- WebSocket 连接数
- 缓存命中率

### 2. MyStocks 健康状态仪表板

专注于健康状态监控：
- 核心服务健康状态（后端、API、数据库）
- 业务模块健康状态
- 数据源可用性
- 数据完整性指标

## 🔄 更新仪表板

### 手动导入仪表板

1. 登录 Grafana
2. 点击 "+" → "Import"
3. 上传 JSON 文件或粘贴仪表板 ID

### 自动加载仪表板

仪表板已配置为自动加载，位于 `provisioning/dashboards/` 目录。

## 🛑 停止监控栈

```bash
docker-compose down

# 保留数据
# docker-compose down

# 清除数据（慎用）
# docker-compose down -v
```

## 🔍 故障排查

### Prometheus 无法抓取指标

1. 检查后端是否运行：`curl http://localhost:8020/api/metrics`
2. 检查 Docker 网络连接：`docker logs mystocks-prometheus`
3. 对于 Docker Desktop，使用 `host.docker.internal`
4. 对于 Linux，使用 `172.17.0.1` 或宿主机 IP

### Grafana 无法连接 Prometheus

1. 检查 Prometheus 是否运行：`curl http://localhost:9090/-/healthy`
2. 检查 Grafana 数据源配置

## 📝 告警配置（可选）

编辑 `config/alertmanager.yml` 配置邮件或 Webhook 告警：

```yaml
receivers:
  - name: 'default'
    webhook_configs:
      - url: 'http://host.docker.internal:8020/api/alerts/webhook'
```

## 🔗 相关链接

- [Prometheus 文档](https://prometheus.io/docs/)
- [Grafana 文档](https://grafana.com/docs/)
- [Phase 2.4 实现文档](../docs/)
