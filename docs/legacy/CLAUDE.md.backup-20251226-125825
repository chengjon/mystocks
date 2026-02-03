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

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Note**: This file works in conjunction with the project constitution (`.specify/memory/constitution.md`) and the highest guidance document (`项目开发规范与指导文档.md`) to ensure consistent development practices.

## 🗂️ 重大更新 (2025-11-09): 项目目录重组完成

**目录结构优化**: 从42个杂乱的根目录精简到13个科学组织的目录

**重组成果**:
- ✅ 所有源代码整合到 `src/` 目录
- ✅ 所有文档整合到 `docs/` 目录
- ✅ 所有脚本整合到 `scripts/` 目录
- ✅ 统一导入路径为 `from src.*` 格式
- ✅ 创建 `src/db_manager/` 兼容层确保平滑过渡
- ✅ Git历史完整保留 (使用 `git mv` 移动所有文件)
- ✅ 目录混乱度降低 **69%**

**新的导入路径标准**:
```python
# ✅ 推荐: 新的标准导入路径
from src.core import ConfigDrivenTableManager, DataClassification
from src.adapters.akshare_adapter import AkshareDataSource
from src.data_access import TDengineDataAccess, PostgreSQLDataAccess
from src.db_manager import DatabaseTableManager  # 兼容层
from src.monitoring import MonitoringDatabase, AlertManager
from src.interfaces import IDataSource

# ⚠️ 仍然有效: 旧的导入路径 (通过兼容层)
from core import ConfigDrivenTableManager
from db_manager.database_manager import DatabaseTableManager

# ❌ 已废弃: 直接从根目录导入模块目录
from adapters.akshare_adapter import AkshareDataSource
```

**脚本路径更新**:
```bash
# ✅ 新路径
python scripts/runtime/system_demo.py
python scripts/tests/test_config_driven_table_manager.py
python scripts/database/check_tdengine_tables.py

# ❌ 旧路径
python system_demo.py
python test_config_driven_table_manager.py
```

**详细报告**: 参见 [`REORGANIZATION_COMPLETION_REPORT.md`](./REORGANIZATION_COMPLETION_REPORT.md)

**核心原则**: 清晰的目录结构 + 科学的文件分类 + 完整的Git历史保留

---

## 📊 Current Development Status (2025-11-22)

### Development Progress Summary

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1-3 | Core System (监控/技术分析/多数据源) | ✅ 完成 |
| Phase 4 | GPU API System (回测引擎/ML服务) | ✅ 完成 |
| Phase 5 | Backtest Engine (12个策略) | ✅ 完成 |
| Phase 6 | Technical Debt Remediation | ✅ 完成 |
| Phase 6.4 | GPU加速引擎集成与测试 | ✅ 完成 (68.58x性能提升) |

### GPU加速引擎开发成果

**Phase 6.4 完成情况**:
- **集成测试成功率**: 100% (从85.7%优化到100%)
- **平均性能提升**: 68.58x
- **矩阵运算加速比**: 187.35x (最大306.62x)
- **内存操作加速比**: 82.53x (最大372.72x)
- **峰值性能**: 662.52 GFLOPS
- **长期稳定性**: 83.3%成功率，100%并发安全

**关键技术突破**:
- **HAL层架构**: 4层抽象设计，策略隔离，故障容灾
- **算法优化**: Strassen算法(O(n^2.807))，分块矩阵乘法，CUDA流并行
- **内存管理**: 智能内存池，100%命中率，自动清理机制
- **标准化接口**: GPU/CPU回退机制，生产级稳定性保障

**文档与经验**: 完整的开发经验已记录在 [`docs/api/GPU开发经验总结.md`](./docs/api/GPU开发经验总结.md)

### Technical Debt Status (技术债务现状)

**代码质量指标** (Pylint Analysis):
- Errors: 215 (严重问题，需优先修复)
- Warnings: 2,606 (潜在问题)
- Refactoring: 571 (需要重构)
- Convention: 1,858 (代码风格)

**测试覆盖率目标**:
- 当前覆盖率: ~6% → **目标: 80%**
- 单元测试: 459个 (部分失败)
- data_access层: PostgreSQL 67%, TDengine 56%

**修复计划**:
1. ✅ Phase 1: 配置 `.pylintrc` 和 `.pre-commit-config.yaml`
2. 🔄 Phase 2: 提升测试覆盖率 (进行中)
3. ⏳ Phase 3: 重构高复杂度方法

