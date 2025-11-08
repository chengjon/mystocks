# MyStocks 量化交易数据管理系统 - 项目概览

## 项目概述

MyStocks是一个专业的量化交易数据管理系统和Web管理平台，采用科学的数据分类体系和智能路由策略，实现多数据库协同工作。系统基于适配器模式和工厂模式构建统一的数据访问层，提供配置驱动的自动化管理，确保数据的高效存储、快速查询和实时监控。

### 核心特点
- **🌐 现代化Web管理平台**: 基于FastAPI + Vue 3的全栈架构
- **🤖 多智能体系统**: 集成ValueCell多智能体系统，支持实时监控、技术分析、多数据源集成
- **📊 双数据库存储策略**: TDengine(高频时序) + PostgreSQL(通用数据)
- **🔧 智能数据调用**: 统一接口规范，自动路由策略
- **🏗️ 先进数据流设计**: 适配器模式、工厂模式、策略模式、观察者模式

### 技术栈
- **后端语言**: Python 3.8+
- **数据库**: TDengine 3.3.x + PostgreSQL 17.x (TimescaleDB扩展)
- **Web框架**: FastAPI + Vue 3 + Element Plus
- **数据源**: akshare, baostock, tushare, efinance, 通达信等
- **GPU加速**: RAPIDS (cuDF/cuML) - 可选
- **监控**: Prometheus + Grafana (可选)

## 项目结构

```
/opt/claude/mystocks_spec/
├── core.py                          # 核心数据分类与路由策略
├── unified_manager.py               # 统一管理器(简化版包装器)
├── data_access.py                   # 统一数据访问层
├── monitoring.py                    # 独立监控与告警系统
├── system_demo.py                   # 完整功能演示
├── table_config.yaml                # 配置驱动表管理
├── requirements.txt                 # Python依赖
├── .env.example                     # 环境变量模板

├── adapters/                        # 数据源适配器模块
│   ├── tdx_adapter.py              # 通达信直连适配器
│   ├── akshare_adapter.py          # Akshare数据源适配器
│   ├── financial_adapter.py        # 财务数据适配器
│   ├── customer_adapter.py         # 自定义数据源适配器
│   ├── baostock_adapter.py         # Baostock数据源适配器
│   ├── tushare_adapter.py          # Tushare数据源适配器
│   └── byapi_adapter.py            # BYAPI数据源适配器

├── db_manager/                      # 数据库管理基础设施
│   └── database_manager.py         # 数据库连接管理

├── utils/                           # 工具模块
│   └── column_mapper.py            # 统一列名映射

├── gpu_api_system/                 # GPU加速回测系统(可选)
│   ├── services/                   # 核心服务
│   ├── tests/                      # 完整测试套件
│   └── wsl2_gpu_init.py           # WSL2 GPU初始化

├── web/                            # Web管理平台
│   ├── backend/                    # FastAPI后端
│   └── frontend/                   # Vue3前端
```

## 核心模块详解

### 1. 数据分类体系 (core.py)

系统采用5大数据分类体系，基于数据特性选择最优存储策略：

#### 第1类：市场数据 (Market Data)
- **TDengine专用**: Tick数据、分钟K线、深度数据
- **PostgreSQL**: 日线数据、实时行情快照

#### 第2类：参考数据 (Reference Data) 
- **PostgreSQL**: 股票信息、成分股信息、交易日历

#### 第3类：衍生数据 (Derived Data)
- **PostgreSQL+TimescaleDB**: 技术指标、量化因子、模型输出、交易信号

#### 第4类：交易数据 (Transaction Data)
- **PostgreSQL**: 订单记录、成交记录、持仓记录、账户资金

#### 第5类：元数据 (Meta Data)
- **PostgreSQL**: 数据源状态、任务调度、策略参数、系统配置

### 2. 统一管理器 (unified_manager.py)

提供简单易用的统一接口，所有操作都通过2行代码完成：

