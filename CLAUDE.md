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

> **⚠️ 核心约束 (Critical Requirement)**:
> 在执行任何代码修改或架构设计前，**必须**首先阅读并遵守 [architecture/STANDARDS.md](architecture/STANDARDS.md) 定义的工程红线。任何违反准则（如硬编码 App.vue、单例未初始化等）的操作将被视为无效交付。

## 1. 统一规则引用 (Canonical Rules)

为避免多文档分叉，以下共享规则统一以 [architecture/STANDARDS.md](architecture/STANDARDS.md) 为准：

- `方案先行准则 (Proposal-First Rule)`：见“零、统一治理与审批门禁”
- `推荐开发流程：六步走战略`：见“一、推荐开发流程：六步走战略”
- `Docker 一等公民原则`：见“二、技术工程红线 -> 3. 环境一致性”

本文件仅保留 Claude 使用方式、协作流程和排障细节，不再重复上述规则正文。

---

## 2. 项目基础认知 (Project Basic Cognition)

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

### 1.1.1 项目定位与设计边界约束 (Project Positioning and Design Boundary Constraints)

**核心定位**：MyStocks 是面向**个人/小型量化投资者**的量化交易分析和管理工具，**不是**面向大型企业的多用户平台。

**部署模式**：
- 个体本地化部署为主（单用户或小团队）
- 非云服务/SaaS 模式
- 无需高并发、多租户、分布式锁等企业级特性

**设计边界约束（严格执行）**：

| ✅ 适合本系统 | ❌ 不适合本系统（过度设计） |
|-------------|--------------------------|
| 单用户/小团队认证 | 复杂的 RBAC 权限系统 |
| 基础的安全防护 | 企业级安全审计日志 |
| 简单的本地缓存 | 分布式缓存一致性 |
| 直接数据库连接 | 连接池复杂治理 |
| 功能性 API | API 网关/限流熔断 |
| 本地文件存储 | 分布式文件系统 |
| 简单定时任务 | 分布式任务调度 |

**新增功能评估原则**：
1. **必要性**：是否解决实际用户痛点？
2. **简洁性**：能否用更简单的方式实现？
3. **维护成本**：是否增加测试/运维负担？
4. **适用性**：是否符合"个人本地化部署"场景？

**违反此约束的后果**：
- 增加代码复杂度和维护成本
- 引入不必要的依赖和测试负担
- 偏离项目核心目标

### Git 分支检测与工作流程 (Git Branch Detection and Workflow)

**关键要求**: 根据当前 git 分支确定工作流程。

```bash
# 检测当前分支（在当前仓库路径执行）
git branch --show-current
# 或
git rev-parse --abbrev-ref HEAD
```

**工作流程规则**:
- **如果分支为 `main`**: 遵循 Main CLI 职责
  - 协调角色：使用 `.FILE_OWNERSHIP` 分配任务
  - 监控 Worker 进度：查阅 `TASK.md` 和 `TASK-REPORT.md`（Worker CLI 工件）
  - 不直接在 Worker 任务文件中报告任务
  - 参考：`.multi-cli-tasks/guides/MULTI_CLI_WORKTREE_MANAGEMENT.md`

- **如果分支为非 main**（worktree）：遵循 Worker CLI 工作流程
  - 使用 worktree 根目录下的 `TASK.md` + `TASK-REPORT.md`（+ `TASK-*-REPORT.md`）
  - 报告进度和完成状态
  - 参考：`.multi-cli-tasks/guides/GIT_WORKTREE_MAIN_CLI_MANUAL.md`

**强制声明（必须遵守）**:
- 使用 Git Worktree 进行 multi-cli 协作时，必须遵守 `.multi-cli-tasks/guides/MULTI_CLI_WORKTREE_MANAGEMENT.md`（v3.2）及其配套指南。
- `main` 只负责协调与验收，不直接承载功能开发提交。
- 新功能统一在 `worktree/dev-*` 分支开发，并以 PR 方式合并到 `main`。
- 每个 PR 必须提供：变更范围、验证命令与结果、风险与回滚说明。
- 合并前必须通过三道门禁：质量门（TS/Python/tests）、安全门（secrets/audit/SAST）、审查门（code review）。
- `main` 仅保留“干净、可复现、可回滚”的可发布状态。
- 任何偏离上述分支策略、PR 要件、门禁规则与验证流程的交付，均视为不合规。

