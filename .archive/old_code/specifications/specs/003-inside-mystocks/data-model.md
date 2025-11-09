# 数据模型设计文档 (Data Model Design)

**Feature**: 股票数据扩展功能集成
**Version**: 1.0.0
**Date**: 2025-10-14
**Status**: Phase 1 - Design

---

## 目录

1. [概述](#1-概述)
2. [实体关系图 (ER Diagram)](#2-实体关系图-er-diagram)
3. [核心实体设计](#3-核心实体设计)
4. [数据分类映射](#4-数据分类映射)
5. [数据库表详细设计](#5-数据库表详细设计)
6. [索引策略](#6-索引策略)
7. [数据生命周期管理](#7-数据生命周期管理)

---

## 1. 概述

### 1.1 设计原则

本数据模型设计遵循MyStocks项目的7大宪法原则：

1. **5层数据分类体系** - 所有实体都明确归类到5-tier分类系统
2. **智能自动路由** - 通过`DataClassification`自动路由到最优数据库
3. **配置驱动管理** - 所有表结构在`table_config.yaml`中定义
4. **时序优化** - 时间序列数据优先使用TimescaleDB的hypertable
5. **关系完整性** - 参考数据使用MySQL的外键约束保证ACID
6. **读写分离** - 热数据(Redis) + 冷数据(PostgreSQL/MySQL)分离
7. **监控埋点** - 所有数据操作自动记录到监控数据库

### 1.2 实体概览

本次设计涉及 **13个核心实体**：

| 实体ID | 实体名称 | 分类 | 目标数据库 |
|-------|---------|------|-----------|
| E01 | Stock | 参考数据-股票信息 | MySQL |
| E02 | StockDailyData | 市场数据-日线K线 | PostgreSQL+TimescaleDB |
| E03 | FundFlow | 衍生数据-资金流向 | PostgreSQL+TimescaleDB |
| E04 | ETFData | 市场数据-ETF数据 | PostgreSQL+TimescaleDB |
| E05 | ChipRaceData | 衍生数据-交易分析 | PostgreSQL+TimescaleDB |
| E06 | LongHuBangData | 衍生数据-机构流向 | PostgreSQL+TimescaleDB |
| E07 | BlockTradeData | 衍生数据-机构流向 | PostgreSQL+TimescaleDB |
| E08 | DividendData | 参考数据-公司行动 | MySQL |
| E09 | TechnicalIndicator | 衍生数据-技术指标 | PostgreSQL+TimescaleDB |
| E10 | TradingStrategy | 元数据-策略配置 | MySQL |
| E11 | StrategySignal | 衍生数据-交易信号 | PostgreSQL+TimescaleDB |
| E12 | BacktestResult | 衍生数据-回测结果 | PostgreSQL |
| E13 | BacktestTrade | 衍生数据-回测结果 | PostgreSQL+TimescaleDB |

---

## 2. 实体关系图 (ER Diagram)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         市场数据层 (Market Data)                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐      ┌──────────────────┐      ┌──────────────┐  │
│  │ Stock (E01)  │──────│ StockDailyData   │──────│ ETFData      │  │
│  │ (MySQL)      │ 1:N  │ (E02, PG+TSDB)  │      │ (E04, PG)    │  │
│  └──────┬───────┘      └────────┬─────────┘      └──────────────┘  │
│         │                       │                                    │
│         │ 1:N                   │ 1:N                                │
│         │                       │                                    │
└─────────┼───────────────────────┼────────────────────────────────────┘
          │                       │
┌─────────┼───────────────────────┼────────────────────────────────────┐
│         │                       │  衍生数据层 (Derived Data)          │
├─────────┼───────────────────────┼────────────────────────────────────┤
│         │                       │                                    │
│  ┌──────▼───────┐      ┌───────▼──────────┐      ┌──────────────┐  │
│  │ FundFlow     │      │ TechnicalIndicator│      │ ChipRaceData │  │
│  │ (E03, PG)    │      │ (E09, PG+TSDB)   │      │ (E05, PG)    │  │
│  └──────────────┘      └──────────────────┘      └──────────────┘  │
│                                                                       │
│  ┌──────────────┐      ┌──────────────────┐      ┌──────────────┐  │
│  │ LongHuBangData│     │ BlockTradeData   │      │ StrategySignal│ │
│  │ (E06, PG)    │      │ (E07, PG)        │      │ (E11, PG)    │  │
│  └──────────────┘      └──────────────────┘      └──────┬───────┘  │
│                                                           │           │
└───────────────────────────────────────────────────────────┼───────────┘
                                                            │
┌───────────────────────────────────────────────────────────┼───────────┐
│                                                           │策略层      │
├───────────────────────────────────────────────────────────┼───────────┤
│                                                           │            │
│  ┌──────────────┐      ┌──────────────────┐      ┌──────▼───────┐  │
│  │ TradingStrategy│ 1:N│ BacktestResult   │  1:N │ BacktestTrade│  │
│  │ (E10, MySQL) │─────│ (E12, PG)        │──────│ (E13, PG)    │  │
│  └──────────────┘      └──────────────────┘      └──────────────┘  │
│         │                                                            │
│         │ 1:N                                                        │
│         │                                                            │
│  ┌──────▼───────┐                                                   │
│  │ StrategySignal│                                                  │
│  │ (E11, PG)    │                                                   │
│  └──────────────┘                                                   │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│                         参考数据层 (Reference Data)                    │
├───────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌──────────────┐      ┌──────────────────┐                          │
│  │ Stock (E01)  │──────│ DividendData     │                          │
│  │ (MySQL)      │ 1:N  │ (E08, MySQL)     │                          │
│  └──────────────┘      └──────────────────┘                          │
│                                                                        │
└───────────────────────────────────────────────────────────────────────┘

【图例】
─────  一对多关系 (1:N)
PG     PostgreSQL
TSDB   TimescaleDB
MySQL  MySQL/MariaDB
```

---

## 3. 核心实体设计

### 3.1 E01 - Stock (股票基本信息)

**用途**: 股票静态参考数据
**数据分类**: `DataClassification.SYMBOLS_INFO`
**存储**: MySQL/MariaDB

```python
# 实体属性
class Stock:
    id: int                    # 主键
    symbol: str                # 股票代码 (如: 600519.SH)
    name: str                  # 股票名称
    exchange: str              # 交易所 (SH/SZ)
    sector: str                # 行业
    industry: str              # 细分行业
    list_date: date            # 上市日期
    market_cap: Decimal        # 总市值
    circulating_cap: Decimal   # 流通市值
    is_active: bool            # 是否有效
    created_at: datetime       # 创建时间
    updated_at: datetime       # 更新时间
```

**关系**:
- 1:N → StockDailyData (一个股票有多条日线数据)
- 1:N → FundFlow (一个股票有多条资金流向记录)
- 1:N → DividendData (一个股票有多次分红记录)

---

### 3.2 E02 - StockDailyData (股票日线数据)

**用途**: 股票历史OHLCV数据
**数据分类**: `DataClassification.DAILY_KLINE`
**存储**: PostgreSQL+TimescaleDB (hypertable)

```python
class StockDailyData:
    id: int                    # 主键
    symbol: str                # 股票代码 (外键 → Stock)
    trade_date: date           # 交易日期 (时间分区键)
    open: Decimal              # 开盘价
    high: Decimal              # 最高价
    low: Decimal               # 最低价
    close: Decimal             # 收盘价
    volume: int                # 成交量
    amount: Decimal            # 成交额
    turnover_rate: Decimal     # 换手率
    adj_factor: Decimal        # 复权因子
    created_at: datetime       # 创建时间
```

**时序特性**:
- TimescaleDB hypertable, 按 `trade_date` 分区
- 自动压缩历史数据 (>30天)
- 支持高效时间范围查询

---

### 3.3 E03 - FundFlow (个股资金流向)

**用途**: 个股主力资金流向分析
**数据分类**: `DataClassification.FUND_FLOW`
**存储**: PostgreSQL+TimescaleDB

```python
class FundFlow:
    id: int                          # 主键
    symbol: str                      # 股票代码 (外键 → Stock)
    trade_date: date                 # 交易日期 (时间分区键)
    timeframe: str                   # 时间维度 ('1','3','5','10')
    main_net_inflow: Decimal         # 主力净流入额
    main_net_inflow_rate: Decimal    # 主力净流入占比
    super_large_net_inflow: Decimal  # 超大单净流入额
    large_net_inflow: Decimal        # 大单净流入额
    medium_net_inflow: Decimal       # 中单净流入额
    small_net_inflow: Decimal        # 小单净流入额
    created_at: datetime             # 创建时间

    # 唯一约束
    UNIQUE(symbol, trade_date, timeframe)
```

**数据源**: Akshare Adapter (ENHANCE)

---

### 3.4 E04 - ETFData (ETF基金数据)

**用途**: ETF基金实时和历史数据
**数据分类**: `DataClassification.ETF_DATA`
**存储**: PostgreSQL+TimescaleDB

```python
class ETFData:
    id: int                          # 主键
    symbol: str                      # ETF代码
    name: str                        # ETF名称
    trade_date: date                 # 交易日期 (时间分区键)
    latest_price: Decimal            # 最新价
    change_percent: Decimal          # 涨跌幅
    change_amount: Decimal           # 涨跌额
    volume: int                      # 成交量
    amount: Decimal                  # 成交额
    open_price: Decimal              # 开盘价
    high_price: Decimal              # 最高价
    low_price: Decimal               # 最低价
    prev_close: Decimal              # 昨收价
    turnover_rate: Decimal           # 换手率
    total_market_cap: Decimal        # 总市值
    circulating_market_cap: Decimal  # 流通市值
    created_at: datetime             # 创建时间

    # 唯一约束
    UNIQUE(symbol, trade_date)
```

**数据源**: Akshare Adapter (ENHANCE)

---

### 3.5 E05 - ChipRaceData (竞价抢筹数据)

**用途**: 早盘/尾盘竞价抢筹分析
**数据分类**: `DataClassification.TRADING_ANALYSIS`
**存储**: PostgreSQL+TimescaleDB

```python
class ChipRaceData:
    id: int                      # 主键
    symbol: str                  # 股票代码 (外键 → Stock)
    name: str                    # 股票名称
    trade_date: date             # 交易日期 (时间分区键)
    race_type: str               # 抢筹类型 ('open'=早盘, 'end'=尾盘)
    latest_price: Decimal        # 最新价
    change_percent: Decimal      # 涨跌幅
    prev_close: Decimal          # 昨收价
    open_price: Decimal          # 今开价
    race_amount: Decimal         # 抢筹金额
    race_amplitude: Decimal      # 抢筹幅度
    race_commission: Decimal     # 抢筹委托金额
    race_transaction: Decimal    # 抢筹成交金额
    race_ratio: Decimal          # 抢筹占比
    created_at: datetime         # 创建时间

    # 唯一约束
    UNIQUE(symbol, trade_date, race_type)
```

**数据源**: TQLEX Adapter (NEW)

---

### 3.6 E06 - LongHuBangData (龙虎榜数据)

**用途**: 龙虎榜机构席位和交易明细
**数据分类**: `DataClassification.INSTITUTIONAL_FLOW`
**存储**: PostgreSQL+TimescaleDB

```python
class LongHuBangData:
    id: int                      # 主键
    symbol: str                  # 股票代码 (外键 → Stock)
    name: str                    # 股票名称
    trade_date: date             # 交易日期 (时间分区键)
    reason: str                  # 上榜原因
    buy_amount: Decimal          # 买入总额
    sell_amount: Decimal         # 卖出总额
    net_amount: Decimal          # 净买入额
    turnover_rate: Decimal       # 换手率
    institution_buy: Decimal     # 机构买入额
    institution_sell: Decimal    # 机构卖出额
    created_at: datetime         # 创建时间

    # 唯一约束
    UNIQUE(symbol, trade_date)
```

**数据源**: Akshare Adapter (ENHANCE)

---

### 3.7 E07 - BlockTradeData (大宗交易数据)

**用途**: 大宗交易明细和统计
**数据分类**: `DataClassification.INSTITUTIONAL_FLOW`
**存储**: PostgreSQL+TimescaleDB

```python
class BlockTradeData:
    id: int                      # 主键
    symbol: str                  # 股票代码 (外键 → Stock)
    name: str                    # 股票名称
    trade_date: date             # 交易日期 (时间分区键)
    trade_price: Decimal         # 成交价
    trade_volume: int            # 成交量
    trade_amount: Decimal        # 成交额
    buyer_branch: str            # 买方营业部
    seller_branch: str           # 卖方营业部
    discount_rate: Decimal       # 折价率
    created_at: datetime         # 创建时间
```

**数据源**: Akshare Adapter (ENHANCE)

---

### 3.8 E08 - DividendData (分红配送数据)

**用途**: 股票分红派息和配股信息
**数据分类**: `DataClassification.CORPORATE_ACTION`
**存储**: MySQL/MariaDB

```python
class DividendData:
    id: int                      # 主键
    symbol: str                  # 股票代码 (外键 → Stock)
    announce_date: date          # 公告日期
    ex_dividend_date: date       # 除权除息日
    record_date: date            # 股权登记日
    dividend_ratio: Decimal      # 分红比例 (每股)
    bonus_share_ratio: Decimal   # 送股比例
    transfer_ratio: Decimal      # 转增比例
    allotment_ratio: Decimal     # 配股比例
    allotment_price: Decimal     # 配股价
    created_at: datetime         # 创建时间
```

**数据源**: Akshare Adapter (ENHANCE)

---

### 3.9 E09 - TechnicalIndicator (技术指标计算结果)

**用途**: 存储技术指标计算结果 (可选缓存)
**数据分类**: `DataClassification.TECHNICAL_INDICATOR`
**存储**: PostgreSQL+TimescaleDB

```python
class TechnicalIndicator:
    id: int                      # 主键
    symbol: str                  # 股票代码 (外键 → Stock)
    indicator_name: str          # 指标名称 (如: SMA, RSI)
    calculation_date: timestamp  # 计算日期 (时间分区键)
    parameters: JSON             # 指标参数 (如: {"timeperiod": 20})
    output_values: JSON          # 输出值 (如: {"sma": 123.45})
    created_at: datetime         # 创建时间

    # 索引
    INDEX(symbol, indicator_name, calculation_date)
```

**注意**: 技术指标通常**实时计算**,此表用于可选的结果缓存

---

### 3.10 E10 - TradingStrategy (交易策略配置)

**用途**: 策略定义和参数配置
**数据分类**: `DataClassification.STRATEGY_CONFIG`
**存储**: MySQL/MariaDB

```python
class TradingStrategy:
    id: int                      # 主键
    strategy_id: str             # 策略ID (唯一标识)
    strategy_name: str           # 策略名称
    strategy_description: text   # 策略描述
    category: str                # 策略分类 (trend_following, mean_reversion, etc.)
    parameters: JSON             # 默认参数 (JSON格式)
    is_active: bool              # 是否启用
    created_by: int              # 创建用户ID
    created_at: datetime         # 创建时间
    updated_at: datetime         # 更新时间

    # 唯一约束
    UNIQUE(strategy_id)
```

**关系**:
- 1:N → StrategySignal (一个策略生成多个信号)
- 1:N → BacktestResult (一个策略有多个回测结果)

---

### 3.11 E11 - StrategySignal (策略交易信号)

**用途**: 策略生成的买卖信号
**数据分类**: `DataClassification.TRADING_SIGNAL`
**存储**: PostgreSQL+TimescaleDB

```python
class StrategySignal:
    id: int                      # 主键
    strategy_id: str             # 策略ID (外键 → TradingStrategy)
    symbol: str                  # 股票代码 (外键 → Stock)
    signal_date: timestamp       # 信号生成时间 (时间分区键)
    signal_type: int             # 信号类型 (1=买入, -1=卖出, 0=持有)
    price: Decimal               # 信号价格
    reason: text                 # 信号原因说明
    confidence: Decimal          # 信号置信度 (0-1)
    metadata: JSON               # 额外元数据 (如: 指标值快照)
    created_at: datetime         # 创建时间

    # 索引
    INDEX(strategy_id, signal_date DESC)
    INDEX(symbol, signal_date DESC)
```

**实时性**: 信号数据可先存入Redis缓存,再异步写入PostgreSQL

---

### 3.12 E12 - BacktestResult (回测结果汇总)

**用途**: 策略回测的性能指标汇总
**数据分类**: `DataClassification.BACKTEST_RESULT`
**存储**: PostgreSQL

```python
class BacktestResult:
    id: int                      # 主键
    backtest_id: str             # 回测ID (唯一标识)
    strategy_id: str             # 策略ID (外键 → TradingStrategy)
    symbol: str                  # 股票代码 (外键 → Stock)
    start_date: date             # 回测开始日期
    end_date: date               # 回测结束日期
    initial_capital: Decimal     # 初始资金
    final_capital: Decimal       # 最终资金
    total_return: Decimal        # 总收益率
    annual_return: Decimal       # 年化收益率
    sharpe_ratio: Decimal        # 夏普比率
    max_drawdown: Decimal        # 最大回撤
    win_rate: Decimal            # 胜率
    total_trades: int            # 总交易次数
    profit_factor: Decimal       # 盈亏比
    parameters: JSON             # 策略参数快照
    created_at: datetime         # 创建时间

    # 唯一约束
    UNIQUE(backtest_id)

    # 索引
    INDEX(strategy_id, created_at DESC)
    INDEX(symbol, created_at DESC)
```

**关系**:
- 1:N → BacktestTrade (一个回测有多笔交易明细)

---

### 3.13 E13 - BacktestTrade (回测交易明细)

**用途**: 回测过程中的每笔交易记录
**数据分类**: `DataClassification.BACKTEST_RESULT`
**存储**: PostgreSQL+TimescaleDB

```python
class BacktestTrade:
    id: int                      # 主键
    backtest_id: str             # 回测ID (外键 → BacktestResult)
    trade_date: timestamp        # 交易日期 (时间分区键)
    action: str                  # 操作类型 ('BUY' or 'SELL')
    symbol: str                  # 股票代码
    price: Decimal               # 成交价格
    shares: int                  # 成交股数
    amount: Decimal              # 成交金额
    commission: Decimal          # 手续费
    profit: Decimal              # 本次交易盈亏 (仅SELL时有值)
    return_rate: Decimal         # 本次交易收益率

    # 索引
    INDEX(backtest_id, trade_date)
```

---

## 4. 数据分类映射

根据MyStocks Constitution的5-tier分类体系：

### 4.1 市场数据 (Market Data)

| 实体 | 分类枚举 | 存储 | 特性 |
|-----|---------|------|------|
| StockDailyData | DAILY_KLINE | PostgreSQL+TimescaleDB | 高频写入,时序查询 |
| ETFData | ETF_DATA | PostgreSQL+TimescaleDB | 准实时更新 |

### 4.2 参考数据 (Reference Data)

| 实体 | 分类枚举 | 存储 | 特性 |
|-----|---------|------|------|
| Stock | SYMBOLS_INFO | MySQL/MariaDB | 静态,低频更新 |
| DividendData | CORPORATE_ACTION | MySQL/MariaDB | 静态,事件驱动 |

### 4.3 衍生数据 (Derived Data)

| 实体 | 分类枚举 | 存储 | 特性 |
|-----|---------|------|------|
| FundFlow | FUND_FLOW | PostgreSQL+TimescaleDB | 每日计算 |
| ChipRaceData | TRADING_ANALYSIS | PostgreSQL+TimescaleDB | 每日盘前/盘后 |
| LongHuBangData | INSTITUTIONAL_FLOW | PostgreSQL+TimescaleDB | 每日收盘后 |
| BlockTradeData | INSTITUTIONAL_FLOW | PostgreSQL+TimescaleDB | 每日收盘后 |
| TechnicalIndicator | TECHNICAL_INDICATOR | PostgreSQL+TimescaleDB | 实时计算(可选缓存) |
| StrategySignal | TRADING_SIGNAL | PostgreSQL+TimescaleDB | 实时生成 |
| BacktestResult | BACKTEST_RESULT | PostgreSQL | 按需计算 |
| BacktestTrade | BACKTEST_RESULT | PostgreSQL+TimescaleDB | 按需计算 |

### 4.4 元数据 (Meta Data)

| 实体 | 分类枚举 | 存储 | 特性 |
|-----|---------|------|------|
| TradingStrategy | STRATEGY_CONFIG | MySQL/MariaDB | 用户配置,低频 |

---

## 5. 数据库表详细设计

### 5.1 PostgreSQL+TimescaleDB 表 (7张)

#### 5.1.1 stock_fund_flow (E03)

```sql
-- 个股资金流向表
CREATE TABLE IF NOT EXISTS stock_fund_flow (
    id BIGSERIAL,
    symbol VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    main_net_inflow DECIMAL(20, 2),
    main_net_inflow_rate DECIMAL(10, 4),
    super_large_net_inflow DECIMAL(20, 2),
    large_net_inflow DECIMAL(20, 2),
    medium_net_inflow DECIMAL(20, 2),
    small_net_inflow DECIMAL(20, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, trade_date),
    UNIQUE(symbol, trade_date, timeframe)
);

-- 创建TimescaleDB hypertable
SELECT create_hypertable('stock_fund_flow', 'trade_date',
    chunk_time_interval => INTERVAL '1 month',
    if_not_exists => TRUE
);

-- 启用自动压缩 (30天后)
ALTER TABLE stock_fund_flow SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol,timeframe',
    timescaledb.compress_orderby = 'trade_date DESC'
);

SELECT add_compression_policy('stock_fund_flow', INTERVAL '30 days');
```

**索引策略**:
```sql
CREATE INDEX idx_stock_fund_flow_symbol_date
    ON stock_fund_flow(symbol, trade_date DESC);

CREATE INDEX idx_stock_fund_flow_timeframe
    ON stock_fund_flow(timeframe, trade_date DESC);
```

---

#### 5.1.2 etf_spot_data (E04)

```sql
-- ETF实时数据表
CREATE TABLE IF NOT EXISTS etf_spot_data (
    id BIGSERIAL,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(100),
    trade_date DATE NOT NULL,
    latest_price DECIMAL(10, 3),
    change_percent DECIMAL(10, 4),
    change_amount DECIMAL(10, 3),
    volume BIGINT,
    amount DECIMAL(20, 2),
    open_price DECIMAL(10, 3),
    high_price DECIMAL(10, 3),
    low_price DECIMAL(10, 3),
    prev_close DECIMAL(10, 3),
    turnover_rate DECIMAL(10, 4),
    total_market_cap DECIMAL(20, 2),
    circulating_market_cap DECIMAL(20, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, trade_date),
    UNIQUE(symbol, trade_date)
);

SELECT create_hypertable('etf_spot_data', 'trade_date',
    chunk_time_interval => INTERVAL '1 month',
    if_not_exists => TRUE
);

-- 压缩策略
ALTER TABLE etf_spot_data SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol',
    timescaledb.compress_orderby = 'trade_date DESC'
);

SELECT add_compression_policy('etf_spot_data', INTERVAL '30 days');
```

---

#### 5.1.3 chip_race_data (E05)

```sql
-- 竞价抢筹数据表
CREATE TABLE IF NOT EXISTS chip_race_data (
    id BIGSERIAL,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(100),
    trade_date DATE NOT NULL,
    race_type VARCHAR(10) NOT NULL,
    latest_price DECIMAL(10, 3),
    change_percent DECIMAL(10, 4),
    prev_close DECIMAL(10, 3),
    open_price DECIMAL(10, 3),
    race_amount DECIMAL(20, 2),
    race_amplitude DECIMAL(10, 4),
    race_commission DECIMAL(20, 2),
    race_transaction DECIMAL(20, 2),
    race_ratio DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, trade_date),
    UNIQUE(symbol, trade_date, race_type)
);

SELECT create_hypertable('chip_race_data', 'trade_date',
    chunk_time_interval => INTERVAL '1 month',
    if_not_exists => TRUE
);
```

---

#### 5.1.4 stock_lhb_detail (E06)

```sql
-- 龙虎榜详细数据表
CREATE TABLE IF NOT EXISTS stock_lhb_detail (
    id BIGSERIAL,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(100),
    trade_date DATE NOT NULL,
    reason VARCHAR(200),
    buy_amount DECIMAL(20, 2),
    sell_amount DECIMAL(20, 2),
    net_amount DECIMAL(20, 2),
    turnover_rate DECIMAL(10, 4),
    institution_buy DECIMAL(20, 2),
    institution_sell DECIMAL(20, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, trade_date),
    UNIQUE(symbol, trade_date)
);

SELECT create_hypertable('stock_lhb_detail', 'trade_date',
    chunk_time_interval => INTERVAL '1 month',
    if_not_exists => TRUE
);
```

---

#### 5.1.5 strategy_signals (E11)

```sql
-- 策略信号表
CREATE TABLE IF NOT EXISTS strategy_signals (
    id BIGSERIAL,
    strategy_id VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    signal_date TIMESTAMP NOT NULL,
    signal_type INT NOT NULL,
    price DECIMAL(10, 3),
    reason TEXT,
    confidence DECIMAL(5, 4),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, signal_date)
);

SELECT create_hypertable('strategy_signals', 'signal_date',
    chunk_time_interval => INTERVAL '1 week',
    if_not_exists => TRUE
);

-- 索引
CREATE INDEX idx_strategy_signals_strategy
    ON strategy_signals(strategy_id, signal_date DESC);

CREATE INDEX idx_strategy_signals_symbol
    ON strategy_signals(symbol, signal_date DESC);
```

---

#### 5.1.6 backtest_trades (E13)

```sql
-- 回测交易明细表
CREATE TABLE IF NOT EXISTS backtest_trades (
    id BIGSERIAL,
    backtest_id VARCHAR(50) NOT NULL,
    trade_date TIMESTAMP NOT NULL,
    action VARCHAR(10) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    price DECIMAL(10, 3),
    shares INT,
    amount DECIMAL(20, 2),
    commission DECIMAL(20, 2),
    profit DECIMAL(20, 2),
    return_rate DECIMAL(10, 4),
    PRIMARY KEY (id, trade_date)
);

SELECT create_hypertable('backtest_trades', 'trade_date',
    chunk_time_interval => INTERVAL '1 month',
    if_not_exists => TRUE
);

-- 索引
CREATE INDEX idx_backtest_trades_backtest
    ON backtest_trades(backtest_id, trade_date);
```

---

### 5.2 MySQL/MariaDB 表 (2张)

#### 5.2.1 strategy_configs (E10)

```sql
-- 策略配置表
CREATE TABLE IF NOT EXISTS strategy_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    strategy_id VARCHAR(50) NOT NULL UNIQUE,
    strategy_name VARCHAR(100) NOT NULL,
    strategy_description TEXT,
    category VARCHAR(50),
    parameters JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_active (is_active),
    INDEX idx_strategy_id (strategy_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略配置表';
```

---

#### 5.2.2 dividend_data (E08)

```sql
-- 分红配送数据表
CREATE TABLE IF NOT EXISTS dividend_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    announce_date DATE NOT NULL,
    ex_dividend_date DATE,
    record_date DATE,
    dividend_ratio DECIMAL(10, 4),
    bonus_share_ratio DECIMAL(10, 4),
    transfer_ratio DECIMAL(10, 4),
    allotment_ratio DECIMAL(10, 4),
    allotment_price DECIMAL(10, 3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_symbol_announce_date (symbol, announce_date),
    INDEX idx_symbol (symbol),
    INDEX idx_ex_dividend_date (ex_dividend_date),
    FOREIGN KEY (symbol) REFERENCES symbols(symbol) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分红配送数据表';
```

---

### 5.3 PostgreSQL 表 (非hypertable) (1张)

#### 5.3.1 backtest_results (E12)

```sql
-- 回测结果汇总表
CREATE TABLE IF NOT EXISTS backtest_results (
    id BIGSERIAL PRIMARY KEY,
    backtest_id VARCHAR(50) NOT NULL UNIQUE,
    strategy_id VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(20, 2),
    final_capital DECIMAL(20, 2),
    total_return DECIMAL(10, 4),
    annual_return DECIMAL(10, 4),
    sharpe_ratio DECIMAL(10, 4),
    max_drawdown DECIMAL(10, 4),
    win_rate DECIMAL(5, 4),
    total_trades INT,
    profit_factor DECIMAL(10, 4),
    parameters JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_backtest_results_strategy
    ON backtest_results(strategy_id, created_at DESC);

CREATE INDEX idx_backtest_results_symbol
    ON backtest_results(symbol, created_at DESC);

CREATE INDEX idx_backtest_results_backtest_id
    ON backtest_results(backtest_id);
```

---

## 6. 索引策略

### 6.1 索引设计原则

1. **时序数据索引**: 所有hypertable默认按时间列分区,自动创建时间索引
2. **复合索引**: 高频查询场景使用复合索引 (symbol + time)
3. **JSON索引**: 对JSONB字段的高频查询字段创建GIN索引
4. **唯一约束**: 防止重复数据的唯一索引

### 6.2 关键索引汇总

| 表名 | 索引名 | 字段 | 类型 | 用途 |
|-----|-------|------|------|------|
| stock_fund_flow | idx_stock_fund_flow_symbol_date | (symbol, trade_date DESC) | BTREE | 单股资金流查询 |
| etf_spot_data | idx_etf_spot_symbol | (symbol, trade_date DESC) | BTREE | ETF历史数据查询 |
| chip_race_data | idx_chip_race_symbol | (symbol, trade_date DESC) | BTREE | 抢筹历史查询 |
| stock_lhb_detail | idx_stock_lhb_symbol | (symbol, trade_date DESC) | BTREE | 龙虎榜历史查询 |
| strategy_signals | idx_strategy_signals_strategy | (strategy_id, signal_date DESC) | BTREE | 策略信号查询 |
| strategy_signals | idx_strategy_signals_symbol | (symbol, signal_date DESC) | BTREE | 个股信号查询 |
| backtest_trades | idx_backtest_trades_backtest | (backtest_id, trade_date) | BTREE | 回测交易明细 |
| backtest_results | idx_backtest_results_strategy | (strategy_id, created_at DESC) | BTREE | 策略回测历史 |

### 6.3 分区策略

所有TimescaleDB hypertable采用以下分区策略:

- **时间分区**: 按月分区 (chunk_time_interval = 1 month)
- **压缩策略**: 30天后自动压缩
- **保留策略**: 根据业务需求设置 (如: 保留3年历史数据)

```sql
-- 示例: 设置数据保留策略 (保留3年)
SELECT add_retention_policy('stock_fund_flow', INTERVAL '3 years');
```

---

## 7. 数据生命周期管理

### 7.1 数据写入流程

```
[数据源]
    → [Adapter层] (akshare_adapter / tqlex_adapter)
    → [UnifiedManager.save_data_by_classification()]
    → [DataStorageStrategy.get_target_database()] (自动路由)
    → [目标数据库] (PostgreSQL / MySQL / Redis)
    → [MonitoringDatabase] (日志记录)
```

### 7.2 数据更新策略

| 数据类型 | 更新频率 | 更新方式 | 数据源 |
|---------|---------|---------|--------|
| 股票日线数据 | 每日收盘后 | 增量插入 | Akshare |
| 资金流向 | 每日收盘后 | UPSERT (ON CONFLICT) | Akshare |
| ETF数据 | 每日收盘后 | UPSERT | Akshare |
| 竞价抢筹 | 早盘/尾盘 | 实时插入 | TQLEX |
| 龙虎榜 | 每日收盘后 | 增量插入 | Akshare |
| 分红数据 | 按公告更新 | 增量插入 | Akshare |
| 策略信号 | 实时生成 | 实时插入 | Strategy Engine |
| 回测结果 | 按需计算 | 插入 | Backtest Engine |

### 7.3 数据清理策略

#### 7.3.1 时序数据压缩

```sql
-- 所有hypertable在30天后自动压缩
-- 压缩率约 5:1 到 10:1

-- 查看压缩状态
SELECT * FROM timescaledb_information.compression_settings
WHERE hypertable_name IN (
    'stock_fund_flow',
    'etf_spot_data',
    'chip_race_data',
    'stock_lhb_detail',
    'strategy_signals',
    'backtest_trades'
);
```

#### 7.3.2 历史数据归档

```sql
-- 示例: 归档3年以上的回测交易明细到冷存储
-- (可选) 使用TimescaleDB的数据节点功能

-- 方案1: 删除旧数据 (设置保留策略)
SELECT add_retention_policy('backtest_trades', INTERVAL '3 years');

-- 方案2: 导出到S3/OSS (使用pg_dump或timescaledb_toolkit)
```

### 7.4 缓存策略

#### 7.4.1 Redis热数据缓存

```python
# 缓存策略设计
CACHE_CONFIG = {
    # 实时行情数据 (5分钟过期)
    "stock_realtime": {
        "ttl": 300,
        "key_pattern": "rt:stock:{symbol}",
        "source": "akshare_adapter.get_real_time_data()"
    },

    # 策略信号 (1小时过期)
    "strategy_signal": {
        "ttl": 3600,
        "key_pattern": "signal:{strategy_id}:{symbol}",
        "source": "strategy_engine.get_latest_signal()"
    },

    # 技术指标 (1天过期)
    "technical_indicator": {
        "ttl": 86400,
        "key_pattern": "ind:{symbol}:{indicator}:{params_hash}",
        "source": "indicator_calculator.calculate()"
    }
}
```

---

## 总结

### 数据模型统计

- **总实体数**: 13个
- **PostgreSQL+TimescaleDB表**: 7个 (时序数据)
- **MySQL/MariaDB表**: 2个 (参考数据/元数据)
- **PostgreSQL表**: 1个 (汇总数据)
- **Redis缓存**: 3种类型

### Constitution合规性

✅ **Principle I**: 所有实体都明确分类到5-tier体系
✅ **Principle II**: 通过MyStocksUnifiedManager自动路由
✅ **Principle III**: 所有表结构将添加到table_config.yaml
✅ **Principle IV**: 数据适配器分离 (akshare_adapter + tqlex_adapter)
✅ **Principle V**: 所有操作自动记录到MonitoringDatabase
✅ **Principle VI**: 策略引擎使用工厂模式 (StrategyRegistry)
✅ **Principle VII**: MyStocksUnifiedManager作为统一访问层

### 下一步

- ✅ 数据模型设计完成
- ⏳ API合约设计 (contracts/)
- ⏳ 快速开始指南 (quickstart.md)
- ⏳ 更新Agent上下文

---

**Document Status**: ✅ Phase 1 - Data Model Design Completed
