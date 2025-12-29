# GPU监控 - Grafana Dashboard 集成指南

## 概述

将GPU监控指标集成到Grafana，提供统一的监控平台。

## 架构

```
GPU Hardware
    ↓
pynvml (GPU监控服务)
    ↓
Prometheus Exporter (端口9100)
    ↓
Prometheus (端口9090)
    ↓
Grafana Dashboard
```

## 组件

### 1. GPU Prometheus Exporter

**文件**: `src/gpu_monitoring/prometheus_exporter.py`

**功能**:
- 从GPU硬件采集指标
- 暴露Prometheus格式指标
- 定期更新（默认10秒）

**支持的指标**:

| 指标名称 | 描述 | 标签 |
|---------|------|------|
| `gpu_utilization_percent` | GPU利用率 (%) | device_id, device_name |
| `gpu_memory_used_bytes` | 已用显存 (bytes) | device_id |
| `gpu_memory_total_bytes` | 总显存 (bytes) | device_id |
| `gpu_memory_utilization_percent` | 显存利用率 (%) | device_id |
| `gpu_temperature_celsius` | GPU温度 (°C) | device_id |
| `gpu_power_usage_watts` | GPU功耗 (W) | device_id |
| `gpu_power_limit_watts` | GPU功耗限制 (W) | device_id |
| `gpu_sm_clock_mhz` | SM时钟频率 (MHz) | device_id |
| `gpu_memory_clock_mhz` | 显存时钟频率 (MHz) | device_id |
| `gpu_pcie_throughput_tx_mbps` | PCIe发送吞吐量 (MB/s) | device_id |
| `gpu_pcie_throughput_rx_mbps` | PCIe接收吞吐量 (MB/s) | device_id |
| `gpu_matrix_gflops` | 矩阵运算性能 (GFLOPS) | device_id |
| `gpu_matrix_speedup_ratio` | 矩阵运算加速比 | device_id |
| `gpu_matrix_throughput_ops_per_sec` | 矩阵运算吞吐量 (ops/s) | device_id |
| `gpu_memory_bandwidth_gbps` | 内存带宽 (GB/s) | device_id |
| `gpu_memory_speedup_ratio` | 内存操作加速比 | device_id |
| `gpu_memory_throughput_ops_per_sec` | 内存操作吞吐量 (ops/s) | device_id |
| `gpu_overall_speedup_ratio` | 综合加速比 | device_id |
| `gpu_cache_hit_rate_percent` | 缓存命中率 (%) | device_id |
| `gpu_task_success_rate_percent` | 任务成功率 (%) | device_id |
| `gpu_benchmark_runs_total` | 基准测试次数 | device_id |
| `gpu_benchmark_duration_seconds` | 基准测试持续时间 | device_id, benchmark_type |

### 2. Grafana Dashboard

**文件**: `config/monitoring/dashboards/gpu-monitoring.json`

**包含的Panel**:

#### 硬件指标 (Row 1)
- **GPU Utilization**: GPU利用率（阈值：70%/90%）
- **GPU Temperature**: GPU温度（阈值：75°C/85°C）
- **GPU Memory Usage**: 显存使用量（已用/总计）
- **GPU Power**: 功耗（使用/限制）

#### 性能趋势 (Row 2)
- **GPU & Memory Utilization**: 利用率趋势图
- **GPU Temperature Trend**: 温度趋势图

#### 性能指标 (Row 3)
- **Matrix Performance (GFLOPS)**: 矩阵运算性能
- **Speedup Ratio**: 加速比（综合/矩阵/内存）
- **Cache Hit Rate**: 缓存命中率（阈值：80%/50%）
- **Task Success Rate**: 任务成功率（阈值：95%/90%）
- **Memory Bandwidth (GB/s)**: 内存带宽趋势

#### 时钟和PCIe (Row 4)
- **Clock Frequencies**: SM和显存时钟频率
- **PCIe Throughput**: PCIe吞吐量（TX/RX）

## 快速开始

### 方式1: 使用启动脚本（推荐）

```bash
# 1. 启动GPU Metrics Exporter
./scripts/start_gpu_exporter.sh

# 2. 访问metrics端点
curl http://localhost:9100/metrics | grep gpu_

# 3. 访问Grafana
# http://localhost:3000
```

### 方式2: 手动启动

```bash
# 1. 安装prometheus_client
pip install prometheus_client

# 2. 启动exporter
python3 src/gpu_monitoring/prometheus_exporter.py [port] [interval]

# 例如:
python3 src/gpu_monitoring/prometheus_exporter.py 9100 10

# 3. 验证metrics
curl http://localhost:9100/metrics | grep gpu_utilization
```

## Prometheus配置

### 添加抓取配置

编辑 `monitoring/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'gpu-metrics'
    static_configs:
      - targets: ['host.docker.internal:9100']
    metrics_path: '/metrics'
    scrape_interval: 10s
```

### 重启Prometheus

```bash
# 使用Docker
docker restart mystocks-prometheus

# 或使用systemd
sudo systemctl restart prometheus
```

### 验证Prometheus抓取

```bash
# 访问Prometheus目标页面
http://localhost:9090/targets

# 查询GPU指标
http://localhost:9090/graph?g=cpu_utilization_percent
```

## Grafana配置

### 导入Dashboard

1. 访问Grafana: http://localhost:3000
2. 登录（默认: admin/admin）
3. 导航到 **Dashboard** → **Import**
4. 上传 `config/monitoring/dashboards/gpu-monitoring.json`
5. 或粘贴JSON内容

### 配置数据源

1. 导航到 **Configuration** → **Data Sources**
2. 选择 **Prometheus**
3. 配置:
   - Name: `Prometheus`
   - URL: `http://prometheus:9090`
   - Access: `Server (default)`
