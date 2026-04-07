# Code Inventory 20260223 Large File Splitting Implementation Plan

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、任务方案或执行矩阵，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值和时间线如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 基于 `reports/code_inventory_report_20260223.md`，完成可拆分大文件治理，优先消除当前扫描范围内真实可拆分的 >1000 行文件。

**Architecture:** 采用“薄入口 + 分域模块”拆分策略。保持 `scripts/tests/web-usability-runner.js` 对外入口与行为不变，把 `runner-core.js` 中环境检查、功能/性能/安全/可用性/数据质量、评分与报告渲染拆到独立模块；先建立失败的 guardrail，再做增量拆分，最后回归验证。

**Tech Stack:** Node.js (CommonJS), Python `pytest`, `rg`/`wc` 行数扫描, 现有 `scripts/tests/test_large_file_top5_guardrail.py`。

---

## 1. 输入结论（来自报告与复核）

- 报告 `reports/code_inventory_report_20260223.md` 显示：超过阈值文件 61 个（阈值 1000 行）。
- 报告 Top20 主要集中在 `scripts/dev/**` 第三方工件（Playwright/Puppeteer/jsdom/Babel），不建议拆分。
- 按报告扫描范围 `src scripts web/backend/app` 复核并排除 `scripts/dev/**` 后，当前 >1000 行的可拆分业务文件为：

| 行数 | 文件 |
|---|---|
| 1289 | `scripts/tests/web-usability/runner-core.js` |

---

## 2. 已检索的大文件拆分 MD 文档

1. `architecture/standards/large_file_splitting_principles.md`
2. `reports/plans/large_file_splitting_workplan.md`
3. `reports/compliance/large_file_splitting_report.md`
4. `reports/compliance/top5_large_file_splitting_report.md`
5. `reports/compliance/exceptions/large_files.md`
6. `reports/compliance/exceptions/marginal_python_files.md`
7. `docs/plans/2026-02-16-large-file-splitting-top5-implementation-plan.md`
8. `CLAUDE.md`（第 5 节：大文件拆分规则与例外）

---

## 3. 具体拆分方案（审批后执行）

### Task 1: 建立 `runner-core.js` Guardrail（先红后绿）

**Files:**
- Modify: `scripts/tests/test_large_file_top5_guardrail.py`
- Test: `scripts/tests/test_large_file_top5_guardrail.py`

**Step 1: 写失败用例**

- 新增 `scripts/tests/web-usability/runner-core.js` 行数断言（目标 `<=500`，与拆分原则对齐）。

**Step 2: 运行用例确认失败**

Run: `pytest scripts/tests/test_large_file_top5_guardrail.py -v`  
Expected: FAIL，提示 `runner-core.js` 超过阈值。

**Step 3: 提交 guardrail 变更（仅测试）**

```bash
git add scripts/tests/test_large_file_top5_guardrail.py
git commit -m "test: add guardrail for web-usability runner core file size"
```

---

### Task 2: 按职责拆分 `runner-core.js`（阶段一：测试执行域）

**Files:**
- Create: `scripts/tests/web-usability/core/environment.js`
- Create: `scripts/tests/web-usability/core/functional.js`
- Create: `scripts/tests/web-usability/core/performance.js`
- Create: `scripts/tests/web-usability/core/security.js`
- Create: `scripts/tests/web-usability/core/usability.js`
- Create: `scripts/tests/web-usability/core/data-quality.js`
- Modify: `scripts/tests/web-usability/runner-core.js`
- Test: `scripts/tests/web-usability-runner.js`

**Step 1: 拆分方法到模块**

- 从 `runner-core.js` 提取以下方法到对应模块并导出纯函数：
  - 环境：`checkEnvironment`, `checkDatabaseConnection`
  - 功能：`runFunctionalTests`, `executePlaywrightTests`, `parsePlaywrightResults`, `executeAPITests`
  - 性能：`runPerformanceTests`, `runLighthouseTest`, `runAPIPerformanceTest`, `runLoadTest`, `runResourceTest`
  - 安全：`runSecurityTests`, `runVulnerabilityScan`, `runAuthenticationTests`, `runInputValidationTests`
  - 可用性：`runUsabilityTests`, `runResponsiveTests`, `runAccessibilityTests`, `runInteractionTests`
  - 数据质量：`runDataQualityTests`, `runDataAccuracyTests`, `runDataRealtimeTests`, `runDataIntegrityTests`

