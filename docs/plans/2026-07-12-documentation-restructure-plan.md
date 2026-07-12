# MyStocks 核心文档重构规划

> **创建日期**: 2026-07-12
> **维护者**: 文档治理团队
> **文档类型**: 治理规划
> **状态**: 待审批
> **触发原因**: 现有 `docs/api/` 200+ 文件、`docs/reports/` 100+ 文件严重膨胀，历史一次性产物未退役，同主题文档按时间分多份，缺少以"读者任务"为导向的统一入口。

---

## 一、现状诊断

### 1.1 各目录体量

| 目录 | 文件分布 | 健康度 | 核心问题 |
|------|---------|--------|---------|
| `docs/guides/` | 23 子目录 + 5 根文件 | 🟢 健康 | 子目录多但 entry 清晰 |
| `docs/api/` | **235 文件**（根级 147 + 6 子目录） | 🔴 膨胀 | Apifox 入门/导入/快速指南/成功 4 份、error code 2 份、phase reports 13 份、AI/LLM APIs 混入 |
| `docs/reports/` | **1,246 文件**（根级 671 + 19+ 子目录） | 🔴 严重膨胀 | 历史完成报告堆砌；数据量是规划预期的 12x |
| `docs/operations/` | 17 根文件 + 3 子目录（ci-cd/deployment/monitoring） | 🟡 中 | 结构合理，ci-cd/ 已收敛仅 11 份；缺少统一入口 |
| `docs/testing/` | 31 文件（含 e2e/ 子目录） | 🟡 中 | 偏薄，缺总纲（strategy） |
| `docs/archive/` | **存在但为空（0 文件）** | 🔴 未建立 | 需要先建立归档机制 |
| `docs/FUNCTION_TREE.md` | v1.0.0, 2026-03-12, 521 行 | 🟢 主骨 | 功能主线清晰，但太厚重 |
| `docs/standards/` | **35 文件**（含 security/ 子目录） | 🟡 被忽略 | 未在规划中考虑；重安全标准、代码规范 |
| `docs/design/` | **20 文件**（含 update/ 子目录） | 🟡 被忽略 | Figma 指南、ArtDeco 设计规格、Token 定义 |
| `docs/architecture/` | **30+ 文件**（含 legacy-cn/ 子目录） | 🟡 独立域 | 架构评估、适配器指南等功能性文档 |
| `docs/overview/` | 14 文件 | 🟢 小 | 项目总览、功能映射、初始提示 |
| `docs/references/` | 25 文件 | 🟢 小 | 参考手册、分类管理 |
| `docs/INDEX.md` | **2,197 行**（2026-03-25 生成） | 🔴 严重过时 | 全量索引文件严重庞大，早已成为维护负担 |

### 1.2 根因分析

1. **历史增量产物无退役规则**：phase 报告、验证报告、API 修复报告按"日期+阶段"持续堆积在 `api/`、`reports/`。`reports/` 实际 1,246 文件，远超预期。
2. **同主题文档按时间分多份**：Error Code 有 2 份、Apifox 4 份、API 契约 2 份，没有以读者任务收敛。
3. **角色入口缺失**：开发者/测试/运维/AI 工具/契约管理各自所需文档散在不同目录，没有以"一条主线 + 五本手册"分流的总入口。
4. **附属目录被忽略**：`docs/standards/`（35 份）、`docs/design/`（20 份）、`docs/overview/`（14 份）等独立目录未被纳入重构范围，导致治理盲区。

---

## 二、设计原则

1. **以项目功能为主线**：以现有 `FUNCTION_TREE.md` 的 10 域为骨架，主文档挂载功能入口锚点。
2. **以读者任务分手册**：按开发 / 测试 / 运维 / AI 工具 / API 契约 5 个视角分流，每手册一份"主文档"。
3. **索引与内容分离**：一份总入口 `CORE.md` + 每手册一份"主文档"；子文档仅做深度参考，不承载导航责任。
4. **最小迁移原则**：除膨胀源 (`api/`, `reports/`) 外，现有 `guides/`、`operations/`、`testing/` 子目录中活跃文档保留原位，通过超链接挂到新骨架。

