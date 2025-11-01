# 数据源适配器模块

**创建人**: JohnC & Claude
**版本**: 2.0.0
**批准日期**: 2025-08-01
**最后修订**: 2025-10-16
**本次修订内容**: 数据源适配器说明

---

数据源适配器模块实现了统一的数据接口，支持多种金融数据源的访问。采用适配器模式设计，为不同的数据源提供统一的API接口。

## 📁 模块文件说明

### 核心适配器文件

#### 1. `financial_adapter.py`
- **功能**: 综合财务数据适配器，支持双数据源
- **数据源**: efinance（主要）+ easyquotation（备用）
- **特性**: 自动切换数据源、完善错误处理
- **用途**: 股票日线、实时行情、指数数据、财务数据

#### 2. `akshare_adapter.py`
- **功能**: Akshare数据源适配器
- **数据源**: akshare
- **特性**: 重试机制、超时控制
- **用途**: 股票数据、指数数据、宏观经济数据

#### 3. `baostock_adapter.py`
- **功能**: BaoStock数据源适配器
- **数据源**: baostock
- **特性**: 高质量历史数据
- **用途**: 股票历史数据、复权数据、财务数据

#### 4. `customer_adapter.py`
- **功能**: 自定义数据源适配器
- **数据源**: efinance + easyquotation
- **特性**: 双库管理、智能切换
- **用途**: 实时行情数据获取

#### 5. `tushare_adapter.py`
- **功能**: Tushare数据源适配器
- **数据源**: tushare
- **特性**: 专业级数据接口
- **用途**: 股票、基金、股指期货、宏观数据

#### 6. `tdx_adapter.py` ⭐ **v2.1新增**
- **功能**: 通达信(TDX)数据源适配器
- **数据源**: pytdx (本地库)
- **特性**:
  - 直连通达信服务器，无API限流
  - 支持多周期K线 (1m/5m/15m/30m/1h/1d)
  - 智能服务器切换和重试
  - 详细文档见 `README_TDX.md`
- **用途**: 实时行情、多周期K线、指数数据
- **辅助库**: `temp/pytdx/` (本地pytdx代码，可二次开发)

#### 7. `byapi_adapter.py` ⭐ **v2.1新增**
- **功能**: Byapi (biyingapi.com) 数据源适配器
- **数据源**: biyingapi.com API
- **特性**:
  - 内置频率控制 (300请求/分钟)
  - 支持涨停/跌停股池查询
  - 技术指标内置计算
  - API许可证: `04C01BF1-7F2F-41A3-B470-1F81F14B1FC8`
- **用途**: 实时行情、K线数据、财务报表、技术指标
- **辅助文件**: `byapi/` 子目录
  - `byapi_info_all.md` - 完整API文档
  - `byapi_mapping_updated.py` - 字段映射表
  - `api_info.json` - API元数据
  - `README.md` - Byapi使用指南

### 测试和示例文件

#### 6. `test_financial_adapter.py`
- **功能**: financial_adapter测试脚本
- **用途**: 验证财务适配器功能

#### 7. `test_customer_adapter.py`
- **功能**: customer_adapter测试脚本
- **用途**: 验证客户适配器功能

#### 8. `financial_adapter_example.py`
- **功能**: financial_adapter使用示例
- **用途**: 展示完整使用流程

#### 9. `simple_test.py`
- **功能**: 简单测试脚本
- **用途**: 快速功能验证

## 🏗️ 设计架构

### 适配器模式实现

```python
# 统一接口定义
from mystocks.interfaces.data_source import IDataSource

# 各适配器都实现相同接口
class AkshareDataSource(IDataSource):
    def get_stock_daily(self, symbol, start_date, end_date): ...
    def get_real_time_data(self, symbol): ...
    def get_stock_basic(self, symbol): ...
```

### 工厂模式集成

适配器与 `mystocks.factory` 模块配合使用：

