# MyStocks 监控系统 - 文档索引

## 📑 快速导航

### 🚀 从这里开始

**第一次接触本项目?** 
→ 先读 [`MONITORING_SYSTEM_SUMMARY.md`](./MONITORING_SYSTEM_SUMMARY.md)

**想要完整的技术细节?**
→ 查看 [`docs/monitoring/MONITORING_EXPLORATION_REPORT.md`](./docs/monitoring/MONITORING_EXPLORATION_REPORT.md)

**需要代码示例和API参考?**
→ 参考 [`docs/monitoring/MONITORING_CODE_REFERENCE.md`](./docs/monitoring/MONITORING_CODE_REFERENCE.md)

**想快速入门?**
→ 查看 [`docs/monitoring/README.md`](./docs/monitoring/README.md)

---

## 📚 完整文档清单

### 核心文档

| 文档 | 位置 | 大小 | 用途 |
|------|------|------|------|
| **总结概览** | `./MONITORING_SYSTEM_SUMMARY.md` | 8.6KB | 快速了解整个监控系统 |
| **完整探索报告** | `./docs/monitoring/MONITORING_EXPLORATION_REPORT.md` | 19KB | 详细的代码分析和架构设计 |
| **代码参考指南** | `./docs/monitoring/MONITORING_CODE_REFERENCE.md` | 12KB | 代码示例和使用方式 |
| **快速入门指南** | `./docs/monitoring/README.md` | 6.3KB | 导航和常用命令 |

### 文档总大小: ~46KB

---

## 🎯 按需求查找文档

### 如果你想...

#### 快速了解项目状态
```
MONITORING_SYSTEM_SUMMARY.md
└─ 第 1 部分: 现有的强大基础设施 ✅
└─ 第 2 部分: 核心位置地图
└─ 结论: MyStocks 已有业界级别的监控基础
```

#### 学习各个监控组件
```
MONITORING_EXPLORATION_REPORT.md
└─ 第 2 部分: 现有监控代码功能详解
   ├─ A. 监控数据库 (MonitoringDatabase)
   ├─ B. 性能监控 (PerformanceMonitor)
   ├─ C. 数据质量监控 (DataQualityMonitor)
   ├─ D. Prometheus指标端点
   ├─ E. 缓存管理系统
   ├─ F. 监控API端点
   └─ G. 请求时间日志中间件
```

#### 了解可复用的代码
```
MONITORING_EXPLORATION_REPORT.md
└─ 第 3 部分: 可复用的代码部分
   ├─ 上下文管理器模式
   ├─ 指标数据类
   ├─ Prometheus指标定义
   ├─ 中间件响应时间记录
   ├─ 缓存统计度量
   ├─ 告警基础结构
   ├─ Socket.IO集成
   └─ WebSocket Tick接收
```

#### 找出需要实现什么
```
MONITORING_SYSTEM_SUMMARY.md
└─ 第 4 部分: 需要新增的功能（优先级排序）
   ├─ P1 - 关键: MetricsCollector
   ├─ P2 - 重要: 数据库连接池监控
   └─ P3 - 增强: 成本分析、告警规则引擎
```

#### 复制粘贴代码使用
```
MONITORING_CODE_REFERENCE.md
└─ 第 1 部分: 核心代码片段库
   ├─ PerformanceMonitor使用示例
   ├─ MonitoringDatabase使用示例
   ├─ DataQualityMonitor使用示例
   ├─ AlertManager使用示例
   ├─ 缓存系统使用示例
   ├─ Prometheus指标集成
   ├─ 请求响应时间中间件
   └─ Socket.IO实时推送
```

#### 了解架构和集成方案
```
MONITORING_EXPLORATION_REPORT.md
└─ 第 5 部分: 集成建议
   ├─ 推荐集成架构（图表）
   └─ 实现步骤（5步）
```

#### 查看实现路线图
```
MONITORING_SYSTEM_SUMMARY.md
└─ 建议的实现路线图
   ├─ 第1阶段（1-2天）: MetricsCollector
   ├─ 第2阶段（2-3天）: 自动化定时任务
   └─ 第3阶段（2-3天）: 实时仪表板推送
```

---

## 📍 源代码位置参考

### 监控核心模块
```
src/monitoring/
├── monitoring_database.py         (20KB) ← 监控日志存储
├── performance_monitor.py         (13KB) ← 性能跟踪
├── data_quality_monitor.py        (16KB) ← 数据质量检查
├── alert_manager.py               (91行) ← 告警管理
└── monitoring_service.py          (36KB) ← 完整监控服务
```

### Web API监控组件
```
web/backend/app/
├── api/
│   ├── metrics.py                 (142行) ← Prometheus端点
│   └── monitoring.py              (~300行) ← 监控API
├── core/
│   ├── cache_manager.py           (16KB) ← 缓存管理
│   ├── cache_eviction.py          (12KB) ← 缓存淘汰
│   ├── cache_prewarming.py        (11KB) ← 缓存预热
│   ├── socketio_manager.py        (24KB) ← WebSocket
│   └── connection_lifecycle.py    (处理连接)
└── main.py                        (中间件)
```