### Python 代码质量保证工具 (2025-12-23 更新)

**优化策略**: Ruff 优先 + Black 兜底 + Pylint 深度审查

**统一配置**: 所有工具行长度 120 字符

**工具版本**:
- Ruff: 0.9.10 (日常开发 - 效率优先)
- Black: 25.11.0 (格式化兜底)
- Pylint: 4.0.3 (深度质量分析)
- MyPy: (在 dev 依赖中)
- Bandit: 1.7.5+ (安全扫描)
- Safety: 2.3.0+ (依赖安全)

#### 四阶段质量保证流程

**阶段 1: 日常开发** (效率优先)
- **工具**: Ruff (一站式格式化 + Lint)
- **触发时机**: 每次保存文件后
- **命令**: `ruff check --fix .`
- **特点**:
  - 测试专属规则 (PT: pytest 专属规则)
  - 快速失败: 仅检查影响测试执行的问题
  - 自动修复: 大部分问题可自动修复

**阶段 2: 提交前检查** (格式兜底 + 核心检查)
- **工具**: Pre-commit Hooks (自动触发)
- **触发时机**: 每次 `git commit` 时自动运行
- **执行顺序** (9 个步骤):
  1. Ruff (Lint & Fix) - 快速修复错误型问题
  2. Black (Formatter) - 统一代码风格 (1-2秒)
  3. Ruff (Check only) - 二次校验，确保无新问题
  4. MyPy - 类型检查
  5. Bandit - 安全扫描
  6. Safety - 依赖安全检查
  7-9. 通用文件检查、密钥检测、Python 语法检查
- **命令**: `pre-commit run --all-files`

**阶段 3: 定期深度分析** (Pylint 核心价值)
- **工具**: Pylint (测试代码专用配置)
- **触发时机**: 每周 / 每迭代末
- **命令**: `pylint --rcfile=.pylint.test.rc tests/`
- **特点**:
  - 测试专用规则 (`.pylint.test.rc`)
  - 禁用所有，启用核心规则
  - 更宽松的复杂度阈值 (max-args=15, max-locals=25)
  - pytest 专属规则 (PT001-PT025)
  - 生成 HTML 报告

**阶段 4: CI/CD 集成** (快速失败 + 完整检查)
- **工具顺序**: Ruff+Black → MyPy+Bandit+Safety → Pylint (仅记录)
- **策略**:
  - Ruff/Black 问题直接失败 (快速失败)
  - MyPy/Bandit/Safety 问题必须修复 (核心检查)
  - Pylint 仅生成报告，不阻断构建 (记录分析)

#### 关键配置文件

| 配置文件 | 用途 | 位置 |
|----------|------|------|
| `pyproject.toml` | Ruff, Black, MyPy, Pylint (常规) | 项目根目录 |
| `.pylint.test.rc` | Pylint (测试专用) | 项目根目录 |
| `.pre-commit-config.yaml` | Pre-commit hooks | 项目根目录 |
| `config/.security.yml` | 安全配置 | `config/` 目录 |

#### 快速开始

**首次设置**:
```bash
# 安装开发依赖
pip install -e ".[dev]"

# 安装 pre-commit hooks
pre-commit install

# (可选) 安装 pylint-pytest 插件
pip install pylint-pytest

# 验证安装
ruff --version && black --version && pylint --version
```

**日常使用**:
```bash
# 日常开发: 一键修复
ruff check --fix .

# 提交代码: 自动运行 9 步检查
git add . && git commit -m "message"

# 每周分析: 生成质量报告
pylint --rcfile=.pylint.test.rc --output=report.html --output-format=html tests/
```

#### 工作流程图

```
开发代码 → ruff check --fix . → 保存
    ↓
git add → git commit → pre-commit hooks 自动运行
    ↓
    ├─ Ruff (fix) → Black → Ruff (check) → MyPy → Bandit → Safety
    └─ 通用文件检查、密钥检测、Python语法检查
    ↓
提交成功 → 推送到远程 → CI/CD 运行
    ↓
每周末 → pylint --rcfile=.pylint.test.rc tests/ → 生成报告
```

#### 详细文档

完整的 Python 代码质量保证工作流程请参阅:
- **完整工作流程**: `docs/guides/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md`
- **快速参考**: `docs/guides/PYTHON_QUALITY_TOOLS_QUICK_REFERENCE.md`
- **实施总结**: `docs/guides/PYTHON_QUALITY_TOOLS_IMPLEMENTATION_SUMMARY.md`

