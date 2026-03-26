# TDX数据源适配器使用文档

**创建人**: Claude
**版本**: 2.1.0
**批准日期**: 2025-10-15
**最后修订**: 2025-10-16
**本次修订内容**: 通达信TDX集成说明

---

## 概述

TDX(通达信)数据源适配器是MyStocks系统的核心数据源组件之一,提供A股市场的实时行情和历史K线数据访问。

**版本**: 1.0.0
**作者**: MyStocks Team
**日期**: 2025-10-15

## 核心特性

### ✅ 已实现功能

1. **实时行情查询** - `get_real_time_data()`
   - 支持沪深A股实时行情
   - 包含价格、成交量、五档行情等
   - 自动识别市场代码

2. **历史K线数据** - `get_stock_daily()`, `get_index_daily()`
   - 支持日线数据获取
   - 自动分页处理(800条/批)
   - 支持任意时间范围查询

3. **多周期K线** - `get_stock_kline()`, `get_index_kline()`
   - **1分钟线** (`1m`)
   - **5分钟线** (`5m`)
   - **15分钟线** (`15m`)
   - **30分钟线** (`30m`)
   - **1小时线** (`1h`)
   - **日线** (`1d`)

4. **服务器管理**
   - 自动解析connect.cfg配置文件
   - 38个TDX服务器自动发现
   - 主服务器优先级配置
   - 故障自动转移
   - 负载均衡支持

5. **高可用特性**
   - 指数退避重试机制(1s → 2s → 4s)
   - 连接池管理
   - 完整的错误处理
   - 详细的日志记录

### 🚧 待实现功能

- `get_stock_basic()` - 股票基本信息
- `get_financial_data()` - 财务数据
- `get_index_components()` - 指数成分股
- `get_market_calendar()` - 交易日历(TDX不支持)
- `get_news_data()` - 新闻数据(TDX不支持)

## 快速开始

### 1. 基础使用

```python
from adapters.tdx_adapter import TdxDataSource

# 创建TDX数据源实例
tdx = TdxDataSource()

# 获取实时行情
quote = tdx.get_real_time_data('600519')  # 贵州茅台
if isinstance(quote, dict):
    print(f"股票: {quote['name']}")
    print(f"最新价: {quote['price']:.2f}")
    print(f"涨跌幅: {(quote['price']/quote['pre_close']-1)*100:.2f}%")
    print(f"成交量: {quote['volume']:,}手")
```

### 2. 历史K线数据

```python
from datetime import datetime, timedelta

# 获取股票日线数据(最近90天)
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

df = tdx.get_stock_daily('600519', start_date, end_date)
print(f"获取{len(df)}条日线数据")
print(df.head())

# 获取指数日线数据
df_index = tdx.get_index_daily('000001', start_date, end_date)  # 上证指数
print(f"上证指数数据: {len(df_index)}条")
```

### 3. 多周期K线数据

```python
# 获取5分钟K线(最近2天)
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')

df_5m = tdx.get_stock_kline('600519', start_date, end_date, period='5m')
print(f"5分钟K线: {len(df_5m)}条")

# 获取1小时K线
df_1h = tdx.get_stock_kline('600519', start_date, end_date, period='1h')
print(f"1小时K线: {len(df_1h)}条")

# 所有支持的周期
periods = ['1m', '5m', '15m', '30m', '1h', '1d']
for period in periods:
    df = tdx.get_stock_kline('600519', start_date, end_date, period=period)
    print(f"{period}: {len(df)}条数据")
```

### 4. 使用数据源管理器(推荐)

```python
from adapters.data_source_manager import get_default_manager

# 获取默认数据源管理器(自动注册TDX和AKShare)
manager = get_default_manager()

# 方式1: 指定使用TDX数据源
quote = manager.get_real_time_data('600519', source='tdx')

# 方式2: 自动选择(按优先级:tdx → akshare)
quote = manager.get_real_time_data('600519')

# 获取历史数据(自动故障转移)
df = manager.get_stock_daily('600519', '2024-01-01', '2024-12-31')
```

## 配置说明

### 环境变量配置