### 其他监控相关
```
src/ml_strategy/realtime/
├── tick_receiver.py               (~300行) ← WebSocket数据接收

src/gpu/api_system/utils/
├── cache_optimization.py          (~300行) ← 缓存优化
└── monitoring.py                  ← GPU监控

src/database_optimization/
├── performance_monitor.py         ← 数据库性能
└── slow_query_analyzer.py        ← 慢查询分析
```

---

## 🔑 核心概念速查

### 关键指标阈值
```
慢查询阈值      : 5000ms (自动CRITICAL告警)
警告阈值        : 2000ms (WARNING日志)
缓存命中率目标  : >80%
数据缺失率限制  : <5%
数据延迟限制    : <300s (5分钟)
```

### 已定义Prometheus指标
```
HTTP层面:
  - mystocks_http_requests_total (Counter)
  - mystocks_http_request_duration_seconds (Histogram)

数据库层面:
  - mystocks_db_connections_active (Gauge)
  - mystocks_db_connections_idle (Gauge)

缓存层面:
  - mystocks_cache_hits_total (Counter)
  - mystocks_cache_misses_total (Counter)

系统健康:
  - mystocks_api_health_status (Gauge)
  - mystocks_datasource_availability (Gauge)
```

### 数据分类(Classification)
```
TICK_DATA      : 实时行情数据
MINUTE_DATA    : 分钟K线数据
DAILY_KLINE    : 日线数据
REFERENCE_DATA : 参考数据
DERIVED_DATA   : 衍生数据
TRANSACTION    : 交易数据
METADATA       : 元数据
```

---

## 📊 文档统计

### 总内容量
```
总计 4 个文档
总计 1743 行
总计 ~46KB

内容分布:
  - 总结类: 364 行 (MONITORING_SYSTEM_SUMMARY.md)
  - 详解类: 614 行 (MONITORING_EXPLORATION_REPORT.md)
  - 代码类: 511 行 (MONITORING_CODE_REFERENCE.md)
  - 导航类: 254 行 (README.md)
```

### 源代码统计
```
现有监控代码: ~250KB
核心监控文件: 5 个
API监控端点: 2 个
缓存管理文件: 4 个
Prometheus指标: 10+
监控API端点: 10+
```

---

## ✅ 使用建议

### 第一次使用
1. ✅ 阅读 `MONITORING_SYSTEM_SUMMARY.md` 了解全景
2. ✅ 查看本索引找到相关文档
3. ✅ 根据需求选择对应文档详读

### 开发过程中
1. 📖 需要理论知识 → `MONITORING_EXPLORATION_REPORT.md`
2. 💻 需要代码示例 → `MONITORING_CODE_REFERENCE.md`
3. 🚀 需要快速参考 → `MONITORING_SYSTEM_SUMMARY.md`
4. 🗺️ 需要导航帮助 → `docs/monitoring/README.md`

### 集成开发
1. 查看"需要新增的功能"列表（优先级P1-P3）
2. 查看"建议的实现路线图"
3. 参考对应的代码示例
4. 在源代码中实现集成

---

## 🔗 相关资源

### 项目相关文档
- [项目README](./README.md) - 项目概览
- [CLAUDE.md](./CLAUDE.md) - 开发指南
- [API文档](./docs/api/) - API规范

### 源代码文件
- 监控模块: `src/monitoring/`
- API组件: `web/backend/app/api/`
- 缓存系统: `web/backend/app/core/`
- 数据库: `src/storage/database/`

---

## 💡 快速技巧

### 查看监控模块大小
```bash
du -sh /opt/claude/mystocks_spec/src/monitoring/
du -sh /opt/claude/mystocks_spec/web/backend/app/core/cache*
```

### 查看所有监控相关文件
```bash
find /opt/claude/mystocks_spec -type f -name "*monitor*" -o -name "*metric*"
```

### 测试Prometheus指标
```bash
curl http://localhost:8000/metrics
```

### 导入监控模块
```python
from src.monitoring import (
    MonitoringDatabase,
    PerformanceMonitor,
    DataQualityMonitor,
    AlertManager
)
```

---

## 📞 获取帮助

### 如果文档不清楚
1. 检查相应的源代码文件
2. 查看代码注释和文档字符串
3. 参考`MONITORING_CODE_REFERENCE.md`的示例

### 如果需要更新
1. 检查最新的源代码
2. 更新相应文档
3. 保持文档与代码同步

---

## 版本信息

```
生成时间    : 2025-11-12
文档版本    : 1.0
项目        : MyStocks 专业量化交易数据管理系统
状态        : 基础设施完整，等待集成
维护者      : MyStocks团队
```

---

**提示**: 如果你是第一次接触本文档，建议按以下顺序阅读:
1. 本索引（理解整体结构） ← 你在这里
2. `MONITORING_SYSTEM_SUMMARY.md`（5分钟快速了解）
3. `docs/monitoring/README.md`（架构和导航）
4. 根据具体需求查看详细文档

