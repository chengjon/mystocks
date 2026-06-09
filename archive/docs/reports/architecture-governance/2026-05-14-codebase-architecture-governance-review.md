# MyStocks 架构治理审核意见（已批准）

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> 状态：Approved
> 日期：2026-05-14
> 批准记录：用户已在 2026-05-14 明确回复“同意，请继续”。
> 范围：代码库架构治理分析与治理建议
> 执行约束：本文件仅保存审核意见，不包含任务代码修改；任何涉及核心架构、目录结构、API/Schema、前端路由、数据源模式的实施动作，均需按 OpenSpec 与 `architecture/STANDARDS.md` 先审批后执行。

## 1. 审核目的

本次审核使用 `improve-codebase-architecture` 的判断口径，围绕以下问题评估当前项目架构：

- 模块是否足够深，是否能用较小接口隐藏较多行为。
- 架构知识是否集中，维护者是否需要在多个浅模块之间反复跳转。
- 关键接口是否形成稳定测试面。
- 技术债、迁移线、兼容层是否有明确收口路径。
- 架构决策是否可追溯，是否能被后续人类维护者和 AI agent 稳定导航。

本次审核不以“新增抽象”为目标，而以“收口、单源化、降低歧义、提高可导航性”为主。

## 2. 只读事实摘要

### 2.1 当前工作区状态

- 当前分支：`wip/root-dirty-20260403`
- 工作区存在大量未提交变更，约 `1020` 条 dirty 记录。
- 当前状态不适合直接进行跨模块架构修改；后续若实施，应采用小批次治理，并在每个批次中明确 staged scope。

### 2.2 文档与治理真相源

已存在并应作为主要依据的治理材料：

- `architecture/STANDARDS.md`：工程红线、审批门禁、迁移收口与技术债治理规则的共享事实源。
- `openspec/AGENTS.md`：OpenSpec 变更管理、proposal、spec、validation、approval gate 的流程说明。
- `openspec/specs/architecture-governance/spec.md`：架构治理能力事实源。
- `openspec/specs/directory-governance/spec.md`：目录治理与仓库卫生事实源。
- `openspec/specs/frontend-routing/spec.md`：前端路由治理事实源。
- `docs/guides/frontend-structure.md`：当前前端目录与路由事实说明。
- `.zread/wiki/versions/2026-05-14-013747/`：2026-05-13 生成的架构 wiki，可作为项目导航入口。

Matt Pocock 工程技能默认依赖的以下文件当前不存在：

- `CONTEXT.md`
- `docs/CONTEXT.md`
- `docs/adr/`
- `docs/agents/`

这不是立即缺陷，但会导致后续架构分析缺少统一领域术语入口，容易重复发现已知决策。

### 2.3 当前活跃 OpenSpec 变更

当前存在多个与本审核建议直接相关的 active changes：

- `restructure-frontend-directory`：前端目录重构，进度接近收口。
- `implement-html5-migration-experience-optimization`：HTML5 迁移体验优化。
- `enhance-api-contract-management-integration`：API 契约管理集成。
- `optimize-data-source-v2`：数据源管理与数据治理模块优化 V2。
- `implement-optimized-html-vue-artdeco-conversion`：HTML 到 Vue ArtDeco 转换优化。
- `add-smart-quant-monitoring`：智能量化监控。
- `add-comprehensive-risk-management-system`：综合风险管理系统。

结论：当前应优先完成已有变更的收口，不宜另开平行的大型架构治理线，除非新事项无法映射到现有 OpenSpec 变更。

## 3. 架构现状判断

### 3.1 总体判断

MyStocks 已经具备较强的工程治理骨架：OpenSpec、架构标准、zread wiki、前端结构指南、技术债基线与多条迁移计划都已经存在。当前主要风险不是“缺少架构设计”，而是：

- 真相源较多，入口和边界容易混淆。
- 多条迁移线并行，收口压力大。
- 历史兼容层、archive、backup、old 文件仍影响静态分析和 AI 导航。
- 后端 API 层和服务层存在胖模块，业务知识分散在 HTTP 层和服务层之间。
- 数据源、适配器、数据访问、存储路由等概念分布在多个目录中，认知成本偏高。

### 3.2 后端 API 与服务层

扫描到的结构信号：

