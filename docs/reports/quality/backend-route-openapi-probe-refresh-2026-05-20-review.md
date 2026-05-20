# Review: backend-route-openapi-probe-refresh-2026-05-20.md

**Type**: md / proposal | **Perspective**: completeness, consistency, feasibility | **Date**: 2026-05-20

> **历史文档说明**:
> 本文件是审查快照，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Summary

Evidence report for `sequence-backend-architecture-unblocks` Task 5.x. All three output artifacts exist and their summary numbers match the document's claims. One referenced OpenSpec change does not exist on disk. The `/metrics` duplicate finding is verified against the live codebase and correctly classified as a control-plane taxonomy item.

## Verified

- **C1 Required sections**: Status, Output Artifacts, findings, Next Gate — all present
- **C4 Acceptance criteria**: Each artifact has a named JSON file with measurable summary fields
- **A9 Named entities — artifacts**: `.planning/codebase/generated/backend-route-table-2026-05-20.json` exists; `total_routes=548`, `include_in_schema_true=536`, `include_in_schema_false=12`, `endpoint_modules=98` — all match document
- **A9 Named entities — OpenAPI snapshot**: `.planning/codebase/generated/route-openapi-snapshot-2026-05-20.json` exists; `openapi_path_count=500`, `operation_count=536`, `duplicate_operation_id_count=0`, `components_schema_count=294` — all match document
- **A9 Named entities — probe matrix**: `.planning/codebase/generated/probe-consumer-matrix-2026-05-20.json` exists; `scanned_files=5782`, `hit_files=188`, `hit_lines=611`, `health=278`, `openapi=276`, `status=50` — all match document
- **A9 Named entities — /metrics duplicate**: `main.py:722` defines `GET /metrics` with `include_in_schema=False`; `prometheus_exporter.py:418` defines `GET /metrics` with `include_in_schema=True` — duplicate confirmed, classification as control-plane item is correct
- **F2 Dependency availability**: All three JSON artifacts were generated from `app.openapi()` and route-table walks; `app_import_stdout_sha256` and `app_import_stderr_sha256` are recorded in the route table artifact
- **A6 Terminology**: "route table", "OpenAPI snapshot", "probe consumer matrix" used consistently throughout
- **N4 Cross-references**: HEAD `7b097fffd` is consistent across document and all three artifacts

## Issues

- [ ] **[MED]** Referenced change lane `sequence-backend-architecture-unblocks` does not exist as an OpenSpec change directory — Status:line 10
      Evidence: `glob openspec/changes/sequence-*/**` returned no files. The document cites this as its `Change lane` but the OpenSpec branch has not been created on disk yet. This may be intentional (the proposal may still be pending approval), but it should be stated explicitly.

- [ ] **[LOW]** `endpoint_modules=98` is reported in route table but not explained in the document — Route Table Finding
      Evidence: The route table JSON reports `endpoint_modules: 98` but the document only discusses the duplicate path finding. The module count is relevant context for governance — it indicates how many source files contribute routes to the 548 total.

- [ ] **[LOW]** Probe matrix category `strategy_compat: 8` is mentioned in the document but the label does not appear in the JSON summary — Output Artifacts table
      Evidence: The JSON `category_counts` has keys `health`, `openapi`, `status`, but the document adds `strategy_compat: 8`. This category may exist in the JSON's detail rows under a different key. Minor inconsistency between document prose and artifact field names.

## Suggestions

- Add a one-line note next to the `Change lane` field indicating whether `sequence-backend-architecture-unblocks` is `proposed` (not yet on disk) or `created` (exists on disk). This prevents future readers from assuming the OpenSpec branch exists when it does not.
- Include `endpoint_modules` count in the Route Table Finding section for completeness — it helps readers understand route density per module.
- Clarify the `strategy_compat` category mapping between document prose and JSON artifact field names.

## Verdict
APPROVE_WITH_NOTES — Evidence is verified and artifacts exist on disk. The `/metrics` duplicate finding is correctly classified. One medium finding: the referenced OpenSpec change directory does not exist on disk and this should be stated explicitly.
