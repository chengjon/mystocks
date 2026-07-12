# 交易信号监控指标系统设计方案

> **版本**: v3.0 (当前代码对齐)
> **日期**: 2026-07-12（审计更新）
> **状态**: ✅ 绝大部分已完成（约85%，待补充信号告警规则）
> **参考架构**: 指标计算系统V2.1, 数据源管理V2.0
> **相关文档**: [信号监控体系梳理报告](../../reports/SIGNAL_MONITORING_SYSTEM_INVENTORY_20260108.md)

---

## 📝 更新日志

### v3.0 (2026-07-12)
- ✅ 与当前代码库现实对齐
- ✅ 修正 15+ 项过时 ❌/✅ 标记为实际状态
- ✅ 新增 `signal_recorder.py` / `signal_result_tracker.py` / `signal_push_integration.py` 描述
- ✅ 更新行数：`signal_decorator.py` 545→295
- ✅ 标注剩余待办：4 条信号告警规则
- ✅ 更新总体完成度：~30% → ~85%

### v2.0 (2026-01-08)
- ✅ 更新当前实施状态
- ✅ 标记已完成和待实现的功能
- ✅ 基于全面梳理结果更新架构
- ✅ 提供更具体的实施路线图

### v1.0 (原始版本)
- 📋 初始设计方案
- 📋 9个Prometheus指标定义
- 📋 技术实施计划

---

## 1️⃣ 设计目标

### 1.1 背景

#### 当前系统已实现（✅已完成）
- ✅ **Prometheus指标模块**: `src/monitoring/signal_metrics.py` (231行)
- ✅ **信号监控装饰器**: `src/monitoring/signal_decorator.py` (545行)
- ✅ **信号聚合任务**: `src/monitoring/signal_aggregation_task.py`
- ✅ **监控数据库基础设施**: `src/monitoring/infrastructure/postgresql_async_v3.py`
- ✅ **前端监控页面**: 6个Vue组件
- ✅ **API端点**: 监控清单管理API (7个端点)
- ✅ **指标计算系统**: 4个已实现指标 (SMA, EMA, MACD, RSI)

#### 当前代码库实际状态（2026-07-12 审计）
> ⚠️ 以下于 2026-01-08~2026-03 期间已实现，文档 v2.0 未及时更新。

- ✅ **数据库表**：`scripts/migrations/002_signal_monitoring_tables.sql`（4 张表：signal_records, signal_execution_results, signal_push_logs, strategy_health）+ `003_signal_statistics_hourly.sql`
- ✅ **信号记录服务**：`src/monitoring/signal_recorder.py`（406 行）
- ✅ **信号结果追踪**：`src/monitoring/signal_result_tracker.py`（443 行）
- ✅ **信号统计API端点**：`/api/signals/statistics`、`/api/signals/active`、`/api/strategies/{id}/health/detailed` — 在 `web/backend/app/api/signal_monitoring/` 中
- ✅ **Grafana信号监控Dashboard**：`data/grafana/provisioning/dashboards/trading-signals-dashboard.json`（9 面板）+ `config/grafana-dashboards/dashboards/signal-monitoring.json`（10 面板）
- ✅ **信号推送集成**：`src/monitoring/signal_push_integration.py`（249 行）— 含 `@monitor_signal_push` 装饰器
- ✅ **服务集成**：`SignalGenerationService` 已使用 `signal_metrics`/`signal_recorder`；策略通知管理器已使用 `MonitoredStrategyExecutor`
- ✅ **聚合任务**：`src/monitoring/signal_aggregation_task.py`（624 行）— 含 `SignalMetricsAggregator`、`MetricsScheduler`、`SignalStatisticsAggregator`
- ✅ **聚合启动脚本**：`scripts/runtime/run_signal_aggregation.py`
- ✅ **单元/集成/E2E测试**：4 个测试文件覆盖

#### 剩余待实现（❌）
- ❌ Prometheus信号专用告警规则（4 条：SignalAccuracyLow / SignalLatencyHigh / StrategyUnhealthy / SignalPushFailureRate）

### 1.2 核心指标（9个）- 已定义

