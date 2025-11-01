# 量化交易数据管理完整方案

## 🎯 概述

基于您的NAS环境（PostgreSQL、Redis、MariaDB、MySQL、TDengine），设计了一套完整的量化交易数据管理方案，采用适配器模式和工厂模式，实现多数据库的统一管理和调用。

## 📊 数据分类体系

### 1. **市场行情数据 (Market Data)** → MySQL
```sql
-- 存储位置: MySQL (192.168.123.104:3306)
-- 数据库: market_db
├── stock_daily          -- 股票日线数据 (OHLCV)
├── index_daily          -- 指数日线数据
├── stock_info           -- 股票基本信息
└── trading_calendar     -- 交易日历
```

### 2. **基本面数据 (Fundamental Data)** → PostgreSQL
```sql
-- 存储位置: PostgreSQL (192.168.123.104:5433)  
-- 数据库: fundamental_db
├── financial_statements -- 财务报表
├── financial_indicators -- 财务指标 (PE/PB/ROE等)
├── company_info         -- 公司基本信息
└── corporate_actions    -- 公司行为 (分红配股)
```

### 3. **宏观经济数据 (Macro Data)** → PostgreSQL
```sql
-- 存储位置: PostgreSQL (192.168.123.104:5433)
-- 数据库: macro_db
├── economic_indicators  -- 经济指标 (GDP/CPI/PMI)
├── industry_data        -- 行业数据
└── policy_data          -- 政策数据
```

### 4. **实时数据 (Realtime Data)** → Redis
```redis
# 存储位置: Redis (192.168.123.104:6379)
├── realtime:stock:{symbol}     -- 股票实时行情
├── realtime:index:{symbol}     -- 指数实时数据
├── cache:popular:stocks        -- 热门股票缓存
└── cache:analysis:{key}        -- 分析结果缓存
```

### 5. **高频时序数据 (High-Frequency Data)** → TDengine
```sql
-- 存储位置: TDengine (192.168.123.104:6041)
-- 数据库: hf_market_db
├── minute_kline         -- 分钟级K线数据
├── tick_data           -- Tick级成交数据
├── money_flow          -- 资金流向数据
└── order_book          -- 委托单数据
```

### 6. **因子和策略数据 (Factor & Strategy)** → PostgreSQL + MySQL
```sql
-- 因子数据: PostgreSQL factor_db
├── technical_factors    -- 技术因子
├── fundamental_factors  -- 基本面因子
└── alternative_factors  -- 另类因子

-- 策略数据: MySQL strategy_db  
├── backtest_results     -- 回测结果
├── portfolio_holdings   -- 持仓记录
└── strategy_performance -- 策略表现
```

## 🗄️ 数据库选择原则

| 数据库 | 适用场景 | 数据特点 | 查询模式 |
|--------|----------|----------|----------|
| **PostgreSQL** | 复杂分析、OLAP | 关系型、低频更新 | 复杂查询、聚合分析 |
| **MySQL** | 核心业务、OLTP | 事务性、高并发 | 简单查询、快速读写 |
| **Redis** | 缓存、实时数据 | 内存型、高速 | 键值查询、实时访问 |
| **TDengine** | 时序数据、高频 | 时序型、压缩 | 时间范围查询 |
| **MariaDB** | 备用业务库 | 兼容MySQL | 备份、分流 |

## 🔧 数据管理API

### 核心管理器使用

```python
from quant_data_manager import QuantDataManager, DataCategory

# 初始化管理器
manager = QuantDataManager()

# 1. 根据数据分类自动保存到合适的数据库
success = manager.save_data_by_category(
    data=stock_df,                    # pandas DataFrame
    category=DataCategory.MARKET_DATA, # 自动选择MySQL
    table_name="stock_daily"
)

# 2. 根据分类自动从合适的数据库加载数据
data = manager.load_data_by_category(
    category=DataCategory.FUNDAMENTAL, # 自动从PostgreSQL查询
    table_name="financial_statements",
    filters={'symbol': '600000'}
)

# 3. 实时数据操作
manager.set_realtime_quote('600000', {
    'price': 10.50,
    'change_pct': 0.02,
    'volume': 1000000
})

quote = manager.get_realtime_quote('600000')

# 4. 缓存分析结果
manager.cache_analysis_result('factor_analysis_20250921', result_df)
cached_result = manager.get_cached_analysis_result('factor_analysis_20250921')
```

