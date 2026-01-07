# 股票监控与投资组合管理系统 - 功能规划方案

**文档类型**: 功能规划提案
**创建日期**: 2025-01-07
**版本**: v1.0
**状态**: 待评审

---

## 📊 执行摘要

### 项目背景

本功能旨在为 MyStocks 系统增加**股票监控与投资组合管理能力**，让用户能够：
- 创建多个监控清单（投资组合）
- 自动跟踪股票表现和技术指标
- 智能评估股票健康度和风险
- 优化投资组合权重配置
- 对比不同清单的表现

### 核心价值

1. **数据驱动决策**: 基于量化指标的客观评估
2. **智能权重优化**: 现代投资组合理论指导配置
3. **风险可视化**: 健康度评分和风险等级一目了然
4. **清单对比分析**: 多维度对比不同投资组合

### 技术优势

- ✅ **复用现有架构**: 无需大规模重构
- ✅ **双数据库支持**: 充分利用TDengine和PostgreSQL优势
- ✅ **模块化设计**: 低耦合，易扩展
- ✅ **性能优化**: 异步处理、批量操作、Redis缓存

---

## 🎯 功能概述

### 核心功能模块

#### 1. 监控清单管理
- ✅ 创建、编辑、删除监控清单
- ✅ 支持多个独立清单（投资组合）
- ✅ 清单导入/导出功能
- ✅ 清单权限管理（按用户隔离）

#### 2. 股票入库和跟踪
- ✅ 添加单只股票或批量导入
- ✅ 精确记录入库时间
- ✅ 自动跟踪分时数据
- ✅ 自动跟踪K线数据（日K、周K、月K）
- ✅ 资金流向和成交量数据

#### 3. 智能分析引擎
- ✅ **技术指标自动计算**:
  - 趋势指标: MA5/10/20/60、MACD
  - 动量指标: RSI、KDJ
  - 成交量指标: 量比、换手率
  - 波动率指标: 20日波动率、ATR

- ✅ **健康度评估**:
  - 多因子综合评分 (0-100分)
  - 5个健康等级: excellent/good/average/weak/poor
  - 4个风险等级: low/medium/high/critical

- ✅ **评分维度**:
  - 趋势强度 (30%)
  - 技术面 (30%)
  - 成交量活跃度 (20%)
  - 波动率 (20%)

#### 4. 投资组合管理
- ✅ **人工权重分配**:
  - 拖拽滑块调整权重
  - 手动输入精确权重
  - 自动归一化到100%

- ✅ **智能权重优化**:
  - 等权重配置
  - 最小方差组合 (Markowitz)
  - 最大健康度加权
  - 风险平价 (Risk Parity)

- ✅ **组合分析**:
  - 组合总市值
  - 累计收益率
  - 组合波动率和方差
  - 夏普比率
  - 最大回撤

#### 5. 清单对比分析
- ✅ 多清单指标对比
- ✅ 雷达图对比
- ✅ 收益曲线对比
- ✅ 排行榜（最佳收益、最低风险等）

---

## 🏗️ 系统架构设计

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    前端展示层 (Vue 3 + Element Plus)              │
├─────────────────────────────────────────────────────────────────┤
│  监控清单管理  │  数据可视化  │  健康度仪表盘  │  投资组合分析   │
└────────────────────┬────────────────────────────────────────────┘
                     │ REST API
┌────────────────────▼────────────────────────────────────────────┐
│                   FastAPI 后端服务层                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  监控清单API  │  │  数据分析API  │  │  组合管理API  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼────────────────┘
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼────────────────┐
│                   业务逻辑层 (新增)                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 清单管理器    │  │ 健康度评估器  │  │ 权重优化器    │          │
│  │ WatchlistMgr │  │HealthAnalyzer│  │WeightOptimizer│         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼────────────────┘
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼────────────────┐
│                   数据访问层 (现有架构)                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐          ┌──────────────────┐            │
│  │ PostgreSQLAccess │          │ TDengineAccess   │            │
│  │  监控清单配置数据  │          │  高频时序市场数据  │            │
│  └──────────────────┘          └──────────────────┘            │
└─────────┬──────────────────────────────┬────────────────────────┘
          │                              │
┌─────────▼──────────────────────────────▼────────────────────────┐
│                   数据源层 (现有适配器)                          │
├─────────────────────────────────────────────────────────────────┤
│  akshare │ tushare │ tdx │ baostock │ efinance │ ...            │
└─────────────────────────────────────────────────────────────────┘
```

### 核心模块设计

#### 模块1: WatchlistManager (清单管理器)
**文件**: `src/monitoring/watchlist_manager.py`

**职责**:
- 清单CRUD操作
- 股票添加/移除
- 权重管理

**关键方法**:
```python
class WatchlistManager:
    async def create_watchlist(name, description, user_id, risk_tolerance)
    async def add_stock_to_watchlist(watchlist_id, stock_code, weight)
    async def remove_stock_from_watchlist(watchlist_id, stock_code)
    async def update_stock_weights(watchlist_id, weight_dict)
    async def get_watchlist_stocks(watchlist_id)
