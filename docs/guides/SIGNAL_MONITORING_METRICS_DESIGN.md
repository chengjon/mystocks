# 交易信号监控指标系统设计方案

> **版本**: v2.0 (更新)
> **日期**: 2026-01-08
> **状态**: 🔄 部分实施中
> **参考架构**: 指标计算系统V2.1, 数据源管理V2.0
> **相关文档**: [信号监控体系梳理报告](./reports/SIGNAL_MONITORING_SYSTEM_INVENTORY_20260108.md)

---

## 📝 更新日志

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

#### 待实现功能（❌TODO）
- ❌ 信号执行结果数据库表（`signal_execution_results`, `signal_statistics_hourly`）
- ❌ 信号统计API端点（`/api/signals/statistics` 等）
- ❌ Grafana信号监控Dashboard（6个规划面板）
- ❌ Prometheus告警规则配置
- ❌ 信号服务集成（集成装饰器到实际服务）

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

### 2.2 待实现功能（❌TODO）

#### 数据库表
```sql
❌ signal_execution_results -- 信号执行结果表
❌ signal_statistics_hourly -- 信号统计汇总表
```

#### API端点
```
❌ GET /api/signals/statistics -- 信号统计
❌ GET /api/signals/active -- 活跃信号
❌ GET /api/strategies/{id}/health -- 策略健康
```

#### Grafana
```
❌ grafana/dashboards/trading-signals-dashboard.json -- 信号监控Dashboard
   - 信号生成趋势面板
   - 信号准确率面板
   - 延迟分布面板
   - 活跃信号面板
   - 策略健康状态面板
   - 推送统计面板
```

