# TDX数据获取清单

**生成时间**: 2026-01-02
**版本**: v2.1.0
**数据源**: 通达信(TDX)
**适配器版本**: 2.1.0

---

## 🔗 相关文档

本文档列出了当前MyStocks项目已实现的TDX功能。如需了解PyTDX的完整功能和增强计划,请参阅:

- **[TDX功能增强计划](./TDX_ENHANCEMENT_PLAN.md)** - 详细的取长补短实施方案
- **[TDX功能对比快速参考](./TDX_COMPARISON_QUICK_REFERENCE.md)** - PyTDX vs MyStocks 快速对比
- **PyTDX参考文档**: `/opt/iflow/tdxpy/data_catalog.md` - PyTDX完整功能清单

**快速摘要**:
- ✅ **已实现**: 11种数据类型 (实时行情、6种K线周期、本地文件读取)
- ❌ **待增强**: 6大功能模块 (财务数据、除权除息、公司信息、板块数据、分时数据、分笔成交)
- 📈 **覆盖率**: 当前30% → 目标95% (详见增强计划)

---

## 📊 数据获取总览

| 数据类别 | 数据类型 | 支持状态 | 数据来源 | 保存数据库 |
|---------|---------|---------|---------|-----------|
| **实时行情** | 实时报价 | ✅ 完全支持 | TDX服务器 | PostgreSQL |
| **实时行情** | 实时快照 | ✅ 完全支持 | TDX服务器 | PostgreSQL |
| **历史K线** | 日线数据 | ✅ 完全支持 | TDX服务器 | PostgreSQL + TimescaleDB |
| **历史K线** | 指数日线 | ✅ 完全支持 | TDX服务器 | PostgreSQL + TimescaleDB |
| **历史K线** | 1分钟K线 | ✅ 完全支持 | TDX服务器 | TDengine |
| **历史K线** | 5分钟K线 | ✅ 完全支持 | TDX服务器 | TDengine |
| **历史K线** | 15分钟K线 | ✅ 完全支持 | TDX服务器 | TDengine |
| **历史K线** | 30分钟K线 | ✅ 完全支持 | TDX服务器 | TDengine |
| **历史K线** | 1小时K线 | ✅ 完全支持 | TDX服务器 | TDengine |
| **本地文件** | 日线数据 | ✅ 完全支持 | 本地.day文件 | TDengine |
| **本地文件** | 5分钟数据 | ✅ 完全支持 | 本地.lc5文件 | TDengine |
| **本地文件** | 1分钟数据 | ✅ 完全支持 | 本地.lc1文件 | TDengine |
| **基本信息** | 股票信息 | ⚠️ 有限支持 | 从日线推导 | PostgreSQL |
| **参考数据** | 指数成分股 | ❌ 不支持 | - | - |
| **财务数据** | 财务报表 | ❌ 不支持 | - | - |
| **市场数据** | 交易日历 | ❌ 不支持 | - | - |
| **市场数据** | 新闻数据 | ❌ 不支持 | - | - |
| **分类数据** | 行业分类 | ❌ 不支持 | - | - |
| **分类数据** | 概念分类 | ❌ 不支持 | - | - |

---

## 1️⃣ 实时行情数据

### 1.1 实时报价 (Real-time Quotes)

| 项目 | 说明 |
|------|------|
| **方法名** | `get_real_time_data(symbol: str)` |
| **脚本位置** | `src/adapters/tdx_adapter.py:648` |
| **数据来源** | TDX服务器 (实时连接) |
| **数据类型** | 实时快照数据 |
| **信息类别** | 实时行情 (REALTIME_QUOTES) |
| **支持市场** | 上海(sh)、深圳(sz) |
| **更新频率** | 实时 (毫秒级延迟) |
| **目标数据库** | PostgreSQL (表名: `realtime_quotes`) |

