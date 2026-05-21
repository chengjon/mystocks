# Review: D2.5 Control-Plane OpenAPI Docs Decision Package (5-file changeset)

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、
> 当前代码与最近一次实际验证结果为准。

**Type**: md + json + yaml / proposal + evidence + governance (5-file changeset) | **Perspective**: completeness, consistency, feasibility | **Date**: 2026-05-22

## Summary

The 5-file D2.5 control-plane OpenAPI docs changeset is internally consistent and well-evidenced. The JSON artifact confirms all key metrics: routes=548, schema-visible=536, hidden=12, OpenAPI paths=500, operations=536, schemas=301, duplicate operationIds=0, broad candidates=144, and 12 focused taxonomy entries. PR #123 is verified MERGED (head `3ffff99ee`, merged 2026-05-21T18:00:58Z). Issue #92 remains OPEN with correct labels. All 6 referenced docs/API files exist, the OpenSpec change directory contains proposal/design/tasks/specs, and the task card YAML correctly scopes the 5-file changeset. Tasks.md shows 23/24 items complete with the single unchecked item (steward tree update) correctly awaiting human review.

## Verified

- **C1 Required sections**: decision package has Status/Authorization Boundary/Evidence Artifacts/Freshness Gate/Broad Candidate Note/Focused Control-Plane Taxonomy/Probe Consumer Matrix/Documentation Decision Routing/Future Docs/API Implementation Packet/Remaining Gates/Verification Commands; tasks has 5 phases (0-4) with checkboxes; task card has version/id/mainline/classification/openspec/function_tree/scope/non_goals/acceptance/risk_and_rollback/delivery/governance; steward tree has D2.5 entry with correct state
- **C2 Edge cases**: `/health/readiness` classified as intentionally absent; `/api/health/ready` kept as compatibility readiness with no retirement; `/metrics` duplicate classified as control-plane taxonomy item; `/api/strategy-mgmt/{path:path}` classified as runtime-only hidden compat route; broad candidate count increase (128→144) explained by broader governance heuristic
- **C4 Acceptance criteria**: tasks.md phase 4 steward tree update correctly unchecked pending review; verification commands reference correct script paths and task card; task card acceptance checks reference correct YAML path
- **F2 Dependency availability**: PR #123 MERGED with head `3ffff99ee`; issue #92 OPEN with labels enhancement/ready-for-human/ready-for-downstream; HEAD commit `15db8ebf5` exists in worktree; all 6 referenced docs/API files found via filesystem check
- **F5 Rollback plan**: task card specifies "revert this PR and return D2.5 to approved-for-governance-execution state"; governance/evidence only, no source edits authorized
- **N1 Terminology**: "focused taxonomy" vs "broad candidate" used consistently; "platform liveness"/"canonical readiness"/"compatibility readiness"/"diagnostic health surface" used consistently across decision package and JSON taxonomy entries
- **N3 Formatting**: all tables consistent; tasks use `- [x]` / `- [ ]` format; task card YAML properly structured with v0.2 schema; steward tree D2.5 entry matches decision package data
- **N4 Cross-references**: JSON artifact path matches decision package evidence table; task card allowed_paths exactly matches the 5 files in the changeset; OpenSpec change ID `stabilize-backend-control-plane-openapi-docs` matches between task card, tasks.md, and decision package; steward tree D2.5 entry references both planning and decision package reports
- **N5 Style**: all 5 files use formal scope-control language with repeated non-authorization disclaimers

## Issues

No issues found.

## Suggestions

- The decision package probe matrix reports "Scanned files: 6060" but the JSON artifact only stores hit records (5186 lines, 1121 unique files), not the total scanned file count. Consider adding a `scanned_files` summary field to future probe artifacts so the scanned-vs-hit ratio is independently verifiable without re-scanning.

## Verdict

APPROVE — All 5 files form a coherent, evidence-backed D2.5 control-plane OpenAPI docs changeset. The JSON artifact confirms every metric in the decision package (548 routes, 500 OpenAPI paths, 0 duplicate operationIds, 12 focused taxonomy entries, 5186 probe hit lines). PR #123 is verified MERGED. The task card correctly scopes the 5-file changeset with explicit forbidden paths and acceptance gates. Tasks are 23/24 complete with the single unchecked steward tree update correctly gated on human review.
