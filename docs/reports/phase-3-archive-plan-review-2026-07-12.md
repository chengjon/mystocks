# Phase 3 归档计划审核报告

> **审核工具**: review2md + 全量代码库审计
> **审核目标**: `docs/plans/phase-3-archive-plan-2026-07-12.md`
> **审核日期**: 2026-07-12
> **审核人**: CodeWhale
> **状态**: ❌ 需修正（9 项问题待修复）

---

## 一、review2md 文档问题（4 项）

### 1.1 ⚠️ Tier 2 表格内容矛盾

**位置**: §2.2 表格（第 90-95 行）
**问题**: 表格中 5 行目录标注"↓ 已归入 Tier 1"但仍列在 Tier 2 表格下，后续建议又说"一并归入 Tier 1"，造成混淆。
**建议**: 删除已归入 Tier 1 的表格行，或以注释形式说明已被重新分类。

### 1.2 ❌ 目录路径遗漏前缀

**位置**: §2.2 第 72 行
**问题**: 列出 `reviews/` 但上下文均为 `reports/` 下的子目录，此处缺少 `reports/` 前缀。
**建议**: 修正为 `reports/reviews/`。

### 1.3 ⚠️ 归档目标写法不统一

**位置**: §2.2 第 82 行
**问题**: 归档目标写为 `docs/archive/reports/legacy-reports/{子目录名}/` 使用变量但未展开。
**建议**: 明确列出所有子目录名称或加注占位符说明。

### 1.4 ℹ️ 归档索引 README 路径缺失

**位置**: §3 第 146 行
**问题**: 归档目录结构图末尾有 `└── README.md` 但未说明具体路径和内容要求。
**建议**: 在步骤中明确创建 `docs/archive/reports/README.md`（路径 `docs/archive/reports/README.md`）。

---

## 二、代码库审计数据偏差（5 项）

### 2.1 🔴 子目录数：31 → 30

| 统计项 | 计划值 | 实际值 |
|-------|--------|--------|
| `reports/` 直接子目录 | 31 | **30** |

实际子目录清单（按 `ls -d reports/*/` 计数）：

```
analysis/  bugs/  calculator_coverage/  cli/  completion/  compliance/
config_loader_coverage/  coverage/  data_classification_coverage/
data_cleaning/  database_cov/  debug/  governance/  integration/
logs/  monitoring/  performance/  phase/  phase7_monitoring/  plans/
playwright-cli/  quant/  reviews/  security/
simple_calculator_full_coverage/  structure-baseline/  tests/
troubleshooting/  type_check/  unit/
```

=> 共计 30 个直接子目录。

### 2.2 🔴 Git 跟踪文件：39 → 179

| 统计项 | 计划值 | 实际值 |
|-------|--------|--------|
| Git 跟踪总数 | 39（6 白名单子目录） | **179**（**23 子目录 + 65 根级文件**）|
| 白名单外跟踪 | — | **141 份** |

**根因分析**：
`.gitignore` 中 `reports/*` 规则在 2026-03-25 左右生效。6 个白名单例外（`completion`、`governance`、`monitoring`、`phase`、`reviews`、`tests`）只控制**新文件是否被跟踪**，无法移除**已提交的文件**。

已跟踪文件分布（按子目录）：

| 目录 | 跟踪数 | 备注 |
|------|--------|------|
| `reports/` 根级 | 65 | 独立 Markdown/JSON 报告 |
| `reports/analysis/` | 20 | 分析产物 |
| `reports/governance/` | 21 | 白名单 ✅ |
| `reports/compliance/` | 8 | 非白名单 |
| `reports/plans/` | 7 | 非白名单 |
| `reports/structure-baseline/` | 5 | 非白名单 |
| `reports/` 其他 16 子目录 | 53 | 非白名单 |
| **合计** | **179** | |

**影响**: 归档时需区分两种操作：
- **`git mv`**：用于 179 份 Git 跟踪文件（否则 Git 检测为删除）
- **普通 `mv`**：用于 1,771 份 .gitignore 忽略文件

### 2.3 🟡 空子目录：3 → 4

| 计划 | 实际 |
|------|------|
| 3 个 | **4 个**（1 个顶层 + 3 个嵌套） |

实际空目录清单：

```
reports/playwright-cli/                                    # 顶层空目录
reports/analysis/runtime-ci-bundle-combined-local/         # 嵌套空目录
reports/analysis/runtime-quality-summary-ci-local/          # 嵌套空目录
reports/analysis/runtime-quality-summary/20260419-202010/  # 嵌套空目录
```

### 2.4 🟡 `reports/security/` 文件分布

| 统计 | 计划 | 实际 |
|------|------|------|
| 根级文件 | — | 1（`README.md`）|
| 嵌套子目录 | — | 3（`hardcoding/*.md`）|
| 合计 | 4 | **4**（计数正确，但未反映嵌套结构）|

归档时需确认是保留子目录结构还是展平。

### 2.5 🟢 分析门禁子目录的文件深度

**结论**: 总文件数 826 ✅ 正确。

但文件分布为 **2-3 层嵌套**（时间戳子目录），非计划暗示的"根级 78 + 直接子目录"。每个门禁子目录（如 `docker-runtime-smoke/`）内部有 10-40 个 `20260419-181541/` 格式的子目录，各含多个运行时文件。

---

## 三、汇总

| 类别 | 问题数 | 严重度 |
|------|--------|--------|
| review2md 文档问题 | 4 | 1 ❌ + 2 ⚠️ + 1 ℹ️ |
| 代码库数据偏差 | 5 | 2 🔴 + 2 🟡 + 1 🟢 |
| **总计** | **9** | |

### 优先修复建议

| 优先级 | 问题 | 操作 |
|--------|------|------|
| P0 | §2.2 Tier 2 表格 | 删除已归入 Tier 1 的 5 行，补充白名单外 141 份文件的处理方案 |
| P0 | Git 跟踪文件 179 份 | 归档步骤增加 `git mv` 分支说明 |
| P1 | `reviews/` 缺前缀 | 补全 `reports/reviews/` |
| P1 | 子目录数 31→30 | 修正为 30 |
| P2 | 空目录 3→4 | 更新为 4 个并列出具体路径 |
| P2 | 归档目标格式 | 统一 `{子目录名}/` 写法 |
| P3 | 归档 README | 在步骤中明确路径 `docs/archive/reports/README.md` |

---

*本报告由 review2md 工具自动生成 + 人工代码审计补充*
