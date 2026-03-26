<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# CLAUDE.md - MyStocks 项目开发指南

本文档为 Claude Code 提供项目开发指导。配合项目宪章 (`.specify/memory/constitution.md`) 和《项目开发规范与指导文档.md》使用。

---

## 📋 目录

1. [项目概览](#项目概览)
2. [开发状态](#开发状态)
3. [核心架构](#核心架构)
4. [开发环境配置](#开发环境配置)
5. [多CLI协作指引](#多cli协作指引)
6. [文件组织规范](#文件组织规范)
7. **[文档工作指引](#文档工作指引)** ⭐
8. [代码质量保证](#代码质量保证)
9. [监控系统](#监控系统)
10. [技术指标管理](#技术指标管理)
11. **[数据源管理工具](#数据源管理工具)** 🚨 **(含强制性开发指引)**
12. [Task Master AI集成](#task-master-ai集成)
13. [BUG登记](#bug登记)

---

## 项目概览

MyStocks 是专业量化交易数据管理系统，采用**双数据库架构**优化不同数据特性。系统基于适配器和工厂模式，提供统一数据访问层和配置驱动自动化。

### 技术栈

**核心框架**:
- Python 3.12+ / FastAPI 0.114+ / Vue 3.4+
- pandas 2.0+ / numpy 1.24+ / pydantic 2.0+

**数据库**:
- **TDengine 3.3+**: 高频时序数据（tick/分钟K线），20:1压缩比，极致写入性能
- **PostgreSQL 17+ + TimescaleDB**: 通用数据存储（日线、参考、交易、元数据）

**GPU加速** (可选):
- CUDA 12.x / cuDF 25.10+ / cuML 25.10+ / CuPy 13.6+
- **68.58x平均性能提升**，矩阵运算最高187.35x加速比
- 详细经验参见: [`docs/api/GPU开发经验总结.md`](./docs/api/GPU开发经验总结.md)

**数据源**:
- akshare / baostock / tushare / efinance / 通达信

### 架构设计原则

**1. 双数据库数据存储** - 正确的数据库处理正确的工作负载
   - **高频时序数据** → TDengine（极致压缩，超高写入性能）
   - **日线数据** → PostgreSQL TimescaleDB 超表
   - **参考/衍生/交易/元数据** → PostgreSQL 标准表

**2. 配置驱动管理**
   - `table_config.yaml` 定义完整表结构
   - `ConfigDrivenTableManager` 自动化表创建和验证

**3. 完整监控集成**
   - LGTM Stack (Loki, Grafana, Tempo, Prometheus)
   - 独立监控数据库追踪所有操作
   - 数据质量自动检查和告警

### 🎯 平台支持策略

**重要原则**: 本项目 **仅支持 Web 桌面端**，**不考虑移动端/平板端适配**。

**支持平台**:
- ✅ **桌面浏览器** (Chrome, Firefox, Safari, Edge)
  - 最小分辨率: 1280x720
  - 推荐分辨率: 1920x1080 或更高

**不支持平台**:
- ❌ **移动设备** (手机、平板)
- ❌ **响应式设计** (@media queries for mobile)
- ❌ **触摸优化** (touch target size > 44px)

**开发规范**:
1. **禁止编写移动端响应式代码**
   - 不使用 `@media (max-width: 768px)` 或类似查询
   - 不编写移动端特定的样式
   - 不进行移动端测试

2. **仅优化桌面端体验**
   - 专注于桌面浏览器性能
   - 优化鼠标交互（而非触摸）
   - 利用桌面端大屏幕优势

3. **设计系统基于桌面端**
   - ArtDeco 设计系统针对桌面端优化
   - 组件尺寸、间距、字体大小均按桌面端标准设计

**代码审查检查点**:
- ❌ 发现 `@media` 查询 → 删除
- ❌ 发现 `max-width: 768px` → 删除
- ❌ 发现移动端特定样式 → 删除
- ❌ 发现响应式布局代码 → 删除

---

## 开发状态

### 🎯 当前进度 (2025-12-29)

| 阶段 | 描述 | 状态 |
|------|------|------|
| Phase 1-3 | 核心系统（监控/技术分析/多数据源） | ✅ 完成 |
| Phase 4 | GPU API System（回测引擎/ML服务） | ✅ 完成 |
| Phase 5 | Backtest Engine（12个策略） | ✅ 完成 |
| Phase 6 | Technical Debt Remediation | ✅ 完成 |
| Phase 6.4 | GPU加速引擎集成与测试 | ✅ 完成 (68.58x性能提升) |

### 📊 技术债务现状

**代码质量指标** (Pylint Analysis):
- Errors: 215（需优先修复）
- Warnings: 2,606（潜在问题）
- Refactoring: 571（需重构）
- Convention: 1,858（代码风格）

**测试覆盖率**: ~6% → 目标80%
- 单元测试: 459个（部分失败）
- data_access层: PostgreSQL 67%, TDengine 56%

**修复计划**:
1. ✅ Phase 1: 配置代码质量工具
2. 🔄 Phase 2: 提升测试覆盖率（进行中）
3. ⏳ Phase 3: 重构高复杂度方法

---

## 核心架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                MyStocks Unified Manager                     │
│                (统一数据访问和路由入口点)                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐       │
│  │  Adapters   │   │    Core     │   │  Monitoring │       │
│  │   (7个)     │   │  (分类/路由) │   │  (监控/告警) │       │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘       │
│         │                 │                 │               │
│  ┌──────▼─────────────────▼─────────────────▼──────┐       │
│  │           Data Access Layer                     │       │
│  │      (TDengineAccess / PostgreSQLAccess)        │       │
│  └──────────────────────┬──────────────────────────┘       │
├────────────────────────┼────────────────────────────────────┤
│  ┌────────────────────┴────────────────────┐               │
│  │          Storage Layer                  │               │
│  │  ┌─────────────┐  ┌──────────────┐     │               │
│  │  │  TDengine   │  │ PostgreSQL   │     │               │
│  │  │ 高频时序数据 │  │ 所有其他数据  │     │               │
│  │  └─────────────┘  └──────────────┘     │               │
│  └─────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

### 核心组件 (重组后的模块路径)

#### Core Management Layer (`src/core/`)
- `DataClassification`: 5大数据分类枚举
- `DatabaseTarget`: 数据库类型（TDengine, PostgreSQL）
- `DataStorageStrategy`: 智能路由逻辑
- `ConfigDrivenTableManager`: YAML配置驱动表管理

**导入示例**:
```python
from src.core import ConfigDrivenTableManager, DataClassification
from src.core.data_storage_strategy import DataStorageStrategy
```

#### Unified Access Layer (`src/core/unified_manager.py`)
- `MyStocksUnifiedManager`: 统一数据操作入口
- `AutomatedMaintenanceManager`: 定时维护和健康检查

**导入示例**:
```python
from unified_manager import MyStocksUnifiedManager  # 根目录入口点
```

#### Database Access Layer (`src/data_access/`)
- `TDengineDataAccess`: 高频时序数据访问
- `PostgreSQLDataAccess`: 其他数据访问

**导入示例**:
```python
from src.data_access import TDengineDataAccess, PostgreSQLDataAccess
```

#### Data Source Adapters (`src/adapters/`)
7个核心适配器，统一接口 `IDataSource`:
- AkshareDataSource, BaostockDataSource, FinancialDataSource
- TdxDataSource, ByapiDataSource, CustomerDataSource, TushareDataSource

**导入示例**:
```python
from src.adapters.akshare_adapter import AkshareDataSource
from src.interfaces import IDataSource
```

#### GPU Acceleration Engine (`src/gpu/`)
**核心成就**: 68.58x平均性能提升，662+ GFLOPS峰值性能

- **HAL层**: GPU资源管理，策略隔离，故障容灾
- **Kernel层**: 矩阵运算引擎，支持Strassen算法
- **API系统**: GPU加速API服务器

**导入示例**:
```python
from src.gpu.core.hardware_abstraction.resource_manager import GPUResourceManager
from src.gpu.core.kernels.matrix_kernels import MatrixKernelEngine
```

### 🗂️ 目录结构重组 (2025-11-09)

**重组成果** - 从42个根目录精简到13个科学组织的目录 (降低69%混乱度):
- ✅ 所有源代码 → `src/` 目录
- ✅ 所有文档 → `docs/` 目录
- ✅ 所有脚本 → `scripts/` 目录
- ✅ 统一导入路径为 `from src.*` 格式

**新的导入路径标准**:
```python
# ✅ 推荐: 新的标准导入路径
from src.core import ConfigDrivenTableManager, DataClassification
from src.adapters.akshare_adapter import AkshareDataSource

# ⚠️ 仍然有效: 旧的导入路径 (通过兼容层)
from core import ConfigDrivenTableManager
from db_manager.database_manager import DatabaseTableManager  # 兼容层

# ❌ 已废弃: 直接从根目录导入模块目录
from adapters.akshare_adapter import AkshareDataSource
```

**脚本路径更新**:
```bash
# ✅ 新路径
python scripts/runtime/system_demo.py
python scripts/tests/test_config_driven_table_manager.py

# ❌ 旧路径
python system_demo.py
```

**详细报告**: [`REORGANIZATION_COMPLETION_REPORT.md`](./REORGANIZATION_COMPLETION_REPORT.md)

### Mock数据使用规则

**核心原则**: 所有模拟数据必须通过Mock数据模块提供，**严禁在业务代码中直接硬编码数据**。

详细规则: [`docs/guides/mock-data/MOCK_DATA_USAGE_RULES.md`](./mock-data/MOCK_DATA_USAGE_RULES.md)

**Mock/Real数据切换**: [`docs/guides/mock-data/MOCK_REAL_DATA_SWITCHING_GUIDE.md`](./mock-data/MOCK_REAL_DATA_SWITCHING_GUIDE.md) 📘
- 三层数据源架构设计
- 环境变量驱动的数据源切换机制
- 实战示例和最佳实践
- 常见问题解答

**快速参考**:
```python
# ✅ 正确: 通过工厂函数获取Mock数据
from src.data_sources.factory import get_timeseries_source
source = get_timeseries_source(source_type="mock")
data = source.get_kline_data(symbol, start_time, end_time, interval)

# ❌ 错误: 直接硬编码数据
historical_data = [
    {"date": "2025-01-01", "close": 10.5},  # 严禁!
]
```

---

## 开发环境配置

### 环境安装

```bash
# 安装依赖（双数据库配置）
pip install pandas numpy pyyaml psycopg2-binary taospy akshare

# 创建 .env 文件配置数据库
# 必需的环境变量:
# TDengine: TDENGINE_HOST, TDENGINE_PORT, TDENGINE_USER, TDENGINE_PASSWORD, TDENGINE_DATABASE
# PostgreSQL: POSTGRESQL_HOST, POSTGRESQL_USER, POSTGRESQL_PASSWORD, POSTGRESQL_PORT, POSTGRESQL_DATABASE
# 监控: MONITOR_DB_URL (使用PostgreSQL)
# 认证: JWT_SECRET_KEY (API认证必需)
```

### 端口分配规范

#### 端口范围定义

| 分类 | 端口范围 | 服务 | 说明 |
|------|----------|------|------|
| **前端** | 3000-3009 | Vue/React 应用 | 前端开发服务器 |
| **后端** | 8000-8009 | FastAPI/Flask 应用 | 后端API服务 |
| **监控** | 9000-9099 | Prometheus/Grafana | 监控系统 |

#### 前端端口详细

| 端口 | 服务 | 用途 | CORS状态 |
|------|------|------|----------|
| 3000 | Grafana | 监控仪表板 | ✅ 已授权 |
| 3001 | Vue Frontend | 前端开发服务器 #1 | ✅ 已授权 |
| 3002 | Vue Frontend | 前端开发服务器 #2 | ✅ 已授权 |
| ... | ... | ... | ✅ 已授权 |
| 3009 | Vue Frontend | 前端开发服务器 #9 | ✅ 已授权 |

#### 后端端口详细

| 端口 | 服务 | 用途 | CORS状态 |
|------|------|------|----------|
| 8000 | FastAPI | 后端API主服务 | ✅ 已授权 |
| 8001 | FastAPI | 后端API服务 #1 | ✅ 已授权 |
| 8002 | FastAPI | 后端API服务 #2 | ✅ 已授权 |
| ... | ... | ... | ✅ 已授权 |
| 8009 | FastAPI | 后端API服务 #9 | ✅ 已授权 |

#### 监控端口

| 端口 | 服务 | 用途 |
|------|------|------|
| 9090 | Prometheus | 指标查询和告警配置 |
| 3000 | Grafana | 可视化仪表板 |
| 3100 | Loki | 日志查询API |
| 3200 | Tempo | 追踪数据API |

### 前端运行命令

```bash
# 进入前端目录
cd /opt/claude/mystocks_spec/web/frontend

# 安装依赖
npm install

# 开发模式运行 (默认端口 5173，需手动指定前端端口)
npm run dev -- --port 3020

# 指定端口运行
npm run dev -- --port 3020  # 前端服务1
npm run dev -- --port 3002  # 前端服务2
# ...

# 构建生产版本
npm run build
```

### 后端运行命令

```bash
# 进入后端目录
cd /opt/claude/mystocks_spec/web/backend

# 开发模式运行 (默认端口 8000)
uvicorn app.main:app --host 0.0.0.0 --port 8020 --reload

# 指定端口运行
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload  # 后端服务1
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload  # 后端服务2
# ...
```

### CORS 配置

**配置文件**: `/opt/claude/mystocks_spec/web/backend/app/core/config.py`

```python
# CORS 配置 (前端端口范围: 3000-3009，后端端口范围: 8000-8009)
cors_origins_str: str = (
    "http://localhost:3000,http://localhost:3020,http://localhost:3002,"
    "http://localhost:3003,http://localhost:3004,http://localhost:3005,"
    "http://localhost:3006,http://localhost:3007,http://localhost:3008,http://localhost:3009,"
    "http://localhost:8020,http://localhost:8001,http://localhost:8002,"
    "http://localhost:8003,http://localhost:8004,http://localhost:8005,"
    "http://localhost:8006,http://localhost:8007,http://localhost:8008,http://localhost:8009"
)
```

### CORS 问题排查

**症状**: 浏览器控制台显示 CORS 错误
```
Access to XMLHttpRequest at 'http://localhost:8020/api/...'
from origin 'http://localhost:3020' has been blocked by CORS policy
```

**解决方案**:
1. 确认前端端口在 CORS 白名单中 (3000-3009)
2. 检查 `/opt/claude/mystocks_spec/web/backend/app/core/config.py` 中的 `cors_origins_str`
3. 重启后端服务使配置生效

**添加新端口到 CORS 白名单**:
```python
# 编辑后端配置，添加到 cors_origins_str
cors_origins_str: str = "http://localhost:3000,...,http://localhost:YOUR_NEW_PORT,..."
```

### JWT 密钥配置

**自动化脚本** (推荐):
```bash
bash scripts/JWT_key_update.sh
```

**手动配置**:
```bash
# 方法1: Python生成
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 方法2: OpenSSL生成 (推荐)
openssl rand -hex 32

# 添加到 .env
echo "JWT_SECRET_KEY=<生成的密钥>" >> .env
```

**相关文件**:
- 配置脚本: `scripts/JWT_key_update.sh`
- 配置模板: `.env.example`
- 配置文档: `docs/standards/LOCAL_ENV_SETUP.md`
- 安全指南: `docs/guides/PHASE0_CREDENTIAL_ROTATION_GUIDE.md`

### 系统初始化和管理

```bash
# 初始化完整系统
python -c "from unified_manager import MyStocksUnifiedManager; manager = MyStocksUnifiedManager(); manager.initialize_system()"

# 运行系统演示
python scripts/runtime/system_demo.py

# 验证数据库连接和表结构
python scripts/database/check_tdengine_tables.py
python scripts/database/verify_tdengine_deployment.py

# 运行实时市场数据保存器
python scripts/runtime/run_realtime_market_saver.py
```

### 测试

```bash
# 测试统一管理器功能
python scripts/tests/test_config_driven_table_manager.py

# 测试金融适配器
python scripts/tests/test_financial_adapter.py

# 测试双数据库架构
python scripts/tests/test_dual_database_architecture.py

# 测试GPU加速引擎（如果可用）
python test_gpu_integration.py
python test_performance_comparison.py
```

---

## 多CLI协作指引

**适用场景**: 使用Git Worktree进行多CLI并行开发

**核心原则**: **主CLI提供指导，Worker CLI负责执行**

### 基本原则

1. **指导但不代替** (Guide, Don't Do)
   - 主CLI职责: 协调和监控
   - 仅在阻塞问题、明确请求、偏离目标时出手
   - **不代替Worker CLI编写代码或修改文件**

2. **问题请示机制**
   - Worker CLI: 独立完成任务，及时报告阻塞问题
   - 问题级别: 🟢 信息级（独立处理）/ 🟡 警告级（尝试解决）/ 🔴 阻塞级（立即报告）

3. **权限边界**
   - 主CLI: 全部worktree读+写权限，但工作期间仅读取状态
   - Worker CLI: 本地worktree读+写权限，本地分支Git提交

### 详细文档

**完整指南** (1000+行通用手册):
- **[Multi-CLI Worktree Management Guide](./docs/guides/MULTI_CLI_WORKTREE_MANAGEMENT.md)** ⭐
  - 完整工作流程、权限管理、里程碑管理
  - 详细的主CLI和Worker CLI工作指引
  - 典型场景示例和反模式警告

- **[Git Worktree Main CLI Manual](./docs/guides/GIT_WORKTREE_MAIN_CLI_MANUAL.md)**
  - Git Worktree官方命令参考
  - 严格操作规范和完整流程

### 相关文档索引

- **[File Organization Rules](./docs/standards/FILE_ORGANIZATION_RULES.md)** - 文件组织规范
- **[Python Quality Assurance Workflow](./docs/operations/ci-cd/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md)** - 代码质量保证流程
- **[GitNexus Workflow](./docs/guides/GITNEXUS_WORKFLOW.md)** - `mystocks_spec` 仓库的 GitNexus 稳定工作流、CLI/MCP 分工与 freshness gate

---

## 文档工作指引 ⭐

**目的**: 规范项目文档的创建、维护和组织流程，确保文档结构清晰、易于查找和维护。

**完整指南**: 📖 **[文档工作指引](./docs/guides/documentation/DOCUMENTATION_WORKFLOW_GUIDE.md)**

### 快速参考

**新增文档时，请遵循3步流程**:
1. **确定分类** - 选择8大分类之一
2. **正确命名** - 使用kebab-case（小写+连字符）
3. **更新索引** - 运行 `python scripts/tools/docs_indexer.py --categories`

### 🗂️ 8大文档分类

| 分类 | 路径 | 用途 | 示例 |
|------|------|------|------|
| **Overview** | `docs/overview/` | 项目概述、核心规范 | agents.md, changelog.md |
| **Guides** | `docs/guides/` | 开发指南、工作流程 | quick-start.md, frontend/enhanced-ui-ux-guide.md |
| **API** | `docs/api/` | API文档、接口规范 | api-documentation.md, web-access-guide.md |
| **Architecture** | `docs/architecture/` | 架构设计、系统组件 | ml-integration-report.md, mock-data-guide.md |
| **Operations** | `docs/operations/` | 部署、监控、运维 | deployment-guide.md, log-monitoring.md |
| **Testing** | `docs/testing/` | 测试策略、质量保障 | testing-strategy.md, quality-reports.md |
| **Reports** | `docs/reports/` | 阶段报告、分析总结 | comprehensive-cleanup.md, project-status.md |
| **Archive** | `archive/docs/` | 归档文档、历史版本 | old-phase-reports/, deprecated-docs/ |

### 📝 文档命名规范

**✅ 推荐格式**:
- 英文：`kebab-case.md` （小写+连字符）
- 示例：`quick-start.md`, `api-authentication-jwt.md`, `wencai-integration.md`

**❌ 避免使用**:
- ❌ 中文文件名：`API文档.md` → `api-documentation.md`
- ❌ 空格：`My Document.md` → `my-document.md`
- ❌ 大写：`README.md` → `guide-name.md`
- ❌ 下划线：`my_document.md` → `my-document.md`

### 🚨 文档位置检查（Pre-commit Hook）

**自动检查机制**:
- ✅ 检测根目录下的.md文件（应移到分类目录）
- ✅ 检测中文文件名（建议使用英文或拼音）
- ✅ 检测临时文档位置（不应在根目录）
- ✅ 提供正确的移动建议

**触发时机**: 每次 `git commit` 时自动运行

**查看详情**: `docs/guides/documentation/DOCUMENTATION_WORKFLOW_GUIDE.md`

### 🔧 常用文档命令

```bash
# 检查文档规范
python scripts/tools/docs_check.py

# 生成文档索引
python scripts/tools/docs_indexer.py --categories

# 查找文档位置
find docs/ -name "*.md" -type f

# 统计文档数量
find docs/ -name "*.md" | wc -l
```

### 📚 相关文档

- **[文档工作指引详细版](./docs/guides/documentation/DOCUMENTATION_WORKFLOW_GUIDE.md)** - 完整的工作流程和最佳实践
- **[文件组织规范](./docs/standards/FILE_ORGANIZATION_RULES.md)** - 代码和脚本的组织规范
- **[文档整理完成报告](./docs/reports/DOC_CLEANUP_COMPLETION_REPORT.md)** - 2026-01-07文档整理项目总结

---

## 文件组织规范

**理念**: 保持干净、最小化的根目录，按功能逻辑分类。每个文件都应有明确的位置。

### 根目录标准

**仅这5个核心文件属于根目录**:
- `README.md` - 项目概览和主文档
- `CLAUDE.md` - Claude Code集成指南（本文件）
- `CHANGELOG.md` - 版本历史和变更
- `requirements.txt` - Python依赖
- `.mcp.json` - MCP服务器配置

**所有其他文件必须组织到子目录中**

### 🚨 重要：禁止使用 /tmp 保存正式文档

**⚠️ 严格规则**: `/tmp` 目录**仅用于临时文件**，所有正式项目文件必须保存在项目目录内。

**❌ 严禁以下行为**:
- 将正式报告、分析文档保存到 `/tmp`
- 将测试脚本、配置文件保存到 `/tmp`
- 使用 `/tmp` 作为长期存储位置
- 在 `/tmp` 保存需要保留的分析结果

**✅ 正确做法**:
- **报告文档** → `docs/reports/` 目录
- **脚本文件** → `scripts/` 目录（按功能分类）
- **配置文件** → `config/` 目录
- **测试结果** → `docs/reports/test-results/` 目录

**✅ /tmp 仅用于**:
- 测试过程中的临时缓存（可随时删除）
- 编译和构建的中间文件
- 下载文件的临时中转位置
- 快速验证和原型测试

**示例对比**:
```
❌ 错误: /tmp/ARTDECO_COMPLETION_REPORT.md
✅ 正确: docs/reports/ARTDECO_COMPLETION_REPORT.md

❌ 错误: /tmp/test_feature.py
✅ 正确: scripts/tests/test_feature.py

❌ 错误: /tmp/app-config.yaml
✅ 正确: config/app-config.yaml
```

**详细规则**: 参见下方"临时文件使用规则"和[`docs/standards/FILE_ORGANIZATION_RULES.md`](./docs/standards/FILE_ORGANIZATION_RULES.md)

### 临时文件使用规则 ⚠️

**核心原则**: `/tmp` 目录**仅用于临时文件**，所有正式项目文件必须保存在项目目录内。

**🚨 严格禁止**:
- ❌ 将正式报告、文档保存到 `/tmp`
- ❌ 将测试脚本保存到 `/tmp`
- ❌ 将配置文件保存到 `/tmp`
- ❌ 使用 `/tmp` 作为长期存储位置
- ❌ 在 `/tmp` 保存需要保留的分析结果

**✅ 允许使用场景**:
- ✅ 测试过程中的临时缓存
- ✅ 编译和构建的中间文件
- ✅ 下载文件的临时位置
- ✅ 快速验证和原型测试（可随时删除）

**✅ 正式文件必须保存到项目目录**:
- 📄 报告 → `docs/reports/`
- 🔧 脚本 → `scripts/` (按功能分类)
- ⚙️ 配置 → `config/`
- 📊 测试结果 → `docs/reports/test-results/`

#### 临时文件定义
- **用途**: 测试、缓存、中间处理文件
- **生命周期**: 短暂存在，可随时删除
- **示例**:
  - 测试截图: `/tmp/test-screenshot.png`
  - 编译缓存: `/tmp/cache-XXXXXX`
  - 下载的临时文件: `/tmp/download-XXXXXX`
  - 快速原型验证: `/tmp/quick-test.mjs`

#### 正式文件放置规范

**文档文件** → `docs/` 目录:
- 报告: `docs/reports/FILENAME.md`
- 指南: `docs/guides/FILENAME.md`
- 设计: `docs/design/FILENAME.md`
- API 文档: `docs/api/FILENAME.md`
- 测试报告: `docs/reports/test-results/FILENAME.md`

**脚本文件** → `scripts/` 目录:
- 测试: `scripts/test_*.py`
- 运行时: `scripts/run_*.py`
- 数据库: `scripts/check_*.py`, `scripts/verify_*.py`
- 开发工具: `scripts/dev/*.py`
- Web测试: `scripts/dev/test_*.mjs`

**配置文件** → `config/` 目录:
- 所有配置文件: `config/*.yaml`, `config/*.toml`, `config/*.ini`

**生成的报告** → `docs/reports/` 目录:
- 分析报告: `docs/reports/REPORT_NAME.md`
- JSON 报告: `docs/reports/report-data.json`
- 截图证据: `docs/reports/screenshots/`

#### 文件放置决策流程

```
是否为项目正式文件？
├─ YES → 是否为文档？
│         ├─ YES → docs/{guides,reports,api,design}/
│         └─ NO → 是否为脚本？
│                   ├─ YES → scripts/{tests,runtime,database,dev}/
│                   └─ NO → 是否为配置？
│                             ├─ YES → config/
│                             └─ NO → 根据功能放置
└─ NO（临时） → /tmp/（可随时删除）
```

#### 示例对比

| 文件类型 | ❌ 错误位置 | ✅ 正确位置 |
|---------|-----------|-----------|
| 完成报告 | `/tmp/report.md` | `docs/reports/report.md` |
| 截图验证 | `/tmp/screenshot.png` | `docs/reports/screenshot.png` |
| 测试脚本 | `/tmp/test.py` | `scripts/tests/test_feature.py` |
| 配置文件 | `/tmp/config.yaml` | `config/app_config.yaml` |
| 临时测试 | `/tmp/quick-test.txt` | `/tmp/quick-test.txt` ✅ |

**重要提醒**:
1. ⚠️  **严禁**将正式文档、报告、脚本保存在 `/tmp`
2. ⚠️  **严禁**使用 `/tmp` 作为长期存储位置
3. ✅  **可以**使用 `/tmp` 作为中转（如：生成→复制到项目目录→删除临时文件）
4. ✅  **必须**确保所有正式文件都有正确的项目目录位置

### 目录结构规则

#### 1. **scripts/** - 所有可执行脚本

按功能组织为4类:

**scripts/tests/** - 测试文件
- 模式: 前缀 `test_`
- 示例: `test_config_driven_table_manager.py`

**scripts/runtime/** - 生产运行脚本
- 模式: 前缀 `run_`, `save_`, `monitor_`, 或 `*_demo.py`
- 示例: `run_realtime_market_saver.py`, `system_demo.py`

**scripts/database/** - 数据库操作
- 模式: 前缀 `check_`, `verify_`, `create_`
- 示例: `check_tdengine_tables.py`

**scripts/dev/** - 开发工具
- 示例: `gpu_test_examples.py`, `validate_documentation_consistency.py`

#### 2. **docs/** - 文档文件

- **docs/guides/** - 用户和开发指南
- **docs/archived/** - 已弃用文档（历史参考）
- **docs/architecture/** - 架构设计文档
- **docs/api/** - API文档

#### 3. **config/** - 配置文件

所有配置文件（不论扩展名）:
- 扩展名: `.yaml`, `.yml`, `.ini`, `.toml`, `docker-compose.*.yml`
- 示例: `mystocks_table_config.yaml`, `docker-compose.tdengine.yml`

#### 4. **reports/** - 生成的报告和分析

- 模式: 由分析脚本生成，如需重复则带时间戳
- 命名约定: ISO日期格式 `YYYYMMDD_HHMMSS`

#### 5. **子模块文档自治规范**

**核心原则**:
- 子模块（如 `web/`, `services/`）拥有文档管理自主权
- 子模块文档不受主项目 `docs/` 目录规范强制约束
- Hook自动文档整理会排除特定目录和文件类型

**排除规则**:
- 目录关键字: `web`, `css`, `js`, `frontend`, `backend`, `api`, `services`, `temp`, `build`, `dist`
- 文件后缀: `.html`, `.css`, `.js`, `.json`, `.xml`, `.yaml`, `.yml`, `.toml`
- **特殊文件**: 所有 README 文件（不区分大小写）保留在原位置，永不移动 ⭐

**详细规范**: [`docs/standards/FILE_ORGANIZATION_RULES.md`](./docs/standards/FILE_ORGANIZATION_RULES.md)

### 脚本导入路径管理

**关键规则**: `scripts/**/` 中的所有脚本必须正确计算项目根目录

**标准模式**:
```python
import sys
import os

# 计算项目根目录（从脚本位置向上3级）
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 现在可以从项目根目录导入
from src.core import ConfigDrivenTableManager
from src.adapters.akshare_adapter import AkshareDataSource
```

### Git最佳实践

```bash
# ✅ 正确: 保留文件历史
git mv old_location/file.py new_location/file.py

# ❌ 错误: 破坏文件历史
mv old_location/file.py new_location/file.py
git add new_location/file.py
```

### 验证清单

重组文件后:
- [ ] 根目录仅包含5个核心文件
- [ ] 所有脚本正确分类在 `scripts/{tests,runtime,database,dev}`
- [ ] 所有文档在 `docs/{guides,archived,architecture,api}`
- [ ] 所有配置文件在 `config/`
- [ ] 所有报告在 `reports/`
- [ ] 所有移动的脚本已更新导入路径
- [ ] 所有文档链接已更新
- [ ] `git status` 显示移动（而非删除+添加）
- [ ] 重组后所有测试通过

---

## 代码质量保证

**优化策略**: Ruff 优先 + Black 兜底 + Pylint 深度审查

**统一配置**: 所有工具行长度 120 字符

### 工具版本

- Ruff: 0.9.10（日常开发 - 效率优先）
- Black: 25.11.0（格式化兜底）
- Pylint: 4.0.3（深度质量分析）
- Bandit: 1.7.5+（安全扫描）
- Safety: 2.3.0+（依赖安全）

### 四阶段质量保证流程

**阶段1: 日常开发** (效率优先)
- 工具: Ruff（一站式格式化 + Lint）
- 触发: 每次保存文件后
- 命令: `ruff check --fix .`

**阶段2: 提交前检查** (格式兜底 + 核心检查)
- 工具: Pre-commit Hooks（自动触发）
- 触发: 每次 `git commit` 时自动运行
- 执行顺序（9步骤）: Ruff (Lint & Fix) → Black → Ruff (Check) → MyPy → Bandit → Safety → 通用检查

**阶段3: 定期深度分析** (Pylint 核心价值)
- 工具: Pylint（测试代码专用配置）
- 触发: 每周 / 每迭代末
- 命令: `pylint --rcfile=.pylint.test.rc tests/`

**阶段4: CI/CD集成** (快速失败 + 完整检查)
- 工具顺序: Ruff+Black → MyPy+Bandit+Safety → Pylint（仅记录）
- Ruff/Black问题直接失败，Pylint仅生成报告

### 关键配置文件

| 配置文件 | 用途 | 位置 |
|----------|------|------|
| `pyproject.toml` | Ruff, Black, MyPy, Pylint（常规） | 项目根目录 |
| `.pylint.test.rc` | Pylint（测试专用） | 项目根目录 |
| `.pre-commit-config.yaml` | Pre-commit hooks | 项目根目录 |
| `config/.security.yml` | 安全配置 | `config/` 目录 |

### 快速开始

**首次设置**:
```bash
# 安装开发依赖
pip install -e ".[dev]"

# 安装 pre-commit hooks
pre-commit install

# 验证安装
ruff --version && black --version && pylint --version
```

**日常使用**:
```bash
# 日常开发: 一键修复
ruff check --fix .

# 提交代码: 自动运行9步检查
git add . && git commit -m "message"

# 每周分析: 生成质量报告
pylint --rcfile=.pylint.test.rc --output=report.html --output-format=html tests/
```

### 详细文档

- **[完整工作流程](./docs/operations/ci-cd/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md)**
- **[快速参考](./docs/operations/ci-cd/PYTHON_QUALITY_TOOLS_QUICK_REFERENCE.md)**
- **[实施总结](./docs/reports/code_quality/PYTHON_QUALITY_TOOLS_IMPLEMENTATION_SUMMARY.md)**

---

## 监控系统

MyStocks 使用 **LGTM Stack** (Loki, Grafana, Tempo, Prometheus) 实现完整可观测性。

### 监控栈概览

| 容器 | 功能 | 端口 | 状态 |
|------|------|------|------|
| Prometheus | 指标存储与查询 | 9090:9090 | ✅ |
| Grafana | 可视化仪表板 | 3000:3000 | ✅ |
| Loki | 日志聚合系统 | 3100:3100 | ✅ |
| Tempo | 分布式追踪系统 | 3200:3200 | ✅ |
| Node Exporter | 系统指标采集器 | 9100:9100 | ✅ |

### 三大支柱

**Metrics (指标)**: 监控**发生了什么**
- 工具: Prometheus
- 内容: 请求延迟、错误率、吞吐量、资源使用率

**Logs (日志)**: 解释**为什么发生**
- 工具: Loki
- 内容: 应用错误日志、异常堆栈、请求/响应详情

**Traces (追踪)**: 展示**在哪里发生**
- 工具: Tempo
- 内容: 微服务调用链路、每个服务耗时、性能瓶颈定位

### 监控配置文件

**环境变量配置**: `/opt/claude/mystocks_spec/monitoring-stack/.env.monitoring`
```bash
# 引用监控配置
source /opt/claude/mystocks_spec/monitoring-stack/.env.monitoring
```

**数据持久化**: `/data/docker/` (prometheus/, grafana/, loki/, tempo/)

### 常用操作命令

```bash
cd /opt/claude/mystocks_spec/monitoring-stack

# 启动所有监控服务
docker-compose up -d

# 停止所有监控服务
docker-compose down

# 重启单个服务
docker-compose restart prometheus
docker-compose restart grafana

# 查看日志
docker logs mystocks-prometheus -f
docker logs mystocks-grafana -f
```

### 访问地址

| 服务 | 外部地址 | 用途 |
|------|----------|------|
| Prometheus | http://localhost:9090 | 指标查询和告警配置 |
| Grafana | http://localhost:3000 | 可视化仪表板（默认 admin/admin） |
| Loki | http://localhost:3100 | 日志查询API |
| Tempo | http://localhost:3200 | 追踪数据API |

### 相关文档

- **[部署状态报告](./monitoring-stack/MONITORING_STATUS.md)**
- **[Docker Compose配置](./monitoring-stack/docker-compose.yml)**
- **[环境变量配置](./monitoring-stack/.env.monitoring)**

---

## 技术指标管理

标准化技术指标计算框架，支持注册、依赖管理、智能调度。

**详细文档**: [指标管理系统设计文档](./docs/03-API与功能文档/指标管理系统设计文档.md)

---

## 数据源管理工具

**状态**: ✅ 生产就绪 (2026-01-02) | **版本**: V2.0

### 🚨 强制性开发指引

**⚠️ 重要**: 所有新增API和新建数据源的开发工作**必须**阅读并遵守开发指引：

📖 [`docs/guides/data-source/NEW_API_SOURCE_INTEGRATION_GUIDE.md`](./docs/guides/data-source/NEW_API_SOURCE_INTEGRATION_GUIDE.md)

---

数据源管理工具提供统一的接口来管理、测试、监控所有外部数据源端点。

### 管理范围

数据源管理工具负责以下范围的管理：

#### ✅ 属于管理范围

**1. 数据源端点管理**
- **配置管理**: 34个已注册数据源接口的配置信息
- **参数定义**: 每个端点的输入参数、默认值、验证规则
- **元数据管理**: 端点名称、描述、数据分类、源类型、优先级
- **状态跟踪**: 健康状态、质量评分、最后测试时间
- **配置文件**: `config/data_sources_registry.yaml`

**2. 接口测试和验证**
- **功能测试**: 验证端点是否可用、参数是否正确
- **数据质量分析**: 完整性、范围、重复性、类型一致性检查
- **性能测试**: 响应时间、成功率、错误率统计
- **测试报告**: 自动生成详细测试报告和指标

**3. 健康监控**
- **实时健康检查**: 单个端点或批量健康状态检查
- **健康指标**: 连接成功率、响应时间、数据质量
- **状态管理**: active/maintenance/deprecated 状态维护
- **告警机制**: 不健康端点自动标记和通知

**4. 数据源搜索和发现**
- **分类搜索**: 按5层数据分类筛选（DAILY_KLINE, MINUTE_KLINE等）
- **源类型过滤**: 按数据源类型筛选（akshare, tushare等）
- **健康状态过滤**: 仅显示健康或维护中的端点
- **关键词搜索**: 按端点名称或描述搜索
- **分类统计**: 获取各类别的端点数量统计

**5. 生命周期管理**
- **端点注册**: 新增数据源端点到注册表
- **配置更新**: 动态更新端点参数和元数据
- **状态变更**: 标记端点为维护中或已弃用
- **优先级调整**: 根据健康状态和质量评分调整优先级

#### ❌ 不属于管理范围

以下功能**不**由数据源管理工具提供：

**1. 数据获取和存储**
- ❌ 实际数据拉取和缓存
- ❌ 数据存储到数据库
- ❌ 历史数据管理
- **归属**: `src/adapters/` 和 `MyStocksUnifiedManager`

**2. 业务逻辑**
- ❌ 数据转换和处理逻辑
- ❌ 技术指标计算
- ❌ 策略回测
- **归属**: `src/core/` 和业务服务层

**3. 用户界面**
- ❌ 前端页面和组件
- ❌ 数据可视化
- **归属**: `web/frontend/` 和前端服务

**4. 数据源适配器实现**
- ❌ Akshare、Tushare等适配器实现
- ❌ API调用封装
- **归属**: `src/adapters/`

### 工具链

数据源管理工具包含两个核心工具：

**1. 手动测试工具** (`scripts/tools/manual_data_source_tester.py`)
- 交互式测试模式
- 命令行批量测试
- 数据质量分析和报告生成

**2. FastAPI管理接口** (`web/backend/app/api/data_source_registry.py`)
- 7个RESTful API端点
- 支持搜索、测试、配置、健康检查
- 统一响应格式和错误处理

### 集成方式

**Vue.js前端**:
```javascript
import dataSourceService from '@/api/dataSourceService'
const sources = await dataSourceService.searchDataSources({
  dataCategory: 'DAILY_KLINE',
  sourceType: 'akshare',
  onlyHealthy: true
})
```

**Python后端**:
```python
from scripts.tools.manual_data_source_tester import DataSourceTester
tester = DataSourceTester()
result = tester.test_data_source(
    endpoint_name='akshare.stock_zh_a_hist',
    test_params={'symbol': '000001', 'period': 'daily'}
)
```

**命令行**:
```bash
python scripts/tools/manual_data_source_tester.py --interactive
```

### 相关文档

- 📖 **[完整使用指南](./docs/guides/data-source/DATA_SOURCE_MANAGEMENT_TOOLS_USAGE_GUIDE.md)** - 1000+行完整文档
- 📋 **[快速参考卡片](./docs/guides/data-source/DATA_SOURCE_TOOLS_QUICK_REFERENCE.md)** - 5分钟快速上手
- 🏗️ **[架构设计文档](./docs/architecture/DATA_SOURCE_MANAGEMENT_V2.md)** - V2.0架构说明
- ✅ **[最终验证报告](./docs/reports/DATA_SOURCE_V2_FINAL_VERIFICATION_REPORT.md)** - 验证结果
- 🚀 **[功能增强提案](./docs/reports/DATA_SOURCE_V2_ENHANCEMENT_PROPOSAL.md)** - 增强计划

### 架构定位

```
┌─────────────────────────────────────────────────────────────┐
│            数据源管理工具 (V2.0)                              │
│      管理范围: 配置、测试、监控、搜索                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ 配置管理      │  │ 健康监控      │  │ 搜索发现      │     │
│  │ YAML注册表   │  │ 状态检查      │  │ 分类筛选      │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                  │             │
│         └─────────────────┼──────────────────┘             │
│                           │                                │
├───────────────────────────┼────────────────────────────────┤
│                           │                                │
│  ┌────────────────────────▼──────────────────────────┐   │
│  │        测试和验证工具链                             │   │
│  │  手动测试工具  +  FastAPI接口  +  数据质量分析     │   │
│  └────────────────────────────────────────────────────┘   │
│                                                           │
│  ❌ 不管理: 数据存储、业务逻辑、UI、适配器实现              │
│  ✅ 提供: 配置、测试、监控、搜索、生命周期管理              │
└───────────────────────────────────────────────────────────┘
```

**核心原则**: 数据源管理工具专注于**管理**而非**执行**，提供标准化的配置、测试、监控接口，与数据适配器、业务逻辑、存储层清晰分离。

---

## Task Master AI集成

**导入Task Master开发工作流程命令和指南，视为CLAUDE.md文件的一部分**

详细内容: `@./.taskmaster/CLAUDE.md`

---

## BUG登记与经验教训管理

**核心原则**: 记录所有有一定难度/或出现频度高的BUG，总结经验教训，为后续开发提供预防指引。

### 📝 BUG报告系统

MyStocks项目使用完整的BUG报告系统，包括：

1. **BUG报告模板**: 标准化的BUG登记格式
2. **经验教训索引**: 总结常见问题和预防措施
3. **自动报告机制**: 修复BUG时自动生成报告

#### 快速命令

输入以下任一命令触发BUG登记：
- **"登记BUG"**
- **"记BUG"**
- **"登记bug"**
- **"记bug"**

#### BUG报告流程

当发现需要登记的BUG时，Claude Code 将：

1. **读取模板**: `docs/standards/bug-report-template.json`
2. **填写BUG信息**: 按照模板格式记录问题
3. **保存报告**: `docs/reports/quality/bugs/BUG-YYYYMMDD-{errorCode}.json`
4. **更新索引**: 更新经验教训索引文档

#### 模板格式

支持两种格式：

| 格式 | 字段 | 数量限制 |
|------|------|----------|
| 单个BUG | `bug` 对象 | 1个 |
| 批量BUG | `bugs` 数组 | 最多20个 |

#### 必填字段

**metadata 元数据**:

| 字段 | 说明 | 示例 |
|------|------|------|
| `version` | 固定为 `"1.0"` | - |
| `format` | 固定为 `"mystocks-bug-report"` | - |
| `reportedAt` | ISO 8601 格式时间 | `"2026-01-08T11:30:00Z"` |
| `reporter` | 登记人姓名 | `"Claude Code"` |

**BUG 对象**:

| 字段 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `errorCode` | ✅ | 大写字母、数字、下划线 | `ERR_DDD_IMPORT_001` |
| `title` | ✅ | BUG标题，简明扼要 | "DDD模块导入路径错误" |
| `message` | ✅ | 详细错误描述 | "Market Data Context的仓储接口导入路径错误..." |
| `stackTrace` | ❌ | 错误堆栈信息 | "ModuleNotFoundError: ..." |
| `severity` | ✅ | 严重程度 | critical/high/medium/low |
| `context` | ❌ | 上下文信息（强烈建议填写） | {projectName, component, phase} |

#### 严重程度分级

| 级别 | 标识 | 响应时间 | 影响范围 | 使用场景 |
|------|------|----------|----------|----------|
| **critical** | 🔴 崩溃 | **立即修复** | 系统不可用 | 服务启动失败、数据丢失、安全漏洞 |
| **high** | 🟠 严重 | **4小时内** | 核心功能受损 | 重要功能不可用、性能严重下降 |
| **medium** | 🟡 中等 | **24小时内** | 功能异常 | 非核心功能异常、有workaround |
| **low** | 🟢 轻微 | **下迭代** | 轻微问题 | UI显示问题、代码规范 |

### 📚 经验教训索引

**文档位置**: `docs/reports/quality/BUG_LESSONS_LEARNED.md`

**核心功能**:
- 记录常见BUG类型和根本原因
- 提供预防措施和最佳实践
- 为开发人员提供事前指引
- 包含快速参考和检查清单

**使用方法**:
1. **开发前查阅**: 看是否有类似问题记录
2. **应用预防措施**: 在开发前就避免这些问题
3. **报告新问题**: 如果是新问题，按模板登记BUG并更新索引

**已记录的BUG类型**:
- DDD架构问题（Dataclass字段顺序、Property vs Method）
- 数据类型问题（浮点数精度）
- 测试问题（测试与实现不匹配）
- 导入路径问题（路径与文件名不一致）
- 配置问题（Linter自动修改）

### 🔧 开发前检查清单

在开始开发前，请确认：

- [ ] **查阅经验教训索引**: `docs/reports/quality/BUG_LESSONS_LEARNED.md`
- [ ] **读取现有实现**: 使用Glob/Grep查找相关代码
- [ ] **理解现有API**: 检查方法签名、参数、返回值
- [ ] **验证导入路径**: 确保`__init__.py`正确导出
- [ ] **了解命名约定**: 遵循现有代码风格
- [ ] **运行现有测试**: 确保基线测试通过

### 📂 相关文件

**BUG报告系统**:
- 模板文件: `docs/standards/bug-report-template.json`
- 经验教训索引: `docs/reports/quality/BUG_LESSONS_LEARNED.md`
- BUG报告目录: `docs/reports/quality/bugs/`
- 使用指南: `/opt/iflow/buger/tools/maintenance/MANUAL_BUG_REPORTING_GUIDE.md`

**参考文档**（外部）:
- `/opt/iflow/buger/tools/maintenance/manual-bug-template.json` - 外部BUGer模板
- `/opt/iflow/buger/tools/maintenance/MANUAL_BUG_REPORTING_GUIDE.md` - 外部BUGer指南

### 🤖 自动报告机制（未来实现）

计划中的自动化功能：

```bash
# Hook触发：git commit时检查是否修复了BUG
# 自动生成BUG报告并保存到 docs/reports/quality/bugs/
# 自动更新经验教训索引
```

**待实现功能**:
1. ✅ Pre-commit hook: 检测commit message是否包含BUG修复
2. ⏳ 自动生成BUG报告: 从diff中提取BUG信息
3. ⏳ 自动更新索引: 提取关键信息更新经验教训文档
4. ⏳ 集成到CI/CD: 测试失败时自动登记BUG

---

**文档版本**: v2.2 (新增BUG经验教训索引)
**最后更新**: 2026-01-08
**维护者**: Main CLI (Claude Code)
**新增说明**: 完整的BUG报告系统和经验教训管理机制