- `web/backend/app/api` 约 `213` 个 Python 文件，其中约 `54` 个超过 500 行。
- `web/backend/app/services` 约 `145` 个 Python 文件，其中约 `28` 个超过 500 行。
- 典型胖 API 文件包括：
  - `web/backend/app/api/monitoring.py`
  - `web/backend/app/api/strategy_management/get_monitoring_db.py`
  - `web/backend/app/api/efinance.py`
  - `web/backend/app/api/tasks.py`
  - `web/backend/app/api/risk/alerts.py`

判断：API 层很可能承担了过多业务编排、缓存、数据访问、异常映射和响应组装职责。问题不在于“文件长”本身，而在于测试面不稳定：如果业务规则只能通过 HTTP endpoint 测试，维护成本会持续升高。

### 3.3 前端视图与路由层

扫描到的结构信号：

- `web/frontend/src/views` 下共有约 `540` 个文件。
- 其中 Vue/TypeScript 文件合计约 `469` 个：Vue 文件约 `257` 个，TypeScript 文件约 `212` 个。
- Vue 文件中超过 500 行的约 `14` 个；若按 `>=500` 行口径统计，则为 `15` 个。
- Vue/TypeScript 文件中 `>=500` 行的合计约 `25` 个。该数字包含 view-local TypeScript、composable 和测试文件，不应误读为“大型 Vue SFC 数量”。
- `web/frontend/src/router/index.ts` 约 `414` 行，包含约 `55` 个 route path 记录和约 `44` 个动态 import。

判断：前端已有合理的三层状态模型（Store / Composable / View-Local），但迁移仍处在收口阶段。当前应优先完成 `restructure-frontend-directory`，而不是再发起新的目录治理方案。

### 3.4 数据层与数据源治理

当前数据相关概念分布在多个区域：

- `src/adapters`
- `src/data_sources`
- `src/data_access`
- `src/storage`
- `src/database`
- `src/core/data_source*`
- `src/core/data_manager.py`
- `src/core/unified_manager.py`
- `src/core/config_driven_table_manager.py`
- `src/core/data_classification.py`

zread wiki 将核心数据路径描述为：

- `MyStocksUnifiedManager`
- `DataManager`
- `DataRouter`
- `AdapterRegistry`
- `TDengineDataAccess`
- `PostgreSQLDataAccess`

补充信号：`AdapterRegistry` 概念在两个位置均有具体实现，分别是 `src/core/infrastructure/adapter_registry.py` 与 `web/backend/app/core/adapter_factory.py`。这进一步说明数据源注册概念存在跨层/跨目录表达，后续治理应先明确 canonical registry，而不是直接做目录搬迁。

判断：数据层的主问题是同一领域概念存在多个目录表达。治理时不应简单搬目录，而应先明确两个深模块：

- `Data Source Runtime`：外部数据源接入、优先级、健康检查、熔断、限流、质量校验、失败恢复。
- `Storage Routing Runtime`：`DataClassification` 到 TDengine/PostgreSQL 的路由、表结构、事务/批量写入、失败策略。

### 3.5 DDD 分层

zread wiki 描述当前后端核心采用 `src/domain`、`src/application`、`src/infrastructure` 的 DDD 分层。静态扫描显示整体分层基础存在，但发现少量 Domain 层反向依赖 Infrastructure 的信号：

- `src/domain/portfolio/service/portfolio_valuation_service.py`
- `src/domain/portfolio/service/portfolio_valuation_service_optimized.py`

问题点：Domain 层导入了 `src.infrastructure.persistence.exceptions`。

判断：这是小范围但高价值的治理点。Domain 层应使用领域错误语义，Infrastructure 层负责把数据库/持久化异常映射为领域可理解的错误。

### 3.6 契约生成与类型同步

当前可见多个契约/类型相关入口：

- `scripts/generate_frontend_types.py`
- `scripts/dev/generate-types/generate_ts_types.py`
- `web/backend/app/api/contract/services/openapi_generator.py`

判断：这些入口可能分别服务于不同阶段，但如果没有明确 canonical path，会产生“类型到底以哪份输出为准”的维护风险。该事项应挂靠 `enhance-api-contract-management-integration`，明确唯一生成命令、兼容包装脚本和 generated 输出目录规则。

### 3.7 Legacy / Archive / Backup 干扰