| 序号 | 指标名称 | 类型 | 代码状态 | 说明 |
|------|----------|------|----------|------|
| 1 | `mystocks_signal_generation_total` | Counter | ✅ 已实现 | 信号生成计数器 |
| 2 | `mystocks_signal_accuracy_percentage` | Gauge | ✅ 已实现 | 信号准确度百分比 |
| 3 | `mystocks_signal_latency_seconds` | Histogram | ✅ 已实现 | 信号生成延迟分布 |
| 4 | `mystocks_active_signals_count` | Gauge | ✅ 已实现 | 活跃信号数量 |
| 5 | `mystocks_signal_success_rate` | Gauge | ✅ 已实现 | 信号成功率 |
| 6 | `mystocks_signal_profit_ratio` | Gauge | ✅ 已实现 | 盈利比率 |
| 7 | `mystocks_signal_push_total` | Counter | ✅ 已实现 | 推送通知计数器 |
| 8 | `mystocks_signal_push_latency_seconds` | Histogram | ✅ 已实现 | 推送延迟分布 |
| 9 | `mystocks_strategy_health_status` | Gauge | ✅ 已实现 | 策略健康状态 |

**状态**: 所有9个Prometheus指标已在 `src/monitoring/signal_metrics.py` 中定义完成！

---

## 2️⃣ 当前实施状态

### 2.1 已完成功能（✅）

#### 核心代码模块
```
✅ src/monitoring/signal_metrics.py (231行)
   - 9个Prometheus指标定义
   - 9个辅助函数（record_signal_generation, record_signal_latency等）

✅ src/monitoring/signal_decorator.py (545行)
   - MonitoredStrategyExecutor (监控包装器)
   - SignalMonitoringContext (监控上下文)
   - SignalMetricsCollector (批量指标收集)
   - monitor_signal_push (推送监控装饰器)

✅ src/monitoring/signal_aggregation_task.py
   - 信号聚合任务

✅ src/monitoring/infrastructure/postgresql_async_v3.py
   - 异步PostgreSQL访问
   - 监控数据库支持
```

#### 前端页面
```
✅ web/frontend/src/views/monitoring/AlertRulesManagement.vue
✅ web/frontend/src/views/monitoring/MonitoringDashboard.vue
✅ web/frontend/src/views/monitoring/RiskDashboard.vue
✅ web/frontend/src/views/monitoring/WatchlistManagement.vue
✅ web/frontend/src/views/RealTimeMonitor.vue
✅ web/frontend/src/views/RiskMonitor.vue
```

#### API端点
```
✅ POST /api/monitoring/watchlists - 创建清单
✅ GET /api/monitoring/watchlists - 获取所有清单
✅ GET /api/monitoring/watchlists/{id} - 获取单个清单
✅ POST /api/monitoring/watchlists/{id}/stocks - 添加股票
✅ DELETE /api/monitoring/watchlists/{id}/stocks/{code} - 移除股票
... (共7个端点)
```

### 2.2 当前实际状态（全量更新 v3.0）

> 以下标注反映 2026-07-12 代码审计结果。

#### 数据库表 ✅ 已完成
```sql
-- ✅ scripts/migrations/002_signal_monitoring_tables.sql
-- 包含: signal_records, signal_execution_results, signal_push_logs, strategy_health

-- ✅ scripts/migrations/003_signal_statistics_hourly.sql
-- 包含: signal_statistics_hourly（含小时级统计指标）
```

#### API端点 ✅ 已完成
```
✅ GET /api/signals/statistics -- web/backend/app/api/signal_monitoring/get_signal_statistics.py
✅ GET /api/signals/active -- web/backend/app/api/signal_monitoring/get_signal_statistics.py
✅ GET /api/strategies/{id}/health/detailed -- web/backend/app/api/signal_monitoring/get_signal_statistics.py
```

#### Grafana ✅ 已完成
```
✅ data/grafana/provisioning/dashboards/trading-signals-dashboard.json (9 panels)
   - 信号准确度 | 信号成功率 | 活跃信号数量
   - 策略健康状态 | 信号盈利比率 | 信号生成速率
   - 信号生成延迟分布 | 信号统计概览

✅ config/grafana-dashboards/dashboards/signal-monitoring.json (10 panels, 749行)
   - 信号生成速率 | 信号准确率 | 信号生成延迟分布
   - 信号成功率 | 策略健康状态 | 活跃信号数量
   - 1天盈利比率 | 推送总数 | 推送延迟 | 信号类型分布
```

