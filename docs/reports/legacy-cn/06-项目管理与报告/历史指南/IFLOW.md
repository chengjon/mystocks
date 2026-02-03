# MyStocks 量化交易数据管理系统 - iFlow 工作指南

## 项目概览

MyStocks 是一个专业的量化交易数据管理系统和 Web 管理平台，采用科学的数据分类体系和智能路由策略，实现多数据库协同工作。系统基于适配器模式和工厂模式构建统一的数据访问层，提供配置驱动的自动化管理，确保数据的高效存储、快速查询和实时监控。

### 核心特点

- **现代化Web管理平台**: 基于FastAPI + Vue 3的全栈架构
- **多智能体系统**: 集成多智能体系统，支持实时监控、技术分析、多数据源集成
- **双数据库存储策略**: TDengine(高频时序) + PostgreSQL(通用数据)
- **智能数据调用**: 统一接口规范，自动路由策略
- **先进数据流设计**: 适配器模式、工厂模式、策略模式、观察者模式
- **GPU加速支持**: RAPIDS (cuDF/cuML) 深度集成，支持WSL2环境
- **统一错误处理**: 提供一致的错误处理策略和日志记录功能
- **Vue + FastAPI 架构**: 已完成前端重构，支持实时推送和现代化UI

### 技术栈

- **后端语言**: Python 3.12+
- **数据库**: TDengine 3.3.x + PostgreSQL 17.x (TimescaleDB扩展)
- **Web框架**: FastAPI + Vue 3 + Element Plus + Pinia + Vue Router
- **数据源**: akshare, baostock, tushare, efinance, 通达信等
- **GPU加速**: RAPIDS (cuDF/cuML) - 支持WSL2环境
- **监控**: Prometheus + Grafana (可选)
- **实时通信**: Socket.IO, SSE (Server-Sent Events)

## 项目结构

### 📁 重组后的科学目录结构 (2025-11-09)

项目已完成全面重组，从42个杂乱的根目录精简到13个科学组织的目录，符合Python最佳实践。

