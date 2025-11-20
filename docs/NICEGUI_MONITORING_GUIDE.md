# MyStocks NiceGUI监控面板使用指南

## 📋 概述

本文档说明如何使用MyStocks NiceGUI监控面板，这是一个基于NiceGUI框架的现代化Web监控界面，提供实时的AI系统监控、告警管理和性能分析功能。

**适用版本**: MyStocks v3.0+  
**目标用户**: mystocks_nice分支开发者、运维工程师、监控管理员  
**最后更新**: 2025-11-16

---

## 🚀 快速开始

### 1. 环境准备

确保系统已安装以下依赖：

```bash
# 检查Python版本 (需要3.8+)
python3 --version

# 安装NiceGUI依赖
pip install nicegui uvicorn

# 或者使用项目requirements.txt
pip install -r requirements.txt
```

### 2. 启动监控面板

#### 方法一：使用启动脚本 (推荐)

```bash
# 基本启动
bash scripts/start_nicegui_monitoring.sh

# 指定地址和端口
bash scripts/start_nicegui_monitoring.sh --host 0.0.0.0 --port 9000

# 启用调试模式
bash scripts/start_nicegui_monitoring.sh --debug

# 查看帮助
bash scripts/start_nicegui_monitoring.sh --help
```

#### 方法二：直接运行Python

```bash
# 进入项目目录
cd /opt/claude/mystocks_spec

# 设置Python路径
export PYTHONPATH="$PWD:$PYTHONPATH"

# 启动监控面板
python3 -m uvicorn web.frontend.nicegui_monitoring_dashboard:app --host 127.0.0.1 --port 8889
```

### 3. 访问监控面板

启动成功后，访问以下地址：

- **监控面板**: http://127.0.0.1:8889
- **API文档**: http://127.0.0.1:8889/docs
- **健康检查**: http://127.0.0.1:8889/api/health
- **告警API**: http://127.0.0.1:8889/api/alerts
- **指标API**: http://127.0.0.1:8889/api/metrics

---

## 📊 界面功能详解

### 监控面板布局

