# Phase 11B: 自选股与组合管理功能实现报告

> **版本**: v1.0
> **日期**: 2026-01-08
> **状态**: 已完成

## 1. 概述

本阶段实现了自选股监控和组合管理两大功能模块，采用DDD架构模式，与现有系统（数据源管理V2、指标计算V2.1）保持一致的工程实践。

### 1.1 核心目标

| 模块 | 核心功能 |
|------|---------|
| 自选股管理 | 分组管理、股票添加、技术指标快照、波动率监控 |
| 组合管理 | 持仓管理、绩效分析、风控监控、配置分析 |
| 预测功能 | 价格走势预测、波动率预测、指标预测 |

### 1.2 技术复用

- **数据源**: 复用 `DataSourceManagerV2` 获取行情数据
- **指标计算**: 复用 `IndicatorFactory` 计算技术指标
- **GPU加速**: 复用 `GPUIndicatorCalculator` 支持GPU计算
- **DDD模式**: 与现有策略/交易/投资组合上下文保持一致

---

## 2. 架构设计

### 2.1 目录结构

```
src/
├── domain/
│   ├── watchlist/                    # 自选股领域层
│   │   ├── model/
│   │   │   ├── watchlist.py          # Watchlist聚合根
│   │   │   └── watchlist_stock.py    # WatchlistStock实体
│   │   ├── value_objects/            # 值对象
│   │   ├── repository/               # 仓储接口
│   │   └── service/
│   │       ├── watchlist_service.py  # 领域服务
│   │       └── snapshot_service.py   # 快照服务
│   └── prediction/                   # 预测服务
│       └── prediction_service.py
│
├── application/
│   ├── watchlist/
│   │   └── watchlist_app_service.py  # 自选股应用服务
│   └── portfolio/
│       ├── model/                    # 组合模型
│       ├── repository/               # 仓储接口
│       └── portfolio_app_service.py  # 组合应用服务
│
└── infrastructure/
    └── persistence/
        ├── watchlist_repository_impl.py
        └── portfolio_repository_impl.py
```

### 2.2 核心聚合根

#### Watchlist (自选股)
```python
@class Watchlist:
    id: str                           # 唯一标识
    name: str                         # 名称
    watchlist_type: WatchlistType     # 类型 (technical/fundamental/event/holding/temporary)
    stocks: Dict[str, WatchlistStock] # 股票列表
    config: WatchlistConfig           # 配置
    alert_conditions: List[AlertCondition] # 预警条件
```

#### Portfolio (组合)
```python
@class Portfolio:
    id: str                           # 唯一标识
    name: str                         # 名称
    portfolio_type: str               # 类型 (real/simulation/research)
    holdings: Dict[str, Holding]      # 持仓
    transactions: List[Transaction]   # 交易记录
    current_value: float              # 当前价值
    cash: float                       # 现金
```

---

## 3. 核心功能实现

### 3.1 自选股管理

#### 3.1.1 分组管理

| 类型 | 说明 |
|------|------|
| TECHNICAL | 技术关注 |
| FUNDAMENTAL | 基本面关注 |
| EVENT_DRIVEN | 事件驱动 |
| HOLDING | 持仓股 |
| TEMPORARY | 临时观察 |

#### 3.1.2 技术指标快照

```python
@class SnapshotService:
    def capture_entry_snapshot(stock_code, indicator_ids, reference_days):
        """捕获入选时的历史快照"""

    def capture_realtime_snapshot(stock_code, indicator_ids):
        """捕获实时快照"""

    def capture_historical_snapshot(stock_code, target_date, indicator_ids):
        """捕获历史时点快照"""
```

支持的指标:
- SMA (简单移动平均线)
- RSI (相对强弱指标)
- MACD (指数平滑移动平均线)
- ATR (真实波幅均值)

#### 3.1.3 波动率监控

```python
@class WatchlistStock:
    def get_volatility_metrics(period_days=10):
        """计算波动率指标"""
        # 返回: historical_volatility, intraday_volatility, max/min, atr
```

### 3.2 组合管理

#### 3.2.1 持仓管理

| 操作 | 说明 |
|------|------|
| add_holding() | 添加持仓 |
| update_holding() | 调整持仓 |
| remove_holding() | 清仓 |

#### 3.2.2 绩效分析

```python
@class Portfolio:
    def get_performance_metrics():
        """计算绩效指标"""
        # 返回: total_return, holdings_value, cash_balance, win_rate, trade_count

    def get_sector_allocation():
        """行业配置分析"""

    def get_position_concentration():
        """持仓集中度分析"""
```

### 3.3 预测功能

```python
@class PredictionService:
    def predict_price_direction(stock_code, lookback_days, prediction_days):
        """预测价格走势方向"""

    def predict_price_target(stock_code, lookback_days):
        """预测目标价格"""

    def predict_volatility(stock_code, period_days):
        """预测波动率"""

    def predict_indicator(stock_code, indicator_id, lookback_days):
        """预测指标值"""
```

