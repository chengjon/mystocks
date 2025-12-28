
---

## 📊 监控系统配置 (2025-12-28 新增)

### 监控栈概览

MyStocks 项目使用 **LGTM Stack** (Loki, Grafana, Tempo, Prometheus) 实现完整的可观测性：

| 容器         | 功能           | 端口           | 数据目录              | 状态   |
|-------------|--------------|---------------|---------------------|-------|
| Prometheus   | 指标存储与查询 | 9090:9090     | /data/docker/prometheus | ✅    |
| Grafana     | 可视化仪表板   | 3000:3000     | /data/docker/grafana    | ✅    |
| Loki        | 日志聚合系统   | 3100:3100, 9096:9096 | /data/docker/loki       | ✅    |
| Tempo       | 分布式追踪系统 | 3200:3200, 4317-4318:4317-4318 | /data/docker/tempo      | ✅    |
| Node Exporter | 系统指标采集器 | 9100:9100     | -                   | ✅    |

### 监控系统功能说明

#### 1️⃣ Prometheus - 指标存储与查询引擎
- **核心功能**: 采集和存储时间序列指标数据
- **查询语言**: PromQL (强大的指标查询语言)
- **告警引擎**: 内置告警规则评估
- **数据抓取**: 定期从应用和服务采集 /metrics 端点

**为什么需要？**
```
应用 → /metrics 端点 → Prometheus → 存储时序数据
                          ↓
                     告警规则评估
                          ↓
                     提供查询接口
```

**典型指标**:
- API 请求延迟、错误率、吞吐量
- 系统资源使用率（CPU、内存、磁盘）
- 数据库查询性能
- 缓存命中率

**关键点**: Prometheus 是指标存储的核心，没有它就无法收集和查询性能数据。

---

#### 2️⃣ Grafana - 可视化仪表板
- **核心功能**: 创建美观的监控仪表板
- **数据源聚合**: 统一展示 Prometheus、Loki、Tempo 数据
- **告警通知**: 支持多种通知渠道
- **权限管理**: 多租户和团队协作

**为什么需要？**
```
Prometheus → 原始数字
      ↓
Grafana → 图表、仪表板、告警 → 可视化展示
```

**典型功能**:
- 实时图表和折线图
- 日志查询界面
- 追踪链路可视化
- 自定义 Dashboard

**关键点**: Prometheus 的数据很难直接阅读，需要 Grafana 将其转化为可视化的监控面板。

---

#### 3️⃣ Loki - 日志聚合系统
- **核心功能**: 高效的分布式日志存储
- **标签查询**: 类似 Prometheus 的查询语法
- **实时索引**: 快速日志搜索和过滤
- **低存储成本**: 相比 ELK Stack 更节省资源

**为什么需要？**
```
应用日志 → Loki → 结构化存储
              ↓
         快速检索和过滤
              ↓
         与 Metrics 关联分析
```

**与 ELK Stack 对比**:

| 特性    | Loki (新) | ELK Stack (旧) |
|---------|-----------|----------------|
| 存储格式 | 压缩索引   | 倒排索引         |
| 内存占用 | 低         | 高               |
| 部署复杂度 | 简单       | 复杂             |
| 集成度    | 与 Grafana 无缝集成 | 需要额外配置     |

**关键点**: 当应用报错时，仅看指标不够，需要查看日志找到根本原因。Loki 提供了与 Prometheus 体验一致的日志查询。

---

#### 4️⃣ Tempo - 分布式追踪
- **核心功能**: 记录请求在微服务间的完整调用链
- **链路可视化**: 可视化跨服务的请求路径
- **性能瓶颈**: 识别哪个服务慢或有问题
- **协议支持**: OpenTelemetry (OTLP)

**为什么需要？**
```
用户请求 → 网关 → 服务A → 服务B → 数据库
    ↓
 Tempo 记录完整调用链
    ↓
 Grafana 展示: 网关(50ms) → 服务A(120ms) → 服务B(200ms) → DB(300ms)
              ↓
         发现服务B是瓶颈
```

**追踪示例**:
```
HTTP GET /api/stocks
├─ Gateway (45ms)
│  └─ Cache Hit (2ms)
├─ Market Service (150ms)
│  ├─ Redis (5ms)
│  └─ TDengine (140ms) ← 发现这里慢
└─ Technical Service (80ms)
```

**关键点**: 在微服务架构中，一个请求涉及多个服务。仅看指标不知道哪个服务有问题，追踪可以定位到具体的慢查询或错误节点。

---

#### 5️⃣ Node Exporter - 系统指标采集器
- **核心功能**: 暴露 Linux 系统指标
- **Prometheus 目标**: 作为 Prometheus 的采集目标
- **轻量级**: 低开销、易部署

**为什么需要？**
```
Linux 系统 → Node Exporter → /metrics 端口 → Prometheus → 存储
```