```

#### 模块2: HealthAnalyzer (健康度评估器)
**文件**: `src/monitoring/health_analyzer.py`

**职责**:
- 技术指标计算
- 健康度评分
- 风险等级评估

**关键方法**:
```python
class HealthAnalyzer:
    async def calculate_health_score(stock_code, date)
    async def batch_calculate_health_scores(stock_list)
    def _calculate_trend_score(kline_data)
    def _calculate_technical_score(kline_data)
    def _calculate_volume_score(kline_data)
    def _calculate_volatility_score(kline_data)
```

#### 模块3: PortfolioOptimizer (权重优化器)
**文件**: `src/monitoring/portfolio_optimizer.py`

**职责**:
- 智能权重优化
- 组合收益计算
- 风险指标计算

**关键方法**:
```python
class PortfolioOptimizer:
    async def optimize_weights(watchlist_id, strategy)
    def _equal_weight_strategy(stocks)
    def _min_variance_optimization(returns_data)
    def _max_health_weighting(stocks)
    def _risk_parity_optimization(returns_data)
```

---

## 🗄️ 数据库设计

### PostgreSQL 表结构

#### 表1: monitoring_watchlists (监控清单主表)
```sql
CREATE TABLE monitoring_watchlists (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    risk_tolerance VARCHAR(20) DEFAULT 'moderate',
    rebalance_frequency VARCHAR(20) DEFAULT 'monthly',
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);
```

#### 表2: monitoring_watchlist_stocks (清单股票关联表)
```sql
CREATE TABLE monitoring_watchlist_stocks (
    id SERIAL PRIMARY KEY,
    watchlist_id INTEGER REFERENCES monitoring_watchlists(id) ON DELETE CASCADE,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    weight DECIMAL(5,4) DEFAULT 0.0000,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE KEY unique_watchlist_stock (watchlist_id, stock_code),
    INDEX idx_watchlist_id (watchlist_id),
    INDEX idx_stock_code (stock_code)
);
```

#### 表3: monitoring_stock_metrics (股票指标快照表)
```sql
CREATE TABLE monitoring_stock_metrics (
    id SERIAL PRIMARY KEY,
    watchlist_id INTEGER REFERENCES monitoring_watchlists(id) ON DELETE CASCADE,
    stock_code VARCHAR(20) NOT NULL,
    snapshot_date DATE NOT NULL,
    snapshot_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    current_price DECIMAL(10,2),
    daily_change_pct DECIMAL(8,4),
    ma5 DECIMAL(10,2),
    ma10 DECIMAL(10,2),
    ma20 DECIMAL(10,2),
    ma60 DECIMAL(10,2),
    rsi_6 DECIMAL(5,2),
    rsi_12 DECIMAL(5,2),
    rsi_24 DECIMAL(5,2),
    macd_dif DECIMAL(10,4),
    macd_dea DECIMAL(10,4),
    macd_bar DECIMAL(10,4),
    volume_ratio DECIMAL(8,2),
    turnover_rate DECIMAL(8,4),
    volatility_20d DECIMAL(8,4),
    max_drawdown DECIMAL(8,4),
    INDEX idx_watchlist_stock_date (watchlist_id, stock_code, snapshot_date),
    INDEX idx_snapshot_date (snapshot_date)
);
```

#### 表4: monitoring_health_scores (健康度评分历史表)
```sql
CREATE TABLE monitoring_health_scores (
    id SERIAL PRIMARY KEY,
    watchlist_id INTEGER REFERENCES monitoring_watchlists(id) ON DELETE CASCADE,
    stock_code VARCHAR(20) NOT NULL,
    score_date DATE NOT NULL,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    overall_score DECIMAL(5,2),
    trend_score DECIMAL(5,2),
    technical_score DECIMAL(5,2),
    volume_score DECIMAL(5,2),
    volatility_score DECIMAL(5,2),
    health_level VARCHAR(10),
    risk_level VARCHAR(10),
    INDEX idx_watchlist_stock_date (watchlist_id, stock_code, score_date),
    INDEX idx_score_date (score_date)
);
```

#### 表5: monitoring_portfolio_snapshots (投资组合快照表)
```sql
CREATE TABLE monitoring_portfolio_snapshots (
    id SERIAL PRIMARY KEY,
    watchlist_id INTEGER REFERENCES monitoring_watchlists(id) ON DELETE CASCADE,
    snapshot_date DATE NOT NULL,
    snapshot_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_value DECIMAL(15,2),
    daily_return DECIMAL(8,4),
    cumulative_return DECIMAL(8,4),
    portfolio_volatility DECIMAL(8,4),
    portfolio_variance DECIMAL(8,4),
    max_drawdown DECIMAL(8,4),
    sharpe_ratio DECIMAL(6,3),
    weight_strategy VARCHAR(20),
    rebalance_count INTEGER DEFAULT 0,
    INDEX idx_watchlist_date (watchlist_id, snapshot_date),
    INDEX idx_snapshot_date (snapshot_date)
);
```

### TDengine 超表
复用现有超表:
- `tick_data` - 分时数据
- `minute_data` - 分钟K线数据

---

## 🔌 API接口设计

### API 模块划分
```
/api/v1/monitoring/
├── watchlists/          # 监控清单管理
├── stocks/              # 股票数据查询
├── health/              # 健康度评分
└── portfolio/           # 投资组合分析
```

### 核心API端点

#### 1. 监控清单管理

##### 创建监控清单
```http
POST /api/v1/monitoring/watchlists
Content-Type: application/json