```python
from mystocks.factory.data_source_factory import DataSourceFactory

# 通过工厂创建适配器实例
ds = DataSourceFactory.create_data_source('akshare')
```

## 📊 数据源特性对比

| 适配器 | 数据源 | 实时数据 | 历史数据 | 财务数据 | 免费使用 | 稳定性 | v2.1核心 |
|--------|--------|----------|----------|----------|----------|--------|---------|
| **tdx_adapter** ⭐ | pytdx | ✅ | ✅ | ❌ | ✅ | 极高 | ✅ |
| **byapi_adapter** ⭐ | biyingapi.com | ✅ | ✅ | ✅ | ✅ | 高 | ✅ |
| financial_adapter | efinance + easyquotation | ✅ | ✅ | ✅ | ✅ | 高 | ❌ |
| akshare_adapter | akshare | ✅ | ✅ | ✅ | ✅ | 高 | ❌ |
| baostock_adapter | baostock | ❌ | ✅ | ✅ | ✅ | 中 | ❌ |
| customer_adapter | efinance + easyquotation | ✅ | ❌ | ❌ | ✅ | 高 | ❌ |
| tushare_adapter | tushare | ✅ | ✅ | ✅ | 部分 | 高 | ❌ |

## 🔧 依赖安装

```bash
# 核心依赖
pip install pandas numpy

# 各数据源依赖
pip install efinance        # financial_adapter, customer_adapter
pip install easyquotation   # financial_adapter, customer_adapter
pip install akshare         # akshare_adapter
pip install baostock        # baostock_adapter
pip install tushare         # tushare_adapter

# 或者全部安装
pip install efinance easyquotation akshare baostock tushare pandas numpy
```

## 🚀 快速开始

### 1. 基本使用模式

```python
# 1. 导入适配器
from adapters.financial_adapter import FinancialDataSource

# 2. 创建实例
ds = FinancialDataSource()

# 3. 获取数据
data = ds.get_stock_daily("000001", "2024-01-01", "2024-12-31")
```

### 2. 与v2.0系统集成

```python
# 与MyStocks v2.0系统集成使用
from unified_manager import MyStocksUnifiedManager
from core import DataClassification

manager = MyStocksUnifiedManager()

# 通过适配器获取数据，然后保存到相应数据库
ds = FinancialDataSource()
data = ds.get_stock_daily("000001", "2024-01-01", "2024-12-31")

# 自动路由到PostgreSQL存储
manager.save_data_by_classification(data, DataClassification.DAILY_KLINE)
```

## 📈 使用建议

### 数据源选择策略

1. **实时行情数据**: 推荐 `financial_adapter` 或 `customer_adapter`
2. **历史数据研究**: 推荐 `akshare_adapter` 或 `baostock_adapter`
3. **专业级数据**: 推荐 `tushare_adapter`（需要token）
4. **综合使用**: 推荐 `financial_adapter`（双数据源保障）

### 性能优化建议

1. **批量获取**: 尽量批量获取数据，减少API调用次数
2. **缓存机制**: 对频繁访问的数据进行缓存
3. **错误重试**: 利用内置的重试机制处理网络不稳定
4. **数据验证**: 获取数据后进行基本的数据质量检查

## 🔍 测试验证

运行测试脚本验证适配器功能：

```bash
# 测试financial_adapter
python adapters/test_financial_adapter.py

# 测试customer_adapter
python adapters/test_customer_adapter.py

# 简单功能测试
python adapters/simple_test.py
```

## ⚠️ 注意事项

1. **网络依赖**: 所有适配器都需要网络连接
2. **API限制**: 注意各数据源的调用频率限制
3. **数据格式**: 不同数据源返回的数据格式可能有差异
4. **异常处理**: 建议在使用时增加适当的异常处理
5. **Token配置**: tushare_adapter需要配置API token

更多详细使用示例和参数配置，请参考 [example.md](./example.md)。