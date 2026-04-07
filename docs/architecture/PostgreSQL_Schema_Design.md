# PostgreSQL关系数据表结构设计

> **参考指南说明**:
> 本文件是架构相关的补充指南、说明或笔记，不是当前仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例和说明应视为补充参考；若与当前代码或主线治理文档冲突，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


> **版本**: 1.0.0
> **创建日期**: 2025-11-21
> **用途**: 定义PostgreSQL中用于存储关系型数据的表结构

---

## 📋 概述

PostgreSQL作为关系型数据库，专门用于存储结构化关系数据（用户配置、策略管理、风险预警、股票基础信息等）。本文档定义了支持IRelationalDataSource接口的完整表结构。

**数据库名称**: `mystocks`

**核心特性**:
- ACID事务支持
- 复杂JOIN查询
- JSONB字段支持半结构化数据
- 全文搜索 (pg_trgm扩展)
- 自动时间戳 (created_at, updated_at)

---

## 🏗️ 表结构设计

### 1. 用户表 (users)

**用途**: 存储用户基础信息

```sql
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',  -- active/inactive/suspended
    role VARCHAR(20) DEFAULT 'user',      -- user/admin/vip
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- 索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at);
```

**字段说明**:
- `id`: 用户唯一标识
- `username`: 用户名 (唯一)
- `email`: 邮箱 (唯一)
- `password_hash`: 密码哈希 (bcrypt)
- `status`: 账户状态
- `role`: 用户角色

---

### 2. 自选股表 (watchlist)

**用途**: 存储用户自选股列表

```sql
CREATE TABLE IF NOT EXISTS watchlist (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    list_type VARCHAR(20) DEFAULT 'favorite',  -- favorite/strategy/industry/concept
    note TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, symbol, list_type)
);

-- 索引
CREATE INDEX idx_watchlist_user_id ON watchlist(user_id);
CREATE INDEX idx_watchlist_symbol ON watchlist(symbol);
CREATE INDEX idx_watchlist_list_type ON watchlist(list_type);
CREATE INDEX idx_watchlist_added_at ON watchlist(added_at DESC);
```

**字段说明**:
- `user_id`: 用户ID (外键)
- `symbol`: 股票代码
- `list_type`: 列表类型
- `note`: 用户备注
- `added_at`: 添加时间

**唯一约束**: (user_id, symbol, list_type) - 同一用户不能重复添加同类型的股票

---

### 3. 策略配置表 (strategy_configs)

**用途**: 存储用户交易策略配置

```sql
CREATE TABLE IF NOT EXISTS strategy_configs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    strategy_type VARCHAR(50) NOT NULL,  -- momentum/mean_reversion/grid/arbitrage
    status VARCHAR(20) DEFAULT 'inactive',  -- active/inactive/backtesting
    parameters JSONB NOT NULL,           -- 策略参数(JSON格式)
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, name)
);

-- 索引
CREATE INDEX idx_strategy_user_id ON strategy_configs(user_id);
CREATE INDEX idx_strategy_type ON strategy_configs(strategy_type);
CREATE INDEX idx_strategy_status ON strategy_configs(status);
CREATE INDEX idx_strategy_updated_at ON strategy_configs(updated_at DESC);

-- GIN索引支持JSONB查询
CREATE INDEX idx_strategy_parameters ON strategy_configs USING GIN(parameters);
```

**字段说明**:
- `name`: 策略名称
- `strategy_type`: 策略类型
- `status`: 运行状态
- `parameters`: 策略参数 (JSONB格式，灵活存储)
- `description`: 策略描述

**参数示例** (JSONB):
```json
{
  "lookback_period": 20,
  "entry_threshold": 0.02,
  "exit_threshold": -0.01,
  "max_position_size": 0.1,
  "stop_loss": -0.05
}
```

---

### 4. 风险预警表 (risk_alerts)

**用途**: 存储用户风险预警配置

```sql
CREATE TABLE IF NOT EXISTS risk_alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    alert_type VARCHAR(20) NOT NULL,     -- price/change/volume/position
    condition VARCHAR(10) NOT NULL,      -- >=, <=, >, <, ==
    threshold DECIMAL(15, 4) NOT NULL,
    notification_methods JSONB NOT NULL, -- ["email", "sms", "webhook"]
    enabled BOOLEAN DEFAULT TRUE,
    triggered_count INTEGER DEFAULT 0,   -- 触发次数
    last_triggered TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_risk_alert_user_id ON risk_alerts(user_id);
CREATE INDEX idx_risk_alert_symbol ON risk_alerts(symbol);
CREATE INDEX idx_risk_alert_type ON risk_alerts(alert_type);
CREATE INDEX idx_risk_alert_enabled ON risk_alerts(enabled);
```

