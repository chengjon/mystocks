# MyStocks 数据源架构 - 接口标准化与数据源解耦

## 1. 概述

MyStocks系统现在采用"接口标准化+数据源解耦"的架构，实现了Mock数据和真实数据的统一接口管理。通过该架构，系统可以：

- 一次对接，平滑切换数据源
- 前端调用逻辑与具体数据源无关
- 仅需通过配置切换数据源，避免重复修改对接代码

## 2. 核心组件

### 2.1 统一接口标准 (`src/interfaces/data_source_interface.py`)

定义了所有数据源必须实现的抽象接口，包括：

- 股票相关接口：`get_stock_list`, `get_stock_detail`, `get_real_time_quote` 等
- 技术分析接口：`get_all_indicators`, `get_trend_indicators`, `get_momentum_indicators` 等
- 监控相关接口：`get_realtime_alerts`, `get_monitoring_summary`, `get_monitoring_status` 等
- 问财筛选接口：`get_wencai_queries`, `execute_query`, `get_query_results` 等
- 策略管理接口：`get_strategy_definitions`, `run_strategy_single`, `get_strategy_results` 等

### 2.2 Mock数据源实现 (`src/data_sources/mock_data_source.py`)

- 实现了统一接口标准
- 封装了现有的Mock函数
- 作为格式基准，确保输出格式一致性

### 2.3 真实数据源实现 (`src/data_sources/real_data_source.py`)

- 实现了统一接口标准
- 对接数据库服务
- 将真实数据转换为与Mock一致的格式

### 2.4 数据源工厂 (`src/factories/data_source_factory.py`)

- 通过环境变量 `USE_MOCK_DATA` 动态切换数据源
- 提供全局访问点
- 支持运行时动态切换

### 2.5 格式兼容性校验 (`src/utils/data_source_validator.py`)

- 批量校验Mock与真实数据源的格式一致性
- 提供详细的差异报告
- 支持自动化测试

## 3. 使用方法

### 3.1 在应用中使用数据源

```python
from src.factories.data_source_factory import get_data_source

# 获取数据源实例
data_source = get_data_source()

# 调用接口方法
stock_list = data_source.get_stock_list({"limit": 20})
real_time_data = data_source.get_real_time_quote("600519")
indicators = data_source.get_all_indicators("600519")
```

### 3.2 切换数据源

```python
from src.factories.data_source_factory import data_source_factory

# 切换到Mock数据源
data_source_factory.switch_to_mock()

# 切换到真实数据源
data_source_factory.switch_to_real()

# 检查当前数据源类型
is_using_mock = data_source_factory.is_using_mock()
```

### 3.3 通过环境变量配置

```bash
# 使用Mock数据
export USE_MOCK_DATA=true

# 使用真实数据
export USE_MOCK_DATA=false
```

## 4. 实现效果

通过这种架构，系统实现了：

1. **接口标准化**：所有数据源遵循统一接口规范
2. **数据源解耦**：前端调用与具体数据源实现分离
3. **平滑切换**：通过配置即可切换Mock/真实数据源
4. **格式一致**：Mock数据与真实数据输出格式完全对齐
5. **易于扩展**：可轻松添加新的数据源实现
6. **质量保障**：通过校验工具确保格式兼容性

## 5. 优势

- **开发效率**：一次对接，多数据源复用
- **测试便利**：Mock数据快速测试，真实数据验证
- **部署灵活**：根据环境选择合适的数据源
- **维护简单**：统一接口降低维护成本
- **扩展性强**：易于集成新的数据源

## 6. 示例代码

参见 `src/examples/data_source_usage_example.py` 了解具体使用方法。