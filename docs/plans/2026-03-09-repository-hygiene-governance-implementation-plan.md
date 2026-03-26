# Repository Hygiene Governance Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将当前目录治理、P1/P2 清理任务、文档生命周期管理整合为一套可执行的仓库卫生治理方案。

**Architecture:** 先对齐 OpenSpec 与治理策略，再落地统一脚本入口，最后分批处理根目录阻塞项与文档收敛。所有会修改文件系统状态的入口先支持 dry-run，并输出可审计报告。

**Tech Stack:** OpenSpec、Python、Bash、pytest、YAML、Git hooks / CI

---

## First Executable Batch

本计划建议先执行 **Batch 1：Governance Alignment and Safe Entry Points**。

### Batch 1 Objective

在不做大规模文件迁移的前提下，先把“规则、目标目录、统一入口、测试基线”四件事对齐，为后续根目录收敛和文档生命周期迁移建立稳定地基。

### Batch 1 Scope

- 刷新 `docs/reports/cleanup/FILE_CLEANUP_TASK.md` 的真实基线与目标目录
- 更新目录治理 policy，使 `docs/`、`reports/`、`archive/`、`var/` 成为正式 canonical targets
- 为 `rotate_logs.sh`、`monitor_file_size.sh`、`auto_cleanup.sh` 建立 dry-run-first 的官方入口
- 增加聚焦测试，确保这些入口先可验证、再可推广

### Batch 1 Exit Criteria

- `openspec validate integrate-repository-hygiene --strict` 通过
- policy 测试证明 canonical lifecycle targets 不会被误判为新的 root violation
- 三个统一入口都具备 dry-run 或等价的安全预览能力
- `python scripts/maintenance/check_structure.py --format text` 不会因为新 canonical targets 引入新增阻塞

### Batch 1 Suggested Commit Split

1. `spec/policy`: 刷新 `docs/reports/cleanup/FILE_CLEANUP_TASK.md` 与 directory governance policy / tests
2. `scripts/logs`: 收敛 `rotate_logs.sh`
3. `scripts/size-monitor`: 新增 `monitor_file_size.sh` 并复用现有扫描逻辑
4. `scripts/cleanup`: 新增或收敛 `auto_cleanup.sh` 与相关 dry-run 测试

### Batch 1 File Set

- `docs/reports/cleanup/FILE_CLEANUP_TASK.md`
- `governance/mainline/policies/directory-structure.yaml`
- `scripts/maintenance/rotate_logs.sh`
- `scripts/maintenance/monitor_file_size.sh`
- `scripts/cleanup/auto_cleanup.sh`
- `scripts/compliance/file_size_guardrail.py`
- `scripts/dev/check_file_sizes.py`
- `scripts/dev/cleanup_temp_files.py`
- `scripts/dev/execute_cleanup.py`
- `tests/unit/scripts/` 下对应聚焦测试

### Batch 1 Verification Checklist

- `openspec validate integrate-repository-hygiene --strict`
- `pytest tests/unit/scripts/test_check_structure_policy.py -q -o addopts=''`
- `pytest tests/unit/scripts/test_rotate_logs.py -q -o addopts=''`
- `pytest tests/unit/scripts/test_monitor_file_size.py -q -o addopts=''`
- `pytest tests/unit/scripts/test_auto_cleanup.py -q -o addopts=''`
- `python scripts/maintenance/check_structure.py --format text`

### Batch 1 Explicit Deferrals

以下内容不放进第一批：

- 大规模根目录文件迁移
- `docs/` 历史材料批量迁往 `archive/`
- `reports/` 证据文档体系的全量重整
- 自动删除或自动搬移的高风险默认行为

---

### Task 1: 补齐规格与设计

**Files:**
- Create: `openspec/changes/integrate-repository-hygiene/proposal.md`
- Create: `openspec/changes/integrate-repository-hygiene/design.md`
- Create: `openspec/changes/integrate-repository-hygiene/tasks.md`
- Create: `openspec/changes/integrate-repository-hygiene/specs/directory-governance/spec.md`
- Create: `openspec/changes/integrate-repository-hygiene/specs/file-organization/spec.md`
- Create: `docs/plans/2026-03-09-repository-hygiene-governance-design.md`
- Create: `docs/plans/2026-03-09-repository-hygiene-governance-implementation-plan.md`

**Step 1: Validate OpenSpec shape**

Run: `openspec validate integrate-repository-hygiene --strict`

Expected: change validates successfully with no schema or scenario errors.

### Task 2: 刷新清理任务基线

**Files:**
- Modify: `docs/reports/cleanup/FILE_CLEANUP_TASK.md`
- Modify: `governance/mainline/policies/directory-structure.yaml`

