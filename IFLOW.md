# MyStocks 量化交易数据管理系统 - iFlow 交互指南

## 项目概述

MyStocks 是一个专业的量化交易数据管理系统和 Web 管理平台，采用科学的数据分类体系和智能路由策略，实现多数据库协同工作。系统基于适配器模式和工厂模式构建统一的数据访问层，提供配置驱动的自动化管理，确保数据的高效存储、快速查询和实时监控。

### 项目基本信息

- **项目类型**: Python 代码项目 (量化交易数据管理系统)
- **当前版本**: v1.3.1 (2025-11-12)
- **Python 版本**: 3.12+ (当前使用 3.12.11)
- **创建者**: JohnC & Claude
- **许可证**: MIT
- **Git 仓库**: git@github.com:chengjon/mystocks.git

### 核心技术栈

- **后端语言**: Python 3.12+
- **Web 框架**: FastAPI + Vue 3 + Element Plus
- **数据库**: TDengine 3.3.x + PostgreSQL 17.x (TimescaleDB扩展)
- **数据源**: akshare, baostock, tushare, efinance, 通达信等
- **GPU 加速**: RAPIDS (cuDF/cuML) - 支持 WSL2 环境
- **监控**: Prometheus + Grafana (可选)
- **开发工具**: Claude Code Hooks 系统 v2.0

### 项目特点

- **🌐 现代化Web管理平台**: 基于 FastAPI + Vue 3 的全栈架构
- **🤖 多智能体系统**: 集成多智能体系统，支持实时监控、技术分析、多数据源集成
- **📊 双数据库存储策略**: TDengine(高频时序) + PostgreSQL(通用数据)
- **🔧 智能数据调用**: 统一接口规范，自动路由策略
- **🏗️ 先进数据流设计**: 适配器模式、工厂模式、策略模式、观察者模式
- **🚀 GPU 加速支持**: RAPIDS 深度集成，支持 WSL2 环境

## 项目结构

### 📁 重组后的科学目录结构 (2025-11-09)

项目已完成全面重组，从42个杂乱的根目录精简到13个科学组织的目录，符合 Python 最佳实践。

```
/opt/claude/mystocks_spec/
├── 📄 核心入口文件
│   ├── README.md                    # 项目主文档
│   ├── CLAUDE.md                    # Claude Code 集成指南
│   ├── CHANGELOG.md                 # 版本变更日志
│   ├── LICENSE                      # MIT 许可证
│   ├── requirements.txt             # Python 依赖清单
│   ├── core.py                      # 核心模块入口点
│   ├── unified_manager.py           # 统一管理器入口点
│   ├── data_access.py               # 数据访问入口点
│   ├── monitoring.py                # 监控模块入口点
│   └── __init__.py                  # Python 包标识
│
├── 📦 src/                          # 所有源代码
│   ├── adapters/                    # 数据源适配器 (7个核心适配器)
│   ├── core/                        # 核心管理类
│   ├── data_access/                 # 数据库访问层
│   ├── storage/                     # 存储层 (database/)
│   ├── monitoring/                  # 监控和告警
│   ├── interfaces/                  # 接口定义
│   ├── utils/                       # 工具函数
│   ├── gpu/                         # GPU 加速模块
│   ├── api/                         # API 接口
│   ├── db_manager/                  # 兼容层
│   ├── ml_strategy/                 # 机器学习策略
│   ├── backup_recovery/             # 备份恢复
│   ├── contract_testing/            # 契约测试
│   ├── data_sources/                # 数据导入模块
│   ├── database_optimization/       # 数据库优化
│   ├── reporting/                   # 报告生成
│   └── visualization/               # 可视化工具
│
├── 🌐 web/                          # Web 管理平台
│   ├── backend/                     # FastAPI 后端
│   │   ├── app/
│   │   │   ├── api/                 # API 端点
│   │   │   ├── core/                # 核心服务
│   │   │   ├── models/              # 数据模型
│   │   │   ├── services/            # 业务服务
│   │   │   └── main.py              # 应用入口
│   │   ├── requirements.txt         # 后端依赖
│   │   └── Dockerfile               # Docker 配置
│   │
│   └── frontend/                    # Vue 3 前端
│       ├── src/
│       │   ├── components/          # Vue 组件
│       │   ├── views/               # 页面视图
│       │   ├── router/              # 路由配置
│       │   ├── stores/              # Pinia 状态管理
│       │   ├── services/            # API 调用服务
│       │   └── main.ts              # 应用入口
│       ├── package.json             # 前端依赖
│       ├── vite.config.ts           # Vite 构建配置
│       └── .env                     # 环境变量
│
├── ⚙️ config/                        # 配置文件
│   ├── table_config.yaml            # 完整表结构配置
│   ├── docker-compose.tdengine.yml  # TDengine Docker 配置
│   ├── docker-compose.postgresql.yml # PostgreSQL Docker 配置
│   └── docker-compose.yml           # Web 平台 Docker 配置
│
├── 🔧 scripts/                       # 脚本工具
│   ├── tests/                        # 测试脚本
│   ├── runtime/                      # 运行时脚本
│   ├── database/                     # 数据库脚本
│   ├── dev/                          # 开发工具
│   └── automation/                   # 自动化脚本
│
├── 📚 docs/                          # 完整文档
│   ├── guides/                       # 用户指南
│   ├── architecture/                 # 架构设计文档
│   ├── api/                          # API 文档
│   ├── features/                     # 功能特性文档
│   └── reports/                      # 项目报告
│
├── 🧪 tests/                         # 测试代码
├── 📖 examples/                      # 示例代码
├── 📝 logs/                          # 日志目录
├── 💾 data/                          # 数据文件
└── 📦 .archive/                      # 归档内容
    ├── old_code/                     # 旧代码备份
    ├── old_docs/                     # 旧文档备份
    └── ARCHIVE_INDEX.md              # 归档索引
```

