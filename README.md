# CLI-1: Phase 6 监控系统验证

**分支**: `phase6-monitoring-verification`  
**工作目录**: `/opt/claude/mystocks_phase6_monitoring`  
**预计时间**: 4-6 小时  
**优先级**: 🔴 高（核心基础设施）  
**分配给**: GEMINI 或 OPENCODE  

---

## 🎯 任务目标

验证 Phase 5 实现的完整监控栈功能是否正常工作，包括：

1. ✅ Prometheus metrics 端点可访问且返回正确格式
2. ✅ Grafana Dashboard 可以导入并显示所有指标
3. ✅ Loki 日志聚合收集到应用日志
4. ✅ Tempo 分布式追踪显示调用链路
5. ✅ 告警规则测试通过
6. ✅ SLO 配置验证

---

## 📋 详细任务清单

### 任务 1.1: 验证 Prometheus metrics 端点 (30分钟)

**目标**: 确认后端服务的 `/metrics` 端点正常工作

**步骤**:
```bash
# 1. 启动后端服务（如果未启动）
cd /opt/claude/mystocks_phase6_monitoring/web/backend
ADMIN_PASSWORD=password python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# 2. 等待服务启动（约10秒）
sleep 10

# 3. 访问 metrics 端点
curl http://localhost:8000/metrics

# 4. 验证输出包含以下指标：
# - http_request_duration_seconds_bucket (Histogram)
# - database_query_duration_seconds (Histogram)
# - system_cpu_usage (Gauge)
# - system_memory_usage (Gauge)
# - cache_hits_total (Counter)
# - cache_misses_total (Counter)

# 5. 检查指标格式是否为 Prometheus 文本格式
curl -s http://localhost:8000/metrics | head -20
```

**验收标准**:
- ✅ `/metrics` 端点返回 200 OK
- ✅ 输出格式符合 Prometheus 文本格式（`# HELP`, `# TYPE` 注释）
- ✅ 包含至少 6 个核心指标
- ✅ 指标包含 `le` 标签（Histogram bucket）

**可能的问题**:
- **问题**: 端点返回 404
  - **解决**: 检查 `src/core/middleware/performance.py` 中 `/metrics` 路由是否正确注册
  
- **问题**: 没有指标数据
  - **解决**: 检查 `src/core/database_metrics.py` 中 `start_metrics_server()` 是否被调用

---

### 任务 1.2: 配置 Prometheus 抓取目标 (45分钟)

**目标**: Prometheus 可以成功抓取应用 metrics

**步骤**:
```bash
# 1. 检查 Prometheus 配置文件
cd /opt/claude/mystocks_phase6_monitoring
cat config/monitoring/prometheus.yml

# 2. 验证 scrape_configs 包含我们的应用
# 应该看到：
# scrape_configs:
#   - job_name: 'mystocks_backend'
#     static_configs:
#       - targets: ['localhost:8000']
#     metrics_path: /metrics
#     scrape_interval: 15s

# 3. 启动 Prometheus（使用 Docker）
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/config/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus:latest

# 4. 等待 Prometheus 启动
sleep 15

# 5. 访问 Prometheus UI
# 浏览器打开: http://localhost:9090

# 6. 检查 Targets 页面
# http://localhost:9090/targets
# 应该看到 'mystocks_backend' 任务状态为 "UP"

# 7. 执行测试查询
# 在 Prometheus UI 中执行以下查询：
# - up{job="mystocks_backend"}
# - rate(http_request_duration_seconds_sum[5m])
# - cache_hits_total
```

**验收标准**:
- ✅ Prometheus 容器成功启动
- ✅ Targets 页面显示 `mystocks_backend` 状态为 "UP"
- ✅ 可以查询到应用指标
- ✅ Scrape interval 配置正确（15秒）

**可能的问题**:
- **问题**: Target 显示 "DOWN"
  - **解决**: 检查后端服务是否在运行，端口 8000 是否开放
  
- **问题**: 无法访问 Prometheus UI
  - **解决**: 检查 Docker 容器是否运行：`docker ps | grep prometheus`

---

### 任务 1.3: 导入 Grafana Dashboard (1小时)

**目标**: Grafana 显示 API 概览仪表板