在`.env`文件中配置TDX服务器参数:

```bash
# TDX服务器配置
TDX_SERVER_HOST=101.227.73.20  # 默认服务器地址
TDX_SERVER_PORT=7709            # 默认端口
TDX_MAX_RETRIES=3               # 最大重试次数
TDX_RETRY_DELAY=1               # 重试延迟(秒)
TDX_API_TIMEOUT=10              # API超时(秒)
```

### 服务器配置文件

TdxDataSource会自动读取`temp/connect.cfg`文件,该文件包含38个TDX服务器的配置信息:

```ini
[HQHOST]
HostNum=38
PrimaryHost=5

HostName01=通达信深圳双线主站1
IPAddress01=110.41.147.114
Port01=7709

HostName02=通达信深圳双线主站2
IPAddress02=110.41.2.72
Port02=7709
...
```

### 自定义配置

```python
# 使用自定义服务器
tdx = TdxDataSource(
    tdx_host='example.local',
    tdx_port=7709,
    max_retries=5,
    retry_delay=2,
    use_server_config=False  # 不使用connect.cfg
)

# 使用connect.cfg但自定义重试参数
tdx = TdxDataSource(
    max_retries=5,
    retry_delay=2,
    use_server_config=True
)
```

## 市场代码识别规则

### 股票市场

- **深圳市场** (market=0)
  - 000xxx: 深市主板
  - 002xxx: 中小板
  - 300xxx: 创业板

- **上海市场** (market=1)
  - 600xxx, 601xxx, 603xxx: 沪市主板
  - 688xxx: 科创板

### 指数市场

- **深圳指数** (market=0): 399xxx (如399001=深证成指)
- **上海指数** (market=1): 000xxx (如000001=上证指数)

**注意**: 指数的市场代码与股票不同!

## 数据格式说明

### 实时行情数据

```python
{
    'code': '600519',           # 股票代码
    'name': '贵州茅台',          # 股票名称
    'price': 1462.00,           # 最新价
    'pre_close': 1451.02,       # 昨收价
    'open': 1450.98,            # 今开
    'high': 1463.00,            # 最高
    'low': 1445.08,             # 最低
    'volume': 42785,            # 成交量(手)
    'amount': 6233407488.0,     # 成交额(元)
    'bid1': 1461.99,            # 买一价
    'bid1_volume': 2,           # 买一量
    'ask1': 1462.00,            # 卖一价
    'ask1_volume': 21,          # 卖一量
    'timestamp': '2025-10-15 14:51:15'  # 查询时间
}
```

### K线数据DataFrame

```python
# 日线数据
        date    open    high     low   close  volume
0 2025-07-17 1528.00 1542.00 1526.01 1537.00 45678.0
1 2025-07-18 1538.00 1545.00 1530.00 1540.00 42345.0
...

# 分钟线数据(包含完整时间)
             date    open    high     low   close  volume
0 2025-10-15 09:30:00 1451.00 1455.00 1450.00 1454.00 125400.0
1 2025-10-15 09:35:00 1454.50 1458.00 1454.00 1456.50 98500.0
...
```

## 错误处理

### 常见错误类型

1. **连接错误** - 服务器无法连接
```python
quote = tdx.get_real_time_data('600519')
if isinstance(quote, str):
    print(f"错误: {quote}")  # 返回错误消息字符串
```

2. **参数错误** - 股票代码格式错误
```python
quote = tdx.get_real_time_data('AAPL')
# 返回: "无效的股票代码格式: AAPL (需要6位数字)"
```

3. **无数据** - 查询结果为空
```python
df = tdx.get_stock_daily('999999', '2024-01-01', '2024-12-31')
# 返回空DataFrame: pd.DataFrame()
```

### 重试机制

TDX适配器内置指数退避重试:

```
第1次失败 → 等待1秒 → 重试
第2次失败 → 等待2秒 → 重试
第3次失败 → 等待4秒 → 重试
第4次失败 → 抛出异常
```

同时,如果启用了`use_server_config=True`,每次重试会自动切换到备用服务器。

## 性能优化建议

### 1. 批量查询

