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

# 项目 Claude AI 集成指南 (Project Claude AI Integration Guide)

**本指南说明 MyStocks 中 Claude/OpenCode 的使用方式、开发约束与协作规范。它与 `AGENTS.md`、`docs/` 文档共同构成 AI 工作手册。**

## 1. 项目基础认知：Claude AI 集成总览 (Project Basic Cognition: Claude AI Integration Overview)

### 1.1 项目定位与Claude核心功能 (Project Positioning and Core Claude Functions)

MyStocks 使用 Claude/OpenCode 作为交互式开发助手，协助完成代码修改、验证与文档维护。Claude 在本仓库的核心工作包括：

- 快速定位代码与文档，理解现有实现
- 执行最小变更，保持与仓库规范一致
- 运行必要的验证命令并汇报结果
- 更新文档与索引，保持信息一致

权威来源（冲突时以此为准）：

- `AGENTS.md`：命令、风格、目录结构等硬性规则
- `openspec/AGENTS.md`：计划/提案流程与变更规范
- `docs/`：详细指南与参考文档

平台支持策略（重要）：

- 仅支持桌面端 Web（最小分辨率 1280x720）
- 禁止移动端/平板适配，禁止添加 `@media (max-width: ...)` 等响应式规则

### 1.2 技术栈与 Claude 依赖 (Technology Stack and Claude Dependencies)

核心技术栈：

- Python 3.12+ / FastAPI 0.114+ / Vue 3.4+
- TDengine 3.3+（高频时序）/ PostgreSQL 17+ + TimescaleDB（其他数据）
- GPU 加速可选：`gpu_api_system/` 与 `src/gpu/`

仓库速查：

- `src/`：Python 核心业务代码
- `web/backend/`：FastAPI 后端
- `web/frontend/`：Vue 3 前端
- `config/`：配置文件
- `scripts/`：可执行脚本
- `docs/`：项目文档
- `monitoring-stack/`：监控栈

Claude 依赖说明：

- 本仓库不包含 Claude API/SDK 直接集成（N/A）。
- 如需引入 Claude 服务端调用，视为架构变更，需先走 OpenSpec 流程。

### 1.3 Claude 相关版本与更新记录 (Claude-related Version and Update Records)

- 2026-02-01：按模板重写 CLAUDE.md，历史版本已归档到 `docs/archive/CLAUDE.md.2026-02-01.md` 与 `docs/archive/CLAUDE.md.2026-02-01.v2.md`

---

## 2. Claude 集成开发与高级配置 (Claude Integration Development and Advanced Configuration)

### 2.1 Claude 相关环境搭建 (Claude-related Environment Setup)

- 本仓库默认不需要 Claude API Key/SDK 配置。
- 本地环境变量与数据库配置参见 `docs/standards/LOCAL_ENV_SETUP.md`。
- 双数据库连接由环境变量驱动（TDengine + PostgreSQL），监控配置在 `monitoring-stack/`。

### 2.2 核心 Claude 使用示例 (Core Claude Usage Examples)

#### 2.2.1 常用质量检查

```bash
pytest
ruff check src/
black --check .
mypy src/ --no-error-summary
```

#### 2.2.2 运行服务与演示

```bash
cd web/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

cd web/frontend
npm install
npm run dev -- --port 3001

python -c "from unified_manager import MyStocksUnifiedManager; MyStocksUnifiedManager().initialize_system()"
```

### 2.3 Claude 相关配置说明 (Claude-related Configuration Description)

- 通用配置集中在 `config/`（例如 `config/data_sources_registry.yaml`）。
- 后端 CORS 配置在 `web/backend/app/core/config.py`。
- 监控与可观测性配置在 `monitoring-stack/`。
- 计划/提案与规范更新遵循 `openspec/AGENTS.md`。
- Claude API/SDK 配置：本仓库默认不使用（N/A）。

---

