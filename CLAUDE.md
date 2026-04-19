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

# MyStocks 项目 Claude 集成指南

> **权威来源声明**: 本文件是 Claude 在本仓库的执行入口。仓库级共享规则以 [architecture/STANDARDS.md](architecture/STANDARDS.md) 为唯一事实来源；涉及 OpenSpec 提案时遵循 `openspec/AGENTS.md`。若本文件与 STANDARDS.md 冲突，以 STANDARDS.md 为准。

> **核心约束**: 执行任何代码修改或架构设计前，**必须**首先阅读并遵守 [architecture/STANDARDS.md](architecture/STANDARDS.md) 定义的工程红线。

---

## 1. 项目定位与边界

**定位**: MyStocks 是面向个人/小型量化投资者的量化交易分析和管理工具，非企业级多用户平台。

**部署模式**: 个体本地化部署（单用户/小团队），非 SaaS。

**设计边界约束（严格执行）**:

| 适合本系统 | 不适合（过度设计） |
|-----------|-----------------|
| 单用户/小团队认证 | 复杂 RBAC 权限系统 |
| 基础安全防护 | 企业级安全审计日志 |
| 简单本地缓存 | 分布式缓存一致性 |
| 直接数据库连接 | 连接池复杂治理 |
| 功能性 API | API 网关/限流熔断 |
| 本地文件存储 | 分布式文件系统 |

**新增功能评估**: 必要性 → 简洁性 → 维护成本 → 适用性（是否符合个人本地化部署场景）。

**平台支持**: 仅桌面端 Web（最小分辨率 1280x720），禁止移动端/平板适配和 `@media (max-width)` 响应式规则。

---

## 2. 技术栈与端口

| 层 | 技术 |
|---|------|
| 后端 | Python 3.12+ / FastAPI 0.114+ / SQLAlchemy / Pydantic |
| 前端 | Vue 3.4+ / TypeScript / Pinia / **ArtDeco 设计系统** |
| 时序库 | TDengine 3.3+ |
| 关系库 | PostgreSQL 17+ / TimescaleDB |
| GPU（可选） | RAPIDS (cuDF/cuML) |

**端口（必须通过 `.env` 注入，禁止硬编码）**:

| 服务 | 端口 | 备用 |
|------|------|------|
| 前端 | 3020 | 3021 |
| 后端 | 8020 | 8021 |
| QM 前端 | 3030 | — |
| QM 后端 | 8030 | — |

---

## 3. 项目结构速查

```
mystocks_spec/
├── src/                # Python 核心业务逻辑
├── web/backend/        # FastAPI 后端 (app/main.py 入口)
├── web/frontend/       # Vue 3 + ArtDeco 前端
├── config/             # 配置文件（Docker/Playwright/PM2）
├── architecture/       # 架构定义与域边界
├── docs/               # 文档库 (guides/api/reports)
├── scripts/            # 工具脚本
├── tests/              # 测试代码
└── openspec/           # OpenSpec 变更管理
```

---

## 4. 开发工作流

### 4.1 推荐流程

1. 读取 [STANDARDS.md](architecture/STANDARDS.md) 与相关 `docs/`，确认约束
2. **实现前先做"现有能力盘点"**: 检索 `src/`、`web/`、`config/`、`docs/` 是否已有可复用模块，禁止未检索就新建实现
3. 以最小修改完成需求，避免顺手重构
4. 运行验证命令并记录结果
5. 汇总变更与下一步建议

### 4.2 常用验证命令

```bash
# Python
pytest && ruff check src/ web/backend/app/ && black --check .

# 前端
cd web/frontend && npx stylelint "src/**/*.{vue,scss,css}"   # 零错误
npx vue-tsc --noEmit                                          # TS 类型检查

# 服务启动（端口来自 .env）
cd web/backend && uvicorn app.main:app --host 0.0.0.0 --port "${BACKEND_PORT:-8020}" --reload
cd web/frontend && npm run dev -- --port "${FRONTEND_PORT:-3020}"
```