```python
# 保存数据 - 自动路由到最优数据库
manager.save_data_by_classification(
    DataClassification.TICK_DATA, tick_df, 'tick_600000'
)

# 加载数据 - 统一语法，自动优化
data = manager.load_data_by_classification(
    DataClassification.DAILY_KLINE, 'daily_kline', 
    filters={'symbol': '600000'}
)
```

### 3. 监控与告警系统 (monitoring.py)

- **操作监控**: 所有数据库操作自动记录
- **性能监控**: 慢查询检测、响应时间统计
- **质量监控**: 数据完整性、准确性、新鲜度检查
- **告警机制**: 多渠道告警(邮件、Webhook、日志)

### 4. 数据源适配器 (adapters/)

每个数据源都有专门的适配器实现统一接口：

- **tdx_adapter.py**: 通达信直连，无限流，多周期K线 (1058行)
- **financial_adapter.py**: 双数据源(efinance+easyquotation)，财务数据全能 (1078行) 
- **akshare_adapter.py**: 免费全面，历史数据研究首选 (510行)
- **customer_adapter.py**: 实时行情专用 (378行)
- **byapi_adapter.py**: REST API，涨跌停股池，技术指标 (625行)

## 构建和运行

### 环境要求
- **Python**: 3.8+
- **TDengine**: 3.3.x (高频时序数据专用)
- **PostgreSQL**: 17.x + TimescaleDB扩展
- **GPU**: NVIDIA GPU + CUDA 11.8+ (可选，用于GPU加速)

### 快速开始

#### 1. 环境配置
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件配置数据库连接
vim .env
```

#### 2. 安装依赖
```bash
# 基础依赖
pip install -r requirements.txt

# GPU加速依赖(可选)
pip install cupy-cuda12x cudf-cu12 cuml-cu12
```

#### 3. 系统初始化
```python
from unified_manager import MyStocksUnifiedManager
from core import DataClassification

# 创建统一管理器
manager = MyStocksUnifiedManager()

# 自动初始化系统
results = manager.initialize_system()
if results['config_loaded']:
    print("✅ 系统初始化成功!")
```

#### 4. 数据操作示例
```python
import pandas as pd
from datetime import datetime

# 保存股票基本信息(→ PostgreSQL)
symbols_data = pd.DataFrame({
    'symbol': ['600000', '000001'],
    'name': ['浦发银行', '平安银行'],
    'exchange': ['SH', 'SZ']
})
manager.save_data_by_classification(
    symbols_data, DataClassification.SYMBOLS_INFO
)

# 保存高频Tick数据(→ TDengine)  
tick_data = pd.DataFrame({
    'ts': [datetime.now()],
    'symbol': ['600000'],
    'price': [10.50],
    'volume': [1000]
})
manager.save_data_by_classification(
    tick_data, DataClassification.TICK_DATA
)
```

#### 5. Web平台启动
```bash
# 启动后端
cd web/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 启动前端(新终端)
cd web/frontend  
npm install && npm run dev

# 访问
# API文档: http://localhost:8000/api/docs
# 前端界面: http://localhost:5173
```

### 实时数据获取

```bash
# 使用efinance获取实时行情并保存
python run_realtime_market_saver.py

# 持续运行(每5分钟获取一次)
python run_realtime_market_saver.py --count -1 --interval 300
```

### GPU加速系统 (可选)

```bash
# 初始化GPU环境(WSL2环境)
cd gpu_api_system
python wsl2_gpu_init.py

# 启动GPU API服务
python main_server.py