---

## 三、目标结构

```
docs/
├── CORE.md                         🆕 总入口（按读者角色分流 + 功能域速查表）
├── FUNCTION_TREE.md                🔄 保留升级（补稳定 ID + 各域入口锚点）
│
├── dev/    (开发手册)              🆕 整合 guides/ 中与"开发任务"直接相关的指南
│   ├── index.md
│   ├── onboarding.md
│   ├── api-development.md         ← 合并 Apifox 多份 + API 集成指南 + 版本映射
│   ├── frontend-components.md     ← 整合 ArtDeco 组件指南 + 前端变更卫生
│   ├── data-sources.md
│   ├── architecture-standards.md  ← 指向 architecture/STANDARDS.md
│   └── governance.md              ← 合并 AGENTS 系列 4 份治理文档
│
├── test/   (测试手册)              🆕 整合 testing/ + guides/e2e
│   ├── index.md
│   ├── strategy.md
│   ├── e2e-guide.md
│   ├── ci-cd-guide.md             ← 跨链 operations/ci-cd/ 家族
│   └── quality-gate.md
│
├── ops/    (运维手册)              🔄 由 operations/ 升级
│   ├── index.md
│   ├── deployment.md              ← 合并 deploy-guide.md + operations/deployment/
│   ├── monitoring.md              ← 合并 operations/monitoring/ + 监控总览
│   ├── backup-recovery.md         ← 指向 operations/BACKUP_GUIDE.md
│   ├── troubleshooting.md         ← 合并 TROUBLESHOOTING.md + 快参
│   └── runbooks/                  ← 按需加入故障处理预案
│
├── api/    (API 契约管理)          🔄 大瘦身，仅保留"活"API 契约
│   ├── index.md
│   ├── contracts/                 ← OpenAPI 契约文件
│   ├── error-codes.md             ← 合并 ERROR_CODES.md + ERROR_CODE_GUIDE.md
│   ├── apifox-guide.md            ← 合并 APIFOX 系列 4 份
│   └── integration.md             ← 整合 API_INTEGRATION_GUIDE.md[✅ 已存在] + API_CONTRACT_ARCHITECTURE_ANALYSIS.md + MyStocks_API_Mapping_Document.md 等
│
├── ai/     (AI 工具手册)           🆕 从 api/ 中拆分
│   ├── index.md
│   └── prompts/                   ← LLMS 类、AI 工具类
│
└── archive/                       🆕 需先建立归档机制（当前为空）
    ├── phase-reports/             ← api/PHASE*.md 13 份 + reports/phase_reports/
    ├── api-fix-reports/           ← api/DEEP_FIXES_REPORT.md 等 3 份
    ├── api-standalone-docs/       ← api/ 根级约 90 份一次性/历史独立文档
    ├── artdeco-optimization/      ← reports/ARTDECO_*.md 33 份
    ├── design-reports/            ← docs/design/ 中的一次性产物
    ├── standard-reports/          ← docs/standards/ 中一次性评审/审计报告
    └── analysis/                  ← 保留有价值分析报告（api/reports/analysis/ 6 份等）
```

注：`docs/guides/`（23 子目录 + 5 根文件，内部按主题已分层）、`docs/architecture/`（30+ 功能性架构文档）保持现状；`docs/operations/ci-cd/` 保持现状（已收敛完成仅 11 份，2026-07-12 最后核对）。

---

## 四、主要迁移/合并动作（20 项）

