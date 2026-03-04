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

# AGENTS.md - Coding Agent Configuration

## Project Overview

**MyStocks** 是一套面向量化交易的全栈数据管理系统，核心目标：
- 整合多源市场数据（股票/ETF/行业资金流向等），提供实时监控、技术分析、风险评估能力
- 基于双数据库架构（TDengine+PostgreSQL）实现高频时序数据与结构化数据的高效存储/查询
- 支撑量化策略回测、实时交易风控、多维度数据可视化（60+前端页面）
- Phase 5+ 目标：完成E2E测试覆盖、容器化部署、性能优化（API响应≤300ms）、生产级监控

**基本信息**：
- 项目类型: Python 量化交易数据管理系统
- 当前版本: v2.0.0
- Python 版本: 3.12+ (使用 3.12.11)
- Git 仓库: git@github.com:chengjon/mystocks.git
- 许可证: MIT

---

## Global Architecture Standards

- 执行任何代码修改前，必须先阅读 `architecture/STANDARDS.md`。
- `方案先行准则 (Proposal-First Rule)`、`六步走战略`、`Docker 一等公民原则` 统一以 `architecture/STANDARDS.md` 为准。
- 本文件只保留 Agent 执行层面的流程、命令和协作规范，避免重复维护共享规则正文。

---

## Git Branch Detection and Workflow

**Critical**: Determine the current git branch to follow the correct workflow.

```bash
# Detect current branch
git branch --show-current
# OR
git rev-parse --abbrev-ref HEAD
```

**Workflow Rules**:
- **If branch is `main`**: Follow Main CLI responsibilities
  - Coordination role: use `.FILE_OWNERSHIP` to assign tasks
  - Monitor worker progress via `TASK.md` and `TASK-REPORT.md` (worker artifacts)
  - No direct task reporting in worker task files
  - Reference: `docs/guides/MULTI_CLI_WORKTREE_MANAGEMENT.md`

- **If branch is non-main** (worktree): Follow Worker CLI workflow
  - Use `TASK.md` + `TASK-REPORT.md` (+ `TASK-*-REPORT.md`) in worktree root
  - Report progress and completion status
  - Reference: `docs/guides/GIT_WORKTREE_MAIN_CLI_MANUAL.md`

---

## Build/Lint/Test Commands

### Python Tests
```bash
# Run all tests (with coverage)
pytest

# Run specific test file
pytest tests/unit/test_specific_module.py

# Run specific test function
pytest tests/unit/test_specific_module.py::test_specific_function

# Run with markers
pytest -m unit                    # Unit tests only
pytest -m integration             # Integration tests only
pytest -m "not slow"              # Skip slow tests
pytest -m gpu                     # GPU tests (requires GPU)

# Run with coverage report
pytest --cov=src --cov=web/backend/app --cov-report=html

# Run parallel tests
pytest -n auto                    # Auto-detect CPU cores
```

### Frontend Tests
```bash
# Unit tests (Vitest)
cd web/frontend && npm run test
npm run test:watch                # Watch mode
npm run test:coverage             # With coverage

# E2E tests (Playwright)
npm run test:e2e                  # All E2E tests
npm run test:e2e:chromium         # Chromium only
npm run test:e2e:firefox          # Firefox only
npm run test:e2e:webkit           # WebKit only
npm run test:e2e:ui               # UI mode
npm run test:e2e:debug            # Debug mode
```

### Linting & Formatting
```bash
# Python linting
black .                           # Format code
black --check .                   # Check formatting
mypy src/                         # Type checking
ruff check src/                   # Fast linting
pylint src/                       # Deep analysis

# Frontend linting
cd web/frontend && npm run lint   # ESLint
npm run lint:artdeco              # ArtDeco tokens check
```

### Security Scanning
```bash
bandit -r src/                    # Security issues
safety check                      # Dependency vulnerabilities
```

### Development Server
```bash
# Backend (FastAPI)
cd web/backend && python -m uvicorn app.main:app --reload --port 8888

# Frontend (Vite)
cd web/frontend && npm run dev

# PM2 production
npm run pm2:start                 # Start with PM2
npm run pm2:stop                  # Stop PM2
npm run pm2:logs                  # View logs
```

---

## Code Style Guidelines

### Imports
- Use absolute imports with `src.` prefix: `from src.core import ConfigDrivenTableManager`
- Group imports: standard library, third-party, local imports
- Avoid wildcard imports
- Use explicit imports for clarity

### Formatting
- Use Black formatter with **line-length: 120** (see pyproject.toml)
- Use double quotes for strings
- Use 4 spaces for indentation
- Ruff is configured for fast linting with Black compatibility

### Types
- Use type hints for all function parameters and return values
- Prefer `from __future__ import annotations` for forward references
- Use Pydantic models for data validation where appropriate