# 运行性能测试
./run_tests.sh all
```

## 开发规范

### 代码风格
- **Python**: 遵循PEP 8规范，使用类型注解
- **配置驱动**: 所有表结构通过YAML配置管理
- **模块化设计**: 适配器模式，统一数据源接口
- **错误处理**: 完善的异常处理和日志记录
- **监控集成**: 所有操作自动记录到监控数据库

### 测试规范
- **单元测试**: pytest框架，覆盖核心功能
- **集成测试**: 数据库连接、适配器功能
- **性能测试**: GPU加速效果、缓存命中率
- **端到端测试**: 完整工作流程验证

### 部署规范
- **配置分离**: 环境变量和配置文件分离
- **数据库监控**: 健康检查、性能监控
- **日志管理**: 结构化日志，便于问题排查
- **备份策略**: 自动数据备份和恢复

## 核心功能模块

### 1. 实时监控系统 (ValueCell Phase 1)
- **告警规则**: 7种告警类型(价格突破、成交量激增等)
- **龙虎榜跟踪**: 实时监控大单交易
- **资金流向分析**: 主力资金流入流出统计
- **自定义规则**: 用户自定义监控条件

### 2. 技术分析系统 (ValueCell Phase 2)
- **26个技术指标**: 趋势(MA、MACD)、动量(RSI、KDJ)、波动(ATR)、成交量(OBV)
- **交易信号生成**: 基于技术指标的买卖信号
- **可视化图表**: 实时K线图和指标图表
- **批量计算**: 高效的批量指标计算

### 3. 多数据源集成 (ValueCell Phase 3)
- **优先级路由**: 智能数据源选择和故障转移
- **数据源健康监控**: 实时监控各数据源状态
- **公告监控**: 类似SEC Agent的官方公告监控
- **API限流管理**: 智能控制API调用频率

### 4. GPU加速系统 (Phase 4)
- **RAPIDS深度集成**: cuDF/cuML一体化GPU加速
- **15-20倍回测加速**: 高性能策略回测
- **智能三级缓存**: L1应用层 + L2 GPU内存 + L3 Redis，命中率>90%
- **WSL2支持**: 完整解决WSL2下RAPIDS GPU访问问题

## 扩展开发

### 添加新数据源
1. 实现`IDataSource`接口
2. 创建适配器类，继承基础适配器
3. 注册到DataSourceFactory
4. 在配置文件中添加连接参数

### 自定义技术指标
1. 在`core/technical_indicators.py`中实现指标逻辑
2. 添加到指标注册表
3. 配置计算参数和缓存策略

### Web页面开发
1. 后端: 在`web/backend/app/api/`中添加API端点
2. 前端: 在`web/frontend/src/components/`中添加Vue组件
3. 路由: 在`web/frontend/src/router/`中配置路由
4. 样式: 使用Element Plus组件库

## 性能优化

### 缓存策略
- **L1缓存**: 应用层LRU缓存，命中率>90%
- **L2缓存**: PostgreSQL查询缓存
- **L3缓存**: TDengine内存优化

### 数据库优化
- **TDengine**: 超高压缩比(20:1)，列式存储
- **PostgreSQL**: TimescaleDB扩展，自动分区
- **索引策略**: 基于查询模式的智能索引

### GPU优化
- **并行计算**: 多策略同时回测
- **内存管理**: 智能GPU内存分配和释放
- **批处理**: 大数据集分批GPU处理

## 最佳实践

### 数据管理
- 定期备份关键数据
- 监控数据质量和完整性
- 合理设置数据保留策略
- 及时清理过期日志

### 性能调优
- 定期分析慢查询
- 优化数据库连接池
- 调整缓存大小和TTL
- 监控GPU利用率

### 安全措施
- 定期更新依赖包
- 加密存储敏感信息
- 限制数据库访问权限
- 记录操作审计日志

## 故障排查

### 常见问题
1. **数据库连接失败**: 检查网络和配置
2. **数据源API限流**: 调整请求频率和重试策略
3. **GPU初始化失败**: 检查CUDA和驱动版本
4. **Web服务启动失败**: 确认端口占用和依赖

### 日志位置
- **系统日志**: `mystocks_system.log`
- **适配器日志**: `adapters/*.log`
- **Web日志**: `web/backend/logs/`
- **GPU日志**: `gpu_api_system/logs/`

### 监控面板
- **Grafana面板**: http://localhost:3000 (如果配置了)
- **TDengine控制台**: http://localhost:6041
- **PostgreSQL控制台**: pgAdmin (如果配置了)

## 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。贡献前请阅读贡献指南。

---

*本文档基于MyStocks v3.0.0生成，最后更新: 2025-11-08*