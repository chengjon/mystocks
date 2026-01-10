# 监控清单管理 - Spec Delta

**能力**: 监控清单管理 (Watchlist Management)
**变更ID**: add-smart-quant-monitoring
**状态**: 待审核

---

## ADDED Requirements

### Requirement: 创建监控清单

The system MUST allow users to create multiple independent monitoring watchlists (portfolios), each containing name, type, and risk control configuration.

#### Scenario: 用户创建手动监控清单

**GIVEN** 用户已登录系统
**WHEN** 用户发送 POST 请求到 `/api/v1/monitoring/watchlists`
**AND** 请求体包含：
```json
{
  "name": "核心科技股",
  "user_id": 1,
  "type": "manual",
  "risk_profile": {
    "risk_tolerance": "high",
    "max_drawdown_limit": 0.2
  }
}
```
**THEN** 系统返回 201 Created
**AND** 响应体包含新创建的 watchlist_id
**AND** 数据库 `monitoring_watchlists` 表新增一条记录

#### Scenario: 用户创建策略自动清单

**GIVEN** 用户已登录系统
**WHEN** 用户创建清单时指定 type="strategy"
**THEN** 系统标记该清单为策略自动管理类型
**AND** 清单允许策略模块自动添加/移除股票

---

### Requirement: 添加股票到清单（含入库上下文）

The system MUST support adding stocks to watchlists with entry context recording, including entry price, entry reason, stop loss price, and target price.

#### Scenario: 用户添加股票并记录入库上下文

**GIVEN** 用户已创建清单 "核心科技股"（watchlist_id=1）
**WHEN** 用户发送 POST 请求到 `/api/v1/monitoring/watchlists/1/stocks`
**AND** 请求体包含：
```json
{
  "stock_code": "600519.SH",
  "entry_price": 1850.50,
  "entry_reason": "macd_gold_cross",
  "stop_loss_price": 1750.00,
  "target_price": 2000.00
}
```
**THEN** 系统返回 201 Created
**AND** 数据库 `monitoring_watchlist_stocks` 表新增记录
**AND** 所有风控字段正确保存

#### Scenario: 用户添加股票但不指定入库理由

**GIVEN** 用户已创建清单
**WHEN** 用户添加股票时不提供 entry_reason
**THEN** 系统使用默认值 "manual_pick"
**AND** 其他字段正常保存

#### Scenario: 用户重复添加同一股票

**GIVEN** 清单中已存在 stock_code="600519.SH"
**WHEN** 用户再次添加同一股票
**THEN** 系统返回 400 Bad Request
**AND** 错误消息提示 "股票已在清单中"

---

### Requirement: 批量添加股票到清单

The system MUST support batch adding multiple stocks to a watchlist in a single operation to improve efficiency.

#### Scenario: 用户批量添加10只股票

**GIVEN** 用户已创建清单
**WHEN** 用户发送 POST 请求到 `/api/v1/monitoring/watchlists/1/stocks/batch`
**AND** 请求体包含 10 只股票信息
**THEN** 系统批量插入所有股票
**AND** 返回成功添加的数量（10）
**AND** 所有数据正确保存到数据库

#### Scenario: 批量添加时部分股票已存在

**GIVEN** 清单中已存在 stock_code="600519.SH"
**WHEN** 用户批量添加包含 "600519.SH" 的10只股票
**THEN** 系统跳过已存在的股票
**AND** 返回成功添加 9 只
**AND** 返回跳过 1 只（已存在）

---

### Requirement: 从清单移除股票

The system MUST support removing stocks from watchlists while preserving historical entry records (soft delete).

#### Scenario: 用户移除清单中的股票

**GIVEN** 清单中存在 stock_code="600519.SH"
**WHEN** 用户发送 DELETE 请求到 `/api/v1/monitoring/watchlists/1/stocks/600519.SH`
**THEN** 系统返回 204 No Content
**AND** 数据库记录标记为 is_active=False
**AND** 历史入库数据保留（软删除）