**返回数据字段**:
```python
{
    'code': str,           # 股票代码 (6位)
    'name': str,           # 股票名称
    'price': float,        # 最新价
    'pre_close': float,    # 昨收价
    'open': float,         # 今开价
    'high': float,         # 最高价
    'low': float,          # 最低价
    'volume': int,         # 成交量(手)
    'amount': float,       # 成交额(元)
    'bid1': float,         # 买一价
    'bid1_volume': int,    # 买一量
    'ask1': float,         # 卖一价
    'ask1_volume': int,    # 卖一量
    'timestamp': str       # 查询时间戳
}
```

**使用示例**:
```python
from src.adapters.tdx_adapter import TdxDataSource

tdx = TdxDataSource()
quote = tdx.get_real_time_data('600519')
print(f"股票名称: {quote['name']}")
print(f"最新价: {quote['price']:.2f}")
print(f"涨跌幅: {((quote['price']/quote['pre_close']-1)*100):.2f}%")
```

**特性**:
- ✅ 自动重试机制 (最多3次)
- ✅ 服务器故障转移
- ✅ 数据验证和清洗
- ✅ 毫秒级延迟

---

## 2️⃣ 历史K线数据

### 2.1 股票日线数据

| 项目 | 说明 |
|------|------|
| **方法名** | `get_stock_daily(symbol, start_date, end_date)` |
| **脚本位置** | `src/adapters/tdx_adapter.py:278` |
| **数据来源** | TDX服务器 (在线查询) |
| **数据类型** | 历史日线数据 |
| **信息类别** | 日线K线 (DAILY_KLINE) |
| **支持市场** | 上海(sh)、深圳(sz) |
| **时间范围** | 最多约40年 (分页获取,每批800条) |
| **目标数据库** | PostgreSQL + TimescaleDB (表名: `stock_daily`) |

**返回数据字段**:
```python
pd.DataFrame(columns=[
    'date',     # 交易日期 (YYYY-MM-DD)
    'open',     # 开盘价
    'high',     # 最高价
    'low',      # 最低价
    'close',    # 收盘价
    'volume',   # 成交量(手)
    'amount'    # 成交额(元)
])
```

**使用示例**:
```python
from src.adapters.tdx_adapter import TdxDataSource

tdx = TdxDataSource()
df = tdx.get_stock_daily('600519', '2024-01-01', '2024-12-31')
print(f"获取数据: {len(df)}条")
print(df.head())
```

**数据验证**:
- ✅ 必需列检查
- ✅ 价格非负验证
- ✅ 成交量非负验证
- ✅ OHLC逻辑检查

---

### 2.2 指数日线数据

| 项目 | 说明 |
|------|------|
| **方法名** | `get_index_daily(symbol, start_date, end_date)` |
| **脚本位置** | `src/adapters/tdx_adapter.py:430` |
| **数据来源** | TDX服务器 (在线查询) |
| **数据类型** | 指数历史日线数据 |
| **信息类别** | 日线K线 (DAILY_KLINE) |
| **支持市场** | 上证指数(000xxx)、深证指数(399xxx) |
| **目标数据库** | PostgreSQL + TimescaleDB (表名: `index_daily`) |

**常用指数代码**:
- `000001` - 上证指数
- `399001` - 深证成指
- `399006` - 创业板指

**返回数据字段**: 同股票日线

---

### 2.3 多周期K线数据

| 项目 | 说明 |
|------|------|
| **方法名** | `get_stock_kline(symbol, start_date, end_date, period)` |
| **脚本位置** | `src/adapters/tdx_adapter.py:811` |
| **数据来源** | TDX服务器 (在线查询) |
| **数据类型** | 多周期K线数据 |
| **信息类别** | 分钟K线 (MINUTE_KLINE) 或 日线K线 (DAILY_KLINE) |
| **支持周期** | 1m, 5m, 15m, 30m, 1h, 1d |
| **目标数据库** | TDengine (分钟线) / PostgreSQL (日线) |