```
/opt/claude/mystocks_spec/
├── README.md                          # 项目主文档
├── CLAUDE.md                          # Claude Code集成指南
├── CHANGELOG.md                       # 版本变更日志
├── LICENSE                            # MIT许可证
├── requirements.txt                   # Python依赖清单
├── core.py                            # 核心模块入口点
├── unified_manager.py                 # 统一管理器入口点
├── data_access.py                     # 数据访问入口点
├── monitoring.py                      # 监控模块入口点
├── ai_strategy_analyzer.py            # AI策略分析器
├── gpu_ai_integration.py              # GPU AI集成管理器
├── ai_monitoring_optimizer.py         # AI监控优化器
└── __init__.py                        # Python包标识

├── src/                               # 📦 所有源代码
│   ├── adapters/                      # 数据源适配器模块 (7个核心适配器)
│   │   ├── tdx_adapter.py             # 通达信直连适配器 (1058行)
│   │   ├── byapi_adapter.py           # BYAPI数据源适配器 (625行)
│   │   ├── financial_adapter.py       # 财务数据适配器 (1078行)
│   │   ├── akshare_adapter.py         # Akshare数据源适配器 (510行)
│   │   ├── baostock_adapter.py        # Baostock数据源适配器 (257行)
│   │   ├── customer_adapter.py        # 自定义数据源适配器 (378行)
│   │   └── tushare_adapter.py         # Tushare数据源适配器 (199行)
│   │
│   ├── core/                          # 核心管理类
│   │   ├── config_driven_table_manager.py  # 配置驱动表管理
│   │   ├── data_classification.py           # 数据分类枚举
│   │   └── data_storage_strategy.py         # 存储策略路由
│   │
│   ├── data_access/                   # 数据库访问层
│   │   ├── tdengine_access.py         # TDengine高频时序数据访问
│   │   └── postgresql_access.py       # PostgreSQL通用数据访问
│   │
│   ├── storage/                       # 存储层
│   │   └── database/
│   │       ├── connection_manager.py  # 数据库连接管理
│   │       ├── database_manager.py    # 数据库表管理
│   │       └── db_utils.py            # 数据库工具函数
│   │
│   ├── monitoring/                    # 监控和告警
│   │   ├── monitoring_database.py     # 监控数据库
│   │   ├── performance_monitor.py     # 性能监控
│   │   ├── data_quality_monitor.py    # 数据质量监控
│   │   └── alert_manager.py           # 告警管理器
│   │
│   ├── interfaces/                    # 接口定义
│   │   └── data_source_interface.py   # DataSourceInterface统一接口
│   │
│   ├── database/                      # 数据库相关
│   │   ├── database_service.py        # 数据库服务层
│   │   └── mock_data_storage.py       # Mock数据存储层
│   │
│   ├── data_sources/                  # 数据源实现
│   │   ├── mock_data_source.py        # Mock数据源实现
│   │   └── real_data_source.py        # 真实数据源实现
│   │
│   ├── factories/                     # 工厂类
│   │   └── data_source_factory.py     # 数据源工厂
│   │
│   ├── utils/                         # 工具模块
│   │   └── column_mapper.py           # 统一列名映射
│   │
│   ├── gpu/                           # GPU加速模块
│   ├── api/                           # API接口
│   ├── db_manager/                    # 兼容层 (与storage/database兼容)
│   ├── ml_strategy/                   # 机器学习策略
│   ├── backup_recovery/               # 备份恢复
│   ├── contract_testing/              # 契约测试
│   ├── data_sources/                  # 数据导入模块
│   ├── database_optimization/         # 数据库优化
│   ├── reporting/                     # 报告生成
│   └── visualization/                 # 可视化工具
│
├── web/                               # 🌐 Web管理平台
│   ├── backend/                       # FastAPI后端
│   │   ├── app/
│   │   │   ├── api/                   # API端点
│   │   │   │   ├── endpoints/         # 详细API端点
│   │   │   │   │   ├── data.py        # 数据API
│   │   │   │   │   ├── auth.py        # 认证API
│   │   │   │   │   ├── system.py      # 系统API
│   │   │   │   │   ├── indicators.py  # 指标API
│   │   │   │   │   ├── market.py      # 市场API
│   │   │   │   │   ├── tdx.py         # 通达信API
│   │   │   │   │   ├── metrics.py     # 指标API
│   │   │   │   │   ├── tasks.py       # 任务API
│   │   │   │   │   ├── wencai.py      # 问财API
│   │   │   │   │   ├── stock_search.py # 股票搜索API
│   │   │   │   │   ├── watchlist.py   # 自选股API
│   │   │   │   │   ├── tradingview.py # TradingView API
│   │   │   │   │   ├── notification.py # 通知API
│   │   │   │   │   ├── ml.py          # 机器学习API
│   │   │   │   │   ├── market_v2.py   # 市场API V2
│   │   │   │   │   ├── strategy.py    # 策略API
│   │   │   │   │   ├── monitoring.py  # 监控API
│   │   │   │   │   ├── technical_analysis.py # 技术分析API
│   │   │   │   │   ├── multi_source.py # 多数据源API
│   │   │   │   │   ├── announcement.py # 公告API
│   │   │   │   │   ├── strategy_management.py # 策略管理API
│   │   │   │   │   ├── risk_management.py # 风险管理API
│   │   │   │   │   ├── sse_endpoints.py # SSE实时推送API
│   │   │   │   │   ├── cache.py       # 缓存管理API
│   │   │   │   │   └── pool_monitoring.py # 连接池监控API
│   │   │   ├── core/                  # 核心服务
│   │   │   │   ├── config.py          # 配置管理
│   │   │   │   ├── database.py        # 数据库连接管理
│   │   │   │   ├── cache_eviction.py  # 缓存淘汰调度器
│   │   │   │   ├── socketio_manager.py # Socket.IO管理器
│   │   │   │   └── openapi_config.py  # OpenAPI配置
│   │   │   ├── models/                # 数据模型
│   │   │   ├── services/              # 业务服务
│   │   │   └── main.py                # 应用入口
│   │   ├── requirements.txt           # 后端依赖
│   │   └── Dockerfile                 # Docker配置
│   │
│   └── frontend/                      # Vue 3前端
│       ├── src/
│       │   ├── components/            # Vue组件
│       │   │   ├── AI/                # AI相关组件
│       │   │   ├── Monitoring/        # 监控相关组件
│       │   │   ├── GPU/               # GPU相关组件
│       │   │   └── common/            # 通用组件
│       │   ├── views/                 # 页面视图
│       │   │   ├── Home.vue           # 首页
│       │   │   ├── AI/                # AI相关页面
│       │   │   ├── Monitoring/        # 监控相关页面
│       │   │   ├── GPU/               # GPU相关页面
│       │   │   └── Settings.vue       # 设置页面
│       │   ├── router/                # 路由配置
│       │   ├── stores/                # Pinia状态管理
│       │   ├── services/              # API调用服务
│       │   ├── utils/                 # 工具函数
│       │   ├── styles/                # 样式文件
│       │   ├── assets/                # 静态资源
│       │   └── main.ts                # 应用入口
│       ├── public/                    # 静态资源
│       ├── package.json               # 前端依赖
│       ├── tsconfig.json              # TypeScript配置
│       ├── vite.config.ts             # Vite构建配置
│       └── .env                       # 环境变量
│
├── config/                            # ⚙️ 配置文件
│   ├── table_config.yaml              # 完整表结构配置
│   ├── adapter_priority_config.yaml   # 适配器优先级配置
│   ├── docker-compose.tdengine.yml    # TDengine Docker配置
│   ├── docker-compose.postgresql.yml  # PostgreSQL Docker配置
│   └── docker-compose.yml             # Web平台Docker配置
│
├── scripts/                           # 🔧 脚本工具
│   ├── tests/                         # 测试脚本
│   ├── runtime/                       # 运行时脚本
│   ├── database/                      # 数据库脚本
│   └── dev/                           # 开发工具
│
├── docs/                              # 📚 完整文档
│   ├── guides/                        # 用户指南
│   │   ├── Vue_FastAPI_AI_Strategy_Implementation_Guide.md    # AI策略实施指南
│   │   ├── Vue_FastAPI_Monitoring_Implementation_Guide.md     # 监控系统实施指南
│   │   ├── Vue_FastAPI_GPU_System_Implementation_Guide.md     # GPU系统实施指南
│   │   ├── Vue_FastAPI_Deployment_Implementation_Guide.md     # 部署实施指南
│   │   ├── Vue_FastAPI_Code_Reference_Guide.md                # 代码参考手册
│   │   └── Vue_FastAPI_Implementation_Master_Guide.md         # 实施总指南
│   ├── architecture/                  # 架构设计文档
│   ├── api/                           # API文档
│   └── features/                      # 功能特性文档
│
├── tests/                             # 🧪 测试代码
├── examples/                          # 📖 示例代码
├── logs/                              # 📝 日志目录
└── data/                              # 💾 数据文件

├── share/                             # 📚 共享文档和指南
│   ├── README.md                      # 共享文档说明
│   ├── AI_STRATEGY_GUIDE.md           # AI策略实施指南
│   ├── GPU_SYSTEM_GUIDE.md            # GPU系统实施指南
│   ├── MONITORING_GUIDE.md            # 监控系统实施指南
│   ├── DEPLOYMENT_GUIDE.md            # 部署指南
│   └── CODE_REFERENCE.md              # 代码参考手册
│
└── .archive/                          # 📦 归档内容 (历史代码/文档)
    ├── old_code/                      # 旧代码备份
    ├── old_docs/                      # 旧文档备份
    └── ARCHIVE_INDEX.md               # 归档索引
```

