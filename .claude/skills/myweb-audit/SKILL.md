---
name: myweb-audit
description: Page-by-page frontend audit and repair orchestration for the web app. Use when the user wants route-based page inspection, API/render consistency checks, responsive and accessibility review, ArtDeco visual compliance checks, batch repair, and verification reporting. Not for product redesign, backend architecture changes, or large-scale refactors.
---

# MyWeb Audit

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

Use `myweb-audit` only when the user wants page-by-page frontend auditing, repair, and verification for the web application.

This skill standardizes route inventory, page batching, functional review, API/render consistency checks, visual and ArtDeco review, responsive and accessibility checks, repair, and verification reporting.

It also defines three lightweight execution artifacts for consistency:

- a batch `manifest`
- a normalized `findings schema`
- a final `closeout checklist`

These artifacts are the batch state truth for resumability and closeout. Do not rely only on the main agent's transient context memory.

## Version Notes

`v1.4` clarifies:

- role handoff and role boundaries
- repair scope and batch-level failure handling
- ArtDeco alignment with current repository truth
- batching rules, batch naming, and reporting consistency
- dedicated agent specs for each fixed audit role
- environment prerequisites, execution mode, and fallback behavior
- desktop-first breakpoint policy
- explicit repair approval gate before fixes

For version history and maintenance notes, see `references/CHANGELOG.md`.

## When to Use

Use this skill when the user asks to:

- inspect frontend pages one by one
- verify links, buttons, forms, dialogs, tables, charts, filters, and route behavior
- check whether API data matches visible rendered content
- validate loading, empty, error, disabled, and extreme-data states
- review spacing, sizing, alignment, typography, and layout quality
- validate responsive behavior and accessibility
- audit pages against the project's ArtDeco direction
- batch-scan routes and fix issues page by page

Use `Quick Mode` when the user asks for a single-page or very small-scope check without full batch orchestration.

## Do Not Use

Do not use this skill for:

- redefining product requirements or business rules
- unconstrained full-site visual redesign
- backend architecture changes, database changes, or API redesign
- large-scale refactors, file migrations, or cross-system restructuring
- generic code review tasks unrelated to page auditing

## Quick Mode

Use Quick Mode when all of the following are true:

- the request is limited to one page or one narrow route flow
- the user wants a fast check rather than a resumable batch run
- no multi-batch coordination is needed

Quick Mode rules:

- skip batch grouping
- skip manifest creation unless the user requests file artifacts
- run audit dimensions inline instead of as separate role outputs
- output a simplified inline report
- skip closeout checklist unless the user asks for a formal audit artifact

Full Mode remains the default for multi-page audits, repair waves, and resumable work.

## Operating Rules

- Follow repository-wide rules in `architecture/STANDARDS.md` and root `AGENTS.md`.
- Preserve the existing design system, route truth, and page family patterns.
- Prefer focused page-batch fixes over broad cosmetic edits.
- Do not change backend behavior by default. If a page issue depends on backend changes, report the dependency explicitly.
- Do not stop at listing issues. The default goal is `audit -> fix -> verify`.
- Keep v1 lightweight. Do not introduce new frameworks, automation platforms, or large support systems.

## Repository Alignment

When this skill touches ArtDeco-related judgment, use this priority order:

1. `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md`
2. `DESIGN.md`
3. `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md`
4. `docs/api/ArtDeco_System_Architecture_Summary.md`
5. `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`

For route truth and canonical page entry, always defer to:

- `web/frontend/src/router/index.ts`
- `docs/guides/frontend-structure.md`
- `web/frontend/src/views/<domain>/*.vue`

Do not treat `views/artdeco-pages/**` as the default truth source for all active business routes.

## Environment Prerequisites

Before running a live-page audit, confirm:

- frontend app is reachable on the actual run URL
- backend API is reachable at least for health or readiness checks when API verification is required
- a browser automation surface is available:
  - preferred: Playwright
  - acceptable fallback: equivalent browser/devtools automation

Execution surfaces:

- `live-audit`: routed page loaded in a reachable frontend runtime with browser tooling
- `code-review-only`: code inspection without confirmed live interaction

If browser tooling or app reachability is unavailable, downgrade to `code-review-only` and mark verification as partial.

## Workflow

Run the workflow in this order:

1. Scan real routes, menu entries, and page entry files.
2. Build a page inventory and split pages into batches of 3-5 by business module.
3. Create a minimal batch manifest using `references/manifest-template.md`.
4. Audit the current batch using the fixed audit roles defined below.
5. Normalize findings into the shared structure in `references/findings-schema-example.md`.
6. Merge findings, remove duplicates, and sort by severity.
7. Identify shared-impact candidates before repair and record the decision in the batch state.
8. Present merged findings to the user for repair approval.
9. Fix only the issues explicitly approved by the user for the current batch.
10. Run focused regression verification on the repaired areas using the declared verification policy.
11. Output a per-page report and a batch summary.
12. Run the closeout checklist in `references/closeout-checklist.md`.
13. Continue to the next batch until the requested scope is complete.

