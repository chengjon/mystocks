# Phase 3：reports/ 一次性报告归档计划

> **日期**: 2026-07-12 | **状态**: 待审核
> **前置**: Phase 2 已验收通过（见 phase-2-merge-acceptance-2026-07-12.md）
> **本阶段目标**: 清理 reports/ 中一次性产物，使活跃报告可发现、可维护
> **审核意见**: 已根据 phase-3-archive-plan-review-2026-07-12.md 修正（子目录数、Git 跟踪数、空目录数、层级结构）

---

## 1. 现状总览

| 指标 | 数值 |
|------|------|
| reports/ 总文件数 | **1,950** |
| 直接子目录数 | **30**（+ reports/ 根级散落文件） |
| Git 跟踪文件 | **179**（根级 65 + 子目录 114，分布在 24 个子目录） |
| Git 忽略文件 | **1,771** |
| 空目录 | **4** 个 |

> **关键事实**: `.gitignore` 的 `reports/*` 规则于 **2026-03-26**（commit `4c1e2171d`）生效。
> 6 个白名单例外（`completion`、`governance`、`monitoring`、`phase`、`reviews`、`tests`）仅控制**新文件是否被跟踪**，无法移除**已提交的文件**。
> 因此归档执行必须区分两种操作：
> - **`git mv`** — 179 份 Git 跟踪文件（否则 Git 检测为删除+新增，丢失历史）
> - **普通 `mv`** — 1,771 份 .gitignore 忽略文件

## 2. 分类方案（全部归档，无保留 Tier）

所有 reports/ 内容均为一次性产物（时序门禁快照、HTML 覆盖率、阶段完成证明），**全部迁移至 `docs/archive/reports/`**。不再区分"Tier 1 / Tier 2"，统一按内容类型归档。

### 2.1 覆盖率家族（949 份）

| 来源目录 | 文件数 | 产物类型 |
|----------|--------|----------|
| `reports/coverage/` | 317 | HTML 覆盖率报告（hash 命名） |
| `reports/database_cov/` | 301 | HTML 覆盖率报告 |
| `reports/calculator_coverage/` | 301 | HTML 覆盖率报告 |
| `reports/simple_calculator_full_coverage/` | 10 | 覆盖率报告 |
| `reports/data_classification_coverage/` | 10 | 覆盖率报告 |
| `reports/config_loader_coverage/` | 10 | 覆盖率报告 |
| **小计** | **949** | |

→ 归档目标：`docs/archive/reports/coverage/{来源目录名}/`

### 2.2 分析报告 / 运行时门禁（826 份）

| 来源目录 | 文件数 | 产物类型 | 嵌套深度 |
|----------|--------|----------|----------|
| `reports/analysis/docker-runtime-smoke/` | 233 | Docker 冒烟运行时输出 | 1 层（时间戳子目录） |
| `reports/analysis/runtime-delivery-gate/` | 154 | 交付门禁时序记录 | **2 层**（时间戳 → runtime-ci-bundle 等） |
| `reports/analysis/api-performance-gate/` | 143 | API 性能门禁时序记录 | 1 层 |
| `reports/analysis/api-monitoring-auth-gate/` | 100 | 监控鉴权门禁记录 | 1 层 |
| `reports/analysis/frontend-runtime-gate/` | 81 | 前端运行时门禁时序记录 | 1 层 |
| `reports/analysis/runtime-quality-summary/` | 35 | 运行时质量摘要 | 1 层（含 1 个空子目录） |
| `reports/analysis/`（根级散落） | 78 | 各类分析报告（.md） | — |
| `reports/analysis/typescript-extension-validation/` | 2 | TS 扩展验证 | — |
| **小计** | **826** | | |

→ 归档目标：`docs/archive/reports/analysis-gates/{来源目录名}/`
> 注意：保留原始嵌套结构（特别是 runtime-delivery-gate 的 2 层时间戳目录），不展平。

### 2.3 根级散落文件（78 份）

| 来源 | 文件数 | 产物类型 |
|------|--------|----------|
| `reports/`（根级） | 78 | 独立 Markdown / JSON / HTML 报告 |

