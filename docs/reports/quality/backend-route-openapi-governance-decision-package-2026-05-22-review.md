# Review: backend-route-openapi-governance-decision-package-2026-05-22 + tasks.md

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、
> 当前代码与最近一次实际验证结果为准。

**Type**: md / proposal + workflow (2-file changeset) | **Perspective**: completeness, consistency, feasibility | **Date**: 2026-05-22

## Summary

The decision package is well-evidenced: all 4 generated JSON artifacts exist under `.planning/codebase/generated/` (gitignored), the route table confirms 548 routes at HEAD `c173bbc8d48d`, and the OpenAPI snapshot summary confirms 500 paths / 536 operations / 0 duplicate operationIds — matching the document exactly. The tasks.md shows 15 of 16 items checked, with only the steward tree update pending (correctly awaiting human review). One low finding: ownership classification shows 40 trading-owned routes but the module table sums to 41 (7+3+5+8+6+5+6+1), suggesting the trading-adjacent unclassified route is counted in the module table but not in the "trading-owned" classification row.

## Verified

- **C1 Required sections**: decision package has Status/Authorization Boundary/Evidence Artifacts/Freshness Gate/Snapshot/Ownership Classification/Probe Matrix/Consumer Matrix/Decision Routing/Task Status/Next Gate; tasks has 5 phases (0-4) with checkboxes
- **C2 Edge cases**: `/metrics` duplicate classified as D2.5 control-plane; trading-adjacent route kept unclassified; backup routes routed to D2.4; PM2 to D2.6; GPU warning treated as environmental smoke note
- **C4 Acceptance criteria**: tasks.md phase 4.63 (steward tree update) correctly unchecked pending review; minimum regression gates specified for all 6 route groups
- **F2 Dependency availability**: HEAD commit `c173bbc8d48d` exists; issue #92 OPEN; route table artifact confirms routes=548; OpenAPI snapshot confirms paths=500, operations=536
- **F5 Rollback plan**: governance/evidence only — no source edits authorized, so rollback = discard the package
- **N1 Terminology**: "trading-owned", "trading-adjacent-unclassified" used consistently; D2.3-D2.6 lane routing consistent between decision package and tasks
- **N3 Formatting**: tables consistent; tasks use `- [x]` / `- [ ]` format; both files uniform
- **N4 Cross-references**: generated artifact paths match actual filesystem locations; HEAD commit matches; OpenSpec change name consistent

## Issues

- [ ] **[LOW]** Module route count sums to 41 but trading-owned class shows 40 — "Module Counts" table + "D2.3 Ownership Classification" table
      Evidence: Codebase: module table rows sum to 7+3+5+8+6+5+6+1=41 routes. Document: "Trading-owned" class shows 40 routes, "Trading-adjacent unclassified" shows 1 — the total is 41 across both rows, which is internally consistent. The module table includes all 8 modules including `advanced_analysis_api` (1 route), while the classification correctly splits 40 owned + 1 unclassified = 41. No actual discrepancy — withdrawn on internal resolution check.

No remaining issues.

## Suggestions

- Consider adding a row-level footnote to the module counts table noting which module corresponds to the trading-adjacent unclassified classification, to make the 40+1=41 mapping traceable at a glance.

## Verdict
APPROVE — Decision package accurately reflects generated evidence artifacts (verified 548 routes, 500 OpenAPI paths, 0 duplicate operationIds at HEAD c173bbc8d48d). Tasks are 15/16 complete with the single unchecked item correctly gated on human review. Scope control is tight: 12 explicit non-authorizations in the boundary section, no source edits, no implementation issues created.
