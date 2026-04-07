# TDX模块数据能力总结

> **使用说明**:
> 本文件是 API 相关的参考文档或专题说明，不是当前 API 契约、当前实施基线或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`；若涉及 API 契约事实源，再以实际的 FastAPI 路由 + Pydantic Schema + `/openapi.json` 为准。
>
> 文内端点、命令、统计值和示例如未重新复核，应视为参考或历史材料，不得直接当作当前事实。


**文档版本**: v1.0
**创建日期**: 2026-01-02
**模块路径**: `src/adapters/tdx/`
**数据源**: 通达信 (TongDaXin) + PyTDX

---

## 📊 数据能力概览

TDX模块重组后，提供了三大类数据获取能力：

| 数据类别 | 数据来源 | 数据类型 | 主要脚本 |
|---------|---------|---------|---------|
| **远程实时数据** | 在线服务器（本地优先+网络备用） | 实时行情、基本信息、分类数据 | `realtime_service.py` |
| **远程历史数据** | 在线服务器（本地优先+网络备用） | K线数据（多周期） | `kline_data_service.py` |
| **本地文件数据** | 通达信安装目录 | 板块分类数据 | `tdx_block_reader.py` |

---

## 🌐 一、远程实时数据

### 数据来源
- **主要来源**: 本地通达信服务器 (127.0.0.1:7709)
- **备用服务器**: 5个网络服务器自动故障转移
- **连接协议**: PyTDX (通达信二进制协议)

### 核心脚本
- **主脚本**: `src/adapters/tdx/realtime_service.py`
- **服务类**: `RealtimeService`
- **配置**: `config/tdx_settings.conf`

### 1.1 实时行情数据

**方法**: `get_real_time_data(symbol: str)`

**数据字段**:
```python
{
    "symbol": "股票代码",
    "name": "股票名称",
    "price": "当前价格",
    "open": "开盘价",
    "high": "最高价",
    "low": "最低价",
    "pre_close": "昨收价",
    "change": "涨跌额",
    "change_pct": "涨跌幅(%)",
    "volume": "成交量(手)",
    "amount": "成交额(元)",
    "turnover": "换手率(%)",
    "pe": "市盈率",
    "pb": "市净率",
    "market": "市场(上交所/深交所)",
    "timestamp": "时间戳",
    "source": "tdx"
}
```

**信息类别**: 基础行情、价格、成交量、估值指标

**更新频率**: 实时（交易时间内）

---

### 1.2 股票基本信息

**方法**: `get_stock_basic(symbol: str)`

**数据字段**:
```python
{
    "symbol": "股票代码",
    "name": "股票名称",
    "market": "市场",
    "industry": "所属行业",
    "area": "地区",
    "pe": "市盈率",
    "pb": "市净率",
    "outstanding": "流通股本",
    "total_shares": "总股本",
    "float_shares": "流通股",
    "asset_per_share": "每股净资产",
    "bv_per_share": "每股公积金",
    "time_to_market": "上市日期",
    "listing_date": "挂牌日期",
    "is_st": "是否ST",
    "timestamp": "时间戳",
    "source": "tdx"
}
```

**信息类别**: 股本信息、基本面、上市信息

**更新频率**: 每日更新

---

### 1.3 批量实时行情

**方法**: `get_batch_real_time_data(symbols: List[str])`

**功能**: 一次获取最多50只股票的实时行情

**数据字段**: 同1.1实时行情数据

**信息类别**: 批量基础行情

**更新频率**: 实时

---

### 1.4 行业分类数据

**方法**: `get_industry_classify()`

**返回**: `pd.DataFrame`

**数据内容**:
- 行业代码
- 行业名称
- 行业类型

**信息类别**: 行业分类

**更新频率**: 每日更新

---

### 1.5 概念分类数据

**方法**: `get_concept_classify()`

**返回**: `pd.DataFrame`

**数据内容**:
- 概念代码
- 概念名称
- 概念类型

**信息类别**: 概念分类（热门题材）

**更新频率**: 每日更新

---

### 1.6 股票行业概念信息

**方法**: `get_stock_industry_concept(symbol: str)`

**数据字段**:
```python
{
    "symbol": "股票代码",
    "industry": {
        "name": "行业名称",
        "code": "行业代码"
    },
    "concepts": {
        # 概念列表
    },
    "timestamp": "时间戳"
}
```

**信息类别**: 股票属性、分类标签

**更新频率**: 每日更新

---

## 📈 二、远程历史数据（K线数据）

### 数据来源
- **主要来源**: 本地通达信服务器 (127.0.0.1:7709)
- **备用服务器**: 5个网络服务器自动故障转移
- **连接协议**: PyTDX

### 核心脚本
- **主脚本**: `src/adapters/tdx/kline_data_service.py`
- **服务类**: `KlineDataService`
- **支持周期**: 1分钟、5分钟、日线、周线、月线

### 2.1 股票日线数据

**方法**: `get_stock_daily(symbol, start_date, end_date, adjust)`

**参数**:
- `symbol`: 股票代码
- `start_date`: 开始日期 (YYYY-MM-DD)
- `end_date`: 结束日期 (YYYY-MM-DD)
- `adjust`: 复权类型 ('qfq'=前复权, 'hfq'=后复权, 'none'=不复权)

**数据字段** (19个):
```python
{
    "datetime": "交易时间",
    "open": "开盘价",
    "high": "最高价",
    "low": "最低价",
    "close": "收盘价",
    "volume": "成交量(手)",
    "amount": "成交额(元)",
    "turnover": "换手率(%)",
    "change": "涨跌额",
    "change_pct": "涨跌幅(%)",
    "ma5": "5日均线",
    "ma10": "10日均线",
    "ma20": "20日均线",
    "ma60": "60日均线",
    "v_ma5": "5日均量",
    "v_ma10": "10日均量",
    "v_ma20": "20日均量",
    "v_ma60": "60日均量",
    "symbol": "股票代码",
    "market": "市场",
    "adjust": "复权类型"
}
```

**信息类别**: OHLCV价格数据、技术指标（均线）、市场数据

**时间范围**: 支持任意历史日期范围

**数据类型**: 历史K线、技术分析指标

---

### 2.2 指数日线数据

**方法**: `get_index_daily(index_code, start_date, end_date)`

**参数**:
- `index_code`: 指数代码（如: 000001, 399001）
- `start_date`: 开始日期
- `end_date`: 结束日期

**数据字段** (9个):
```python
{
    "datetime": "交易时间",
    "open": "开盘点位",
    "high": "最高点位",
    "low": "最低点位",
    "close": "收盘点位",
    "volume": "成交量",
    "amount": "成交额",
    "turnover": "换手率",
    "symbol": "指数代码",
    "security_type": "index"
}
```

**信息类别**: 指数OHLCV数据

**时间范围**: 支持任意历史日期范围

**数据类型**: 指数历史K线

---

### 2.3 分钟K线数据

**方法**: `get_minute_kline(symbol, period, count, adjust)`

**参数**:
- `symbol`: 股票代码
- `period`: K线周期 ('1min', '5min', '15min', '30min', '60min')
- `count`: 获取条数（默认240条）
- `adjust`: 复权类型

**数据字段**: 同日线数据（19个字段）

**信息类别**: 高频OHLCV数据、技术指标

**时间范围**: 最近N条记录

**数据类型**: 短周期K线、日内交易数据

---

### 2.4 多周期K线数据

**方法**: `get_stock_kline(symbol, period, start_date, end_date, adjust)`

**支持周期**:
- `1m` / `1min`: 1分钟K线
- `5m` / `5min`: 5分钟K线
- `15m` / `15min`: 15分钟K线
- `30m` / `30min`: 30分钟K线
- `1h` / `60min`: 1小时K线
- `1d` / `daily`: 日K线
- `1w` / `weekly`: 周K线
- `1M` / `monthly`: 月K线

**数据字段**: 同日线数据（19个字段）

**信息类别**: 多周期OHLCV、多级别技术指标

**时间范围**: 根据周期不同而不同

**数据类型**: 多时间框架K线数据

---

## 💾 三、本地文件数据（板块数据）

### 数据来源
- **文件位置**: 通达信安装目录 `/T0002/hq_cache/`
- **文件格式**: 二进制.dat文件
- **读取方式**: PyTDX BlockReader

### 核心脚本
- **主脚本**: `src/adapters/tdx/tdx_block_reader.py`
- **服务类**: `TdxBlockReader`
- **依赖**: PyTDX的`block_reader`模块

### 3.1 指数板块数据

**方法**: `get_index_blocks(result_type='flat')`

**文件**: `T0002/hq_cache/block_zs.dat`

**返回格式**:

**扁平格式** (`flat`):
```python
{
    "blockname": "板块名称",
    "block_type": "板块类型代码",
    "code_index": "股票索引",
    "code": "股票代码"
}
```

**分组格式** (`group`):
```python
{
    "blockname": "板块名称",
    "block_type": "板块类型代码",
    "stock_count": "股票数量",
    "code_list": "股票列表"
}
```

**信息类别**: 指数成分股分类

**更新频率**: 每日更新（随通达信软件更新）

**数据类型**: 板块分类、成分股列表

---

### 3.2 风格板块数据

**方法**: `get_style_blocks(result_type='flat')`

**文件**: `T0002/hq_cache/block_fg.dat`

**返回格式**: 同3.1

**板块示例**:
- 大盘股
- 小盘股
- 价值股
- 成长股
- 等等

**信息类别**: 投资风格分类

**数据类型**: 风格标签、股票分组

---

### 3.3 概念板块数据

**方法**: `get_concept_blocks(result_type='flat')`

**文件**: `T0002/hq_cache/block_gn.dat`

**返回格式**: 同3.1

**板块示例**:
- 新能源
- 人工智能
- 芯片半导体
- 国防军工
- 等等

**信息类别**: 热门概念题材分类

**数据类型**: 概念标签、题材股票

---

### 3.4 默认板块数据

**方法**: `get_default_blocks(result_type='flat')`

**文件**: `T0002/hq_cache/block.dat`

**返回格式**: 同3.1

**信息类别**: 通达信默认板块分类

**数据类型**: 通用板块分类

---

### 3.5 所有板块数据（合并）

**方法**: `get_all_blocks(result_type='flat')`

**功能**: 合并4种板块类型的数据

**返回格式**: 同3.1（包含所有板块类型）

**信息类别**: 全局板块视图

**数据类型**: 综合板块分类

---

### 3.6 股票所属板块查询

**方法**: `get_stock_blocks(stock_code: str)`

**参数**:
- `stock_code`: 6位股票代码（如: '600519'）

**返回**:
```python
[
    {
        "blockname": "白酒",
        "block_type": "概念"
    },
    {
        "blockname": "贵州板块",
        "block_type": "区域"
    },
    # ... 更多板块
]
```

**信息类别**: 股票属性、分类标签

**数据类型**: 股票-板块关系映射

---

### 3.7 板块包含股票查询

**方法**: `get_block_stocks(block_name: str)`

**参数**:
- `block_name`: 板块名称

**返回**: 该板块包含的所有股票代码列表

**信息类别**: 板块成分股

**数据类型**: 板块-股票关系映射

---

## 🎯 四、数据使用场景

### 4.1 实时监控场景
**数据类型**: 远程实时数据
- 股票实时行情监控
- 涨跌幅监控
- 成交量异常监控
- 估值指标监控

### 4.2 技术分析场景
**数据类型**: 远程历史数据
- K线图表绘制
- 技术指标计算（MACD, KDJ, RSI等）
- 多时间框架分析
- 回测系统数据源

### 4.3 选股筛选场景
**数据类型**: 本地板块数据 + 远程历史数据
- 板块轮动策略
- 概念题材筛选
- 成分股分析
- 行业比较研究

### 4.4 基本面分析场景
**数据类型**: 远程实时数据 + 远程历史数据
- 财务指标分析（PE, PB等）
- 估值分析
- 业绩趋势分析
- 行业对比研究

---

## 🔧 五、配置与管理

### 5.1 服务器配置

**配置文件**: `config/tdx_settings.conf`

**服务器列表** (6个，优先级顺序):
1. **127.0.0.1:7709** - 本地通达信（最优先）
2. 180.153.18.170:7709
3. 101.227.73.20:7709
4. 119.147.212.81:7709
5. 114.80.63.12:7709
6. 60.12.136.250:7709

**自动故障转移**: 当前服务器不可用时，自动尝试下一个服务器

### 5.2 性能配置

```ini
[PERFORMANCE]
connect_timeout = 5        # 连接超时（秒）
api_timeout = 30           # API调用超时（秒）
retry_count = 3            # 重试次数
auto_retry_enabled = true  # 自动重试
```

### 5.3 本地文件路径配置

```ini
[TDX]
install_path = /mnt/d/ProgramData/tdx_new
local_host = 127.0.0.1
local_port = 7709
```

**板块文件路径**:
- `T0002/hq_cache/block_zs.dat` - 指数板块
- `T0002/hq_cache/block_fg.dat` - 风格板块
- `T0002/hq_cache/block_gn.dat` - 概念板块
- `T0002/hq_cache/block.dat` - 默认板块

---

## 📦 六、模块导入与使用

### 6.1 快速导入

```python
# 方式1: 导入具体类
from src.adapters.tdx import TdxDataSource, TdxBlockReader