---

### Requirement: 查询清单详情

The system MUST support retrieving complete watchlist information, including all members and entry context.

#### Scenario: 用户查询清单详情

**GIVEN** 用户已创建清单 "核心科技股"
**AND** 清单包含 5 只股票
**WHEN** 用户发送 GET 请求到 `/api/v1/monitoring/watchlists/1`
**THEN** 系统返回 200 OK
**AND** 响应体包含：
  - watchlist_id, name, type, risk_profile
  - stocks 数组（5只股票）
  - 每只股票包含 stock_code, entry_price, entry_reason, stop_loss_price, target_price

#### Scenario: 查询不存在的清单

**GIVEN** 数据库中不存在 watchlist_id=999
**WHEN** 用户查询该清单
**THEN** 系统返回 404 Not Found

---

### Requirement: 列出用户所有清单

The system MUST support paginated retrieval of all user watchlists with filtering by type.

#### Scenario: 用户查询所有清单

**GIVEN** 用户创建了 3 个清单
**WHEN** 用户发送 GET 请求到 `/api/v1/monitoring/watchlists?user_id=1`
**THEN** 系统返回 200 OK
**AND** 响应体包含 3 个清单的摘要信息

#### Scenario: 用户筛选只显示手动清单

**GIVEN** 用户创建了 2 个手动清单、1 个策略清单
**WHEN** 用户查询时添加参数 `type=manual`
**THEN** 系统只返回 2 个手动清单

---

### Requirement: 更新清单风控配置

The system MUST support updating the risk control configuration (risk_profile) of watchlists.

#### Scenario: 用户更新清单风控配置

**GIVEN** 用户已创建清单
**WHEN** 用户发送 PUT 请求到 `/api/v1/monitoring/watchlists/1`
**AND** 请求体包含：
```json
{
  "risk_profile": {
    "risk_tolerance": "medium",
    "max_drawdown_limit": 0.15
  }
}
```
**THEN** 系统返回 200 OK
**AND** risk_profile 字段更新成功

---

### Requirement: 删除清单（级联删除成员）

The system MUST support deleting entire watchlists with automatic cascade deletion of all members (soft delete).

#### Scenario: 用户删除清单

**GIVEN** 用户已创建清单（包含 5 只股票）
**WHEN** 用户发送 DELETE 请求到 `/api/v1/monitoring/watchlists/1`
**THEN** 系统返回 204 No Content
**AND** monitoring_watchlists 表记录删除
**AND** monitoring_watchlist_stocks 表中所有相关记录级联删除

---

## MODIFIED Requirements

*无修改现有需求*

---

## REMOVED Requirements

*无删除现有需求*

---

## Cross-References

- **依赖**: `health-scoring` - 清单中的股票需要计算健康度评分
- **关联**: `portfolio-optimization` - 清单数据用于投资组合优化
- **关联**: `data-migration` - 现有 watchlist 数据迁移到新系统

---

## 数据模型

### monitoring_watchlists 表

```sql
CREATE TABLE monitoring_watchlists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) DEFAULT 'manual',  -- manual/strategy/benchmark
    risk_profile JSONB,                 -- 风控配置
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### monitoring_watchlist_stocks 表

```sql
CREATE TABLE monitoring_watchlist_stocks (
    id SERIAL PRIMARY KEY,
    watchlist_id INTEGER REFERENCES monitoring_watchlists(id) ON DELETE CASCADE,
    stock_code VARCHAR(20) NOT NULL,

    -- 入库上下文（关键新增）
    entry_price DECIMAL(10,2),
    entry_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    entry_reason VARCHAR(50),  -- 'macd_gold_cross', 'manual_pick'

    -- 风控设置
    stop_loss_price DECIMAL(10,2),
    target_price DECIMAL(10,2),

    weight DECIMAL(5,4) DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,

    UNIQUE(watchlist_id, stock_code)
);
```

---

**状态**: 待审核
**版本**: v1.0