**Step 1: Write the failing test**

- Add a policy-focused test proving canonical targets such as `archive/` and `var/` do not trigger root errors once approved.

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/scripts/test_check_structure_policy.py -q -o addopts='' -k canonical_targets`

Expected: FAIL because the current policy does not yet allow the required rollout targets.

**Step 3: Write minimal implementation**

- Update the policy allowlists and tolerated entries
- Refresh `docs/reports/cleanup/FILE_CLEANUP_TASK.md` so its target directories and current baseline match reality

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/scripts/test_check_structure_policy.py -q -o addopts=''`

Expected: PASS with no regression in existing policy tests.

### Task 3: 收敛日志轮转入口

**Files:**
- Modify: `scripts/maintenance/rotate_logs.sh`
- Create: `tests/unit/scripts/test_rotate_logs.sh` or a Python-based wrapper test

**Step 1: Write the failing test**

- Add a test covering dry-run log rotation and archive target resolution.

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/scripts/test_rotate_logs.py -q -o addopts=''`

Expected: FAIL because the current script lacks the governed dry-run/report behavior.

**Step 3: Write minimal implementation**

- Add dry-run support
- Align targets to canonical runtime/archive directories
- Emit a summary report

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/scripts/test_rotate_logs.py -q -o addopts=''`

Expected: PASS.

### Task 4: 建立统一文件大小监控入口

**Files:**
- Create: `scripts/maintenance/monitor_file_size.sh`
- Modify: `scripts/compliance/file_size_guardrail.py`
- Modify: `scripts/dev/check_file_sizes.py`
- Create: `tests/unit/scripts/test_monitor_file_size.py`

**Step 1: Write the failing test**

- Add a test proving the canonical monitor can scan for large files and emit machine-readable output.

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/scripts/test_monitor_file_size.py -q -o addopts=''`

Expected: FAIL because the canonical entrypoint does not yet exist.

**Step 3: Write minimal implementation**

- Create the canonical shell entrypoint
- Reuse or wrap existing Python logic instead of duplicating file scanning

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/scripts/test_monitor_file_size.py -q -o addopts=''`

Expected: PASS.

### Task 5: 建立统一自动清理入口

**Files:**
- Create: `scripts/cleanup/auto_cleanup.sh`
- Modify: `scripts/dev/cleanup_temp_files.py`
- Modify: `scripts/dev/execute_cleanup.py`
- Create: `tests/unit/scripts/test_auto_cleanup.py`

**Step 1: Write the failing test**

- Add tests for dry-run cleanup, Python cache cleanup, coverage cleanup, backup archival planning, and report generation.

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/scripts/test_auto_cleanup.py -q -o addopts=''`

Expected: FAIL because the canonical cleanup workflow does not yet exist.

**Step 3: Write minimal implementation**

- Provide a single official cleanup entrypoint
- Reuse existing helper logic where safe
- Make destructive actions opt-in

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/scripts/test_auto_cleanup.py -q -o addopts=''`

Expected: PASS.

### Task 6: 做第一批根目录阻塞项收敛

**Files:**
- Modify: `governance/mainline/policies/directory-structure.yaml`
- Modify: affected root paths in small, focused batches
- Create: `reports/governance/` artifacts as needed

**Step 1: Baseline the repository**

Run: `python scripts/maintenance/check_structure.py --format text`

Expected: current blocking `error` items are visible and grouped.

**Step 2: Write the failing test**

- Add a focused regression test for the first remediation batch if policy behavior changes.

**Step 3: Write minimal implementation**

- Move runtime artifacts to canonical locations
- Resolve unexpected root files/directories in one batch at a time

**Step 4: Run verification**

Run: `python scripts/maintenance/check_structure.py --format json`

Expected: targeted root `error` count is reduced without introducing new violations.

### Task 7: 文档生命周期收敛

**Files:**
- Modify: `docs/reports/cleanup/FILE_CLEANUP_TASK.md`
- Modify: `docs/guides/documentation/DOCUMENTATION_WORKFLOW_GUIDE.md`
- Modify: `governance/mainline/policies/directory-structure.yaml`
- Move: selected historical docs into `archive/docs/`
- Move: selected evidence docs into `reports/`

**Step 1: Produce migration inventory**

Run: `python scripts/maintenance/check_structure.py --format json`

Expected: warning-class convergence targets are visible for documentation and archive sprawl.

**Step 2: Write minimal implementation**

- Define migration batches by lifecycle
- Move only one bounded category per batch

**Step 3: Run verification**

Run: `openspec validate integrate-repository-hygiene --strict && python scripts/maintenance/check_structure.py --format text`

Expected: spec remains valid and warning/error counts move in the expected direction.