| # | 动作 | 来源 | → 目标 | 优先级 |
|---|------|------|--------|--------|
| 1 | 合并 Apifox 4 份 | `api/APIFOX_BEGINNER_GUIDE/IMPORT_GUIDE/QUICK_START/IMPORT_SUCCESS.md` | `api/apifox-guide.md` | P0 |
| 2 | 合并 Error Code 2 份 | `api/ERROR_CODES.md` + `api/ERROR_CODE_GUIDE.md` | `api/error-codes.md` | P0 |
| 3 | 合并 API 契约 2 份 | `api/CONTRACT_MANAGEMENT_API.md` + `api/CONTRACT_TESTING_API.md` | `api/contracts/` | P0 |
| 4 | 合并 Error/Exception 2 份 | `api/ERROR_CODE_GUIDE.md` + `api/EXCEPTION_HANDLER_GUIDE.md` | `api/error-codes.md`（合并到 #2） | P0 |
| 5 | 合并部署 | `operations/deployment/` + `operations/deployment-guide.md`[✅ 已存在] | `ops/deployment.md` | P1 |
| 6 | 合并监控 | `operations/monitoring/` + `operations/MYSTOCKS_MONITORING_SYSTEM_OVERVIEW.md` | `ops/monitoring.md` | P1 |
| 7 | 合并排障 | `operations/TROUBLESHOOTING.md` + `operations/TROUBLESHOOTING_QUICK_REFERENCE.md`[✅ 皆存在] | `ops/troubleshooting.md` | P1 |
| 8 | 归档 Phase 报告 | `api/PHASE*.md` 13 份 + `reports/phase_reports/` | `archive/phase-reports/` | P1 |
| 9 | 归档 API 修复报告 | `api/DEEP_FIXES_REPORT.md`、`POSTTOOLUSE_WRITE_HOOK_FIX_REPORT.md`、`SYSTEM_FIX_EXPERIENCE_REPORT.md` 共 3 份 | `archive/api-fix-reports/` | P1 |
| 10 | 归档 ARTDECO 报告 | `reports/ARTDECO_*.md` 33 份 | `archive/artdeco-optimization/` | P2 |
| 11 | AI 部分独立 | `api/LLMS_API_DOCUMENTATION.md`、`api/AGENTS_SKILLS_AVAILABILITY_REPORT.md` | `ai/` | P2 |
| 12 | 合并 AGENTS 治理文档 | `api/AGENTS_AUDIT_REPORT.md` + `api/AGENTS_QUICK_REFERENCE.md` + `api/AGENTS_SKILLS_AVAILABILITY_REPORT.md` 共 3 份 | `dev/governance.md` | P2 |
| 13 | 新建总入口 | — | `docs/CORE.md` | P0 |
| 14 | 新建开发/测试手册入口 | — | `docs/dev/index.md`、`docs/test/index.md` | P0 |
| 15 | 新建运维/API/AI 手册入口 | — | `docs/ops/index.md`、`docs/api/index.md`、`docs/ai/index.md` | P0 |
| 16 | **新增**: 评估 `docs/standards/` 35 份 | 保留活跃安全/编码规范，归档一次审计报告 | `dev/architecture-standards.md` / `archive/standard-reports/` | P2 |
| 17 | **新增**: 评估 `docs/design/` 20 份 | 保留 Figma/设计 Token/组件规格；归档一次性方案 | `dev/frontend-components.md` / `archive/design-reports/` | P2 |
| 18 | **新增**: 归档 `api/` 根级一次性文档 | `api/` 根级 147 份中约 90 份历史/一次性文档 | `archive/api-standalone-docs/` | P2 |
| 19 | **新增**: 清理 `docs/INDEX.md` | 2,197 行自动索引 → 轻量索引指向 `CORE.md` | `docs/INDEX.md` — 重写为轻量导航 | P0 |
| 20 | **新增**: 修复引用文档路径偏差 | 用户参考文档路径与实际情况不符（5 份在子目录而非根级） | 更新文档元数据/各引用处的路径 | P2 |

---

## 五、对日常需求的覆盖矩阵

| 日常任务 | 主查阅路径 | 关键文档 |
|---------|-----------|---------|
| 新增 API | `dev/api-development.md` → `api/contracts/` | API 版本映射、FastAPI 应用开发指南 |
| 前端开发 | `dev/frontend-components.md` | ArtDeco 组件指南、前端变更卫生、CSS/SCSS 开发指南 |
| 跑测试 | `test/e2e-guide.md` → `test/ci-cd-guide.md` | E2E 测试指南、CI 家族、Playwright 配置 |
| 发布上线 | `ops/deployment.md` | deploy.yml、PM2 一等公民、部署清单 |
| 排障 | `ops/troubleshooting.md` | 故障排除、phase6 恢复预案、Lnav 日志分析 |
| API 契约同步 | `api/contracts/` → `api/apifox-guide.md` | Apifox 导入/同步流程 |
| 查错误码 | `api/error-codes.md` | — |
| AI 调用 | `ai/index.md` | LLMS API 文档 |
| 新增数据源 | `dev/data-sources.md` | 新数据源接入指南 |
| CI/CD (pipeline) | `docs/operations/ci-cd/ARCHITECTURE.md` | 已在 2026-07-12 收敛完成 |
| 量化策略 | `dev/quant-trading.md` | 见 guides/quant-trading/ |
| 架构红线 | `dev/architecture-standards.md` | architecture/STANDARDS.md |