> 其中 65 份 Git 跟踪（`AI_Developer_Onboarding_Guide.md`、安全扫描 JSON、阶段完成报告等），13 份 Git 忽略。

→ 归档目标：`docs/archive/reports/root-level/`

### 2.4 遗留子目录报告（97 份）

| 来源目录 | 文件数 | 备注 |
|----------|--------|------|
| `reports/governance/` | 21 | 含 1 个 `.gitkeep` |
| `reports/compliance/` | 9 | |
| `reports/plans/` | 7 | |
| `reports/structure-baseline/` | 5 | |
| `reports/performance/` | 5 | |
| `reports/phase7_monitoring/` | 4 | |
| `reports/phase/` | 4 | |
| `reports/security/` | 4 | 含嵌套 `hardcoding/` 子目录（保留结构） |
| `reports/logs/` | 4 | |
| `reports/type_check/` | 4 | |
| `reports/tests/` | 4 | |
| `reports/completion/` | 4 | |
| `reports/monitoring/` | 3 | |
| `reports/debug/` | 3 | |
| `reports/reviews/` | 3 | |
| `reports/quant/` | 2 | |
| `reports/integration/` | 2 | |
| `reports/bugs/` | 2 | |
| `reports/data_cleaning/` | 2 | |
| `reports/troubleshooting/` | 2 | |
| `reports/unit/` | 2 | |
| `reports/cli/` | 1 | 含 `INDEX.md` |
| `reports/playwright-cli/` | 0 | **空目录** |
| **小计** | **97** | |

→ 归档目标：`docs/archive/reports/legacy-reports/{来源目录名}/`
> `security/` 保留 `hardcoding/` 嵌套结构，展平会丢失语义。

---

## 3. 归档目录结构（目标态）

```
docs/archive/reports/
├── coverage/                           # 覆盖率家族（949）
│   ├── root/
│   ├── database/
│   ├── calculator/
│   ├── simple-calculator-full/
│   ├── data-classification/
│   └── config-loader/
├── analysis-gates/                     # 运行时/交付/性能门禁（826）
│   ├── docker-runtime-smoke/
│   ├── runtime-delivery-gate/
│   ├── api-performance-gate/
│   ├── api-monitoring-auth-gate/
│   ├── frontend-runtime-gate/
│   ├── runtime-quality-summary/
│   ├── typescript-extension-validation/
│   └── root-analysis-reports/          # 原 analysis/ 根级 78 份
├── root-level/                         # reports/ 根级散落（78）
├── legacy-reports/                     # 遗留子目录（97）
│   ├── governance/（含 .gitkeep）
│   ├── compliance/
│   ├── plans/
│   ├── structure-baseline/
│   ├── performance/
│   ├── phase7_monitoring/
│   ├── phase/
│   ├── security/hardcoding/            # 保留嵌套
│   ├── logs/
│   ├── type_check/
│   ├── tests/
│   ├── completion/
│   ├── monitoring/
│   ├── debug/
│   ├── reviews/
│   ├── quant/
│   ├── integration/
│   ├── bugs/
│   ├── data_cleaning/
│   ├── troubleshooting/
│   ├── unit/
│   └── cli/（含 INDEX.md）
└── README.md                           # 归档索引（来源、日期、总数 1950）
```

---

## 4. 执行步骤（审批后）

### 4.1 创建归档目录
```bash
mkdir -p docs/archive/reports/{coverage/{root,database,calculator,simple-calculator-full,data-classification,config-loader},analysis-gates/{docker-runtime-smoke,runtime-delivery-gate,api-performance-gate,api-monitoring-auth-gate,frontend-runtime-gate,runtime-quality-summary,typescript-extension-validation,root-analysis-reports},root-level,legacy-reports/{governance,compliance,plans,structure-baseline,performance,phase7_monitoring,phase,security/hardcoding,logs,type_check,tests,completion,monitoring,debug,reviews,quant,integration,bugs,data_cleaning,troubleshooting,unit,cli}}
```

### 4.2 迁移文件（按目录分批）

对每个来源目录，按 Git 跟踪状态分别处理：

