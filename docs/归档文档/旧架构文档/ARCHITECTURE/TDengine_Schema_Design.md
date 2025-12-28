# TDengine超表结构设计

> **版本**: 1.0.0
> **创建日期**: 2025-11-21
> **用途**: 定义TDengine中用于存储高频时序数据的超表结构

---

## 📋 概述

TDengine作为时序数据库，专门用于存储高频市场数据（Tick、分钟K线、盘口快照等）。本文档定义了支持ITimeSeriesDataSource接口的超表结构。

---

## 🏗️ 超表设计

### 1. tick_data (Tick数据超表)

**用途**: 存储逐笔成交数据

**字段定义**:
```sql
CREATE STABLE IF NOT EXISTS tick_data (
    ts TIMESTAMP,              -- 时间戳 (主键)
    price FLOAT,               -- 成交价格
    volume INT,                -- 成交量
    amount FLOAT,              -- 成交额
    direction BINARY(4),       -- 方向 (buy/sell/neutral)
    bid_price FLOAT,           -- 买一价
    ask_price FLOAT,           -- 卖一价
    bid_volume INT,            -- 买一量
    ask_volume INT             -- 卖一量
) TAGS (
    symbol BINARY(20),         -- 股票代码 (如: 600000.SH)
    exchange BINARY(10)        -- 交易所 (SSE/SZSE)
);
```

**索引**:
- 时间戳自动索引
- Tag自动索引 (symbol, exchange)

**保留策略**: 90天

---

### 2. minute_kline (分钟K线超表)

**用途**: 存储分钟级K线数据

**字段定义**:
```sql
CREATE STABLE IF NOT EXISTS minute_kline (
    ts TIMESTAMP,              -- 时间戳 (分钟起始时间)
    open FLOAT,                -- 开盘价
    high FLOAT,                -- 最高价
    low FLOAT,                 -- 最低价
    close FLOAT,               -- 收盘价
    volume BIGINT,             -- 成交量
    amount FLOAT,              -- 成交额
    num_trades INT,            -- 成交笔数
    vwap FLOAT                 -- 成交均价
) TAGS (
    symbol BINARY(20),         -- 股票代码
    exchange BINARY(10),       -- 交易所
    period BINARY(5)           -- 周期 (1m/5m/15m/30m/60m)
);
```

**索引**:
- 时间戳自动索引
- Tag自动索引 (symbol, exchange, period)

**保留策略**: 365天

---

### 3. daily_kline (日K线超表)

**用途**: 存储日线数据

**字段定义**:
```sql
CREATE STABLE IF NOT EXISTS daily_kline (
    ts TIMESTAMP,              -- 时间戳 (交易日期 00:00:00)
    open FLOAT,                -- 开盘价
    high FLOAT,                -- 最高价
    low FLOAT,                 -- 最低价
    close FLOAT,               -- 收盘价
    volume BIGINT,             -- 成交量
    amount FLOAT,              -- 成交额
    change_pct FLOAT,          -- 涨跌幅 (%)
    turn_over FLOAT,           -- 换手率 (%)
    total_mv FLOAT,            -- 总市值
    circulation_mv FLOAT       -- 流通市值
) TAGS (
    symbol BINARY(20),         -- 股票代码
    exchange BINARY(10)        -- 交易所
);
```

**索引**:
- 时间戳自动索引
- Tag自动索引 (symbol, exchange)

**保留策略**: 永久保留

---

### 4. fund_flow (资金流向超表)

**用途**: 存储主力资金流向数据

**字段定义**:
```sql
CREATE STABLE IF NOT EXISTS fund_flow (
    ts TIMESTAMP,              -- 时间戳
    main_net_inflow FLOAT,     -- 主力净流入 (元)
    main_inflow FLOAT,         -- 主力流入
    main_outflow FLOAT,        -- 主力流出
    super_net_inflow FLOAT,    -- 超大单净流入
    large_net_inflow FLOAT,    -- 大单净流入
    medium_net_inflow FLOAT,   -- 中单净流入
    small_net_inflow FLOAT,    -- 小单净流入
    net_inflow_rate FLOAT      -- 净流入率 (%)
) TAGS (
    symbol BINARY(20),         -- 股票代码
    exchange BINARY(10)        -- 交易所
);
```

**索引**:
- 时间戳自动索引
- Tag自动索引 (symbol, exchange)

**保留策略**: 90天

---

### 5. index_realtime (指数实时数据超表)

**用途**: 存储指数实时行情