### Naming Conventions
- Classes: PascalCase (`DataManager`)
- Functions/Variables: snake_case (`save_data_by_classification`)
- Constants: UPPER_SNAKE_CASE (`DATABASE_CONFIG`)
- Private members: prefixed with underscore (`_private_method`)
- API paths: kebab-case (`/api/market-data/stock`)
- Database tables: snake_case with module prefix (`market_daily_kline`)

### Error Handling
- Use specific exception types
- Log errors with context before raising
- Implement retry logic for external API calls
- Use context managers for resource management

### Project Structure
```
/opt/claude/mystocks_spec/
├── src/                    # 核心源代码 (35+ 模块)
│   ├── adapters/           # 数据源适配器 (7个核心适配器)
│   ├── core/               # 核心管理类
│   ├── ml_strategy/        # 机器学习策略系统
│   ├── gpu/                # GPU 加速系统
│   ├── monitoring/         # 监控和告警系统
│   ├── data_access/        # 数据库访问层
│   ├── governance/         # 风险治理模块
│   ├── backtesting/        # 回测引擎
│   └── ...
├── web/
│   ├── backend/            # FastAPI 后端
│   │   ├── app/api/        # API 端点
│   │   ├── app/services/   # 业务服务
│   │   └── app/schemas/    # 数据模式
│   └── frontend/           # Vue 3 前端
│       ├── src/views/      # 页面视图
│       ├── src/components/ # Vue 组件
│       ├── src/stores/     # Pinia 状态管理
│       └── src/api/        # API 调用
├── config/                 # 配置文件
├── scripts/                # 脚本工具
├── tests/                  # 测试代码
├── docs/                   # 文档
├── openspec/               # OpenSpec 变更管理
└── .claude/                # Claude Code 系统
```

---

## Database Architecture

### Dual Database Strategy
- **TDengine 3.0+**: 高频时序数据专用库
  - Tick 数据、分钟 K 线、实时深度
  - 极高压缩比(20:1)、超强写入性能、列式存储
  - 超表命名: `ts_` 前缀 (如 `ts_tick_data`)

- **PostgreSQL 15+ (TimescaleDB)**: 通用数据仓库
  - 日线 K 线、技术指标、量化因子、参考数据、交易数据、元数据
  - 自动分区、复杂查询、ACID 事务、JSON 支持

### Data Classification
使用 `DataClassification` 枚举进行数据分类：
- `TICK_DATA`: 逐笔成交数据
- `MINUTE_KLINE`: 分钟 K 线
- `DAILY_KLINE`: 日线数据
- `TECHNICAL_INDICATOR`: 技术指标
- `REFERENCE_DATA`: 参考数据

### Key Import Patterns
```python
# Core components
from src.core import ConfigDrivenTableManager, DataClassification
from src.core.unified_manager import MyStocksUnifiedManager

# Data access
from src.data_access import TDengineDataAccess, PostgreSQLDataAccess

# Adapters
from src.adapters.akshare_adapter import AkshareDataSource
from src.interfaces import IDataSource

# Database management
from src.storage.database import DatabaseTableManager

# GPU API system
from src.gpu.api_system.services import GPUBacktestService, GPURealtimeService

# Monitoring
from src.monitoring import MonitoringDatabase, AlertManager

# Web API
from web.backend.app.api import trading_signals_api, monitoring_api
```

---

## Tech Stack

### Backend
- **Framework**: FastAPI (异步API)
- **Validation**: Pydantic v2
- **Database**: SQLAlchemy 2.0
- **Task Queue**: Celery
- **Cache**: Redis
- **Monitoring**: Prometheus + Grafana

### Frontend
- **Framework**: Vue 3 + Composition API
- **UI Library**: Element Plus
- **State**: Pinia
- **Router**: Vue Router 4
- **Charts**: ECharts + KLineCharts
- **Build**: Vite 5
- **Testing**: Vitest + Playwright

### Data Sources (7 Adapters)
1. **tdx_adapter**: 通达信直连，无限流
2. **financial_adapter**: 双数据源(efinance+easyquotation)
3. **akshare_adapter**: 免费全面，历史数据研究首选
4. **byapi_adapter**: REST API，涨跌停股池
5. **customer_adapter**: 实时行情专用
6. **baostock_adapter**: 高质量历史数据
7. **tushare_adapter**: 专业级，需 token

### GPU Acceleration (Optional)
- **RAPIDS**: cuDF/cuML 一体化 GPU 加速
- **Performance**: 15-44倍回测加速
- **WSL2 Support**: 完整解决 WSL2 环境下 GPU 访问问题

---

## Testing Strategy