---

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
cd web/frontend && npx stylelint "src/**/*.{vue,scss,css}"   # CSS/SCSS 零错误检查
```

#### 2.2.2 运行服务与演示

```bash
# 端口来自 .env（固定口径）
# 默认（ArtDeco / 现有系统）：
# FRONTEND_PORT=3020
# FRONTEND_BACKUP_PORT=3021
# BACKEND_PORT=8020
# BACKEND_BACKUP_PORT=8021
#
# Quant Matrix Pro 专用端口：
# QM_FRONTEND_PORT=3030
# QM_BACKEND_PORT=8030

cd web/backend
uvicorn app.main:app --host 0.0.0.0 --port "${BACKEND_PORT}" --reload

cd web/frontend
npm install
npm run dev -- --port "${FRONTEND_PORT}"

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

0. **环境稳定性检查**: 开发前在 `~/.codex/config.toml` 中禁用不必要的 MCP 服务器（如后端任务禁用浏览器工具），防止工具集过大导致连接中断。
1. 读取 `AGENTS.md` 与相关 `docs/`，确认约束与现有实现
2. **实现前必须先做“现有能力盘点”**：优先检索 `src/`、`web/`、`config/` 与 `docs/` 是否已有可复用模块、接口、配置或页面逻辑；禁止在未检索复用路径前直接新建实现，避免重复造轮子与多头管理
3. 以最小修改完成需求，避免顺手重构
4. 运行必要的验证命令并记录结果
5. 汇总变更与下一步建议

### 3.1.0 主线治理链路（PR 强制）

以下链路用于确保“目标不跑偏、成果不沉没”，与 `architecture/STANDARDS.md` / `openspec/AGENTS.md` 联动执行：

1. 规范基线：`governance/mainline/spec/ai-development-mainline-governance-spec.md`
2. 任务卡模板：`governance/mainline/templates/ai-task-card.yaml`
3. 任务卡 Schema：`governance/mainline/schemas/ai-task-card.schema.json`
4. 本地门禁脚本：`governance/mainline/scripts/mainline_scope_gate.py`
5. CI 门禁工作流：`.github/workflows/mainline-governance.yml`
6. PR 模板入口：`.github/pull_request_template.md`
7. 报告产物：`governance/mainline/reports/mainline-governance-report.json`

执行要求：
- 每个 PR 必须提供 `governance/mainline/task-cards/pr-<PR号>.yaml`
- `feature` 类型必须满足 `openspec.change_id` 非空且 `openspec.approval_status=approved`
- 门禁失败不得绕过，必须修复根因后再合并

遇到"计划/提案/架构调整"类需求时，先打开 `openspec/AGENTS.md`。

#### 3.1.1 推荐开发流程：六步走战略

> 共享正文已统一至 [architecture/STANDARDS.md](architecture/STANDARDS.md)：
> - “零、统一治理与审批门禁”（含 `Proposal-First Rule`）
> - “一、推荐开发流程：六步走战略”
> - “二、技术工程红线 -> 3. 环境一致性”（Docker/PM2 一等公民）

#### Skill 手动加载

当自动激活未触发时，可使用 `/skill` 命令手动加载技能包：

```
/skill vue3          # 加载 Vue 3 官方指南与 API 参考（全局 skill）
```

全局 skill 位置：`/root/.claude/skills/`，项目级 skill 位置：`.claude/skills/`。

### 3.2 编码与协作规范 (Coding and Collaboration Specifications)

#### 编码与架构要点

- 使用 `from src.*` 的绝对导入，按标准库/三方/本地分组
- 函数参数与返回值使用类型提示；必要时使用 Pydantic
- 数据读写通过 `MyStocksUnifiedManager` 按分类路由
- 记录上下文的异常日志，外部调用考虑重试
- 端口配置必须通过 `.env` 注入，禁止在运行时代码中硬编码端口号；固定口径为：
  - 默认（ArtDeco / 现有系统）前端：`3020`（备用 `3021`）
  - 默认（ArtDeco / 现有系统）后端：`8020`（备用 `8021`）
  - Quant Matrix Pro 专用前端：`3030`（`QM_FRONTEND_PORT`）
  - Quant Matrix Pro 专用后端：`8030`（`QM_BACKEND_PORT`）