Do not analyze the whole site first and postpone all edits. Work batch by batch.

## Role Handoff

Use this handoff order:

1. `route-inventory` produces the canonical page list, module grouping, and batch order.
2. The current batch is passed to:
   - `functional-audit`
   - `data-state-audit`
   - `visual-artdeco-audit`
   - `responsive-a11y-audit`
3. Findings from all audit roles are merged, deduplicated, and sorted by severity.
4. Shared-impact candidates are identified and the merged findings are presented for user approval.
5. Approved frontend fixes are applied.
6. The repaired areas are regression-checked and recorded in the page report and batch report.

Do not let audit roles drift into each other's scope. Each role should produce findings in its own dimension, then hand off to the repair/verification step.

`Shared Impact` is a pre-repair orchestrator decision, not a report-only appendix added after fixes land.

## Execution Mode

Default execution mode:

- `route-inventory`: sequential and blocking
- `functional-audit`, `data-state-audit`, `visual-artdeco-audit`, `responsive-a11y-audit`: parallel when agent capacity and browser tooling are available
- merge, deduplication, shared-impact review, approval, repair, and verification: sequential

Failure behavior:

- one audit role failing does not block the others from completing
- failed roles must be marked `incomplete`
- if all live-audit roles fail because the environment is not usable, downgrade the batch to `code-review-only` or defer it

High-frequency environment fallback branches that must be recorded explicitly:

- Playwright permission failure or artifact-path failure
- existing frontend runtime or PM2 port conflict
- dirty worktree that requires staged-scope switching before closeout
- sub-agent capacity exhaustion or delegation unavailability

These are workflow states, not incidental notes. Record the chosen fallback in the manifest and final closeout.

## Code-Review-Only Rules

When the run is downgraded to `code-review-only`, do not stop at generic static review.

The audit must explicitly check for:

- inert interactions:
  - empty click handlers
  - emitted events without meaningful consumers
  - controls that mutate local state but do not affect the rendered result
- truth-source drift:
  - router meta vs page config vs service endpoint mismatch
  - wrapper page vs canonical page behavior drift
- data resilience gaps:
  - partial-success responses incorrectly degraded to global empty/error states
  - payload normalization inconsistency between closely related pages
- desktop redline violations:
  - unsupported mobile-width media queries
  - layout logic built around unsupported mobile breakpoints

`code-review-only` findings should prefer concrete code-path evidence over speculative runtime claims.

## Reporting Model

Reports in this skill must preserve both layers of the audit:

1. `agent findings`
   - what each audit role found inside its own scope
2. `main skill decisions`
   - how findings were merged, deduplicated, prioritized, repaired, verified, or deferred

Do not collapse all findings into a single final summary without showing which audit role surfaced the issue and how the main skill handled it.

When reports are written to files, keep the artifact relationship explicit:

- one batch manifest per batch
- one or more page reports per batch
- one batch report per batch
- one closeout checklist result per completed requested scope

Manifest minimum truth for every Full Mode batch:

- requested scope and route set
- route class (`canonical-page`, `detail-page`, or `compatibility-redirect`)
- completed pages and pending pages
- fixed files
- validation status
- staged scope
- shared impact
- verification policy

## Role Boundaries

Use these role boundaries to avoid overlap:

- `route-inventory`
  - defines page scope, canonical entry, and batch grouping
  - does not judge API correctness, visual quality, or interaction quality
- `functional-audit`
  - judges operability, interaction flow, and user-task completion
  - does not judge ArtDeco style or backend/API correctness
- `data-state-audit`
  - judges request/render consistency, state coverage, refresh logic, and display-format correctness
  - may flag data presentation problems only when they break semantic correctness or readability of returned data
  - does not judge pure visual style or design-language preference
- `visual-artdeco-audit`
  - judges hierarchy, spacing, framing, typography treatment, token alignment, and ArtDeco compliance
  - may flag visual data presentation problems only when they damage comprehension
  - does not confirm API correctness or backend behavior
- `responsive-a11y-audit`
  - judges breakpoint stability, overflow, focus, click target size, contrast, and keyboard access
  - does not judge business logic correctness

## Fixed Audit Roles

Use these fixed roles when splitting work. They define responsibilities, not a required implementation mechanism.

Agent spec mapping:

- `route-inventory` -> `.claude/agents/myweb-audit-route-inventory.md`
- `functional-audit` -> `.claude/agents/myweb-audit-functional-audit.md`
- `data-state-audit` -> `.claude/agents/myweb-audit-data-state-audit.md`
- `visual-artdeco-audit` -> `.claude/agents/myweb-audit-visual-artdeco-audit.md`
- `responsive-a11y-audit` -> `.claude/agents/myweb-audit-responsive-a11y-audit.md`

When a run is delegated into subagents or separate role prompts, use these files as the role-specific source of truth.

### `route-inventory`

Responsibility:

- scan real routes, menu entries, and page ownership
- identify canonical page entry files
- generate page inventory and batch grouping suggestions

Output:

- page list
- module/group
- page purpose
- batch suggestion
- priority notes
- route class
- canonical target for compatibility redirects or aliases
- special-route verification notes

### `functional-audit`

Responsibility:

- inspect buttons, links, forms, filters, sorting, pagination, dialogs, tabs, submit flows, navigation, and back/return flows
- focus on actual operability and user task completion

Output:

- severity
- title
- trigger
- expected
- actual
- evidence
- repair_target
- can_fix_frontend
- dependency
- verification_surface

### `data-state-audit`

Responsibility:

- inspect API URL, method, params, trigger timing, visible render consistency, and display format correctness
- verify that visible page content matches returned data
- cover loading, empty, error, disabled, and extreme-data states

Output:

- severity
- title
- trigger
- expected
- actual
- evidence
- repair_target
- can_fix_frontend
- dependency
- verification_surface

### `visual-artdeco-audit`

Responsibility:

- inspect typography treatment, spacing, alignment, hierarchy, borders, cards, tables, chart proportions, and section rhythm
- evaluate ArtDeco compliance using the rubric in `references/artdeco-rubric.md`

Output:

- severity
- title
- trigger
- expected
- actual
- evidence
- repair_target
- can_fix_frontend
- dependency
- verification_surface

### `responsive-a11y-audit`

Responsibility:

- inspect responsive behavior at `1920`, `1440`, and `1280`
- inspect overflow, clipping, overlap, horizontal scroll, focus visibility, click target size, contrast, and basic labeling

Output:

- severity
- title
- trigger
- expected
- actual
- evidence
- repair_target
- can_fix_frontend
- dependency
- verification_surface

## Repair Scope Rules

Repairs are in scope when they are limited to the current frontend batch and fit one of these categories:

- route or link target correction
- page-local structure and layout fixes
- component composition fixes within the page family
- state rendering fixes for loading, empty, error, disabled, or extreme-data states
- token-aligned style fixes
- interaction fixes for buttons, forms, tabs, dialogs, filters, sorting, and pagination
- responsive and accessibility fixes within the current page batch

Repairs are out of scope when they require:

- product requirement redefinition
- backend contract changes
- database or schema changes
- architecture-level refactors
- broad visual redesign across unrelated page families
- migrating large numbers of files or redefining component ownership

When a fix is out of scope, record it as a deferred item with reason and dependency.

`can_fix_frontend` must answer whether the current approved frontend batch can repair the issue without backend/API redesign or out-of-scope platform work.

`approved frontend scope` means the user has explicitly confirmed which merged findings should be repaired in the current batch.

## Required Checks Per Page

For every page, check all items in `references/audit-checklist.md`.

Minimum required dimensions:

- page structure completeness
- functional and interaction correctness
- API data and rendered content consistency
- visual hierarchy, sizing, spacing, and proportion
- responsive layout behavior
- accessibility and usability
- global design consistency
- ArtDeco compliance
- cross-source truth consistency for page config, route meta, and canonical data entry

## Required States Per Page

Every page must cover these states:

- default state
- loading state
- empty-data state
- error state
- disabled or no-permission state
- extreme-data state

Extreme-data state should be judged relative to the page's actual container, component density, and data shape.

At minimum, inspect:

- text that is materially longer than the intended label or field width
- numeric values that materially exceed normal display length for the module
- empty or null fields inside otherwise populated modules
- dense tables, dense lists, or crowded chart labels
- mixed-state cards where some fields are present and others are missing

Do not force a single numeric threshold across all page types. Judge whether the data remains readable, aligned, and structurally stable.

## Failure Handling

If route scanning, page loading, or API inspection cannot complete, do not stop the workflow silently.

Handle failures as follows:

- route cannot be resolved:
  record the route gap, identify the nearest canonical source, and continue with the rest of the batch
- page fails to load:
  classify as at least `High`, record the failure condition, and continue with remaining pages
- API cannot be reached or verified:
  record verification as partial, inspect the page's state handling, and mark the dependency explicitly
- canonical entry is ambiguous:
  defer to router truth, frontend structure guidance, and current domain entry files before auditing the page
- compatibility redirect or alias route is under review:
  verify canonical target, query/hash preservation, auth interaction, and post-login destination rather than treating it as a normal page body

If the whole batch fails to load or cannot be resolved:

- stop repair for that batch
- produce a batch-level blocking report
- mark the batch as deferred
- record the root blocking condition
- continue only after route truth, app availability, or environment readiness is re-confirmed

Never fabricate verification results when the underlying route, page, or API could not be confirmed.

## Environment Fallback

Handle environment-level failures explicitly:

- browser tool unavailable:
  downgrade to `code-review-only`, mark findings `verification_surface: code-review-only`, and set verification to partial
- frontend or backend port conflict:
  use the actual reachable URL if already provided by the environment and record it in the manifest
- agent capacity exhausted:
  fall back to sequential inline execution and skip parallel dispatch
- dirty worktree or staging conflict during repair:
  stage target files individually and avoid blanket staging as the batch verdict source
- report output path not writable:
  emit inline artifacts in the response and record file output as skipped

## Execution Artifacts

Use these lightweight artifacts to keep runs reproducible and easy to resume:

### Batch Manifest

Create one manifest per batch before auditing starts.

The manifest is the planning and scope-control artifact for the current batch. It should record:

- audit run id
- batch id
- module and route scope
- canonical page entries
- assigned audit roles
- environment assumptions
- verification intent

Use the template in `references/manifest-template.md`.

### Findings Schema

Normalize all role outputs to the same schema before merge and deduplication.

Every finding should capture at least:

- page and route
- source role
- severity
- issue type
- reproduction or trigger
- expected vs actual behavior
- evidence
- repair target or dependency
- verification surface
- verification completeness

Use the structure and example in `references/findings-schema-example.md`.
Use `references/findings-schema.json` when a run needs machine validation of finding payloads.

### Closeout Checklist

Before declaring the requested scope complete, run the closeout checklist.

The checklist is the final quality gate for this skill. It must confirm:

- scope completion
- manifest/report completeness
- fix vs defer accounting
- verification coverage
- residual risk disclosure
- repository-rule compliance

Use the template in `references/closeout-checklist.md`.

## ArtDeco Alignment Rules

ArtDeco judgment in this skill must align with the current repository truth:

- active design identity is `Original ArtDeco + A-share financial semantics + high-density quant workbench`
- route truth and ArtDeco workbench truth are not the same thing
- typography should respect the current ArtDeco stack:
  - headings: `Cinzel`
  - body: `Barlow`
  - numeric/meta emphasis: `JetBrains Mono`
- visual hierarchy must follow the existing repository scale and tokenized patterns rather than inventing new type ramps
- page title, section title, module title, body text, and metadata must remain visibly tiered
- financial semantics must preserve A-share convention:
  - rise/profit: red
  - down/loss: green
- visual fixes should prefer existing ArtDeco tokens, spacing scales, grid rhythms, and shared components
- do not reintroduce decorative brand chrome that current docs say has already been reduced
- do not use local hardcoded colors, spacing, radius, shadow, or transitions when tokenized alternatives exist

## Severity

Use this severity model:

- `Blocking`: page unusable, critical flow broken, major layout breakage, critical link failure
- `High`: core user task degraded, important state missing, layout unstable in common use
- `Medium`: usable but poor experience, visual hierarchy confused, responsive issues noticeable
- `Low`: polish issues, minor spacing/alignment inconsistencies, small visual defects

When consolidated findings disagree on severity, use the highest severity among contributing roles.

## Reference Order

Read references in this order:

1. `references/audit-checklist.md`
2. `references/batching-rules.md`
3. `references/manifest-template.md`
4. `references/findings-schema-example.md`
5. `references/findings-schema.json`
6. `references/artdeco-rubric.md`
7. `references/report-template.md`
8. `references/artifact-conventions.md`
9. `references/example-audit-run.md`
10. `references/closeout-checklist.md`
11. `references/CHANGELOG.md`

Use the first two to decide what to audit and how to batch work.
Use the manifest template to lock batch scope before auditing.
Use the findings schema example to normalize outputs before merge and deduplication.
Use the JSON schema when a run needs machine validation or programmatic post-processing.
Use the ArtDeco rubric only for visual and design-language judgment.
Use the report template before writing final findings.
Use the artifact conventions when a run needs consistent file output and archival structure.
Use the example run reference when you need a concrete Quick Mode or Full Mode execution pattern.
Use the closeout checklist before declaring the requested scope complete.

## Default Report Behavior

Unless the user explicitly asks to write report files, output the page report and batch report directly in the assistant response using the templates in `references/report-template.md`.

Whether reports are inline or written to files, they must include:

- per-role findings summary
- consolidated issues after merge and deduplication
- main skill repair decisions
- fixes applied
- verification results
- deferred items or residual risks

If the user requests file-based artifacts, write them in this order:

1. batch manifest
2. page report(s)
3. batch report
4. closeout checklist result