## 核心架构设计

### 数据分类体系

系统采用 5 大数据分类体系，基于数据特性选择最优存储策略：

#### 1. 市场数据 (Market Data)
- **TDengine 专用**: Tick 数据、分钟 K 线、深度数据
- **PostgreSQL**: 日线数据、实时行情快照

#### 2. 参考数据 (Reference Data) 
- **PostgreSQL**: 股票信息、成分股信息、交易日历

#### 3. 衍生数据 (Derived Data)
- **PostgreSQL + TimescaleDB**: 技术指标、量化因子、模型输出、交易信号

#### 4. 交易数据 (Transaction Data)
- **PostgreSQL**: 订单记录、成交记录、持仓记录、账户资金

#### 5. 元数据 (Meta Data)
- **PostgreSQL**: 数据源状态、任务调度、策略参数、系统配置

### 数据库分工与存储方案

| 数据库 | 专业定位 | 适用数据 | 核心优势 |
|--------|----------|----------|----------|
| **TDengine** | 高频时序数据专用库 | Tick 数据、分钟 K 线、实时深度 | 极高压缩比(20:1)、超强写入性能、列式存储 |
| **PostgreSQL + TimescaleDB** | 通用数据仓库+分析引擎 | 日线 K 线、技术指标、量化因子、参考数据、交易数据、元数据 | 自动分区、复杂查询、ACID 事务、JSON 支持 |

**Week 3 简化成果**:
- ✅ MySQL 数据迁移到 PostgreSQL（18张表，299行数据）
- ✅ Redis 移除（配置的 db1 为空）
- ✅ 系统复杂度降低 50%

## 核心功能模块

### 1. 统一管理器 (unified_manager.py)

提供简单易用的统一接口，所有操作都通过 2 行代码完成：

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

- **tdx_adapter.py**: 通达信直连，无限流，多周期 K 线 (1058行)
- **financial_adapter.py**: 双数据源(efinance+easyquotation)，财务数据全能 (1078行) 
- **akshare_adapter.py**: 免费全面，历史数据研究首选 (510行)
- **byapi_adapter.py**: REST API，涨跌停股池，技术指标 (625行)
- **customer_adapter.py**: 实时行情专用 (378行)
- **baostock_adapter.py**: 高质量历史数据 (257行)
- **tushare_adapter.py**: 专业级，需 token (199行)

### 3. 监控与告警系统

- **操作监控**: 所有数据库操作自动记录
- **性能监控**: 慢查询检测、响应时间统计
- **质量监控**: 数据完整性、准确性、新鲜度检查
- **告警机制**: 多渠道告警(邮件、Webhook、日志)

