# AkShare Market Gates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local AkShare availability probe and a repo-truth consistency gate for `expand-akshare-data-sources` without touching runtime market-data logic.

**Architecture:** Add two standalone Python CLI scripts under `scripts/dev/quality_gate/`. The first produces a local availability snapshot from the installed `akshare` package; the second validates OpenSpec, docs, registry, adapter, route, and focused-test closure against that snapshot and the live repository.

**Tech Stack:** Python 3.12, `argparse`, `json`, `pathlib`, `re`, `subprocess`, `pytest`

---

### Task 1: Availability Probe CLI

**Files:**
- Create: `tests/unit/scripts/test_collect_akshare_market_function_availability.py`
- Create: `scripts/dev/quality_gate/collect_akshare_market_function_availability.py`

- [ ] **Step 1: Write the failing test**

```python
def test_collect_akshare_market_function_availability_writes_snapshot(tmp_path: Path):
    ...
    assert payload["summary"]["available_count"] == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/scripts/test_collect_akshare_market_function_availability.py -q --no-cov`
Expected: FAIL because the CLI script does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```python
def collect_availability(function_names: list[str]) -> dict[str, object]:
    import akshare as ak
    ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/scripts/test_collect_akshare_market_function_availability.py -q --no-cov`
Expected: PASS

### Task 2: Repo-Truth Gate CLI

**Files:**
- Create: `tests/unit/scripts/test_validate_akshare_market_repo_truth.py`
- Create: `scripts/dev/quality_gate/validate_akshare_market_repo_truth.py`

- [ ] **Step 1: Write the failing test**

```python
def test_validate_akshare_market_repo_truth_passes_on_aligned_fixture(tmp_path: Path):
    ...
    assert payload["pass"] is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/scripts/test_validate_akshare_market_repo_truth.py -q --no-cov`
Expected: FAIL because the repo-truth gate script does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```python
def validate_repo_truth(... ) -> dict[str, object]:
    ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/scripts/test_validate_akshare_market_repo_truth.py -q --no-cov`
Expected: PASS

### Task 3: Live Repo Validation And Docs

**Files:**
- Modify: `docs/guides/akshare/AKSHARE_MARKET_MAINTENANCE.md`
- Modify: `docs/guides/akshare/AKSHARE_MARKET_TROUBLESHOOTING.md`

- [ ] **Step 1: Add command references and usage notes**

Document:
- availability probe command
- repo-truth gate command
- read-only/report-only boundary

- [ ] **Step 2: Run the new CLIs against the live worktree**

Run: `python scripts/dev/quality_gate/collect_akshare_market_function_availability.py --output /tmp/akshare-market-availability.json`
Expected: JSON report with current local availability

Run: `python scripts/dev/quality_gate/validate_akshare_market_repo_truth.py --output /tmp/akshare-market-repo-truth.json`
Expected: PASS on the current repo-truth state

- [ ] **Step 3: Run the focused verification suite**

Run: `pytest tests/unit/scripts/test_collect_akshare_market_function_availability.py tests/unit/scripts/test_validate_akshare_market_repo_truth.py -q --no-cov`
Expected: PASS

- [ ] **Step 4: Record outcomes in the final handoff**

Summarize:
- local `akshare` availability counts
- gate pass/fail
- any residual risks
