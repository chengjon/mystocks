# MyStocks 快速开始指南

> **最新更新**: 2025-11-16  
> **版本**: 3.0.0  
> **主要功能**: 量化交易数据管理、Web界面、实时监控、AI策略系统

MyStocks是一个专业的量化交易数据管理系统和Web管理平台，支持多种数据源和双数据库架构。本文将帮助您快速了解系统功能并启动前端和后端服务。

## 系统概览

MyStocks 3.0.0引入了多项重大改进，特别是Week 3简化（从4数据库简化为2数据库）和系统功能-3集成。系统特点：

- **双数据库架构**: TDengine（高频时序数据）+ PostgreSQL（通用数据）
- **Web界面**: 基于FastAPI + Vue 3的全栈架构
- **实时监控**: 龙虎榜、资金流向、告警系统
- **多数据源**: 支持akshare、tushare、efinance等多个数据源
- **AI策略系统**: 集成AI策略分析、GPU加速和监控告警

## 1. 快速体验流程

### 启动前后端服务

1. **启动后端服务（FastAPI）**
```bash
# 进入后端目录
cd web/backend

# 使用自动端口范围检测功能启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --reload
```

2. **启动前端服务（Vue 3）**
```bash
# 进入前端目录
cd web/frontend

# 安装依赖（仅首次运行）
npm install

# 启动开发服务器（自动端口范围检测）
npm run dev
```

### 访问Web界面

- **前端界面**: http://localhost:3000 (或自动检测到的3000-3010范围内的可用端口)
- **API文档**: http://localhost:8000/docs (或自动检测到的8000-8010范围内的可用端口)

### 端口范围说明

为了避免端口冲突，系统实现了自动端口范围检测功能：

- **后端服务**: 自动在8000-8010端口范围内查找可用端口
- **前端服务**: 自动在3000-3010端口范围内查找可用端口

系统启动时会显示实际使用的端口号。

## 2. 核心功能导航

### 2.1 实时监控面板（系统功能）

访问前端首页后，您将看到实时监控面板：

- **实时行情**: 显示主要股票实时价格、涨跌幅、成交量
- **龙虎榜**: 监控大单交易情况和活跃股票
- **资金流向**: 查看主力资金和散户资金流向分析
- **自定义告警**: 设置价格突破、成交量激增等告警规则

### 2.2 技术分析系统（系统功能）

在左侧菜单中点击"技术分析"，可访问：

- **技术指标计算**: 26个技术指标（MA、MACD、RSI、KDJ等）
- **交易信号生成**: 基于技术指标的买卖信号识别
- **可视化图表**: 实时K线图和指标图表
- **批量指标计算**: 支持多只股票的指标计算

### 2.3 多数据源系统（系统功能）

在左侧菜单中点击"多数据源"，可查看：

- **数据源健康状态**: 监控各数据源API状态和响应时间
- **数据源优先级**: 智能数据源选择和故障转移
- **公告监控**: 重要上市公司公告监控（类似SEC Agent）
- **API限流管理**: 自动控制API调用频率

### 2.4 Web API接口

API文档地址：`http://localhost:8000/docs`

主要API端点包括：

- **市场数据API**: 实时行情、历史K线、资金流向
- **技术指标API**: 各类技术指标计算
- **监控系统API**: 告警规则、系统状态
- **多数据源API**: 数据源管理、故障转移

## 3. 数据功能测试

### 3.1 使用数据源适配器

系统支持多种数据源，您可以使用以下方式测试：

1. **akshare适配器**（免费，全面）
```python
from src.adapters.akshare_adapter import AkshareDataSource

adapter = AkshareDataSource()
stock_info = adapter.get_stock_basic()
print(f"获取到 {len(stock_info)} 只股票信息")
```

2. **efinance适配器**（实时行情）
```python
from adapters.customer_adapter import CustomerDataSource

adapter = CustomerDataSource(use_column_mapping=True)
realtime_data = adapter.get_market_realtime_quotes()
print(f"获取到 {len(realtime_data)} 只股票的实时行情")
```

3. **统一数据源工厂**
```python
from src.factories.data_source_factory import get_data_source

source = get_data_source()
stock_list = source.get_stock_list()
print(f"获取到 {len(stock_list)} 只股票信息")
```

### 3.2 数据存储与查询

系统实现了自动路由策略，根据数据特性选择最优数据库：