**字段说明**:
- `alert_type`: 预警类型
- `condition`: 触发条件
- `threshold`: 阈值
- `notification_methods`: 通知方式 (JSONB数组)
- `enabled`: 是否启用
- `triggered_count`: 触发次数统计

---

### 5. 用户偏好设置表 (user_preferences)

**用途**: 存储用户个性化设置

```sql
CREATE TABLE IF NOT EXISTS user_preferences (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    display_settings JSONB DEFAULT '{}',      -- 显示设置
    notification_settings JSONB DEFAULT '{}', -- 通知设置
    trading_settings JSONB DEFAULT '{}',      -- 交易设置
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- GIN索引支持JSONB查询
CREATE INDEX idx_preferences_display ON user_preferences USING GIN(display_settings);
CREATE INDEX idx_preferences_notification ON user_preferences USING GIN(notification_settings);
```

**字段说明**:
- `display_settings`: 显示偏好 (主题、语言、图表类型等)
- `notification_settings`: 通知偏好
- `trading_settings`: 交易偏好

**设置示例** (JSONB):
```json
{
  "display_settings": {
    "theme": "dark",
    "language": "zh_CN",
    "chart_type": "candle",
    "default_period": "1d"
  },
  "notification_settings": {
    "email_enabled": true,
    "sms_enabled": false,
    "push_enabled": true,
    "quiet_hours": {"start": "22:00", "end": "08:00"}
  },
  "trading_settings": {
    "default_order_type": "limit",
    "confirm_before_trade": true,
    "auto_stop_loss": false
  }
}
```

---

### 6. 股票基础信息表 (stock_basic_info)

**用途**: 存储股票基础静态信息

```sql
CREATE TABLE IF NOT EXISTS stock_basic_info (
    symbol VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    pinyin VARCHAR(100),                 -- 拼音首字母 (用于搜索)
    market VARCHAR(20) NOT NULL,         -- 上海/深圳
    industry VARCHAR(50),
    sector VARCHAR(50),
    list_date DATE,
    total_shares BIGINT,                 -- 总股本
    float_shares BIGINT,                 -- 流通股本
    status VARCHAR(20) DEFAULT 'active', -- active/suspended/delisted
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_stock_name ON stock_basic_info(name);
CREATE INDEX idx_stock_market ON stock_basic_info(market);
CREATE INDEX idx_stock_industry ON stock_basic_info(industry);
CREATE INDEX idx_stock_status ON stock_basic_info(status);

-- 全文搜索索引 (GIN + pg_trgm)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_stock_name_trgm ON stock_basic_info USING GIN(name gin_trgm_ops);
CREATE INDEX idx_stock_pinyin_trgm ON stock_basic_info USING GIN(pinyin gin_trgm_ops);
```

**字段说明**:
- `symbol`: 股票代码 (主键)
- `name`: 股票名称
- `pinyin`: 拼音首字母 (支持快速搜索)
- `market`: 交易市场
- `industry`: 所属行业
- `sector`: 所属板块
- `list_date`: 上市日期
- `total_shares`: 总股本
- `float_shares`: 流通股本

---

### 7. 行业分类表 (industry_classification)

**用途**: 存储行业分类信息

```sql
CREATE TABLE IF NOT EXISTS industry_classification (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    classification VARCHAR(20) NOT NULL,  -- sw/csrc/zjh
    level INTEGER NOT NULL,               -- 1/2/3 (一级/二级/三级)
    parent_code VARCHAR(20),
    stock_count INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_code) REFERENCES industry_classification(code) ON DELETE SET NULL
);

-- 索引
CREATE INDEX idx_industry_code ON industry_classification(code);
CREATE INDEX idx_industry_classification ON industry_classification(classification);
CREATE INDEX idx_industry_level ON industry_classification(level);
CREATE INDEX idx_industry_parent ON industry_classification(parent_code);
```

**字段说明**:
- `code`: 行业代码 (如: 801010)
- `name`: 行业名称
- `classification`: 分类标准 (sw/csrc/zjh)
- `level`: 分类级别
- `parent_code`: 父级行业代码

**分类标准**:
- `sw`: 申万行业分类
- `csrc`: 证监会行业分类
- `zjh`: 中金行业分类

---

### 8. 概念板块表 (concept_classification)

**用途**: 存储概念板块信息

```sql
CREATE TABLE IF NOT EXISTS concept_classification (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    stock_count INTEGER DEFAULT 0,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_concept_code ON concept_classification(code);
CREATE INDEX idx_concept_name ON concept_classification(name);
CREATE INDEX idx_concept_updated ON concept_classification(updated_at DESC);
```

**字段说明**:
- `code`: 概念代码 (如: BK0001)
- `name`: 概念名称
- `stock_count`: 成分股数量
- `description`: 概念描述

