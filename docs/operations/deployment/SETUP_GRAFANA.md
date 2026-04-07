# Grafana 自动化配置说明

> **使用说明**:
> 本文件是 Grafana 专项配置指南，不是当前前端基线、当前监控主入口或仓库共享规则的唯一事实来源。
> 若涉及当前环境一致性、统一运行口径或审批门禁，请优先阅读 `architecture/STANDARDS.md`；若涉及运维执行流程或协作约束，再结合根目录 `AGENTS.md` 与 `docs/operations/README.md`、`docs/operations/monitoring/INDEX.md`。
>
> 文内 `http://localhost:3000` 指向 Grafana，而不是仓库前端默认访问地址；当前前端默认地址仍应以根目录治理文档声明为准。

## 📋 快速开始

### 方法 1: 使用自动化脚本（推荐）

```bash
cd /opt/claude/mystocks_phase6_monitoring

# 启动 Playwright 安装（首次使用）
./setup-grafana.sh setup

# 运行自动化配置
./setup-grafana.sh ui
```

### 方法 2: 手动操作步骤

#### 1. 登录
- 访问: http://localhost:3000
- 用户名: `admin`
- 密码: `admin`

#### 2. 添加数据源

**注意**: 如果自动脚本已添加，可以跳过此步骤

**添加 Prometheus 数据源**:
1. 左侧菜单 → Connections → Data Sources
2. 点击右上角 "Add new data source"
3. 配置:
   - Name: `Prometheus`
   - URL: `http://mystocks-prometheus:9090`
   - Type: `Prometheus`
   - 点击 "Save & Test"

**添加 Loki 数据源**:
1. 点击 "Add new data source"
2. 配置:
   - Name: `Loki`
   - URL: `http://mystocks-loki:3100`
   - Type: `Loki`
   - 点击 "Save & Test"

**添加 Tempo 数据源**:
1. 点击 "Add new data source"
2. 配置:
   - Name: `Tempo`
   - URL: `http://mystocks-tempo:3200`
   - Type: `Tempo`
   - 点击 "Save & Test"

**添加 NodeExporter 数据源**:
1. 点击 "Add new data source"
2. 配置:
   - Name: `NodeExporter`
   - URL: `http://mystocks-node-exporter:9100`
   - Type: `Prometheus`
   - 点击 "Save & Test"

#### 3. 创建 Dashboard

**创建新 Dashboard**:
1. 点击左侧菜单 `+` → `Dashboard`
2. 点击右上角 `New dashboard`

**添加面板 1: 系统状态**:
1. 点击 `Add an empty panel`
2. 配置:
   - Title: `System Status`
   - Visualization: `Stat`
   - Data source: `Prometheus`
   - Query: `up`
3. 点击 `Apply`
4. 保存 Dashboard

**添加面板 2: API 延迟**:
1. 点击 `Add an empty panel`
2. 配置:
   - Title: `API Latency (P95)`
   - Visualization: `Time series`
   - Data source: `Prometheus`
   - Query: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
   - Unit: `s(秒)`
3. 点击 `Apply`
4. 保存 Dashboard

**添加面板 3: CPU 使用率**:
1. 点击 `Add an empty panel`
2. 配置:
   - Title: `CPU Usage`
   - Visualization: `Gauge`
   - Data source: `Prometheus`
   - Query: `100 * (1 - avg(rate(process_cpu_seconds_total[5m])))`
   - Min: 0
   - Max: 100
   - Unit: `percent(0-100)`
   - Thresholds:
     - Red: 80
     - Yellow: 90
3. 点击 `Apply`
4. 保存 Dashboard

**添加面板 4: 内存使用**:
1. 点击 `Add an empty panel`
2. 配置:
   - Title: `Memory Usage`
   - Visualization: `Gauge`
   - Data source: `Prometheus`
   - Query: `process_resident_memory_bytes / 1024 / 1024 / 1024`
   - Min: 0
   - Max: 16
   - Unit: `GB(GB)`
   - Thresholds:
     - Red: 12
     - Yellow: 14
3. 点击 `Apply`
4. 保存 Dashboard

## 🤖 Playwright 自动化

### 脚本文件
- `playwright-grafana.config.ts` - Playwright 配置
- `playwright-tests/grafana/grafana-setup.spec.ts` - 测试用例
- `setup-grafana.sh` - 启动脚本
- `package-grafana.json` - npm 脚本配置

### 运行命令

```bash
cd /opt/claude/mystocks_phase6_monitoring

# 首次使用需要安装浏览器
./setup-grafana.sh setup

# 运行自动化
./setup-grafana.sh ui
```

### 测试用例说明

1. `添加 Prometheus 数据源` - 自动添加 Prometheus 数据源
2. `添加 Loki 数据源` - 自动添加 Loki 数据源
3. `添加 Tempo 数据源` - 自动添加 Tempo 数据源
4. `添加 NodeExporter 数据源` - 自动添加 NodeExporter 数据源
5. `创建 Dashboard` - 创建包含 4 个面板的监控 Dashboard
6. `等待并截图` - 等待完成并截图保存

### 故障排查

#### 问题 1: Playwright 未安装
```bash
./setup-grafana.sh setup
```

#### 问题 2: 浏览器未安装
```bash
./setup-grafana.sh browsers
npx playwright install chromium
```

#### 问题 3: 脚本执行失败
```bash
# 查看 Playwright 报告
./setup-grafana.sh report
```

#### 问题 4: 数据源添加失败
检查：
1. Prometheus 是否运行: curl http://localhost:9090/-/healthy
2. Grafana 是否运行: curl http://localhost:3000/api/health
3. 网络连接: docker network inspect mystocks-monitoring

## 📊 预期结果

### 自动化完成后
- ✅ 4 个数据源自动添加并测试通过
- ✅ 1 个 Dashboard 自动创建
- ✅ Dashboard 包含 4 个监控面板
- ✅ 截图保存到 `playwright-tests/grafana/grafana-setup.png`

### 手动操作完成后
- ✅ 4 个数据源手动配置完成
- ✅ 1 个 Dashboard 手动创建完成
- ✅ Dashboard 包含 4 个监控面板

---

**推荐**: 先尝试自动化脚本，如果失败则使用手动操作步骤。