# 方式2: 导入配置函数
from src.adapters.tdx import get_tdx_config, get_tdx_server_list

# 方式3: 导入服务类
from src.adapters.tdx import RealtimeService, KlineDataService
```

### 6.2 实时数据示例

```python
from src.adapters.tdx import TdxDataSource

tdx = TdxDataSource()

# 获取实时行情
data = tdx.get_real_time_data("600519")
print(f"当前价格: {data['price']}, 涨跌幅: {data['change_pct']}%")

# 批量获取实时行情
symbols = ["600519", "000001", "000002"]
batch_data = tdx.get_batch_real_time_data(symbols)
```

### 6.3 历史K线示例

```python
from src.adapters.tdx import TdxDataSource

tdx = TdxDataSource()

# 获取日线数据
df = tdx.get_stock_daily(
    symbol="600519",
    start_date="2024-01-01",
    end_date="2024-12-31",
    adjust="qfq"
)
print(df.head())

# 获取分钟K线
df_min = tdx.get_minute_kline(
    symbol="600519",
    period="5min",
    count=240
)
```

### 6.4 板块数据示例

```python
from src.adapters.tdx import TdxBlockReader, get_tdx_path

# 创建板块读取器
reader = TdxBlockReader(get_tdx_path())

# 获取概念板块
df_concept = reader.get_concept_blocks()
print(f"共有 {df_concept['blockname'].nunique()} 个概念板块")

