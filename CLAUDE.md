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

# CLAUDE.md - MyStocks AI Development Guide (Claude/OpenCode)

本文件是给 AI coding agent/CLI 的“项目工作手册”。目标是让 Agent 在 MyStocks 仓库里稳定、高质量地完成任务：知道该看什么、该改哪里、怎么验证、哪些是硬性约束。

如果你是人类开发者：这里也可以作为快速上手的索引，但不替代 `README.md`、`docs/` 的产品/架构文档。

---

## 0. Read This First (必读)

1. **命令与代码风格的权威来源**: `AGENTS.md`
   - 测试/质量命令、导入规范、目录结构等都在 `AGENTS.md`
2. **遇到“计划/提案/架构调整”**: 先打开 `openspec/AGENTS.md`
   - 按 OpenSpec 流程写变更提案，再实现
3. **不要在 `/tmp` 存放正式文件**
   - 正式文档 -> `docs/`；脚本 -> `scripts/`；配置 -> `config/`

---

## 1. Project Overview (项目概览)

MyStocks 是量化交易数据管理系统，核心特点：

- **双数据库架构**: TDengine (高频时序) + PostgreSQL/TimescaleDB (其他数据)
- **配置驱动表管理**: 通过 YAML 配置自动创建/验证表结构
- **统一访问入口**: `MyStocksUnifiedManager` 负责路由、读写、维护
- **可观测性**: LGTM Stack (Loki/Grafana/Tempo/Prometheus) + 独立监控数据库
- **GPU 加速系统**(可选): `gpu_api_system/` 与 `src/gpu/`

---

## 2. Non-Negotiables (硬性规则)

- **最小变更**: 只改与任务直接相关的代码/文档；不要顺手重构。
- **不要回滚用户已有改动**: 除非用户明确要求。
- **证据优先**: 声称“已修复/已通过”前，先运行对应命令并确认输出。
- **避免泄露敏感信息**: 不要提交 `.env`、私钥、token、账号口令。

### Web 平台支持策略 (重要)

本项目仅支持 Web 桌面端：

- ✅ 桌面浏览器 (Chrome/Firefox/Safari/Edge)
- ✅ 最小分辨率 1280x720
- ❌ 不做移动端/平板端适配
- ❌ 禁止加入移动端响应式样式：不要写 `@media (max-width: ...)` 之类规则

---

## 3. Repository Map (目录速查)

- `src/`: Python 核心业务代码
- `web/backend/`: FastAPI 后端
- `web/frontend/`: Vue 3 前端
- `config/`: 配置文件（YAML/TOML/INI/compose 等）
- `scripts/`: 可执行脚本（runtime/tests/database/dev 分类）
- `docs/`: 项目文档（指南/报告/架构/API 等）
- `gpu_api_system/`: GPU API 系统（可选）
- `monitoring-stack/`: 监控栈 (Prometheus/Grafana/Loki/Tempo)

常用入口点：

- `src/core/unified_manager.py`: `MyStocksUnifiedManager`（统一数据入口）
- `src/adapters/`: 外部数据源适配器
- `src/data_access/`: TDengine / PostgreSQL 数据访问层

---

## 4. Architecture Cheat Sheet (架构速记)

### 4.1 Dual-DB Routing (双库路由)

- TDengine: tick / 分钟级等高频时序数据
- PostgreSQL(+TimescaleDB): 日线、参考、衍生、交易、元数据等
- 统一入口负责“按分类路由”，不要在业务里直接硬编码“写哪个库”

### 4.2 Key Import Patterns (推荐导入)

```python
from src.core import ConfigDrivenTableManager, DataClassification
from src.core.unified_manager import MyStocksUnifiedManager

from src.data_access import TDengineDataAccess, PostgreSQLDataAccess
from src.adapters.akshare_adapter import AkshareDataSource
```

兼容入口（历史原因仍可用）：

```python
from unified_manager import MyStocksUnifiedManager
```

---

## 5. Daily Workflows (常用工作流)

命令以 `AGENTS.md` 为准；这里仅给“最短路径”。

### 5.1 Tests / Lint / Type Check

```bash
pytest
ruff check src/
black --check .
mypy src/ --no-error-summary
```