```
┌─────────────────────────────────────────────────────────────────────┐
│  🔍 MyStocks AI实时监控系统  │  NiceGUI Web监控面板  │  🟢 在线     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  📊 系统指标概览                                                       │
│  ┌─────────┬─────────┬─────────┬─────────┐                          │
│  │ CPU使用率│ GPU使用率│ 内存使用率│ 活跃告警 │                          │
│  │   75%   │   60%   │   45%   │    2    │                          │
│  │ ████████│ ██████  │ █████   │ 🔴1🟡1🔵0│                          │
│  │   正常   │   正常   │   正常   │        │                          │
│  └─────────┴─────────┴─────────┴─────────┘                          │
│                                                                     │
│  🚨 告警状态管理                                                      │
│  🔴 严重 2  🟡 警告 1  🔵 信息 0                                     │
│  ┌────────────────────────────────────────────┐                     │
│  │ 当前活跃告警:                                │                     │
│  │ 🔴 CPU使用率过高                             │                     │
│  │    CPU使用率达到85% (阈值: 80%)              │                     │
│  │    [✅ 确认]                                  │                     │
│  └────────────────────────────────────────────┘                     │
│                                                                     │
│  💚 系统健康状态                                                      │
│  健康状态: HEALTHY    监控状态: RUNNING                              │
│  监控统计: 总循环 150 | 成功 148  成功率: 98.7%                       │
│                                                                     │
│  📈 实时性能图表                                                      │
│  CPU使用率趋势 (最近1分钟):                                         │
│  当前: 75%                                                           │
│  ████████████████████████████████                                   │
│                                                                     │
│  🎮 控制面板                                                          │
│  [▶️ 开始监控] [⏹️ 停止监控] [🧪 测试告警] [🔄 刷新数据]              │
│                                                                     │
│  📋 告警历史                                                         │
│  ┌────────┬────────┬────────┬────────┬────────┐                     │
│  │  时间   │  规则  │ 严重性 │  消息  │  状态  │                     │
│  ├────────┼────────┼────────┼────────┼────────┤                     │
│  │14:30:25│CPU过高 │ 警告   │CPU达85%│  已解决 │                     │
│  │14:25:10│GPU内存│ 严重   │GPU达92%│  已解决 │                     │
│  └────────┴────────┴────────┴────────┴────────┘                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 核心功能模块

#### 1. 📊 系统指标概览
- **CPU使用率**: 实时显示CPU使用百分比和状态
- **GPU使用率**: 显示GPU利用率和内存使用情况
- **内存使用率**: 物理内存使用状态
- **活跃告警**: 当前未解决的告警数量统计

#### 2. 🚨 告警管理
- **告警级别**: 按严重性分类显示 (严重/警告/信息)
- **活跃告警列表**: 实时显示未解决的告警
- **告警确认**: 点击确认按钮标记告警为已处理
- **告警详情**: 显示告警规则、当前值、阈值等信息

#### 3. 💚 系统健康状态
- **整体健康**: 基于系统各组件状态的综合评估
- **监控状态**: 显示监控服务的运行状态
- **性能统计**: 监控循环次数、成功率、平均执行时间

#### 4. 📈 实时图表
- **性能趋势**: CPU/GPU/内存使用率趋势图
- **文本图表**: 简单直观的ASCII风格图表
- **历史数据**: 最近1分钟的性能变化

#### 5. 🎮 控制面板
- **开始/停止监控**: 启停实时监控系统
- **测试告警**: 发送测试告警验证系统功能
- **刷新数据**: 手动刷新当前显示的数据

#### 6. 📋 告警历史
- **历史表格**: 显示所有告警记录
- **状态追踪**: 跟踪告警从触发到解决的状态
- **时间序列**: 按时间顺序展示告警历史

---

## 🔧 API接口

### 健康检查

```
GET /api/health
```

**响应示例**:
```json
{
  "overall_status": "healthy",
  "checks": {
    "monitoring_status": {
      "status": "running",
      "message": "监控正常运行"
    },
    "alert_system": {
      "status": "healthy",
      "message": "无活跃告警"
    },
    "gpu_status": {
      "status": "available",
      "message": "GPU监控可用"
    }
  },
  "timestamp": "2025-11-16T10:30:00"
}
```

### 告警信息

```
GET /api/alerts
```

**响应示例**:
```json
{
  "summary": {
    "active_alerts_count": 1,
    "total_alerts": 25,
    "critical_alerts": 2,
    "warning_alerts": 3,
    "info_alerts": 0,
    "resolved_alerts": 20,
    "alert_rules_count": 6,
    "enabled_rules_count": 6
  },
  "active_alerts": [
    {
      "id": "alert_20251116_103025",
      "rule_name": "CPU使用率过高",
      "alert_type": "system_resource_high",
      "severity": "warning",
      "message": "CPU使用率过高: 85.0% (阈值: 80%)",
      "timestamp": "2025-11-16T10:30:25",
      "metrics": {
        "current_value": 85.0,
        "threshold": 80.0,
        "duration_seconds": 60
      },
      "resolved": false,
      "acknowledged": false
    }
  ]
}
```

### 性能指标

```
GET /api/metrics
```

**响应示例**:
```json
{
  "monitoring_status": "running",
  "current_metrics": {
    "cpu_usage": "75.3%",
    "memory_usage": "45.2%",
    "gpu_utilization": "60.8%",
    "gpu_memory_usage": "5120/8192MB",
    "disk_usage": "35.1%",
    "active_strategies": 3,
    "win_rate": "57.1%",
    "daily_return": "1.23%"
  },
  "statistics": {
    "total_cycles": 150,
    "successful_cycles": 148,
    "failed_cycles": 2,
    "success_rate": "98.7%",
    "avg_cycle_time": "0.052s",
    "history_size": 148,
    "monitoring_duration": "1250s"
  },
  "configuration": {
    "monitoring_interval": "5.2s",
    "adaptive_intervals": true,
    "gpu_monitoring": true,
    "ai_strategy_monitoring": true
  }
}
```

### 系统控制

```
POST /api/control/{action}
```

**可用操作**:
- `start`: 启动监控
- `stop`: 停止监控

**请求示例**:
```bash
curl -X POST http://127.0.0.1:8889/api/control/start
```

---

## ⚙️ 配置选项

### 启动参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--host` | 监听地址 | `127.0.0.1` |
| `--port` | 监听端口 | `8889` |
| `--debug` | 启用调试模式 | `false` |

### 环境变量

```bash
# 设置日志级别
export LOG_LEVEL="info"  # debug, info, warning, error

# 设置Python路径
export PYTHONPATH="/opt/claude/mystocks_spec:$PYTHONPATH"

# 设置NiceGUI配置
export NICEGUI_FASTAPI_RELOAD=false
```

### 监控配置

可以通过修改 `AIRealtimeMonitor` 的配置来调整监控行为：

```python
from src.monitoring.ai_realtime_monitor import MonitoringConfig

config = MonitoringConfig(
    monitoring_interval=5.0,        # 监控间隔(秒)
    max_history_size=1000,          # 最大历史记录数
    enable_gpu_monitoring=True,     # 启用GPU监控
    enable_ai_strategy_monitoring=True,  # 启用AI策略监控
    adaptive_intervals=True,        # 启用自适应间隔
    alert_check_frequency=1         # 告警检查频率
)
```

---

## 🚨 告警规则

系统内置以下告警规则：

| 规则名称 | 触发条件 | 严重性 | 阈值 | 持续时间 |
|----------|----------|--------|------|----------|
| CPU使用率过高 | CPU > 80% | 警告 | 80% | 60秒 |
| GPU内存使用率过高 | GPU内存 > 85% | 警告 | 85% | 30秒 |
| AI策略胜率异常 | 胜率 < 30% | 严重 | 30% | 300秒 |
| AI策略回撤过大 | 回撤 > 5% | 严重 | 5% | 180秒 |
| 数据质量异常 | 质量分 < 80% | 警告 | 80% | 120秒 |
| 慢查询检测 | 查询时间 > 5秒 | 警告 | 5000ms | 30秒 |