命名上带有 `legacy`、`archive`、`backup`、`bak`、`old`、`deprecated`、`part` 等信号的文件较多，主要集中在 archive 区域，但活跃目录中仍有少量旧文件。

GitNexus 对核心符号出现歧义，例如 `MyStocksUnifiedManager`、`ConfigDrivenTableManager` 同时存在于 `src/` 和 archive 中。

判断：这会降低 AI 导航和静态分析质量。治理时应区分：

- 工具视角：GitNexus、zread、静态分析默认排除 archive/legacy，降低误命中。
- 代码视角：活跃目录中的 `.old.py`、`.backup`、`.bak` 按 `architecture/STANDARDS.md` 的迁移收口与删除决策标准逐项处理。

## 4. 治理建议

### 建议 1：Closure-First，优先完成既有 OpenSpec 收口

优先级：P0

不要新增“架构优化总计划”。应先把已有 active changes 映射、收口、归档：

- `restructure-frontend-directory`：完成 review、最终批准、合并、CI/staging 验证和归档。
- `optimize-data-source-v2`：作为数据源治理主线继续推进。
- `enhance-api-contract-management-integration`：作为前后端契约治理主线继续推进。

验收口径：

- 每项治理建议都能映射到已有 active change；无法映射时才创建新的 OpenSpec proposal。
- 不允许在同一领域开平行 proposal 造成双轨治理。

### 建议 2：建立轻量架构索引层，避免重复真相源

优先级：P1

建议后续经审批新增一个轻量文档，例如：

- `docs/agents/architecture-map.md`，或
- `CONTEXT.md`

当前 `docs/agents/` 目录不存在；若选择 `docs/agents/architecture-map.md`，实施时需要显式创建该目录。若希望减少目录新增，根目录 `CONTEXT.md` 是更轻量的候选入口。

该文件不复制规则正文，只维护术语和事实源链接：

- 工程红线指向 `architecture/STANDARDS.md`
- 当前能力事实指向 `openspec/specs/*/spec.md`
- 活跃变更指向 `openspec/changes/*`
- 前端目录事实指向 `docs/guides/frontend-structure.md`
- zread wiki 作为导航入口而非规范正文

收益：

- 后续 agent 不必重新发现项目治理结构。
- Matt Pocock 工程技能可以获得稳定上下文。
- 降低 STANDARDS、AGENTS、OpenSpec、wiki 之间的重复维护成本。

### 建议 3：后端 API 层治理为“薄路由 + 用例服务”

优先级：P1

建议选择一个高价值领域试点，例如：

- `monitoring`
- `strategy_management`
- `efinance`

目标：

- 路由只负责参数解析、认证/权限、错误映射、响应包装。
- 业务编排进入 application/use-case service。
- 数据访问通过 repository/port 进入。
- 核心业务测试面从 HTTP endpoint 收缩到稳定 use-case 接口。

这属于架构模式变化，实施前应创建或挂靠 OpenSpec proposal。

### 建议 4：数据层按两个深模块治理，而不是机械搬目录

优先级：P2

建议在 `optimize-data-source-v2` 中明确两个深模块：

- `Data Source Runtime`
- `Storage Routing Runtime`

先做接口和职责矩阵，再决定目录是否调整。

判断标准：

- 删除某个 manager/router 后，如果复杂度散落到多个调用方，则该模块有深度，应该保留并加深。
- 删除某个 pass-through 后，如果复杂度消失，则应纳入收口候选。

### 建议 5：修复 Domain 层对 Infrastructure 异常的反向依赖

优先级：P2

建议后续以小切片治理：

- 为 Portfolio Domain 定义领域错误语义。
- Infrastructure 将持久化异常映射为领域错误。
- 增加分层约束测试，防止 `src/domain` 导入 `src.infrastructure`。

收益：

- Domain 层测试无需知道持久化实现。
- Application 层可以统一处理业务错误。
- DDD 分层从目录约定变成可执行约束。

### 建议 6：明确前后端类型生成唯一入口

优先级：P1

建议挂靠 `enhance-api-contract-management-integration`：

- 明确唯一 canonical 生成命令。
- 明确哪些脚本是兼容包装。
- 明确 generated 文件不可手改。
- 明确前端扩展类型应放置在哪些安全目录。
- CI 门禁应比较唯一契约 artifact。

收益：

