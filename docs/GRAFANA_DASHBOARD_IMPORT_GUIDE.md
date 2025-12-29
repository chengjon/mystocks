# Grafana GPU监控Dashboard - 导入指南

## 快速开始

### 1. 启动GPU Metrics Exporter

```bash
# 启动Prometheus Exporter
./scripts/start_gpu_exporter.sh

# 或者手动启动
python3 src/gpu_monitoring/prometheus_exporter.py 9100 10
```

Exporter启动后，Prometheus会自动开始抓取GPU指标。

**验证Exporter运行**:
```bash
curl http://localhost:9100/metrics | grep gpu_
```

### 2. 导入Dashboard到Grafana

访问Grafana: `http://localhost:3000`

#### 方式1: 上传Dashboard文件（推荐）

1. 登录Grafana（默认: admin/admin）
2. 点击左侧菜单的 **+** → **Import**
3. 点击 **Upload JSON file**
4. 选择文件: `config/monitoring/dashboards/gpu-monitoring.json`
5. 点击 **Load**
6. 确认数据源为 **Prometheus**
7. 点击 **Import**

#### 方式2: 复制粘贴JSON

1. 登录Grafana
2. 点击左侧菜单的 **+** → **Import**
3. 粘贴 `config/monitoring/dashboards/gpu-monitoring.json` 的内容
4. 点击 **Load**
5. 确认数据源
6. 点击 **Import**

### 3. 验证Dashboard

访问Dashboard: `http://localhost:3000/d/gpu-monitoring/gpu-monitoring`

**检查项**:
- [ ] 所有Panel显示数据
- [ ] GPU利用率、温度、显存指标正常显示
- [ ] 图表时间轴正常
- [ ] 自动刷新工作（默认10秒）

### 4. 配置自动刷新

在Dashboard右上角设置刷新间隔：
- 推荐设置: `10s`（与Prometheus抓取间隔一致）
- 其他选项: `5s`, `30s`, `1m`

## Dashboard概览

### Panel布局

**Row 1: GPU硬件指标** (4个Stat)
- GPU Utilization（利用率）
- GPU Temperature（温度）
- GPU Memory Usage（显存使用）
- GPU Power（功耗）

**Row 2: 硬件趋势** (2个Time Series)
- GPU & Memory Utilization（利用率趋势）
- GPU Temperature Trend（温度趋势）

**Row 3: GPU性能指标** (5个Panel)
- Matrix Performance (GFLOPS)（矩阵运算性能）
- Speedup Ratio（加速比）
- Cache Hit Rate（缓存命中率）
- Task Success Rate（任务成功率）
- Memory Bandwidth (GB/s)（内存带宽）

**Row 4: 时钟和PCIe** (2个Time Series)
- Clock Frequencies（时钟频率）
- PCIe Throughput（PCIe吞吐量）

### 总计: 16个Panel

## Prometheus指标说明

### 硬件指标

| 指标名称 | 描述 | 示例查询 |
|---------|------|----------|
| `gpu_utilization_percent` | GPU利用率 | `gpu_utilization_percent` |
| `gpu_temperature_celsius` | GPU温度 | `gpu_temperature_celsius` |
| `gpu_memory_used_bytes` | 已用显存 | `gpu_memory_used_bytes / 1024 / 1024 / 1024` |
| `gpu_memory_total_bytes` | 总显存 | `gpu_memory_total_bytes / 1024 / 1024 / 1024` |
| `gpu_power_usage_watts` | GPU功耗 | `gpu_power_usage_watts` |
| `gpu_sm_clock_mhz` | SM时钟频率 | `gpu_sm_clock_mhz` |
| `gpu_memory_clock_mhz` | 显存时钟频率 | `gpu_memory_clock_mhz` |
| `gpu_pcie_throughput_tx_mbps` | PCIe发送吞吐量 | `gpu_pcie_throughput_tx_mbps` |
| `gpu_pcie_throughput_rx_mbps` | PCIe接收吞吐量 | `gpu_pcie_throughput_rx_mbps` |

### 性能指标

| 指标名称 | 描述 |
|---------|------|
| `gpu_matrix_gflops` | 矩阵运算性能（GFLOPS）|
| `gpu_overall_speedup_ratio` | 综合加速比 |
| `gpu_matrix_speedup_ratio` | 矩阵运算加速比 |
| `gpu_memory_speedup_ratio` | 内存操作加速比 |
| `gpu_cache_hit_rate_percent` | 缓存命中率 |
| `gpu_task_success_rate_percent` | 任务成功率 |
| `gpu_memory_bandwidth_gbps` | 内存带宽（GB/s）|