#### 前端 TypeScript / Vue 补充规范

- 适用范围：仅适用于 `web/frontend` 下的 TypeScript / Vue / JavaScript 代码；后端与 Python 代码继续遵循本节其他全局规范
- 渐进治理：以下规则默认适用于新增代码与本次修改代码，不要求一次性重写历史文件；如与技术债基线冲突，按基线治理流程推进

##### Import Convention

- 使用 ES modules；本地模块导入应显式写出扩展名（如 `.js`、`.ts`、`.vue`），第三方包导入保持包名形式
- 导入顺序统一为：第三方包 → 别名/本地模块 → 样式文件；同组内保持稳定排序

##### Function Patterns

- 顶层纯工具函数、服务函数优先使用 `function` 声明，便于提升可读性、调试栈与声明提升语义
- 回调函数、内联函数、短生命周期闭包优先使用箭头函数
- `defineStore`、composables、工厂函数等依赖闭包或框架约定的场景，允许继续使用 `const xxx = () =>`

##### Type Annotations

- `api/`、`services/`、`utils/` 中新增或修改的导出函数必须显式标注返回类型；复杂 composables 也应补充返回类型或返回接口
- 优先使用显式类型、接口、泛型、联合类型或 `unknown`，禁止在业务代码中新增无说明的裸 `any`
- 自动生成文件、类型声明文件、兼容层代码、测试代码可按实际情况豁免，但应尽量缩小 `any` 的影响范围并说明原因

#### 清理 / 删除判定标准（强制）

- **“未引用 / 未使用” 不等于“可删除”**。禁止仅凭静态搜索结果、编辑器提示、lint 报警或“当前文件内未使用”就直接删除文件、模块、组件、函数、测试、配置或导入。
- 在执行任何清理、删除、裁剪前，必须同时完成两类判定：
  1. **代码路径判定**：核查其是否仍被路由、菜单、注册表、动态导入、构建脚本、样式副作用、兼容分支、特性开关、运行时字符串映射或文档约定使用。
  2. **功能树判定**：核查其在当前项目功能树中的归属与状态，并明确标记为：`有效`、`失效但兼容保留`、`实验/灰度`、`重复冗余`、`待判定` 之一。
- 只有当 **代码路径已证明可安全移除**，且 **功能树状态明确为“重复冗余”或“正式下线”** 时，才允许删除。
- 若该对象仍承载有效功能、兼容职责、实验用途，或功能状态无法确认，则默认 **不删除**；优先采用补文档、补注释、登记技术债、标记弃用、或在任务汇报中说明保留原因。
- 对 `unused import`、未使用局部变量、未使用解构项等低层级清理，也必须确认其不承担 **副作用初始化、样式加载、类型约束、自动注册、polyfill、扩展占位** 等隐含职责；无法证明时不得删除。
- 涉及清理 / 删除的提交、`TASK-REPORT` 或最终汇报，应至少说明：**清理对象、所属功能节点、状态判定、删除依据、保留原因（如适用）**。

#### 文档与维护工作流

- 文档放在 `docs/{guides,api,architecture,operations,testing,reports,archive}/`，命名使用 `kebab-case`
- 前端变更卫生 / 微提交规范：`docs/guides/frontend/frontend-change-hygiene-and-micro-commit-guide.md`
- 运行索引更新：`python scripts/tools/docs_indexer.py --categories`
- 技术债治理执行章程：`docs/standards/technical-debt-governance-charter-v1.md`（门禁、基线、豁免与周报模板）
- TypeScript 修复遵循三原则，并参考：
  - `docs/reports/TYPESCRIPT_FIX_BEST_PRACTICES.md`
  - `docs/reports/TYPESCRIPT_TECHNICAL_DEBT_MANAGEMENT.md`
  - `docs/reports/TYPESCRIPT_TECHNICAL_DEBTS.md`
  - `docs/reports/TYPESCRIPT_FIX_REFLECTION.md`
