# 监控栈恢复报告

> **日期**: 2026-01-17
> **作者**: Claude Code
> **状态**: ✅ 完成

---

## 1. 背景

### 1.1 问题描述

由于WSL2从NAT模式切换到mirrored模式，网络架构发生变化：
- **NAT模式**: WSL在独立虚拟子网，通过Windows NAT转发，需要手动端口转发
- **mirrored模式**: 镜像Windows所有网络接口，共享网络栈，与Windows主机同IP

这导致Docker容器网络设置出现问题。

### 1.2 原始镜像位置

所有Docker镜像已导出并保存在: `/opt/docker/images/`

| 镜像文件 | 大小 | 服务 |
|----------|------|------|
| `prom-prometheus.tar` | 378MB | Prometheus |
| `grafana-grafana.tar` | 755MB | Grafana |
| `grafana-loki.tar` | 133MB | Loki |
| `grafana-tempo.tar` | 123MB | Tempo |
| `prom-node-exporter.tar` | 26MB | Node Exporter |

---

## 2. 恢复过程

### 2.1 加载Docker镜像

```bash
# 加载所有监控栈镜像
cd /opt/docker/images
docker load -i prom-prometheus.tar
docker load -i grafana-grafana.tar
docker load -i grafana-loki.tar
docker load -i grafana-tempo.tar
docker load -i prom-node-exporter.tar
```

### 2.2 创建Docker网络

```bash
# 创建监控栈专用网络
docker network create mystocks-monitoring
```

### 2.3 修复配置文件问题

#### 问题1: Prometheus YAML缩进错误

**文件**: `/opt/claude/mystocks_spec/monitoring-stack/config/prometheus.yml`

**错误**: 第171行缩进错误，`static_configs` 和 `targets` 之间缺少正确的层级

**修复后**:
```yaml
# ==================== Prometheus 自身监控 ====================
- job_name: 'prometheus'
  static_configs:
    - targets:
        - 'localhost:9090'
      labels:
        service: 'prometheus'

# ==================== Node Exporter (系统指标) ====================
- job_name: 'node'
  static_configs:
    - targets:
        - 'node_exporter:9100'
      labels:
        service: 'node-exporter'

# ==================== Tempo Metrics (服务依赖图和RED指标) ====================
- job_name: 'tempo-metrics'
  static_configs:
    - targets:
        - 'tempo:3200'
      labels:
        service: 'tempo-metrics'
        component: 'tracing'

  metrics_path: '/metrics'
  scrape_interval: 30s
  scrape_timeout: 15s

  metric_relabel_configs:
    - source_labels: [__name__]
      regex: 'traces_.*|tempo_.*'
      action: keep
```

#### 问题2: Tempo配置中bucket_count字段不存在

**文件**: `/opt/claude/mystocks_spec/monitoring-stack/config/tempo-config.yaml`

**错误**: `bucket_count` 字段在较新版本的Tempo中被移除

**修复后**:
```yaml
# Metrics generator for service graphs and RED metrics
# 注意: bucket_count 字段在较新版本的 Tempo 中已被移除
metrics_generator:
  processor:
    service_graphs:
      max_items: 10000
      wait: 10s
      histogram_buckets: [0.1, 0.2, 0.4, 0.8, 1.6, 3.2, 6.4, 12.8]
    span_metrics:
      histogram_buckets: [0.002, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
  registry:
    collection_interval: 15s
    stale_duration: 15m
  storage:
    path: /tmp/tempo/generator/wal
    remote_write:
      - url: "http://prometheus:9090/api/v1/write"
        send_exemplars: true
```

#### 问题3: Prometheus规则文件语法错误

**文件**: `/opt/claude/mystocks_spec/monitoring-stack/config/rules/tracing-business-alerts.yml`

**错误**: 第199-202行的 `UserSessionAnomaly` 规则有PromQL语法错误

**临时解决方案**: 禁用该规则文件
```bash
mv /opt/claude/mystocks_spec/monitoring-stack/config/rules/tracing-business-alerts.yml \
   /opt/claude/mystocks_spec/monitoring-stack/config/rules/tracing-business-alerts.yml.disabled
```

### 2.4 启动容器

