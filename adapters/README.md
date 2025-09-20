# Financial适配器使用说明

Financial适配器是一个支持双数据源（efinance和easyquotation）的财务数据适配器，用于获取股票、指数等金融数据。

## 功能特性

1. **双数据源支持**：优先使用efinance获取数据，当efinance不可用时自动切换到easyquotation
2. **股票日线数据**：获取指定股票的历史日线数据
3. **股票基本信息**：获取股票的基本信息
4. **实时数据**：获取股票或市场的实时行情数据
5. **指数数据**：获取指数的日线数据和成分股信息
6. **财务数据**：获取股票的财务数据
7. **错误处理**：完善的错误处理机制，确保程序稳定性

## 安装依赖

在使用Financial适配器之前，请确保已安装以下依赖：

```bash
pip install efinance easyquotation pandas
```

## 使用方法

### 1. 导入适配器

```python
from adapters.financial_adapter import FinancialDataSource
```

### 2. 创建数据源实例

```python
# 创建Financial数据源实例
financial_ds = FinancialDataSource()
```

### 3. 获取股票日线数据

```python
# 获取股票日线数据
symbol = "000001"  # 股票代码
start_date = "2023-01-01"  # 开始日期
end_date = "2023-12-31"   # 结束日期
daily_data = financial_ds.get_stock_daily(symbol, start_date, end_date)
```

### 4. 获取股票基本信息

```python
# 获取股票基本信息
basic_info = financial_ds.get_stock_basic(symbol)
```

### 5. 获取实时数据

```python
# 获取特定股票的实时数据
real_time_data = financial_ds.get_real_time_data(symbol)

# 获取市场快照
market_snapshot = financial_ds.get_real_time_data(market="CN")
```

### 6. 获取指数数据

```python
# 获取指数日线数据
index_data = financial_ds.get_index_daily("000001", start_date, end_date)

# 获取指数成分股
components = financial_ds.get_index_components("000001")
```

### 7. 获取财务数据

```python
# 获取股票财务数据
financial_data = financial_ds.get_financial_data(symbol)
```

## 测试

可以运行测试文件验证适配器功能：

```bash
python adapters/test_financial_adapter.py
```

## 注意事项

1. **网络连接**：确保网络连接正常，以便从数据源获取数据
2. **API限制**：注意数据源的API调用频率限制
3. **数据格式**：返回的数据格式可能因数据源不同而有所差异
4. **错误处理**：适配器包含完善的错误处理机制，但建议在使用时仍进行异常处理

## 支持的数据源

1. **efinance**：主要数据源，提供丰富的金融数据
2. **easyquotation**：备用数据源，当efinance不可用时使用

## 返回数据格式

所有方法返回pandas DataFrame格式的数据，便于后续处理和分析。