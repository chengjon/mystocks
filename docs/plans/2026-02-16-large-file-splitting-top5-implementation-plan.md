# Top 5 Large Files Splitting Implementation Plan

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、任务方案或执行矩阵，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值和时间线如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Bring the 5 agreed large files into compliance with `architecture/standards/large_file_splitting_principles.md`, while preserving runtime behavior and test stability.

**Architecture:** Use incremental refactor with compatibility entrypoints. Generated type files are handled via generator-first strategy + exception workflow; executable JS/Playwright files are split by responsibility; archived Vue page is handled by exclusion governance first, not forced code churn.

**Tech Stack:** Python 3.12, Vue 3, TypeScript, Playwright, Node.js scripts, OpenSpec governance docs.

---

### Task 1: Baseline + Guardrail Test (TDD Entry)

**Files:**
- Create: `scripts/tests/test_large_file_top5_guardrail.py`
- Modify: `reports/plans/large_file_splitting_backlog.tsv`
- Test: `scripts/tests/test_large_file_top5_guardrail.py`

**Step 1: Write the failing test**

Add file-size assertions for:
- `web/frontend/src/api/types/generated-types.ts` (exception-only)
- `web/frontend/src/api/types/common.ts` (must <= 500 after split)
- `scripts/tests/web-usability-runner.js` (must <= 500 after split)
- `web/frontend/tests/api-automation.spec.js` (must <= 1000 after split)
- `web/frontend/src/views/converted.archive/market-quotes.vue` (must be excluded or archived path documented)

**Step 2: Run test to verify it fails**

Run: `pytest scripts/tests/test_large_file_top5_guardrail.py -v`  
Expected: FAIL for current oversized files.

**Step 3: Mark backlog rows in progress**

Update matching rows in `reports/plans/large_file_splitting_backlog.tsv` from `TODO` to `IN_PROGRESS`.

**Step 4: Run test again**

Run: `pytest scripts/tests/test_large_file_top5_guardrail.py -v`  
Expected: still FAIL (until refactors complete).

**Step 5: Commit**

```bash
git add scripts/tests/test_large_file_top5_guardrail.py reports/plans/large_file_splitting_backlog.tsv
git commit -m "test: add guardrail for top5 large-file splitting targets"
```

---

### Task 2: `generated-types.ts` Exception + Compatibility Entry

**Files:**
- Modify: `scripts/generate_frontend_types.py`
- Modify: `web/frontend/src/api/types/generated-types.ts`
- Create: `reports/compliance/exceptions/large_files.md`
- Test: `web/frontend/src/api/types/index.ts`

**Step 1: Write the failing test**

Extend `scripts/tests/test_large_file_top5_guardrail.py` with:
- Rule: `generated-types.ts` can exceed threshold only if listed in `reports/compliance/exceptions/large_files.md`.
- Rule: exception record must include owner, reason, expiry date, mitigation.

**Step 2: Run test to verify it fails**

Run: `pytest scripts/tests/test_large_file_top5_guardrail.py::test_generated_types_exception_record -v`  
Expected: FAIL because exception record does not exist yet.

**Step 3: Implement minimal solution**

- In `scripts/generate_frontend_types.py`, generate `generated-types.ts` as compatibility barrel (re-export only), not full model dump.
- Keep old import path stable (`@/api/types/generated-types`).
- Create `reports/compliance/exceptions/large_files.md` and add exception entry with explicit expiry/review cycle.

**Step 4: Run tests**

Run:
- `pytest scripts/tests/test_large_file_top5_guardrail.py -v`
- `cd web/frontend && npm run type-check`

Expected:
- guardrail exception case PASS
- frontend type-check PASS (or documented existing baseline debt only)

**Step 5: Commit**

```bash
git add scripts/generate_frontend_types.py web/frontend/src/api/types/generated-types.ts reports/compliance/exceptions/large_files.md scripts/tests/test_large_file_top5_guardrail.py
git commit -m "refactor: convert generated-types to compatibility entry with governed exception"
```

---

### Task 3: Split `common.ts` by Domain/Concern (Wave 3 P0)

