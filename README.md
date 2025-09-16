# MyStocks 数据管理系统

[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](./CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

MyStocks是一个灵活、可扩展的股票数据获取和管理系统，采用了工厂模式和适配器模式的设计模式，支持多种数据源，提供统一的数据访问接口。

2025-9-16 截止目前，该程序的框架已经完成，但目前仅支持Akshare数据源，其他数据源正在开发中，功能完善中。

## 🆕 最新更新

### v1.1.0 新增功能
- ✅ **扩展接口支持**: 新增实时数据、交易日历、财务数据、新闻数据等接口
- ✅ **多返回类型**: 支持DataFrame、Dict、List、JSON等多种返回格式
- ✅ **统一列名管理**: 自动处理不同数据源的列名差异，支持中英文互转
- ✅ **批量数据源注册**: 支持一次性注册多个数据源
- ✅ **Tushare数据源**: 新增完整的Tushare数据源适配器
- ✅ **数据源管理增强**: 支持查看、取消注册数据源

## 系统架构

系统采用分层架构设计，主要包含以下几个核心组件：

### 1. 接口层 (interfaces/data_source.py)

定义了所有数据源必须实现的统一接口，确保系统可以无缝切换不同的数据源。

**最新接口支持：**
- ✅ 基础数据：股票日线、指数日线、股票基本信息、指数成分股
- ✅ **实时数据**: 实时价格、成交量等实时信息
- ✅ **交易日历**: 交易日、节假日信息
- ✅ **财务数据**: 年报、季报财务数据
- ✅ **新闻数据**: 个股新闻和市场新闻
- ✅ **多返回类型**: 支持DataFrame、Dict、List、JSON等格式

### 2. 适配器层 (adapters/*.py)

实现了具体的数据源适配器，如AkshareDataSource和BaostockDataSource，将不同数据源的API转换为系统统一接口。

### 3. 工厂层 (factory/data_source_factory.py)

负责创建具体的数据源对象，隐藏数据源创建的复杂性，提供注册新数据源的机制。

**最新墟能：**
- ✅ **批量注册**: `register_multiple_sources()` - 一次性注册多个数据源
- ✅ **数据源管理**: `get_available_sources()` - 查看所有可用数据源
- ✅ **取消注册**: `unregister_source()` - 动态移除数据源
- ✅ **错误处理**: 更完善的创建失败处理机制

### 4. 管理层 (manager/unified_data_manager.py)

作为系统的门户，提供简洁的API，协调不同数据源的使用，管理数据源实例的生命周期。

### 5. 应用层 (mystocks_main.py)

主程序入口，提供用户交互界面，创建统一数据管理器实例，处理用户输入和命令。

### 6. 工具层 (utils/*.py)

提供日期和股票代码处理等通用功能，支持多种格式的输入。

**最新工具：**
- ✅ **统一列名管理器** (`column_mapper.py`): 自动处理不同数据源的列名差异
- ✅ **中英文互转**: 支持DataFrame列名的中英文自由转换
- ✅ **列名验证**: 自动验证数据格式的完整性
- ✅ **智能格式识别**: 支持多种列名格式的自动识别和映射

## 运行逻辑和处理流程

### 数据获取流程

1. **用户请求**：用户通过mystocks_main.py或直接调用UnifiedDataManager发起数据请求
2. **参数处理**：UnifiedDataManager对请求参数进行标准化处理（如日期格式化、股票代码标准化）
3. **数据源选择**：UnifiedDataManager根据用户指定或默认设置选择合适的数据源
4. **数据源创建**：如果数据源实例不存在，通过DataSourceFactory创建数据源实例
5. **数据获取**：调用数据源适配器的相应方法获取数据
6. **数据返回**：将获取的数据返回给用户

### 数据源扩展流程

1. **创建适配器**：实现IDataSource接口，创建新的数据源适配器
2. **注册数据源**：在DataSourceFactory中注册新的数据源类型
3. **使用新数据源**：通过UnifiedDataManager指定新的数据源类型即可使用

## 组件间的配合关系

```
+-------------------+
| mystocks_main.py  |  <-- 用户入口
+--------+----------+
         |
         v
+--------+----------+
|UnifiedDataManager |  <-- 统一管理
+--------+----------+
         |
         v
+--------+----------+
|DataSourceFactory  |  <-- 创建数据源
+--------+----------+
         |
         v
+--------+----------+     +-------------------+
|   IDataSource     | <-- |具体数据源适配器实现|
+-------------------+     +-------------------+
```

- **mystocks_main.py** 调用 **UnifiedDataManager** 获取数据
- **UnifiedDataManager** 使用 **DataSourceFactory** 创建数据源
- **DataSourceFactory** 根据类型创建实现了 **IDataSource** 接口的具体适配器
- 具体适配器负责实际的数据获取工作

## 使用方法

### 基本使用

```python
from mystocks.manager.unified_data_manager import UnifiedDataManager

# 创建统一数据管理器
manager = UnifiedDataManager()

# 获取股票数据
stock_data = manager.get_stock_daily("600000", "2023-01-01", "2023-01-10")
print(stock_data)

# 获取指数数据
index_data = manager.get_index_daily("sh000001", "2023-01-01", "2023-01-10")
print(index_data)

# 使用列名映射器标准化数据
standardized_data = ColumnMapper.to_english(stock_data)  # 转为英文列名
chinese_data = ColumnMapper.to_chinese(standardized_data)  # 转为中文列名
```

### 新增功能使用

```python
# 获取实时数据
real_time = manager.get_source('akshare').get_real_time_data('600000')
print(real_time)

# 获取交易日历
calendar = manager.get_source('tushare').get_market_calendar('2023-01-01', '2023-01-31')
print(calendar)

# 获取财务数据
financial = manager.get_source('tushare').get_financial_data('600000', period='annual')
print(financial)

# 获取新闻数据
news = manager.get_source('akshare').get_news_data('600000', limit=5)
print(news)
```

### 切换数据源

```python
# 设置默认数据源
manager.set_default_source('baostock')

# 或者在获取数据时指定数据源
stock_data = manager.get_stock_daily("600000", "2023-01-01", "2023-01-10", source_type='akshare')
```

### 灵活的参数格式

系统支持多种格式的股票代码和日期：

```python
# 不同格式的股票代码
data1 = manager.get_stock_daily("600000", "2023-01-01", "2023-01-10")
data2 = manager.get_stock_daily("sh600000", "2023-01-01", "2023-01-10")
data3 = manager.get_stock_daily("600000.SH", "2023-01-01", "2023-01-10")

# 不同格式的日期
data4 = manager.get_stock_daily("600000", "2023-01-01", "2023-01-10")
data5 = manager.get_stock_daily("600000", "20230101", "20230110")
data6 = manager.get_stock_daily("600000", "2023/01/01", "2023/01/10")

# 使用天数而不是结束日期
data7 = manager.get_stock_daily("600000", "2023-01-01", days=10)
```

### 比较数据源

```python
# 比较不同数据源的数据
manager.compare_data_sources("600000", "2023-01-01", "2023-01-10")
```

## 扩展系统

### 添加新的数据源

#### 方法1：单个注册

```python
from mystocks.interfaces.data_source import IDataSource
from mystocks.factory.data_source_factory import DataSourceFactory

class NewDataSource(IDataSource):
    def __init__(self):
        # 初始化代码
        pass
        
    def get_stock_daily(self, symbol, start_date, end_date):
        # 实现获取股票数据的方法
        pass
        
    def get_real_time_data(self, symbol):
        # 实现获取实时数据的方法
        pass
        
    # 实现其他必要的方法...

# 注册新数据源
DataSourceFactory.register_source('new_source', NewDataSource)
```

#### 方法2：批量注册

```python
# 批量注册多个数据源
new_sources = {
    'tushare': TushareDataSource,
    'efinance': EfinanceDataSource,
    'custom': CustomDataSource
}
DataSourceFactory.register_multiple_sources(new_sources)

# 查看所有可用数据源
print(DataSourceFactory.get_available_sources())
```

#### 方法3：使用新数据源

```python
manager = UnifiedDataManager()
manager.set_default_source('tushare')
data = manager.get_stock_daily("600000", "2023-01-01", "2023-01-10")

# 或者指定数据源
data = manager.get_stock_daily("600000", "2023-01-01", "2023-01-10", source_type='tushare')
```

### 使用统一列名管理器

```python
from mystocks.utils.column_mapper import ColumnMapper

# 自动标准化不同数据源的列名
akshare_data = pd.DataFrame({"日期": ["2023-08-01"], "股票代码": ["600000"]})
baostock_data = pd.DataFrame({"date": ["2023-08-01"], "code": ["600000"]})

# 统一转换为英文标准列名
std_ak_data = ColumnMapper.to_english(akshare_data)
std_bs_data = ColumnMapper.to_english(baostock_data)

# 验证列名完整性
required_cols = ColumnMapper.get_standard_columns("stock_daily", "en")
is_valid, missing, extra = ColumnMapper.validate_columns(std_ak_data, required_cols)
print(f"验证结果: 通过={is_valid}, 缺失={missing}, 额外={extra}")
```

## 注意事项

- 确保已安装所需的依赖库（如akshare、baostock、tushare等）
- 不同数据源可能有不同的数据格式和字段名，系统会自动进行标准化处理
- 部分数据源可能需要网络连接或API密钥（如Tushare需要Token）
- 建议使用虚拟环境管理依赖
- 使用ColumnMapper可以自动处理不同数据源的列名差异

## 文档列表

- [QUICKSTART.md](./QUICKSTART.md) - 快速入门指南
- [CHANGELOG.md](./CHANGELOG.md) - 更新日志
- [ARCHITECTURE_VERIFICATION_REPORT.md](./ARCHITECTURE_VERIFICATION_REPORT.md) - 架构验证报告
- [EXTENSION_DEMO.md](./EXTENSION_DEMO.md) - 系统扩展功能演示
- [register_new_sources.py](./register_new_sources.py) - 新数据源注册演示脚本

## 支持的数据源

| 数据源 | 状态 | 特性 | 说明 |
|---------|------|---------|---------|
| AKShare | ✅ 可用 | 免费，数据丰富 | 默认数据源，支持股票、指数、基本面 |
| Baostock | ✅ 可用 | 免费，数据准确 | 适合量化分析，支持历史数据 |
| Tushare | ✅ 可用 | 需Token，专业 | 量化专业数据，支持财务数据 |
| EFinance | ⚠️ 模板 | 免费，实时 | 东方财富数据，需要实现适配器 |
| EasyQuotation | ⚠️ 模板 | 实时行情 | 实时股价数据，需要实现适配器 |
| 自定义的数据源 | ✅ 支持 | 灵活 | 支持爬虫等自定义数据源 |

## 免责声明加强

本软件仅供学习和研究使用。使用本软件进行实际交易的风险由用户自行承担。

作者不对任何投资损失承担责任。

## 风险提醒

**警告：量化交易存在风险，历史数据不代表未来表现。**

**请在充分了解风险的情况下使用本工具。**