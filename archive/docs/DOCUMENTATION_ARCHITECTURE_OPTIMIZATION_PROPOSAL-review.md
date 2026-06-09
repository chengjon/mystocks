# Review: DOCUMENTATION_ARCHITECTURE_OPTIMIZATION_PROPOSAL.md

Source: `docs/DOCUMENTATION_ARCHITECTURE_OPTIMIZATION_PROPOSAL.md`  
Reference: `/opt/claude/eltdx/docs/DOCS_METHODOLOGY.md`  
Review date: 2026-06-09  
Detected: `.md` / proposal  
Perspectives: completeness, consistency, feasibility, architecture

## Verdict

Revision required before execution.

The proposal correctly borrows useful ideas from the eltdx methodology: a reader-first entrypoint, layered navigation, smaller single-purpose pages, relative cross-references, and not copying the SDK-specific `helpers/ + methods/` split into a service/application repository. However, several recommendations conflict with this repository's current documentation governance truth. The highest-risk problems are:

- The proposal diagnoses a missing/unclear documentation hierarchy even though this repo already has a canonical trunk model.
- It proposes `docs/_archive/`, while the current OpenSpec file-organization truth says historical docs should converge into `archive/docs/`.
- It plans directory merges, archives, INDEX rewrites, and possible deletions without the current classification, approval, and verification gates required by this repo.

## Evidence Scope

Current filesystem facts were measured from `/opt/claude/mystocks_spec/docs` on 2026-06-09:

| Metric | Current fact |
|---|---:|
| All files under `docs/` | 5,331 |
| Markdown files under `docs/` | 2,873 |
| Directories under `docs/` | 146 |
| Max file path depth | 6 segments |
| Markdown files under `docs/reports/` | 1,971 |
| All files under `docs/reports/` | 4,379 |
| Markdown files under `docs/guides/` | 283 |
| Direct child directories under `docs/guides/` | 23 |
| `INDEX.md` files under `docs/` | 78 |
| `README.md` files under `docs/` | 27 |
| `INDEX.md` files with same-directory `README.md` | 20 |
| Markdown files containing absolute local links | 123 |
| Absolute local links in Markdown docs | 737 |

Important current truth sources checked:

- `architecture/STANDARDS.md`
- `docs/README.md`
- `docs/overview/documentation-system.md`
- `docs/guides/documentation/CANONICAL_TRUNK_ADMISSION_GUIDE.md`
- `openspec/specs/documentation-governance/spec.md`
- `openspec/specs/file-organization/spec.md`
- `openspec/specs/directory-governance/spec.md`
- `openspec/specs/api-documentation/spec.md`
- `PRODUCT.md`
- `DESIGN.md`

## Findings

- [ ] **[HIGH]** The diagnosis that the repo has no layered/current-truth documentation system is stale and would cause the proposal to rewrite the wrong surface.

  Source: `docs/DOCUMENTATION_ARCHITECTURE_OPTIMIZATION_PROPOSAL.md:22`, `:24`, `:153`, `:155`, `:158`, `:160`, `:297`

  Evidence checked:
  - The proposal says there is no L1-L5 reader layering and that `docs/README.md` and `docs/INDEX.md` conflict.
  - Current `docs/README.md:1-5` already declares itself as the `docs/` canonical entrypoint.
  - Current `docs/README.md:18-29` already maps canonical trunks, including `architecture/STANDARDS.md`, `openspec/specs/`, `openspec/changes/`, `docs/operations/README.md`, `docs/testing/README.md`, `docs/api/README.md`, and `docs/reports/README.md`.
  - Current `docs/README.md:31-39` already provides reader routing.
  - Current `docs/overview/documentation-system.md:21-36` defines the canonical trunk map and explicitly says `docs/README.md` is a navigation entrypoint while subtree README/INDEX files must not become parallel truth.
  - Current `architecture/STANDARDS.md:5-6` directs readers to `docs/README.md` and `docs/overview/documentation-system.md` for the documentation system's canonical trunk map and reader routing.

  Why the source document does not resolve it:
  - The proposal contains no `canonical` or `trunk` references.
  - It proposes rewriting `docs/README.md` by the eltdx entry template instead of preserving the existing trunk-first map and adding reader-layer affordances on top.

  Recommendation:
  - Reframe P1/P3 as "existing canonical trunk map needs readability and compression improvements", not "no layered system".
  - Preserve `docs/README.md` as the trunk-first router. Add eltdx-style role reading paths only as a secondary section.
  - Treat `docs/INDEX.md` as already demoted: it currently states it is generated and not the shared-rule truth at `docs/INDEX.md:3-5`.

