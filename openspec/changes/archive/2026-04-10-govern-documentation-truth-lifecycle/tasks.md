## 1. Canonical Documentation System

> **使用说明**:
> 本文件用于记录当前 OpenSpec 变更的执行清单、操作步骤或协作约束，帮助跟踪实施过程。
> 其中勾选状态、执行顺序和局部说明仅代表任务推进视角，不应脱离 proposal、design、正式 specs、`architecture/STANDARDS.md` 与实际验证结果单独解读为最终事实。

- [x] 1.1 Create or update a canonical documentation entrypoint (`docs/README.md` or equivalent) that routes readers to active trunks instead of broad catch-all trees
  - Evidence: `docs/README.md` now routes readers to the canonical trunks for governance rules, OpenSpec truth, API contract truth, operations, testing, and historical evidence instead of sending readers into broad subtrees first.
- [x] 1.2 Create `docs/overview/documentation-system.md` describing documentation trunks, precedence, lifecycle classes, and reader routing rules
  - Evidence: `docs/overview/documentation-system.md` defines the canonical trunk map, lifecycle classes, delete gate, default action bias, and recommended execution order.
- [x] 1.3 Cross-link `architecture/STANDARDS.md`, `openspec/project.md`, and the canonical docs index so AI/humans can find the trunk map first
  - Evidence: `architecture/STANDARDS.md`, `openspec/project.md`, and `docs/overview/README.md` now route readers to `docs/README.md` and `docs/overview/documentation-system.md`.
- [x] 1.4 Document the four governance principles explicitly: trunk-first, aggressive stale deletion, one active truth per concern, and AI-friendly hierarchy
  - Evidence: both `docs/README.md` and `docs/overview/documentation-system.md` now state the four governance principles and the `delete/archive > rewrite` bias.

## 2. Governance Rules and Audit Inputs

- [x] 2.1 Add a machine-readable governance manifest such as `config/governance/documentation-taxonomy.yaml`
  - Evidence: `config/governance/documentation-taxonomy.yaml` now defines scan roots, canonical entrypoints, trunk IDs, lifecycle classes, protected doc families, family rules, archive targets, and delete-gate requirements.
- [x] 2.2 Define trunk IDs, lifecycle classes, protected doc families, archive targets, and delete-gate requirements in that manifest
  - Evidence: the taxonomy manifest explicitly records trunk IDs such as `repository-standards`, `docs-entrypoint`, `documentation-governance-trunk`, and `api-navigation`, plus lifecycle definitions and guarded `delete_candidate` families.
- [x] 2.3 Add a focused audit script such as `scripts/governance/audit_documentation_system.py` to classify documents and emit text/JSON findings
  - Evidence: `scripts/governance/audit_documentation_system.py` now loads the taxonomy, classifies markdown paths, emits text/JSON reports, and flags `duplicate_truths`, `unclassified`, and `blocked_delete_candidates`.
- [x] 2.4 Add focused tests for taxonomy parsing, duplicate-truth detection, and delete-gate validation
  - Evidence: `tests/unit/scripts/test_audit_documentation_system.py` covers taxonomy parsing, duplicate canonical truth detection, and delete-gate blocking for unresolved delete candidates.

## 3. Inventory and Decision Register

- [x] 3.1 Generate a first-pass documentation inventory report for active high-risk trees
  - Evidence: `docs/reports/documentation-governance/2026-04-08-first-pass-inventory.md` records measured classified/unclassified counts for `docs/api/`, `docs/reports/`, `docs/guides/`, `docs/overview/`, `docs/operations/`, and `docs/testing/`.
- [x] 3.2 Create a decision register with statuses `keep-canonical`, `keep-supporting`, `merge-into-trunk`, `archive`, `delete`, `needs-replacement`
  - Evidence: `docs/reports/documentation-governance/2026-04-08-decision-register.md` defines the status vocabulary and assigns cluster-level decisions.
- [x] 3.3 Record owner, subtree, canonical replacement, and inbound-link status for each cleanup cluster
  - Evidence: the decision register now records `Owner`, `Subtree / Cluster`, `Canonical replacement`, `Inbound-link status`, and execution gate per row.
- [x] 3.4 Mark any cluster without a canonical replacement as blocked from deletion
  - Evidence: the decision register explicitly blocks `docs/guides/` and `docs/guides/README.md` + `docs/guides/INDEX.md` because their canonical replacements remain unresolved by concern.
- [x] 3.5 Add a default action rule in the decision register: when replacement exists and no retention duty remains, prefer `delete` over `rewrite`
  - Evidence: the decision register now defines `delete > rewrite` and `archive > rewrite` as the default action bias once canonical replacement and retention gates are satisfied.

## 4. Cleanup Wave 1: API Documentation Surface

