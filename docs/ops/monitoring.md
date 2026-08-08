# 监控指南

> **版本**: 1.0 | **更新日期**: 2026-07-12
> **维护者**: 运维
> **合并来源**: `operations/monitoring/MONITORING_GUIDE.md` + `MYSTOCKS_MONITORING_OPTIMIZATION_DEPLOYMENT.md` + `告警规则设置方法.md` + `INDEX.md`
> **子系统文档**: [异步监控](operations/monitoring/ASYNC_MONITORING_GUIDE.md) | [信号指标设计](operations/monitoring/SIGNAL_MONITORING_METRICS_DESIGN.md) | [适配器日志监控](operations/monitoring/TMUX_LNAV_ADAPTER_MONITORING.md)

---

## 概述

MyStocks 监控栈基于 Prometheus + Grafana + Loki + Tempo 四件套构建，覆盖指标采集、日志聚合、分布式追踪与可视化告警。

```
┌─────────────────────────────────────────────────────────────────┐
│                        Monitoring Stack                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Prometheus│  │ Grafana  │  │   Loki   │  │  Tempo   │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │             │             │              │
│       └─────────────┴─────────────┴─────────────┘              │
│                         │                                      │
│              ┌──────────┴──────────┐                           │
│              │   MyStocks API      │                           │
│              │   (Metrics + Logs   │                           │
│              │    + Traces)        │                           │
│              └─────────────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 核心组件

### Prometheus

**配置**: `config/monitoring/prometheus.yml` / `monitoring-stack/config/`

**暴露指标** (`/metrics`):

| 指标 | 类型 | 说明 |
|------|------|------|
| `http_request_duration_seconds` | Histogram | 请求延迟分布 |
| `http_requests_total` | Counter | 请求计数(按端点/方法) |
| `http_requests_active` | Gauge | 活跃请求数 |
| `slow_http_requests_total` | Counter | 慢请求计数(>300ms) |
| `cache_hits_total` | Counter | 缓存命中数 |
| `cache_misses_total` | Counter | 缓存未命中数 |
| `cache_evictions_total` | Counter | 缓存驱逐数 |

### Grafana

**Dashboard**: `config/monitoring/dashboards/api-overview.json`

**面板**: Request Rate、P95 Latency、Error Rate、Cache Hit Rate、SLO Status

### Loki (日志聚合)

**配置**: `config/monitoring/loki-config.yaml`

```json
{
  "timestamp": "2025-12-27T10:30:00.000Z",
  "level": "INFO",
  "message": "Request processed",
  "trace_id": "abc123",
  "request_id": "xyz789",
  "service": "mystocks-api",
  "environment": "production"
}
```

### Tempo (分布式追踪)

**配置**: `config/monitoring/tempo-config.yaml`

**Trace 属性**: `http.method` / `http.url` / `http.status_code` / `trace_id`

**OTel 采样率**: 10% (`monitoring-stack/.env.monitoring`)

---

## SLO 定义

| 指标 | 目标 | 测量周期 |
|------|------|----------|
| 可用性 (Availability) | ≥99.9% | 30 天 |
| P95 延迟 | ≤300ms | 30 天 |
| 错误率 | ≤0.1% | 30 天 |

---

## 部署步骤

### 1. 启动监控栈

```bash
cd /opt/claude/mystocks_spec/monitoring-stack
docker-compose down          # 停止现有容器
docker-compose up -d         # 重启所有服务
```

### 2. 单独启动各组件(调试用)

```bash
# Prometheus
docker run -d --name prometheus -p 9090:9090 \
  -v $(pwd)/config/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Grafana
docker run -d --name grafana -p 3000:3000 grafana/grafana

# Loki
docker run -d --name loki -p 3100:3100 \
  -v $(pwd)/config/monitoring/loki-config.yaml:/etc/loki/loki-config.yaml \
  grafana/loki

# Tempo
docker run -d --name tempo -p 3200:3200 -p 4317:4317 -p 4318:4318 \
  -v $(pwd)/config/monitoring/tempo-config.yaml:/etc/tempo/tempo-config.yaml \
  grafana/tempo
```

### 3. 配置告警

```bash
# Prometheus 告警规则
curl -s http://localhost:9090/api/v1/rules | jq '.data.groups[] | {name,rules:length}'