**Files:**
- Create: `web/frontend/src/api/types/common/index.ts`
- Create: `web/frontend/src/api/types/common/api.ts`
- Create: `web/frontend/src/api/types/common/alert.ts`
- Create: `web/frontend/src/api/types/common/algorithm.ts`
- Create: `web/frontend/src/api/types/common/market.ts`
- Modify: `scripts/generate_frontend_types.py`
- Modify: `web/frontend/src/api/types/common.ts` (convert to barrel export)
- Test: `web/frontend/src/api/types/index.ts`

**Step 1: Write the failing test**

Add guardrail test asserting:
- `common.ts` <= 500 lines.
- no single generated `web/frontend/src/api/types/common/*.ts` file > 500 lines.

**Step 2: Run test to verify it fails**

Run: `pytest scripts/tests/test_large_file_top5_guardrail.py::test_common_types_split_threshold -v`  
Expected: FAIL on current `common.ts`.

**Step 3: Write minimal implementation**

- Add chunk/scope split strategy in `scripts/generate_frontend_types.py` for common-domain models.
- Output multiple files under `web/frontend/src/api/types/common/`.
- Keep `web/frontend/src/api/types/common.ts` as barrel:
  - `export * from './common/index'`
- Keep external import compatibility for existing files.

**Step 4: Run tests**

Run:
- `python scripts/generate_frontend_types.py`
- `pytest scripts/tests/test_large_file_top5_guardrail.py -v`
- `cd web/frontend && npm run type-check`

Expected:
- split guardrail PASS
- type-check PASS (or baseline-only debt)

**Step 5: Commit**

```bash
git add scripts/generate_frontend_types.py web/frontend/src/api/types/common.ts web/frontend/src/api/types/common/ scripts/tests/test_large_file_top5_guardrail.py
git commit -m "refactor: split common frontend types into modular generated files"
```

---

### Task 4: Split `web-usability-runner.js` by Responsibility

**Files:**
- Create: `scripts/tests/web-usability/runner.js`
- Create: `scripts/tests/web-usability/environment.js`
- Create: `scripts/tests/web-usability/functional.js`
- Create: `scripts/tests/web-usability/performance.js`
- Create: `scripts/tests/web-usability/security.js`
- Create: `scripts/tests/web-usability/usability.js`
- Create: `scripts/tests/web-usability/data-quality.js`
- Create: `scripts/tests/web-usability/report.js`
- Modify: `scripts/tests/web-usability-runner.js` (thin entry)
- Test: `scripts/tests/web-usability-runner.js`

**Step 1: Write the failing test**

Add guardrail assertion for `scripts/tests/web-usability-runner.js <= 500`.

**Step 2: Run test to verify it fails**

Run: `pytest scripts/tests/test_large_file_top5_guardrail.py::test_web_usability_runner_size -v`  
Expected: FAIL.

**Step 3: Write minimal implementation**

- Move class methods into dedicated modules by capability.
- Keep CLI behavior unchanged:
  - `node scripts/tests/web-usability-runner.js`
- Entry file only wires config + orchestrates imports.

**Step 4: Run tests**

Run:
- `node scripts/tests/web-usability-runner.js --help || true`
- `pytest scripts/tests/test_large_file_top5_guardrail.py -v`

Expected:
- no module resolution errors
- guardrail PASS for this target

**Step 5: Commit**

```bash
git add scripts/tests/web-usability-runner.js scripts/tests/web-usability/ scripts/tests/test_large_file_top5_guardrail.py
git commit -m "refactor: split web usability runner into suite modules"
```

---

### Task 5: Split `api-automation.spec.js` into Focused Specs + Helpers

**Files:**
- Create: `web/frontend/tests/api-automation/helpers/openapi.js`
- Create: `web/frontend/tests/api-automation/helpers/endpoint-test.js`
- Create: `web/frontend/tests/api-automation/helpers/report.js`
- Create: `web/frontend/tests/api-automation.smoke.spec.js`
- Create: `web/frontend/tests/api-automation.endpoints.spec.js`
- Create: `web/frontend/tests/api-automation.tags.spec.js`
- Modify: `web/frontend/tests/api-automation.spec.js` (reduce to compatibility or remove)
- Test: `web/frontend/tests/api-automation*.spec.js`

