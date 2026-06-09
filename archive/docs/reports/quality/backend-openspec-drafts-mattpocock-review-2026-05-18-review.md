# Review: backend-openspec-drafts-mattpocock-review-2026-05-18.md

> **Current status (2026-05-18 later pass)**:
> This review-of-review is directionally useful, but its task-count notes are
> superseded by
> `docs/reports/quality/backend-openspec-drafts-mattpocock-review-2026-05-18-addendum.md`
> and the current status summary in
> `docs/reports/quality/backend-openspec-drafts-post-mattpocock-review-2026-05-18.md`.
> Current task counts are C=31, E=24, F=24, G=29.

**Type**: .md / proposal | **Perspective**: completeness + consistency + feasibility | **Date**: 2026-05-18 | **Reviewer**: Claude

---

## Executive Summary

本 review 文档的方向性判断正确（四个草案结构完整、需要跨 change 编排），但五个 Blocker 中有四个已被后续草案更新和 orchestration artifact 的创建所解决。核心问题是：**本 review 的 Blockers 部分描述的是草案被修订前的状态，但未标注版本/时间戳，读起来像是当前状态的判断**。如果作为当前审批依据使用，会误导评审者认为草案仍有未解决的缺陷。

## Document Metadata

| Field | Value |
|-------|-------|
| Source | `docs/reports/quality/backend-openspec-drafts-mattpocock-review-2026-05-18.md` |
| File Type | .md |
| Doc Type | proposal |
| Sections | 8 |
| Referenced Files | 10 found / 0 missing |
| Referenced Symbols | 8 found / 0 missing |

## Evidence Verification

### Files Referenced

All 10 L2 references verified: 4 OpenSpec change directories (each with proposal/design/tasks/specs), plus `docs/agents/{issue-tracker,triage-labels,domain}.md`, `architecture/STANDARDS.md`, `openspec/AGENTS.md`, `web/backend/CONTEXT.md`. All exist.

### Functions/Classes Referenced

| Symbol | Found? | Location |
|--------|--------|----------|
| `router_registry.py` | yes | `web/backend/app/router_registry.py` |
| `VERSION_MAPPING.py` | yes | `web/backend/app/api/VERSION_MAPPING.py` |
| `app.core.logger` | yes | `web/backend/app/core/logger.py` |
| `trading_runtime.py` | yes | `web/backend/app/api/trading_runtime.py` |
| `trading_monitor.py` | yes | `web/backend/app/api/trading_monitor.py` |
| `backup_recovery.py` | yes | `web/backend/app/api/backup_recovery.py` |
| `backup_recovery_secure/` | yes | `web/backend/app/api/backup_recovery_secure/` |
| `cleanup_old_backups.py` | yes | `web/backend/app/api/backup_recovery_secure/cleanup_old_backups.py` |

### Claims Verified

| Claim | Status | Evidence |
|-------|--------|----------|
| GET /health: 22 modules | confirmed | `backend-route-table-openapi-baseline-2026-05-18.md:115` |
| GET /status: 13 modules | confirmed | `backend-route-table-openapi-baseline-2026-05-18.md:116` |
| C has 25 tasks | **contradicted** | grep of `tasks.md` finds 31 top-level `N.M` tasks |
| E has 21 tasks | **contradicted** | grep finds 29 |
| F has 21 tasks | **contradicted** | grep finds 24 |
| G has 23 tasks | **contradicted** | grep finds 24 |
| C doesn't address trading/backup | **contradicted** | C design.md:13, proposal.md:31, tasks.md:1.9/2.4/2.5 |
| G doesn't address GET /status | **contradicted** | G design.md:7, :18, :21 list status as classification target |
| C/G don't require prefix-expanded route table | **contradicted** | C design.md:16,:42; G design.md:46-48,:79 |
| Orchestration artifact missing | **contradicted** | `backend-openspec-change-orchestration-2026-05-18.md` exists, all 4 drafts reference it |
| E/F don't coordinate | **contradicted** | E design.md:51-53; F design.md:26,:49,:78-79,:85 |

## Checklist Results

6 items PASS (C1, C4, C5, N1, N3, N5). FAIL and N/A below:

| # | Check | Result | Notes |
|---|-------|--------|-------|
| C2 | Edge cases | FAIL | Review 不考虑被审对象可能已在本 review 之后被修订 |
| C3 | Implicit assumptions | FAIL | 假设被审对象处于 review 写作时状态，未标注版本/快照 |
| N2 | Naming conventions | FAIL | 结构表 task 计数与实际 tasks.md 不一致（4/4 均偏低） |
| N4 | Cross-references | FAIL | Blockers 部分对草案内容的描述与当前草案版本不符 |
| F2 | Dependency availability | FAIL | 声称 orchestration artifact 需要创建，但该 artifact 已存在 |
| F3 | Timeline realism | N/A | review 未含时间线估算 |
| F4 | Resource constraints | N/A | review 未涉及资源约束 |

## Findings

### Critical Issues

