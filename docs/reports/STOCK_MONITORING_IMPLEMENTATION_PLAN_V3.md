# 智能量化监控与决策系统 - 实施架构设计方案 v3.0

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


**文档类型**: 实施架构设计
**创建日期**: 2026-01-07
**版本**: v3.0 (集成落地版)
**状态**: 待实施
**基于**:
- `STOCK_MONITORING_PORTFOLIO_OPTIMIZED_PROPOSAL.md` (v2.0)
- 现有代码: `src/monitoring/async_monitoring.py`
- 现有代码: `src/monitoring/gpu_integration_manager.py`

---

## 📊 1. 执行摘要 (Executive Summary)

### 核心差异 (v3.0 vs v2.0)
本方案（v3.0）不再是一个通用的设计提案，而是**完全贴合 MyStocks 现有架构**的落地实施方案。核心在于从"重复造轮子"转向"资产复用"。

| 维度 | v2.0 提案方案 | **v3.0 实施方案 (本项目)** | 优势 |
| :--- | :--- | :--- | :--- |
| **异步机制** | 自建 asyncpg 写入循环 | **复用 `MonitoringEventPublisher`** | 利用现有的 Redis 缓冲、重试和降级机制，系统更健壮 |
| **计算引擎** | 单纯 Pandas 向量化 | **Pandas + GPU 双引擎** | 深度集成 `src/gpu` 模块，大规模回测/扫描性能提升 50x+ |
| **数据流向** | API 直接写库 | **读写分离 (CQRS模式)** | API 负责快速读取，Worker 负责批量写入，彻底解决高并发阻塞 |
| **风险控制** | 静态止损 | **入库上下文风控** | 引入 `entry_reason` 和 `stop_loss`，实现策略级风控 |

---

## 🏗️ 2. 系统架构设计

### 2.1 总体架构图

```mermaid
graph TD
    User[用户/前端] --> API[FastAPI Layer]

    subgraph "应用层 (Application)"
        API --> WatchlistSvc[清单管理服务]
        API --> AnalysisSvc[智能分析服务]
    end

    subgraph "领域层 (Domain) - 核心引擎"
        AnalysisSvc --> RegimeIdent[市场体制识别]
        AnalysisSvc --> CalcFactory[计算引擎工厂]

        CalcFactory -->|CPU模式| VectorCalc[Pandas向量化引擎]
        CalcFactory -->|GPU模式| GPUCalc[GPU加速引擎]

        GPUCalc -.->|调用| ExistingGPU[src.gpu.accelerated]
    end

    subgraph "基础设施层 (Infrastructure)"
        WatchlistSvc --> AsyncPG[PostgreSQL (asyncpg)]
        VectorCalc --> TDEngine[TDengine (原生异步)]
    end

    subgraph "异步事件总线 (Existing)"
        AnalysisSvc -.->|发布事件| EventPub[MonitoringEventPublisher]
        EventPub -->|Redis Channel| Redis[(Redis MQ)]
        Redis -->|订阅| EventWorker[MonitoringEventWorker]
        EventWorker -->|批量写入| DB_Write[指标数据落库]
    end
```

### 2.2 核心流程：异步指标计算与写入

利用 `src/monitoring/async_monitoring.py` 实现读写分离：

1.  **用户请求**: `POST /api/v1/monitoring/analysis/calculate`
2.  **实时计算**: `AnalysisSvc` 调用计算引擎（CPU/GPU）快速得出结果。
3.  **快速响应**: API 直接返回计算结果给前端展示（不等待写库）。
4.  **异步落库**:
    *   `AnalysisSvc` 构建 `MonitoringEvent` (type=`metric_update`)。
    *   调用 `MonitoringEventPublisher.publish_event(event)` 推送至 Redis。
    *   后台 `MonitoringEventWorker` 消费消息，批量写入 `monitoring_stock_metrics` 表。

---

## 🧠 3. 核心功能实现策略

### 3.1 双模计算引擎 (Dual-Mode Engine)

复用 `src/monitoring/gpu_performance_optimizer.py` 实现自动硬件加速切换。

**实现逻辑 (伪代码)**:

```python
# src/monitoring/domain/calculator_factory.py
from src.monitoring.gpu_performance_optimizer import get_gpu_performance_optimizer

class HealthCalculatorFactory:
    @staticmethod
    async def get_calculator():
        # 检查现有 GPU 模块状态
        gpu_optimizer = await get_gpu_performance_optimizer()
        health_status = await gpu_optimizer.get_gpu_health_status()

        # 判定是否启用 GPU 模式 (健康且显存充足)
        if health_status['available'] and health_status['healthy']:
            return GPUHealthCalculator()  # 使用 CuPy / RAPIDS
        else:
            return VectorizedHealthCalculator()  # 使用 Pandas / Numpy
```

