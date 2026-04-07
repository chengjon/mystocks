# Guides Onboarding Migration Implementation Plan

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move `docs/guides/DEVELOPER_GUIDE.md` and `docs/guides/USER_GUIDE.md` into a dedicated `docs/guides/onboarding/` family without breaking hygiene tests, guide indices, or active references.

**Architecture:** Treat these two documents as onboarding entrypoints rather than generic root guides. Keep the change narrow: update tests first, move only the two files, regenerate `docs`/`guides` indexes, create an `onboarding/INDEX.md`, and patch the curated cleanup snapshot plus a small set of active reference docs that still point at the old root paths.

**Tech Stack:** Markdown docs, pytest hygiene tests, `scripts/dev/tools/docs_indexer.py`, directory structure governance checks.

---

### Task 1: Lock Expected Behavior In Tests

**Files:**
- Modify: `tests/unit/scripts/test_repository_hygiene_paths.py`

- [ ] **Step 1: Write the failing test**

Update existing assertions so `DEVELOPER_GUIDE.md` and `USER_GUIDE.md` are expected under `docs/guides/onboarding/`, and add a focused onboarding-family convergence test.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/scripts/test_repository_hygiene_paths.py -q --no-cov -o tdd_guard_project_root=/opt/claude/mystocks_spec --timing-file=/tmp/test_timing.csv -k 'testing_specialized_guides or operational_guides_are_converged or onboarding_guides_are_converged'`
Expected: FAIL because files and indexes still use root `docs/guides/`.

### Task 2: Move Docs And Repair References

**Files:**
- Create: `docs/guides/onboarding/`
- Move: `docs/guides/DEVELOPER_GUIDE.md`
- Move: `docs/guides/USER_GUIDE.md`
- Modify: `docs/reports/PHASE6_CLI_STATUS_T2.5H.md`
- Modify: `docs/reports/PHASE6_CLI_STATUS_T4H.md`
- Modify: `docs/reports/PHASE6_FINAL_COMPLETION_REPORT.md`

- [ ] **Step 1: Move the two onboarding docs**

Move both files into `docs/guides/onboarding/` and keep content unchanged unless a path reference needs correction.

- [ ] **Step 2: Patch active references**

Update the few active docs that still mention `docs/guides/USER_GUIDE.md` so they point to `docs/guides/onboarding/USER_GUIDE.md`.

- [ ] **Step 3: Run targeted tests**

Run: `pytest tests/unit/scripts/test_repository_hygiene_paths.py -q --no-cov -o tdd_guard_project_root=/opt/claude/mystocks_spec --timing-file=/tmp/test_timing.csv -k 'testing_specialized_guides or operational_guides_are_converged or onboarding_guides_are_converged'`
Expected: either PASS or fail only on missing index updates.

### Task 3: Rebuild Indices And Cleanup Snapshot

**Files:**
- Modify: `docs/INDEX.md`
- Modify: `docs/guides/INDEX.md`
- Create: `docs/guides/onboarding/INDEX.md`
- Modify: `docs/reports/cleanup/index-artifacts/INDEX_root.md`

- [ ] **Step 1: Regenerate global and guides indexes**

Run: `python scripts/dev/tools/docs_indexer.py --path docs/ --output docs/INDEX.md --categories`

- [ ] **Step 2: Generate onboarding family index**

Run: `python scripts/dev/tools/docs_indexer.py --path docs/guides/onboarding --output docs/guides/onboarding/INDEX.md`

- [ ] **Step 3: Patch curated cleanup snapshot**

Update `INDEX_root.md` so the historical curated pointers for `DEVELOPER_GUIDE` and `USER_GUIDE` use `guides/onboarding/...`.

### Task 4: Full Verification

**Files:**
- Verify only

- [ ] **Step 1: Verify onboarding-affected tests**

Run: `pytest tests/unit/scripts/test_repository_hygiene_paths.py -q --no-cov -o tdd_guard_project_root=/opt/claude/mystocks_spec --timing-file=/tmp/test_timing.csv`
Expected: PASS

- [ ] **Step 2: Verify docs hygiene suite**

Run: `pytest tests/unit/scripts/test_docs_indexer.py tests/unit/scripts/test_repository_hygiene_paths.py -q --no-cov -o tdd_guard_project_root=/opt/claude/mystocks_spec --timing-file=/tmp/test_timing.csv`
Expected: PASS

- [ ] **Step 3: Verify structure governance**

Run: `python -m scripts.maintenance.check_structure --format text .`
Expected: `errors: 0`, `warnings: 0`