| # | Section | Issue | Impact | Evidence | Recommendation |
|---|---------|-------|--------|----------|----------------|
| 1 | Blocker #2 (line 76-91) | 声称 C 草案未覆盖 trading/backup，但 C 的 proposal.md Non-Goals、design.md domain matrix、tasks.md 1.9/2.4/2.5 均已明确 deferral | 误导审批者认为 C 有 scope gap | C proposal.md:31 "This change does not implement trading or backup router consolidation. It records them as deferred OpenSpec follow-ups"; tasks.md:18-19 有显式 deferred tasks | 修订为 "C 已 deferral trading/backup，建议确认 deferral 登记是否充分" |
| 2 | Blocker #3 (line 93-106) | 声称 G 未覆盖 GET /status，但 G design.md 将 status 列为 problem statement、goal 和 classification 对象 | 误导审批者认为 G 有治理洞 | G design.md:7 "GET /status local decorator duplicates across 13 modules"; :18 "Define canonical health/status categories" | 修订为 "G 已纳入 status taxonomy，建议确认 health/status 分类边界是否清晰" |
| 3 | Blocker #4 (line 107-122) | 声称 C/G 草案未区分 local decorator duplicate 和 final full-path conflict，但两份 design.md 均有显式决策段落 | 误导审批者认为 C/G 的 implementation gate 不充分 | C design.md:16,:42; G design.md:46-48 "Decision: Final full-path route table gates runtime conflict claims" | 修订为确认 C/G 的 prefix-expanded requirement 是否已足够具体 |
| 4 | Blocker #5 (line 124-135) | 声称 E/F 需要建立 dependency rule，但 E design.md:51-53 和 F design.md:26,:49,:78-79 均有显式协调决策 | 误导审批者认为 E/F 有未声明的依赖 | E design.md:51 "Core import compatibility gates shared-module DI"; F design.md:26 "does not move lifecycle-owned Core modules until coordination with migrate-backend-singletons-to-lifecycle-di" | 修订为 "E/F 已建立 cross-reference，建议确认具体 lifecycle-owned module 清单是否已对齐" |

### Medium Issues

| # | Section | Issue | Impact | Evidence | Recommendation |
|---|---------|-------|--------|----------|----------------|
| 5 | Blocker #1 (line 44-75) | 建议创建 orchestration artifact，但该 artifact 已存在且被四份草案共同引用为 prerequisite | 审批者可能误以为需要额外工作 | `backend-openspec-change-orchestration-2026-05-18.md` 存在，含 execution order、shared prerequisites、shared surfaces；C/E/F/G 所有 tasks.md 第 1.1 条均引用此 artifact | 修订为 "确认现有 orchestration artifact 是否覆盖所有必要 surface" |
| 6 | 结构检查 (line 33-38) | 4 个 task 计数均低于实际 grep 结果（C:25→31, E:21→29, F:21→24, G:23→24） | 结构表数据不准确 | grep `^- \[ \] \d+\.\d+` on all 4 tasks.md files, scope: `openspec/changes/*/tasks.md` | 更新计数或注明计数方法（是否只计顶层 section heading 而非 subtask） |

### Low Issues

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 7 | 全文 | 未标注被审草案的版本/commit SHA | review 与被审对象同时演进，但 review 未标注快照时间点 | 在 review 头部添加 "Reviewed at: \<commit SHA or timestamp\>" |
| 8 | Approval Checklist (line 223-235) | 部分 checklist item 已被满足（C 已 deferral trading/backup, E/F 已建立协调），但 checklist 写成未完成状态 | 见 Critical #1-#4 证据 | 将已满足的 item 标记为 done 并注明证据位置 |

## Strengths

- 结构检查表的六维度分解（Files/Spec deltas/Requirements/Scenarios/Tasks）提供了有效的草案比较框架
- Issue Readiness Review 表格准确应用了 `docs/agents/triage-labels.md` 的标签体系
- Per-Change Review 部分的优点/修订双栏结构清晰，建议状态判定合理
- 跨 change collision risk 识别准确（route/OpenAPI/import surface 冲突风险真实存在）
- 正确区分了 local decorator duplicate 与 final full-path conflict 的语义差异

## Recommendations

1. **添加版本快照标注**：在 review 头部添加被审草案的 commit SHA 或最后修改时间，明确 review 描述的状态快照。这是解决 "review 与被审对象不同步" 的最小成本方案。

2. **将 Blockers 重分类**：五个 Blocker 中四个应降级为 "已部分解决的建议"，仅保留 "确认 orchestration artifact 覆盖度" 作为审批前的最后确认项。

3. **更新结构表计数**：用 `grep -c '^\- \[ \] \d+\.\d+' tasks.md` 重新计数，或在表中注明 "sections" 而非 "tasks"。

4. **Approval Checklist 增量更新**：已满足的 item 标记完成，保持 review 作为 living document 的实用性。

## Scoring

| Dimension | Score (1-5) | Evidence |
|-----------|-------------|----------|
| Technical Accuracy | 2 | 5 个 Blocker 中 4 个与当前草案状态不符；6 个 numeric claims 中 4 个与 grep 矛盾 |
| Completeness | 3 | 结构完整（8 个 section），但缺少版本快照和 stale-state 警告 |
| Codebase Alignment | 2 | 对草案内容的描述与当前实际文件内容存在系统性偏差 |
| Actionability | 4 | 每个 Blocker 都有明确的建议和二选一选项；Per-Change Review 格式可直接用于修订 |
| Terminology Consistency | 4 | C/E/F/G 标签、route taxonomy 概念全文一致 |
| **Overall** | **2.7** | Actionability 和 Terminology 拉高，但 Technical Accuracy 和 Codebase Alignment 拉低 |

## Verdict

NEEDS_REVISION

本 review 的框架、Issue Readiness 分析和 Per-Change Review 结构具有高价值。但 Blockers 部分描述的是草案修订前的状态，与当前被审对象存在系统性事实偏差。建议：(1) 添加版本快照标注；(2) 将已解决的 Blocker 降级并标注证据；(3) 更新结构表计数。修订后本 review 可作为审批流程的有效参考文档。
