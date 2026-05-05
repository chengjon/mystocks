# MyStocks

> **导航说明**:
> 本文件是导航页或索引页，不是当前仓库共享规则或实现状态的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及具体执行入口，再按职责分别参考根目录 `AGENTS.md` 与根目录 `CLAUDE.md`。

MyStocks 是一个面向 A 股量化研究、监控、分析与交易辅助的桌面端 Web 平台，采用 `Vue 3 + FastAPI + ArtDeco` 的前后端分离架构，并以功能树、测试门禁和文档真相源分层来管理持续演进。

> 平台约束：仅支持桌面端 Web，默认不为移动端或平板提供适配。

[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://python.org)
[![Vue](https://img.shields.io/badge/Vue-3.4%2B-brightgreen.svg)](https://vuejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.114%2B-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 快速导航

- [项目概览](#项目概览)
- [功能亮点](#功能亮点)
- [关键文档入口与真相源](#关键文档入口与真相源)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [开发流程与治理方法](#开发流程与治理方法)
- [测试与质量门禁](#测试与质量门禁)
- [部署与运行](#部署与运行)
- [配置说明](#配置说明)
- [项目结构](#项目结构)
- [ArtDeco 设计系统](#artdeco-设计系统)
- [Kronos AI 推理集成](#kronos-ai-推理集成)
- [FAQ 与健康检查](#faq-与健康检查)
- [贡献与标准](#贡献与标准)
- [历史背景](#历史背景)
- [许可证](#许可证)

## 项目概览

MyStocks 不是单一的行情页面或单一的后端接口集合，而是一套围绕量化交易工作流组织起来的工程系统：

- 以前后端分离方式提供市场数据、技术分析、策略管理、风险监控与系统治理能力。
- 以前端 ArtDeco 设计系统统一金融终端视觉语言，而不是继续扩散旧 UI 组件风格。
- 以 `FUNCTION_TREE` 路由业务能力，以 `STANDARDS` 管审批和工程红线，以测试门禁和 PR 证据闭环保证交付质量。
- 以“先路由、再下钻”的文档方法降低新人和 AI 在大型仓库中的搜索成本。

## 功能亮点

- 多数据源量化数据平台：整合 TDX、AKShare、EFinance、BaoStock 等多类市场与参考数据源。
- 桌面端交易分析终端：覆盖行情、技术分析、策略、风控、监控、自选股和系统管理等主要业务域。
- 双数据库分工：`TDengine` 承担高频时序数据，`PostgreSQL/TimescaleDB` 承担结构化与分析型数据。
- AkShare 市场门禁收口：以本地 `akshare` 同名函数为边界，提供 availability / repo-truth 校验与标准化审计报告。
- ArtDeco 金融设计系统：统一 token、组件、布局与视觉治理，降低页面风格漂移。
- 前端类型扩展治理链：生成层类型与 frontend-only `extensions` 命名空间分层管理，配套 validation/report/dashboard 工具链。
- 分层测试门禁：前端类型检查、Vitest、Playwright、PM2 冒烟、后端 Pytest 分层执行。
- 规范化治理链路：功能树、任务路由、OpenSpec、PR 模板和验证证据形成协作闭环。

## 关键文档入口与真相源

### 真相源分层

| 类别 | 当前入口 | 用途 |
|------|----------|------|
| 业务能力真相源 | [docs/FUNCTION_TREE.md](./docs/FUNCTION_TREE.md) | 按功能域定位状态、模块路径、API 前缀、规范/测试/运行入口 |
| 流程治理真相源 | [architecture/STANDARDS.md](./architecture/STANDARDS.md) / [openspec/AGENTS.md](./openspec/AGENTS.md) | 审批门禁、工程红线、Proposal/Spec 工作流 |
| 数据源优化 V2 本地收口状态 | [openspec/changes/optimize-data-source-v2/tasks.md](./openspec/changes/optimize-data-source-v2/tasks.md) / [openspec/changes/optimize-data-source-v2/REPO_LOCAL_STATUS.md](./openspec/changes/optimize-data-source-v2/REPO_LOCAL_STATUS.md) | 说明 `optimize-data-source-v2` 当前仓库内实现、测试、文档与治理已闭环，剩余事项仅限外部部署、观测、验收与归档 |
| AkShare 市场门禁真相源 | [docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md](./docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md) / [docs/guides/akshare/INDEX.md](./docs/guides/akshare/INDEX.md) | 约束 MyStocks 仅接入本地已存在的 AkShare 同名函数，并通过 wrapper-first 门禁输出审计报告 |
| 前端类型扩展与治理 | [docs/guides/typescript/TYPESCRIPT_EXTENSION_SYSTEM_REPO_TRUTH_GUIDE.md](./docs/guides/typescript/TYPESCRIPT_EXTENSION_SYSTEM_REPO_TRUTH_GUIDE.md) / [openspec/changes/implement-typescript-type-extension-system/tasks.md](./openspec/changes/implement-typescript-type-extension-system/tasks.md) | `extensions` 命名空间、canonical 目录布局、验证脚本、回滚路径与专题闭环证据 |
| 任务路由入口 | [docs/guides/ai-tools/AI_QUICK_START.md](./docs/guides/ai-tools/AI_QUICK_START.md) | 按任务类型决定先读什么、再跳到哪个功能域 |
| 文档导航入口 | [docs/INDEX.md](./docs/INDEX.md) | 从文档系统入口快速定位 active guides |
| 变更交付真相源 | [docs/guides/governance/FEATURE_MANAGEMENT_WORKFLOW.md](./docs/guides/governance/FEATURE_MANAGEMENT_WORKFLOW.md) / [.github/pull_request_template.md](./.github/pull_request_template.md) | 功能域映射、入口同步规则、PR 校验与验证证据 |

### 推荐阅读顺序

1. 先看 [docs/guides/ai-tools/AI_QUICK_START.md](./docs/guides/ai-tools/AI_QUICK_START.md)
2. 再进入 [docs/FUNCTION_TREE.md](./docs/FUNCTION_TREE.md) 的目标功能域
3. 涉及规则与审批时，回到 [architecture/STANDARDS.md](./architecture/STANDARDS.md)
4. 涉及 proposal、spec、能力新增或架构调整时，再读 [openspec/AGENTS.md](./openspec/AGENTS.md)
5. 若主题是 `optimize-data-source-v2`，再直接核对 [openspec/changes/optimize-data-source-v2/tasks.md](./openspec/changes/optimize-data-source-v2/tasks.md) 与 [openspec/changes/optimize-data-source-v2/REPO_LOCAL_STATUS.md](./openspec/changes/optimize-data-source-v2/REPO_LOCAL_STATUS.md)，确认本地是否还有合法未闭合项

### 模块文档说明

- [docs/standards/PROJECT_MODULES.md](./docs/standards/PROJECT_MODULES.md) 可以保留为模块清单参考。
- 该文档目前仍含旧口径，例如 `Element Plus` 与旧目录命名，不应作为当前模块事实源。
- 当前模块与业务能力判断，应优先回到 [docs/FUNCTION_TREE.md](./docs/FUNCTION_TREE.md) 和实际代码入口。

### 不作为现行真相源

- 历史报告、archive、demo、一次性完成报告默认不作为当前运行状态、当前门禁口径或当前功能完成度的真相源。
- 这些文档可以作为背景、审计证据或里程碑记录，但引用时必须保留日期和上下文。

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | Vue 3、TypeScript、Vite、Pinia、Vue Router、ECharts、ArtDeco |
| 后端 | Python 3.12+、FastAPI、Pydantic、SQLAlchemy |
| 数据库 | PostgreSQL 17+、TimescaleDB、TDengine 3.3+ |
| 测试 | Vitest、Playwright、Pytest |
| 部署 | PM2、Docker、环境变量驱动配置 |
| AI 集成 | Kronos 外部 GPU 推理服务，采用 contract-first 集成方式 |

## 快速开始

### 环境要求

- Python `3.12+`
- Node.js `18+`
- PostgreSQL `17+`
- TimescaleDB
- TDengine `3.3+`（可选，用于高频时序数据）

### 安装依赖

```bash
# backend
cd web/backend
pip install -r requirements.txt

# frontend
cd web/frontend
npm install
```

### 启动开发环境

```bash
# backend
cd web/backend
uvicorn app.main:app --host 0.0.0.0 --port 8020 --reload

# frontend
cd web/frontend
npm run dev -- --port 3020
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端 | `http://localhost:3020` |
| 后端 | `http://localhost:8020` |
| Swagger | `http://localhost:8020/docs` |
| 健康检查 | `http://localhost:8020/health` |

## 开发流程与治理方法

### 项目管理方法

- 方案先行：涉及菜单结构、UI 风格、核心架构或能力新增，必须先走 proposal / approval。
- 功能树驱动：先在 [docs/FUNCTION_TREE.md](./docs/FUNCTION_TREE.md) 定位功能域，再下钻规范、代码、测试和运行入口。
- 契约先行：接口语义以 FastAPI 路由、Pydantic schema 与导出的 OpenAPI 为准，不维护并行真值。
- 垂直切片：一次打通一个 feature 的 `DB -> Service -> API -> UI -> Test` 链路。
- 测试闭环：提交前必须提供对应验证证据，而不是只给代码 diff。

### 推荐协作入口

- 共享规则： [architecture/STANDARDS.md](./architecture/STANDARDS.md)
- OpenSpec： [openspec/AGENTS.md](./openspec/AGENTS.md)
- 功能管理： [docs/guides/governance/FEATURE_MANAGEMENT_WORKFLOW.md](./docs/guides/governance/FEATURE_MANAGEMENT_WORKFLOW.md)
- PR 校验： [.github/pull_request_template.md](./.github/pull_request_template.md)

## 测试与质量门禁

### 前端常用命令

```bash
cd web/frontend
npm run type-check
npm run type:audit:quality
npm run type:report
npm run type:dashboard
npm run test
npm run test:unit:stable
npm run test:e2e:business-smoke
npm run test:e2e:chromium
```

### 后端常用命令

```bash
pytest
pytest -m unit
pytest -m integration
pytest --cov=src --cov=web/backend/app --cov-report=html
```

### 质量门禁关注点

- 结构性语法错误必须为 `0`
- 前端类型错误不得高于技术债基线
- `mystocks-backend` 与 `mystocks-frontend` 的运行状态必须可确认
- E2E 必须按实际执行结果报告，不再使用历史固定值

### AkShare 市场门禁

- 统一入口：[`scripts/dev/quality_gate/run_akshare_market_gates.py`](./scripts/dev/quality_gate/run_akshare_market_gates.py)
- 标准输出：`akshare-market-function-availability.json`、`akshare-market-repo-truth-gate.json`、`akshare-market-gates-summary.json`
- 固化边界：仅校验本地 `akshare` 同名函数与仓库台账的一致性，不自动生成业务代码，不以第三方或异源接口补缺
- 专题文档：[`docs/guides/akshare/INDEX.md`](./docs/guides/akshare/INDEX.md)

### 测试文档入口

- [docs/testing/README.md](./docs/testing/README.md)
- [docs/testing/E2E_TEST_GUIDE.md](./docs/testing/E2E_TEST_GUIDE.md)
- [docs/guides/frontend/PR_GATE_QUICK_REFERENCE.md](./docs/guides/frontend/PR_GATE_QUICK_REFERENCE.md)
- [scripts/run_e2e_pm2.sh](./scripts/run_e2e_pm2.sh)

## 部署与运行

### PM2 与生产运行

- 本仓库支持 PM2 管理前后端服务，但不同阶段存在多份 PM2 配置。
- README 只给出入口，不把某一个历史命令误写成唯一真相。
- 当前应优先参考：
  - [docs/guides/pm2/PM2_QUICK_START_GUIDE.md](./docs/guides/pm2/PM2_QUICK_START_GUIDE.md)
  - [docs/operations/README.md](./docs/operations/README.md)
  - [config/ecosystem.config.js](./config/ecosystem.config.js)
  - [config/ecosystem.production.config.js](./config/ecosystem.production.config.js)

### 默认服务名

- `mystocks-frontend`
- `mystocks-backend`

### Docker 与运维

- Docker、运维排障和监控不在 README 内重复展开。
- 运行、排障与基础设施检查统一从 [docs/operations/README.md](./docs/operations/README.md) 下钻。

## 配置说明

### 环境变量

复制 `.env.example` 为 `.env`，再填写数据库、JWT、CORS 与端口配置。

```bash
cp .env.example .env
```

### 当前默认端口

| 键 | 默认值 |
|----|--------|
| `FRONTEND_PORT` | `3020` |
| `FRONTEND_BACKUP_PORT` | `3021` |
| `BACKEND_PORT` | `8020` |
| `BACKEND_BACKUP_PORT` | `8021` |

### 关键配置关注项

- `POSTGRESQL_*`
- `JWT_SECRET_KEY`
- `CORS_ORIGINS`
- `KLINE_FALLBACK_ENABLED`
- `REDIS_*`（可选）

## 项目结构

```text
mystocks_spec/
├── architecture/                 # 架构红线、域边界、治理规则
├── config/                       # PM2、部署、运行配置
├── docs/                         # 文档系统入口、功能树、guides、reports
│   ├── FUNCTION_TREE.md          # 业务能力真相源入口
│   ├── INDEX.md                  # 文档总入口
│   ├── guides/                   # 开发、治理、前端、PM2 等指南
│   ├── operations/               # 运行、排障、监控
│   ├── standards/                # 标准、基线、参考清单
│   └── testing/                  # 测试 trunk 与专题文档
├── openspec/                     # Proposal / spec 工作流
├── scripts/                      # 开发、生成、验证、自动化脚本
├── src/                          # Python 核心业务与数据层
│   ├── adapters/                 # 多数据源适配器
│   ├── core/                     # 核心分类、路由、管理器
│   ├── data_access/              # 数据库访问层
│   ├── governance/               # 风控与治理
│   ├── monitoring/               # 监控与告警
│   └── gpu/                      # GPU 与加速能力
├── tests/                        # 后端、集成、性能、安全测试
├── web/
│   ├── backend/                  # FastAPI 后端
│   │   ├── app/api/              # API 路由
│   │   ├── app/services/         # 应用服务层
│   │   └── app/schemas/          # 请求/响应 schema
│   └── frontend/                 # Vue 3 + ArtDeco 前端
│       ├── src/views/            # 业务页面
│       ├── src/components/       # 组件
│       ├── src/stores/           # Pinia 状态
│       ├── src/router/           # 路由入口
│       ├── src/api/              # 前端 API 封装
│       └── src/styles/           # ArtDeco token、样式层、兼容层
└── README.md
```

## ArtDeco 设计系统

ArtDeco 是当前前端视觉与组件治理主线，不再把旧 `Element Plus` 叙述当作 README 主口径。

### 设计真相源

- [DESIGN.md](./DESIGN.md)
- [docs/guides/web/ARTDECO_START_HERE.md](./docs/guides/web/ARTDECO_START_HERE.md)
- [docs/guides/web/ARTDECO_MASTER_INDEX.md](./docs/guides/web/ARTDECO_MASTER_INDEX.md)
- [docs/guides/web/ARTDECO_SCSS_GOVERNANCE_BASELINE.md](./docs/guides/web/ARTDECO_SCSS_GOVERNANCE_BASELINE.md)

### 管理原则

- Design token 与视觉语义统一收敛，不继续扩散平行样式体系。
- 兼容层只允许做桥接，不再作为主真值维护。
- 文档链路按 `START_HERE -> MASTER_INDEX -> SPEC / GUIDE / CATALOG` 使用。

## Kronos AI 推理集成

MyStocks 对 Kronos 的定位是外部 GPU 推理依赖，而不是把 Kronos 内嵌成仓库内业务模块。

### 集成思路

- 采用 contract-first，先固化服务契约，再接入业务链路。
- 优先约束 `HTTP` 推理接口，并保持 `MCP + HTTP` 共享同一 runtime 的方向。
- 明确错误码、超时、降级和可观测性字段，避免推理服务接口漂移。

### 参考文档

- [docs/plans/kronos-integration-developer-guidance.md](./docs/plans/kronos-integration-developer-guidance.md)
- [openspec/changes/add-kronos-integration-contract/proposal.md](./openspec/changes/add-kronos-integration-contract/proposal.md)
- [openspec/changes/add-kronos-integration-contract/specs/kronos-integration-contract/spec.md](./openspec/changes/add-kronos-integration-contract/specs/kronos-integration-contract/spec.md)

## FAQ 与健康检查

### 前后端是否正常运行

```bash
pm2 list
```

应关注：

- `mystocks-frontend`
- `mystocks-backend`

### 访问地址不通怎么办

- 先确认 `.env` 中端口是否仍为 `3020 / 8020`
- 再确认本地是否有端口占用
- 最后查看 [docs/operations/TROUBLESHOOTING_QUICK_REFERENCE.md](./docs/operations/TROUBLESHOOTING_QUICK_REFERENCE.md)

### 从哪里开始排障

- 运行与运维： [docs/operations/README.md](./docs/operations/README.md)
- 测试与 E2E： [docs/testing/README.md](./docs/testing/README.md)
- 业务功能入口： [docs/FUNCTION_TREE.md](./docs/FUNCTION_TREE.md)

## 贡献与标准

- 仓库共享规则与审批门禁： [architecture/STANDARDS.md](./architecture/STANDARDS.md)
- OpenSpec 工作流： [openspec/AGENTS.md](./openspec/AGENTS.md)
- 功能管理同步规则： [docs/guides/governance/FEATURE_MANAGEMENT_WORKFLOW.md](./docs/guides/governance/FEATURE_MANAGEMENT_WORKFLOW.md)
- PR 提交模板： [.github/pull_request_template.md](./.github/pull_request_template.md)

提交和评审时，应至少说明：

- 本次改动属于哪个功能域
- 影响了哪个 `FUNCTION_TREE` 节点
- 修改了哪些入口文档
- 提供了哪些验证证据

## 历史背景

本节仅保留背景、演进和管理方法线索，不作为当前实现或当前门禁的真相源。

### 前端手工测试修改机制建立

- 入口文档： [docs/changes/frontend/FRONTEND_CHANGES.md](./docs/changes/frontend/FRONTEND_CHANGES.md)
- 作用：把前端人工测试修正、变更记录和回溯线索沉淀为持续可查的文档链路。

### Maestro 多 CLI 协作闭环

- 入口文档： [docs/reports/MONGODB_MULTICLI_COORDINATION_PROGRESS_2026-03-14.md](./docs/reports/MONGODB_MULTICLI_COORDINATION_PROGRESS_2026-03-14.md)
- 作用：记录多 CLI 协作、任务同步、过程证据和收口方法的阶段性背景。

### 其他里程碑参考

- [docs/plans/frontend-page-optimization-list.md](./docs/plans/frontend-page-optimization-list.md)
- [src/monitoring/code_inventory/README.md](./src/monitoring/code_inventory/README.md)
- [docs/api/security-remediation-report.md](./docs/api/security-remediation-report.md)
- [architecture/DOMAIN_BOUNDARIES.md](./architecture/DOMAIN_BOUNDARIES.md)

## 许可证

MIT License，详见 [LICENSE](./LICENSE)。