---

### 9. 股票-行业关系表 (stock_industry_mapping)

**用途**: 股票与行业的多对多关系

```sql
CREATE TABLE IF NOT EXISTS stock_industry_mapping (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL REFERENCES stock_basic_info(symbol) ON DELETE CASCADE,
    industry_code VARCHAR(20) NOT NULL REFERENCES industry_classification(code) ON DELETE CASCADE,
    effective_date DATE DEFAULT CURRENT_DATE,
    UNIQUE(symbol, industry_code)
);

-- 索引
CREATE INDEX idx_stock_industry_symbol ON stock_industry_mapping(symbol);
CREATE INDEX idx_stock_industry_code ON stock_industry_mapping(industry_code);
```

---

### 10. 股票-概念关系表 (stock_concept_mapping)

**用途**: 股票与概念的多对多关系

```sql
CREATE TABLE IF NOT EXISTS stock_concept_mapping (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL REFERENCES stock_basic_info(symbol) ON DELETE CASCADE,
    concept_code VARCHAR(20) NOT NULL REFERENCES concept_classification(code) ON DELETE CASCADE,
    effective_date DATE DEFAULT CURRENT_DATE,
    UNIQUE(symbol, concept_code)
);

-- 索引
CREATE INDEX idx_stock_concept_symbol ON stock_concept_mapping(symbol);
CREATE INDEX idx_stock_concept_code ON stock_concept_mapping(concept_code);
```

---

## 🔧 数据完整性约束

### 1. 外键约束
- 所有用户相关表通过`user_id`关联到`users`表
- 级联删除 (`ON DELETE CASCADE`) - 删除用户时自动删除关联数据
- 股票映射表通过外键确保数据一致性

### 2. 唯一约束
- `watchlist`: (user_id, symbol, list_type)
- `strategy_configs`: (user_id, name)
- `industry_classification`: code
- `concept_classification`: code
- `stock_industry_mapping`: (symbol, industry_code)
- `stock_concept_mapping`: (symbol, concept_code)

### 3. 默认值
- 时间戳字段自动设置 `CURRENT_TIMESTAMP`
- 状态字段默认值 (active/inactive等)
- 计数器字段默认0

---

## 📊 存储估算

### 核心业务表

| 表名 | 预估行数 | 单行大小 | 总大小 |
|------|---------|---------|--------|
| users | 100,000 | 300B | 30MB |
| watchlist | 1,000,000 | 150B | 150MB |
| strategy_configs | 200,000 | 500B | 100MB |
| risk_alerts | 500,000 | 200B | 100MB |
| user_preferences | 100,000 | 1KB | 100MB |

### 参考数据表

| 表名 | 预估行数 | 单行大小 | 总大小 |
|------|---------|---------|--------|
| stock_basic_info | 5,000 | 500B | 2.5MB |
| industry_classification | 500 | 200B | 100KB |
| concept_classification | 1,000 | 200B | 200KB |
| stock_industry_mapping | 10,000 | 100B | 1MB |
| stock_concept_mapping | 50,000 | 100B | 5MB |

**总计**: 约490MB (业务数据) + 9MB (参考数据) = **~500MB**

**增长预估**:
- 每月新增用户: ~1,000
- 每月新增自选股: ~10,000
- 每月新增策略: ~2,000

---

## 🚀 查询优化策略

### 1. 索引优化

**B-Tree索引** (默认):
- 主键、外键自动索引
- 频繁WHERE过滤字段 (user_id, symbol, status)
- 排序字段 (created_at DESC, updated_at DESC)

**GIN索引** (JSONB):
```sql
-- 支持JSONB字段的高效查询
CREATE INDEX idx_strategy_parameters ON strategy_configs USING GIN(parameters);
CREATE INDEX idx_preferences_display ON user_preferences USING GIN(display_settings);
```

**全文搜索索引** (pg_trgm):
```sql
-- 支持模糊搜索和拼音搜索
CREATE INDEX idx_stock_name_trgm ON stock_basic_info USING GIN(name gin_trgm_ops);
CREATE INDEX idx_stock_pinyin_trgm ON stock_basic_info USING GIN(pinyin gin_trgm_ops);
```

### 2. 查询示例

**自选股查询** (带JOIN避免N+1):
```sql
SELECT
    w.id, w.symbol, w.list_type, w.note, w.added_at,
    s.name, s.industry, s.market
FROM watchlist w
LEFT JOIN stock_basic_info s ON w.symbol = s.symbol
WHERE w.user_id = $1
  AND w.list_type = $2
ORDER BY w.added_at DESC;
```