### 4. GPU 加速系统

- **RAPIDS 深度集成**: cuDF/cuML 一体化 GPU 加速
- **15-20倍回测加速**: 高性能策略回测
- **智能三级缓存**: L1 应用层 + L2 GPU 内存 + L3 Redis，命中率>90%
- **WSL2 支持**: 完整解决 WSL2 下 RAPIDS GPU 访问问题
- **测试覆盖**: 160+ 测试用例，100% 测试覆盖率

### 5. Claude Code Hooks 系统

**生产就绪的 7 个 Hooks**:
1. **user-prompt-submit-skill-activation.sh** - 智能技能激活
2. **post-tool-use-file-edit-tracker.sh** - 文件编辑追踪
3. **post-tool-use-database-schema-validator.sh** - 数据库架构验证
4. **post-tool-use-document-organizer.sh** - 文档组织检查
5. **stop-python-quality-gate.sh** - Python 代码质量门禁
6. **session-start-task-master-injector.sh** - 会话开始任务注入
7. **session-end-cleanup.sh** - 会话结束清理

**状态**: ✅ 100% 完成，12/13 测试通过(92%成功率)

## 构建和运行

### 环境要求

- **Python**: 3.12+ (当前使用 3.12.11)
- **TDengine**: 3.3.x (高频时序数据专用)
- **PostgreSQL**: 17.x + TimescaleDB 扩展
- **GPU**: NVIDIA GPU + CUDA 12.x+ (可选，用于 GPU 加速)
- **Node.js**: 16+ (Web 前端)

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

#### 3. GPU 加速依赖(可选)
```bash
# RTX 2080 GPU 加速支持
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

#### 5. Web 平台启动
```bash
# 启动后端
cd web/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload

# 启动前端(新终端)
cd web/frontend  
npm run dev

# 访问
# API 文档: http://localhost:8888/api/docs
# 前端界面: http://localhost:5173
```

#### 6. 实时数据获取
```bash
# 使用 efinance 获取实时行情并保存
python run_realtime_market_saver.py

# 持续运行(每5分钟获取一次)
python run_realtime_market_saver.py --count -1 --interval 300
```

#### 7. GPU 加速系统 (可选)
```bash
# 初始化 GPU 环境(WSL2 环境)
cd src/gpu/api_system
python wsl2_gpu_init.py

# 启动 GPU API 服务
python main_server.py

# 运行性能测试 (160+用例，100%覆盖率)
./run_tests.sh all
```

## 数据源适配器使用

### 基础使用示例

```python
# 使用 akshare 适配器
from src.adapters.akshare_adapter import AkshareDataSource
import pandas as pd

# 创建数据源实例
adapter = AkshareDataSource()

# 获取股票基本信息
stock_info = adapter.get_stock_basic()
print(f"获取到 {len(stock_info)} 只股票信息")

# 获取日线数据
daily_data = adapter.get_stock_daily('600000', '2024-01-01', '2024-12-31')
print(f"获取到 {len(daily_data)} 条日线数据")

# 通过统一管理器保存数据
from unified_manager import MyStocksUnifiedManager
from core import DataClassification

manager = MyStocksUnifiedManager()
manager.save_data_by_classification(daily_data, DataClassification.DAILY_KLINE)
```

### 财务数据适配器

```python
# 使用财务数据适配器(双数据源)
from src.adapters.financial_adapter import FinancialDataSource

adapter = FinancialDataSource()

# 获取股票财务数据
financial_data = adapter.get_stock_financial('600000')
print(f"获取到财务数据: {financial_data.shape}")

# 获取基本面数据
basic_info = adapter.get_stock_basic_info('600000')
print(f"获取到基本面信息: {basic_info}")
```

### 通达信适配器

```python
# 使用通达信适配器(直连，无限流)
from src.adapters.tdx_adapter import TdxDataSource

adapter = TdxDataSource()

# 获取多周期 K 线数据
kline_data = adapter.get_kline_data('600000', '1min', '2024-01-01', '2024-12-31')
print(f"获取到1分钟 K 线数据: {len(kline_data)} 条")
```

## Web API 使用

### 核心 API 端点

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

### API 使用示例

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
```

## 核心功能特性