#### 告警规则 🔄 部分完成
```
✅ config/alerts/mystocks-alerts.yml — 通用API/数据库/系统告警已配置
❌ 信号专用告警规则（4 条待补充）:
   - SignalAccuracyLow
   - SignalLatencyHigh
   - StrategyUnhealthy
   - SignalPushFailureRate
```

---

## 3️⃣ 指标详细定义（已实现）

### 3.1 信号生成指标

#### 信号生成计数器
```python
# ✅ 已实现: src/monitoring/signal_metrics.py:24-28
SIGNAL_GENERATION_TOTAL = Counter(
    "mystocks_signal_generation_total",
    "Total number of signals generated",
    ["strategy_id", "signal_type", "symbol", "status"]
)
```

**Labels**:
- `strategy_id`: 策略标识
- `signal_type`: BUY/SELL/HOLD
- `symbol`: 标的代码
- `status`: generated/rejected/filtered

**辅助函数**: `record_signal_generation()` - ✅ 已实现

---

#### 信号生成延迟
```python
# ✅ 已实现: src/monitoring/signal_metrics.py:30-35
SIGNAL_LATENCY_SECONDS = Histogram(
    "mystocks_signal_latency_seconds",
    "Signal generation latency in seconds",
    ["strategy_id", "indicator_count"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)
```

**Bucket范围**: 1ms ~ 1000ms

**辅助函数**: `record_signal_latency()` - ✅ 已实现

---

### 3.2 信号质量指标

#### 信号准确度百分比
```python
# ✅ 已实现: src/monitoring/signal_metrics.py:41-45
SIGNAL_ACCURACY_PERCENTAGE = Gauge(
    "mystocks_signal_accuracy_percentage",
    "Signal accuracy percentage (0-100), calculated from executed signals",
    ["strategy_id", "signal_type"]
)
```

**计算方式**: `(profitable_signals / total_signals) * 100`

**辅助函数**: `update_signal_accuracy()` - ✅ 已实现

---

#### 信号成功率
```python
# ✅ 已实现: src/monitoring/signal_metrics.py:47-49
SIGNAL_SUCCESS_RATE = Gauge(
    "mystocks_signal_success_rate",
    "Signal execution success rate (0-100)",
    ["strategy_id", "signal_type"]
)
```

**定义**: 成功执行（未被撤销或拒绝）的信号占比

**辅助函数**: `update_signal_success_rate()` - ✅ 已实现

---

#### 盈利比率
```python
# ✅ 已实现: src/monitoring/signal_metrics.py:51-55
SIGNAL_PROFIT_RATIO = Gauge(
    "mystocks_signal_profit_ratio",
    "Profit ratio of executed signals (0-100)",
    ["strategy_id", "time_window"]  # time_window: 1d/1w/1m/3m
)
```

**计算**: `(盈利信号数 / 总执行信号数) * 100`

**辅助函数**: `update_profit_ratio()` - ✅ 已实现

---

#### 活跃信号数量
```python
# ✅ 已实现: src/monitoring/signal_metrics.py:57-61
ACTIVE_SIGNALS_COUNT = Gauge(
    "mystocks_active_signals_count",
    "Number of currently active signals waiting for execution",
    ["strategy_id", "symbol", "signal_type"]
)
```

**用途**: 实时监控系统当前待执行的信号数量

**辅助函数**: `update_active_signals_count()` - ✅ 已实现

---

### 3.3 推送指标

#### 推送通知计数器
```python
# ✅ 已实现: src/monitoring/signal_metrics.py:67-71
SIGNAL_PUSH_TOTAL = Counter(
    "mystocks_signal_push_total",
    "Total number of signal push notifications",
    ["channel", "status"]  # channel: websocket/email/sms/app
)
```

**Labels**:
- `channel`: websocket/email/sms/push
- `status`: success/failed/timeout

**辅助函数**: `record_signal_push()` - ✅ 已实现

---

#### 推送延迟
```python
# ✅ 已实现: src/monitoring/signal_metrics.py:73-78
SIGNAL_PUSH_LATENCY_SECONDS = Histogram(
    "mystocks_signal_push_latency_seconds",
    "Signal push notification latency in seconds",
    ["channel"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)
```