**股票模糊搜索** (全文搜索):
```sql
SELECT symbol, name, pinyin, market,
       CASE
           WHEN symbol LIKE $1 THEN 'code'
           WHEN name LIKE $1 THEN 'name'
           ELSE 'pinyin'
       END as match_type
FROM stock_basic_info
WHERE symbol LIKE $1
   OR name LIKE $1
   OR pinyin LIKE $1
ORDER BY
    CASE match_type
        WHEN 'code' THEN 1
        WHEN 'name' THEN 2
        ELSE 3
    END
LIMIT 20;
```

**行业成分股查询** (JOIN):
```sql
SELECT DISTINCT s.symbol
FROM stock_industry_mapping sim
JOIN stock_basic_info s ON sim.symbol = s.symbol
WHERE sim.industry_code = $1
  AND s.status = 'active'
ORDER BY s.symbol;
```

### 3. 分区策略 (可选)

对于大表可考虑分区：

```sql
-- 按年份分区watchlist表
CREATE TABLE watchlist_2025 PARTITION OF watchlist
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE watchlist_2026 PARTITION OF watchlist
FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
```

---

## 🛡️ 数据安全

### 1. 密码安全
```sql
-- 使用pgcrypto扩展
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 密码哈希存储
INSERT INTO users (username, email, password_hash)
VALUES ('user1', 'user1@example.com', crypt('password123', gen_salt('bf')));

-- 密码验证
SELECT * FROM users
WHERE username = 'user1'
  AND password_hash = crypt('password123', password_hash);
```

### 2. 数据脱敏
```sql
-- 敏感字段加密视图
CREATE VIEW users_safe AS
SELECT id, username,
       regexp_replace(email, '(.{3}).*(@.*)', '\1***\2') as email_masked,
       regexp_replace(phone, '(\d{3})\d{4}(\d{4})', '\1****\2') as phone_masked,
       status, role, created_at
FROM users;
```

### 3. 审计日志
```sql
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(50),
    table_name VARCHAR(50),
    record_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔄 数据库维护

### 1. 自动更新时间戳

```sql
-- 创建触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 应用到所有需要的表
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_strategy_updated_at
    BEFORE UPDATE ON strategy_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 2. 定期清理

```sql
-- 清理超过1年的已触发预警记录
DELETE FROM risk_alerts
WHERE last_triggered < CURRENT_TIMESTAMP - INTERVAL '1 year'
  AND enabled = FALSE;

-- 清理未登录超过2年的用户
DELETE FROM users
WHERE last_login < CURRENT_TIMESTAMP - INTERVAL '2 years'
  AND status = 'inactive';
```

### 3. 统计信息更新

```sql
-- 定期更新行业/概念成分股数量
UPDATE industry_classification
SET stock_count = (
    SELECT COUNT(DISTINCT symbol)
    FROM stock_industry_mapping
    WHERE industry_code = industry_classification.code
);

UPDATE concept_classification
SET stock_count = (
    SELECT COUNT(DISTINCT symbol)
    FROM stock_concept_mapping
    WHERE concept_code = concept_classification.code
);
```

---

## 📝 建表脚本

完整的建表脚本见: `scripts/database/create_postgresql_tables.sql`

**执行顺序**:
1. 创建数据库和扩展
2. 创建基础表 (users, stock_basic_info, industry_classification, concept_classification)
3. 创建关系表 (stock_industry_mapping, stock_concept_mapping)
4. 创建用户相关表 (watchlist, strategy_configs, risk_alerts, user_preferences)
5. 创建索引
6. 创建触发器
7. 插入初始数据

---

## 📖 ER图

```
┌─────────────┐         ┌──────────────────┐
│   users     │◄────────│   watchlist      │
└─────────────┘         └──────────────────┘
      ▲                          │
      │                          │
      │                          ▼
      │                  ┌──────────────────┐
      │                  │ stock_basic_info │
      │                  └──────────────────┘
      │                          │
      │                    ┌─────┴─────┐
      │                    │           │
      │                    ▼           ▼
      │         ┌───────────────┐  ┌──────────────┐
      │         │stock_industry_│  │stock_concept_│
      │         │   mapping     │  │   mapping    │
      │         └───────────────┘  └──────────────┘
      │                 │                 │
      │                 ▼                 ▼
      │         ┌───────────────┐  ┌──────────────┐
      │         │  industry_    │  │  concept_    │
      │         │classification │  │classification│
      │         └───────────────┘  └──────────────┘
      │
      ├─────────┐
      │         │
      ▼         ▼
┌──────────┐ ┌──────────────┐
│strategy_ │ │ risk_alerts  │
│ configs  │ │              │
└──────────┘ └──────────────┘
      │
      │
      ▼
┌──────────────────┐
│ user_preferences │
└──────────────────┘
```

---

**文档版本**: 1.0.0
**最后更新**: 2025-11-21