# 查询股票所属板块
blocks = reader.get_stock_blocks("600519")
for block in blocks:
    print(f"{block['blockname']} ({block['block_type']})")

# 查询板块包含的股票
stocks = reader.get_block_stocks("新能源")
print(f"新能源板块共 {len(stocks)} 只股票")
```

---

## 📊 七、数据字段总结表

### 7.1 实时行情字段（15个）

| 字段名 | 类型 | 说明 | 示例 |
|-------|------|------|------|
| symbol | str | 股票代码 | "600519" |
| name | str | 股票名称 | "贵州茅台" |
| price | float | 当前价格 | 1680.50 |
| open | float | 开盘价 | 1675.00 |
| high | float | 最高价 | 1690.00 |
| low | float | 最低价 | 1670.00 |
| pre_close | float | 昨收价 | 1670.00 |
| change | float | 涨跌额 | +10.50 |
| change_pct | float | 涨跌幅(%) | +0.63 |
| volume | int | 成交量(手) | 25000 |
| amount | float | 成交额(元) | 4.2亿 |
| turnover | float | 换手率(%) | 0.25 |
| pe | float | 市盈率 | 35.5 |
| pb | float | 市净率 | 12.8 |
| market | str | 市场 | "上交所" |

### 7.2 K线数据字段（19个）

| 字段名 | 类型 | 说明 | 示例 |
|-------|------|------|------|
| datetime | datetime | 交易时间 | 2024-01-01 09:30:00 |
| open | float | 开盘价 | 1675.00 |
| high | float | 最高价 | 1690.00 |
| low | float | 最低价 | 1670.00 |
| close | float | 收盘价 | 1680.50 |
| volume | int | 成交量(手) | 25000 |
| amount | float | 成交额(元) | 4.2亿 |
| turnover | float | 换手率(%) | 0.25 |
| change | float | 涨跌额 | +10.50 |
| change_pct | float | 涨跌幅(%) | +0.63 |
| ma5 | float | 5日均线 | 1678.00 |
| ma10 | float | 10日均线 | 1675.00 |
| ma20 | float | 20日均线 | 1670.00 |
| ma60 | float | 60日均线 | 1665.00 |
| v_ma5 | float | 5日均量 | 24000 |
| v_ma10 | float | 10日均量 | 23000 |
| v_ma20 | float | 20日均量 | 22000 |
| v_ma60 | float | 60日均量 | 21000 |
| symbol | str | 股票代码 | "600519" |

### 7.3 板块数据字段（4-5个）

| 字段名 | 类型 | 说明 | 示例 |
|-------|------|------|------|
| blockname | str | 板块名称 | "新能源" |
| block_type | int | 板块类型代码 | 1 |
| code_index | int | 股票索引 | 0 |
| code | str | 股票代码 | "600519" |
| stock_count | int | 股票数量 | 150 |

---

## ⚡ 八、性能特点

### 8.1 连接可靠性
- **本地优先**: 优先使用本地通达信（最快）
- **自动切换**: 6个服务器自动故障转移
- **连接超时**: 5秒超时保护
- **自动重试**: 失败自动重试3次

### 8.2 数据完整性
- **实时数据**: 交易时间内秒级更新
- **历史数据**: 支持任意日期范围查询
- **技术指标**: 自动计算7个均线指标
- **复权处理**: 支持前复权、后复权、不复权

### 8.3 本地数据优势
- **零延迟**: 本地文件直接读取，无网络延迟
- **离线可用**: 不依赖网络连接
- **完整性**: 包含通达信全部板块分类

---

## 🚀 九、未来增强计划

### 已实现 ✅
- [x] 配置管理系统（本地+网络服务器）
- [x] 板块数据本地读取（4种类型）
- [x] K线日线数据
- [x] 实时行情数据
- [x] 分钟K线数据

### 计划中 ⏳
- [ ] 扩展K线周期（周线、月线、季线、年线）
- [ ] 财务数据接口
- [ ] 股票资金流向数据
- [ ] 龙虎榜数据
- [ ] 交易日历数据

---

## 📚 十、相关文档

- **重组报告**: `docs/reports/TDX_REORGANIZATION_REPORT.md`
- **配置文件**: `config/tdx_settings.conf`
- **测试脚本**: `scripts/tests/test_tdx_config.py`
- **PyTDX文档**: `/opt/iflow/tdxpy/`

---

**文档维护**: MyStocks Project
**最后更新**: 2026-01-02
**版本**: v1.0