---

## 4. 数据持久化

### 4.1 数据库表

```sql
-- 自选股表
CREATE TABLE ddd_watchlists (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    watchlist_type VARCHAR(32) NOT NULL,
    description TEXT,
    config_json TEXT,
    color_tag VARCHAR(16),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 自选股内股票表
CREATE TABLE ddd_watchlist_stocks (
    id VARCHAR(64) PRIMARY KEY,
    watchlist_id VARCHAR(64),
    stock_code VARCHAR(16) NOT NULL,
    stock_name VARCHAR(64),
    notes TEXT,
    tags TEXT,
    entry_snapshot TEXT,
    observation_snapshots TEXT,
    is_active BOOLEAN,
    added_at TIMESTAMP,
    last_updated TIMESTAMP
);

-- 组合表
CREATE TABLE ddd_portfolios_v2 (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    portfolio_type VARCHAR(32) NOT NULL,
    initial_capital FLOAT,
    current_value FLOAT,
    cash FLOAT,
    holdings_json TEXT,
    ...
);
```

---

## 5. 使用示例

### 5.1 自选股管理

```python
from src.application.watchlist import WatchlistApplicationService
from src.domain.watchlist.value_objects import WatchlistType

# 创建服务
watchlist_service = create_watchlist_service(watchlist_repo, stock_repo)

# 创建自选股
wl = watchlist_service.create_watchlist(
    name="技术关注组合",
    watchlist_type="technical",
    description="用于技术分析"
)

# 添加股票（自动捕获快照）
watchlist_service.add_stock(
    watchlist_id=wl['id'],
    stock_code="600519",
    stock_name="贵州茅台",
    capture_indicators=["sma.5", "sma.20", "rsi.14"],
    reference_days=20
)

# 获取摘要
summary = watchlist_service.get_watchlist_summary(wl['id'])
```

### 5.2 组合管理

```python
from src.application.portfolio import PortfolioApplicationService

# 创建服务
portfolio_service = create_portfolio_service(portfolio_repo)

# 创建组合
portfolio = portfolio_service.create_portfolio(
    name="科技成长组合",
    portfolio_type="simulation",
    initial_capital=1000000
)

# 添加持仓
portfolio_service.add_position(
    portfolio_id=portfolio['id'],
    symbol="300750",
    quantity=200,
    price=180.0
)

# 获取绩效
perf = portfolio_service.get_performance(portfolio['id'])
```

### 5.3 预测功能

```python
from src.domain.prediction import PredictionService

# 创建预测服务
prediction_service = create_prediction_service(data_source_manager)

# 价格走势预测
result = prediction_service.predict_price_direction("600519", lookback_days=30)

# 波动率预测
result = prediction_service.predict_volatility("600519", period_days=10)
```

---

## 6. 文件清单

| 文件 | 变更 | 描述 |
|------|------|------|
| `src/domain/watchlist/model/watchlist.py` | 新增 | 自选股聚合根 |
| `src/domain/watchlist/model/watchlist_stock.py` | 新增 | 股票实体 |
| `src/domain/watchlist/value_objects/__init__.py` | 新增 | 值对象定义 |
| `src/domain/watchlist/repository/__init__.py` | 新增 | 仓储接口 |
| `src/domain/watchlist/service/watchlist_service.py` | 新增 | 领域服务 |
| `src/domain/watchlist/service/snapshot_service.py` | 新增 | 快照服务 |
| `src/domain/prediction/prediction_service.py` | 新增 | 预测服务 |
| `src/application/portfolio/model/__init__.py` | 新增 | 组合模型 |
| `src/application/portfolio/repository/__init__.py` | 新增 | 组合仓储接口 |
| `src/application/portfolio/portfolio_app_service.py` | 新增 | 组合应用服务 |
| `src/application/watchlist/watchlist_app_service.py` | 新增 | 自选股应用服务 |
| `src/infrastructure/persistence/watchlist_repository_impl.py` | 新增 | 自选股仓储实现 |
| `src/infrastructure/persistence/portfolio_repository_impl.py` | 新增 | 组合仓储实现 |
| `scripts/watchlist_portfolio_demo.py` | 新增 | 演示脚本 |

---

## 7. 下一步计划

### 7.1 前端集成
- 创建Vue.js组件
- 实现实时数据更新
- 添加图表可视化

### 7.2 Web API
- 实现RESTful API
- 添加WebSocket支持
- 集成认证授权

### 7.3 高级功能
- 相关性分析热力图
- 组合对比分析
- 风控预警通知

---

## 8. 验证结果

```bash
# 运行演示
python scripts/watchlist_portfolio_demo.py

# 输出
✅ 自选股演示完成
✅ 组合管理演示完成
✅ 预测功能演示完成
```

---

**报告生成时间**: 2026-01-08
**报告版本**: v1.0