```bash
# --- Git 跟踪文件：用 git mv 保留历史 ---
# 示例：governance（21 份跟踪）
git mv reports/governance/* docs/archive/reports/legacy-reports/governance/

# 示例：根级跟踪文件（65 份，需逐个过滤）
git ls-files 'reports/*' | grep -v '/' | while read f; do
  git mv "$f" docs/archive/reports/root-level/
done

# --- Git 忽略文件：普通 mv ---
# 示例：coverage（317 份，全部忽略）
mv reports/coverage/* docs/archive/reports/coverage/root/

# 示例：analysis 子目录（各时间戳批次）
mv reports/analysis/docker-runtime-smoke/* docs/archive/reports/analysis-gates/docker-runtime-smoke/
```

> **分批策略**: 按 §2 的 4 个类别分 4 批提交，每批独立 commit，便于 `git revert`。
> 每批内先 `git mv` 跟踪文件，再 `mv` 忽略文件，最后 `rmdir` 空目录。

### 4.3 处理 4 个空目录

```bash
rmdir reports/playwright-cli
rmdir reports/analysis/runtime-ci-bundle-combined-local
rmdir reports/analysis/runtime-quality-summary-ci-local
rmdir reports/analysis/runtime-quality-summary/20260419-202010
```

### 4.4 被清空的子目录原位留重定向 README

每个被清空的 reports/ 子目录留一份 `README.md`：

```markdown
> **⚠️ 已归档（2026-07-12）**
> 本目录内容已归档至 [docs/archive/reports/](../../../archive/reports/)。
> 本文件仅作路径兼容保留，不再维护。
```

> 30 个子目录 + 根级留 31 份 README；空目录留 1 份 README（不保留空壳）。

### 4.5 更新 .gitignore

归档后，`reports/` 仅含 README 和空目录残留。移除对应白名单例外规则：

```diff
-!reports/completion/
-!reports/completion/**
-!reports/governance/
-!reports/governance/**
-!reports/monitoring/
-!reports/monitoring/**
-!reports/phase/
-!reports/phase/**
-!reports/reviews/
-!reports/reviews/**
-!reports/tests/
-!reports/tests/**
```

### 4.6 更新索引与链接

```bash
# 更新 docs/INDEX.md / CORE.md（移除或更新对已归档报告的引用）
# 运行文档索引器
python scripts/tools/docs_indexer.py --categories
```

---

## 5. 回滚方案

- 归档操作是移动而非删除，内容零损失
- 每批独立提交，回滚 = `git revert <commit>`
- Git 跟踪文件用 `git mv`，历史连续；回滚可完整恢复

---

## 6. 验收核对项

| # | 核对项 | 期望值 |
|---|--------|--------|
| 1 | `reports/` 子目录数（含 README 空壳） | 30（原目录保留 README 标记） |
| 2 | `docs/archive/reports/` 归档文件总数 | **1,950** |
| 3 | 每个被清空的 reports/ 子目录含重定向 README | 30 份 |
| 4 | 4 个空目录已移除 | 0 个空目录残留 |
| 5 | .gitignore 白名单例外已清理 | 无 `!reports/xxx/` 条目 |
| 6 | docs/INDEX.md / CORE.md 链接已更新 | 无断链 |
| 7 | `python scripts/tools/docs_indexer.py --categories` | 运行成功 |
| 8 | 全量操作在独立提交中 | 可 `git revert` |
| 9 | 3 个原空目录已移除 | playwright-cli 等已删除 |

---

## 7. 风险与注意

| 风险 | 缓解 |
|------|------|
| 误判"一次性"为"活跃文档" | 活跃文档 = 跨阶段持续引用；本报告产物均为时序快照/CI hash 输出，无跨阶段引用 |
| 路径硬编码引用断裂 | 重定向 README 提供路径映射；下一步 Phase 4 做全仓库链接清理 |
| 大批量 git mv 冲突 | 分目录分批提交；先 git mv 跟踪文件，再 mv 忽略文件 |
| 嵌套结构丢失 | analysis/security 的嵌套时间戳目录原样保留，不展平 |