**步骤**:
```bash
# 1. 启动 Grafana（使用 Docker）
docker run -d \
  --name grafana \
  -p 3001:3000 \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  grafana/grafana:latest

# 2. 等待 Grafana 启动
sleep 20

# 3. 访问 Grafana UI
# 浏览器打开: http://localhost:3001
# 用户名: admin
# 密码: admin

# 4. 添加 Prometheus 数据源
# Configuration -> Data Sources -> Add data source
# 选择: Prometheus
# URL: http://host.docker.internal:9090
# 点击 "Save & Test"

# 5. 导入 Dashboard
# Dashboards -> Import -> Upload JSON file
# 选择: config/monitoring/dashboards/api-overview.json

# 6. 验证 Dashboard 显示数据
# 应该看到以下面板：
# - API Request Rate
# - API Latency (p50, p95, p99)
# - Database Query Performance
# - Cache Hit Rate
# - System Resources (CPU, Memory)
```

**验收标准**:
- ✅ Grafana 成功启动并登录
- ✅ Prometheus 数据源连接成功（状态：绿色）
- ✅ Dashboard 导入成功
- ✅ 至少 5 个面板显示数据
- ✅ 时间范围选择器工作正常

**可能的问题**:
- **问题**: 数据源测试失败
  - **解决**: 确认 Prometheus 在运行，使用 `host.docker.internal` 而不是 `localhost`
  
- **问题**: Dashboard 导入后没有数据
  - **解决**: 检查时间范围，确保选择 "Last 5 minutes" 或类似范围

---

### 任务 1.4: 验证 Loki 日志聚合 (45分钟)

**目标**: Loki 收集到应用的结构化日志

**步骤**:
```bash
# 1. 启动 Loki（使用 Docker）
docker run -d \
  --name loki \
  -p 3100:3100 \
  -v $(pwd)/config/monitoring/loki-config.yaml:/mnt/config/loki-config.yaml \
  grafana/loki:latest \
  -config.file=/mnt/config/loki-config.yaml

# 2. 等待 Loki 启动
sleep 10

# 3. 在 Grafana 中添加 Loki 数据源
# http://localhost:3001
# Configuration -> Data Sources -> Add data source
# 选择: Loki
# URL: http://host.docker.internal:3100
# 点击 "Save & Test"

# 4. 打开 Grafana Explore
# 左侧菜单 -> Explore
# 选择 Loki 数据源

# 5. 执行日志查询
# 在查询框中输入:
# {job="mystocks_backend"}

# 6. 验证日志包含 trace_id
# 应该看到 JSON 格式的日志包含:
# - "trace_id": "..."
# - "level": "INFO" / "ERROR"
# - "message": "..."
```

**验收标准**:
- ✅ Loki 容器成功启动
- ✅ Grafana 中 Loki 数据源连接成功
- ✅ Explore 页面可以查询到日志
- ✅ 日志为 JSON 格式
- ✅ 日志包含 `trace_id` 字段

**可能的问题**:
- **问题**: Loki 没有收集到日志
  - **解决**: 检查后端是否配置了 Loki 的导入，查看 `src/core/logging/structured.py`
  
- **问题**: 日志格式不是 JSON
  - **解决**: 验证 `src/core/logging/structured.py` 中 `JSONFormatter` 是否被使用

---

### 任务 1.5: 测试 Tempo 分布式追踪 (45分钟)

**目标**: Tempo 显示请求调用链路

**步骤**:
```bash
# 1. 启动 Tempo（使用 Docker）
docker run -d \
  --name tempo \
  -p 4318:4318 \
  -p 3200:3200 \
  -v $(pwd)/config/monitoring/tempo-config.yaml:/etc/tempo-config.yaml \
  grafana/tempo:latest \
  -config.file=/etc/tempo-config.yaml

# 2. 等待 Tempo 启动
sleep 10

# 3. 在 Grafana 中添加 Tempo 数据源
# http://localhost:3001
# Configuration -> Data Sources -> Add data source
# 选择: Tempo
# URL: http://host.docker.internal:3200
# 点击 "Save & Test"

# 4. 生成一些追踪数据
# 发送几个 API 请求:
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/market/symbols

# 5. 在 Grafana Explore 中查询追踪
# 左侧菜单 -> Explore
# 选择 Tempo 数据源
# 点击 "Search Traces"

# 6. 验证追踪链路
# 应该看到:
# - HTTP GET /health
# - HTTP GET /api/v1/market/symbols
# 每个追踪包含多个 spans（如果调用了数据库）
```