{
  "name": "核心科技股组合",
  "description": "重点关注科技龙头",
  "risk_tolerance": "moderate",
  "rebalance_frequency": "monthly"
}

Response 201:
{
  "success": true,
  "data": {
    "id": 1,
    "name": "核心科技股组合",
    "user_id": 2,
    "created_at": "2025-01-07T10:00:00"
  }
}
```

##### 添加股票到清单
```http
POST /api/v1/monitoring/watchlists/{watchlist_id}/stocks

{
  "stocks": [
    {
      "stock_code": "600519.SH",
      "weight": 0.2000,
      "notes": "贵州茅台"
    }
  ]
}

Response 200:
{
  "success": true,
  "message": "成功添加1只股票"
}
```

#### 2. 健康度评分

##### 计算清单所有股票健康度
```http
POST /api/v1/monitoring/watchlists/{watchlist_id}/health/calculate

Response 200:
{
  "success": true,
  "data": [
    {
      "stock_code": "600519.SH",
      "overall_score": 85.5,
      "health_level": "good",
      "risk_level": "medium",
      "trend_score": 90.0,
      "technical_score": 82.0,
      "volume_score": 78.0,
      "volatility_score": 88.0
    }
  ]
}
```

#### 3. 投资组合分析

##### 智能权重优化
```http
POST /api/v1/monitoring/watchlists/{watchlist_id}/portfolio/optimize

{
  "strategy": "min_variance",
  "risk_tolerance": "moderate"
}

Response 200:
{
  "success": true,
  "data": {
    "optimized_weights": {
      "600519.SH": 0.2500,
      "000858.SZ": 0.2000
    },
    "expected_return": 0.15,
    "expected_risk": 0.12,
    "sharpe_ratio": 1.95
  }
}
```

完整API文档见: **附录A: API接口完整列表**

---

## 🎨 前端界面设计

### 页面结构

#### 页面1: 监控清单管理页
**路径**: `/monitoring/watchlists`

**功能区域**:
1. 顶部操作栏（创建清单、搜索、筛选）
2. 清单卡片网格（显示清单概览）
3. 新建清单对话框

#### 页面2: 清单详情页
**路径**: `/monitoring/watchlists/:id`

**布局**: 三栏式
- 左侧: 股票列表（权重、健康度）
- 中间: 股票详情（K线图、技术指标）
- 右侧: 健康度仪表盘

#### 页面3: 投资组合分析页
**路径**: `/monitoring/watchlists/:id/portfolio`

**功能区域**:
1. 顶部关键指标卡片
2. 组合收益曲线图
3. 权重分布饼图
4. 股票贡献度分析

#### 页面4: 清单对比分析页
**路径**: `/monitoring/compare`

**功能区域**:
1. 清单选择器
2. 指标对比表
3. 雷达图对比
4. 收益曲线对比

### 核心组件

#### StockHealthBadge 组件
显示健康度徽章，自动选择颜色

#### WeightSlider 组件
拖拽滑块调整权重，自动归一化

#### HealthTrendChart 组件
ECharts折线图，展示健康度历史

完整组件设计见: **附录B: 前端组件详细设计**

---

## ⚙️ 技术实现关键点

### 1. 健康度评分算法

#### 多因子评分模型

```python
overall_score = (
    trend_score * 0.30 +
    technical_score * 0.30 +
    volume_score * 0.20 +
    volatility_score * 0.20
)
```

#### 评分等级定义

| 健康度等级 | 分数范围 | 颜色标识 |
|-----------|---------|---------|
| excellent | 90-100  | 🟢 绿色  |
| good      | 75-89   | 🟡 黄色  |
| average   | 60-74   | 🟠 橙色  |
| weak      | 45-59   | 🔴 红色  |
| poor      | 0-44    | ⚫ 黑色  |

### 2. 智能权重优化算法

#### 支持的优化策略

| 策略名称 | 描述 | 适用场景 |
|---------|------|---------|
| equal_weight | 等权重配置 | 新手投资者 |
| min_variance | 最小方差组合 | 风险厌恶型 |
| max_health | 最大健康度加权 | 追求质量 |
| risk_parity | 风险平价 | 平衡配置 |

#### 优化算法示例（最小方差）

使用Markowitz均值-方差模型，通过scipy.optimize求解：
```python
def portfolio_variance(weights, cov_matrix):
    return np.dot(weights.T, np.dot(cov_matrix, weights))

