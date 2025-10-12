# ByapiAdapter 使用文档

**数据源**: biyingapi.com
**适配器版本**: 1.0.0
**创建日期**: 2025-10-11
**License**: 04C01BF1-7F2F-41A3-B470-1F81F14B1FC8

---

## 概述

`ByapiAdapter` 是 MyStocks 系统中用于访问 biyingapi.com 数据源的适配器,实现了标准的 `IDataSource` 接口。该适配器专注于中国A股市场数据,提供实时行情、历史K线、财务报表等全面的金融数据。

### 业务范围

✅ **支持**: A股(必要)、港股(可选)、股指期货
❌ **不支持**: 商品期货、期权、外汇、黄金、美股(非港股的海外市场)

### 特点

✅ **完整的IDataSource接口实现** - 符合MyStocks统一数据源标准
✅ **A股市场全覆盖** - 支持上交所和深交所所有股票
✅ **多维度数据** - 实时行情、历史K线、财务报表、技术指标
✅ **内置频率控制** - 自动控制API请求频率(300次/分钟)
✅ **自动错误处理** - 统一的异常类型和友好的错误消息
✅ **标准化输出** - 所有DataFrame输出符合MyStocks列名规范

---

## 快速开始

### 1. 安装依赖

```bash
pip install pandas requests
```

### 2. 基础使用

```python
from adapters.byapi_adapter import ByapiAdapter

# 初始化适配器 (使用提供的license)
adapter = ByapiAdapter(
    licence="04C01BF1-7F2F-41A3-B470-1F81F14B1FC8"
)

# 获取股票列表
stocks = adapter.get_stock_list()
print(f"共 {len(stocks)} 只股票")

# 获取日线数据
kline = adapter.get_kline_data(
    symbol='000001.SZ',
    start_date='2025-09-01',
    end_date='2025-10-11',
    frequency='daily'
)
print(kline)

# 获取实时行情
quotes = adapter.get_realtime_quotes(['000001.SZ', '600000.SH'])
print(quotes[['symbol', 'current_price', 'change_pct']])
```

---

## API 方法详解

### get_stock_list()

获取所有A股股票列表。

**返回**: DataFrame

| 列名 | 类型 | 说明 |
|------|------|------|
| symbol | str | 股票代码 (如 '000001.SZ') |
| name | str | 股票名称 (如 '平安银行') |
| exchange | str | 交易所 (SSE/SZSE) |
| list_date | datetime | 上市日期 (byapi不提供,返回NaT) |
| status | str | 状态 (固定为 'ACTIVE') |

**示例**:

```python
stocks = adapter.get_stock_list()
# 筛选上交所股票
sse_stocks = stocks[stocks['exchange'] == 'SSE']
print(f"上交所: {len(sse_stocks)} 只")
```

---

### get_kline_data()

获取K线数据 (日线/分钟线等)。

**参数**:

- `symbol` (str): 股票代码 (如 '600000.SH' 或 '600000')
- `start_date` (str): 开始日期 (YYYY-MM-DD)
- `end_date` (str): 结束日期 (YYYY-MM-DD)
- `frequency` (str): 频率
  - `"daily"`: 日线 (默认)
  - `"5min"`: 5分钟线
  - `"15min"`: 15分钟线
  - `"30min"`: 30分钟线
  - `"60min"`: 60分钟线
  - `"weekly"`: 周线
  - `"monthly"`: 月线
  - `"yearly"`: 年线

**返回**: DataFrame

日线数据列:

| 列名 | 类型 | 说明 |
|------|------|------|
| symbol | str | 股票代码 |
| date | datetime | 交易日期 (UTC时区) |
| open | float | 开盘价 |
| high | float | 最高价 |
| low | float | 最低价 |
| close | float | 收盘价 |
| volume | float | 成交量 |
| amount | float | 成交额 |

分钟线数据列: 与日线相同,但 `date` 替换为 `timestamp`

**示例**:

```python
# 获取近3个月日线数据
daily = adapter.get_kline_data(
    symbol='000001.SZ',
    start_date='2025-07-01',
    end_date='2025-10-11',
    frequency='daily'
)

# 获取5分钟线数据
minute5 = adapter.get_kline_data(
    symbol='600000.SH',
    start_date='2025-10-10',
    end_date='2025-10-11',
    frequency='5min'
)
```

---

### get_realtime_quotes()

获取实时行情数据。

**参数**:

- `symbols` (List[str]): 股票代码列表 (如 ['600000.SH', '000001.SZ'])

**返回**: DataFrame

| 列名 | 类型 | 说明 |
|------|------|------|
| symbol | str | 股票代码 |
| name | str | 股票名称 (byapi不提供,返回空字符串) |
| current_price | float | 当前价 |
| change | float | 涨跌额 |
| change_pct | float | 涨跌幅 (%) |
| open | float | 今开 |
| high | float | 最高 |
| low | float | 最低 |
| pre_close | float | 昨收 |
| volume | int | 成交量 |
| amount | float | 成交额 |
| bid_price_1 | float | 买一价 (byapi需单独接口,返回0.0) |
| ask_price_1 | float | 卖一价 (byapi需单独接口,返回0.0) |
| timestamp | datetime | 行情时间 (UTC) |
| turnover_rate | float | 换手率 (%) |

**示例**:

```python
# 获取多只股票实时行情
quotes = adapter.get_realtime_quotes([
    '000001.SZ',  # 平安银行
    '600000.SH',  # 浦发银行
    '600519.SH'   # 贵州茅台
])

# 查看涨幅排序
quotes_sorted = quotes.sort_values('change_pct', ascending=False)
print(quotes_sorted[['symbol', 'current_price', 'change_pct']])
```

---

### get_fundamental_data()

获取财务数据。

**参数**:

- `symbol` (str): 股票代码
- `report_period` (str): 报告期
  - 'YYYY-MM-DD' 格式: 获取指定日期的财报
  - 'latest': 获取最新一期财报
- `data_type` (str): 数据类型
  - `"income"`: 利润表 (默认)
  - `"balance"`: 资产负债表
  - `"cashflow"`: 现金流量表
  - `"metrics"`: 财务指标

**返回**: DataFrame (列名根据data_type不同)

**利润表 (income) 关键列**:

| 列名 | 说明 | 字段名 |
|------|------|--------|
| 截止日期 | jzrq | 报告期 |
| 营业收入 | yysr | 总收入 |
| 营业成本 | yycb | 总成本 |
| 净利润 | jlr | 归属母公司净利润 |
| 基本每股收益 | jbmgsy | EPS |

**资产负债表 (balance) 关键列**:

| 列名 | 说明 | 字段名 |
|------|------|--------|
| 资产总计 | zczj | 总资产 |
| 负债合计 | fzhj | 总负债 |
| 所有者权益合计 | syzqyhj | 净资产 |

**现金流量表 (cashflow) 关键列**:

| 列名 | 说明 | 字段名 |
|------|------|--------|
| 经营活动产生的现金流量净额 | jyhdcsdxjlje | 经营现金流 |
| 投资活动产生的现金流量净额 | tzhdcsdxjlxj | 投资现金流 |
| 筹资活动产生的现金流量净额 | czhdcsdxjlxj | 筹资现金流 |

**财务指标 (metrics) 关键列**:

| 列名 | 说明 | 字段名 |
|------|------|--------|
| 净资产收益率 | jzcsyl | ROE |
| 每股净资产 | mgjzc | BVPS |
| 销售毛利率 | xsmlv | Gross Margin |

**示例**:

```python
# 获取最新利润表
income = adapter.get_fundamental_data(
    symbol='000001.SZ',
    report_period='latest',
    data_type='income'
)

if not income.empty:
    latest = income.iloc[0]
    print(f"报告期: {latest['jzrq']}")
    print(f"营业收入: {latest['yysr']:,.0f} 元")
    print(f"净利润: {latest['jlr']:,.0f} 元")

# 获取指定日期的资产负债表
balance = adapter.get_fundamental_data(
    symbol='600000.SH',
    report_period='2025-06-30',
    data_type='balance'
)

# 获取财务指标
metrics = adapter.get_fundamental_data(
    symbol='600519.SH',
    report_period='latest',
    data_type='metrics'
)
```

---

## 扩展功能 (byapi特有)

### get_limit_up_stocks()

获取指定日期的涨停股池。

**参数**:
- `trade_date` (str): 交易日期 (YYYY-MM-DD)

**返回**: DataFrame 包含涨停股票列表

**示例**:

```python
limit_up = adapter.get_limit_up_stocks('2025-10-10')
print(f"涨停股票: {len(limit_up)} 只")
```

---

### get_limit_down_stocks()

获取指定日期的跌停股池。

**参数**:
- `trade_date` (str): 交易日期 (YYYY-MM-DD)

**返回**: DataFrame 包含跌停股票列表

**示例**:

```python
limit_down = adapter.get_limit_down_stocks('2025-10-10')
print(f"跌停股票: {len(limit_down)} 只")
```

---

### get_technical_indicator()

获取技术指标数据 (MACD、MA、BOLL、KDJ)。

**参数**:
- `symbol` (str): 股票代码
- `indicator` (str): 指标类型 ('macd', 'ma', 'boll', 'kdj')
- `frequency` (str): 频率 (默认 'daily')
- `start_date` (str): 开始日期 (可选)
- `end_date` (str): 结束日期 (可选)
- `limit` (int): 最大返回条数 (默认100)

**返回**: DataFrame 包含技术指标数据

**示例**:

```python
# 获取MACD指标
macd = adapter.get_technical_indicator(
    symbol='000001.SZ',
    indicator='macd',
    frequency='daily',
    limit=30
)

# MACD列: diff, dea, macd, ema12, ema26

# 获取MA指标
ma = adapter.get_technical_indicator(
    symbol='600000.SH',
    indicator='ma',
    frequency='daily',
    limit=50
)

# MA列: ma3, ma5, ma10, ma15, ma20, ma30, ma60, ma120, ma200, ma250
```

---

## 错误处理

所有方法在遇到错误时会抛出 `DataSourceError` 异常。

```python
from adapters.byapi_adapter import DataSourceError

try:
    quotes = adapter.get_realtime_quotes(['INVALID'])
except DataSourceError as e:
    print(f"数据获取失败: {e}")
```

常见错误:

1. **API请求失败**: 网络问题或API服务不可用
2. **无效参数**: 股票代码格式错误或频率参数不支持
3. **数据为空**: 指定日期无交易数据
4. **频率超限**: 请求过于频繁 (超过300次/分钟)

---

## 频率限制

byapi.com 的API频率限制:

| 账户类型 | 频率限制 |
|----------|----------|
| 基础版 | 300 次/分钟 |
| 包年版 | 3000 次/分钟 |
| 白金版 | 6000 次/分钟 |

`ByapiAdapter` 内置频率控制 (默认 0.2秒/请求 = 300次/分钟):

```python
# 自定义请求间隔
adapter = ByapiAdapter(
    licence="YOUR_LICENSE",
    min_interval=0.02  # 0.02秒 = 3000次/分钟 (包年版)
)
```

---

## 与MyStocks系统集成

### 在UnifiedManager中使用

```python
from unified_manager import MyStocksUnifiedManager
from adapters.byapi_adapter import ByapiAdapter

# 添加byapi数据源到系统
mgr = MyStocksUnifiedManager()

# 使用byapi获取实时数据
byapi = ByapiAdapter()
quotes = byapi.get_realtime_quotes(['000001.SZ'])

# 保存到系统 (自动路由到Redis)
mgr.save_data_by_classification(
    data=quotes,
    classification=DataClassification.REALTIME_POSITIONS
)
```

### 在DataSourceFactory中注册