**字段定义**:
```sql
CREATE STABLE IF NOT EXISTS index_realtime (
    ts TIMESTAMP,              -- 时间戳
    price FLOAT,               -- 最新价
    open FLOAT,                -- 开盘价
    high FLOAT,                -- 最高价
    low FLOAT,                 -- 最低价
    pre_close FLOAT,           -- 昨收价
    change_pct FLOAT,          -- 涨跌幅 (%)
    volume BIGINT,             -- 成交量
    amount FLOAT,              -- 成交额
    up_count INT,              -- 上涨家数
    down_count INT,            -- 下跌家数
    flat_count INT             -- 平盘家数
) TAGS (
    index_code BINARY(20),     -- 指数代码 (如: sh000001)
    index_name BINARY(50)      -- 指数名称 (如: 上证指数)
);
```

**索引**:
- 时间戳自动索引
- Tag自动索引 (index_code, index_name)

**保留策略**: 90天

---

### 6. market_snapshot (盘口快照超表)

**用途**: 存储Level2盘口快照数据

**字段定义**:
```sql
CREATE STABLE IF NOT EXISTS market_snapshot (
    ts TIMESTAMP,              -- 时间戳
    price FLOAT,               -- 最新价
    -- 五档买盘
    bid1_price FLOAT,
    bid1_volume INT,
    bid2_price FLOAT,
    bid2_volume INT,
    bid3_price FLOAT,
    bid3_volume INT,
    bid4_price FLOAT,
    bid4_volume INT,
    bid5_price FLOAT,
    bid5_volume INT,
    -- 五档卖盘
    ask1_price FLOAT,
    ask1_volume INT,
    ask2_price FLOAT,
    ask2_volume INT,
    ask3_price FLOAT,
    ask3_volume INT,
    ask4_price FLOAT,
    ask4_volume INT,
    ask5_price FLOAT,
    ask5_volume INT
) TAGS (
    symbol BINARY(20),         -- 股票代码
    exchange BINARY(10)        -- 交易所
);
```

**索引**:
- 时间戳自动索引
- Tag自动索引 (symbol, exchange)

**保留策略**: 30天

---

## 🔧 子表命名规范

**规则**: `{超表名}_{symbol}_{exchange}`

**示例**:
```
tick_data_600000_SH
minute_kline_000001_SZ
daily_kline_sh000001_INDEX
fund_flow_600519_SH
```

---

## 📊 存储估算

### Tick数据
- 每只股票每秒约10条Tick (交易时段)
- 每天4小时 = 14400秒
- 每条记录约100字节
- 单只股票/天: 14400 × 10 × 100B ≈ 14.4MB
- 5000只股票/天: 72GB
- **90天保留**: 6.5TB (压缩后约650GB)

### 分钟K线
- 每只股票每天240分钟 (4小时)
- 每条记录约80字节
- 单只股票/天: 240 × 80B ≈ 19.2KB
- 5000只股票/天: 96MB
- **365天保留**: 35GB (压缩后约3.5GB)

### 日K线
- 每只股票每年约250个交易日
- 每条记录约100字节
- 单只股票/年: 250 × 100B ≈ 25KB
- 5000只股票/年: 125MB
- **永久保留**: 10年 1.25GB

**总计**: 约700GB (压缩后)

---

## 🚀 查询优化策略

### 1. 时间范围分区
```sql
-- 利用TDengine自动时间分区
SELECT * FROM minute_kline
WHERE ts >= '2025-01-01 00:00:00'
  AND ts < '2025-01-02 00:00:00'
  AND symbol = '600000.SH';
```

### 2. 超表聚合查询
```sql
-- 查询所有股票的最新价格
SELECT last(close) as latest_price, symbol
FROM minute_kline
GROUP BY symbol;
```

### 3. 窗口查询
```sql
-- 计算1小时滑动窗口的OHLC
SELECT _wstart, first(open), max(high), min(low), last(close)
FROM minute_kline
WHERE symbol = '600000.SH'
INTERVAL(1h) SLIDING(5m);
```

### 4. 连续查询 (Continuous Query)
```sql
-- 自动从分钟数据聚合到小时数据
CREATE STREAM hour_kline_stream INTO hour_kline AS
SELECT _wstart as ts, first(open) as open, max(high) as high,
       min(low) as low, last(close) as close, sum(volume) as volume
FROM minute_kline
INTERVAL(1h);
```

---

## 🛡️ 数据完整性保障

### 1. 主键约束
- 时间戳 + Tags组合确保唯一性
- TDengine自动处理重复数据覆盖

### 2. 数据压缩
- TDengine自动压缩 (压缩比约10:1)
- 历史数据自动迁移到压缩存储

### 3. 数据保留策略
```sql
-- 设置90天保留期
ALTER DATABASE market_data KEEP 90;

-- 设置自动压缩
ALTER DATABASE market_data COMP 2;
```

---

## 📝 建表脚本

完整的建表脚本见: `scripts/database/create_tdengine_stables.sql`

---

**文档版本**: 1.0.0
**最后更新**: 2025-11-21