**周期参数映射**:
```python
period_map = {
    '1m':  8,   # 1分钟
    '5m':  0,   # 5分钟
    '15m': 1,   # 15分钟
    '30m': 2,   # 30分钟
    '1h':  3,   # 1小时
    '1d':  9    # 日线
}
```

**使用示例**:
```python
from src.adapters.tdx_adapter import TdxDataSource

tdx = TdxDataSource()

# 获取5分钟K线
df_5m = tdx.get_stock_kline('600519', '2024-01-01', '2024-01-31', period='5m')
print(f"5分钟K线: {len(df_5m)}条")

# 获取1小时K线
df_1h = tdx.get_stock_kline('600519', '2024-01-01', '2024-01-31', period='1h')
print(f"1小时K线: {len(df_1h)}条")
```

**返回数据字段**:
```python
pd.DataFrame(columns=[
    'date',     # 日期时间 (YYYY-MM-DD HH:MM:SS)
    'open',     # 开盘价
    'high',     # 最高价
    'low',      # 最低价
    'close',    # 收盘价
    'volume',   # 成交量
    'amount'    # 成交额
])
```

---

### 2.4 指数多周期K线

| 项目 | 说明 |
|------|------|
| **方法名** | `get_index_kline(symbol, start_date, end_date, period)` |
| **脚本位置** | `src/adapters/tdx_adapter.py:941` |
| **数据来源** | TDX服务器 (在线查询) |
| **数据类型** | 指数多周期K线数据 |
| **信息类别** | 分钟K线或日线K线 |
| **支持周期** | 1m, 5m, 15m, 30m, 1h, 1d |
| **目标数据库** | TDengine (分钟线) / PostgreSQL (日线) |

---

## 3️⃣ 本地二进制文件数据

### 3.1 日线数据文件

| 项目 | 说明 |
|------|------|
| **方法名** | `read_day_file(file_path)` 或 `TdxBinaryParser.read_day_data()` |
| **脚本位置** | `src/adapters/tdx_adapter.py:1046` / `src/data_sources/tdx_binary_parser.py` |
| **数据来源** | 本地.day文件 |
| **数据类型** | 历史日线数据 (离线) |
| **信息类别** | 日线K线 (DAILY_KLINE) |
| **文件格式** | 二进制,每条记录32字节 |
| **文件路径** | `{TDX_DATA_PATH}/sh/lday/` 或 `{TDX_DATA_PATH}/sz/lday/` |
| **目标数据库** | TDengine (表名: `stock_daily`) |

**文件格式说明**:
```
每条记录32字节:
- date (4字节): YYYYMMDD格式的整数
- open (4字节): 开盘价×1000
- high (4字节): 最高价×1000
- low (4字节): 最低价×1000
- close (4字节): 收盘价×1000
- amount (4字节): 成交金额(元)
- volume (4字节): 成交量(手)
- reserved (4字节): 保留字段
```

**使用示例**:
```python
from src.data_sources.tdx_binary_parser import TdxBinaryParser

parser = TdxBinaryParser()
data = parser.read_day_data('600519', start_date=date(2024, 1, 1))
print(f"读取数据: {len(data)}条")
print(data.head())
```

**返回数据字段**:
```python
pd.DataFrame(columns=[
    'date',     # 交易日期 (datetime)
    'open',     # 开盘价
    'high',     # 最高价
    'low',      # 最低价
    'close',    # 收盘价
    'volume',   # 成交量(手)
    'amount'    # 成交额(元)
])
```

---

### 3.2 5分钟数据文件

| 项目 | 说明 |
|------|------|
| **方法名** | `TdxBinaryParser.read_5min_data()` |
| **脚本位置** | `src/data_sources/tdx_binary_parser.py:136` |
| **数据来源** | 本地.lc5文件 |
| **数据类型** | 5分钟K线数据 (离线) |
| **信息类别** | 5分钟K线 (MARKET_DATA_MIN5) |
| **文件格式** | 二进制,每条记录32字节 |
| **文件路径** | `{TDX_DATA_PATH}/sh/fzline/` 或 `{TDX_DATA_PATH}/sz/fzline/` |
| **目标数据库** | TDengine (表名: `stock_5min`) |