## 数据分类体系

### 5大数据分类

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

### 数据库分工与存储方案 (Week 3简化后)

| 数据库 | 专业定位 | 适用数据 | 核心优势 |
|--------|----------|----------|----------|
| **TDengine** | 高频时序数据专用库 | Tick数据、分钟K线、实时深度 | 极高压缩比(20:1)、超强写入性能、列式存储 |
| **PostgreSQL + TimescaleDB** | 通用数据仓库+分析引擎 | 日线K线、技术指标、量化因子、参考数据、交易数据、元数据 | 自动分区、复杂查询、ACID事务、JSON支持 |

**Week 3简化成果**:
- ✅ MySQL数据迁移到PostgreSQL（18张表，299行数据）
- ✅ Redis移除（配置的db1为空）
- ✅ 系统复杂度降低50%

## 核心架构组件

### 1. 统一管理器 (unified_manager.py)

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

### 2. 数据源适配器 (adapters/)

每个数据源都有专门的适配器实现统一接口：

- **tdx_adapter.py**: 通达信直连，无限流，多周期K线 (1058行)
- **financial_adapter.py**: 双数据源(efinance+easyquotation)，财务数据全能 (1078行)
- **akshare_adapter.py**: 养生全面，历史数据研究首选 (510行)
- **byapi_adapter.py**: REST API，涨跌停股池，技术指标 (625行)
- **customer_adapter.py**: 实时行情专用 (378行)
- **baostock_adapter.py**: 高质量历史数据 (257行)
- **tushare_adapter.py**: 专业级，需token (199行)

