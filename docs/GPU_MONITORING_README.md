# GPU监控仪表板

## 项目概述

为MyStocks GPU加速引擎提供专业级监控，支持两种监控方式：

1. **独立GPU监控仪表板** - 专业的GPU监控Web应用
2. **Grafana Dashboard** - 统一的监控平台集成

## 快速开始

### 方式1: 独立GPU监控仪表板

```bash
# 启动GPU监控
./scripts/start_gpu_monitoring.sh

# 访问
http://localhost:5173/gpu-monitoring
```

### 方式2: Grafana Dashboard

```bash
# 启动GPU Exporter
./scripts/start_gpu_exporter.sh

# 启动Grafana和Prometheus
docker-compose -f monitoring-stack.yml up -d

# 访问
http://localhost:3000/d/gpu-monitoring/gpu-monitoring
```

### 方式3: 完整启动（推荐）

```bash
# 启动所有服务（独立仪表板 + Grafana）
./scripts/start_gpu_monitoring_complete.sh all
```

## 功能特性

### 独立GPU监控仪表板

#### 硬件监控
- ✅ GPU利用率、显存、温度、功耗
- ✅ 时钟频率、PCIe吞吐量
- ✅ 进程信息显示
- ✅ 2秒自动刷新

#### 性能监控
- ✅ GFLOPS、加速比、吞吐量
- ✅ 缓存命中率、任务成功率
- ✅ 轻量级基准测试

#### 智能优化
- ✅ 5类优化建议
- ✅ 可执行的操作步骤
- ✅ 严重程度分级

#### 实时推送
- ✅ SSE实时数据流（2秒）
- ✅ 自动重连机制

### Grafana Dashboard

#### 硬件指标 (Row 1)
- GPU Utilization (阈值: 70%/90%)
- GPU Temperature (阈值: 75°C/85°C)
- GPU Memory Usage (Used/Total)
- GPU Power (Usage/Limit)

#### 性能趋势 (Row 2)
- GPU & Memory Utilization (时间序列)
- GPU Temperature Trend (时间序列)

#### 性能指标 (Row 3)
- Matrix Performance (GFLOPS)
- Speedup Ratio (综合/矩阵/内存)
- Cache Hit Rate (阈值: 80%/50%)
- Task Success Rate (阈值: 95%/90%)
- Memory Bandwidth (GB/s)

#### 时钟和PCIe (Row 4)
- Clock Frequencies (SM/Memory Clock)
- PCIe Throughput (TX/RX)

## 文档

| 文档 | 描述 |
|------|------|
| [独立仪表板完成报告](docs/GPU_MONITORING_COMPLETION_REPORT.md) | GPU监控仪表板详细报告 |
| [独立仪表板快速开始](docs/GPU_MONITORING_QUICK_START.md) | 快速启动指南 |
| [Grafana集成指南](docs/GPU_MONITORING_GRAFANA_INTEGRATION.md) | Grafana集成完整指南 |
| [Grafana集成完成报告](docs/GPU_MONITORING_GRAFANA_COMPLETE.md) | Grafana集成完成报告 |

## API端点

### 独立GPU监控API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/gpu/metrics` | GET | 获取所有GPU指标 |
| `/api/gpu/metrics/{device_id}` | GET | 获取指定GPU指标 |
| `/api/gpu/processes/{device_id}` | GET | 获取GPU进程列表 |
| `/api/gpu/performance` | GET | 获取当前性能指标 |
| `/api/gpu/history/{device_id}?hours=N` | GET | 获取历史数据 |
| `/api/gpu/stats/{device_id}?hours=N` | GET | 获取聚合统计 |
| `/api/gpu/recommendations` | GET | 获取优化建议 |
| `/api/gpu/stream/{device_id}` | GET | SSE实时数据流 |

### Prometheus Exporter

| 端点 | 方法 | 描述 |
|------|------|------|
| `/metrics` | GET | Prometheus格式指标 |
| `/health` | GET | 健康检查 |

**Exporter地址**: `http://localhost:9100/metrics`

## Prometheus指标

### 硬件指标

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

### 性能指标

| 指标名称 | 描述 | 标签 |
|---------|------|------|
| `gpu_matrix_gflops` | 矩阵运算性能 (GFLOPS) | device_id |
| `gpu_matrix_speedup_ratio` | 矩阵运算加速比 | device_id |
| `gpu_matrix_throughput_ops_per_sec` | 矩阵运算吞吐量 (ops/s) | device_id |
| `gpu_memory_bandwidth_gbps` | 内存带宽 (GB/s) | device_id |
| `gpu_memory_speedup_ratio` | 内存操作加速比 | device_id |
| `gpu_memory_throughput_ops_per_sec` | 内存操作吞吐量 (ops/s) | device_id |
| `gpu_overall_speedup_ratio` | 综合加速比 | device_id |
| `gpu_cache_hit_rate_percent` | 缓存命中率 (%) | device_id |
| `gpu_task_success_rate_percent` | 任务成功率 (%) | device_id |

### 计数器和统计