**Step 2: 保持入口兼容**

- `WebUsabilityTestRunner` 类保留 `runAllTests()` 和对外导出不变。
- `scripts/tests/web-usability-runner.js` 无需改调用方式。

**Step 3: 运行基础回归**

Run: `node -e "const R=require('./scripts/tests/web-usability-runner'); console.log(typeof R)"`  
Expected: 输出 `function`（模块可加载）。

---

### Task 3: 拆分评分与报告渲染（阶段二：报告域）

**Files:**
- Create: `scripts/tests/web-usability/core/scoring.js`
- Create: `scripts/tests/web-usability/core/report-html.js`
- Modify: `scripts/tests/web-usability/runner-core.js`
- Test: `scripts/tests/web-usability-runner.js`

**Step 1: 提取评分逻辑**

- 提取并模块化：
  - `calculateSummary`
  - `evaluatePassingCriteria`
  - `calculateFunctionalPassRate`
  - `calculatePerformanceScore`
  - `calculateSecurityScore`
  - `calculateUsabilityScore`
  - `calculateDataQualityScore`

**Step 2: 提取 HTML 渲染逻辑**

- 提取并模块化：
  - `generateHTMLReport`
  - `renderFunctionalResults`
  - `renderPerformanceResults`
  - `renderSecurityResults`
  - `renderUsabilityResults`
  - `renderDataQualityResults`

**Step 3: 行数目标达成**

- `scripts/tests/web-usability/runner-core.js` 降至 `<=500` 行。
- 新增模块单文件不超过 `500` 行。

---

### Task 4: 最终验证与治理文档更新

**Files:**
- Modify: `reports/compliance/exceptions/large_files.md`
- Create: `reports/compliance/web_usability_runner_core_splitting_report_20260223.md`
- Test: `scripts/tests/test_large_file_top5_guardrail.py`

**Step 1: 运行验证**

Run:
- `pytest scripts/tests/test_large_file_top5_guardrail.py -v`
- `rg --files -uu src scripts web/backend/app -g '*.py' -g '*.vue' -g '*.ts' -g '*.tsx' -g '*.js' -g '*.jsx' | grep -Ev '^scripts/dev/' | while read -r f; do l=$(wc -l < \"$f\"); if [ \"$l\" -gt 1000 ]; then echo \"$l $f\"; fi; done`

Expected:
- guardrail PASS
- 无 `scripts/dev/**` 之外的 >1000 行文件输出

**Step 2: 记录非拆分范围**

- 在 `reports/compliance/exceptions/large_files.md` 补充说明：`scripts/dev/**` 为第三方工件，走“例外+定期复核”，不做手工拆分。

**Step 3: 输出执行报告**

- 生成 `reports/compliance/web_usability_runner_core_splitting_report_20260223.md`，包含拆分前后行数、兼容性验证、回归结果。

---

## 4. 风险与回滚

- 风险 1：模块拆分后 `this` 上下文丢失。  
  规避：统一改为显式参数传递（`config`, `testResults`）。
- 风险 2：报告模板拆分后字段引用断裂。  
  规避：保留 JSON 报告字段结构不变，先对 `generateReport` 做快照比对。
- 风险 3：误把第三方工件纳入拆分范围。  
  规避：执行命令统一 `grep -Ev '^scripts/dev/'`，并在例外文档固化。
- 回滚：按任务粒度小步提交，单任务可 `git revert <commit>` 回退，不影响入口脚本。

---

## 5. 审批项

- [ ] 同意按本方案拆分 `scripts/tests/web-usability/runner-core.js`（目标 `<=500` 行）
- [ ] 同意先加 guardrail 再拆分（TDD 顺序）
- [ ] 同意将 `scripts/dev/**` 按第三方工件纳入“例外+复核”，不做手工拆分