## 3. Claude 驱动的协作与维护 (Claude-driven Collaboration and Maintenance)

### 3.1 开发工作流指引 (Development Workflow Guidance)

本仓库没有固定的 QNEW/QPLAN 等快捷指令，建议流程：

1. 读取 `AGENTS.md` 与相关 `docs/`，确认约束与现有实现
2. 以最小修改完成需求，避免顺手重构
3. 运行必要的验证命令并记录结果
4. 汇总变更与下一步建议

遇到“计划/提案/架构调整”类需求时，先打开 `openspec/AGENTS.md`。

### 3.2 编码与协作规范 (Coding and Collaboration Specifications)

#### 编码与架构要点

- 使用 `from src.*` 的绝对导入，按标准库/三方/本地分组
- 函数参数与返回值使用类型提示；必要时使用 Pydantic
- 数据读写通过 `MyStocksUnifiedManager` 按分类路由
- 记录上下文的异常日志，外部调用考虑重试

#### 文档与维护工作流

- 文档放在 `docs/{guides,api,architecture,operations,testing,reports,archive}/`，命名使用 `kebab-case`
- 运行索引更新：`python scripts/tools/docs_indexer.py --categories`
- TypeScript 修复遵循三原则，并参考：
  - `docs/reports/TYPESCRIPT_FIX_BEST_PRACTICES.md`
  - `docs/reports/TYPESCRIPT_TECHNICAL_DEBT_MANAGEMENT.md`
  - `docs/reports/TYPESCRIPT_TECHNICAL_DEBTS.md`
  - `docs/reports/TYPESCRIPT_FIX_REFLECTION.md`
- BUG 登记按模板 `docs/standards/bug-report-template.json`，输出到 `docs/quality/bugs/` 并更新 `docs/guides/BUG_LESSONS_LEARNED.md`
- 多 CLI/Worktree 协作遵循：
  - `docs/guides/MULTI_CLI_WORKTREE_MANAGEMENT.md`
  - `docs/guides/GIT_WORKTREE_MAIN_CLI_MANUAL.md`

### 3.3 Claude 问题排查指南 (Claude Troubleshooting Guide)

- 测试失败：先运行 `AGENTS.md` 中对应命令，确认失败输出再修复
- 导入问题：检查是否使用 `from src.*` 与正确的 `__init__.py` 导出
- CORS 问题：检查 `web/backend/app/core/config.py` 的端口白名单
- 新数据源/新 API：先读 `docs/guides/NEW_API_SOURCE_INTEGRATION_GUIDE.md`

### 3.4 Claude 相关扩展与二次开发指引 (Claude-related Extension and Secondary Development Guide)

- 新增数据源或 API 接口必须遵循 `docs/guides/NEW_API_SOURCE_INTEGRATION_GUIDE.md`
- 架构级变更、性能/安全大改动须走 OpenSpec（`openspec/AGENTS.md`）
- GPU 相关工作参照 `gpu_api_system/` 与 `src/gpu/`
- 监控扩展遵循 `monitoring-stack/` 现有结构与配置

---

## 4. Claude 使用合规与风险 (Claude Usage Compliance and Risks)

### 4.1 Claude API 使用权限与合规要求 (Claude API Usage Permissions and Compliance Requirements)

- 本仓库不直接集成 Claude API/SDK；若引入需先走 OpenSpec 变更流程
- `.env` 仅用于本地，禁止提交；新增环境变量需同步 `.env.example`（如存在）
- 正式文件不得放入 `/tmp`，应按 `docs/`/`scripts/`/`config/` 归档

### 4.2 Claude 相关风险提示 (Claude-related Risk Warnings)

- Claude 输出可能不准确，所有关键修改需通过实际命令验证
- 声称“已修复/已通过”前必须有可复现的命令输出
- 保持最小变更，不做未请求的重构或回滚用户改动
- Web 仅桌面端支持，避免加入移动端响应式样式

---

**Last updated**: 2026-02-01