**使用示例**:
```python
from src.data_sources.tdx_binary_parser import TdxBinaryParser

parser = TdxBinaryParser()
data = parser.read_5min_data('600519', start_date=date(2024, 1, 1))
print(f"读取5分钟数据: {len(data)}条")
```

---

### 3.3 1分钟数据文件

| 项目 | 说明 |
|------|------|
| **方法名** | `TdxBinaryParser.read_1min_data()` |
| **脚本位置** | `src/data_sources/tdx_binary_parser.py:179` |
| **数据来源** | 本地.lc1文件 |
| **数据类型** | 1分钟K线数据 (离线) |
| **信息类别** | 1分钟K线 (MARKET_DATA_MIN1) |
| **文件格式** | 二进制,每条记录32字节 |
| **文件路径** | `{TDX_DATA_PATH}/sh/minline/` 或 `{TDX_DATA_PATH}/sz/minline/` |
| **目标数据库** | TDengine (表名: `stock_1min`) |

---

## 4️⃣ 批量导入功能

### 4.1 增量导入器

| 项目 | 说明 |
|------|------|
| **类名** | `TdxImporter` |
| **脚本位置** | `src/data_sources/tdx_importer.py` |
| **功能** | 批量导入TDX本地数据到数据库 |
| **支持数据** | 日线、5分钟、1分钟 |
| **特性** | ✅ 断点续传<br>✅ 增量更新<br>✅ 批量处理<br>✅ 进度跟踪 |

**使用示例**:
```python
from unified_manager import MyStocksUnifiedManager
from src.data_sources.tdx_importer import TdxImporter
from datetime import date

# 创建统一管理器
manager = MyStocksUnifiedManager()

# 创建导入器
importer = TdxImporter(unified_manager=manager)

# 全量导入
result = importer.import_market_daily(
    market='sh',
    start_date=date(2024, 1, 1),
    batch_size=100
)

# 增量导入 (最近7天)
result = importer.import_incremental(
    market='sh',
    lookback_days=7
)

print(f"成功导入: {result['success_count']}只股票")
print(f"总记录数: {result['total_records']:,}")
```

**导入性能**:
- 单只股票日线(1年): ~0.01秒
- 批量100只股票: ~10秒
- 全市场5000只股票: ~500秒(约8分钟)

---

## 5️⃣ 辅助功能

### 5.1 股票基本信息

| 项目 | 说明 |
|------|------|
| **方法名** | `get_stock_basic(symbol)` |
| **脚本位置** | `src/adapters/tdx_adapter.py:585` |
| **支持状态** | ⚠️ 有限支持 (从日线数据推导) |
| **数据来源** | 推导数据 |

**返回数据字段**:
```python
{
    'symbol': str,       # 股票代码
    'name': str,         # 股票名称
    'market': str,       # 市场 (SH/SZ)
    'category': str,     # 类别 (stock)
    'status': str,       # 交易状态
    'list_date': str,    # 上市日期
    'total_shares': None, # 总股本 (不支持)
    'float_shares': None  # 流通股本 (不支持)
}
```

---

### 5.2 列出可用股票

| 项目 | 说明 |
|------|------|
| **方法名** | `list_available_stocks(market)` |
| **脚本位置** | `src/data_sources/tdx_binary_parser.py:222` |
| **功能** | 列出指定市场的所有股票 |
| **支持市场** | sh, sz |

**使用示例**:
```python
from src.data_sources.tdx_binary_parser import TdxBinaryParser

parser = TdxBinaryParser()
stocks = parser.list_available_stocks('sh')
print(f"上海市场共 {len(stocks)} 只股票")
print(f"前5只: {stocks[:5]}")
```

---

## 6️⃣ 不支持的数据类型

### 6.1 财务数据