#### 核心原则

1. **Ruff 优先** - 日常开发快速修复
2. **Black 兜底** - 确保格式统一
3. **Pylint 深度** - 定期质量分析
4. **安全必保** - Bandit + Safety 不可替代
5. **统一配置** - 所有工具行长度 120

**优化成果**:
- ✅ 日常开发效率提升: Ruff 一站式处理
- ✅ 提交前自动化: Pre-commit 9 步检查 (1-2 分钟)
- ✅ 深度质量分析: Pylint 每周/每迭代末
- ✅ CI/CD 优化: 快速失败 + 记录报告

### Core Architecture (核心架构)

```
┌─────────────────────────────────────────────────────────────┐
│                    MyStocks Unified Manager                 │
│              (统一数据访问和路由入口点)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  Adapters   │    │    Core     │    │  Monitoring │     │
│  │  (7个)      │    │  (分类/路由) │    │  (监控/告警) │     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘     │
│         │                  │                  │             │
│  ┌──────▼──────────────────▼──────────────────▼──────┐     │
│  │              Data Access Layer                     │     │
│  │         (TDengineAccess / PostgreSQLAccess)        │     │
│  └──────────────────────┬────────────────────────────┘     │
│                         │                                   │
├─────────────────────────┼───────────────────────────────────┤
│  ┌──────────────────────┴──────────────────────┐           │
│  │              Storage Layer                   │           │
│  │  ┌─────────────────┐  ┌─────────────────┐   │           │
│  │  │    TDengine     │  │   PostgreSQL    │   │           │
│  │  │  (高频时序数据)   │  │  (所有其他数据)  │   │           │
│  │  │  Tick/分钟K线    │  │  日线/参考/交易  │   │           │
│  │  └─────────────────┘  └─────────────────┘   │           │
│  └─────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### Key Dependencies (主要依赖)

**核心框架**:
- Python 3.12+ / FastAPI 0.114+ / Vue 3.4+
- pandas 2.0+ / numpy 1.24+ / pydantic 2.0+

**数据库**:
- TDengine 3.3+ (高频时序) / PostgreSQL 17+ (通用存储)
- TimescaleDB 2.x (时序扩展)

**GPU加速** (可选):
- CUDA 12.x / cuDF 25.10+ / cuML 25.10+ / CuPy 13.6+

**GPU加速引擎开发经验**: 详细的GPU开发经验、问题解决方案和最佳实践请参考 [`docs/api/GPU开发经验总结.md`](./docs/api/GPU开发经验总结.md)

**数据源**:
- akshare / baostock / tushare / efinance

---

## ⚡ Week 3 Update (2025-10-19): Database Simplification

**Major Change**: System simplified from 4 databases to 2 (TDengine + PostgreSQL)

**Migration Completed**:
- ✅ MySQL data migrated to PostgreSQL (18 tables, 299 rows)
- ✅ Redis removed (configured db1 was empty)
- ✅ Architecture complexity reduced by 50%
- ✅ **TDengine retained**: Specialized for high-frequency time-series market data
- ✅ **PostgreSQL**: Handles all other data types with TimescaleDB extension

**New Configuration**: See `.env` for 2-database setup (TDengine + PostgreSQL).

**Philosophy**: Right Tool for Right Job, Simplicity > Unnecessary Complexity

---

## Project Overview

MyStocks is a professional quantitative trading data management system that uses a **dual-database architecture** optimized for different data characteristics. The system is built on adapter and factory patterns to provide unified data access layers with configuration-driven automation.

**Current Architecture** (Post-Week 3):
- **TDengine**: High-frequency time-series market data (tick/minute data) with extreme compression
- **PostgreSQL + TimescaleDB**: All other data types (daily bars, reference data, derived data, metadata)
- **GPU加速引擎**: 高性能矩阵运算和算法加速，实现68.58x平均性能提升
- **Optimized Operations**: Right database for right workload, reduced unnecessary complexity

## Common Development Commands

### Environment Setup
```bash
# Install dependencies (dual-database setup)
pip install pandas numpy pyyaml psycopg2-binary taospy akshare