### 4.3 主线治理链路（PR 强制）

每个 PR 必须通过三道门禁：质量门（TS/Python/tests）、安全门（secrets/audit/SAST）、审查门（code review）。

详细规范: `governance/mainline/spec/ai-development-mainline-governance-spec.md`

### 4.4 GSD 使用口径

- GSD 不再作为仓库写操作的强制入口
- 需要规划工件、阶段执行或跨会话状态同步时，可按需使用 `/gsd:*`
- 未走 GSD 时，仍必须遵守 `architecture/STANDARDS.md`、OpenSpec 与现有验证/汇报要求

---

## 5. Git 分支与协作

```bash
git branch --show-current   # 检测当前分支
```

- **`main` 分支**: 协调角色，使用 `.FILE_OWNERSHIP` 分配任务，监控 Worker 进度（`TASK.md` / `TASK-REPORT.md`）
- **非 `main` 分支（worktree）**: Worker 角色，使用 worktree 根目录下的 `TASK.md` + `TASK-REPORT.md`
- **强制**: 遵守 `.multi-cli-tasks/guides/MULTI_CLI_WORKTREE_MANAGEMENT.md`（v3.2）；`main` 不承载功能开发；新功能在 `worktree/dev-*` 分支开发并以 PR 合并

---

## 6. 编码规范（要点摘要）

> 完整规则见 [architecture/STANDARDS.md](architecture/STANDARDS.md)。以下仅为启动时高频引用的要点。

### Python

- 绝对导入 `from src.*`，按 stdlib → third-party → local 分组
- 函数参数与返回值使用类型提示，Pydantic 做数据验证
- 数据读写通过 `MyStocksUnifiedManager` 按分类路由
- 文件体积红线: Python 800 行、Vue/TS 500 行、测试 1000 行

### 前端 TypeScript / Vue

- ES modules；本地导入写扩展名（`.js`/`.ts`/`.vue`）；导入顺序: 第三方 → 本地 → 样式
- 顶层纯函数用 `function` 声明；回调用箭头函数
- `api/`、`services/`、`utils/` 导出函数必须标注返回类型；禁止裸 `any`
- **CSS/SCSS 强制规则**（详见 `docs/guides/frontend/css-scss-development-guide.md`）:
  - 禁止内联样式；组件样式在同级 `styles/` 目录
  - 提交前 `npx stylelint` 零错误
- Composable 协作定位: 1 个消费者 → `./composables/` 同目录共存；2+ 消费者 → `src/composables/`

### 迁移收口

- 统一以 [STANDARDS.md](architecture/STANDARDS.md) "三、迁移收口与技术债治理规则" 为唯一事实来源
- 处理 `*_new.py`、shim、平行目录、`.bak` 等临时文件时，必须回到 STANDARDS.md 执行
- 技术债治理细则: `docs/standards/technical-debt-governance-charter-v1.md`

---

## 7. 关键文档入口

