# Local SQLite Tracker Implementation Plan

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、任务方案或执行矩阵，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值和时间线如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the default Symphony task source with a local SQLite-backed tracker while preserving the existing orchestration loop.

**Architecture:** Keep the orchestrator and runner unchanged, add a new `LocalIssueTrackerClient`, and select the tracker implementation through config-driven factory wiring. Persist current issue state in `issues` and append audit entries to `issue_events`.

**Tech Stack:** Python 3.12, `sqlite3`, existing Symphony service modules, `pytest`

---

### Task 1: Extend tracker config for local SQLite

**Files:**
- Modify: `src/services/symphony/config.py`
- Test: `tests/unit/services/symphony/test_config.py`

**Step 1: Write the failing test**

Add tests asserting:
- `tracker.kind: local` is accepted
- default `sqlite_path` resolves to `.symphony/tracker.db`
- `validate_dispatch_config()` accepts local tracker config

**Step 2: Run test to verify it fails**

Run: `pytest --no-cov tests/unit/services/symphony/test_config.py -q`
Expected: FAIL because `local` is unsupported and `sqlite_path` does not exist yet.

**Step 3: Write minimal implementation**

Update `TrackerConfig` and config parsing to:
- accept `local`
- parse `sqlite_path`
- validate local config without requiring Linear API credentials

**Step 4: Run test to verify it passes**

Run: `pytest --no-cov tests/unit/services/symphony/test_config.py -q`
Expected: PASS

### Task 2: Add SQLite local tracker client

**Files:**
- Create: `src/services/symphony/local_tracker.py`
- Modify: `src/services/symphony/errors.py`
- Test: `tests/unit/services/symphony/test_local_tracker.py`

**Step 1: Write the failing test**

Add tests covering:
- database/table bootstrap
- candidate issue fetch from active states
- state refresh by issue ids
- event log append on writes

**Step 2: Run test to verify it fails**

Run: `pytest --no-cov tests/unit/services/symphony/test_local_tracker.py -q`
Expected: FAIL because `LocalIssueTrackerClient` does not exist yet.

**Step 3: Write minimal implementation**

Implement:
- schema bootstrap
- row ↔ `Issue` mapping
- `fetch_candidate_issues()`
- `fetch_issues_by_states()`
- `fetch_issue_states_by_ids()`
- minimal write helpers used by CLI

**Step 4: Run test to verify it passes**

Run: `pytest --no-cov tests/unit/services/symphony/test_local_tracker.py -q`
Expected: PASS

### Task 3: Wire tracker factory into Symphony service

**Files:**
- Create: `src/services/symphony/tracker_factory.py`
- Modify: `src/services/symphony/service.py`
- Modify: `src/services/symphony/__init__.py`
- Test: `tests/unit/services/symphony/test_tracker_factory.py`

**Step 1: Write the failing test**

Add tests asserting:
- `linear` config builds `LinearIssueTrackerClient`
- `local` config builds `LocalIssueTrackerClient`

**Step 2: Run test to verify it fails**

Run: `pytest --no-cov tests/unit/services/symphony/test_tracker_factory.py -q`
Expected: FAIL because no tracker factory exists.

**Step 3: Write minimal implementation**

Introduce a small factory and switch `SymphonyService` to use it instead of hardcoding Linear.

**Step 4: Run test to verify it passes**

Run: `pytest --no-cov tests/unit/services/symphony/test_tracker_factory.py -q`
Expected: PASS

### Task 4: Add local tracker CLI

**Files:**
- Create: `scripts/runtime/local_tracker.py`
- Test: `tests/unit/services/symphony/test_local_tracker_cli.py`

**Step 1: Write the failing test**

Add tests covering:
- `create` command inserts an issue
- `list` command prints created issues
- `update-state` changes issue state

**Step 2: Run test to verify it fails**

Run: `pytest --no-cov tests/unit/services/symphony/test_local_tracker_cli.py -q`
Expected: FAIL because CLI does not exist yet.

**Step 3: Write minimal implementation**

Implement an argparse-based CLI using the local tracker write helpers.

**Step 4: Run test to verify it passes**

Run: `pytest --no-cov tests/unit/services/symphony/test_local_tracker_cli.py -q`
Expected: PASS

### Task 5: Switch default workflow to local tracker and verify dry-run

**Files:**
- Modify: `WORKFLOW.md`
- Modify: `.env.example` if needed
- Test: `tests/unit/services/symphony/test_workflow_loader.py`

**Step 1: Write the failing test**

Add a test or assertion showing local workflow config parses cleanly.

**Step 2: Run test to verify it fails**

Run: `pytest --no-cov tests/unit/services/symphony/test_workflow_loader.py -q`
Expected: FAIL if local workflow config is not yet supported.

**Step 3: Write minimal implementation**

Update `WORKFLOW.md` to local tracker defaults and remove Linear-specific dynamic tool guidance.

**Step 4: Run test to verify it passes**

Run: `pytest --no-cov tests/unit/services/symphony/test_workflow_loader.py -q`
Expected: PASS

### Task 6: Full validation

**Files:**
- Validate: `src/services/symphony/`
- Validate: `scripts/runtime/local_tracker.py`
- Validate: `tests/unit/services/symphony/`

**Step 1: Run targeted Symphony test suite**

Run: `pytest --no-cov tests/unit/services/symphony -q`
Expected: PASS

**Step 2: Run lint and format checks**

Run: `ruff check src/services/symphony scripts/runtime/run_symphony.py scripts/runtime/local_tracker.py tests/unit/services/symphony`

Run: `black --check src/services/symphony scripts/runtime/run_symphony.py scripts/runtime/local_tracker.py tests/unit/services/symphony`

Expected: PASS

**Step 3: Run OpenSpec validation**

Run: `openspec validate <change-id> --strict`
Expected: PASS