**Bucket范围**: 10ms ~ 5000ms

**辅助函数**: `record_push_latency()` - ✅ 已实现

---

### 3.4 策略健康指标

#### 策略健康状态
```python
# ✅ 已实现: src/monitoring/signal_metrics.py:84-86
STRATEGY_HEALTH_STATUS = Gauge(
    "mystocks_strategy_health_status",
    "Strategy health status (1=healthy, 0=degraded, -1=unhealthy)",
    ["strategy_id"]
)
```

**健康检查项**:
- 指标计算是否正常
- 信号生成是否超时
- 推送是否失败

**辅助函数**: `update_strategy_health()` - ✅ 已实现

---

## 4️⃣ 技术实现方案（已实现）

### 4.1 信号监控装饰器

**文件**: `src/monitoring/signal_decorator.py` (545行)

#### 核心类

**MonitoredStrategyExecutor** - 监控包装器
```python
# ✅ 已实现
class MonitoredStrategyExecutor:
    def __init__(self, original_executor: Any, strategy_id: str = "default"):
        self._executor = original_executor
        self._strategy_id = strategy_id
        self._monitoring_context: Optional[SignalMonitoringContext] = None

    def execute(self, symbols, start_date=None, end_date=None, **kwargs):
        # 1. 创建监控上下文
        self._monitoring_context = SignalMonitoringContext(self._strategy_id)
        start_time = time.time()

        try:
            # 2. 执行策略
            result = self._executor.execute(symbols=symbols, ...)

            # 3. 记录信号生成
            for signal in signals:
                self._monitoring_context.record_signal(signal_type, symbol)

            # 4. 记录GPU使用
            if hasattr(self._executor, "_gpu_used"):
                self._monitoring_context.record_gpu_usage(latency_ms)

            # 5. 更新Gauge指标
            self._monitoring_context.update_gauges()

            return result
```

**使用方式**:
```python
from src.monitoring.signal_decorator import monitored_strategy

# 包装现有的StrategyExecutor
executor = StrategyExecutor(strategy, signal_manager)
monitored_executor = monitored_strategy(executor)

# 正常使用，自动记录监控指标
result = monitored_executor.execute(symbols)
```

---

**SignalMonitoringContext** - 监控上下文
```python
# ✅ 已实现
class SignalMonitoringContext:
    def __init__(self, strategy_id: str):
        self.strategy_id = strategy_id
        self.start_time = time.time()
        self.signals_generated: Dict[str, int] = {"BUY": 0, "SELL": 0, "HOLD": 0}
        self.signals_by_symbol: Dict[str, Dict[str, int]] = {}
        self.push_results: Dict[str, Dict[str, int]] = {}
        self.errors: List[str] = []

    def record_signal(self, signal_type: str, symbol: str) -> None:
        # 记录到Prometheus
        if record_signal_generation:
            record_signal_generation(
                strategy_id=self.strategy_id,
                signal_type=signal_type,
                symbol=symbol,
                status="generated"
            )

    def update_gauges(self) -> None:
        # 更新策略健康状态
        if update_strategy_health:
            health_status = 1 if len(self.errors) == 0 else 0
            update_strategy_health(self.strategy_id, health_status)
```

---

### 4.2 推送监控装饰器

```python
# ✅ 已实现: src/monitoring/signal_decorator.py:494-530
def monitor_signal_push(channel: str) -> Callable:
    """
    推送监控装饰器

    Example:
        class PushService:
            @monitor_signal_push("websocket")
            async def send_signal(self, signal):
                ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                latency_ms = (time.time() - start_time) * 1000

                # 记录成功推送
                if record_signal_push:
                    record_signal_push(channel=channel, status="success")
                if record_push_latency:
                    record_push_latency(channel=channel, latency_seconds=latency_ms / 1000)

                return result
            except Exception as e:
                # 记录失败推送
                if record_signal_push:
                    record_signal_push(channel=channel, status="failed")
                raise

        return wrapper
    return decorator
```

---

## 5️⃣ 数据存储设计（✅ 已实现）

### 5.1 信号执行结果表

**状态**: ✅ 已实现（`scripts/migrations/002_signal_monitoring_tables.sql`）