### 具体数据库操作

```python
# PostgreSQL - 复杂分析查询
pg_access = PostgreSQLDataAccess()
fundamental_data = pg_access.load_data(
    table_name="financial_indicators", 
    filters={'industry': '银行', 'roe': '>0.1'},
    database_name="fundamental_db"
)

# MySQL - 快速业务查询  
mysql_access = MySQLDataAccess()
market_data = mysql_access.load_data(
    table_name="stock_daily",
    filters={'symbol': '600000', 'date': '>2024-01-01'},
    database_name="market_db",
    limit=1000
)

# Redis - 实时数据缓存
redis_access = RedisDataAccess()
redis_access.set_realtime_data('hot:stocks', top_stocks_dict, expire=300)

# TDengine - 时序数据查询
td_access = TDengineDataAccess()
hf_data = td_access.load_timeseries_data(
    table_name="minute_kline",
    start_time="2024-09-21 09:30:00",
    end_time="2024-09-21 15:00:00"
)
```

## 🚀 实施建议

### 1. **数据采集优先级**

**第一阶段：核心数据**
```python
# 1. 股票基本信息和日线数据 → MySQL
symbols = ['600000', '000001', '000002']  # 核心股票池
collect_daily_data(symbols, '2023-01-01', '2024-09-21')

# 2. 实时行情数据 → Redis  
setup_realtime_data_collection(symbols, interval=60)  # 每分钟更新
```

**第二阶段：分析数据**
```python
# 3. 财务数据 → PostgreSQL
collect_fundamental_data(symbols, years=[2021, 2022, 2023])

# 4. 技术因子计算 → PostgreSQL
calculate_technical_factors(symbols)
```

**第三阶段：高频数据**
```python
# 5. 分钟级数据 → TDengine
collect_minute_data(symbols, days=30)

# 6. 资金流向数据 → TDengine  
collect_money_flow_data(symbols)
```

### 2. **性能优化策略**

**数据分区策略**
```sql
-- MySQL: 按日期分区
CREATE TABLE stock_daily (
    id BIGINT AUTO_INCREMENT,
    symbol VARCHAR(10),
    date DATE,
    -- 其他字段...
    PRIMARY KEY (id, date)
) PARTITION BY RANGE (YEAR(date)) (
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026)
);

-- PostgreSQL: 按股票代码分区
CREATE TABLE financial_statements (
    symbol VARCHAR(10),
    report_date DATE,
    -- 其他字段...
) PARTITION BY HASH (symbol);
```

**缓存策略**
```python
# 热点数据缓存
CACHE_CONFIG = {
    'realtime_quotes': 60,      # 实时行情缓存60秒
    'daily_data': 3600,         # 日线数据缓存1小时  
    'analysis_results': 7200,   # 分析结果缓存2小时
    'factor_values': 1800       # 因子值缓存30分钟
}
```

### 3. **数据质量控制**

**数据验证规则**
```python
DATA_VALIDATION_RULES = {
    'stock_daily': {
        'required_columns': ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume'],
        'data_types': {'open': 'float', 'volume': 'int'},
        'value_ranges': {'close': (0, 10000), 'volume': (0, float('inf'))}
    },
    'financial_statements': {
        'required_columns': ['symbol', 'report_date', 'revenue', 'net_income'],
        'completeness_threshold': 0.8  # 80%字段完整性要求
    }
}
```

### 4. **监控和告警**