### 1. 实时监控系统
- **告警规则**: 7种告警类型(价格突破、成交量激增等)
- **龙虎榜跟踪**: 实时监控大单交易
- **资金流向分析**: 主力资金流入流出统计
- **自定义规则**: 用户自定义监控条件

### 2. 技术分析系统
- **26个技术指标**: 趋势(MA、MACD)、动量(RSI、KDJ)、波动(ATR)、成交量(OBV)
- **交易信号生成**: 基于技术指标的买卖信号
- **可视化图表**: 实时 K 线图和指标图表
- **批量计算**: 高效的批量指标计算

### 3. 多数据源集成
- **优先级路由**: 智能数据源选择和故障转移
- **数据源健康监控**: 实时监控各数据源状态
- **公告监控**: 类似 SEC Agent 的官方公告监控
- **API 限流管理**: 智能控制 API 调用频率

### 4. GPU 加速系统 (Phase 4)
- **RAPIDS 深度集成**: cuDF/cuML 一体化 GPU 加速
- **15-20倍回测加速**: 高性能策略回测
- **智能三级缓存**: L1 应用层 + L2 GPU 内存 + L3 Redis，命中率>90%
- **WSL2 支持**: 完整解决 WSL2 下 RAPIDS GPU 访问问题
- **测试覆盖**: 160+ 测试用例，100% 测试覆盖率

## 开发规范

### 代码风格
- **Python**: 遵循 PEP 8 规范，使用类型注解
- **配置驱动**: 所有表结构通过 YAML 配置管理
- **模块化设计**: 适配器模式，统一数据源接口
- **错误处理**: 完善的异常处理和日志记录
- **监控集成**: 所有操作自动记录到监控数据库

### 测试规范
- **单元测试**: pytest 框架，覆盖核心功能
- **集成测试**: 数据库连接、适配器功能
- **性能测试**: GPU 加速效果、缓存命中率
- **端到端测试**: 完整工作流程验证
- **契约测试**: API 接口契约验证

### 部署规范
- **配置分离**: 环境变量和配置文件分离
- **数据库监控**: 健康检查、性能监控
- **日志管理**: 结构化日志，便于问题排查
- **备份策略**: 自动数据备份和恢复

### Claude Code 集成
- **Hooks 系统**: 7 个生产就绪的自动化脚本
- **Skills 配置**: 8 个专业技能模板
- **Agents 配置**: 9 个专门代理配置
- **质量门禁**: 自动化代码质量检查

## 性能优化

### 缓存策略
- **L1 缓存**: 应用层 LRU 缓存，命中率>90%
- **L2 缓存**: PostgreSQL 查询缓存
- **L3 缓存**: TDengine 内存优化

### 数据库优化
- **TDengine**: 超高压缩比(20:1)，列式存储
- **PostgreSQL**: TimescaleDB 扩展，自动分区
- **索引策略**: 基于查询模式的智能索引

### GPU 优化
- **并行计算**: 多策略同时回测
- **内存管理**: 智能 GPU 内存分配和释放
- **批处理**: 大数据集分批 GPU 处理
- **智能缓存**: 三级缓存系统，命中率>90%

## 故障排查

### 常见问题
1. **数据库连接失败**: 检查网络和配置
2. **TDengine 初始化错误**: 已修复，参考 TDENGINE_FIX_COMPLETION_REPORT.md
3. **GPU 初始化失败**: 检查 CUDA 和驱动版本，WSL2 需要特殊配置
4. **Web 服务启动失败**: 确认端口占用和依赖
5. **数据源 API 限流**: 调整请求频率和重试策略

### 日志位置
- **系统日志**: `mystocks_system.log`
- **适配器日志**: `adapters/*.log`
- **Web 日志**: `web/backend/logs/`
- **GPU 日志**: `gpu_api_system/logs/`
- **Hooks 日志**: `.claude/logs/`

### 监控面板
- **Grafana 面板**: http://localhost:3000 (如果配置了)
- **TDengine 控制台**: http://localhost:6041
- **PostgreSQL 控制台**: pgAdmin (如果配置了)
- **Claude Code**: http://localhost:3001 (如果配置了)

## 项目版本历史