4. 点击 **Save & Test**

### Dashboard URL

导入后访问: http://localhost:3000/d/gpu-monitoring/gpu-monitoring

## 脚本说明

### 启动脚本

```bash
# 启动GPU Metrics Exporter
./scripts/start_gpu_exporter.sh

# 使用自定义端口
GPU_EXPORTER_PORT=9101 ./scripts/start_gpu_exporter.sh

# 使用自定义间隔
GPU_EXPORTER_INTERVAL=15 ./scripts/start_gpu_exporter.sh
```

### 停止脚本

```bash
# 停止GPU Metrics Exporter
./scripts/stop_gpu_exporter.sh
```

## 验证测试

### 1. 验证Metrics Exporter

```bash
# 检查进程
ps aux | grep prometheus_exporter

# 检查端口
netstat -tuln | grep 9100

# 获取metrics
curl http://localhost:9100/metrics | grep "^gpu_" | head -20
```

### 2. 验证Prometheus抓取

```bash
# 查询Prometheus
curl http://localhost:9090/api/v1/query?query=gpu_utilization_percent

# 检查目标状态
curl http://localhost:9090/api/v1/targets
```

### 3. 验证Grafana Dashboard

访问Grafana Dashboard并确认:
- 所有Panel显示数据
- 图表正常渲染
- 时间范围切换正常
- 自动刷新正常（默认10秒）

## Docker Compose配置

### 添加GPU Exporter服务

编辑 `docker-compose.yml` 或 `monitoring-stack.yml`:

```yaml
services:
  gpu-exporter:
    build:
      context: .
      dockerfile: Dockerfile.gpu-exporter
    container_name: mystocks-gpu-exporter
    ports:
      - "9100:9100"
    environment:
      - GPU_EXPORTER_PORT=9100
      - GPU_EXPORTER_INTERVAL=10
      - NVIDIA_VISIBLE_DEVICES=0
    volumes:
      - ./logs:/app/logs
      - /dev/nvidia0:/dev/nvidia0
    runtime: nvidia
    restart: unless-stopped
    networks:
      - monitoring
```

### Dockerfile.gpu-exporter

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
RUN pip install prometheus-client pynvml

# 复制代码
COPY src/ ./src/
COPY scripts/ ./scripts/

# 暴露端口
EXPOSE 9100

# 启动exporter
CMD ["python3", "-u", "src/gpu_monitoring/prometheus_exporter.py", "9100", "10"]
```

## 故障排查

### 问题1: GPU不可用

**症状**: Metrics显示0值或错误

**解决方案**:
```bash
# 检查GPU
nvidia-smi

# 检查pynvml
python3 -c "import pynvml; print(pynvml.nvmlInit())"
```

### 问题2: Prometheus无法抓取

**症状**: Grafana Dashboard无数据

**解决方案**:
```bash
# 检查exporter是否运行
curl http://localhost:9100/metrics

# 检查Prometheus配置
cat monitoring/prometheus.yml | grep gpu-metrics

# 重启Prometheus
docker restart mystocks-prometheus

# 检查Prometheus日志
docker logs mystocks-prometheus
```

### 问题3: Grafana无法连接Prometheus

**症状**: Dashboard显示"Data source not found"

**解决方案**:
1. 检查Prometheus URL配置
2. 测试数据源连接
3. 检查网络连接
4. 验证Prometheus是否运行

### 问题4: 权限问题（Docker）

**症状**: Docker容器无法访问GPU

**解决方案**:
```bash
# 确保使用nvidia runtime
docker run --runtime=nvidia --gpus all ...

# 检查nvidia-docker
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

## 性能优化

### 调整更新间隔

```bash
# 默认10秒，可根据需求调整
GPU_EXPORTER_INTERVAL=5 ./scripts/start_gpu_exporter.sh  # 5秒刷新
```

### Prometheus抓取间隔

在`monitoring/prometheus.yml`中调整:
```yaml
scrape_interval: 5s  # 从10秒改为5秒
```

### Grafana自动刷新

在Dashboard右上角设置刷新间隔（默认10秒）。

## 高级配置

### 自定义Grafana Panel

复制`config/monitoring/dashboards/gpu-monitoring.json`并修改:
- 添加新的Panel
- 调整阈值
- 自定义颜色
- 修改查询表达式

### 多GPU监控

Prometheus会自动抓取所有GPU指标（通过device_id标签区分），Dashboard需要手动添加多个Panel。

### 告警规则

在Grafana中配置告警:
1. 导航到 **Alerting** → **Alert Rules**
2. 创建新规则
3. 设置条件和通知

示例告警规则:
```yaml
# GPU温度告警
expr: gpu_temperature_celsius > 85
for: 5m
labels:
  severity: critical
annotations:
  summary: "GPU温度过高"
```

## 监控最佳实践

1. **合理设置刷新间隔**: GPU指标更新频率不宜过高（建议5-15秒）
2. **保留历史数据**: Prometheus默认保留15天，可根据需求调整
3. **配置告警**: 关键指标（温度、利用率）应设置告警
4. **定期检查**: 定期检查Dashboard和Exporter日志
5. **性能考虑**: 指标采集会占用少量GPU资源

## 总结

通过集成GPU监控到Grafana，您可以:

✅ 在统一监控平台查看所有指标
✅ 使用强大的Grafana可视化功能
✅ 配置告警和通知
✅ 自定义Dashboard和Panel
✅ 结合其他系统监控

**独立GPU监控仪表板** + **Grafana Dashboard** = 完整监控方案

---

**文档版本**: 1.0
**最后更新**: 2025-12-29