**验收标准**:
- ✅ Tempo 容器成功启动
- ✅ Grafana 中 Tempo 数据源连接成功
- ✅ 可以查询到追踪数据
- ✅ 追踪包含多个 spans（如果有数据库调用）
- ✅ 每个 span 有开始时间和持续时间

**可能的问题**:
- **问题**: Tempo 没有追踪数据
  - **解决**: 检查 `src/core/logging/tracing.py` 中追踪是否被正确初始化
  
- **问题**: 追踪只有一个 span
  - **解决**: 这可能是正常的，如果请求没有调用数据库或其他服务

---

### 任务 1.6: 验证告警规则 (30分钟)

**目标**: 告警规则可以正确触发

**步骤**:
```bash
# 1. 检查告警规则配置
cd /opt/claude/mystocks_phase6_monitoring
cat config/monitoring/alerting.yaml

# 2. 验证告警规则包含:
# - HighAPIlatency (API 延迟 > 1s)
# - HighErrorRate (错误率 > 5%)
# - LowCacheHitRate (缓存命中率 < 80%)
# - HighCPUUsage (CPU > 90%)
# - HighMemoryUsage (内存 > 90%)

# 3. 在 Prometheus 中加载告警规则
# 修改 prometheus.yml 添加:
# rule_files:
#   - '/etc/prometheus/alerting.yaml'

# 4. 重启 Prometheus 应用新配置
docker restart prometheus

# 5. 访问 Prometheus Alerts 页面
# http://localhost:9090/alerts
# 应该看到所有告警规则，状态为 "Inactive" 或 "Pending"

# 6. 测试触发告警
# 可以通过压力测试触发告警，或手动调整阈值
```

**验收标准**:
- ✅ Prometheus 加载告警规则成功
- ✅ Alerts 页面显示所有配置的告警规则
- ✅ 告警规则状态正确（Inactive / Firing）
- ✅ 告警标签正确配置（severity, team）

**可能的问题**:
- **问题**: Prometheus 没有加载告警规则
  - **解决**: 检查 `prometheus.yml` 中 `rule_files` 路径是否正确，检查文件是否被挂载到容器

---

### 任务 1.7: 测试 SLO 配置 (30分钟)

**目标**: SLO（服务级别目标）配置正确

**步骤**:
```bash
# 1. 检查 SLO 配置文件
cat config/monitoring/slo-config.yaml

# 2. 验证 SLO 定义包含:
# - API latency (p95 < 200ms)
# - Error rate (< 1%)
# - Availability (> 99.9%)

# 3. 在 Prometheus 中验证 SLO 指标
# 查询:
# - api_latency_slo:ratio_rate5m
# - api_error_rate_slo:ratio_rate5m
# - api_availability_slo:ratio_rate5m

# 4. 创建 Grafana Dashboard 显示 SLO
# 添加面板显示:
# - SLO 达成率
# - 错误预算消耗
# - 滚动 7天/30天 SLO
```

**验收标准**:
- ✅ SLO 配置文件格式正确
- ✅ Prometheus 中可以查询到 SLO 指标
- ✅ Grafana Dashboard 显示 SLO 数据
- ✅ SLO 告警规则配置正确

**可能的问题**:
- **问题**: SLO 指标没有数据
  - **解决**: SLO 基于 recording rules，需要等待几分钟让数据积累

---

## 🎯 总体验收标准

### 必须满足（Must-have）:
- [ ] Prometheus metrics 端点工作正常
- [ ] Grafana Dashboard 显示至少 5 个面板的数据
- [ ] Loki 收集到结构化日志（JSON 格式 + trace_id）
- [ ] Tempo 显示追踪链路
- [ ] 告警规则在 Prometheus 中可见
- [ ] SLO 配置正确加载

### 加分项（Bonus）:
- [ ] 配置 Grafana 告警通知（Email / Webhook）
- [ ] 创建自定义 Dashboard
- [ ] 测试告警实际触发
- [ ] 优化告警阈值

---

## 📸 必须提供的证据