### v1.3.1 (2025-11-12)
- **Claude Code Hooks 系统完善**: 修复 PostToolUse:Write Hooks JSON 错误处理
- **测试验证**: 6 个测试场景全部通过
- **文档更新**: 详细修复历史和配置指南
- **架构优化**: 文档结构优化，路径修正，版本信息更新

### v1.3.0 (2025-11-04)
- **GPU 缓存优化**: 6 大核心优化策略，命中率从 80% 提升至 90%+
- **WSL2 GPU 支持**: 完全解决 WSL2 环境下 RAPIDS GPU 访问问题
- **测试系统**: 160+ 测试用例，100% 测试覆盖率

### v3.0.0 (2025-10-19)
- **Week 3 简化**: 数据库架构从 4 库简化为 2 库
- **集成**: 完成 Phase 1-3 功能迁移
- **项目重组**: 从 42 个目录精简到 13 个科学组织目录
- **Web 界面**: 完整的 FastAPI + Vue 3 管理平台
- **GPU 支持**: RAPIDS 加速系统，包含 WSL2 支持

## 快速参考

### 启动命令速查
```bash
# 数据库服务
docker-compose up -d tdengine postgresql

# 系统初始化
python scripts/runtime/system_demo.py

# 后端服务
cd web/backend && python -m uvicorn app.main:app --reload

# 前端服务
cd web/frontend && npm run dev

# GPU 服务
cd src/gpu/api_system && python main_server.py

# 实时数据
python run_realtime_market_saver.py --count -1 --interval 300

# 测试系统
pytest tests/ -v

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

# 监控
from src.monitoring import PerformanceMonitor, AlertManager

# Web 后端
from web.backend.app.main import app

# GPU 系统 (集成在 src 目录下)
from src.gpu.api_system.services.gpu_api_server import GPUApiServer
```

### 配置检查
```bash
# 环境变量
cat .env

# 数据库连接
python scripts/database/check_tdengine_tables.py
python scripts/database/check_postgresql_tables.py

# GPU 状态
nvidia-smi
python src/gpu/api_system/wsl2_gpu_init.py

# Claude Code
.claude/hooks/post-tool-use-file-edit-tracker.sh --test
```

## 扩展开发

### 添加新数据源
1. 实现 `IDataSource` 接口
2. 创建适配器类，继承基础适配器
3. 注册到 DataSourceFactory
4. 在配置文件中添加连接参数

### 自定义技术指标
1. 在 `src/monitoring/technical_indicators.py` 中实现指标逻辑
2. 添加到指标注册表
3. 配置计算参数和缓存策略

### Web 页面开发
1. 后端: 在 `web/backend/app/api/` 中添加 API 端点
2. 前端: 在 `web/frontend/src/components/` 中添加 Vue 组件
3. 路由: 在 `web/frontend/src/router/` 中配置路由
4. 状态管理: 在 `web/frontend/src/stores/` 中添加 Pinia store
5. 样式: 使用 Element Plus 组件库

### Claude Code Hooks 开发
1. 在 `.claude/hooks/` 中创建脚本
2. 添加执行权限：`chmod +x script_name.sh`
3. 配置到 `.claude/config.json`
4. 测试 Hooks 功能

## 最佳实践

### 数据管理
- 定期备份关键数据
- 监控数据质量和完整性
- 合理设置数据保留策略
- 及时清理过期日志

### 性能调优
- 定期分析慢查询
- 优化数据库连接池
- 调整缓存大小和 TTL
- 监控 GPU 利用率

### 安全措施
- 定期更新依赖包
- 加密存储敏感信息
- 限制数据库访问权限
- 记录操作审计日志

### Claude Code 使用
- 定期更新 Hooks 脚本
- 监控 Hook 执行状态
- 备份配置文件
- 保持文档同步

## 支持和联系

- **项目状态**: 最新状态参考 `PROJECT_STATUS_QUICK_INDEX.md`
- **详细文档**: 参见 `docs/` 目录下的完整文档
- **变更日志**: 详见 `CHANGELOG.md`
- **问题排查**: 参考各模块的故障排查文档
- **Claude Code**: 参见 `CLAUDE.md` 集成指南

---

*本文档基于 MyStocks v1.3.1 生成，最后更新: 2025-11-21*  
*用于 iFlow CLI 交互指导，项目完整概览和快速入门参考*