```sql
-- 位置: scripts/migrations/001_signal_tables.sql
CREATE TABLE signal_execution_results (
    id SERIAL PRIMARY KEY,
    signal_id VARCHAR(100) UNIQUE NOT NULL,
    strategy_id VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(10) NOT NULL,  -- BUY/SELL
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 执行结果
    executed_at TIMESTAMP,
    execution_status VARCHAR(20),  -- pending/executed/cancelled/expired
    execution_price DECIMAL(10, 2),

    -- 盈亏结果（平仓后更新）
    closed_at TIMESTAMP,
    profit_loss DECIMAL(12, 4),  -- 盈亏金额
    profit_percentage DECIMAL(8, 4),  -- 盈亏比例

    -- 元数据
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_signal_results_strategy ON signal_execution_results(strategy_id);
CREATE INDEX idx_signal_results_symbol ON signal_execution_results(symbol);
CREATE INDEX idx_signal_results_generated ON signal_execution_results(generated_at);
CREATE INDEX idx_signal_results_closed ON signal_execution_results(closed_at);
```

---

### 5.2 信号统计汇总表

**状态**: ✅ 已实现（`scripts/migrations/003_signal_statistics_hourly.sql`）

```sql
-- 位置: scripts/migrations/001_signal_tables.sql
CREATE TABLE signal_statistics_hourly (
    id SERIAL PRIMARY KEY,
    strategy_id VARCHAR(50) NOT NULL,
    symbol VARCHAR(20),
    signal_type VARCHAR(10),
    hour_timestamp TIMESTAMP NOT NULL,

    -- 统计指标
    generated_count INT DEFAULT 0,
    executed_count INT DEFAULT 0,
    cancelled_count INT DEFAULT 0,
    expired_count INT DEFAULT 0,

    -- 质量指标
    accuracy_percentage DECIMAL(5, 2),
    success_rate DECIMAL(5, 2),
    profit_ratio DECIMAL(5, 2),

    -- 性能指标
    avg_latency_ms DECIMAL(10, 3),
    p95_latency_ms DECIMAL(10, 3),
    max_latency_ms DECIMAL(10, 3),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(strategy_id, symbol, signal_type, hour_timestamp)
);

CREATE INDEX idx_stats_hourly_strategy ON signal_statistics_hourly(strategy_id);
CREATE INDEX idx_stats_hourly_timestamp ON signal_statistics_hourly(hour_timestamp);
```

---

## 6️⃣ API设计（✅ 已实现）

### 6.1 信号统计API

**状态**: ✅ 已实现（`web/backend/app/api/signal_monitoring/get_signal_statistics.py`）

```yaml
# 文件: web/backend/app/api/signal_statistics.py

GET /api/signals/statistics
  Query Parameters:
    - strategy_id: str (optional)
    - symbol: str (optional)
    - time_window: str (1h/24h/7d/30d, default: 24h)

  Response:
    {
      "data": {
        "total_generated": 1250,
        "by_type": {
          "BUY": 680,
          "SELL": 570
        },
        "accuracy_percentage": 65.5,
        "success_rate": 72.3,
        "profit_ratio": 58.2,
        "avg_latency_ms": 45.6
      }
    }

GET /api/signals/active
  Response:
    {
      "data": {
        "count": 15,
        "signals": [
          {
            "signal_id": "...",
            "strategy_id": "...",
            "symbol": "600519",
            "side": "BUY",
            "generated_at": "..."
          }
        ]
      }
    }
```

---

### 6.2 策略健康API

**状态**: ✅ 已实现（同上文件，`/strategies/{id}/health/detailed`）

```yaml
# 文件: web/backend/app/api/strategy_health.py

GET /api/strategies/{strategy_id}/health
  Response:
    {
      "data": {
        "strategy_id": "ma_crossover_001",
        "health_status": "healthy",  # healthy/degraded/unhealthy
        "checks": {
          "signal_generation": {"status": "healthy", "latency_ms": 45},
          "data_feed": {"status": "healthy", "latency_ms": 12},
          "push_notification": {"status": "healthy", "latency_ms": 120}
        },
        "last_healthy_at": "2026-01-08T10:00:00Z"
      }
    }
```

---

## 7️⃣ Grafana仪表板（✅ 已实现）

### 7.1 Dashboard配置

**状态**: ✅ 已实现