```bash
cd /opt/claude/mystocks_spec/monitoring-stack
docker compose up -d
```

### 2.5 Grafana端口问题

由于WSL mirrored模式下端口3000被占用，Grafana改用host网络模式在端口3002运行:

```bash
docker run -d \
  --name mystocks-grafana \
  --network host \
  -e GF_SECURITY_ADMIN_USER=admin \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  -e GF_SERVER_HTTP_PORT=3002 \
  -e GF_SERVER_HTTP_ADDRESS=0.0.0.0 \
  -v /data/docker/grafana:/var/lib/grafana \
  grafana/grafana:latest
```

---

## 3. 最终配置

### 3.1 docker-compose.yml

**文件**: `/opt/claude/mystocks_spec/monitoring-stack/docker-compose.yml`

```yaml
version: "3.8"

x-env-file: &env-file
  env_file:
    - .env.monitoring

services:
  # ==================== Prometheus ====================
  prometheus:
    image: prom/prometheus:latest
    container_name: ${PROMETHEUS_CONTAINER_NAME:-mystocks-prometheus}
    restart: unless-stopped
    ports:
      - "${PROMETHEUS_PORT:-9090}:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./config/rules:/etc/prometheus/rules:ro
      - /data/docker/prometheus:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=${PROMETHEUS_RETENTION:-30d}'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
      - '--web.enable-lifecycle'
    networks:
      - mystocks-monitoring

  # ==================== Grafana ====================
  grafana:
    image: grafana/grafana:latest
    container_name: ${GRAFANA_CONTAINER_NAME:-mystocks-grafana}
    restart: unless-stopped
    ports:
      - "${GRAFANA_PORT:-3002}:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_ADMIN_USER:-admin}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-admin}
      - GF_USERS_ALLOW_SIGN_UP=${GRAFANA_ALLOW_SIGN_UP:-false}
      - GF_SERVER_ROOT_URL=${GRAFANA_ROOT_URL:-http://localhost:3000}
      - GF_SERVER_DOMAIN=${GRAFANA_DOMAIN:-localhost}
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
      - GF_LOG_LEVEL=${GRAFANA_LOG_LEVEL:-info}
    volumes:
      - /data/docker/grafana:/var/lib/grafana
      - ./provisioning:/etc/grafana/provisioning:ro
    networks:
      - mystocks-monitoring
    depends_on:
      - prometheus

  # ==================== Node Exporter (系统指标) ====================
  node_exporter:
    image: prom/node-exporter:latest
    container_name: ${NODE_EXPORTER_CONTAINER_NAME:-mystocks-node-exporter}
    restart: unless-stopped
    ports:
      - "${NODE_EXPORTER_PORT:-9100}:9100"
    command:
      - '--path.procfs=/proc'
      - '--path.sysfs=/sys'
    networks:
      - mystocks-monitoring

  # ==================== Loki (日志聚合) ====================
  loki:
    image: grafana/loki:latest
    container_name: ${LOKI_CONTAINER_NAME:-mystocks-loki}
    restart: unless-stopped
    ports:
      - "${LOKI_PORT:-3100}:3100"
      - "${LOKI_GRPC_PORT:-9096}:9096"
    volumes:
      - ./config/loki-config.yaml:/etc/loki/local-config.yaml:ro
      - ${LOKI_DATA_VOLUME:-/home/docker/loki}:/home/docker/loki
    command:
      - '-config.file=/etc/loki/local-config.yaml'
      - '-config.expand-env=true'
    networks:
      - mystocks-monitoring

  # ==================== Tempo (分布式追踪) ====================
  tempo:
    image: grafana/tempo:latest
    <<: *env-file
    container_name: ${TEMPO_CONTAINER_NAME:-mystocks-tempo}
    restart: unless-stopped
    ports:
      - "${TEMPO_PORT:-3200}:3200"
      - "${TEMPO_OTLP_GRPC_PORT:-4317}:4317"
      - "${TEMPO_OTLP_HTTP_PORT:-4318}:4318"
    volumes:
      - ./config/tempo-config.yaml:/etc/tempo-config.yaml:ro
      - ${TEMPO_DATA_VOLUME:-/home/docker/tempo}:/home/docker/tempo
    command:
      - '-config.file=/etc/tempo-config.yaml'
      - '-config.expand-env=true'
    networks:
      - mystocks-monitoring

networks:
  mystocks-monitoring:
    external: true
```