```python
from factory.data_source_factory import DataSourceFactory
from adapters.byapi_adapter import ByapiAdapter

factory = DataSourceFactory()
factory.register_source('byapi', ByapiAdapter())

# 使用工厂获取数据 (自动降级)
kline = factory.get_data(
    'kline_data',
    symbol='000001.SZ',
    start_date='2025-10-01',
    end_date='2025-10-11'
)
```

---

## 性能优化建议

### 1. 批量获取实时行情

```python
# ✅ 推荐: 一次请求多只股票
quotes = adapter.get_realtime_quotes([
    '000001.SZ', '000002.SZ', '600000.SH'
])

# ❌ 避免: 循环单独请求
for symbol in symbols:
    quote = adapter.get_realtime_quotes([symbol])  # 频率浪费
```

### 2. 缓存股票列表

```python
# 股票列表不经常变化,建议缓存
stocks = adapter.get_stock_list()
# 缓存到Redis或本地文件,有效期1天
```

### 3. 合理设置日期范围

```python
# ✅ 推荐: 请求必要的日期范围
kline = adapter.get_kline_data(
    symbol='000001.SZ',
    start_date='2025-09-01',
    end_date='2025-10-11'
)

# ❌ 避免: 请求全部历史数据 (数据量大,速度慢)
kline = adapter.get_kline_data(
    symbol='000001.SZ',
    start_date='2000-01-01',
    end_date='2025-10-11'
)
```

---

## API映射表

| IDataSource方法 | Byapi API端点 | 说明 |
|-----------------|---------------|------|
| get_stock_list() | /hslt/list/{licence} | 股票列表 |
| get_kline_data() | /hsstock/history/{symbol}/{level}/n/{licence} | 历史K线 |
| get_realtime_quotes() | /hsrl/ssjy/{code}/{licence} | 实时行情 |
| get_fundamental_data() (income) | /hsstock/financial/income/{symbol}/{licence} | 利润表 |
| get_fundamental_data() (balance) | /hsstock/financial/balance/{symbol}/{licence} | 资产负债表 |
| get_fundamental_data() (cashflow) | /hsstock/financial/cashflow/{symbol}/{licence} | 现金流量表 |
| get_fundamental_data() (metrics) | /hsstock/financial/pershareindex/{symbol}/{licence} | 财务指标 |

---

## 常见问题 (FAQ)

### Q1: 为什么实时行情的 name 字段为空?

**A**: byapi的实时接口不返回股票名称。如需名称,请先调用 `get_stock_list()` 获取完整列表并缓存。

### Q2: 如何获取五档盘口数据?

**A**: byapi需单独调用五档接口 `/hsstock/real/five/{symbol}/{licence}`,目前未集成到 `get_realtime_quotes()` 中。可使用 `adapter._request()` 直接调用:

```python
url = f"https://api.biyingapi.com/hsstock/real/five/000001.SZ/{adapter.licence}"
five_level = adapter._request(url)
```

### Q3: 支持港股和美股吗?

**A**: 本适配器当前仅启用中国A股市场数据 (上交所SSE + 深交所SZSE)。根据项目业务范围限定，不包括期货(除股指期货外)、期权、外汇、黄金、美股等。

### Q4: 如何获取更多历史数据?

**A**: byapi会返回指定日期范围内的所有数据,不限制条数。如需更长时间跨度,直接扩大 `start_date` 和 `end_date` 范围即可。

---

## 参考链接

- **Byapi官方文档**:
  - 沪深股票: https://biyingapi.com/doc_hs
  - 指数数据: https://biyingapi.com/doc_zs
  - 基金数据: https://biyingapi.com/doc_jj

- **MyStocks项目文档**:
  - IDataSource接口: `specs/001-readme-md-md/contracts/data_source_api.md`
  - 快速开始: `specs/001-readme-md-md/quickstart.md`

---

**文档版本**: 1.0.0
**最后更新**: 2025-10-11
**维护者**: MyStocks Team