# Create .env file with database configuration
# Required environment variables for 2-database architecture:
# TDengine (high-frequency time-series data):
# - TDENGINE_HOST, TDENGINE_PORT, TDENGINE_USER, TDENGINE_PASSWORD, TDENGINE_DATABASE
# PostgreSQL (all other data):
# - POSTGRESQL_HOST, POSTGRESQL_USER, POSTGRESQL_PASSWORD, POSTGRESQL_PORT, POSTGRESQL_DATABASE
# - MONITOR_DB_URL (uses PostgreSQL for monitoring database)

# Note: MySQL (pymysql) and Redis removed after Week 3 simplification

# JWT Authentication Configuration
# - JWT_SECRET_KEY (required for API authentication)
# Use the provided script to generate and set up JWT key:
# bash scripts/JWT_key_update.sh
```

### JWT 密钥配置 (JWT_SECRET_KEY)

**问题描述**: 如果启动后端服务时出现 `JWT_SECRET_KEY` 配置错误，需要设置 JWT 密钥。

**解决方案 - 自动化脚本 (推荐)**:
```bash
# 运行自动化脚本，自动生成并配置 JWT_SECRET_KEY
bash scripts/JWT_key_update.sh
```

**解决方案 - 手动配置**:
```bash
# 方法1: 使用 Python 生成密钥
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 方法2: 使用 OpenSSL 生成密钥 (推荐)
openssl rand -hex 32

# 然后将生成的密钥添加到 .env 文件:
# echo "JWT_SECRET_KEY=<生成的密钥>" >> .env
```

**相关文件**:
- 配置脚本: `scripts/JWT_key_update.sh` - 自动化 JWT 密钥配置和服务重启
- 配置模板: `.env.example` - 包含所有必需的环境变量
- 配置文档: `docs/standards/LOCAL_ENV_SETUP.md` - 环境配置完整指南
- 安全指南: `docs/guides/PHASE0_CREDENTIAL_ROTATION_GUIDE.md` - 凭证轮换指南

**后端配置实现** (`web/backend/app/core/config.py`):
```python
# JWT 认证配置字段
jwt_secret_key: str = Field(default="", env="JWT_SECRET_KEY")

# 向后兼容属性
@property
def secret_key(self) -> str:
    return self.jwt_secret_key
```

**注意**: Pydantic-Settings v2 中，字段名 `jwt_secret_key` 在 `case_sensitive=False` 时会自动映射到 `JWT_SECRET_KEY` 环境变量。

---

### System Initialization and Management
```bash
# Initialize the complete system
python -c "from unified_manager import MyStocksUnifiedManager; manager = MyStocksUnifiedManager(); manager.initialize_system()"

# Run system demonstration
python scripts/runtime/system_demo.py

# Validate database connections and table structures
python -c "from core import ConfigDrivenTableManager; mgr = ConfigDrivenTableManager(); mgr.validate_all_table_structures()"

# Run realtime market data saver
python scripts/runtime/run_realtime_market_saver.py

# Check database connections (TDengine + PostgreSQL)
python scripts/database/check_tdengine_tables.py
python scripts/database/verify_tdengine_deployment.py
```

### Testing
```bash
# Test unified manager functionality
python scripts/tests/test_config_driven_table_manager.py

# Test financial adapter
python scripts/tests/test_financial_adapter.py

# Test dual database architecture
python scripts/tests/test_dual_database_architecture.py

# Test realtime data functionality
python scripts/tests/test_save_realtime_data.py

# Test TDX adapter
python scripts/tests/test_tdx_mvp.py

