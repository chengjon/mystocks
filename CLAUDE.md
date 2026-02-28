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
  - 参考：`docs/guides/MULTI_CLI_WORKTREE_MANAGEMENT.md`

- **如果分支为非 main**（worktree）：遵循 Worker CLI 工作流程
  - 使用 worktree 根目录下的 `TASK.md` + `TASK-REPORT.md`（+ `TASK-*-REPORT.md`）
  - 报告进度和完成状态
  - 参考：`docs/guides/GIT_WORKTREE_MAIN_CLI_MANUAL.md`

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

0. **环境稳定性检查**: 开发前在 `~/.codex/config.toml` 中禁用不必要的 MCP 服务器（如后端任务禁用浏览器工具），防止工具集过大导致连接中断。
1. 读取 `AGENTS.md` 与相关 `docs/`，确认约束与现有实现
2. 以最小修改完成需求，避免顺手重构
3. 运行必要的验证命令并记录结果
4. 汇总变更与下一步建议

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

#### 文档与维护工作流

- 文档放在 `docs/{guides,api,architecture,operations,testing,reports,archive}/`，命名使用 `kebab-case`
- 运行索引更新：`python scripts/tools/docs_indexer.py --categories`
- TypeScript 修复遵循三原则，并参考：
  - `docs/reports/TYPESCRIPT_FIX_BEST_PRACTICES.md`
  - `docs/reports/TYPESCRIPT_TECHNICAL_DEBT_MANAGEMENT.md`
  - `docs/reports/TYPESCRIPT_TECHNICAL_DEBTS.md`
  - `docs/reports/TYPESCRIPT_FIX_REFLECTION.md`
- **CSS/SCSS 开发必须遵循 `docs/guides/css-scss-development-guide.md`（强制执行）**：
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
- BUG 登记按模板 `docs/standards/bug-report-template.json`，输出到 `docs/quality/bugs/` 并更新 `docs/guides/BUG_LESSONS_LEARNED.md`
- 多 CLI/Worktree 协作核心索引 (必读):
  - **`docs/guides/MULTI_CLI_WORKTREE_MANAGEMENT.md` (总手册)**
  - 链接文档：
    - `docs/guides/.multi-cli-tasks/MAIN_CLI_WORKFLOW_STANDARDS.md` (主 CLI 规范)
    - `docs/guides/.multi-cli-tasks/CLI_WORKFLOW_GUIDE.md` (Worker CLI 规范)
    - `docs/guides/.multi-cli-tasks/GIT_WORKTREE_COLLABORATION_CONFLICT_PREVENTION.md` (冲突预防)
- **2026Q1 物理布局与治理指引**:
  - **Zero-Root-Config**: 禁止在根目录新增工具配置，所有配置必须入库 `config/` 对应子目录。
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
