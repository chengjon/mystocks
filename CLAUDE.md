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
7. [代码质量保证](#代码质量保证)
8. [技术指标管理](#技术指标管理)
9. [监控系统](#监控系统)

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

详细规则: [`docs/guides/MOCK_DATA_USAGE_RULES.md`](./docs/guides/MOCK_DATA_USAGE_RULES.md)

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
- **[Python Quality Assurance Workflow](./docs/guides/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md)** - 代码质量保证流程

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

- **[完整工作流程](./docs/guides/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md)**
- **[快速参考](./docs/guides/PYTHON_QUALITY_TOOLS_QUICK_REFERENCE.md)**
- **[实施总结](./docs/guides/PYTHON_QUALITY_TOOLS_IMPLEMENTATION_SUMMARY.md)**

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

## Task Master AI集成

**导入Task Master开发工作流程命令和指南，视为CLAUDE.md文件的一部分**

详细内容: `@./.taskmaster/CLAUDE.md`

---

**文档版本**: v2.1 (增加技术指标管理章节)
**最后更新**: 2025-12-30
**维护者**: Main CLI (Claude Code)
**优化说明**: 新增技术指标管理章节，63个指标测试全部通过
