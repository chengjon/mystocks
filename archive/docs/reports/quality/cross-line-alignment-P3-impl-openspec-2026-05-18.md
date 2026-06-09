# Cross-Line Alignment: P3 Implementation ↔ OpenSpec Governance

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **Date**: 2026-05-18
> **Purpose**: Align the OpenSpec governance line's issue drafts with work already completed on the P3 implementation line.
> **Action required**: Update manifest and issue bodies before any publication.

---

## 1. Already-Completed Work (P3 Implementation Line)

The P3 implementation line has executed backend code changes in 6 commits on branch `wip/root-dirty-20260403`. These commits overlap with several of the 13 draft issues.

### 1.1 Issue-Level Mapping

| Draft Issue | Subject | Implementation Status | Evidence | Recommendation |
|---|---|---|---|---|
| #1 | Approve orchestration | **Partially stale** — C announcement/strategy/risk decisions already made and implemented | P3-A1/A2/A3 decision records; P3-B and P3-C1 commits | Update issue body to acknowledge completed work; re-scope approval to remaining items only (E/F/G, trading/backup follow-ups) |
| #2 | Refresh route table + OpenAPI evidence | **Partially done** — route table generated (588 routes, 0 full-path duplicates); OpenAPI baseline exists (501 paths, 3.1.0) | `docs/reports/quality/generated/backend-fullpath-route-table.{json,md}`, `openapi-before.json` | Update issue body to reference existing artifacts; scope remaining work to: (1) regenerate post-implementation baseline, (2) diff against `openapi-before.json` |
| #3 | Decide announcement canonical router | **RESOLVED** | P3-A1 DR: `announcement/` package is canonical; `announcement.py` deleted in `243d40a8a` | **Do not publish**. Mark as `already-resolved` in manifest. Close after issue 1 approval if needed. |
| #4 | Decide strategy canonical router | **RESOLVED** | P3-A2 DR: `strategy_management/` package is canonical; 3→1 convergence in `1241c4b7e` | **Do not publish**. Mark as `already-resolved`. Close after issue 1 approval. |
| #5 | Decide risk canonical router | **RESOLVED** | P3-A3 DR: `risk/` package is canonical; 6 orphan files deleted in `243d40a8a` | **Do not publish**. Mark as `already-resolved`. Close after issue 1 approval. |
| #6 | Create trading follow-up OpenSpec | Still needed | P3-A6 DR: `trading_runtime.py` is canonical; `trading_monitor.py` orphan deleted | **Keep**. No implementation overlap. |
| #7 | Create backup follow-up OpenSpec | Still needed | P3-A7 DR: `backup_recovery_secure/` is canonical; `backup_recovery.py` deleted | **Keep**. No implementation overlap. |
| #8 | Build health/status taxonomy | **Partially done** — P3-A5 taxonomy proposed; 52-route inventory generated | `backend-audit-P3-progress-report.md` §6 appendix | Update issue body to reference existing taxonomy and inventory; scope remaining to: (1) formalize taxonomy in OpenSpec G change, (2) designate canonical `/health` handler |
| #9 | Decide health/status canonical paths | Still needed | P3-A5 DR: proposed 3-tier taxonomy, not yet implemented | **Keep**. No implementation overlap. |
| #10 | Build Core import compatibility matrix | Still needed | P3-A4 singleton inventory exists but is narrower scope | **Keep**. No implementation overlap. |
| #11 | Build singleton lifecycle inventory | **Partially done** — P3-A4 singleton lifecycle inventory completed | `backend-audit-phase3-decision-records.md` P3-A4 | Update issue body to reference P3-A4; scope remaining to DI-specific lifecycle classification |
| #12 | Select first DI pilot | Still needed | Depends on #11 | **Keep**. |
| #13 | Draft first Core split batch | Still needed | Depends on #10 | **Keep**. |

### 1.2 Summary