| 项目 | 说明 |
|------|------|
| **方法名** | `get_financial_data(symbol, period)` |
| **支持状态** | ❌ 不支持 (返回空DataFrame) |
| **建议** | 使用AkShare或Tushare适配器 |

---

### 6.2 交易日历

| 项目 | 说明 |
|------|------|
| **方法名** | `get_market_calendar(start_date, end_date)` |
| **支持状态** | ❌ 不支持 (返回空DataFrame) |
| **建议** | 使用AkShare适配器 |

---

### 6.3 新闻数据

| 项目 | 说明 |
|------|------|
| **方法名** | `get_news_data(symbol, limit)` |
| **支持状态** | ❌ 不支持 (返回空列表) |
| **建议** | 使用其他数据源 |

---

### 6.4 指数成分股

| 项目 | 说明 |
|------|------|
| **方法名** | `get_index_components(symbol)` |
| **支持状态** | ❌ 不支持 (返回空列表) |
| **建议** | 使用AkShare或Tushare适配器 |

---

### 6.5 行业/概念分类

| 项目 | 说明 |
|------|------|
| **方法名** | `get_industry_classify()`, `get_concept_classify()`, `get_stock_industry_concept()` |
| **支持状态** | ❌ 不支持 (返回空数据) |
| **建议** | 使用AkShare适配器 |

---

## 7️⃣ 数据路由说明

所有TDX数据通过系统的5-tier数据分类自动路由到最优数据库:

### 7.1 数据分类映射

| 数据分类 | 分类枚举 | 目标数据库 | 压缩比 | 说明 |
|---------|---------|-----------|-------|------|
| 日线K线 | DAILY_KLINE | PostgreSQL + TimescaleDB | 5:1 | 长期存储,时序优化 |
| 分钟K线 | MINUTE_KLINE | TDengine | 20:1 | 高频数据,极致压缩 |
| 实时行情 | REALTIME_QUOTES | PostgreSQL | - | 快速读写,事务保证 |
| Tick数据 | TICK_DATA | TDengine | 20:1 | 超高频,原始数据 |

### 7.2 数据保存示例

```python
from unified_manager import MyStocksUnifiedManager
from src.core import DataClassification

manager = MyStocksUnifiedManager()

# 保存实时行情 → PostgreSQL
manager.save_data_by_classification(
    classification=DataClassification.REALTIME_QUOTES,
    data=quote_df,
    table_name='realtime_quotes'
)

# 保存日线数据 → PostgreSQL + TimescaleDB
manager.save_data_by_classification(
    classification=DataClassification.DAILY_KLINE,
    data=daily_df,
    table_name='stock_daily'
)

# 保存分钟K线 → TDengine
manager.save_data_by_classification(
    classification=DataClassification.MINUTE_KLINE,
    data=min5_df,
    table_name='stock_5min'
)
```

---

## 8️⃣ 性能特性

### 8.1 连接管理

- ✅ **自动重试**: 最多3次重试,指数退避
- ✅ **服务器切换**: 支持connect.cfg配置,自动故障转移
- ✅ **连接池**: 高效复用连接
- ✅ **超时控制**: 默认10秒超时

### 8.2 数据验证

- ✅ **必需列检查**: 确保数据完整性
- ✅ **价格非负**: 自动修正负值
- ✅ **成交量非负**: 自动修正负值
- ✅ **OHLC逻辑**: 检查高低价关系

### 8.3 性能指标

| 操作 | 性能 |
|------|------|
| 实时行情查询 | < 100ms |
| 单只股票日线(1年) | ~0.01秒 |
| 批量100只股票 | ~10秒 |
| 本地文件读取(1年日线) | ~0.005秒 |

---

## 9️⃣ 配置说明

### 9.1 环境变量

```bash
# TDX数据路径 (本地文件)
TDX_DATA_PATH=/mnt/d/ProgramData/tdx_new/vipdoc

# TDX服务器配置 (在线查询)
TDX_SERVER_HOST=101.227.73.20
TDX_SERVER_PORT=7709
TDX_MAX_RETRIES=3
TDX_RETRY_DELAY=1
TDX_API_TIMEOUT=10
```