---

## 六、分阶段施工计划

### Phase 1：建骨架 + 总入口（预估 1-2 小时）

- 新建 `docs/CORE.md`：按角色分流（开发/测试/运维/AI 工具/API 契约），附功能域速查表。
- 新建 `docs/dev/index.md`、`docs/test/index.md`、`docs/ops/index.md`、`docs/api/index.md`、`docs/ai/index.md`。
- 更新 `docs/INDEX.md`：指向 `CORE.md`，不再直接堆砌全量链接。

**审计点 1**：索引连通性——从 `CORE.md` 每角色入口可达对应手册主页。

### Phase 2：合并同主题膨胀文档（预估 2-4 小时）

- 依次执行 P0 + P1 动作 #1-#7（合并 Apifox、Error/Exception、API 契约、部署、监控、排障）。
- 每合并一份，在原位留 `→ 已合并至 xxx，本文件仅作历史参考` 的重定向头。

**审计点 2**：在每份新合并文档头部标注"合并来源清单 + 合并日期"。

### Phase 3：归档历史一次性产物（预估 3-5 小时）

> ⚠️ 注意：`docs/reports/` 实际 1,246 文件（其中根级 671 份），远超规划预期的 100+。需分批进行。

- 先处理 P0-P1 动作 #8-#12（归档 Phase/API 修复、AGENTS 合并）。
- 归档 `docs/reports/` 中有日期后缀的尾报告（根级筛选优先移走尾部带日期的 ~300 份）。
- 执行新增动作 #16-#18：评估 `docs/standards/`、`docs/design/`、`api/` 根级一次性文档。
- 执行新增动作 #19：重写 `docs/INDEX.md` 为轻量导航。
- 已在 `docs/archive/` 的做软链接或重定向；未归档的迁入。需先建立 `docs/archive/` 归档子目录结构。

**审计点 3**：`docs/reports/` 根级从 671 份降到 ≤100 份；子目录从 19+ 个减少到 ≤10 个；`docs/archive/` 从空目录开始包含 ≥1 有效子目录。

### Phase 4：链接清洗 + 回归验证（预估 1-2 小时）

- 运行 `python scripts/tools/docs_indexer.py --categories` 更新索引。
- 用 `tests/unit/scripts/test_repository_hygiene_paths.py` 已建立的 CI hygiene 校验检查链接断裂。
- 在 `governance/mainline/task-cards/` 中建立治理任务卡跟踪。

**审计点 4**：`docs/INDEX.md` 交叉验证通过，CI hygiene 门禁零失败。

---

## 七、需确认的 3 个方向性决策

| # | 问题 | 选项 | 推荐 |
|---|------|------|------|
| 1 | 手册层级 | **A)** 新建顶层目录 `dev/test/ops/ai`（清晰但改动大）、**B)** 在现有 `guides/api/` 内部分层（改动小但结构仍不够直觉） | **A**（现有 `guides/` 内部也已经 27 个子目录，B 方案稀释不足） |
| 2 | archive 策略 | **A)** 整目录下沉为 archive、**B)** 仅把一次性报告归档，保留 analysis 类 | **B**（analysis 类报告仍有查阅价值） |
| 3 | 迁移强度 | **A)** 一次性全量迁移（快但冲击大）、**B)** 分阶段迁移 + 原位保留重定向头（稳但需 2 周） | **B**（避免断裂，原位留头给开发者过渡期） |

---

## 八、风险与缓解