### 3. 统一数据源接口 (interfaces/data_source_interface.py)

定义了所有数据源必须实现的统一接口：

```python
class DataSourceInterface(ABC):
    @abstractmethod
    def get_stock_list(self, params: Optional[Dict] = None) -> List[Dict]:
        """获取股票列表"""
        pass

    @abstractmethod
    def get_real_time_quote(self, stock_code: str) -> Dict:
        """获取实时行情"""
        pass

    @abstractmethod
    def get_technical_indicators(self, stock_code: str, start_date: str, end_date: str) -> List[Dict]:
        """获取技术指标"""
        pass

    # ... 其他方法
```

### 4. 数据源工厂模式 (factories/data_source_factory.py)

通过配置动态切换Mock/真实数据源：

```python
# 工厂类实现单例模式
class DataSourceFactory:
    def _initialize_data_source(self) -> None:
        """
        初始化数据源
        根据环境变量USE_MOCK_DATA决定使用Mock数据还是真实数据
        """
        use_mock = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'

        if use_mock:
            self._data_source = MockDataSource()
        else:
            self._data_source = RealDataSource()

    def get_data_source(self) -> DataSourceInterface:
        """
        获取数据源实例
        """
        if self._data_source is None:
            self._initialize_data_source()
        return self._data_source
```

### 5. Mock与真实数据源实现

- **MockDataSource**: 实现所有接口方法，返回模拟数据，支持数据存储验证
- **RealDataSource**: 实现所有接口方法，调用数据库服务层访问真实数据

### 6. 数据库服务层 (database/database_service.py)

提供统一的数据库访问接口，适配双数据库架构：

- **故障转移机制**: 根据配置文件定义的优先级自动切换数据源
- **适配器统一调用**: 提供统一入口访问所有数据适配器
- **数据存储一致性**: Mock数据也支持存储验证

### 7. Mock数据存储层 (database/mock_data_storage.py)

- 使用SQLite模拟真实数据库存储
- 支持技术指标、实时行情、股票信息等多种数据类型
- 用于测试数据落地逻辑

## 优化特性

### 1. 统一适配器调用方式

通过`get_data_from_adapter`方法统一访问所有数据适配器：

```python
result = source.get_data_from_adapter('akshare', 'get_stock_list')
```

### 2. 适配器优先级与故障转移

- 配置文件定义适配器优先级
- 自动在失败适配器之间切换
- 提供结果有效性检查

### 3. Mock数据存储一致性

- Mock数据在模拟数据库中正确存储
- 与真实数据具有相同的存储逻辑
- 便于测试数据落地功能

### 4. Vue + FastAPI 架构优化

- **现代前端**: 使用Vue 3 + TypeScript + Element Plus构建
- **状态管理**: 使用Pinia进行状态管理
- **路由系统**: 使用Vue Router进行页面路由
- **实时通信**: 集成Socket.IO和SSE进行实时数据推送
- **API设计**: 完整的RESTful API设计和WebSocket实时通信

## 构建和运行

### 环境要求
- **Python**: 3.12+
- **TDengine**: 3.3.x (高频时序数据专用)
- **PostgreSQL**: 17.x + TimescaleDB扩展
- **GPU**: NVIDIA GPU + CUDA 12.x+ (可选，用于GPU加速)
- **Node.js**: 18+ (Web前端)

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

# 后端依赖
cd web/backend
pip install -r requirements.txt

# 前端依赖
cd web/frontend
npm install
```

#### 3. GPU加速依赖(可选)
```bash
# RTX 2080 GPU加速支持
pip install cupy-cuda12x cudf-cu12 cuml-cu12
```

#### 4. 系统初始化
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

#### 5. Web平台启动
```bash
# 启动后端
cd web/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload

# 启动前端(新终端)
cd web/frontend
npm run dev

# 访问
# API文档: http://localhost:8888/api/docs
# 前端界面: http://localhost:5173
```

## 数据源适配器使用

### 基础使用示例

```python
# 使用统一数据源工厂
from src.factories.data_source_factory import get_data_source
import os

# 设置环境变量控制使用Mock/真实数据
os.environ['USE_MOCK_DATA'] = 'false'  # 使用真实数据
# os.environ['USE_MOCK_DATA'] = 'true'   # 使用Mock数据