result = minimize(
    portfolio_variance,
    initial_weights,
    args=(cov_matrix,),
    method='SLSQP',
    bounds=bounds,
    constraints=constraints
)
```

### 3. 定时任务调度

#### Cron Jobs配置

| 任务 | 执行时间 | 功能 |
|-----|---------|------|
| daily_stock_metrics_snapshot | 每天16:00 | 股票指标快照 |
| daily_health_score_calculation | 每天17:00 | 健康度评分计算 |
| daily_portfolio_snapshot | 每天18:00 | 组合快照 |
| weekly_rebalance_reminder | 每周一9:00 | 再平衡提醒 |

### 4. 性能优化策略

#### 批量处理
```python
# 批量插入指标数据
async def batch_insert_metrics(metrics_data: list[dict]):
    async with PostgreSQLPool.acquire() as conn:
        await conn.executemary(sql, metrics_data)
```

#### Redis缓存
```python
# 缓存健康度评分（1小时）
@cache(ttl=3600)
async def get_health_score(stock_code: str, date: str):
    return await calculate_health_score(stock_code, date)
```

#### 虚拟滚动（前端）
```vue
<RecycleScroller
  :items="stocks"
  :item-size="80"
  key-field="id"
/>
```

---

## ⚠️ 风险评估和应对措施

### 技术风险

| 风险 | 影响 | 概率 | 应对措施 |
|-----|------|------|---------|
| 大量数据更新导致性能下降 | 高 | 中 | 批量处理、异步队列、Redis缓存 |
| 权重优化算法不准确 | 中 | 中 | 回测验证、添加约束条件 |
| PostgreSQL和TDengine数据不一致 | 高 | 低 | 事务管理、数据校验、错误重试 |
| 前端渲染大量数据导致卡顿 | 中 | 中 | 虚拟滚动、分页加载、Web Worker |

### 业务风险

| 风险 | 影响 | 概率 | 应对措施 |
|-----|------|------|---------|
| 用户不理解健康度评分逻辑 | 中 | 高 | 提供详细说明文档、交互式解释 |
| 投资组合优化结果与预期不符 | 高 | 中 | 风险提示、回测验证、敏感性分析 |
| 数据源故障导致无法更新 | 高 | 低 | 多数据源备份、降级方案 |

---

## 📅 开发计划

### 阶段1: 基础设施 (2周)
- ✅ 数据库表创建和迁移
- ✅ 核心业务逻辑层开发
- ✅ 基础API端点实现

### 阶段2: 核心功能 (3周)
- ✅ 监控清单管理
- ✅ 股票数据跟踪
- ✅ 技术指标计算
- ✅ 健康度评分算法

### 阶段3: 高级功能 (2周)
- ✅ 智能权重优化
- ✅ 投资组合分析
- ✅ 清单对比分析

### 阶段4: 前端开发 (3周)
- ✅ 页面和组件开发
- ✅ 数据可视化
- ✅ 用户交互优化

### 阶段5: 测试和优化 (2周)
- ✅ 单元测试
- ✅ 集成测试
- ✅ 性能优化
- ✅ 用户验收测试

**总计**: 约12周（3个月）

---

## 📚 附录

### 附录A: API接口完整列表
(详见下一节)

### 附录B: 前端组件详细设计
(详见下一节)

### 附录C: 数据库ER图
(详见下一节)

---

## ✅ 总结

本功能规划方案提供了一个完整的股票监控与投资组合管理系统设计，包括：

1. **完善的功能设计**: 从清单管理到智能权重优化的完整链路
2. **清晰的技术架构**: 基于现有架构，最小化改动
3. **详细的数据库设计**: 5张核心表，支持所有功能需求
4. **完整的API规范**: RESTful设计，易于扩展
5. **用户友好的界面**: 清晰的信息层级和交互流程
6. **可行的实施计划**: 5个阶段，12周完成

### 下一步行动

1. **评审**: 与团队评审此方案，收集反馈
2. **细化**: 根据反馈细化设计细节
3. **原型**: 开发前端原型，验证交互设计
4. **开发**: 按照计划开始第一阶段开发

---

**文档版本**: v1.0
**最后更新**: 2025-01-07
**作者**: Claude Code (Main CLI)