**采集的指标**:
- CPU 使用率、核心数、负载
- 内存使用情况、交换分区
- 磁盘 I/O、空间使用
- 网络流量、连接数
- 文件系统信息

**关键点**: 应用指标只反映应用层面的性能，系统指标告诉你服务器本身是否有资源瓶颈。

---

### 监控配置文件

#### 环境变量配置
所有连接配置已定义在: `/opt/claude/mystocks_spec/monitoring-stack/.env.monitoring`

```bash
# 引用监控配置
source /opt/claude/mystocks_spec/monitoring-stack/.env.monitoring
```

**核心配置**:

| 配置项                       | 值                              | 说明                          |
|-----------------------------|----------------------------------|-----------------------------|
| PROMETHEUS_URL             | http://mystocks-prometheus:9090   | Prometheus 内部访问地址       |
| PROMETHEUS_PUBLIC_URL      | http://localhost:9090             | Prometheus 外部访问地址       |
| GRAFANA_URL                | http://mystocks-grafana:3000     | Grafana 内部访问地址         |
| GRAFANA_PUBLIC_URL         | http://localhost:3000             | Grafana 外部访问地址         |
| LOKI_URL                   | http://mystocks-loki:3100         | Loki 内部访问地址            |
| LOKI_PUBLIC_URL            | http://localhost:3100             | Loki 外部访问地址            |
| TEMPO_URL                  | http://mystocks-tempo:3200        | Tempo 内部访问地址           |
| TEMPO_PUBLIC_URL           | http://localhost:3200             | Tempo 外部访问地址           |
| TEMPO_OTLP_ENDPOINT        | http://mystocks-tempo:4317       | Tempo OTLP GRPC 端点        |
| TEMPO_OTLP_HTTP_ENDPOINT  | http://mystocks-tempo:4318       | Tempo OTLP HTTP 端点        |
| NODE_EXPORTER_URL          | http://mystocks-node-exporter:9100 | Node Exporter 访问地址      |
| MONITORING_NETWORK         | mystocks-monitoring               | Docker 网络名称               |

**数据源配置 (Grafana 内部使用)**:
```bash
GRAFANA_DATASOURCE_PROMETHEUS_URL=http://mystocks-prometheus:9090
GRAFANA_DATASOURCE_LOKI_URL=http://mystocks-loki:3100
GRAFANA_DATASOURCE_TEMPO_URL=http://mystocks-tempo:3200
GRAFANA_DATASOURCE_NODE_EXPORTER_URL=http://mystocks-node-exporter:9100
```

#### 数据持久化目录
所有监控数据存储在: `/data/docker/`

```
/data/docker/
├── prometheus/        # Prometheus 时序数据
├── grafana/           # Grafana 配置和仪表板
├── loki/             # Loki 日志数据
│   ├── boltdb-shipper-active/
│   ├── boltdb-shipper-cache/
│   ├── chunks/
│   ├── wal/           # Write Ahead Log
│   └── compactor/    # Compactor 工作目录
└── tempo/            # Tempo 追踪数据
    └── traces/
```

**权限配置**:
```bash
# Grafana 数据目录 (用户 472:472)
chown -R 472:472 /data/docker/grafana
chmod -R 777 /data/docker/grafana

# 其他服务数据目录 (用户 nobody:nogroup)
chown -R nobody:nogroup /data/docker/{prometheus,loki,tempo}
chmod -R 777 /data/docker/{prometheus,loki,tempo}
```

---

### 服务访问与验证

#### 访问地址

| 服务      | 内部地址 (容器间)                     | 外部地址 (宿主机)           | 用途               |
|-----------|-------------------------------------|---------------------------|--------------------|
| Prometheus | http://mystocks-prometheus:9090       | http://localhost:9090       | 指标查询和告警配置 |
| Grafana    | http://mystocks-grafana:3000       | http://localhost:3000       | 可视化仪表板       |
| Loki       | http://mystocks-loki:3100          | http://localhost:3100       | 日志查询 API       |
| Tempo      | http://mystocks-tempo:3200         | http://localhost:3200       | 追踪数据 API       |
| Node Exporter | http://mystocks-node-exporter:9100 | http://localhost:9100       | 系统指标端点       |

#### 健康检查命令

```bash
# Prometheus
curl http://localhost:9090/-/healthy

# Grafana (浏览器访问: http://localhost:3000)
# 默认凭据: admin/admin

# Loki
curl http://localhost:3100/ready

# Tempo
curl http://localhost:3200/ready

# Node Exporter
curl http://localhost:9100/metrics
```

---

### 常用操作命令

#### 启动/停止监控服务