#### 告警规则
```yaml
❌ alerts/signal_generation.yaml
   - SignalAccuracyLow
   - SignalLatencyHigh
   - StrategyUnhealthy
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

## 5️⃣ 数据存储设计（待实现）

### 5.1 信号执行结果表

**状态**: ❌ 待创建

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

**状态**: ❌ 待创建

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

## 6️⃣ API设计（待实现）

### 6.1 信号统计API

**状态**: ❌ 待实现

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

**状态**: ❌ 待实现

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

## 7️⃣ Grafana仪表板（待实现）

### 7.1 Dashboard配置

**状态**: ❌ 待创建

**文件**: `grafana/dashboards/trading-signals-dashboard.json`

### 7.2 面板规划

| 面板 | 类型 | 数据源 | 状态 | 说明 |
|------|------|--------|------|------|
| 信号生成趋势 | Time series | Prometheus | ❌ | 按策略/类型分组 |
| 信号准确率 | Gauge | Prometheus | ❌ | 实时准确率 |
| 延迟分布 | Histogram | Prometheus | ❌ | P50/P95/P99 |
| 活跃信号 | Table | PostgreSQL | ❌ | 当前待执行信号 |
| 策略健康状态 | Status grid | Prometheus | ❌ | 各策略健康状态 |
| 推送统计 | Bar gauge | Prometheus | ❌ | 各渠道推送情况 |

---

## 8️⃣ 实施路线图（更新）

### Phase 0: 基础设施 ✅ (已完成)
- ✅ 创建 `src/monitoring/signal_metrics.py` - 9个指标定义完成
- ✅ 创建 `src/monitoring/signal_decorator.py` - 装饰器实现完成
- ✅ 集成到 `__init__.py` 导出
- ✅ 监控数据库基础设施完成
- ✅ 前端监控页面完成 (6个Vue组件)

### Phase 1: 数据层 🔄 (进行中 - 优先级P0)
- [ ] **创建数据库迁移脚本**
  - [ ] `scripts/migrations/001_signal_tables.sql`
  - [ ] `signal_execution_results` 表
  - [ ] `signal_statistics_hourly` 表
- [ ] **执行数据库迁移**
  - [ ] 在监控数据库中创建表
  - [ ] 验证表结构
  - [ ] 测试插入和查询

**预计工作量**: 0.5天

### Phase 2: 服务集成 📋 (待开始 - 优先级P0)
- [ ] **集成信号监控装饰器**
  - [ ] 在 `SignalGenerationService` 中使用 `MonitoredStrategyExecutor`
  - [ ] 在 `SignalPushService` 中使用 `@monitor_signal_push`
  - [ ] 验证指标记录是否正确
- [ ] **实现信号结果跟踪**
  - [ ] 记录信号执行结果到 `signal_execution_results`
  - [ ] 更新信号状态（pending → executed/cancelled/expired）
  - [ ] 记录盈亏结果

**预计工作量**: 1.5天

### Phase 3: 统计聚合 📋 (待开始 - 优先级P1)
- [ ] **实现定时聚合任务**
  - [ ] 每小时统计信号生成数量
  - [ ] 计算准确率、成功率、盈利比率
  - [ ] 计算延迟统计（avg/p95/max）
  - [ ] 写入 `signal_statistics_hourly` 表
- [ ] **实现 `SignalAggregationTask`**
  - [ ] 定时任务调度
  - [ ] 批量计算逻辑
  - [ ] 异常处理和重试

**预计工作量**: 1天

### Phase 4: API层 📋 (待开始 - 优先级P0)
- [ ] **实现信号统计API**
  - [ ] `GET /api/signals/statistics`
  - [ ] `GET /api/signals/active`
  - [ ] 查询 `signal_execution_results` 和 `signal_statistics_hourly`
- [ ] **实现策略健康API**
  - [ ] `GET /api/strategies/{id}/health`
  - [ ] 综合指标计算
  - [ ] 健康状态判断逻辑

**预计工作量**: 1天

### Phase 5: Grafana Dashboard 📋 (待开始 - 优先级P1)
- [ ] **创建Dashboard配置**
  - [ ] `grafana/dashboards/trading-signals-dashboard.json`
  - [ ] 6个面板配置
- [ ] **配置数据源**
  - [ ] Prometheus数据源
  - [ ] PostgreSQL数据源（监控数据库）
- [ ] **验证可视化**
  - [ ] 检查数据连接
  - [ ] 验证面板显示
  - [ ] 调整查询和布局

**预计工作量**: 0.5天

### Phase 6: 告警配置 📋 (待开始 - 优先级P2)
- [ ] **创建Prometheus告警规则**
  - [ ] `alerts/signal_generation.yaml`
  - [ ] SignalAccuracyLow 规则
  - [ ] SignalLatencyHigh 规则
  - [ ] StrategyUnhealthy 规则
- [ ] **配置告警通知**
  - [ ] 邮件通知
  - [ ] Webhook通知
  - [ ] 测试告警触发

**预计工作量**: 0.5天

### Phase 7: 测试与验证 📋 (待开始 - 优先级P0)
- [ ] **单元测试**
  - [ ] 测试指标记录功能
  - [ ] 测试装饰器功能
  - [ ] 测试API端点
- [ ] **集成测试**
  - [ ] 端到端信号流程测试
  - [ ] 数据持久化测试
  - [ ] Grafana面板验证
- [ ] **性能测试**
  - [ ] 高并发指标记录
  - [ ] 大数据量统计计算
  - [ ] 响应时间验证

**预计工作量**: 1天

---

## 9️⃣ 监控告警规则（待配置）

### 9.1 告警配置

**状态**: ❌ 待创建

**文件**: `alerts/signal_generation.yaml`

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
│  ❌ 待实现模块                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │signal_tables │    │Signal Stats  │    │   Grafana    │  │
│  │  (2个表)     │    │    API       │    │  Dashboard   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │Signal Aggr.  │    │ Alert Rules  │    │   Service    │  │
│  │   Task       │    │  (YAML配置)   │    │ Integration  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
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

## 1️⃣3️⃣ 下一步行动（优先级排序）

### P0 - 核心功能（必须完成）
1. **创建数据库表** (0.5天)
   ```bash
   # 执行迁移脚本
   python scripts/migrations/001_signal_tables.sql
   ```

2. **集成装饰器到服务** (1天)
   - 修改 `SignalGenerationService` 使用 `MonitoredStrategyExecutor`
   - 修改 `SignalPushService` 使用 `@monitor_signal_push`

3. **实现API端点** (1天)
   - `/api/signals/statistics`
   - `/api/signals/active`
   - `/api/strategies/{id}/health`

### P1 - 增强功能（推荐完成）
4. **实现统计聚合任务** (1天)
   - 定时计算小时级统计
   - 更新 `signal_statistics_hourly` 表

5. **创建Grafana Dashboard** (0.5天)
   - 6个面板配置
   - 数据源配置

### P2 - 优化功能（可选）
6. **配置Prometheus告警规则** (0.5天)
   - 3个告警规则
   - 通知渠道配置

---

## 📚 相关文档

- [信号监控体系梳理报告](./reports/SIGNAL_MONITORING_SYSTEM_INVENTORY_20260108.md) - 完整的架构梳理
- [监控功能分类手册](./function-classification-manual/04-monitoring-functions.md) - 功能清单
- [监控快速参考](./MONITORING_QUICK_REFERENCE.md) - 快速入门
- [指标管理系统设计](../03-API与功能文档/指标管理系统设计文档.md) - 指标计算系统

---

## 🎯 总结

### 当前状态（v2.0）
- ✅ **基础设施完成**: 9个Prometheus指标已定义并可用
- ✅ **监控代码完成**: 装饰器和指标收集器已实现（776行代码）
- ✅ **前端页面完成**: 6个Vue监控页面
- ✅ **监控数据库**: 基础设施已就绪
- ❌ **数据持久化**: 待创建数据库表
- ❌ **API层**: 待实现3个统计端点
- ❌ **可视化**: 待创建Grafana Dashboard
- ❌ **告警**: 待配置Prometheus告警规则

### 实施进度
- ✅ **Phase 0 (已完成)**: 基础设施
- 🔄 **Phase 1-7 (进行中)**: 数据层 → 服务集成 → 统计聚合 → API层 → Grafana → 告警 → 测试

### 预计总工作量
- **剩余工作量**: 约5.5天
- **推荐优先级**: P0功能优先（2.5天），P1功能次之（1.5天），P2功能最后（0.5天）

---

**文档版本**: v2.0 (更新)
**最后更新**: 2026-01-08
**状态**: 🔄 部分实施中（基础设施已完成，数据层和API层待实现）
**维护者**: MyStocks开发团队