- [x] 4.1 Define the canonical API documentation trunk using code contract truth plus retained navigation docs
  - Evidence: `docs/api/README.md` now defines the API documentation trunk explicitly: runtime contract truth stays in code/OpenAPI, while `docs/api/README.md` is the canonical navigation layer.
- [x] 4.2 Partition `docs/api/` into canonical/supporting/report/archive/delete-candidate clusters
  - Evidence: `docs/reports/documentation-governance/2026-04-08-api-wave1.md` and `config/governance/documentation-taxonomy.yaml` now partition `docs/api/` into canonical, supporting, generated reference, report, plan, and delete-candidate clusters.
- [x] 4.3 Update API indexes so they point only to retained canonical or supporting documents
  - Evidence: `docs/api/README.md`, `docs/api/INDEX.md`, and `docs/INDEX.md` no longer route readers through `docs/api/legacy-cn/` and now point to retained supporting entrypoints only.
- [x] 4.4 Archive or delete bounded `docs/api/` clusters only after the decision register confirms replacement mapping and link cleanup
  - Evidence: after cleaning active-tree inbound links, the bounded `docs/api/legacy-cn/` cluster was removed and recorded in `2026-04-08-api-wave1.md`.
- [x] 4.5 Avoid one-off disclaimer edits for stale API docs unless a bounded transition gap explicitly requires them
  - Evidence: Wave 1 used trunk rewrite + index cleanup + bounded deletion instead of disclaimer-only edits.

## 5. Cleanup Wave 2: Reports and Guides

- [x] 5.1 Partition `docs/reports/` into retained evidence, archive candidates, and delete candidates
  - Evidence: `2026-04-08-reports-guides-wave1.md` records `docs/reports/README.md` as retained evidence trunk and `docs/reports/legacy-cn/` as an executed archive batch.
- [x] 5.2 Partition `docs/guides/` into active runbooks/guides versus stale feature notes and superseded walkthroughs
  - Evidence: `config/governance/documentation-taxonomy.yaml` now classifies guides into transition indexes, active guide families, and root compatibility entries instead of leaving the subtree unclassified.
- [x] 5.3 Update guide/report indexes so active trunks stop routing through stale documents
  - Evidence: `docs/guides/README.md` and `docs/guides/INDEX.md` now act as transition indexes by concern instead of broad historical catch-all entrypoints.
- [x] 5.4 Execute bounded archive/delete batches for `docs/reports/` and `docs/guides/`
  - Evidence: `docs/reports/legacy-cn/` was archived to `archive/docs/reports/legacy-cn-2026-04-08/`, while guides root indexes were boundedly rewritten instead of preserving the stale catch-all surface.

## 6. Cleanup Wave 3: Overview, Operations, Testing

- [x] 6.1 Reconcile `docs/overview/` with the canonical documentation system and remove duplicate trunk indexes
  - Evidence: `docs/overview/README.md` and `docs/overview/INDEX.md` now act only as transition/supporting indexes that route to `docs/README.md`, `documentation-system.md`, and retained overview docs.
- [x] 6.2 Reconcile `docs/operations/` with active operational runbooks only
  - Evidence: `docs/operations/README.md` now serves as the bounded operations trunk, while `docs/operations/INDEX.md` routes only to active runbook families and root runbooks.
- [x] 6.3 Reconcile `docs/testing/` with active testing strategy and verification runbooks only
  - Evidence: `docs/testing/README.md` and `docs/testing/INDEX.md` now route readers to active testing strategy, E2E, environment, and troubleshooting docs instead of legacy branches.
- [x] 6.4 Archive or delete superseded overview/operations/testing branches based on the decision register
  - Evidence: `docs/testing/legacy-cn/` was removed from the active tree and archived to `archive/docs/testing/legacy-cn-2026-04-08/`; taxonomy and the decision register now record that execution.

## 7. Enforcement and Rollout

- [x] 7.1 Integrate the documentation audit command into existing governance / CI entrypoints
  - Evidence: `.github/workflows/directory-compliance.yml` now runs `python scripts/governance/audit_documentation_system.py --format json` and fails the job on `duplicate_truths` or `blocked_delete_candidates`.
- [x] 7.2 Add a lightweight operating guide for how new docs are admitted into canonical trunks
  - Evidence: `docs/guides/documentation/CANONICAL_TRUNK_ADMISSION_GUIDE.md` now defines the admission workflow, lifecycle selection, minimum checks, and anti-patterns.
- [x] 7.3 Stop using file-by-file disclaimer editing as the default remediation for stale documentation
  - Evidence: `docs/overview/documentation-system.md` and `CANONICAL_TRUNK_ADMISSION_GUIDE.md` now codify `delete/archive > rewrite` and the default remediation order.
- [x] 7.4 Run `openspec validate govern-documentation-truth-lifecycle --strict`
  - Evidence: `openspec validate govern-documentation-truth-lifecycle --strict` returned valid after rollout tasks 7.1-7.3 and wave 3 archive changes.