| 领域 | 文档 |
|------|------|
| 工程红线 | [architecture/STANDARDS.md](architecture/STANDARDS.md) |
| 前端变更记录 | [docs/changes/frontend/FRONTEND_CHANGES.md](docs/changes/frontend/FRONTEND_CHANGES.md) |
| CSS/SCSS 开发指南 | [docs/guides/frontend/css-scss-development-guide.md](docs/guides/frontend/css-scss-development-guide.md) |
| 前端微提交规范 | [docs/guides/frontend/frontend-change-hygiene-and-micro-commit-guide.md](docs/guides/frontend/frontend-change-hygiene-and-micro-commit-guide.md) |
| 技术债治理章程 | [docs/standards/technical-debt-governance-charter-v1.md](docs/standards/technical-debt-governance-charter-v1.md) |
| TypeScript 修复实践 | [docs/reports/TYPESCRIPT_FIX_BEST_PRACTICES.md](docs/reports/TYPESCRIPT_FIX_BEST_PRACTICES.md) |
| Bug 经验库 | [docs/reports/quality/BUG_LESSONS_LEARNED.md](docs/reports/quality/BUG_LESSONS_LEARNED.md) |
| 新数据源集成指南 | [docs/guides/data-source/NEW_API_SOURCE_INTEGRATION_GUIDE.md](docs/guides/data-source/NEW_API_SOURCE_INTEGRATION_GUIDE.md) |
| Web Hooks 指南 | [docs/guides/hooks/web-dev-hooks-guide.md](docs/guides/hooks/web-dev-hooks-guide.md) |
| 多 CLI 协作手册 | [.multi-cli-tasks/guides/MULTI_CLI_WORKTREE_MANAGEMENT.md](.multi-cli-tasks/guides/MULTI_CLI_WORKTREE_MANAGEMENT.md) |
| OpenSpec 变更管理 | [openspec/AGENTS.md](openspec/AGENTS.md) |
| 代码清单扫描工具 | [src/monitoring/code_inventory/](src/monitoring/code_inventory/) |
| 大文件拆分规则 | [architecture/standards/large_file_splitting_principles.md](architecture/standards/large_file_splitting_principles.md) |

---

## 8. GitNexus 代码智能（要点）

> 详细 CLI 和配置参考见 `.claude/skills/gitnexus/` 目录。

- **编辑前**: 必须运行 `gitnexus_impact({target, direction: "upstream"})` 分析影响范围
- **提交前**: 必须运行 `gitnexus_detect_changes({scope: "staged"})` 确认变更范围
- **dirty worktree 规则**: `gitnexus_detect_changes({scope: "unstaged"})` 在 dirty worktree 中反映的是整个工作区，MUST NOT 作为当前微批次的风险结论；应先暂存目标文件，再用 `gitnexus_detect_changes({scope: "staged"})` 做精确检查
- **HIGH/CRITICAL 风险**: 必须向用户报告后再决定是否继续
- **重命名**: 必须使用 `gitnexus_rename`，禁止 find-and-replace
- **索引更新**: 代码提交后运行 `gitnexus analyze`（嵌入可选 `--embeddings`）

---

## 9. 行为纪律

**解决问题，不掩盖问题。**

- 质量门/测试失败/错误阈值阻塞时 → 分析根因并提出修复方案，禁止调阈值/禁用检查绕过
- 配置变更/阈值调整/规则修改 → 先报告原因和方案，获批准后再执行
- 涉及项目规范/配置/流程 → 一律先报告、再审批、后执行
- TS/代码错误 → 先分析来源（AI 生成 vs 代码生成器产物），再针对性修复
- 声称"已修复"前必须有可复现的命令输出
- 保持最小变更，不做未请求的重构

---

## 10. 问题排查速查

| 问题 | 检查点 |
|------|--------|
| 测试失败 | 先运行对应命令，确认失败输出再修复 |
| 导入问题 | 检查 `from src.*` 与 `__init__.py` 导出 |
| CORS | `web/backend/app/core/config.py` 端口白名单 |
| 新数据源/API | 先读 `docs/guides/data-source/NEW_API_SOURCE_INTEGRATION_GUIDE.md` |
| Hooks | 先查阅 `docs/guides/hooks/web-dev-hooks-guide.md`，再按需核对 `/opt/mydoc/Anthropic/Claude-code/hooks-guide.md` 与 `/opt/mydoc/Anthropic/Claude-code/hooks.md` |

---

## 11. Claude 依赖说明

- 本仓库不包含 Claude API/SDK 直接集成
- 如需引入 Claude 服务端调用，视为架构变更，需先走 OpenSpec 流程
- Claude Auto / Agent 自动 worklog 写入 `docs/reports/worklogs/claude-auto/`
- `.env` 仅用于本地，禁止提交；新增环境变量需同步 `.env.example`

---

**Last updated**: 2026-04-19
