# Monitoring Stack 部署关键要点总结

## 概述

本文档总结 MyStocks 监控栈 5 个容器的关键配置要点，涵盖 Prometheus、Grafana、Loki、Tempo 和 Node Exporter。

## 目录结构

```
monitoring-stack/
├── docker-compose-loki-tempo.yml    # 主编排文件
├── config/
│   ├── loki-config.yaml            # Loki 配置
│   ├── prometheus.yml              # Prometheus 配置
│   └── tempo-config.yaml           # Tempo 配置
├── data/
│   ├── loki/                       # Loki 数据目录
│   ├── grafana/                    # Grafana 数据目录
│   ├── prometheus/                 # Prometheus 数据目录
│   └── tempo/                      # Tempo 数据目录
└── provisioning/
    ├── datasources/                # Grafana 数据源配置
    └── dashboards/                 # Grafana 仪表板配置
```

---

## 1. Loki 容器（重点）

### 1.1 核心问题背景

**问题症状**: Loki 容器持续重启，错误信息：
```
CONFIG ERROR: tsdb must always have periodic config for index set to 24h
CONFIG ERROR: boltdb-shipper works best with 24h periodic index config
directory required for local rules config
```

**根本原因**:
- Loki 3.x 版本移除了对 `boltdb-shipper` 的默认支持
- TSDB 存储引擎要求 `index.period` 必须为 `24h`
- 缺少 `rules` 目录导致 ruler 模块启动失败

### 1.2 成功配置

**Docker Compose 配置** (`docker-compose-loki-tempo.yml:43-55`):

```yaml
loki:
  image: grafana/loki:latest
  container_name: mystocks-loki
  restart: unless-stopped
  ports:
    - "3100:3100"   # HTTP API
    - "9096:9096"   # gRPC
  volumes:
    - ./config/loki-config.yaml:/etc/loki/local-config.yaml:ro
    - ./data/loki:/tmp/loki
  command: -config.file=/etc/loki/local-config.yaml -validation.allow-structured-metadata=false
  networks:
    - mystocks-monitoring
```

**关键配置选项**:
- `-validation.allow-structured-metadata=false`: 禁用结构化元数据验证，解决兼容性问题
- 端口映射：3100 (HTTP), 9096 (gRPC)

**Loki 配置文件** (`loki-config.yaml`):

```yaml
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /tmp/loki
  storage:
    filesystem:
      chunks_directory: /tmp/loki/chunks
      rules_directory: /tmp/loki/rules
  ring:
    kvstore:
      store: inmemory
  replication_factor: 1

ingester:
  lifecycler:
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1

storage_config:
  tsdb_shipper:
    active_index_directory: /tmp/loki/tsdb-index
    cache_location: /tmp/loki/tsdb-cache
  filesystem:
    directory: /tmp/loki/chunks

schema_config:
  configs:
    - from: 2024-01-01
      store: tsdb                    # ✅ 使用 TSDB（推荐）
      object_store: filesystem
      schema: v13
      index:
        period: 24h                  # ✅ 必须为 24h

limits_config:
  reject_old_samples: true
  reject_old_samples_max_age: 168h

ruler:
  storage:
    local:
      directory: /tmp/loki/rules     # ✅ 必须配置
  rule_path: /tmp/loki/rules
```

### 1.3 Loki 关键配置说明

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `store` | `tsdb` | 推荐使用 TSDB 存储引擎 |
| `schema` | `v13` | 使用最新 schema 版本 |
| `index.period` | `24h` | TSDB 必须设置为 24h |
| `rules_directory` | `/tmp/loki/rules` | 必须创建并配置 |
| `allow_structured_metadata` | `false` | 禁用结构化元数据 |

### 1.4 数据目录权限

```bash
# 创建目录并设置权限
mkdir -p monitoring-stack/data/loki/rules
chmod -R 777 monitoring-stack/data/loki
```

### 1.5 验证 Loki 状态

```bash
# 健康检查
curl http://localhost:3100/ready

# API 测试
curl http://localhost:3100/loki/api/v1/labels
```

---

## 2. Prometheus 容器

### 2.1 Docker Compose 配置

```yaml
prometheus:
  image: prom/prometheus:latest
  container_name: mystocks-prometheus
  restart: unless-stopped
  ports:
    - "9090:9090"
  volumes:
    - ./config/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    - ./data/prometheus:/prometheus
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
    - '--storage.tsdb.retention.time=30d'
    - '--web.enable-lifecycle'
  networks:
    - mystocks-monitoring
```

### 2.2 关键配置说明

| 参数 | 说明 |
|------|------|
| `storage.tsdb.path` | TSDB 存储路径 |
| `storage.tsdb.retention.time` | 数据保留时间（30天） |
| `web.enable-lifecycle` | 启用热重载 |

---

## 3. Grafana 容器

### 3.1 Docker Compose 配置