# Test GPU acceleration engine (if available)
python test_gpu_integration.py
python test_performance_comparison.py
python test_long_term_stability.py
```

### Configuration Management
```bash
# View current table configuration
python -c "
import yaml
with open('table_config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
print(f'Configuration version: {config.get(\"version\", \"unknown\")}')
print(f'Tables configured: {len(config.get(\"tables\", []))}')
"

# Create tables from configuration
python -c "from db_manager.database_manager import DatabaseTableManager; mgr = DatabaseTableManager(); mgr.batch_create_tables('table_config.yaml')"
```

## High-Level Architecture

### Mock数据使用规则 (重要)

**核心原则**: 所有模拟数据必须通过 Mock 数据模块提供，**严禁在业务代码中直接硬编码数据**。

详细规则请参阅: [`docs/guides/MOCK_DATA_USAGE_RULES.md`](./guides/MOCK_DATA_USAGE_RULES.md)

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

**主要Mock模块**:
- `src/data_sources/factory.py` - 数据源工厂入口
- `src/data_sources/mock/timeseries_mock.py` - 时序数据
- `src/data_sources/mock/relational_mock.py` - 关系数据
- `src/data_sources/mock/business_mock.py` - 业务数据
- `src/mock/` - 页面级Mock数据

---

### Core Design Principles

1. **Dual-Database Data Storage** (Week 3+): Right database for right workload
   - **High-Frequency Market Data** (高频时序数据): Tick/minute data → **TDengine** (extreme compression, ultra-high write performance)
   - **Daily Market Data** (日线数据): Daily bars, historical data → **PostgreSQL TimescaleDB** hypertables
   - **Reference Data** (参考数据): Relatively static descriptive data → **PostgreSQL** standard tables
   - **Derived Data** (衍生数据): Computed analytical results → **PostgreSQL** standard tables
   - **Transaction Data** (交易数据): Orders, positions, portfolios → **PostgreSQL** standard tables
   - **Meta Data** (元数据): System configuration and metadata → **PostgreSQL** standard tables

2. **Optimized Architecture** (Post-Week 3): 2-database strategy balances performance and simplicity
   - **TDengine database**: `market_data` (超表: tick_data, minute_data)
   - **PostgreSQL database**: `mystocks` (所有其他表 + TimescaleDB混合表)
   - Unified access layer abstracts database differences
   - Monitoring database in PostgreSQL tracks all operations

3. **Configuration-Driven Management**: All table structures managed through YAML configuration
   - `table_config.yaml` defines complete table schemas
   - `ConfigDrivenTableManager` automates table creation and validation

4. **Complete Monitoring Integration**: Separate monitoring database tracks all operations
   - `MonitoringDatabase` logs all operations independent of business databases
   - `PerformanceMonitor` tracks query performance and alerts on slow operations
   - `DataQualityMonitor` ensures data completeness, freshness, and accuracy

### Key Components (重组后的模块路径)

#### Core Management Layer (`src/core/`)
**位置**: `src/core/` 目录
- `DataClassification`: 5大数据分类枚举定义
- `DatabaseTarget`: 支持的数据库类型 (**TDengine**, **PostgreSQL**)
- `DataStorageStrategy`: 智能路由逻辑,自动映射数据类型到最优数据库
- `ConfigDrivenTableManager`: YAML配置驱动的表管理器

**导入**:
```python
from src.core import ConfigDrivenTableManager, DataClassification
from src.core.data_storage_strategy import DataStorageStrategy
```

#### Unified Access Layer (`src/core/` - unified_manager)
**位置**: `src/core/unified_manager.py` + 根目录 `unified_manager.py` (入口点)
- `MyStocksUnifiedManager`: 所有数据操作的统一入口点
- `AutomatedMaintenanceManager`: 定时维护和健康检查
- 自动路由方法: `save_data_by_classification()` 和 `load_data_by_classification()`

**导入**:
```python
from unified_manager import MyStocksUnifiedManager  # 通过根目录入口点
# 或
from src.core.unified_manager import MyStocksUnifiedManager  # 直接导入
```

#### Database Access Layer (`src/data_access/`)
**位置**: `src/data_access/` 目录
- `TDengineDataAccess`: 高频时序数据访问 (tick, 分钟K线)
- `PostgreSQLDataAccess`: 所有其他数据访问 (日线、指标、参考数据、元数据)

**导入**:
```python
from src.data_access import TDengineDataAccess, PostgreSQLDataAccess
```

#### Data Source Adapters (`src/adapters/`)
**位置**: `src/adapters/` 目录 (7个核心适配器)
- 统一接口 `IDataSource` 定义于 `src/interfaces/data_source.py`
- `AkshareDataSource`: Akshare中国市场数据
- `BaostockDataSource`: Baostock历史数据
- `FinancialDataSource`: 财务报表和基本面数据
- `TdxDataSource`: 通达信直连数据源
- `ByapiDataSource`: REST API数据源
- `CustomerDataSource`: 实时行情数据源
- `TushareDataSource`: Tushare专业数据源

**导入**:
```python
from src.adapters.akshare_adapter import AkshareDataSource
from src.adapters.tdx_adapter import TdxDataSource
from src.interfaces import IDataSource
```

#### Database Infrastructure (`src/storage/database/` + 兼容层 `src/db_manager/`)
**实际位置**: `src/storage/database/` 目录
**兼容层**: `src/db_manager/` (重导出 `src.storage.database` 的所有类)

- `DatabaseTableManager`: 双数据库连接和表管理
- `DatabaseConnectionManager`: 数据库连接池管理
- 支持 **TDengine** (WebSocket/Native) 和 **PostgreSQL** (TimescaleDB扩展)
- 环境变量驱动配置,确保安全性

**导入** (两种方式均可):
```python
# 方式1: 通过兼容层 (旧代码可继续使用)
from src.db_manager import DatabaseTableManager, DatabaseConnectionManager

# 方式2: 直接导入 (推荐)
from src.storage.database import DatabaseTableManager, DatabaseConnectionManager
```

#### Monitoring and Quality (`src/monitoring/`)
**位置**: `src/monitoring/` 目录
- `MonitoringDatabase`: 独立监控数据库
- `DataQualityMonitor`: 数据完整性、准确性、新鲜度检查
- `PerformanceMonitor`: 查询性能跟踪和慢查询检测
- `AlertManager`: 多渠道告警 (邮件、Webhook、日志)

**导入**:
```python
from src.monitoring import MonitoringDatabase, DataQualityMonitor
from src.monitoring import PerformanceMonitor, AlertManager
```

#### GPU Acceleration Engine (`src/gpu/`)
**位置**: `src/gpu/` 目录
- **Hardware Abstraction Layer (HAL)**: `src/gpu/core/hardware_abstraction/`
  - `GPUResourceManager`: GPU资源管理器，策略隔离和故障容灾
  - `StrategyGPUContext`: 策略GPU上下文管理
  - `MemoryPool`: 智能内存池管理，100%命中率
- **Kernel Layer**: `src/gpu/core/kernels/`
  - `MatrixKernelEngine`: 矩阵运算引擎，支持Strassen算法和分块优化
  - `TransformKernelEngine`: 数据变换引擎，支持FFT等算法
  - `StandardizedKernelInterface`: 标准化内核接口，支持GPU/CPU回退
- **API System**: `src/gpu/api_system/`
  - `gpu_api_server`: GPU加速API服务器
  - 集成测试和性能监控

**核心成就**:
- **68.58x平均性能提升**，矩阵运算最高187.35x加速比
- **662+ GFLOPS峰值性能**，100%集成测试通过率
- **生产级稳定性**，长期运行验证和故障容灾机制

**导入**:
```python
from src.gpu.core.hardware_abstraction.resource_manager import GPUResourceManager
from src.gpu.core.kernels.matrix_kernels import MatrixKernelEngine
from src.gpu.core.kernels.standardized_interface import StandardizedKernelInterface
```

### Data Flow Architecture

1. **Data Ingestion**: External adapters → Unified Manager → Auto-routing
2. **Storage Strategy**: Classification determines optimal database automatically
3. **Access Pattern**: Unified interface regardless of underlying database
4. **Monitoring**: All operations logged to separate monitoring database
5. **Quality Assurance**: Automated data quality checks and alerts

### Database Specialization Strategy

- **TDengine**: Extreme compression (20:1 ratio), ultra-high write performance for high-frequency market data (tick/minute)
  - Native time-series database optimized for IoT and financial data
  - Automatic data retention policies
  - Superior performance for time-range queries on tick data

- **PostgreSQL + TimescaleDB**: Robust relational database with time-series optimization
  - ACID compliance for all transactional data
  - Complex JOIN operations on reference and derived data
  - TimescaleDB hypertables for daily market data
  - Full-text search and advanced indexing

## Important Implementation Notes

### Configuration Management
- All database connections configured via environment variables (never hardcode credentials)
- `table_config.yaml` contains complete table schemas with support for all database types
- Tables auto-created on system initialization via `ConfigDrivenTableManager`

### Data Operations
- Always use `MyStocksUnifiedManager` as the primary entry point
- Classification-based methods: `save_data_by_classification()`, `load_data_by_classification()`
- System automatically selects optimal database based on data classification

### Error Handling and Monitoring
- All operations automatically logged to monitoring database
- Performance metrics tracked and slow operations flagged
- Data quality checks run automatically with configurable thresholds

### Testing and Validation
- Use `system_demo.py` for comprehensive system testing
- Individual component tests available in `test_*.py` files
- Database validation available via `check_*_tables.py` scripts

### Dual-Database Support
- **TDengine** for high-frequency time-series data (tick, minute bars)
- **PostgreSQL** for all other data types (daily bars, reference, metadata)
- Unified access layer abstracts database differences
- Seamless connection management and automatic routing

This architecture enables efficient handling of quantitative trading data by using the right database for each workload, with comprehensive monitoring and configuration-driven automation.

## File Organization Rules

**Philosophy**: Maintain a clean, minimal root directory with logical categorization by functionality. Every file should have a clear, rule-based location.

**代码大小优化规范**: 为了保证代码的可维护性和可读性，强烈建议遵循[《代码文件长度优化规范》](./CODE_SIZE_OPTIMIZATION_REPORT.md)。该规范要求：

1. **代码文件长度限制**: 单个Python文件应控制在2000行以内，大于此限制的文件需要进行模块化拆分
2. **模块化拆分原则**: 将大文件按照功能拆分为多个小文件，每个文件专注于特定功能
3. **向后兼容性**: 拆分后的代码应保持原有的导入路径不变，确保现有代码可以正常工作
4. **排除目录**: temp目录及其子目录下的所有文件不纳入长度优化范围

遵循此规范有助于提高代码质量，降低维护难度，并提升开发效率。详细内容请参阅[《代码文件长度优化规范》](./CODE_SIZE_OPTIMIZATION_REPORT.md)。

### Root Directory Standards

**ONLY these 5 core files belong in root**:
- `README.md` - Project overview and main documentation
- `CLAUDE.md` - Claude Code integration guide (this file)
- `CHANGELOG.md` - Version history and changes
- `requirements.txt` - Python dependencies
- `.mcp.json` - MCP server configuration

**All other files MUST be organized into subdirectories**.

### Directory Structure and Rules

#### 1. **scripts/** - All Executable Scripts

Organized by functionality into 4 categories:

**scripts/tests/** - Test Files
- **Pattern**: Files prefixed with `test_`
- **Purpose**: Unit tests, integration tests, acceptance tests
- **Examples**: `test_config_driven_table_manager.py`, `test_financial_adapter.py`
- **Special files**: `test_requirements.txt`, `coverage.xml`

**scripts/runtime/** - Production Runtime Scripts
- **Pattern**: Files prefixed with `run_`, `save_`, `monitor_`, or `*_demo.py`
- **Purpose**: Production data collection, monitoring, demonstrations
- **Examples**: `run_realtime_market_saver.py`, `save_realtime_data.py`, `system_demo.py`

**scripts/database/** - Database Operations
- **Pattern**: Files prefixed with `check_`, `verify_`, `create_`
- **Purpose**: Database initialization, validation, management
- **Examples**: `check_tdengine_tables.py`, `verify_tdengine_deployment.py`

**scripts/dev/** - Development Tools
- **Pattern**: Development utilities not fitting other categories
- **Purpose**: Code validation, testing utilities, development aids
- **Examples**: `gpu_test_examples.py`, `validate_documentation_consistency.py`
- **Special files**: `git_commit_comments.txt`

#### 2. **docs/** - Documentation Files

**docs/guides/** - User and Developer Guides
- **Files**: `QUICKSTART.md`, `IFLOW.md`, tutorial documents
- **Purpose**: Getting started guides, workflow documentation

**docs/archived/** - Deprecated Documentation
- **Files**: `START_HERE.md`, `TASKMASTER_START_HERE.md` (kept for historical reference)
- **Purpose**: Preserve old documentation without cluttering active docs
- **Rule**: Add deprecation notice at top of file when archiving

**docs/architecture/** - Architecture Design Documents
- **Purpose**: System design, technical architecture documentation
- **Examples**: Database design docs, system architecture diagrams

**docs/api/** - API Documentation
- **Purpose**: API reference, endpoint documentation, SDK guides

#### 3. **config/** - Configuration Files

**All configuration files** (regardless of extension):
- **Extensions**: `.yaml`, `.yml`, `.ini`, `.toml`, `docker-compose.*.yml`
- **Examples**:
  - `mystocks_table_config.yaml` - Table structure definitions
  - `docker-compose.tdengine.yml` - Docker setup
  - `pytest.ini` - Test configuration
  - `.readthedocs.yaml` - Documentation build config

#### 4. **reports/** - Generated Reports and Analysis

**Pattern**: Files generated by analysis scripts, timestamped if recurring
- **Extensions**: `.json`, `.txt`, analysis outputs
- **Examples**:
  - `database_assessment_20251019_165817.json`
  - `query_patterns_analysis.txt`
  - `dump_result.txt`
  - `WENCAI_INTEGRATION_FILES.txt`

**Naming Convention**: Use ISO date format for timestamped files: `YYYYMMDD_HHMMSS`

### File Lifecycle Management

#### Pre-Classification (Proactive)

**When creating new files**, place them directly in the correct location:

1. **Determine file purpose**: Test? Runtime? Configuration? Documentation?
2. **Match against rules**: Use the directory structure above
3. **Create in correct location**: Never create in root unless it's one of the 5 core files

**Example Pre-Classification**:
```python
# Creating a new test file
# ✅ CORRECT: Create directly in scripts/tests/
with open('scripts/tests/test_new_feature.py', 'w') as f:
    f.write(test_code)

# ❌ INCORRECT: Creating in root
with open('test_new_feature.py', 'w') as f:
    f.write(test_code)
```

#### Post-Classification (Reactive)

**When organizing existing files**:

1. **Identify misplaced files**: Use `ls` or `find` to list root directory files
2. **Categorize by rules**: Match each file against the directory structure rules
3. **Plan the reorganization**: Create a categorization plan before execution
4. **Use git mv**: Preserve file history when moving tracked files
5. **Update references**: Update all import paths, documentation links
6. **Validate**: Test that moved files work correctly

**Post-Classification Workflow**:
```bash
# 1. List root directory files (exclude core 5)
ls -1 | grep -v -E '^(README\.md|CLAUDE\.md|CHANGELOG\.md|requirements\.txt|\.mcp\.json)$'

# 2. For each file, determine correct location using rules above

# 3. Move files (use git mv for tracked files)
git mv test_something.py scripts/tests/
git mv run_collector.py scripts/runtime/
git mv config.yaml config/
git mv analysis_report.txt reports/

# 4. Update references in affected files

# 5. Commit with descriptive message
git commit -m "refactor: organize files according to directory structure rules"
```

### Import Path Management for Scripts

**Critical Rule**: All scripts in nested directories must calculate project root correctly.

**Standard Pattern for scripts in `scripts/**/`**:
```python
import sys
import os
from pathlib import Path

# Calculate project root (3 levels up from script location)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Now you can import from project root
from core import ConfigDrivenTableManager
from adapters.akshare_adapter import AkshareDataSource
from db_manager.database_manager import DatabaseTableManager
```

**Explanation**:
- Script in `scripts/tests/test_something.py`
- `__file__` → `scripts/tests/test_something.py`
- `os.path.dirname(__file__)` → `scripts/tests/`
- `os.path.dirname(os.path.dirname(__file__))` → `scripts/`
- `os.path.dirname(os.path.dirname(os.path.dirname(__file__)))` → project root `/opt/claude/mystocks_spec/`

### Git Best Practices

**Always use `git mv` for tracked files**:
```bash
# ✅ CORRECT: Preserves file history
git mv old_location/file.py new_location/file.py

# ❌ INCORRECT: Breaks file history
mv old_location/file.py new_location/file.py
git add new_location/file.py
```

**For untracked files**, regular `mv` is fine:
```bash
# For files not in git yet
mv untracked_file.log reports/
```

### Validation Checklist

After any file reorganization:

- [ ] Root directory contains only the 5 core files
- [ ] All scripts properly categorized in scripts/{tests,runtime,database,dev}
- [ ] All documentation in docs/{guides,archived,architecture,api}
- [ ] All configuration files in config/
- [ ] All reports in reports/
- [ ] All moved scripts have updated import paths (3-level dirname)
- [ ] All documentation links updated to new paths
- [ ] `git status` shows moves (not deletions + additions)
- [ ] All tests pass after reorganization
- [ ] `scripts/README.md` is up to date

### Common Mistakes to Avoid

1. **Creating files in root**: Always use subdirectories unless it's one of the 5 core files
2. **Wrong import paths**: Remember to use 3-level dirname for scripts in nested directories
3. **Using `mv` instead of `git mv`**: Always preserve git history
4. **Forgetting to update references**: Check all imports, documentation links
5. **Mixing purposes**: Don't put test files in runtime/, or config files in docs/

### Reference Documentation

For detailed directory contents and file inventory:
- **Complete documentation structure**: See `docs/DOCUMENTATION_STRUCTURE.md`
- **Script organization guide**: See `scripts/README.md`

## Task Master AI Instructions
**Import Task Master's development workflow commands and guidelines, treat as if import is in the main CLAUDE.md file.**
@./.taskmaster/CLAUDE.md