- [ ] **[HIGH]** The proposed archive location `docs/_archive/` conflicts with the current canonical lifecycle directory rule.

  Source: `docs/DOCUMENTATION_ARCHITECTURE_OPTIMIZATION_PROPOSAL.md:140`, `:180`, `:187`, `:194`, `:222`, `:243`, `:306`, `:361`, `:391`

  Evidence checked:
  - The proposal repeatedly introduces `_archive/` under `docs/`, including moving `docs/reports/` to `docs/_archive/reports/`.
  - Current `openspec/specs/file-organization/spec.md:104-106` says historical assets are archived under `archive/`.
  - Current `openspec/specs/file-organization/spec.md:120-121` says stale historical docs in active docs locations must be phased into `archive/docs/`.
  - Current filesystem has `archive/docs` and does not have `docs/_archive`.
  - Current `openspec/specs/directory-governance/spec.md:123-126` permits approved lifecycle targets such as `archive/`, `reports/`, and `var/`.

  Why the source document does not resolve it:
  - The proposal never mentions `archive/docs/`.
  - It justifies `_archive/` by sort order and discoverability, but does not address the existing OpenSpec lifecycle target.

  Recommendation:
  - Replace `docs/_archive/` with `archive/docs/` unless a new OpenSpec change explicitly modifies the file-organization spec.
  - Keep `docs/reports/README.md` as a routing/explanatory index that links to archived report clusters under `archive/docs/reports/`.

- [ ] **[HIGH]** The execution plan lacks the repo's required OpenSpec, approval, lifecycle classification, and verification gates for a structural documentation migration.

  Source: `docs/DOCUMENTATION_ARCHITECTURE_OPTIMIZATION_PROPOSAL.md:173-194`, `:196-210`, `:224`, `:234-236`, `:291-328`, `:345-352`

  Evidence checked:
  - The proposal plans broad archive/move/merge operations: `reports/`, `plans/`, `worklogs/`, `superpowers/`, `guides/`, `api/`, and `INDEX.md` conversions.
  - The proposal contains no `OpenSpec`, `approval`, `审批`, `canonical`, `trunk`, `archive_candidate`, `delete_candidate`, or `generated_reference` gate.
  - Current `architecture/STANDARDS.md:12-20` requires proposal-first approval for architecture/menu/UI/core pattern changes and says shared rules are centralized there.
  - Current `architecture/STANDARDS.md:22-25` separates evidence-only inventory from source-authorized implementation and says deletions/retirements require separate authorization and gates.
  - Current `architecture/STANDARDS.md:108` says architecture convergence, including directory merges and compatibility-layer retirement, must follow the Proposal-First Rule.
  - Current `openspec/specs/documentation-governance/spec.md:11-18` requires defining canonical trunks before cleanup and routing through trunks first.
  - Current `openspec/specs/documentation-governance/spec.md:43-45` requires classification as `canonical`, `supporting`, `report`, `plan`, `generated_reference`, `archive_candidate`, or `delete_candidate`.
  - Current `openspec/specs/documentation-governance/spec.md:63-65` allows deletion only after canonical replacement mapping, inbound-link cleanup, and retention checks are complete.
  - Current `openspec/specs/directory-governance/spec.md:151-154` requires explicit approval and verification commands for batches including directory merges or deletions.
  - `openspec list` showed active changes, but no active documentation-architecture migration change matching this proposal.

  Why the source document does not resolve it:
  - "grep before/after" at `:350` is not enough for this repo's governance bar.
  - The execution plan has steps and rough durations, but no OpenSpec `change-id`, no tasks checklist, no spec deltas, no lifecycle inventory manifest, and no concrete verification commands.

  Recommendation:
  - Convert the proposal into an OpenSpec change before execution, for example `refactor-documentation-architecture`.
  - Add deltas for `documentation-governance`, `file-organization`, and possibly `directory-governance` if any lifecycle target changes.
  - Add a manifest table per document family: current path, canonical trunk, lifecycle class, proposed action, inbound references, retention obligation, verification command.
  - Define commands such as `openspec validate <change-id> --strict`, link validation, generated index validation, inbound-reference scans, and before/after count reports.