**系统监控指标**
```python
MONITORING_METRICS = {
    'data_freshness': {
        'realtime_data': 120,      # 实时数据超过2分钟告警
        'daily_data': 86400,       # 日线数据超过1天告警
    },
    'database_performance': {
        'query_timeout': 30,       # 查询超时30秒告警
        'connection_pool': 0.8     # 连接池使用率超过80%告警
    },
    'data_quality': {
        'missing_rate': 0.05,      # 数据缺失率超过5%告警
        'anomaly_detection': True   # 异常值检测
    }
}
```

## 📱 Navicat集中管理配置

### 连接配置建议

**1. PostgreSQL连接**
```
名称: MyStocks-PostgreSQL-Analysis
主机: 192.168.123.104
端口: 5433
用户: paperless
密码: paperless
数据库: fundamental_db, macro_db, factor_db
```

**2. MySQL连接**
```
名称: MyStocks-MySQL-Market  
主机: 192.168.123.104
端口: 3306
用户: root
密码: c790414J
数据库: market_db, strategy_db, system_db
```

**3. MariaDB连接（备用）**
```
名称: MyStocks-MariaDB-Backup
主机: 192.168.123.104  
端口: 3307
用户: root
密码: c790414J
```

### Navicat使用建议

**1. 数据库分组管理**
- 📊 量化分析组: PostgreSQL连接
- 💹 市场数据组: MySQL连接  
- ⚡ 实时数据组: Redis连接
- 📈 备份数据组: MariaDB连接

**2. 常用查询收藏**
```sql
-- 查询股票池表现
SELECT symbol, 
       AVG(close) as avg_price,
       STDDEV(close) as volatility,
       COUNT(*) as trading_days
FROM market_db.stock_daily 
WHERE date >= '2024-01-01'
GROUP BY symbol;

-- 查询财务指标排名
SELECT symbol, company_name, roe, pe_ratio
FROM fundamental_db.financial_indicators 
WHERE report_date = (SELECT MAX(report_date) FROM fundamental_db.financial_indicators)
ORDER BY roe DESC LIMIT 50;
```

**3. 数据同步任务**
- 每日同步: market_db → mariadb (备份)
- 每周同步: fundamental_db → 本地文件
- 实时监控: 关键表数据量变化

## 🎯 使用流程总结

### 完整工作流程

```python
# 1. 初始化系统
from quant_trading_pipeline import QuantTradingDataPipeline
pipeline = QuantTradingDataPipeline()

# 2. 设置数据库结构
pipeline.setup_databases()

# 3. 数据采集存储
symbols = ['600000', '000001', '000002']
pipeline.collect_and_store_market_data(symbols, '2024-01-01', '2024-09-21')
pipeline.collect_and_store_fundamental_data(symbols)
pipeline.collect_and_store_realtime_data(symbols)

# 4. 因子计算
pipeline.calculate_and_store_factors(symbols)

# 5. 策略回测
pipeline.run_backtest_and_store_results("MyStrategy", symbols)

# 6. 数据查询分析
pipeline.query_data_examples()
```

### 日常调用模式

```python
from quant_data_manager import QuantDataManager, DataCategory

manager = QuantDataManager()

# 快速获取数据
realtime_price = manager.get_realtime_quote('600000')
daily_data = manager.load_data_by_category(DataCategory.MARKET_DATA, "stock_daily")
factors = manager.load_data_by_category(DataCategory.FACTOR_SIGNAL, "technical_factors")

# 快速保存结果
manager.save_data_by_category(analysis_result, DataCategory.STRATEGY_PORTFOLIO, "my_analysis")
```

## 🎉 总结

这套方案为您提供了：

1. **🎯 明确的数据分类**: 6大类数据，各有专属存储策略
2. **🗄️ 合理的数据库分配**: 基于数据特性选择最适合的存储方案  
3. **🔧 统一的访问接口**: 适配器+工厂模式，屏蔽底层差异
4. **⚡ 高效的查询模式**: 缓存+分区+索引优化
5. **📱 便捷的管理工具**: 与Navicat无缝集成
6. **🚀 完整的实施方案**: 从数据采集到分析的全流程

现在您可以通过`python quant_trading_pipeline.py`开始体验完整的量化数据管理流程！