```python
from unified_manager import MyStocksUnifiedManager
from core import DataClassification

# 创建统一管理器
manager = MyStocksUnifiedManager()

# 保存数据（自动路由到最优数据库）
# - Tick数据 → TDengine（高频时序数据）
# - 日线数据 → PostgreSQL（历史分析数据）
# - 技术指标 → PostgreSQL + TimescaleDB（复杂查询）

# 查询数据（统一语法，自动优化）
data = manager.load_data_by_classification(
    DataClassification.DAILY_KLINE,
    filters={'symbol': '600000', 'trade_date': '>2024-01-01'},
    order_by='trade_date DESC',
    limit=100
)
```

## 4. 数据库架构（Week 3简化后）

### 4.1 双数据库架构

Week 3（2025-10-19）实现了数据库架构的重大简化，从4数据库缩减为2数据库：

- **TDengine**: 专用于高频时序数据（Tick数据、分钟K线、实时深度）
  - 极高压缩比（20:1）
  - 超强写入性能（毫秒级）
  - 列式存储优化

- **PostgreSQL + TimescaleDB**: 处理所有其他数据类型
  - 日线K线（TimescaleDB优化）
  - 技术指标和量化因子
  - 参考数据（股票信息等）
  - 交易数据（订单、持仓等）
  - 元数据（系统配置等）

### 4.2 数据分类体系

系统采用5大数据分类，自动路由到最优数据库：

1. **市场数据**: Tick数据、分钟K线、日线数据、深度数据
2. **参考数据**: 股票信息、成分股信息、交易日历
3. **衍生数据**: 技术指标、量化因子、模型输出
4. **交易数据**: 订单记录、成交记录、持仓记录
5. **元数据**: 数据源状态、任务调度、策略参数

## 5. GPU加速系统（Phase 4）

### 5.1 GPU加速功能

MyStocks包含一个完整的GPU加速量化交易API系统：

- **GPU回测引擎**: 使用RAPIDS（cuDF/cuML），实现15-20倍性能提升
- **实时市场数据处理**: 10,000条/秒的实时处理能力
- **GPU机器学习服务**: cuML算法库，15-44倍加速
- **智能三级缓存**: 命中率>90%，显著减少GPU内存访问延迟
- **WSL2支持**: 完全解决WSL2环境下RAPIDS GPU访问问题

### 5.2 GPU系统快速启动

```bash
# 进入GPU系统目录
cd gpu_api_system

# 测试GPU环境（WSL2需要初始化）
python wsl2_gpu_init.py

# 启动主服务
python main_server.py

# 运行测试
./run_tests.sh all
```

## 6. 进一步探索

### 6.1 示例脚本

项目提供了多个示例脚本，帮助您进一步了解系统功能：

```bash
# 系统功能演示
python scripts/runtime/system_demo.py

# 实时行情保存系统
python scripts/runtime/run_realtime_market_saver.py

# 单次运行保存数据
python scripts/runtime/run_realtime_market_saver.py

# 持续运行（每5分钟获取一次）
python scripts/runtime/run_realtime_market_saver.py --count -1 --interval 300
```

### 6.2 文档资源

项目提供了丰富的文档资源：

- **项目概览**: [README.md](./README.md) - 详细介绍项目架构和功能
- **IFLOW指南**: [docs/IFLOW.md](./docs/IFLOW.md) - 完整工作流程指南
- **架构设计**: [docs/architecture](./docs/architecture/) - 深度技术架构分析
- **API文档**: [docs/api](./docs/api/) - 完整的Web API文档

## 7. 常见问题解答

### Q: 如何确认前端和后端服务正常启动？
A: 
- 后端启动成功后会显示类似 `INFO: Started server process [12345]` 的信息
- 前端启动成功后会显示类似 `Local: http://localhost:3001/` 的信息
- 访问前端界面和API文档页面，确认页面可以正常加载

### Q: 端口被占用怎么办？
A: 
- 系统实现了自动端口范围检测功能
- 后端会在8000-8010范围内自动查找可用端口
- 前端会在3000-3010范围内自动查找可用端口
- 查看启动日志，确认实际使用的端口号

### Q: 数据库连接失败怎么处理？
A: 
- 检查.env文件中数据库连接配置是否正确
- 确认TDengine和PostgreSQL服务是否正常运行
- 查看后端日志，检查详细的错误信息

### Q: 如何启用GPU加速功能？
A: 
- 需要NVIDIA GPU和CUDA环境
- 运行 `python gpu_api_system/wsl2_gpu_init.py` 进行初始化
- 启动GPU API服务器：`python gpu_api_system/main_server.py`

## 8. 获取帮助

如果在使用过程中遇到问题，可以通过以下方式获取帮助：

1. **查看日志**: 检查控制台输出和日志文件
2. **参考文档**: 阅读项目中的详细文档
3. **社区支持**: 在GitHub上提交问题或参与讨论

---

**快速开始指南**  
**版本**: 3.0.0  
**最后更新**: 2025-11-16