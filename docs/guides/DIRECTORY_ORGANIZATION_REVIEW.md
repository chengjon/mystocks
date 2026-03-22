# 两文档一致性审核报告

**审核文档**：
- `docs/standards/DIRECTORY_AND_FILE_ORGANIZATION_RULES.md`（通用规则，v1.0，2026-03-22）
- `docs/guides/DIRECTORY_ORGANIZATION_PLAN.md`（项目整理方案，v2.0，2026-03-22）

**审核日期**：2026-03-22
**审核人**：AI Reviewer

---

## 一、高度一致的部分

| 方面 | 结论 |
|------|------|
| 核心目录结构哲学 | 两文档均遵循九大顶层目录模型（src, tests, scripts, config, docs, architecture, reports, archive, data） |
| 归档目录重复问题识别 | `archive/` + `archived/` 双目录问题两边一致，合并方向一致 |
| Git 操作原则 | 均要求使用 `git mv` 保留历史，禁用普通 `mv` |
| scripts/ 三分类 | runtime/、database/、dev/ 三者完全对齐 |
| 文件放置决策树 | 关键词 → 目录的映射规则两文档一致 |
| 禁止操作意识 | 均强调禁止在根目录创建非清单文件 |

---

## 二、发现的关键冲突与问题

### 🔴 冲突 1：工具链配置文件位置

| 文件 | 通用规则 (Doc1) | 项目方案 (Doc2) | 实际情况 |
|------|-----------------|-----------------|----------|
| `playwright.config.*` | ✅ 允许保留根目录 | → `config/playwright/` | `config/playwright/` ✅ 已存在 |
| `pm2.config.js` | ✅ 允许保留根目录 | → `config/pm2/` | `config/pm2/` ✅ 已存在 |
| `vitest.config.mts` | ✅ 允许保留根目录 | 未提及 | 根目录存在 |

**分析**：Doc2 的判断更合理——工具链配置收敛到 `config/` 符合"根目录极简主义"原则。但 Doc1 附录 A 的模板里依然将这些列在根目录，造成规范与方案不一致。

**建议**：Doc1 应明确"工具链配置**建议**收敛到 `config/` 子目录"，而不是放在"允许清单"里。

---

### 🔴 冲突 2：Python line-length 标准

- **Doc1 正文**：`line-length: 120`（第135行）
- **Doc1 表格**（附录 B）未提及此参数
- **Doc2** 依赖 Doc1 但未单独核查

**实际情况**：`pyproject.toml` 确认 `line-length = 120`，与 Doc1 一致。

**建议**：在 Doc1 的"格式化"一节中明确说明 `line-length = 120`，避免读者误以为用 Black 默认值 88。

---

### 🟡 问题 3：测试文件位置的矛盾

- **Doc1**：`tests/` 作为独立顶层目录（第74行），测试文件命名 `test_*.py`、`*_test.py`
- **Doc2 Phase 3**（第352行）：`scripts/tests/` → `tests/`

但 Doc1 的 `scripts/` 分类表格（第96-118行）中并未将 `scripts/tests/` 列为合法子目录——说明 Doc1 的设计本意就是测试文件**不在** `scripts/` 下，而是直接在 `tests/` 下。

**问题**：当前仓库中 `scripts/tests/` 存在，这与 Doc1 规范矛盾。Doc2 Phase 3 应将此作为 **P0 优先级** 迁移（而非 P2）。

---

### 🟡 问题 4：文档索引维护要求缺失

- **Doc1 第九章**明确要求每个主要目录维护 `INDEX.md`
- **Doc2 验收标准**（第七章）**未纳入此要求**

---

### 🟡 问题 5：禁止移动清单的遗漏

Doc2 第五章的"禁止移动清单"未包含：
- `monitoring-stack/`（监控栈配置目录）
- `gpu_api_system/`（GPU 加速系统）

这两个目录在 Doc1 的九大顶层目录框架外，但实际存在且有独立功能，方案应对其明确标注。

---

## 三、Doc2 方案的优缺点

**优点**：
1. 问题诊断详实，有具体的文件清单和映射表
2. 分 Phase 执行计划合理，降低了单次变更风险
3. 禁止操作清单和删除审批清单设计合理
4. 回滚策略设计完备

**不足**：
1. Phase 3（scripts/ 整理）标注为 P2，但涉及测试文件迁移应为 P0
2. 时间估算（Phase 1: 4h）偏乐观，docs/ 含 40+ 子目录合并实际可能需要 6-8h
3. 未明确说明 Phase 执行顺序——建议明确"Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4"的串行依赖关系

---

## 四、审核结论与推荐行动

| 项目 | 状态 |
|------|------|
| 两文档基础框架一致性 | ✅ 通过 |
| Doc1 规范的可执行性 | ⚠️ 需修订（工具链配置位置、line-length 显式声明） |
| Doc2 方案的完整性 | ⚠️ 需补强（测试文件优先级、禁止清单补全） |
| 实际落地情况 | 部分 Phase 已执行（config/ 已收敛 playwright/pm2） |

### 推荐行动

| 优先级 | 行动项 | 责任文档 |
|--------|--------|----------|
| P1 | 在 Doc1 "根目录允许清单"中增加注释：工具链配置建议收敛到 `config/` | `DIRECTORY_AND_FILE_ORGANIZATION_RULES.md` |
| P1 | 在 Doc1 "格式化"节中显式声明 `line-length = 120` | `DIRECTORY_AND_FILE_ORGANIZATION_RULES.md` |
| P1 | 将 Doc2 Phase 3 测试文件迁移从 P2 提升为 P0 | `DIRECTORY_ORGANIZATION_PLAN.md` |
| P2 | 在 Doc2 验收标准中补入索引维护检查项 | `DIRECTORY_ORGANIZATION_PLAN.md` |
| P2 | 补充禁止移动清单：`monitoring-stack/`、`gpu_api_system/` | `DIRECTORY_ORGANIZATION_PLAN.md` |
| P3 | 修正 Phase 时间估算（Phase 1 从 4h → 6-8h） | `DIRECTORY_ORGANIZATION_PLAN.md` |
| P3 | 明确 Phase 串行执行顺序（0→1→2→3→4） | `DIRECTORY_ORGANIZATION_PLAN.md` |