```yaml
grafana:
  image: grafana/grafana:latest
  container_name: mystocks-grafana
  restart: unless-stopped
  user: "472:472"
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_USER=admin
    - GF_SECURITY_ADMIN_PASSWORD=admin
    - GF_USERS_ALLOW_SIGN_UP=false
    - GF_SERVER_ROOT_URL=http://localhost:3000
    - GF_SERVER_DOMAIN=localhost
    - GF_INSTALL_PLUGINS=grafana-piechart-panel
  volumes:
    - ./data/grafana:/var/lib/grafana
    - ./provisioning:/etc/grafana/provisioning:ro
  networks:
    - mystocks-monitoring
  depends_on:
    - prometheus
```

### 3.2 关键配置说明

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `user` | `472:472` | Grafana 进程用户，避免权限问题 |
| `provisioning` | `ro` | 只读挂载，自动加载数据源和仪表板 |

### 3.3 数据源配置 (`provisioning/datasources/monitoring.yml`)

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://mystocks-prometheus:9090
    isDefault: true
    editable: true

  - name: Loki
    type: loki
    access: proxy
    url: http://mystocks-loki:3100
    isDefault: false
    editable: true
    jsonData:
      maxLines: 1000

  - name: Tempo
    type: tempo
    access: proxy
    url: http://mystocks-tempo:3200
    isDefault: false
    editable: true

  - name: NodeExporter
    type: prometheus
    access: proxy
    url: http://mystocks-prometheus:9090
    isDefault: false
    editable: true
    jsonData:
      timeInterval: 15s
```

---

## 4. Tempo 容器

### 4.1 Docker Compose 配置

```yaml
tempo:
  image: grafana/tempo:latest
  container_name: mystocks-tempo
  restart: unless-stopped
  ports:
    - "3200:3200"   # HTTP API
    - "4317:4317"   # OTLP gRPC
    - "4318:4318"   # OTLP HTTP
  volumes:
    - ./config/tempo-config.yaml:/etc/tempo-config.yaml:ro
    - ./data/tempo:/tmp/tempo
  command: -config.file=/etc/tempo-config.yaml
  networks:
    - mystocks-monitoring
```

### 4.2 端口说明

| 端口 | 协议 | 用途 |
|------|------|------|
| 3200 | HTTP | Tempo Query UI API |
| 4317 | gRPC | OTLP gRPC 接收器 |
| 4318 | HTTP | OTLP HTTP 接收器 |

---

## 5. Node Exporter 容器

### 5.1 Docker Compose 配置

```yaml
node_exporter:
  image: prom/node-exporter:latest
  container_name: mystocks-node-exporter
  restart: unless-stopped
  ports:
    - "9100:9100"
  command:
    - '--path.procfs=/proc'
    - '--path.sysfs=/sys'
    - '--no-collector.filesystem.mounted'
  networks:
    - mystocks-monitoring
```

### 5.2 关键配置说明

| 参数 | 说明 |
|------|------|
| `--path.procfs=/proc` | 挂载宿主机的 /proc |
| `--path.sysfs=/sys` | 挂载宿主机的 /sys |
| `--no-collector.filesystem.mounted` | 排除已挂载的文件系统 |

---

## 网络配置

```yaml
networks:
  mystocks-monitoring:
    name: mystocks-monitoring
    driver: bridge
```

**服务发现**:
- 容器间通过服务名通信（如 `mystocks-prometheus:9090`）
- 使用 bridge 网络模式

---

## 部署命令

```bash
# 启动所有服务
cd monitoring-stack
docker compose -f docker-compose-loki-tempo.yml up -d

# 查看状态
docker compose -f docker-compose-loki-tempo.yml ps

# 查看日志
docker logs -f mystocks-loki
docker logs -f mystocks-grafana
docker logs -f mystocks-prometheus

# 重启单个服务
docker restart mystocks-loki

# 停止所有服务
docker compose -f docker-compose-loki-tempo.yml down
```

---

## 访问地址

| 服务 | 地址 | 用途 |
|------|------|------|
| Grafana | http://localhost:3000 | 监控面板 (admin/admin) |
| Prometheus | http://localhost:9090 | 指标查询 |
| Loki | http://localhost:3100 | 日志存储 |
| Tempo | http://localhost:3200 | 链路追踪 |
| Node Exporter | http://localhost:9100 | 节点指标 |

---

## 常见问题排查

### Loki 启动失败

```bash
# 检查配置语法
docker logs mystocks-loki | grep error

# 常见错误：
# 1. "tsdb must always have periodic config" -> 检查 schema_config.index.period
# 2. "directory required for local rules config" -> 确保 rules 目录存在
```

### Grafana 数据源未加载

```bash
# 检查 provisioning 文件
docker exec mystocks-grafana cat /etc/grafana/provisioning/datasources/monitoring.yml

# 重置 admin 密码
docker exec mystocks-grafana grafana cli admin reset-admin-password
```

### Prometheus 无法抓取指标

```bash
# 检查 targets
curl http://localhost:9090/api/v1/targets
```