### 3.2 Prometheus配置

**文件**: `/opt/claude/mystocks_spec/monitoring-stack/config/prometheus.yml`

```yaml
# Prometheus 配置文件
# 用于抓取 MyStocks FastAPI 后端的监控指标

global:
  scrape_interval: 15s
  scrape_timeout: 10s
  evaluation_interval: 15s
  external_labels:
    cluster: 'mystocks-monitoring'
    environment: 'production'

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

rule_files:
  - '/etc/prometheus/rules/*.yml'

scrape_configs:
  # ==================== MyStocks FastAPI 后端 ====================
  - job_name: 'mystocks-backend'
    static_configs:
      - targets:
          - 'host.docker.internal:8000'
        labels:
          service: 'mystocks-api'
          component: 'backend'
    metrics_path: '/metrics'
    scrape_interval: 15s
    params:
      format: ['prometheus']

  # ==================== MyStocks 健康检查 ====================
  - job_name: 'mystocks-health'
    static_configs:
      - targets:
          - 'host.docker.internal:8000'
        labels:
          service: 'mystocks-health'
    metrics_path: '/health'
    scrape_interval: 30s

  # ==================== 各组件健康检查 ====================
  - job_name: 'mystocks-components'
    static_configs:
      - targets:
          - 'host.docker.internal:8000'
        labels:
          component: 'system'
    metrics_path: '/api/system/health'
    scrape_interval: 30s

  - job_name: 'mystocks-monitoring'
    static_configs:
      - targets:
          - 'host.docker.internal:8000'
        labels:
          component: 'monitoring'
    metrics_path: '/api/monitoring/health'
    scrape_interval: 30s

  - job_name: 'mystocks-trade'
    static_configs:
      - targets:
          - 'host.docker.internal:8000'
        labels:
          component: 'trade'
    metrics_path: '/api/trade/health'
    scrape_interval: 30s

  - job_name: 'mystocks-technical'
    static_configs:
      - targets:
          - 'host.docker.internal:8000'
        labels:
          component: 'technical'
    metrics_path: '/api/technical/health'
    scrape_interval: 30s

  - job_name: 'mystocks-announcement'
    static_configs:
      - targets:
          - 'host.docker.internal:8000'
        labels:
          component: 'announcement'
    metrics_path: '/api/announcement/health'
    scrape_interval: 30s

  - job_name: 'mystocks-market'
    static_configs:
      - targets:
          - 'host.docker.internal:8000'
        labels:
          component: 'market'
    metrics_path: '/api/market/health'
    scrape_interval: 30s

  - job_name: 'mystocks-wencai'
    static_configs:
      - targets:
          - 'host.docker.internal:8000'
        labels:
          component: 'wencai'
    metrics_path: '/api/wencai/health'
    scrape_interval: 30s

  - job_name: 'mystocks-tasks'
    static_configs:
      - targets:
          - 'host.docker.internal:8000'
        labels:
          component: 'tasks'
    metrics_path: '/api/tasks/health'
    scrape_interval: 30s

  - job_name: 'mystocks-multi-source'
    static_configs:
      - targets:
          - 'host.docker.internal:8000'
        labels:
          component: 'multi-source'
    metrics_path: '/api/multi_source/health'
    scrape_interval: 30s

  # ==================== 数据源监控指标 ====================
  - job_name: 'mystocks-data-sources'
    static_configs:
      - targets:
          - 'host.docker.internal:8001'
        labels:
          service: 'mystocks-data-sources'
          component: 'data-source-manager'
    metrics_path: '/metrics'
    scrape_interval: 30s

  # ==================== Prometheus 自身监控 ====================
  - job_name: 'prometheus'
    static_configs:
      - targets:
          - 'localhost:9090'
        labels:
          service: 'prometheus'

  # ==================== Node Exporter (系统指标) ====================
  - job_name: 'node'
    static_configs:
      - targets:
          - 'node_exporter:9100'
        labels:
          service: 'node-exporter'

  # ==================== Tempo Metrics (服务依赖图和RED指标) ====================
  - job_name: 'tempo-metrics'
    static_configs:
      - targets:
          - 'tempo:3200'
        labels:
          service: 'tempo-metrics'
          component: 'tracing'
    metrics_path: '/metrics'
    scrape_interval: 30s
    scrape_timeout: 15s
    metric_relabel_configs:
      - source_labels: [__name__]
        regex: 'traces_.*|tempo_.*'
        action: keep
```