- 降低 OpenAPI、Pydantic、TypeScript 类型漂移。
- 减少脚本多头维护。
- 提高契约变更可审计性。

### 建议 7：前端治理集中在路由与目录收口

优先级：P1

短期不建议扩大新的前端架构改造。建议只做：

- 完成 `restructure-frontend-directory`。
- 禁止新增根级 `views/*.vue` 大页面。
- 新页面按业务域进入 canonical 目录。
- 对超过 500 行的视图，只在业务切片中迁移数据加载、转换、API 调用到 composable 或 view-local `.ts`。

注意：

- `/dashboard` 当前仍由 `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue` 提供。
- `/trade/terminal` 当前仍由 `web/frontend/src/views/TradingDashboard.vue` 提供。
- 上述 repo-truth 例外应保留，不能被旧迁移快照误导。

### 建议 8：Legacy / Archive 治理先降低工具干扰，再逐项收口

优先级：P2

建议分两层处理：

1. 工具层：
   - GitNexus、zread、静态分析默认排除 archive/legacy 区域。
   - 降低旧符号对当前架构导航的干扰。

2. 代码层：
   - 活跃目录中的 `.old.py`、`.backup`、`.bak` 文件进入技术债清单。
   - 按 `architecture/STANDARDS.md` 的迁移收口与删除决策标准逐项审批处理。

禁止：

- 禁止仅凭“搜不到引用”直接删除。
- 禁止在 dirty 工作区里做大范围清理。

## 5. 建议实施顺序

### P0：收口优先

- 完成 `restructure-frontend-directory` 的剩余审批、合并、CI、归档。
- 明确数据源 V2 和 API contract integration 的剩余任务是否仍有效。
- 暂停新增与这些变更重叠的架构 proposal。

### P1：单源化与接口治理

- 建立轻量架构索引层。
- 明确类型生成 canonical path。
- 选择一个后端胖 API 领域试点“薄路由 + 用例服务”。
- 前端路由和目录继续按现有 active change 收口。

### P2：分层约束与技术债清理

- 修复 Domain -> Infrastructure 反向依赖。
- 为 DDD 分层增加可执行约束测试。
- 清点 active 目录中的 old/backup 文件。
- 配置工具排除 archive/legacy 干扰。

## 6. 审批建议

建议审批方式分为三档：

### 选项 A：批准治理方向，但不立即实施代码

批准本文作为后续治理参考。后续每个 P1/P2 项目单独创建 OpenSpec proposal 或挂靠现有 active change，经审批后再执行。

### 选项 B：批准并指定一个试点

建议优先试点之一：

1. API contract canonical path 收口。
2. `monitoring` API 薄路由治理。
3. Domain -> Infrastructure 反向依赖修复。
4. 架构索引层文档建立。

### 选项 C：退回修改

如认为当前意见粒度过大，可要求补充：

- 更细的文件清单。
- 对某个领域的专门治理方案。
- 与某个 OpenSpec active change 的逐项映射。
- 风险矩阵和验收标准。

## 7. 明确非目标

本审核意见不授权以下动作：

- 不授权修改业务代码。
- 不授权删除 legacy/archive/backup 文件。
- 不授权调整前端路由结构。
- 不授权修改 API/Schema。
- 不授权创建新的 OpenSpec change。
- 不授权执行测试基线更新。

如需进入实施阶段，应先由用户明确批准具体治理切片。

## 附录 A. 统计复现口径

本报告中的结构统计为辅助判断，不作为固定质量门禁。复现时应在项目根目录执行，并记录统计口径。

前端 `views` 文件统计口径：

```bash
# 全部文件数
find web/frontend/src/views -type f | wc -l

# Vue 文件数
find web/frontend/src/views -type f -name "*.vue" | wc -l

# TypeScript 文件数
find web/frontend/src/views -type f -name "*.ts" | wc -l
```

大文件统计建议使用脚本按行数计算，避免 `wc -l` 与文本末尾换行差异造成 1 行偏差。本文采用的口径是：

- Vue 文件 `>500` 行：约 `14` 个。
- Vue 文件 `>=500` 行：约 `15` 个。
- Vue/TypeScript 文件 `>=500` 行：约 `25` 个。

后续若用这些数字作为治理门槛，应把统计脚本固化到仓库脚本或质量报告中，而不是依赖人工复算。