```bash
cd /opt/claude/mystocks_spec/monitoring-stack

# 启动所有监控服务
docker-compose up -d

# 停止所有监控服务
docker-compose down

# 启动指定服务
docker-compose up -d prometheus grafana loki tempo node_exporter

# 重启单个服务
docker-compose restart prometheus
docker-compose restart grafana
docker-compose restart loki
docker-compose restart tempo
docker-compose restart node_exporter
```

#### 查看日志

```bash
# Prometheus 日志
docker logs mystocks-prometheus -f

# Grafana 日志
docker logs mystocks-grafana -f

# Loki 日志
docker logs mystocks-loki -f

# Tempo 日志
docker logs mystocks-tempo -f

# Node Exporter 日志
docker logs mystocks-node-exporter -f
```

#### 查看容器状态

```bash
# 查看所有监控容器
docker ps --filter "network=mystocks-monitoring"

# 查看容器网络
docker network inspect mystocks-monitoring

# 查看容器挂载点
docker inspect mystocks-prometheus --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}'
```

---

### Grafana 数据源配置

#### 添加 Prometheus 数据源

1. 访问: http://localhost:3000 (admin/admin)
2. Configuration → Data Sources → Add data source
3. 选择: Prometheus
4. 配置:
   - **Name**: Prometheus
   - **URL**: `http://mystocks-prometheus:9090`
5. 点击 "Save & Test"

#### 添加 Loki 数据源

1. Configuration → Data Sources → Add data source
2. 选择: Loki
3. 配置:
   - **Name**: Loki
   - **URL**: `http://mystocks-loki:3100`
4. 点击 "Save & Test"

#### 添加 Tempo 数据源

1. Configuration → Data Sources → Add data source
2. 选择: Tempo
3. 配置:
   - **Name**: Tempo
   - **URL**: `http://mystocks-tempo:3200`
4. 点击 "Save & Test"

---

### 问题定位流程示例

**场景**: 用户报告 API 响应慢

1. **Grafana 仪表板** → 查看 API 延迟趋势
2. **Prometheus 指标** → 查询 `/api/stocks` 接口 P99 延迟
3. **Loki 日志** → 查询相关时间段的错误日志
4. **Tempo 追踪** → 查看完整调用链，定位慢查询
5. **Node Exporter** → 检查系统资源使用情况

**监控协同**:
```
┌─────────────────────────────────────────────────────┐
│              MyStocks 应用                      │
└────────┬──────────┬──────────┬────────────────┘
         │          │          │
         ↓          ↓          ↓
    /metrics    应用日志    /traces
         │          │          │
         ↓          ↓          ↓
┌────────┴─┬─────┴──┬─────┴─────────────────────┐
│ Prometheus │   Loki   │       Tempo            │
│ 指标存储   │  日志存储  │      追踪存储         │
└─────┬─────┴─────┬───┴──────┬────────────────┘
      │            │           │                │
      ↓            ↓           ↓                │
┌─────────────────────────────────────────────┐│
│          Grafana 可视化平台             │◄┘
│  ┌────────┐ ┌──────┐ ┌──────────┐   │
│  │ 指标图 │ │ 日志 │ │ 追踪图   │   │
│  └────────┘ └──────┘ └──────────┘   │
└─────────────────────────────────────────────┘

      ↑
      │
┌─────┴─────────────────────────────┐
│     Node Exporter              │
│    (系统指标: CPU/Mem/磁盘)     │
└─────────────────────────────────────┘
```

---

### 完整可观测性 - 三大支柱

**Metrics (指标)**: 监控**发生了什么**
- 请求延迟、错误率、吞吐量
- 系统资源使用率
- 数据库性能指标
- 工具: Prometheus

**Logs (日志)**: 解释**为什么发生**
- 应用错误日志
- 异常堆栈跟踪
- 请求/响应详情
- 工具: Loki

**Traces (追踪)**: 展示**在哪里发生**
- 微服务调用链路
- 每个服务的耗时
- 性能瓶颈定位
- 工具: Tempo

---

### 相关文档

- **部署状态报告**: `/opt/claude/mystocks_spec/monitoring-stack/MONITORING_STATUS.md`
- **Docker Compose 配置**: `/opt/claude/mystocks_spec/monitoring-stack/docker-compose.yml`
- **环境变量配置**: `/opt/claude/mystocks_spec/monitoring-stack/.env.monitoring`
- **Prometheus 配置**: `/opt/claude/mystocks_spec/monitoring-stack/config/prometheus.yml`
- **Loki 配置**: `/opt/claude/mystocks_spec/monitoring-stack/config/loki-config.yaml`
- **Tempo 配置**: `/opt/claude/mystocks_spec/monitoring-stack/config/tempo-config.yaml`

---

### 监控栈部署信息

**部署时间**: 2025-12-28  
**部署状态**: ✅ 全部正常运行  
**数据持久化**: ✅ 所有数据存储在 /data/docker/  
**网络**: ✅ 统一运行在 mystocks-monitoring 网络  