# 获取数据源实例
source = get_data_source()

# 获取股票列表
stock_list = source.get_stock_list()
print(f"获取到 {len(stock_list)} 只股票信息")

# 获取实时行情
realtime_quote = source.get_real_time_quote('600000')
print(f"获取到实时行情: {realtime_quote}")

# 获取技术指标
technical_indicators = source.get_technical_indicators('600000', '2024-01-01', '2024-12-31')
print(f"获取到技术指标: {len(technical_indicators)} 条记录")
```

### 统一适配器调用

```python
# 统一调用不同适配器
result = source.get_data_from_adapter('akshare', 'get_stock_list')
print(f"适配器调用结果: {result}")

# 使用故障转移机制
result = source.get_data_with_failover('realtime_quote', 'get_stock_daily', symbol='000001.SZ')
print(f"故障转移调用结果: {result}")
```

## 核心功能模块

### 1. 实时监控系统
- **告警规则**: 7种告警类型(价格突破、成交量激增等)
- **龙虎榜跟踪**: 实时监控大单交易
- **资金流向分析**: 主力资金流入流出统计
- **自定义规则**: 用户自定义监控条件

### 2. 技术分析系统
- **26个技术指标**: 趋势(MA、MACD)、动量(RSI、KDJ)、波动(ATR)、成交量(OBV)
- **交易信号生成**: 基于技术指标的买卖信号
- **可视化图表**: 实时K线图和指标图表
- **批量计算**: 高效的批量指标计算

### 3. 多数据源集成
- **优先级路由**: 智能数据源选择和故障转移
- **数据源健康监控**: 实时监控各数据源状态
- **公告监控**: 类似SEC Agent的官方公告监控
- **API限流管理**: 智能控制API调用频率

### 4. GPU加速系统 (Phase 4)
- **RAPIDS深度集成**: cuDF/cuML一体化GPU加速
- **15-20倍回测加速**: 高性能策略回测
- **智能三级缓存**: L1应用层 + L2 GPU内存 + L3 Redis，命中率>90%
- **WSL2支持**: 完整解决WSL2下RAPIDS GPU访问问题

### 5. Vue + FastAPI 现代化前端 (最新集成)
- **Vue 3 + TypeScript**: 现代化前端框架
- **Element Plus**: 企业级UI组件库
- **Pinia**: 状态管理
- **Vue Router**: 前端路由
- **实时推送**: Socket.IO + SSE 实时数据推送
- **响应式设计**: 适配各种屏幕尺寸

## Web API 使用

### 核心API端点

#### 实时监控系统 (Phase 1)
```
GET  /api/monitoring/alert-rules          # 获取告警规则
POST /api/monitoring/alert-rules          # 创建告警规则
GET  /api/monitoring/realtime             # 获取实时行情
POST /api/monitoring/realtime/fetch       # 获取最新实时数据
GET  /api/monitoring/dragon-tiger         # 获取龙虎榜
GET  /api/monitoring/summary              # 获取监控摘要
```

#### 技术分析系统 (Phase 2)
```
GET  /api/technical/{symbol}/indicators   # 获取所有技术指标
GET  /api/technical/{symbol}/trend        # 获取趋势指标
GET  /api/technical/{symbol}/momentum     # 获取动量指标
GET  /api/technical/{symbol}/volatility   # 获取波动性指标
GET  /api/technical/{symbol}/signals      # 获取交易信号
POST /api/technical/batch/indicators      # 批量获取指标
```

#### 多数据源系统 (Phase 3)
```
GET  /api/multi-source/health             # 获取所有数据源健康状态
GET  /api/multi-source/realtime-quote     # 获取实时行情（多数据源）
GET  /api/multi-source/fund-flow          # 获取资金流向（多数据源）
GET  /api/announcement/today              # 获取今日公告
GET  /api/announcement/important          # 获取重要公告
POST /api/announcement/monitor/evaluate   # 评估监控规则
```

#### Vue + FastAPI 新增端点
```
GET  /api/socketio-status                 # Socket.IO服务器状态
GET  /api/csrf-token                      # 获取CSRF Token
GET  /api/stock-search                    # 股票搜索
GET  /api/watchlist                       # 自选股管理
GET  /api/tradingview                     # TradingView widgets
GET  /api/notification                    # 邮件通知
GET  /api/machine-learning                # 机器学习预测
GET  /api/strategy                        # 股票策略筛选
GET  /api/technical-analysis              # 技术分析
GET  /api/pool-monitoring                 # 连接池监控
GET  /api/cache                          # 缓存管理
```

### API使用示例

```python
import requests