### 统计指标

| 指标名称 | 描述 |
|---------|------|
| `gpu_benchmark_runs_total` | 基准测试总次数 |
| `gpu_benchmark_duration_seconds` | 基准测试持续时间 |

## 常见问题

### 问题1: Dashboard显示"No Data"

**原因**: Prometheus未抓取到GPU指标

**解决方案**:
```bash
# 1. 检查Exporter是否运行
curl http://localhost:9100/metrics | grep gpu_

# 2. 检查Prometheus是否抓取
# 访问 http://localhost:9090/targets

# 3. 查询Prometheus
# 访问 http://localhost:9090/graph?g=gpu_utilization_percent
```

### 问题2: Panel显示错误

**原因**: 查询语法错误或指标不存在

**解决方案**:
1. 编辑Panel
2. 检查Query字段
3. 确认指标名称正确

### 问题3: 时间范围无数据

**原因**: 指标开始时间太早

**解决方案**:
- 在Dashboard右上角选择时间范围（Last 5 minutes）
- 或选择"Now"

### 问题4: 刷新后数据不变

**原因**: Prometheus抓取间隔未到

**解决方案**:
- 等待10-15秒（Prometheus默认抓取间隔）
- 检查Prometheus配置中的`scrape_interval`

## Dashboard定制

### 修改Panel颜色

1. 编辑Panel
2. 进入 **Color** 设置
3. 选择颜色模式（阈值/色板）
4. 配置阈值值

### 修改Panel单位

1. 编辑Panel
2. 进入 **Field** → **Unit**
3. 选择合适的单位

### 添加新Panel

1. 点击Dashboard右上角的 **+** → **Add panel**
2. 选择Panel类型（Stat/Time Series/Gauge等）
3. 配置数据源和查询
4. 保存

### 创建告警

1. 点击Panel右上角的 **...** → **Create alert from this panel**
2. 配置告警条件
3. 设置通知方式
4. 保存告警规则

## 性能优化

### 调整刷新间隔

根据需求调整Prometheus抓取间隔和Dashboard刷新间隔：

**低延迟模式**（实时监控）:
```yaml
# prometheus.yml
scrape_interval: 5s
```
Dashboard刷新: `5s`

**标准模式**（平衡性能）:
```yaml
# prometheus.yml
scrape_interval: 10s
```
Dashboard刷新: `10s`

**低资源模式**（节省资源）:
```yaml
# prometheus.yml
scrape_interval: 30s
```
Dashboard刷新: `30s`

## 停止Exporter

```bash
# 停止GPU Metrics Exporter
./scripts/stop_gpu_exporter.sh

# 或手动停止
ps aux | grep prometheus_exporter | grep -v grep | awk '{print $2}' | xargs kill
```

## 监控建议

### 关键指标

**必须监控**:
- GPU温度（告警阈值: >85°C）
- GPU利用率（目标: >70%）
- 显存使用率（告警阈值: >90%）

**建议监控**:
- GPU功耗
- 矩阵运算性能（GFLOPS）
- 缓存命中率
- 任务成功率

### 告警配置示例

在Grafana中创建告警:

**GPU高温告警**:
```
条件: gpu_temperature_celsius > 85
持续时间: 5m
通知: 邮件/Slack/Webhook
```

**GPU利用率告警**:
```
条件: gpu_utilization_percent < 10
持续时间: 30m
通知: 邮件/Slack/Webhook
```

## 总结

✅ **Dashboard已创建**: `config/monitoring/dashboards/gpu-monitoring.json`
✅ **Exporter已实现**: `src/gpu_monitoring/prometheus_exporter.py`
✅ **启动脚本已准备**: `scripts/start_gpu_exporter.sh`
✅ **Prometheus配置已更新**: `monitoring/prometheus.yml`

**使用步骤**:
1. 启动Exporter: `./scripts/start_gpu_exporter.sh`
2. 导入Dashboard: 复制JSON到Grafana → Import
3. 验证Dashboard: 检查Panel是否显示数据
4. 配置告警: 根据需要设置告警规则

**访问地址**:
- Dashboard: `http://localhost:3000/d/gpu-monitoring/gpu-monitoring`
- Exporter: `http://localhost:9100/metrics`
- Prometheus: `http://localhost:9090`

---

**文档版本**: 1.0
**最后更新**: 2025-12-29