- **CSS/SCSS 开发必须遵循 `docs/guides/frontend/css-scss-development-guide.md`（强制执行）**：
  - **禁止内联样式**：Vue 组件 `<style>` 块仅允许 `@import` 引用外部 SCSS 文件，不得直接编写 CSS
  - **样式文件位置**：组件样式放在同级 `styles/` 目录，全局样式放在 `src/styles/`
  - **组件体积红线**：单个 `.vue` 文件不得超过 800 行，超过时必须提取 CSS 到独立 SCSS 或拆分 composables
  - **提交前零错误**：`cd web/frontend && npx stylelint "src/**/*.{vue,scss,css}"` 必须通过
  - **禁止废弃属性**（如 `clip`）、禁止 shorthand 覆盖冲突、禁止重复选择器
- **代码清单扫描工具（强制执行）**:
  - 位置：`src/monitoring/code_inventory/`
  - 用途：扫描代码行数、检测Mock数据使用、生成Markdown报告
  - 运行命令：`python -m src.monitoring.code_inventory.cli --no-validation --scan-dirs src scripts web/backend/app`
  - **定期扫描要求**：每月至少执行一次扫描，检查代码复杂度趋势和Mock使用情况
  - 报告位置：`reports/code_inventory_report_*.md`
  - 发现问题处理：如发现超过阈值文件或异常Mock使用，需在相应模块下创建治理任务
- BUG 登记按模板 `docs/standards/bug-report-template.json`，输出到 `docs/reports/quality/bugs/` 并更新 `docs/reports/quality/BUG_LESSONS_LEARNED.md`
- 多 CLI/Worktree 协作核心索引 (必读):
  - **`.multi-cli-tasks/guides/MULTI_CLI_WORKTREE_MANAGEMENT.md` (总手册，强制遵守)**
  - 链接文档：
    - `.multi-cli-tasks/guides/MAIN_CLI_WORKFLOW.md` (主 CLI 规范)
    - `.multi-cli-tasks/guides/WORKER_CLI_GUIDE.md` (Worker CLI 规范)
    - `.multi-cli-tasks/guides/CONFLICT_PREVENTION.md` (冲突预防)
- **2026Q1 物理布局与治理指引**:
  - **Zero-Root-Config**: 禁止在根目录新增工具配置，所有配置必须入库 `config/` 对应子目录。
    - **例外: `.gitleaksignore`**: gitleaks CLI（含 `gitleaks-action@v2`）硬编码 `.gitleaksignore` 必须位于仓库根目录，不支持自定义路径。该文件为本规则的**合法根目录例外**，仅用于记录已轮换/已失效密钥的历史 finding 抑制（见 commit `462dcf5c2` 处理记录）。新增条目必须附 `# commitSHA — 描述` 注释说明背景。
  - **Logic Gravity**: 业务逻辑下沉 `src/`，根目录 `.py` 文件仅作为 Re-export 外壳。
  - **API Standardization**: 所有新 API 必须通过 `web/backend/app/api/VERSION_MAPPING.py` 注册，严禁在 `main.py` 中硬编码路由前缀。

### 3.3 Claude 问题排查指南 (Claude Troubleshooting Guide)

- 测试失败：先运行 `AGENTS.md` 中对应命令，确认失败输出再修复
- 导入问题：检查是否使用 `from src.*` 与正确的 `__init__.py` 导出
- CORS 问题：检查 `web/backend/app/core/config.py` 的端口白名单
- 新数据源/新 API：先读 `docs/guides/NEW_API_SOURCE_INTEGRATION_GUIDE.md`
- **Hooks 相关**：当用户说"检查hooks"或"检查*hooks"时，必须先查阅 `/opt/mydoc/Anthropic/Claude-code/hooks-guide.md` 与 `/opt/mydoc/Anthropic/Claude-code/hooks.md` 了解 Claude Code hooks 的配置、事件类型、安全注意事项与调试方法

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
- 声称"已修复/已通过"前必须有可复现的命令输出
- 保持最小变更，不做未请求的重构或回滚用户改动
- Web 仅桌面端支持，避免加入移动端响应式样式

### 4.3 Claude 行为纪律 (Claude Behavioral Discipline)

**问题处理原则：解决问题，不掩盖问题。**