### Test Markers
```python
# Available markers in pytest.ini
@pytest.mark.unit          # Unit tests
@pytest.mark.integration   # Integration tests
@pytest.mark.slow          # Slow tests (skip with -m "not slow")
@pytest.mark.network       # Requires network access
@pytest.mark.gpu           # Requires GPU support
@pytest.mark.frontend      # Frontend-related tests
@pytest.mark.playwright    # Playwright browser automation
```

### Coverage Requirements
- Unit tests: ≥95% pass rate
- E2E tests: ≥95% pass rate
- API P95 response: ≤300ms
- Coverage threshold: 30% (configured in pytest.ini)

### Mandatory Quality Status Confirmation (Must Follow)
每次涉及前端构建、类型检查、E2E或服务启动的任务结束时，必须附带以下状态确认，不允许省略：
方案审批门禁请遵循 `architecture/STANDARDS.md` 的“零、统一治理与审批门禁”。

| 检查项 | 强制要求 |
|--------|----------|
| 结构性语法错误 | 必须为 `0`（阻塞项） |
| 类型推断错误 | 当前基线以 `reports/analysis/tech-debt-baseline.json` 的 `frontend_type_errors` 为准（历史技术债按优先级分阶段治理） |
| PM2 服务 | 必须确认运行中（`mystocks-backend` 与 `mystocks-frontend`） |
| E2E 测试 | 必须报告通过情况（当前基线 `18/18`） |

执行与报告规范：
- 必须明确区分“本次引入问题”与“仓库既有技术债务”。
- 若出现类型推断错误（如 `'x' is of type 'unknown'`），必须标注其是否为预先存在问题。
- 在结构性语法错误为 `0` 且 E2E 通过时，可判定为“可运行”；类型推断债务不应被误报为本次回归。
- 若本次改动导致类型推断错误数量高于基线文件 `reports/analysis/tech-debt-baseline.json` 的 `frontend_type_errors`，视为回归，必须在合并前修复或回退改动。
- 状态确认中必须包含服务访问地址：
  - `mystocks-backend`: `http://localhost:8020`
  - `mystocks-frontend`: `http://localhost:3020`
- 技术债治理执行章程统一参考 `docs/guides/technical-debt-governance-charter-v1.md`，门禁、基线、豁免与周报模板以该文档为准，并与 `CLAUDE.md` 保持一致。

类型推断债务治理（长期工作，非单次会话可完成）：

**治理策略：先分级再分阶段**

1. **错误分级**：
   - 高优先级：影响核心业务逻辑（组件 Props 未声明、接口返回值用 any、工具函数类型模糊）
   - 中优先级：增加维护成本但不影响运行（边缘工具函数、局部变量推断模糊）
   - 低优先级：历史代码/废弃模块中的错误

2. **分阶段治理**：
   - 短期（1-2周）：修复高优先级错误，替换 any、显式声明 Props/Emits
   - 中期（1-2月）：覆盖中优先级错误，补充泛型和类型声明
   - 长期：常态化治理，每次迭代预留时间消化低优先级错误

3. **工具提效**：
   - CI/CD 集成 vue-tsc --noEmit 与技术债基线对比门禁，校验类型错误不高于基线文件
   - 编写脚本统计错误分布，生成可视化报告
   - 新模块开启 strict: true，老模块用 @ts-ignore 兼容

4. **规范预防**：
   - 组件 Props/Emits 必须显式声明类型
   - 工具函数、接口返回值禁止滥用 any
   - 第三方库无类型时手动编写 .d.ts 声明文件
   - 代码评审标准：无新增高优先级类型推断错误

### Test Directory Structure
```
tests/
├── unit/              # 单元测试
├── integration/       # 集成测试
├── contract/          # 契约测试
├── e2e/               # 端到端测试
├── performance/       # 性能测试
└── security/          # 安全测试
```

---

## 推荐开发流程与环境一致性（统一引用）

以下共享规范已统一收敛到 `architecture/STANDARDS.md`，此处不再重复正文：

- “零、统一治理与审批门禁”（含 `Proposal-First Rule`）
- “一、推荐开发流程：六步走战略”
- “二、技术工程红线 -> 3. 环境一致性”（Docker/PM2 一等公民）

---

## CI/CD Workflows

### Available Workflows (.github/workflows/)
| Workflow | Purpose |
|----------|---------|
| `code-quality.yml` | 代码质量检查 (Black, MyPy, Ruff, Bandit, Safety) |
| `test-coverage.yml` | 测试覆盖率报告 |
| `security-testing.yml` | 安全漏洞扫描 |
| `comprehensive-testing.yml` | 全栈集成测试 |
| `e2e-testing.yml` | 端到端测试 (Playwright) |
| `api-compliance-testing.yml` | API合规性验证 |
| `contract-testing.yml` | 合同测试 |
| `frontend-testing.yml` | 前端测试 |
| `p0-quality-gate.yml` | P0 质量门禁 |
| `quant-strategy-validation.yml` | 量化策略验证 |

