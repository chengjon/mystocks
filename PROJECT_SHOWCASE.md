# MyStocks 项目展示

## 项目简介

MyStocks 是一个基于**适配器模式**和**工厂模式**设计的多数据源股票数据获取系统。该项目旨在为量化交易研究者和金融分析师提供一个统一、简洁且可扩展的数据访问接口，屏蔽不同数据源之间的技术差异。

## 核心优势

### 1. 统一接口设计
- 通过适配器模式封装不同数据源的接口差异
- 用户只需学习一套API即可访问所有数据源
- 降低学习成本，提高开发效率

### 2. 动态扩展能力
- 工厂模式支持运行时动态注册新数据源
- 提供标准化的适配器接口模板
- 支持批量注册多个数据源

### 3. 智能参数处理
- 自动识别和转换不同格式的股票代码
- 支持多种日期格式
- 灵活的日期范围指定方式

### 4. 数据标准化
- 统一列名管理器自动处理不同数据源的列名差异
- 数据格式标准化确保一致性
- 编码标准化处理中文字符问题

## 系统架构图

```
MyStocks 系统架构

+-------------------+     +-------------------+
|   Application     |     |     Utils         |
|  (main.py等)      |     | (日期处理、代码   |
+-------------------+     |  格式化等工具)    |
         |                +-------------------+
         |                         |
+-------------------+     +-------------------+
|  UnifiedDataManager|<---|   ColumnMapper    |
|   (统一数据管理器) |     |  (列名标准化工具) |
+-------------------+     +-------------------+
         |
         |    +-------------------+
         +--->| DataSourceFactory |
              |   (数据源工厂)    |
              +-------------------+
                       |
        +--------------+--------------+
        |              |              |
+----------------+ +----------------+ +----------------+
| AkshareAdapter | | BaostockAdapter| | TushareAdapter |
| (AKShare适配器)| | (Baostock适配器)| | (Tushare适配器)|
+----------------+ +----------------+ +----------------+
```

## 快速开始

### 安装依赖
```bash
pip install akshare baostock tushare
```

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
```

### 切换数据源
```python
# 设置默认数据源
manager.set_default_source('baostock')

# 或者在获取数据时指定数据源
stock_data = manager.get_stock_daily("600000", "2023-01-01", "2023-01-10", source_type='akshare')
```

### 扩展新数据源
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
        
    # 实现其他必要的方法...

# 注册新数据源
DataSourceFactory.register_source('new_source', NewDataSource)
```

## 支持的数据源

| 数据源 | 状态 | 特性 | 说明 |
|---------|------|---------|---------|
| AKShare | ✅ 可用 | 免费，数据丰富 | 默认数据源，支持股票、指数、基本面 |
| Baostock | ✅ 可用 | 免费，数据准确 | 适合量化分析，支持历史数据 |
| Tushare | ✅ 可用 | 需Token，专业 | 量化专业数据，支持财务数据 |
| EFinance | ⚠️ 模板 | 免费，实时 | 东方财富数据，需要实现适配器 |
| EasyQuotation | ⚠️ 模板 | 实时行情 | 实时股价数据，需要实现适配器 |
| 自定义的数据源 | ✅ 支持 | 灵活 | 支持爬虫等自定义数据源 |

## 技术验证

### 架构验证
- ✅ 适配器模式验证通过
- ✅ 工厂模式验证通过
- ✅ 统一管理层验证通过
- ✅ 数据源比较功能验证通过

### 功能验证
- ✅ 股票日线数据获取
- ✅ 指数日线数据获取
- ✅ 实时数据获取
- ✅ 交易日历数据获取
- ✅ 财务数据获取
- ✅ 新闻数据获取

### 环境验证
- ✅ Python 3.12 兼容性验证通过
- ✅ Python 3.13 兼容性验证通过
- ✅ 多数据源环境兼容性验证通过

## 项目文档

- [README.md](./README.md) - 项目介绍和使用说明
- [QUICKSTART.md](./QUICKSTART.md) - 快速入门指南
- [CHANGELOG.md](./CHANGELOG.md) - 更新日志
- [ARCHITECTURE_VERIFICATION_REPORT.md](./ARCHITECTURE_VERIFICATION_REPORT.md) - 架构验证报告
- [ARCHITECTURE_VALIDATION_SUMMARY.md](./ARCHITECTURE_VALIDATION_SUMMARY.md) - 架构验证总结报告
- [EXTENSION_DEMO.md](./EXTENSION_DEMO.md) - 系统扩展功能演示
- [FINAL_VALIDATION_REPORT.md](./FINAL_VALIDATION_REPORT.md) - 系统最终验证报告
- [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) - 项目总结报告
- [register_new_sources.py](./register_new_sources.py) - 新数据源注册演示脚本

## 项目价值

### 对开发者
- 提供标准化的数据访问接口
- 减少重复开发工作
- 提高开发效率
- 降低维护成本

### 对研究者
- 简化数据获取流程
- 统一数据格式标准
- 支持多数据源对比
- 提供丰富的数据类型

### 对量化交易
- 提供高质量的历史数据
- 支持实时数据获取
- 保证数据的一致性
- 提高策略开发效率

## 未来发展方向

1. **功能增强**：添加更多数据源支持（如Wind、Choice等）
2. **性能优化**：实现数据缓存机制和并发数据获取
3. **用户体验**：开发可视化界面和RESTful API
4. **技术完善**：完善单元测试和性能监控功能

## 总结

MyStocks项目成功实现了基于设计模式的多数据源股票数据获取系统，通过清晰的架构设计、完整的功能实现和全面的测试验证，为用户提供了一个统一、简洁且可扩展的数据访问解决方案。系统具有良好的可维护性、可扩展性和稳定性，能够满足量化交易研究者和金融分析师的数据获取需求。