### 5.2 Run Web Backend (FastAPI)

```bash
cd web/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5.3 Run Web Frontend (Vue)

```bash
cd web/frontend
npm install
npm run dev -- --port 3001
```

### 5.4 Initialize / Demo

```bash
python -c "from unified_manager import MyStocksUnifiedManager; MyStocksUnifiedManager().initialize_system()"
python scripts/runtime/system_demo.py
```

### 5.5 Monitoring Stack

```bash
cd monitoring-stack
docker-compose up -d
```

---

## 6. Coding Conventions (编码规范)

以 `AGENTS.md` 为权威，这里强调最常踩坑：

- **导入**: 使用 `from src.*` 的绝对导入；标准库/三方/本地分组
- **格式化**: Black；行长默认 120
- **类型**: 函数参数/返回值加类型；必要时用 Pydantic model
- **异常**: 捕获具体异常；日志带上下文；外部调用考虑重试

---

## 7. Documentation Workflow (文档工作流)

新增/更新文档时：

- **放置位置**: `docs/{guides,api,architecture,operations,testing,reports,archive}/`
- **命名**: 英文 `kebab-case.md`（小写+连字符）
- **更新索引**: `python scripts/tools/docs_indexer.py --categories`

严禁：

- 将正式文档放到 `/tmp`
- 在根目录堆放临时 `*.md`（除非是 `README.md`/`CLAUDE.md`/`CHANGELOG.md` 等约定文件）

相关指南：

- `docs/guides/DOCUMENTATION_WORKFLOW_GUIDE.md`
- `docs/standards/FILE_ORGANIZATION_RULES.md`

---

## 8. Data Source Management Tools (数据源管理工具)

定位：只负责“端点注册/配置/测试/监控/搜索”，不负责真实业务拉取与存储。

- 注册表: `config/data_sources_registry.yaml`
- CLI 测试工具: `scripts/tools/manual_data_source_tester.py`
- 后端 API: `web/backend/app/api/data_source_registry.py`

强制指引（新增数据源/新 API 必读）：

- `docs/guides/NEW_API_SOURCE_INTEGRATION_GUIDE.md`

---

## 9. TypeScript Fix Policy (TypeScript 修复规范)

当任务是“修 TypeScript 报错”，遵循三原则：

- **最小修改**: 只修类型，不改业务逻辑
- **显式优于隐式**: 明确返回类型/断言，避免无意义的 `any`
- **从源头修复**: 需要 mock 时建立 mock 模块，不要在业务里硬编码临时数据

参考文档：

- `docs/reports/TYPESCRIPT_FIX_BEST_PRACTICES.md`
- `docs/reports/TYPESCRIPT_TECHNICAL_DEBT_MANAGEMENT.md`
- `docs/reports/TYPESCRIPT_TECHNICAL_DEBTS.md`
- `docs/reports/TYPESCRIPT_FIX_REFLECTION.md`

---

## 10. Bug Reporting (BUG 登记)

当用户要求“登记BUG/记BUG”，按模板生成报告并更新索引：

- 模板: `docs/standards/bug-report-template.json`
- 输出目录: `docs/quality/bugs/`
- 经验教训索引: `docs/guides/BUG_LESSONS_LEARNED.md`

---

## 11. Multi-CLI / Worktree (多 CLI 协作)

使用 Git worktree 多 CLI 并行时，遵循“主 CLI 指导、worker CLI 执行”。

- `docs/guides/MULTI_CLI_WORKTREE_MANAGEMENT.md`
- `docs/guides/GIT_WORKTREE_MAIN_CLI_MANUAL.md`

---

## 12. Security & Secrets (安全与密钥)

- `.env` 仅用于本地；不要提交
- 新增环境变量时同步更新 `.env.example`（如仓库约定存在）
- 遇到鉴权/密钥相关变更，优先使用仓库已有脚本与文档（例如 JWT 相关脚本在 `scripts/`）

---

## 13. Maintenance Notes (维护信息)

- 本文件仅包含“AI 在本仓库如何工作”的要点；过长的教程应迁移到 `docs/` 并在此处链接。
- 旧版 CLAUDE.md 已备份到: `docs/archive/CLAUDE.md.2026-02-01.md`

**Last updated**: 2026-02-01