---

## OpenSpec Workflow

- Always open `@/openspec/AGENTS.md` when the request mentions planning or proposals
- Use OpenSpec for introducing new capabilities, breaking changes, architecture shifts
- Follow the change proposal format in `openspec/changes/`
- Keep managed blocks for 'openspec update' to refresh instructions

### Quick Commands
```bash
openspec list                  # List active changes
openspec list --specs          # List specifications
openspec show [item]           # Display change or spec
openspec validate [item]       # Validate changes or specs
openspec archive <change-id>   # Archive after deployment
```

---

## Skill 手动加载

当自动激活未触发时，可使用 `/skill` 命令手动加载技能包：

```
/skill vue3          # 加载 Vue 3 官方指南与 API 参考（全局 skill）
```

全局 skill 位置：`/root/.claude/skills/`，项目级 skill 位置：`.claude/skills/`。

---

## Advanced Architecture Features

### 智能数据路由 (Intelligent Data Routing)
- **自适应路由算法**: 根据数据类型、访问频率和系统负载自动选择最优存储引擎
- **实时性能监控**: 持续监控各数据库性能指标，动态调整路由策略
- **负载均衡**: 在多个数据源间智能分配查询压力
- **故障自动转移**: 当主数据源故障时，自动切换到备用数据源

### TDD方法应用 (Test-Driven Development)
- **红绿重构循环**: 严格遵循测试先行、快速反馈、重构优化的TDD开发流程
- **测试覆盖率驱动**: 确保核心业务逻辑测试覆盖率达到95%以上
- **行为驱动测试**: 使用BDD框架(Gherkin/Cucumber)编写业务可读的测试用例

### DDD架构实施 (Domain-Driven Design)
- **领域建模**: 通过事件风暴和工作坊识别和定义核心业务领域
- **聚合设计**: 明确聚合根、实体、值对象和服务对象的职责边界
- **领域服务**: 封装复杂业务逻辑，确保领域层的纯净性
- **上下文映射**: 定义限界上下文间的集成关系和防腐层

### 智能量化监控与投资组合管理系统
- **实时风险监控**: 基于VaR、CVaR等指标的实时风险评估和预警
- **投资组合优化**: 使用现代投资组合理论(Markowitz模型)进行资产配置优化
- **绩效归因分析**: 深入分析投资组合收益来源和风险贡献
- **智能再平衡**: 根据市场条件和风险偏好自动调整投资组合权重

### 信号监控管理系统
- **多维度信号聚合**: 整合技术指标、基本面和量化信号的统一监控平台
- **信号质量评估**: 通过回测和实盘表现评估信号的有效性和稳定性
- **实时信号分发**: WebSocket推送和消息队列确保信号的低延迟传递
- **信号回溯分析**: 完整的信号生成、执行和结果的审计追踪

---

## Key Business Rules

### 数据更新频率
- Tick数据: 实时推送 (WebSocket)
- 日线数据: 每日收盘后更新
- 缓存失效: 市场闭市后清空当日缓存

### 风控阈值
- 单股票仓位: ≤10%
- 单日最大亏损: ≤5%
- 触发后自动平仓

### 数据源优先级
- 优先使用官方数据源
- 失败后自动切换到备用数据源（7个数据源轮询）

### 生产环境约束
- 服务器资源: 8核16G
- 可用性要求: 99.9%（每月故障时间≤43分钟）
- 数据保留: Tick数据保留3个月，分钟级数据保留1年，日线数据永久保留
- 安全要求: JWT Token有效期2小时

---

## File Ownership Reference

See `.FILE_OWNERSHIP` for detailed ownership mapping. Quick reference:

| Directory/Pattern | Owner | Notes |
|-------------------|-------|-------|
| `src/` | main | 核心业务逻辑 |
| `config/` | main | 配置文件 |
| `web/frontend/src/components/Charts/` | cli-1 | K线图组件 |
| `docs/api/contracts/` | cli-2 | API契约文档 |
| `src/gpu/` | cli-5 | GPU相关代码 |
| `tests/` | cli-6 | 测试文件 |
| `README.md` | main+clis | 主CLI维护，CLI可建议 |

---

## Quick Reference

### 常用命令
```bash
# 数据库服务
docker-compose up -d tdengine postgresql

# 系统初始化
python scripts/runtime/system_demo.py

# 后端服务
cd web/backend && python -m uvicorn app.main:app --reload

# 前端服务
cd web/frontend && npm run dev

# 测试系统
pytest tests/ -v

# 代码质量
black . && mypy src/ && ruff check src/
```

### 环境配置
```bash
# 环境变量
cat .env

# 数据库连接
python scripts/database/check_tdengine_tables.py
python scripts/database/check_postgresql_tables.py
```
