# TDX数据集成文档

## 概述

MyStocks量化交易系统的TDX数据集成模块，提供从通达信本地数据文件读取和导入数据到系统数据库的完整功能。

## 功能特性

### ✅ 核心功能

- **二进制文件解析**
  - 支持日线数据 (.day文件)
  - 支持5分钟数据 (.lc5文件)
  - 支持1分钟数据 (.lc1文件)

- **多市场支持**
  - 上海证券交易所 (sh)
  - 深圳证券交易所 (sz)
  - 北京证券交易所 (bj)

- **智能数据路由**
  - 自动通过5-tier数据分类系统路由
  - 时序数据 → TDengine数据库
  - 元数据 → MySQL数据库

- **增量导入**
  - 支持全量导入和增量导入
  - 断点续传
  - 批量处理优化

## 模块组成

### 1. TdxBinaryParser (tdx_binary_parser.py)

二进制文件解析器，负责读取TDX本地数据文件。

**主要方法:**

```python
from data_sources import TdxBinaryParser

parser = TdxBinaryParser()

# 读取日线数据
day_data = parser.read_day_data('sh600000', start_date=date(2024, 1, 1))

# 读取5分钟数据
min5_data = parser.read_5min_data('sh600000', start_date=date(2024, 1, 1))

# 列出可用股票
stocks = parser.list_available_stocks('sh')

# 获取最新数据日期
latest_date = parser.get_latest_date('sh600000')
```

**数据格式:**

日线数据包含以下字段:
- `date`: 交易日期
- `open`: 开盘价
- `high`: 最高价
- `low`: 最低价
- `close`: 收盘价
- `volume`: 成交量（手）
- `amount`: 成交金额（元）

### 2. TdxImporter (tdx_importer.py)

数据导入器，负责将TDX数据批量导入到MyStocks数据库。

**主要方法:**

```python
from data_sources import TdxImporter
from unified_manager import MyStocksUnifiedManager

# 创建数据管理器
manager = MyStocksUnifiedManager()

# 创建导入器
importer = TdxImporter(unified_manager=manager)

# 全量导入某个市场
result = importer.import_market_daily(
    market='sh',
    start_date=date(2024, 1, 1),
    batch_size=100
)

# 增量导入（最近7天）
result = importer.import_incremental(
    market='sh',
    lookback_days=7
)
```

## 使用场景

### 场景1: 首次搭建系统（全量导入）

```python
from data_sources import TdxImporter
from unified_manager import MyStocksUnifiedManager
from datetime import date

# 初始化
manager = MyStocksUnifiedManager()
importer = TdxImporter(unified_manager=manager)

# 导入上海市场所有股票的历史数据
result = importer.import_market_daily(
    market='sh',
    start_date=date(2020, 1, 1),  # 从2020年开始
    batch_size=100
)

print(f"成功导入 {result['success_count']} 只股票")
print(f"总记录数: {result['total_records']:,}")
```

### 场景2: 每日定时更新（增量导入）

```python
# 每天执行一次，导入最新数据
result = importer.import_incremental(
    market='sh',
    lookback_days=3  # 最近3天（含节假日容错）
)
```

### 场景3: 特定股票池导入

```python
# 只导入指定股票
my_stocks = ['sh600000', 'sh600016', 'sh600036']

result = importer.import_market_daily(
    market='sh',
    symbols=my_stocks,
    start_date=date(2024, 1, 1)
)
```

## 数据路由说明

TDX数据通过MyStocks的5-tier数据分类系统自动路由：

| 数据类型 | 分类 | 目标数据库 | 表名 |
|---------|------|-----------|------|
| 日线数据 | MARKET_DATA_DAILY | TDengine | stock_daily |
| 5分钟数据 | MARKET_DATA_MIN5 | TDengine | stock_5min |
| 1分钟数据 | MARKET_DATA_MIN1 | TDengine | stock_1min |
| 导入记录 | META_DATA | MySQL | tdx_import_jobs |

## 性能优化

### 批量处理

默认批量大小为100，可根据系统性能调整：

```python
result = importer.import_market_daily(
    market='sh',
    batch_size=200  # 增大批量提高速度
)
```

### 并行处理

```python
# 在strategy_config.yaml中配置
tdx:
  parallel_import: true
  parallel_workers: 4
```

### 导入速度参考

- 单只股票日线数据（1年）: ~0.01秒
- 批量100只股票: ~10秒
- 全市场5000只股票: ~500秒（约8分钟）

## 配置说明

### 环境变量 (.env)

```bash
# TDX数据路径
TDX_DATA_PATH=/mnt/d/ProgramData/tdx_new/vipdoc

# 支持的市场
TDX_MARKETS=sh,sz,bj,cw,ds,ot

# 自动复权
TDX_APPLY_ADJUSTMENT=true

# 跳过周末
TDX_SKIP_WEEKENDS=true
```

### 策略配置 (config/strategy_config.yaml)

```yaml
tdx:
  enabled: true
  data_path: '${TDX_DATA_PATH}'
  markets:
    - sh
    - sz
  parallel_import: true
  batch_size: 100
```

## 错误处理

### 常见错误及解决方案

1. **文件不存在**
   ```
   错误: 文件不存在: /path/to/sh600000.day
   解决: 检查TDX_DATA_PATH配置是否正确
   ```

2. **数据库连接失败**
   ```
   错误: 保存到数据库失败
   解决: 检查数据库连接配置和服务状态
   ```

3. **权限不足**
   ```
   错误: Permission denied
   解决: 确保对TDX数据目录有读权限
   ```

## 示例代码

完整示例请参考: `examples/tdx_import_example.py`

运行示例:
```bash
python examples/tdx_import_example.py
```

## API参考

### TdxBinaryParser

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `read_day_data()` | 读取日线数据 | symbol, start_date, end_date | DataFrame |
| `read_5min_data()` | 读取5分钟数据 | symbol, start_date, end_date | DataFrame |
| `read_1min_data()` | 读取1分钟数据 | symbol, start_date, end_date | DataFrame |
| `list_available_stocks()` | 列出可用股票 | market | List[str] |
| `get_latest_date()` | 获取最新日期 | symbol | date |

### TdxImporter

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `import_market_daily()` | 导入市场日线数据 | market, start_date, end_date, symbols, batch_size | Dict |
| `import_incremental()` | 增量导入 | market, lookback_days | Dict |
| `get_import_progress()` | 获取导入进度 | market | Dict |

## 最佳实践

1. **首次导入**: 使用小批量测试（10-100只股票）
2. **生产环境**: 增加批量大小（200-500）
3. **定时任务**: 使用增量导入，lookback_days=3-7
4. **监控日志**: 关注导入失败的股票
5. **备份策略**: 导入前备份数据库

## 更新日志

### v1.0.0 (2025-10-18)
- ✅ 实现TDX二进制文件解析器
- ✅ 实现数据导入器
- ✅ 支持日线、5分钟、1分钟数据
- ✅ 集成5-tier数据分类系统
- ✅ 增量导入功能
- ✅ 批量处理优化

## 技术支持

如有问题，请查看:
- 代码文档: data_sources/tdx_binary_parser.py
- 示例代码: examples/tdx_import_example.py
- 项目文档: CLAUDE.md

## 许可证

MyStocks Project © 2025