### 9.2 服务器配置

从`connect.cfg`文件加载服务器列表,支持:
- 主服务器配置
- 备用服务器配置
- 自动故障转移

---

## 🔟 快速参考

### 10.1 完整工作流程示例

```python
from src.adapters.tdx_adapter import TdxDataSource
from unified_manager import MyStocksUnifiedManager
from src.core import DataClassification
from datetime import date

# 1. 创建TDX数据源
tdx = TdxDataSource()

# 2. 获取实时行情
quote = tdx.get_real_time_data('600519')
print(f"实时价格: {quote['price']:.2f}")

# 3. 获取历史日线
df_daily = tdx.get_stock_daily('600519', '2024-01-01', '2024-12-31')
print(f"历史日线: {len(df_daily)}条")

# 4. 获取5分钟K线
df_5min = tdx.get_stock_kline('600519', '2024-01-01', '2024-01-31', period='5m')
print(f"5分钟K线: {len(df_5min)}条")

# 5. 保存到数据库 (自动路由)
manager = MyStocksUnifiedManager()

# 实时行情 → PostgreSQL
manager.save_data_by_classification(
    DataClassification.REALTIME_QUOTES,
    pd.DataFrame([quote]),
    'realtime_quotes'
)

# 日线数据 → PostgreSQL + TimescaleDB
manager.save_data_by_classification(
    DataClassification.DAILY_KLINE,
    df_daily,
    'stock_daily'
)

# 分钟数据 → TDengine
manager.save_data_by_classification(
    DataClassification.MINUTE_KLINE,
    df_5min,
    'stock_5min'
)
```

### 10.2 脚本位置汇总

| 功能 | 脚本位置 |
|------|---------|
| TDX适配器 | `src/adapters/tdx_adapter.py` |
| 二进制解析器 | `src/data_sources/tdx_binary_parser.py` |
| 增量导入器 | `src/data_sources/tdx_importer.py` |
| 统一管理器 | `src/core/unified_manager.py` |
| 数据分类 | `src/core/__init__.py` |
| 接口定义 | `src/interfaces/data_source.py` |

---

## 📝 总结

### 支持的数据类型 (11种)

1. ✅ **实时报价** - 毫秒级延迟
2. ✅ **股票日线** - 约40年历史
3. ✅ **指数日线** - 主要指数
4. ✅ **1分钟K线** - 在线查询
5. ✅ **5分钟K线** - 在线查询
6. ✅ **15分钟K线** - 在线查询
7. ✅ **30分钟K线** - 在线查询
8. ✅ **1小时K线** - 在线查询
9. ✅ **本地日线** - 离线文件
10. ✅ **本地5分钟** - 离线文件
11. ✅ **本地1分钟** - 离线文件

### 不支持的数据类型 (6种)

1. ❌ 财务数据 (使用AkShare)
2. ❌ 交易日历 (使用AkShare)
3. ❌ 新闻数据 (使用其他源)
4. ❌ 指数成分股 (使用AkShare/Tushare)
5. ❌ 行业分类 (使用AkShare)
6. ❌ 概念分类 (使用AkShare)

### 核心优势

- 🚀 **极速响应**: 实时行情毫秒级延迟
- 📡 **直连服务器**: 无API限流
- 🔄 **智能重试**: 自动故障转移
- 📊 **多周期支持**: 1m到1d全周期覆盖
- 💾 **双数据库优化**: 自动路由到最优数据库
- ✅ **数据验证**: 完整的数据质量检查

---

**文档维护**: MyStocks项目组
**最后更新**: 2026-01-02
**相关文档**:
- `docs/architecture/DATASOURCE_AND_DATABASE_ARCHITECTURE.md`
- `src/data_sources/README_TDX.md`
- `CLAUDE.md`