- [ ] **[MED]** The numeric diagnosis mixes "all files" and "Markdown documents", which makes the scale and expected reduction misleading.

  Source: `docs/DOCUMENTATION_ARCHITECTURE_OPTIMIZATION_PROPOSAL.md:13-16`, `:23`, `:31-43`, `:175`, `:187-192`, `:198`, `:228`, `:336-341`

  Evidence checked:
  - The proposal says `docs/` has `2,871` document files and `reports/` has `1,970` files.
  - Current measured facts: `docs/` has 5,331 files total, 2,873 Markdown files; `docs/reports/` has 4,379 files total, 1,971 Markdown files.
  - The proposal's directory counts mostly match Markdown counts, not all files: `guides/` Markdown files are 283; `api/` Markdown files are 214 while all files are 233; `architecture/` Markdown files are 102 while all files are 103.
  - `reports/quality/` has 774 Markdown files but 1,550 total files, largely because `reports/quality/myweb-audit/` contains 1,306 total files.
  - The proposal says `20+` `INDEX.md`; current count is 78.

  Why the source document does not resolve it:
  - The proposal does not state the counting scope, command, exclusion rules, or whether "file" means Markdown only.
  - Expected effects such as `-85%` and `-97%` are therefore not reproducible.

  Recommendation:
  - Rewrite all metrics as scoped measurements, for example "Markdown files under `docs/`, excluding `.git`, `.worktrees`, `node_modules`".
  - Split Markdown docs from generated evidence/assets.
  - Add the exact measurement command to the proposal.

- [ ] **[MED]** P7 identifies missing `docs/ARCHITECTURE.md`, but the proposal never defines the architecture-document remediation.

  Source: `docs/DOCUMENTATION_ARCHITECTURE_OPTIMIZATION_PROPOSAL.md:28`, `:83-146`, `:162-171`, `:298`

  Evidence checked:
  - P7 says both `docs/PRODUCT.md` and `docs/ARCHITECTURE.md` are missing.
  - The target directory structure includes `PRODUCT.md` but does not include `ARCHITECTURE.md`.
  - The detailed remediation section only creates `docs/PRODUCT.md`.
  - The only `ARCHITECTURE.md` mention in the proposal is the P7 problem statement.
  - Current repo already has root `PRODUCT.md` and root `DESIGN.md`; root `PRODUCT.md:4-5` defines its status and references `architecture/STANDARDS.md`, `AGENTS.md`, `CLAUDE.md`, and `openspec/AGENTS.md`.
  - Root `PRODUCT.md:54-85` already captures Web product/design canon and route truth.
  - `docs/overview/项目总览.md:4-5` is explicitly historical/supporting, not current truth.

  Why the source document does not resolve it:
  - It says root `PRODUCT.md` is product planning, but current root `PRODUCT.md` is product/design context and Web canon, not just planning.
  - It does not define whether `docs/PRODUCT.md` becomes canonical, supporting, or a redirect to root `PRODUCT.md`.
  - It does not define whether `docs/ARCHITECTURE.md` should exist, or whether architecture truth should remain split across `architecture/STANDARDS.md`, `openspec/specs/`, and `docs/architecture/README.md`.

  Recommendation:
  - Either remove `docs/ARCHITECTURE.md` from P7 or add a concrete remediation.
  - If `docs/PRODUCT.md` is created, make it a thin reader-facing supporting doc with an explicit relationship to root `PRODUCT.md`, not a parallel product truth.

- [ ] **[MED]** The `INDEX.md` migration rule is too coarse for the current 78-file INDEX surface and could delete compatibility/generated indexes without classification.

  Source: `docs/DOCUMENTATION_ARCHITECTURE_OPTIMIZATION_PROPOSAL.md:224`, `:228`, `:234-236`, `:299`, `:317`, `:351`, `:367-369`

  Evidence checked:
  - The proposal says existing `INDEX.md` files are unified into `README.md` or deleted if automatic/no independent value.
  - Current facts: 78 `INDEX.md` files, 27 `README.md` files, and 20 `INDEX.md` files with same-directory `README.md`.
  - Current `docs/INDEX.md:3-5` already says it is generated navigation and not the unique truth for governance.
  - Current `docs/overview/README.md:26-30` says `docs/overview/INDEX.md` is retained as a legacy-link compatibility index.
  - Current `docs/overview/documentation-system.md:35-36` says subtree README/INDEX files can route readers but must not become parallel truth.

  Why the source document does not resolve it:
  - It has no per-INDEX classification as `generated_reference`, `supporting`, `archive_candidate`, or `delete_candidate`.
  - It uses "已有同级 README.md -> 删除 INDEX.md" without proving content equivalence or inbound-link safety.

  Recommendation:
  - Inventory all 78 `INDEX.md` files and classify each before mutation.
  - Treat generated and compatibility indexes as a distinct lifecycle class.
  - Only delete same-directory pairs after content equivalence and inbound references are checked.