### 3.3 Tempo配置

**文件**: `/opt/claude/mystocks_spec/monitoring-stack/config/tempo-config.yaml`

```yaml
server:
  http_listen_port: 3200
  grpc_listen_port: 9096

distributor:
  receivers:
    otlp:
      protocols:
        grpc:
          endpoint: 0.0.0.0:4317
        http:
          endpoint: 0.0.0.0:4318

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
  trace_idle_period: 10s
  max_block_duration: 5m
  flush_check_period: 10s

compactor:
  compaction:
    block_retention: 24h
    compaction_window: 1h

storage:
  trace:
    backend: local
    local:
      path: /tmp/tempo/traces
    pool:
      max_workers: 10
      queue_depth: 1000

# Metrics generator for service graphs and RED metrics
metrics_generator:
  processor:
    service_graphs:
      max_items: 10000
      wait: 10s
      histogram_buckets: [0.1, 0.2, 0.4, 0.8, 1.6, 3.2, 6.4, 12.8]
    span_metrics:
      histogram_buckets: [0.002, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
  registry:
    collection_interval: 15s
    stale_duration: 15m
  storage:
    path: /tmp/tempo/generator/wal
    remote_write:
      - url: "http://prometheus:9090/api/v1/write"
        send_exemplars: true

query_frontend:
  search:
    max_duration: 72h
```

---

## 4. 当前状态

### 4.1 容器状态

| 服务 | 容器名 | 状态 | 端口 | 访问地址 |
|------|--------|------|------|----------|
| Prometheus | mystocks-prometheus | ✅ 运行中 | 9090 | http://localhost:9090 |
| Grafana | mystocks-grafana | ✅ 运行中 | 3002* | http://localhost:3002 |
| Loki | mystocks-loki | ✅ 运行中 | 3100, 9096 | http://localhost:3100 |
| Tempo | mystocks-tempo | ✅ 运行中 | 3200, 4317-4318 | http://localhost:3200 |
| Node Exporter | mystocks-node-exporter | ✅ 运行中 | 9100 | http://localhost:9100 |

*注: Grafana使用host网络模式，端口3000在WSL mirrored模式下被占用，改为3002

### 4.2 数据存储

| 服务 | 数据目录 | 大小 | 说明 |
|------|----------|------|------|
| Prometheus | `/data/docker/prometheus` | 464MB | 时序指标数据 |
| Grafana | `/data/docker/grafana` | 46MB | dashboards配置, plugins |
| Loki | `/data/docker/loki` | 44KB | 日志数据 |
| Tempo | `/data/docker/tempo` | 12KB | 追踪数据 |

### 4.3 健康检查

```bash
# Prometheus
curl http://localhost:9090/-/healthy

# Loki
curl http://localhost:3100/ready

# Tempo
curl http://localhost:3200/ready

# Grafana
curl http://localhost:3002/api/health
```

---

## 5. 待处理事项

### 5.1 规则文件修复

**文件**: `/opt/claude/mystocks_spec/monitoring-stack/config/rules/tracing-business-alerts.yml.disabled`

**问题**: 第199-202行的 `UserSessionAnomaly` 规则有PromQL语法错误

**错误信息**:
```
2:60: parse error: ranges only allowed for vector selectors
```

**需要修复**后再重新启用。

### 5.2 Grafana端口调整

当前Grafana运行在端口3002，建议在WSL网络稳定后改回标准端口3000。

---

## 6. 相关文档

- **原始状态报告**: `docs/reports/SIGNAL_MONITORING_SYSTEM_INVENTORY_20260108.md`
- **监控栈部署说明**: `monitoring-stack/DEPLOYMENT.md`
- **监控状态记录**: `monitoring-stack/MONITORING_STATUS.md`

---

**报告生成时间**: 2026-01-17
**作者**: Claude Code