**文件**:
- `data/grafana/provisioning/dashboards/trading-signals-dashboard.json`（9 面板）
- `config/grafana-dashboards/dashboards/signal-monitoring.json`（10 面板，749 行）
- `config/grafana_trading_signals_dashboard.json`（备选版本）

### 7.2 已实现面板

| 面板 | 类型 | 文件 | 状态 |
|------|------|------|------|
| 交易信号准确度 | Gauge | trading-signals-dashboard | ✅ |
| 信号成功率 | Gauge | trading-signals-dashboard | ✅ |
| 活跃信号数量 | Table | trading-signals-dashboard | ✅ |
| 策略健康状态 | Status grid | trading-signals-dashboard | ✅ |
| 信号盈利比率 | Gauge | trading-signals-dashboard | ✅ |
| 信号生成速率 | Time series | trading-signals-dashboard + signal-monitoring | ✅ |
| 信号生成延迟分布 | Histogram | trading-signals-dashboard + signal-monitoring | ✅ |
| 信号统计概览 | Table | trading-signals-dashboard | ✅ |
| 信号准确率 | Gauge | signal-monitoring | ✅ |
| 推送通知总数 | Bar gauge | signal-monitoring | ✅ |
| 推送延迟 | Histogram | signal-monitoring | ✅ |
| 信号类型分布 | Pie | signal-monitoring | ✅ |

---

## 8️⃣ 实施路线图（更新至 v3.0）

### ✅ Phase 0: 基础设施（已完成）
- ✅ 创建 `src/monitoring/signal_metrics.py` - 9个指标定义完成
- ✅ 创建 `src/monitoring/signal_decorator.py`（295行）- 装饰器实现完成
- ✅ 集成到 `__init__.py` 导出
- ✅ 监控数据库基础设施完成
- ✅ 前端监控页面完成 (6个Vue组件)

### ✅ Phase 1: 数据层（已完成）
- ✅ `scripts/migrations/002_signal_monitoring_tables.sql`（4 张表）
- ✅ `scripts/migrations/003_signal_statistics_hourly.sql`
- ✅ `src/monitoring/signal_recorder.py`（406行）- 新增模块
- ✅ `src/monitoring/signal_result_tracker.py`（443行）- 新增模块

### ✅ Phase 2: 服务集成（已完成）
- ✅ `SignalGenerationService` 使用 `signal_metrics` + `signal_recorder`
- ✅ `@monitor_signal_push` 在 `signal_push_integration.py` 中实现（249行）
- ✅ `MonitoredNotificationManager` 包装通知管理器
- ✅ 信号结果跟踪：`signal_result_tracker.py` 追踪生命周期

### ✅ Phase 3: 统计聚合（已完成）
- ✅ `SignalMetricsAggregator` — 小时级/日级/按需聚合
- ✅ `MetricsScheduler` — 定时调度器
- ✅ `SignalStatisticsAggregator` — 额外统计聚合器
- ✅ `scripts/runtime/run_signal_aggregation.py` — 聚合启动脚本

### ✅ Phase 4: API层（已完成）
- ✅ `GET /api/signals/statistics`
- ✅ `GET /api/signals/active`
- ✅ `GET /api/strategies/{id}/health/detailed`
- ✅ `web/backend/app/api/signal_monitoring/` 完整模块（3 文件）

### ✅ Phase 5: Grafana Dashboard（已完成）
- ✅ `data/grafana/provisioning/dashboards/trading-signals-dashboard.json`（9 面板）
- ✅ `config/grafana-dashboards/dashboards/signal-monitoring.json`（10 面板）
- ✅ `config/grafana_trading_signals_dashboard.json`（备选）

### 🔄 Phase 6: 告警配置（部分完成）
- ✅ 通用告警：API响应时间/错误率/数据库/系统 → `config/alerts/mystocks-alerts.yml`
- ✅ Alertmanager路由：`config/alertmanager.yml`
- ❌ **信号专用告警规则**（4 条待补充）:
  - `SignalAccuracyLow`
  - `SignalLatencyHigh`
  - `StrategyUnhealthy`
  - `SignalPushFailureRate`

