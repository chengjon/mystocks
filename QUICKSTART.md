# MyStocks 项目快速入门

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install akshare baostock pandas
# 可选：tushare（需要Token）
pip install tushare
```

### 2. 基本使用
```python
from mystocks.manager.unified_data_manager import UnifiedDataManager

# 创建管理器
manager = UnifiedDataManager()

# 获取股票数据
data = manager.get_stock_daily("600000", "2023-08-01", "2023-08-31")
print(data.head())
```

### 3. 高级功能
```python
# 使用列名映射器
from mystocks.utils.column_mapper import ColumnMapper
standardized_data = ColumnMapper.to_english(data)

# 切换数据源
tushare_data = manager.get_stock_daily("600000", "2023-08-01", "2023-08-31", source_type='tushare')

# 数据源比较
manager.compare_data_sources("600000", "2023-08-01", "2023-08-31")
```

## 📊 支持的数据源

| 数据源 | 免费 | 实时数据 | 历史数据 | 财务数据 |
|--------|------|----------|----------|----------|
| AKShare | ✅ | ✅ | ✅ | ✅ |
| Baostock | ✅ | ❌ | ✅ | ✅ |
| Tushare | Token | ✅ | ✅ | ✅ |

## 🏗️ 架构特点

- **适配器模式**：统一不同数据源接口
- **工厂模式**：动态创建数据源实例
- **模块化设计**：清晰的组件分离
- **可扩展性**：轻松添加新数据源
- **列名标准化**：自动处理列名差异

## 📁 核心组件

```
mystocks/
├── interfaces/         # 统一接口定义
├── adapters/          # 数据源适配器
├── factory/           # 数据源工厂
├── manager/           # 统一管理器
└── utils/             # 工具函数
```

## 🔧 扩展示例

### 添加新数据源
```python
from mystocks.interfaces.data_source import IDataSource
from mystocks.factory.data_source_factory import DataSourceFactory

class MyDataSource(IDataSource):
    def get_stock_daily(self, symbol, start_date, end_date):
        # 实现数据获取逻辑
        pass

# 注册新数据源
DataSourceFactory.register_source('my_source', MyDataSource)
```

### 使用统一列名
```python
from mystocks.utils.column_mapper import ColumnMapper

# 转换为英文标准列名
english_data = ColumnMapper.to_english(raw_data)

# 转换为中文列名
chinese_data = ColumnMapper.to_chinese(raw_data)
```

## 📖 详细文档

- [完整功能说明](./README.md)
- [架构验证报告](./ARCHITECTURE_VERIFICATION_REPORT.md)
- [扩展功能演示](./EXTENSION_DEMO.md)
- [更新日志](./CHANGELOG.md)

## 💡 应用场景

- **量化投资**：统一的数据获取接口
- **金融分析**：多数据源数据对比
- **投研系统**：标准化数据处理流程
- **学习研究**：设计模式实践案例

## ⚡ 性能特点

- **延迟导入**：减少启动时间
- **实例缓存**：避免重复创建
- **错误重试**：提高数据获取成功率
- **格式自适应**：智能处理不同格式

---

**开始使用MyStocks，让数据获取变得简单！**