**Step 1: Write the failing test**

Add guardrail assertion for `web/frontend/tests/api-automation.spec.js <= 1000`.

**Step 2: Run test to verify it fails**

Run: `pytest scripts/tests/test_large_file_top5_guardrail.py::test_api_automation_spec_size -v`  
Expected: FAIL.

**Step 3: Write minimal implementation**

- Extract OpenAPI fetch + endpoint extraction + endpoint test + report generation to helper modules.
- Keep test semantics:
  - smoke validation
  - full endpoint traversal
  - tag-group traversal

**Step 4: Run tests**

Run:
- `cd web/frontend && npm run test:e2e -- --list`
- `pytest scripts/tests/test_large_file_top5_guardrail.py -v`

Expected:
- Playwright discovers new specs
- guardrail PASS for this target

**Step 5: Commit**

```bash
git add web/frontend/tests/api-automation* web/frontend/tests/api-automation/helpers scripts/tests/test_large_file_top5_guardrail.py
git commit -m "test: split API automation Playwright spec into focused suites"
```

---

### Task 6: Handle `converted.archive/market-quotes.vue` via Exclusion Governance

**Files:**
- Modify: `reports/plans/large_file_splitting_backlog.tsv`
- Modify: `reports/compliance/exceptions/large_files.md`
- Modify: `web/frontend/src/views/converted.archive/market-quotes.vue` (optional header note only)
- Test: `scripts/tests/test_large_file_top5_guardrail.py`

**Step 1: Write the failing test**

Add guardrail assertion:
- files under `web/frontend/src/views/converted.archive/**` must be marked `EXCLUDED` in backlog and exception/governance notes.

**Step 2: Run test to verify it fails**

Run: `pytest scripts/tests/test_large_file_top5_guardrail.py::test_converted_archive_is_governed -v`  
Expected: FAIL if not marked.

**Step 3: Write minimal implementation**

- Mark this file as `EXCLUDED` in backlog with reason: archive path out-of-scope.
- Add governance note in `reports/compliance/exceptions/large_files.md`.
- Do not split unless product confirms this page will be reactivated in active router.

**Step 4: Run tests**

Run: `pytest scripts/tests/test_large_file_top5_guardrail.py -v`  
Expected: PASS for archive-governance rule.

**Step 5: Commit**

```bash
git add reports/plans/large_file_splitting_backlog.tsv reports/compliance/exceptions/large_files.md scripts/tests/test_large_file_top5_guardrail.py
git commit -m "docs: govern converted archive oversized page as excluded scope"
```

---

### Task 7: Final Verification + Closeout

**Files:**
- Modify: `reports/plans/large_file_splitting_backlog.tsv`
- Create: `reports/compliance/top5_large_file_splitting_report.md`
- Test: frontend/backend quality gates

**Step 1: Run full required checks**

Run:
- `pytest scripts/tests/test_large_file_top5_guardrail.py -v`
- `cd web/frontend && npm run lint`
- `cd web/frontend && npm run type-check`
- `cd web/frontend && npm run test:e2e -- --list`

**Step 2: Verify no circular deps (frontend)**

Run: `madge --circular --extensions js,ts,vue web/frontend/src`

**Step 3: Update backlog statuses**

Set statuses for all 5 targets to `DONE` or `EXCLUDED` (with reason).

**Step 4: Write closeout report**

Create `reports/compliance/top5_large_file_splitting_report.md`:
- before/after line counts
- exception records
- verification command outputs summary

**Step 5: Commit**

```bash
git add reports/plans/large_file_splitting_backlog.tsv reports/compliance/top5_large_file_splitting_report.md
git commit -m "docs: close top5 large-file splitting execution and verification"
```

---

## Notes

- Follow `@superpowers:test-driven-development` per task (failing check first).
- Before claiming completion, run `@superpowers:verification-before-completion`.
- If implementing in current workspace, preserve existing unrelated changes; do not revert user edits.