# 获取实时行情
response = requests.get('http://localhost:8888/api/monitoring/realtime')
real_time_data = response.json()

# 获取技术指标
response = requests.get('http://localhost:8888/api/technical/600000/indicators')
indicators = response.json()

# 获取数据源健康状态
response = requests.get('http://localhost:8888/api/multi-source/health')
health_status = response.json()

# 获取CSRF Token（用于修改操作）
response = requests.get('http://localhost:8888/api/csrf-token')
csrf_token = response.json()['csrf_token']

# 使用CSRF Token进行POST请求
headers = {
    'x-csrf-token': csrf_token,
    'Content-Type': 'application/json'
}
response = requests.post('http://localhost:8888/api/monitoring/alert-rules',
                        json={'rule_name': 'My Rule', 'rule_type': 'limit_up'},
                        headers=headers)
```

## 开发规范

### 代码风格
- **Python**: 遵循PEP 8规范，使用类型注解
- **TypeScript**: 遵循TypeScript最佳实践，使用类型注解
- **配置驱动**: 所有表结构通过YAML配置管理
- **模块化设计**: 适配器模式，统一数据源接口
- **错误处理**: 完善的异常处理和日志记录
- **监控集成**: 所有操作自动记录到监控数据库

### 测试规范
- **单元测试**: pytest框架，覆盖核心功能
- **集成测试**: 数据库连接、适配器功能
- **性能测试**: GPU加速效果、缓存命中率
- **端到端测试**: 完整工作流程验证
- **契约测试**: API接口契约验证
- **前端测试**: Playwright端到端测试

### 部署规范
- **配置分离**: 环境变量和配置文件分离
- **数据库监控**: 健康检查、性能监控
- **日志管理**: 结构化日志，便于问题排查
- **备份策略**: 自动数据备份和恢复
- **CSRF保护**: 所有修改操作需要CSRF token验证

## 扩展开发

### 添加新数据源
1. 实现`DataSourceInterface`接口
2. 创建适配器类，继承基础适配器
3. 注册到DataSourceFactory
4. 在配置文件中添加连接参数

### 自定义技术指标
1. 在`src/monitoring/technical_indicators.py`中实现指标逻辑
2. 添加到指标注册表
3. 配置计算参数和缓存策略

### Web页面开发
1. 后端: 在`web/backend/app/api/`中添加API端点
2. 前端: 在`web/frontend/src/components/`中添加Vue组件
3. 路由: 在`web/frontend/src/router/`中配置路由
4. 状态管理: 在`web/frontend/src/stores/`中添加Pinia store
5. 样式: 使用Element Plus组件库

### Vue + FastAPI 集成开发
1. **API端点**: 在`web/backend/app/api/endpoints/`中添加新端点
2. **前端服务**: 在`web/frontend/src/services/`中添加API服务
3. **组件开发**: 在`web/frontend/src/components/`中添加Vue组件
4. **状态管理**: 在`web/frontend/src/stores/`中添加Pinia store
5. **路由配置**: 在`web/frontend/src/router/`中配置路由

### Claude Code Hooks开发
1. 在`.claude/hooks/`中创建脚本
2. 添加执行权限：`chmod +x script_name.sh`
3. 配置到`.claude/config.json`
4. 测试Hooks功能

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
- **智能缓存**: 三级缓存系统，命中率>90%

### 前端性能优化
- **代码分割**: 使用Vite进行代码分割
- **懒加载**: 路由和组件懒加载
- **缓存策略**: HTTP缓存和浏览器缓存
- **资源优化**: 图片压缩，字体预加载

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
- CSRF保护：所有修改操作需要CSRF token

### 前端安全
- 验证所有用户输入
- 使用HTTPS传输
- 实施CSP策略
- 保护API端点
- 防止XSS和CSRF攻击

## 故障排查

### 常见问题
1. **数据库连接失败**: 检查网络和配置
2. **TDengine初始化错误**: 已修复，参考TDENGINE_FIX_COMPLETION_REPORT.md
3. **GPU初始化失败**: 检查CUDA和驱动版本，WSL2需要特殊配置
4. **Web服务启动失败**: 确认端口占用和依赖
5. **数据源API限流**: 调整请求频率和重试策略
6. **CSRF错误**: 检查前端是否正确获取和使用CSRF token
7. **Socket.IO连接问题**: 检查后端Socket.IO服务状态

### 日志位置
- **系统日志**: `mystocks_system.log`
- **适配器日志**: `adapters/*.log`
- **Web日志**: `web/backend/logs/`
- **GPU日志**: `gpu_api_system/logs/`
- **Hooks日志**: `.claude/logs/`

### 监控面板
- **Grafana面板**: http://localhost:3000 (如果配置了)
- **TDengine控制台**: http://localhost:6041
- **PostgreSQL控制台**: pgAdmin (如果配置了)
- **Claude Code**: http://localhost:3001 (如果配置了)

## 项目版本历史

### v3.1.0 (2025-11-16)
- **Vue + FastAPI 架构完成**: 前端采用Vue 3 + TypeScript现代化架构
- **实时推送系统**: 集成Socket.IO和SSE实时数据推送
- **CSRF安全增强**: 添加CSRF token保护所有修改操作
- **API端点扩展**: 新增多个功能模块API端点
- **文档完善**: 创建完整的Vue + FastAPI实施指南套件

### v3.0.0 (2025-10-19)
- **Week 3简化**: 数据库架构从4库简化为2库
- **集成**: 完成Phase 1-3功能迁移
- **项目重组**: 从42个目录精简到13个科学组织目录
- **Web界面**: 完整的FastAPI + Vue 3管理平台
- **GPU支持**: RAPIDS加速系统，包含WSL2支持

### v2.0.0
- **重构**: 完全基于配置驱动的系统
- **适配器模式**: 统一数据源访问接口
- **监控体系**: 完整的操作、性能、质量监控

### v1.0.0
- **基础版本**: 基本的双数据库架构
- **核心功能**: 数据存储、查询、基础监控

## 快速参考

### 启动命令速查
```bash
# 数据库服务
docker-compose up -d tdengine postgresql

# 系统初始化
python scripts/runtime/system_demo.py

# 后端服务 (端口范围: 8000-8010)
cd web/backend && python -m uvicorn app.main:app --reload
# 系统会自动在8000-8010范围内查找可用端口并启动

# 前端服务 (端口范围: 3000-3010)
cd web/frontend && npm run dev
# 系统会自动在3000-3010范围内查找可用端口并启动

# GPU服务
cd src/gpu/api_system && python main_server.py

# 实时数据
python run_realtime_market_saver.py --count -1 --interval 300

# 测试系统
pytest tests/ -v
npm run test  # 前端测试

# Claude Code
.claude/hooks/session-start-task-master-injector.sh
```

### 文件导入速查
```python
# 核心模块
from src.core import MyStocksUnifiedManager, DataClassification

# 数据源适配器
from src.adapters import AkshareDataSource, TdxDataSource

# 数据库访问
from src.data_access import TDengineDataAccess, PostgreSQLDataAccess

# 统一数据源
from src.factories.data_source_factory import get_data_source

# 监控
from src.monitoring import PerformanceMonitor, AlertManager

# AI策略
from ai_strategy_analyzer import AIStrategyAnalyzer

# GPU系统
from gpu_ai_integration import GPUAIIntegrationManager

# Web后端
from web.backend.app.main import app

# Vue前端
from web.frontend.src.stores import useStrategyStore, useMonitoringStore
from web.frontend.src.services import strategyService, monitoringService
```

### 配置检查
```bash
# 环境变量
cat .env

# 数据库连接
python scripts/database/check_tdengine_tables.py
python scripts/database/check_postgresql_tables.py

# GPU状态
nvidia-smi
python src/gpu/api_system/wsl2_gpu_init.py

# 前端依赖
cd web/frontend && npm list
```

## 支持和联系

- **项目状态**: 最新状态参考 `PROJECT_STATUS_QUICK_INDEX.md`
- **详细文档**: 参见 `docs/` 目录下的完整文档
- **变更日志**: 详见 `CHANGELOG.md`
- **问题排查**: 参考各模块的故障排查文档
- **Claude Code**: 参见 `CLAUDE.md` 集成指南
- **Vue + FastAPI 指南**: 参见 `docs/guides/` 目录下的实施指南套件

---

*本文档基于MyStocks v3.1.0生成，最后更新: 2025-11-16*