| 风险 | 缓解 |
|------|------|
| 旧链接断裂 | 被迁移文件原位保留"重定向头"（Phase 2-3 持续 3 个月） |
| 合稿冲突 | 每份合并文档标注"合并来源清单 + 合并日期"，便于回查源文件 |
| ownership 不清 | 每手册主页标注 Owner（dev/→开发测试组长，test/→QA，ops/→运维，api/→后端架构） |
| 短期搜索失败 | `docs/INDEX.md` 保留"已迁移文档别名 → 新路径"的重定向清单（Phase 2-3 持续） |
| **reports/ 体量远超预期**（1,246 份） | Phase 3 按子目录分批归档，不追求一次性全量；根级 671 份 → 先归档尾部带日期的历史报告 |

---

## 九、验收标准

- [ ] `CORE.md` 角色分流 5 个入口各自可达对应手册主页
- [ ] `docs/api/` 从 235 份降到 ≤30 份（仅保留契约、错误码、集成、apifox 等"活"文档）
- [ ] `docs/reports/` 根级从 671 份降到 ≤100 份（Phase 3 分批；长尾日期报告优先归档，分析类保留）
- [ ] `docs/reports/` 子目录从 19+ 个减少到 ≤10 个（合并同类子目录）
- [ ] `docs/archive/` 从空目录变为包含 ≥1 个有效归档子目录
- [ ] `docs/INDEX.md` 从 2,197 行重写为轻量导航（≤100 行总入口卡片）
- [ ] 每份合并文档头部有"合并来源 + 合并日期"
- [ ] CI hygiene 门禁（`test_repository_hygiene_paths.py`等）零失败
- [ ] `python scripts/tools/docs_indexer.py --categories` 更新完成

---

## 十、附录 A：引用文档路径偏差修正

以下文档在仓库中的实际路径与惯用/预期路径不同，在索引更新、合并迁移时需注意：

| 文档名 | 惯例路径（用户/引用处） | 实际路径 |
|--------|----------------------|---------|
| `WEB_TESTING_TOOLS_SETUP.md` | `docs/guides/` | `docs/guides/web/WEB_TESTING_TOOLS_SETUP.md` |
| `NEW_API_SOURCE_INTEGRATION_GUIDE.md` | `docs/guides/` | `docs/guides/data-source/NEW_API_SOURCE_INTEGRATION_GUIDE.md` |
| `CHROME_DEVTOOLS_MCP_FIX_GUIDE.md` | `docs/guides/` | `docs/guides/chrome-devtools/CHROME_DEVTOOLS_MCP_FIX_GUIDE.md` |
| `css-scss-development-guide.md` | `docs/guides/` | `docs/guides/frontend/css-scss-development-guide.md` |
| `INFRASTRUCTURE_CHECKLIST.md` | `docs/guides/` | `docs/operations/INFRASTRUCTURE_CHECKLIST.md` |
| `MYSTOCKS_MONITORING_OPTIMIZATION_DEPLOYMENT.md` | `docs/guides/` | `docs/operations/monitoring/MYSTOCKS_MONITORING_OPTIMIZATION_DEPLOYMENT.md` |

## 十一、附录 B：审核日志

| 项目 | 内容 |
|------|------|
| 审核日期 | 2026-07-12 |
| 审核范围 | `docs/` 全目录审计（12 个子目录 + 根级 <br>1,656 文件） |
| 发现偏差 | 15 项数据偏差 + 8 项目录遗漏 |
| 修正动作 | 更新 1.1 节数据表、1.2 节根因分析、<br>3 节目标结构、4 节迁移动作表、<br>6 节 Phase 3、8 节风险、9 节验收标准 |
| 新增动作 | 4 项（#16-#20），合并动作从 15 → 20 项 |
| 状态 | 已修正，待审批 |

---

**待审批**：经主页查询后，Phase 1 可立即开工（建骨架风险低、收益明确）。

> 本规划同步受 [ARCHITECTURE.md](operations/ci-cd/ARCHITECTURE.md) 文档收敛原则约束——新增顶层目录需登记于 `docs/operations/ci-cd/ARCHITECTURE.md` 文档索引段。