### ✅ Phase 7: 测试与验证（已完成）
- ✅ `tests/unit/test_monitoring/test_signal_monitoring.py` — 单元测试
- ✅ `tests/api/file_tests/test_signal_monitoring_api.py` — API测试
- ✅ `tests/unit/test_signal_monitoring_integration.py` — 集成测试
- ✅ `tests/e2e/monitoring-dashboard.spec.ts` — E2E测试
- ✅ `tests/monitoring/test_monitoring_alerts.py` — 告警测试

---

## 9️⃣ 监控告警规则（部分已配置）

### 9.1 告警配置

**状态**: 🔄 部分完成 — 通用告警已就绪，信号专用告警待补

**现有文件**: `config/alerts/mystocks-alerts.yml`（通用 API/数据库/系统告警）
**待创建文件**: 4 条信号专用规则（见下方）

```yaml
groups:
  - name: signal_generation
    rules:
      - alert: SignalAccuracyLow
        expr: mystocks_signal_accuracy_percentage < 50
        for: 1h
        labels:
          severity: warning
          team: trading
        annotations:
          summary: "信号准确率过低"
          description: "策略 {{ $labels.strategy_id }} 的信号准确率低于50%"

      - alert: SignalLatencyHigh
        expr: histogram_quantile(0.95, rate(mystocks_signal_latency_seconds_sum[5m])) > 0.5
        for: 10m
        labels:
          severity: warning
          team: trading
        annotations:
          summary: "信号生成延迟过高"
          description: "策略 {{ $labels.strategy_id }} P95延迟超过500ms"

      - alert: StrategyUnhealthy
        expr: mystocks_strategy_health_status == 0
        for: 5m
        labels:
          severity: critical
          team: trading
        annotations:
          summary: "策略健康状态异常"
          description: "策略 {{ $labels.strategy_id }} 状态不健康"

      - alert: SignalPushFailureRate
        expr: rate(mystocks_signal_push_total{status="failed"}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
          team: infrastructure
        annotations:
          summary: "信号推送失败率过高"
          description: "渠道 {{ $labels.channel }} 推送失败率超过10%"
```

---

## 🔟 依赖关系图（更新）