- 遇到质量门（quality gate）、测试失败、错误阈值等阻塞时，必须分析根因并提出修复方案，禁止通过调整阈值、禁用检查等方式绕过
- 对于任何配置变更、阈值调整、规则修改，必须先向用户报告原因和方案，获得明确批准后才能动手修改
- 禁止擅自做决定：涉及项目规范、配置、流程的改动，一律先报告、再审批、后执行

**TS/代码错误分析原则：**

- 遇到大量 TypeScript 或代码错误时，必须先分析错误来源：
  - 若为 AI 写代码时顺手生成的错误 → 直接修复源文件
  - 若为自动生成代码（如类型生成器、代码生成脚本）产生的错误 → 追溯到生成器/模板源头修复
- 禁止不分析来源就批量修改或忽略错误

---

## 5. 大文件拆分规则与例外 (Large File Splitting Rules and Exceptions)

- 规则：`architecture/standards/large_file_splitting_principles.md`（Python >800行、Vue >500行、TS >500行、测试 >1000行强制拆分）
- 例外：`reports/compliance/exceptions/`（19个边缘超标 Python 文件 + 37个单块 TS 文件已记录）
- 工具与基线：`scripts/dev/tools/`（6个自动化拆分工具）、`reports/plans/inventory/*.tsv`（基线清单）

---