1. **截图清单**:
   - Prometheus Targets 页面（显示 UP 状态）
   - Prometheus Graph 页面（显示指标查询）
   - Grafana Dashboard（显示所有面板）
   - Grafana Explore 页面（显示 Loki 日志查询）
   - Grafana Explore 页面（显示 Tempo 追踪）
   - Prometheus Alerts 页面（显示告警规则）

2. **命令输出**:
   - `curl http://localhost:8000/metrics` 输出（前 50 行）
   - `docker ps` 输出（显示所有监控容器）
   - Prometheus 查询结果（至少 3 个查询）

3. **配置文件**:
   - `prometheus.yml` (如果修改)
   - `alerting.yaml` (如果修改)

---

## 🐛 常见问题和解决方案

### 问题 1: Docker 容器无法启动
**症状**: `docker run` 命令失败，容器立即退出
**解决**: 
```bash
# 查看容器日志
docker logs prometheus
docker logs grafana

# 检查端口占用
lsof -i :9090
lsof -i :3001

# 停止占用端口的进程
```

### 问题 2: host.docker.internal 无法访问
**症状**: Grafana 无法连接到 Prometheus 或 Loki
**解决**:
```bash
# Linux 需要额外配置
# 使用宿主机 IP 地址
hostname -I  # 获取 IP
# 然后在 Grafana 数据源配置中使用该 IP
```

### 问题 3: Metrics 端点返回空数据
**症状**: `/metrics` 端点返回 200 OK 但内容很少
**解决**:
```bash
# 检查 metrics 中间件是否注册
# 查看 web/backend/app/main.py 中是否包含:
# app.add_middleware(PrometheusMiddleware)

# 触发一些 API 请求生成指标
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/market/symbols
```

---

## 📊 最终交付物

### 1. 监控系统验证报告
**文件**: `MONITORING_VERIFICATION_REPORT.md`
**内容**:
```markdown
# Phase 6 监控系统验证报告

## 执行时间
[开始时间] - [结束时间]

## 任务完成情况
- ✅ 任务 1.1: Prometheus metrics 端点验证
- ✅ 任务 1.2: Prometheus 抓取配置
- ✅ 任务 1.3: Grafana Dashboard 导入
- ✅ 任务 1.4: Loki 日志聚合
- ✅ 任务 1.5: Tempo 分布式追踪
- ✅ 任务 1.6: 告警规则验证
- ✅ 任务 1.7: SLO 配置测试

## 验证结果
### Prometheus
- [ ] Metrics 端点正常
- [ ] Target 状态 UP
- [ ] 指标数据完整

### Grafana
- [ ] Dashboard 导入成功
- [ ] 数据源连接正常
- [ ] 面板显示数据

### Loki
- [ ] 日志收集正常
- [ ] JSON 格式正确
- [ ] trace_id 存在

### Tempo
- [ ] 追踪数据收集
- [ ] 调用链路完整

## 发现的问题
[记录所有遇到的问题和解决方案]

## 优化建议
[基于验证过程的改进建议]

## 截图附件
[列出所有截图文件名]
```

### 2. Git 提交
**提交信息**:
```bash
cd /opt/claude/mystocks_phase6_monitoring
git add .
git commit -m "feat(phase6): Complete monitoring system verification

✅ Prometheus metrics endpoint verified
✅ Grafana dashboard imported and configured
✅ Loki log aggregation tested
✅ Tempo distributed tracing validated
✅ Alert rules verified
✅ SLO configuration tested

验证结果:
- Prometheus: Target UP, metrics collecting
- Grafana: 8 panels displaying data
- Loki: Structured JSON logs with trace_id
- Tempo: Trace chains visible

发现问题: [如果有]
优化建议: [如果有]

🤖 Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

git push origin phase6-monitoring-verification
```

### 3. 必需文件
- `MONITORING_VERIFICATION_REPORT.md`
- `screenshots/` 目录（包含所有截图）
- `config/` 目录（如果有配置修改）

---

## 📞 需要帮助？

如果遇到无法解决的问题，请联系 **Main CLI**:
- 检查 Main CLI 的状态报告
- 在项目中创建 issue
- 查看项目文档: `docs/monitoring/MONITORING_GUIDE.md`

---

**任务开始时间**: ___________  
**任务完成时间**: ___________  
**实际耗时**: ___________  
**完成度**: ___________%

**签名**: CLI-1 (Monitoring Verification Team)