| 指标名称 | 描述 | 标签 |
|---------|------|------|
| `gpu_benchmark_runs_total` | 基准测试次数 | device_id |
| `gpu_benchmark_duration_seconds` | 基准测试持续时间 | device_id, benchmark_type |

## 脚本说明

### 启动脚本

| 脚本 | 功能 |
|------|------|
| `start_gpu_monitoring.sh` | 启动独立GPU监控仪表板（API + 前端） |
| `start_gpu_exporter.sh` | 启动Prometheus Exporter |
| `start_gpu_monitoring_complete.sh` | 完整启动（API + Exporter + Grafana） |

### 停止脚本

| 脚本 | 功能 |
|------|------|
| `stop_gpu_monitoring.sh` | 停止独立GPU监控仪表板 |
| `stop_gpu_exporter.sh` | 停止Prometheus Exporter |
| `stop_gpu_monitoring_complete.sh` | 停止所有服务 |

## 架构

```
┌─────────────────────────────────────────────────────────┐
│                    GPU硬件                          │
│              (NVIDIA GPU + Driver)                    │
└───────────────────────┬───────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
┌───────▼────────┐            ┌─────────▼──────────┐
│  GPU监控API     │            │ Prometheus Exporter │
│   (端口8000)    │            │    (端口9100)      │
│                │            │                     │
│ - 硬件指标     │            │ - 指标采集        │
│ - 性能指标     │            │ - Prometheus格式    │
│ - SSE推送      │            └─────────┬───────────┘
└───────┬────────┘                      │
        │                               │
┌───────▼────────┐            ┌─────────▼─────────────┐
│ 独立GPU仪表板   │            │    Prometheus         │
│   (端口5173)   │            │    (端口9090)       │
│                │            │                      │
│ - 自定义UI      │            │ - 抓取指标(10s)    │
│ - SSE实时推送    │            │ - 存储时序数据      │
│ - 智能优化建议  │            └─────────┬───────────┘
└────────────────┘                      │
                                       │
                             ┌─────────▼─────────────┐
                             │       Grafana        │
                             │    (端口3000)       │
                             │                      │
                             │ - Dashboard (18个Panel)
                             │ - 可视化
                             │ - 告警配置
                             └──────────────────────┘
```

## 性能指标

| 指标 | 独立仪表板 | Grafana |
|------|-----------|---------|
| 指标采集延迟 | ~50ms | ~50ms |
| 实时推送延迟 | ~2秒 (SSE) | ~10秒 (Prometheus轮询) |
| 前端渲染 | ~300ms | ~500ms |
| 内存占用 | ~150MB | ~500MB |
| CPU占用 | <10% | <15% |

## 系统要求

### 必需
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+

### 可选
- NVIDIA GPU (无GPU时使用模拟数据)
- Docker (用于Grafana/Prometheus)
- Prometheus (用于Grafana Dashboard)
- Grafana (用于统一监控)

## 依赖安装

### Python包

```bash
pip install fastapi uvicorn pynvml psutil sqlalchemy pydantic prometheus_client
```

### Node.js包

```bash
cd web/frontend
npm install
```

### Docker服务

```bash
# Grafana + Prometheus
docker-compose -f monitoring-stack.yml up -d
```

## 故障排查

### 独立GPU监控仪表板

#### GPU不可用
```bash
# 检查GPU
nvidia-smi

# 检查日志
tail -f logs/gpu-api.log
tail -f logs/gpu-frontend.log
```

#### API无法访问
```bash
# 检查端口
netstat -tuln | grep 8000

# 测试健康检查
curl http://localhost:8000/health
```

### Grafana Dashboard

#### Exporter无法访问
```bash
# 检查Exporter
curl http://localhost:9100/metrics

# 检查日志
tail -f logs/gpu-exporter.log
```

#### Prometheus无法抓取
```bash
# 检查Prometheus配置
cat monitoring/prometheus.yml | grep gpu-metrics

# 重启Prometheus
docker restart mystocks-prometheus

# 检查目标
curl http://localhost:9090/api/v1/targets
```

#### Grafana无数据
```bash
# 测试Prometheus查询
curl 'http://localhost:9090/api/v1/query?query=gpu_utilization_percent'

# 检查Grafana数据源
# Grafana → Configuration → Data Sources → Prometheus → Test
```

## 使用建议

### 开发环境
- **独立GPU监控仪表板**: 实时性更好，开发调试方便
- **Grafana Dashboard**: 可选，用于统一监控

### 生产环境
- **同时使用**: 互补功能
- **独立仪表板**: 运维人员专用，实时监控
- **Grafana**: 统一监控平台，告警和报表

### 最佳实践
1. 使用独立仪表板进行日常监控
2. 使用Grafana进行长期趋势分析
3. 在Grafana中配置关键指标告警
4. 定期检查Exporter日志
5. 根据实际需求调整刷新间隔

## 许可证

MIT

## 联系

如有问题，请查看文档或提交Issue。

---

**最后更新**: 2025-12-29
**版本**: 1.0.0