### 3.2 复用异步事件总线

无需编写新的 Worker，只需扩展现有 `MonitoringEventWorker` 的处理逻辑。

**扩展逻辑**:

```python
# 修改 src/monitoring/async_monitoring.py

def _flush_events(self):
    # ... 现有代码 ...

    for event in events:
        if event.event_type == "metric_update":
            # 新增处理逻辑：批量写入指标
            monitoring_db.batch_save_metrics(event.data)
        elif event.event_type == "portfolio_snapshot":
            # 新增处理逻辑：保存组合快照
            monitoring_db.save_portfolio_snapshot(event.data)

    # ... 现有代码 ...
```

---

## 🗄️ 4. 数据库设计 (Schema v3.0)

### 4.1 监控清单 (Portfolio Context)

PostgreSQL 表结构设计，重点增强了"入库上下文"字段，以支持更高级的策略归因。

```sql
-- 1. 监控清单主表
CREATE TABLE monitoring_watchlists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) DEFAULT 'manual', -- manual(手动), strategy(策略自动), benchmark(基准)
    risk_profile JSONB, -- 存储风控配置 {risk_tolerance: 'high', max_drawdown_limit: 0.2}
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 清单成员表 (增强版)
CREATE TABLE monitoring_watchlist_stocks (
    id SERIAL PRIMARY KEY,
    watchlist_id INTEGER REFERENCES monitoring_watchlists(id) ON DELETE CASCADE,
    stock_code VARCHAR(20) NOT NULL,

    -- 入库上下文 (关键新增)
    entry_price DECIMAL(10,2),           -- 入库价格
    entry_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 入库时间
    entry_reason VARCHAR(50),            -- 入库理由: 'macd_gold_cross', 'manual_pick'
    entry_strategy_id VARCHAR(50),       -- 关联的策略ID (如果有)

    -- 风控设置
    stop_loss_price DECIMAL(10,2),       -- 止损价格
    target_price DECIMAL(10,2),          -- 止盈价格

    weight DECIMAL(5,4) DEFAULT 0.0,     -- 目标权重
    is_active BOOLEAN DEFAULT TRUE,

    UNIQUE(watchlist_id, stock_code)
);
```

### 4.2 分析结果 (Analysis Results)

```sql
-- 3. 每日健康度评分
CREATE TABLE monitoring_health_scores (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    score_date DATE NOT NULL,

    -- 综合评分
    total_score DECIMAL(5,2),

    -- 五维雷达分 (JSONB存储，便于扩展)
    -- {trend: 80, technical: 70, funding: 60, emotion: 50, risk: 90}
    radar_scores JSONB,

    -- 市场环境快照
    market_regime VARCHAR(20), -- 'bull', 'bear', 'shock'

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, score_date)
);
```

---

## 📅 5. 实施路线图 (Roadmap)

### Phase 1: 基础设施连接 (Infrastructure) - 1周
*   [ ] **数据库迁移**: 创建上述 v3.0 SQL 表结构。
*   [ ] **事件适配**: 修改 `src/monitoring/async_monitoring.py`，注册新的事件类型 `metric_update`。
*   [ ] **数据层封装**: 基于 `asyncpg` 实现 `PostgreSQLAsyncAccess` 类。

### Phase 2: 核心计算引擎 (Core Engine) - 2周
*   [ ] **市场体制识别**: 实现 `MarketRegimeIdentifier` (牛熊市判断)。
*   [ ] **CPU 计算器**: 实现 `VectorizedHealthCalculator`。
*   [ ] **GPU 桥接**: 实现 `GPUHealthCalculator` 并集成 `CalculatorFactory`。

### Phase 3: 业务 API 开发 (Business API) - 2周
*   [ ] **清单管理**: 实现 `/watchlists` CRUD 接口，支持 `entry_reason` 等新字段。
*   [ ] **实时分析**: 实现 `/analysis` 接口，连接计算引擎与事件总线。
*   [ ] **数据迁移**: 编写脚本 `scripts/migrate_v1_watchlists.py`。

### Phase 4: 前端可视化 (Frontend) - 2周
*   [ ] **雷达图组件**: 开发五维健康度雷达图。
*   [ ] **风控看板**: 展示触发止损预警的股票。

---

## ✅ 总结

v3.0 方案通过**复用现有异步事件总线**和**集成 GPU 优化模块**，将原计划的开发工作量降低了约 30%，同时显著提升了系统的吞吐量和计算性能。这是一个高性价比、可落地的实施路径。