```python
# 不推荐: 逐个查询
for symbol in ['600519', '600036', '000001']:
    quote = tdx.get_real_time_data(symbol)
    # 处理数据...

# 推荐: 使用连接池复用
tdx = TdxDataSource()  # 创建一次,复用多次
for symbol in symbols:
    quote = tdx.get_real_time_data(symbol)
```

### 2. 日期范围控制

```python
# 不推荐: 获取全部历史(可能数万条)
df = tdx.get_stock_daily('600519', '1900-01-01', '2099-12-31')

# 推荐: 按需获取
df = tdx.get_stock_daily('600519', '2024-01-01', '2024-12-31')
```

### 3. 周期选择

```python
# 根据需求选择合适的周期
# 策略回测 → 使用日线(1d)
# 盘中监控 → 使用5分钟(5m)或15分钟(15m)
# 高频交易 → 使用1分钟(1m)
```

## 测试

### 运行MVP测试

```bash
# 测试基础功能(实时行情+日线)
python test_tdx_mvp.py

# 测试多周期K线
python test_tdx_multiperiod.py

# 测试服务器配置
python -c "from utils.tdx_server_config import TdxServerConfig; config = TdxServerConfig(); print(config)"
```

### 预期结果

```
============================================================
测试结果汇总
============================================================
server_config       : ✓ PASS
real_time_quote     : ✓ PASS
stock_daily         : ✓ PASS
index_daily         : ✓ PASS
error_handling      : ✓ PASS

总计: 5/5 测试通过

🎉 所有MVP功能测试通过!
```

## 常见问题FAQ

### Q1: 为什么使用本地pytdx而不是pip安装?

A: 为了支持二次开发和定制化需求,MyStocks使用本地`temp/pytdx/`目录中的pytdx代码。这样可以:
- 修改和扩展pytdx功能
- 不受PyPI版本更新影响
- 保证代码稳定性

### Q2: connect.cfg文件如何获取?

A: connect.cfg是通达信客户端的配置文件,通常位于TDX安装目录(如`D:\ProgramData\tdx_new\`)。将其复制到`temp/`目录即可。

如果没有connect.cfg,适配器会自动使用默认服务器(101.227.73.20:7709)。

### Q3: 如何处理市场休市时段?

A: TDX服务器在休市时段仍可连接,但返回的是最后一个交易日的数据。建议:
- 结合交易日历判断当前是否交易时段
- 检查`timestamp`字段判断数据时效性
- 使用`get_market_calendar()`获取交易日历(需AKShare等其他数据源)

### Q4: 支持港股/美股吗?

A: 不支持。TDX适配器仅支持A股市场(深交所+上交所),不包含:
- 港股
- 美股
- 期货
- 期权

如需其他市场数据,请使用AKShare等其他数据源。

### Q5: 数据延迟多少?

A: TDX实时行情数据通常有3-5秒延迟,不属于Level-2行情。适合:
- 策略研发和回测
- 盘中监控
- 低频交易

不适合:
- 高频交易(毫秒级)
- 需要精确到毫秒的场景

## 更新日志

### v1.0.0 (2025-10-15)

**MVP版本发布**

- ✅ 实时行情查询
- ✅ 历史日线数据(股票+指数)
- ✅ 多周期K线(1m/5m/15m/30m/1h/1d)
- ✅ 服务器配置管理(38个服务器)
- ✅ 故障转移和负载均衡
- ✅ 完整的错误处理和重试机制
- ✅ 数据验证和格式化
- ✅ 全部测试通过(5/5 MVP + 6/6 多周期)

### 后续计划

- 🚧 财务数据支持
- 🚧 指数成分股查询
- 🚧 更多K线周期(周线/月线)
- 🚧 分时数据支持
- 🚧 板块信息查询

## 许可证

本项目为MyStocks系统的一部分,遵循MIT许可证。

## 联系方式

- **项目地址**: `/opt/claude/mystocks_spec`
- **文档路径**: `adapters/README_TDX.md`
- **测试脚本**: `test_tdx_mvp.py`, `test_tdx_multiperiod.py`

---

*最后更新: 2025-10-15*