**Last updated**: 2026-02-15

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **mystocks_spec** (91043 symbols, 224595 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `gitnexus analyze` in terminal first.

> If GitNexus behaves differently across machines or CI, run `gitnexus doctor --json` to inspect `native-runtime`, `language-support`, and host configuration checks.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Dirty Worktree Rule

- In a dirty worktree, `gitnexus_detect_changes({scope: "unstaged"})` reflects the whole worktree and MUST NOT be used as the risk verdict for the current micro-batch.
- Stage the intended batch first with `git add <paths>`, then run `gitnexus_detect_changes({scope: "staged"})` for the precise pre-commit scope check.
- If no files are staged yet, report that staged scope is empty instead of falling back to `unstaged`.

## When Debugging

1. `gitnexus_query({query: "<error or symptom>"})` — find execution flows related to the issue
2. `gitnexus_context({name: "<suspect function>"})` — see all callers, callees, and process participation
3. `READ gitnexus://repo/mystocks_spec/process/{processName}` — trace the full execution flow step by step
4. For regressions: `gitnexus_detect_changes({scope: "compare", base_ref: "main"})` — see what your branch changed

## When Refactoring

- **Renaming**: MUST use `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` first. Review the preview — graph edits are safe, text_search edits need manual review. Then run with `dry_run: false`.
- **Extracting/Splitting**: MUST run `gitnexus_context({name: "target"})` to see all incoming/outgoing refs, then `gitnexus_impact({target: "target", direction: "upstream"})` to find all external callers before moving code.
- After any refactor: run `gitnexus_detect_changes({scope: "all"})` to verify only expected files changed.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Tools Quick Reference

| Tool | When to use | Command |
|------|-------------|---------|
| `query` | Find code by concept | `gitnexus_query({query: "auth validation"})` |
| `context` | 360-degree view of one symbol | `gitnexus_context({name: "validateUser"})` |
| `impact` | Blast radius before editing | `gitnexus_impact({target: "X", direction: "upstream"})` |
| `detect_changes` | Pre-commit scope check | `gitnexus_detect_changes({scope: "staged"})` |
| `rename` | Safe multi-file rename | `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` |
| `cypher` | Custom graph queries | `gitnexus_cypher({query: "MATCH ..."})` |

## Impact Risk Levels

| Depth | Meaning | Action |
|-------|---------|--------|
| d=1 | WILL BREAK — direct callers/importers | MUST update these |
| d=2 | LIKELY AFFECTED — indirect deps | Should test |
| d=3 | MAY NEED TESTING — transitive | Test if critical path |

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/mystocks_spec/context` | Codebase overview, check index freshness |
| `gitnexus://repo/mystocks_spec/clusters` | All functional areas |
| `gitnexus://repo/mystocks_spec/processes` | All execution flows |
| `gitnexus://repo/mystocks_spec/process/{name}` | Step-by-step execution trace |

## Self-Check Before Finishing

Before completing any code modification task, verify:
1. `gitnexus_impact` was run for all modified symbols
2. No HIGH/CRITICAL risk warnings were ignored
3. `gitnexus_detect_changes()` confirms changes match expected scope
4. All d=1 (WILL BREAK) dependents were updated

## Keeping the Index Fresh

After committing code changes, the GitNexus index becomes stale. Re-run analyze to update it:

```bash
gitnexus analyze
```

If you have modified the local GitNexus source code under `/opt/claude/GitNexus/gitnexus/src`, rebuild first so the CLI picks up the updated `dist` files:

```bash
cd /opt/claude/GitNexus/gitnexus
npm run build
gitnexus analyze
```

Use plain `gitnexus analyze` when you want the fastest refresh and exact symbol, file, or keyword search is enough.

Graph tools, BM25/FTS search, impact analysis, and context lookups still work without embeddings.

Use `gitnexus analyze --embeddings` when natural-language, concept, or fuzzy code search matters.

This enables hybrid retrieval (`BM25 + semantic + RRF`) but takes longer and requires an embedding provider such as Ollama or Hugging Face.

During `gitnexus analyze`, GitNexus automatically detects and stops local `gitnexus mcp` processes that are holding the target repo's `.gitnexus/kuzu` file open. This avoids the common KuzuDB lock conflict when you have multiple CLI or editor sessions open.

Use `gitnexus doctor --json` when you need to verify whether optional grammars such as Kotlin / Swift are actually available in the current environment.

If the index previously included embeddings, preserve them by adding `--embeddings`:

```bash
gitnexus analyze --embeddings
```

To check whether embeddings exist, inspect `.gitnexus/meta.json` — the `stats.embeddings` field shows the count (0 means no embeddings). **Running analyze without `--embeddings` will delete any previously generated embeddings.**

If embedding generation is enabled, these environment variables control the provider and runtime behavior:

```bash
# Raise the CLI safety limit for large repos.
# Start with 64 on a local Ollama GPU setup; use 32 as a conservative fallback.
GITNEXUS_EMBEDDING_NODE_LIMIT=90000
GITNEXUS_EMBEDDING_BATCH_SIZE=64

# Use a Hugging Face mirror / custom endpoint
HF_ENDPOINT=https://hf-mirror.com
# or
GITNEXUS_HF_REMOTE_HOST=https://hf-mirror.com

# Persist downloaded model files
GITNEXUS_HF_CACHE_DIR=/path/to/hf-cache

# Use a predownloaded local Hugging Face model only
GITNEXUS_HF_LOCAL_MODEL_PATH=/path/to/local-models
GITNEXUS_HF_LOCAL_ONLY=1

# Use Ollama instead of Hugging Face for both indexing and query embeddings
GITNEXUS_EMBEDDING_PROVIDER=ollama
GITNEXUS_OLLAMA_BASE_URL=http://localhost:11434
GITNEXUS_OLLAMA_MODEL=qwen3-embedding:0.6b
```

Recommended Ollama example:

```bash
GITNEXUS_EMBEDDING_PROVIDER=ollama \
GITNEXUS_OLLAMA_BASE_URL=http://localhost:11434 \
GITNEXUS_OLLAMA_MODEL=qwen3-embedding:0.6b \
GITNEXUS_EMBEDDING_NODE_LIMIT=90000 \
GITNEXUS_EMBEDDING_BATCH_SIZE=64 \
gitnexus analyze --embeddings
```

Use `--force` only for intentional full rebuilds or corrupted indexes.

The same settings can also be stored in `~/.gitnexus/config.json`:

```json
{
  "embeddings": {
    "provider": "ollama",
    "ollamaBaseUrl": "http://localhost:11434",
    "ollamaModel": "qwen3-embedding:0.6b",
    "nodeLimit": 90000,
    "batchSize": 64
  }
}
```

Priority is: environment variables > `~/.gitnexus/config.json` > built-in defaults.

You can inspect or update this without editing JSON manually:

```bash
gitnexus config embeddings show
gitnexus config embeddings set --provider ollama --ollama-base-url http://localhost:11434 --ollama-model qwen3-embedding:0.6b --node-limit 90000 --batch-size 64
gitnexus config embeddings clear
```

> Claude Code users: A PostToolUse hook handles this automatically after `git commit` and `git merge`.

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