- **3 issues resolved** (#3, #4, #5) — do not publish as HITL decision issues
- **3 issues partially done** (#1, #2, #8) — update body to reference existing work
- **1 issue partially done** (#11) — reference P3-A4 inventory
- **6 issues unchanged** (#6, #7, #9, #10, #12, #13) — proceed as drafted

---

## 2. Implementation Commits (for evidence cross-reference)

| Commit | Subject | Files Changed |
|---|---|---|
| `e03279c72` | P3-A2–A7 decision records | 1 file (decision records doc) |
| `243d40a8a` | P3-B safe closure | 16 files (9 deleted, frontend fixes, registration fixes) |
| `cc0e33719` | P3-B5 monitoring_old orphan | 3 files (2 deleted) |
| `ba40aa211` | P3-B extended orphans | 9 files (5 deleted, 1 registered) |
| `1241c4b7e` | P3-C1 strategy convergence + P3-C6 market shim | 18 files (3 deleted, 1 renamed, 4 new) |

**Total**: 19 files deleted + 1 renamed + 4 new. Route table: 588 routes, 0 full-path duplicates, 12 orphan files remaining.

---

## 3. Route Table vs OpenAPI Baseline Reconciliation

| Artifact | Count | Method |
|---|---|---|
| Route table (this line) | 588 routes | AST scan of decorator paths + registration prefix composition |
| OpenAPI baseline (other line) | 501 paths | FastAPI `openapi.json` generation at runtime |

The ~87 difference is expected: route table counts individual method+path combinations (e.g., GET + POST on same path = 2 routes), while OpenAPI counts unique paths. Some routes may also be excluded from OpenAPI by `include_in_schema=False`.

**Action for issue #2**: The issue should reference both artifacts and clarify the intended reconciliation scope.

---

## 4. OpenSpec C Change: Partially Pre-empted

The `consolidate-backend-api-domain-routers` OpenSpec change (C) has 31 tasks. Based on P3 implementation:

| C Task Category | Tasks | Already Done? |
|---|---|---|
| Announcement canonical router + orphan cleanup | ~5 | **Yes** (P3-A1 + P3-B) |
| Strategy canonical router + 3→1 convergence | ~8 | **Yes** (P3-A2 + P3-C1) |
| Risk canonical router + orphan cleanup | ~5 | **Yes** (P3-A3 + P3-B) |
| Market flat→package | ~2 | **Yes** (P3-C6) |
| Trading follow-up | ~3 | No (deferred) |
| Backup follow-up | ~3 | No (deferred) |
| Compat redirect + frontend migration | ~5 | **Yes** (P3-C1) |

**Recommendation**: When updating `tasks.md`, mark completed items with `[x]` and add commit references. Do not re-implement.

---

## 5. OpenSpec G Change: Check Before Creating New Proposal

The governance line already created `openspec/changes/consolidate-backend-health-endpoints/` with `proposal.md`, `design.md`, and `tasks.md` (29 tasks). Before the implementation line creates its own P3-C7 health endpoint proposal:

- **Check**: Read the existing G proposal first.
- **Update**: If the G proposal is incomplete or stale relative to P3-A5 taxonomy and the 52-route inventory, update it rather than creating a duplicate.
- **Coordinate**: The implementation line should not start P3-C7 implementation without G proposal approval through the governance line's flow.

---

## 6. Recommended Manifest Updates

Replace the current manifest publication order with:

```
Order  Issue  Subject                        Status Change
1      #1     Approve orchestration          UPDATE body (acknowledge C partial completion)
2      #2     Refresh route/OpenAPI evidence  UPDATE body (reference existing artifacts)
—      #3     Decide announcement router      SKIP (already resolved: P3-A1 + P3-B)
—      #4     Decide strategy router          SKIP (already resolved: P3-A2 + P3-C1)
—      #5     Decide risk router              SKIP (already resolved: P3-A3 + P3-B)
3      #8     Build health/status taxonomy    UPDATE body (reference P3-A5 + 52-route inventory)
4      #9     Decide health/status paths      KEEP (still needed)
5      #10    Build Core import matrix        KEEP
6      #11    Build singleton lifecycle        UPDATE body (reference P3-A4 inventory)
7      #12    Select first DI pilot            KEEP
8      #13    Draft first Core split batch     KEEP
9      #6     Create trading follow-up         KEEP
10     #7     Create backup follow-up          KEEP
```

Published issues drop from 13 to 10. Issues 3/4/5 are closed as already-resolved after issue 1 approval.