```
┌─────────────────────────────────────────────────────────────┐
│                    信号监控系统 v2.0                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ✅ 已完成模块                                                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ Prometheus   │◄───│ SignalMetrics │───►│  Monitoring  │  │
│  │ 9个指标      │    │   (231行)    │    │  Database    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│       │                    │                    ▲             │
│       ▼                    ▼                    │             │
│  ┌─────────────────────────────────────────────────┐       │
│  │         signal_decorator.py (545行)             │       │
│  │  MonitoredStrategyExecutor + 推送装饰器          │       │
│  └─────────────────────────────────────────────────┘       │
│       │                    ▲                             │
│       ▼                    │                             │
│  ┌─────────────────────────────────────────────────┐       │
│  │       前端监控页面 (6个Vue组件)                   │       │
│  └─────────────────────────────────────────────────┘       │
│                                                              │
│  ✅ 已实现模块（v3.0 新增）                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │signal_tables │    │Signal Stats  │    │   Grafana    │  │
│  │  (4张表)     │    │    API (3)   │    │  Dashboards  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│       │                    │                    │             │
│       ▼                    ▼                    ▼             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │Signal Aggr.  │    │  Signal      │    │   Service    │  │
│  │   Task       │    │  Recorder /  │    │ Integration  │  │
│  │  (已完成)    │    │  Tracker     │    │  (已完成)    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
│  ❌ 剩余待实现                                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            Alert Rules (信号专用规则, 4条)             │   │
│  │            SignalAccuracyLow / LatencyHigh /         │   │
│  │            StrategyUnhealthy / PushFailureRate       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 1️⃣1️⃣ 向后兼容性

- ✅ 现有 `SignalGenerationService` 接口保持不变（通过装饰器包装）
- ✅ 新增指标记录为异步非阻塞（使用Prometheus client）
- ✅ 数据库表为新增，不影响现有结构
- ✅ API 为新增端点，不影响现有API
- ✅ 装饰器可选项，不强制使用

---

## 1️⃣2️⃣ 风险与缓解（更新）

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 指标Label爆炸 | 标签组合过多 | 中 | 限制strategy_id为活跃策略；使用Prometheus relabeling |
| 统计计算性能 | 大数据量统计慢 | 中 | 使用预聚合表 + 小时级汇总 + 索引优化 |
| 推送延迟统计 | 高并发下性能 | 低 | 使用采样或异步聚合 |
| 数据库表锁竞争 | 高并发写入 | 低 | 使用异步写入 + 批量插入 |
| Grafana查询慢 | 复杂查询 | 低 | 使用查询缓存 + 时间范围限制 |

---

## 1️⃣3️⃣ 下一步行动（v3.0 更新）

### ✅ 已完成（全部已实现）
| 任务 | 状态 | 代码位置 |
|------|------|----------|
| 创建数据库表 | ✅ | `scripts/migrations/002_*` + `003_*` |
| 集成装饰器到服务 | ✅ | `signal_push_integration.py` + `monitored_notification_manager.py` |
| 实现信号统计API | ✅ | `web/backend/app/api/signal_monitoring/get_signal_statistics.py` |
| 实现策略健康API | ✅ | 同上，`/strategies/{id}/health/detailed` |
| 统计聚合任务 | ✅ | `signal_aggregation_task.py` (624行) |
| Grafana Dashboard | ✅ | 3 份 Dashboard 配置（19 面板） |
| 测试 | ✅ | 4 个测试文件 |
| 信号记录服务 | ✅ | `signal_recorder.py` (406行) |
| 信号结果追踪 | ✅ | `signal_result_tracker.py` (443行) |

### ❌ 剩余待办
**唯一剩余**: 配置信号专用 Prometheus 告警规则（4 条，预估 0.5 天）
- `SignalAccuracyLow`
- `SignalLatencyHigh`
- `StrategyUnhealthy`
- `SignalPushFailureRate`

---

## 📚 相关文档

- [信号监控体系梳理报告](./reports/SIGNAL_MONITORING_SYSTEM_INVENTORY_20260108.md) - 完整的架构梳理
- [监控功能分类手册](../references/function-classification-manual/04-monitoring-functions.md) - 功能清单
- [监控快速参考](./MONITORING_QUICK_REFERENCE.md) - 快速入门
- [指标管理系统设计](../03-API与功能文档/指标管理系统设计文档.md) - 指标计算系统

---

## 🎯 总结

### 当前状态（v3.0 — 2026-07-12 代码审计）
- ✅ **基础设施完成**: 9个Prometheus指标已定义并可用
- ✅ **监控代码完成**: 装饰器和指标收集器已实现
- ✅ **前端页面完成**: 6个Vue监控页面
- ✅ **监控数据库**: 基础设施已就绪
- ✅ **数据持久化**: `signal_records`、`signal_execution_results`、`signal_push_logs`、`strategy_health` + `signal_statistics_hourly`
- ✅ **API层**: `/signals/statistics`、`/signals/active`、`/strategies/{id}/health/detailed` 全部就绪
- ✅ **可视化**: 2 份 Grafana Dashboard（19 面板）已部署
- 🔄 **告警**: 通用告警就绪，信号专用告警待补充（4 条规则）

### 实施进度（85% 已完成）
| Phase | 状态 | 说明 |
|-------|------|------|
| ✅ Phase 0 — 基础设施 | 完成 | 9 指标 + 装饰器 + 前端 |
| ✅ Phase 1 — 数据层 | 完成 | 4 张表 + recorder/tracker |
| ✅ Phase 2 — 服务集成 | 完成 | push 集成 + 策略服务集成 |
| ✅ Phase 3 — 统计聚合 | 完成 | 小时级/日级聚合 + 调度 |
| ✅ Phase 4 — API 层 | 完成 | 3 个端点 |
| ✅ Phase 5 — Grafana | 完成 | 19 面板 |
| 🔄 Phase 6 — 告警规则 | 部分完成 | 通用已就绪，4 信号规则待补 |
| ✅ Phase 7 — 测试 | 完成 | 4 个测试文件 |

### 剩余工作量
- **唯一待办**: 4 条 Prometheus 信号告警规则（约 0.5 天）
- 「数据持久化」「API层」「可视化」「服务集成」等原定待办均已在 2026-01 ~ 2026-03 期间落地完成

---

**文档版本**: v3.0 (当前代码对齐)
**最后更新**: 2026-07-12（全量审计更新）
**状态**: ✅ 绝大部分已完成（约85%，仅信号告警规则待补充）
**维护者**: MyStocks开发团队