# AlertManager
curl -s http://localhost:9093/api/v2/status | jq '.cluster'
```

---

## 告警规则

### 严重告警 (Critical)

| 规则 | 条件 | 说明 |
|------|------|------|
| VeryHighErrorRate | 错误率 > 5% 持续 1 分钟 | 服务异常 |
| VeryHighLatency | P95 延迟 > 1s 持续 2 分钟 | 性能劣化 |

### 警告告警 (Warning)

| 规则 | 条件 | 说明 |
|------|------|------|
| HighErrorRate | 错误率 > 1% 持续 2 分钟 | 错误率偏高 |
| HighLatency | P95 延迟 > 300ms 持续 5 分钟 | 延迟偏高 |
| HighCacheMissRate | 缓存未命中率 > 50% | 缓存失效 |
| SlowRequestsDetected | 5 分钟内 >10 条慢请求 | 慢请求突增 |

### Trading Signals 告警规则组 (19 条)

配置位置: `config/alerts/mystocks-alerts.yml`

| 规则组 | 规则数 | 覆盖 |
|--------|--------|------|
| trading_signals_alerts | 12 | 信号准确度、策略健康、生成速率、延迟、数量、质量 |
| system_resources_alerts | 4 | CPU 使用率、内存使用 |
| trading_performance_alerts | 3 | HTTP 延迟、缓存命中、WebSocket 连接 |

> Prometheus 配置中使用 `host.docker.internal:8020` 访问宿主机后端服务，需添加 `--add-host=host.docker.internal:host-gateway`。

---

## 验证命令

### 追踪数据验证

```bash
# Tempo 接收追踪数据
curl -s "http://localhost:3200/api/search?tags=service.name=mystocks-backend&limit=5" | jq '.traces[0]'

# Tempo metrics 被 Prometheus 抓取
curl -s "http://localhost:9090/api/v1/query?query=traces_span_processed_total" | jq '.data.result[0].value[1]'

# 采样率生效验证
docker exec mystocks-tempo env | grep OTEL_TRACES_SAMPLER
# 预期: OTEL_TRACES_SAMPLER=parentbased_traceid_ratio / OTEL_TRACES_SAMPLER_ARG=0.1
```

### 告警验证

```bash
# 活跃告警列表
curl -s http://localhost:9090/api/v1/alerts | jq '.data | group_by(.labels.alertname) | map({alert:.[0].labels.alertname,count:length})'

# 告警规则加载状态
curl -s http://localhost:9090/api/v1/rules | jq '.data.groups[] | select(.name | contains("tracing")) | .name'

# 业务指标查询
curl -s "http://localhost:9090/api/v1/query?query=rate(mystocks_http_requests_total[5m])" | jq '.data.result[0]'
```

### 资源使用验证

```bash
# 容器资源限制(Prometheus 2G / Tempo 1G)
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" mystocks-prometheus mystocks-tempo

# Tempo 存储使用
docker exec mystocks-tempo du -sh /tmp/tempo/traces
```

### API 性能监控

```bash
# 全部指标
curl http://localhost:8020/metrics

# 过滤延迟
curl http://localhost:8020/metrics | grep http_request_duration_seconds

# P95 延迟桶
curl http://localhost:8020/metrics | grep 'http_request_duration_seconds_bucket.*0\.3'
```

---

## 故障排除

| 症状 | 排查 |
|------|------|
| 高延迟 | Grafana Slow Requests 面板 → 定位慢端点 → 检查缓存命中率 → 检查数据库查询 |
| 高错误率 | Grafana Error Rate 面板 → Loki 日志分析 → 识别错误模式 → 检查系统资源 |
| 缓存失效 | Cache Hit Rate 面板 → 驱逐指标 → Redis 连通性 → 调整 TTL |
| 追踪未导出 | `docker logs mystocks-tempo` → 检查 OTLP 端点 → 验证 OTEL 采样率 |
| 服务依赖图缺失 | 检查 Tempo metrics_generator 配置 → Prometheus targets health |
| 告警规则未生效 | `curl -X POST http://localhost:9090/-/reload` → `promtool check rules` |

### 常见坑点（告警部署）

1. **文件路径**: 使用绝对路径 `/opt/claude/mystocks_spec/config/alerts/`，避免相对路径混淆
2. **网络配置**: 容器访问宿主机用 `host.docker.internal:8020` + `--add-host=host.docker.internal:host-gateway`
3. **权限**: Prometheus 容器用户 `65534:65534` 需对数据目录读写权限
4. **渐进验证**: 先最小配置跑通，再添加复杂规则

---

## 维护

| 项目 | 保留期 |
|------|--------|
| Debug 日志 | 7 天 |
| Error 日志 | 30 天 |
| Traces | 24 小时 (可延长至 7 天) |

- Dashboard 自动刷新: 30 秒
- 每日 Review SLO 状态
- Warning 告警 1 小时内响应
- 每周分析趋势调整阈值

---

## 子系统文档

| 文档 | 说明 | 状态 |
|------|------|------|
| [异步监控系统](operations/monitoring/ASYNC_MONITORING_GUIDE.md) | 事件驱动异步监控，业务延迟降低 33% | 实施完成 |
| [交易信号监控指标](operations/monitoring/SIGNAL_MONITORING_METRICS_DESIGN.md) | 9 个 Prometheus 信号指标 + 装饰器 | 部分实施 |
| [适配器日志监控](operations/monitoring/TMUX_LNAV_ADAPTER_MONITORING.md) | tmux + lnav 日志实时分析 | 实施完成 |

---

## 相关文档

- [运维手册主页](index.md)
- [部署指南](deployment.md)
- [排障指南](troubleshooting.md)
- [监控仓库配置](../../../monitoring-stack/)