### 自定义告警规则

可以通过代码添加自定义告警规则：

```python
from src.monitoring.ai_alert_manager import AlertRule, AlertType, AlertSeverity

# 创建自定义规则
custom_rule = AlertRule(
    name="自定义规则",
    alert_type=AlertType.SYSTEM_RESOURCE_HIGH,
    severity=AlertSeverity.INFO,
    threshold=95.0,
    duration_seconds=10,
    enabled=True,
    description="自定义告警规则描述"
)

# 添加到告警管理器
alert_manager.add_alert_rule(custom_rule)
```

---

## 🔧 故障排除

### 常见问题

#### 1. 端口占用
```
Error: [Errno 98] Address already in use
```
**解决方案**:
```bash
# 查看端口占用
netstat -tlnp | grep 8889

# 更换端口启动
bash scripts/start_nicegui_monitoring.sh --port 8890
```

#### 2. 依赖包缺失
```
ModuleNotFoundError: No module named 'nicegui'
```
**解决方案**:
```bash
# 安装依赖
pip install nicegui uvicorn

# 或使用requirements.txt
pip install -r requirements.txt
```

#### 3. 监控数据不更新
**可能原因**:
- AIRealtimeMonitor未启动
- 系统指标收集失败
- 前端刷新间隔设置过长

**解决方案**:
1. 点击"开始监控"按钮
2. 检查控制台日志输出
3. 访问 `/api/health` 检查系统状态

#### 4. GPU监控不可用
**解决方案**:
```bash
# 安装GPUtil
pip install GPUtil

# 检查GPU状态
nvidia-smi
```

### 日志调试

#### 启用详细日志
```bash
# 启动时指定debug级别
bash scripts/start_nicegui_monitoring.sh --debug

# 或设置环境变量
export LOG_LEVEL=debug
```

#### 查看监控日志
```bash
# 实时查看日志
tail -f /tmp/nicegui_monitoring.log

# 或查看控制台输出
python3 -m uvicorn web.frontend.nicegui_monitoring_dashboard:app --log-level debug
```

---

## 🎯 最佳实践

### 1. 监控配置优化

- **生产环境**: 设置较长监控间隔(10-30秒)以减少系统负载
- **开发环境**: 使用较短间隔(2-5秒)便于调试
- **GPU监控**: 在有GPU的系统中启用，禁用以节省资源

### 2. 告警管理

- **合理阈值**: 根据系统实际性能设置合适的告警阈值
- **告警确认**: 及时确认和处理告警，避免告警积压
- **告警测试**: 定期使用测试告警功能验证系统正常

### 3. 性能监控

- **历史数据**: 定期查看历史图表，识别性能趋势
- **成功率监控**: 关注监控循环成功率，确保系统稳定
- **自适应调整**: 启用自适应间隔，根据系统负载自动调整

### 4. 安全考虑

- **网络访问**: 生产环境中使用防火墙限制访问
- **认证授权**: 根据需要添加用户认证机制
- **数据保护**: 避免在日志中记录敏感信息

---

## 📈 性能基准

### 系统要求

- **CPU**: 2核心以上
- **内存**: 4GB以上
- **Python**: 3.8+
- **网络**: 100Mbps以上

### 性能指标

- **响应时间**: 页面加载 < 2秒
- **监控开销**: CPU使用 < 5%
- **内存占用**: 基础运行 < 100MB
- **数据刷新**: 实时更新 < 5秒

### 扩展性

- **并发用户**: 支持10+并发访问
- **历史数据**: 支持1000+历史记录
- **告警容量**: 支持100+活跃告警
- **API调用**: 每秒100+次API请求

---

## 📞 技术支持

### 获取帮助

1. **查看文档**: 参考本指南和API文档
2. **检查日志**: 查看监控日志和错误信息
3. **健康检查**: 访问 `/api/health` 检查系统状态
4. **社区支持**: 通过GitHub Issues提交问题

### 报告问题

提交问题时请包含以下信息：

```bash
# 系统信息
python3 --version
pip list | grep -E "(nicegui|uvicorn)"

# 错误日志
tail -n 50 /tmp/nicegui_monitoring.log

# 健康检查结果
curl http://127.0.0.1:8889/api/health
```

---

**🏷️ 文档标签**: `#NiceGUI` `#监控系统` `#Web界面` `#实时监控` `#告警管理`

**📌 版本信息**:
- **文档版本**: v1.0.0
- **适用版本**: MyStocks v3.0+
- **最后更新**: 2025-11-16
- **维护者**: MyStocks AI开发团队

---

*本文档为MyStocks NiceGUI监控面板的完整使用指南。如有疑问或建议，请通过GitHub Issues反馈。*