- [ ] **[MED]** The `guides/` cleanup table has path-scope ambiguity, especially around `superpowers/`.

  Source: `docs/DOCUMENTATION_ARCHITECTURE_OPTIMIZATION_PROPOSAL.md:196-210`, `:310`, `:389`

  Evidence checked:
  - The section is titled `guides/` cleanup and says `superpowers/ (27 文件) -> _archive/`.
  - Current `docs/guides/superpowers/` has 3 Markdown files.
  - Current `docs/superpowers/` has 27 Markdown files.
  - Current `docs/guides/` has 23 direct child directories, not 20.

  Why the source document does not resolve it:
  - It does not say whether the intended source is `docs/superpowers/` or `docs/guides/superpowers/`.
  - It does not classify the `docs/superpowers/` family before archiving.

  Recommendation:
  - Replace shorthand directory names with exact source and destination paths.
  - Add lifecycle classification and inbound-link evidence for `docs/superpowers/` and `docs/guides/superpowers/` separately.

- [ ] **[LOW]** The relative-link recommendation is directionally aligned with eltdx, but the work item is under-scoped for this repo.

  Source: `docs/DOCUMENTATION_ARCHITECTURE_OPTIMIZATION_PROPOSAL.md:272`, `:287`, `:300`

  Evidence checked:
  - The eltdx methodology favors relative cross-references and gives explicit same-directory / parent-directory patterns.
  - Current `docs/` contains 737 absolute local Markdown links across 123 Markdown files.
  - Current high-value trunks such as `docs/README.md`, `docs/overview/documentation-system.md`, and `docs/operations/README.md` use `/opt/claude/mystocks_spec/...` links.

  Why the source document does not resolve it:
  - It says "fix all absolute path cross-references" but does not define exceptions, batch scope, link checker, or compatibility policy.

  Recommendation:
  - Make link conversion its own bounded batch.
  - Define whether absolute links are forbidden everywhere or only in reader-facing docs.
  - Add a link validation command and a pre/post absolute-link count.

## Verified Strengths

- The proposal correctly recognizes `docs/reports/` as the dominant documentation noise cluster.
- It correctly avoids applying eltdx's SDK-oriented `helpers/ + methods/` dual-entry model directly to a service/application repo.
- It correctly keeps `docs/INDEX.md` as generated auxiliary navigation rather than treating it as the canonical reader entrypoint.
- It correctly prefers archive/retention over immediate deletion in principle, but the archive destination and gates need to align with current repo truth.
- It correctly calls out absolute local links as a portability concern, but that needs a dedicated scoped migration.

## Recommended Rewrite Shape

1. Change the title from "文档架构优化方案" to "文档 canonical trunk 收敛与历史文档归档方案" to match current repo language.
2. Add a "Current Truth Sources" section that cites `docs/README.md`, `docs/overview/documentation-system.md`, `architecture/STANDARDS.md`, and the relevant OpenSpec specs.
3. Replace the "无分层体系" diagnosis with a narrower problem statement: "existing trunk map exists, but active/supporting/report/generated surfaces need further lifecycle classification and route compression."
4. Replace `docs/_archive/` with `archive/docs/`, unless the proposal explicitly changes the file-organization spec.
5. Add a lifecycle manifest before any move/delete:
   - document family
   - current path
   - current owner/trunk
   - lifecycle class
   - proposed action
   - inbound links
   - retention obligation
   - verification command
6. Split execution into approval-bound batches:
   - measurement/inventory only
   - entrypoint wording update
   - generated/compatibility index classification
   - report archival wave
   - guide taxonomy wave
   - link conversion wave
7. Add verification commands and acceptance criteria:
   - `openspec validate <change-id> --strict`
   - generated index validation
   - absolute-link count before/after
   - broken-link scan
   - inbound reference scan for moved directories
   - documentation count report using a committed script or one clearly documented command

