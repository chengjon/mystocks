# ArtDeco Impeccable Line Summary And Next Plan

> Date: 2026-05-29
> Scope: Web frontend ArtDeco design governance and page craft line.
> Method: impeccable design workflow under OpenSpec / project proposal-first gates.

## 1. Line Goal

Use impeccable as a Web-side design governance workflow, not as a broad full-site beautification pass.

The line goal remains:

- audit the already implemented Web ArtDeco design
- improve page design quality
- improve component reuse only after repeated page patterns are proven
- tighten visual token use
- make runtime states part of the interface
- strengthen verification gates
- align implementation with the current ArtDeco document system

The operating rule is unchanged: critique and shape first, source implementation only after explicit approval.

## 2. Completed Work

### 2.1 Governance And Context

| Area | Status | Evidence |
|---|---|---|
| Impeccable context refresh | Completed in two steps | `PRODUCT.md` / `DESIGN.md` were committed on 2026-05-10 in `93f6d6974`, then refreshed again in the current dirty worktree for this Web ArtDeco/page-design line |
| Primary alignment plan | Completed | `docs/reports/tasks/2026-05-28-artdeco-web-design-alignment-plan.md` |
| OpenSpec gate | Completed as active change tasks; not yet archived | `openspec/changes/add-artdeco-impeccable-design-gate/` |
| Governance spec | Updated / available | `openspec/specs/artdeco-design-governance/spec.md` |
| Next-route batch planning | Completed | `docs/reports/tasks/2026-05-29-artdeco-impeccable-next-route-batch-plan.md` |

OpenSpec note:

- `add-artdeco-impeccable-design-gate` tasks are marked complete.
- The change is still active under `openspec/changes/`.
- It should be archived only after the current uncommitted trade positions slice is either committed into the intended batch or explicitly excluded from the OpenSpec closeout; see §5 Phase 1 for the decision point.

### 2.2 Page Pilot 1: Market Realtime

| Item | Status |
|---|---|
| Target | `web/frontend/src/views/market/Realtime.vue` |
| Critique | `docs/reports/tasks/2026-05-28-artdeco-market-realtime-critique.md` |
| Shape brief | `docs/reports/tasks/2026-05-28-artdeco-market-realtime-shape-brief.md` |
| Approval packet | `docs/reports/tasks/2026-05-28-artdeco-market-realtime-approval-packet.md` |
| Implementation report | `docs/reports/tasks/2026-05-28-artdeco-market-realtime-implementation-report.md` |
| Commit | `de0c5b8c9 feat(web): add ArtDeco realtime design gate pilot` |

Implemented direction:

- compact market data workbench
- stronger control/status row
- runtime metadata preserved for E2E compatibility
- ArtDeco token discipline kept
- route-specific implementation without premature shared extraction

Verification recorded in the report:

- `npm run type-check -- --pretty false`: pass, 0 type errors
- targeted Chromium E2E for market data: 18 passed, 0 failed, 0 skipped
- GitNexus impact: LOW risk
- GitNexus detect/refresh remained partially blocked by tooling timeouts

### 2.3 Page Pilot 2: Risk Alerts

| Item | Status |
|---|---|
| Target | `web/frontend/src/views/risk/Alerts.vue` |
| Critique | `docs/reports/tasks/2026-05-29-artdeco-risk-alerts-critique.md` |
| Shape brief | `docs/reports/tasks/2026-05-29-artdeco-risk-alerts-shape-brief.md` |
| Implementation report | `docs/reports/tasks/2026-05-29-artdeco-risk-alerts-implementation-report.md` |
| Commit | `8ed6c91d0 feat(web): craft ArtDeco risk alerts triage desk` |

Implemented direction:

- risk alert triage desk
- clearer severity-first information hierarchy
- runtime status and error handling strengthened
- focused tests added / updated
- route-level E2E coverage preserved

Verification recorded in the report:

- focused Vitest: 1 file, 8 tests passed
- `npm run type-check -- --pretty false`: pass
- Chromium E2E `Risk-Alerts`: 4 tests passed
- ArtDeco token and lint checks completed

### 2.4 Page Pilot 3: Trade Positions

| Item | Status |
|---|---|
| Target | `web/frontend/src/views/trade/Center.vue` |
| Route | `/trade/positions` |
| Critique | `docs/reports/tasks/2026-05-29-artdeco-trade-positions-critique.md` |
| Shape brief | `docs/reports/tasks/2026-05-29-artdeco-trade-positions-shape-brief.md` |
| Implementation report | `docs/reports/tasks/2026-05-29-artdeco-trade-positions-implementation-report.md` |
| Commit | This scoped commit: `feat(web): craft ArtDeco trade positions review desk` |

Implemented direction:

- positions review workbench
- `全部 / 盈利 / 亏损 / 高仓位 / 需关注` review segments
- runtime status strip
- Chinese operational copy
- route-level `data-test` hooks
- transform-based position bar instead of width animation
- row flags for loss / high-weight review

Verification completed:

- `npm run test -- src/views/trade/__tests__/Center.spec.ts`: 1 file, 5 tests passed
- `npx eslint src/views/trade/Center.vue`: pass
- `node scripts/check-artdeco-tokens.js --target-file src/views/trade/Center.vue`: pass
- `npm run type-check -- --pretty false`: pass, 0 type errors
- `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Positions" --project=chromium`: Chromium, 4 passed
- `npx impeccable --json src/views/trade/Center.vue`: `[]`
- 1440px browser screenshot: `/tmp/trade-positions-artdeco-1440-final.png`

GitNexus closeout status:

- GitNexus pre-edit impact returned LOW risk.
- `.gitnexusignore` now excludes generated Grafana / Prometheus local monitoring data so GitNexus can address the repo again as `mystocks`.
- `gitnexus analyze --index-only --max-file-size 64 --worker-timeout 10` refreshed the index registry but still exited non-zero after worker timeouts.
- `gitnexus_detect_changes(scope="staged")` was rerun against the staged target batch and timed out at 120s; CLI `gitnexus detect-changes --scope staged --repo mystocks` also hung beyond the local patience window and was killed.
- Post-commit GitNexus refresh was attempted with the same bounded analyze command, exceeded the MCP 120s call limit, and the current-repo analyze process was killed.

## 3. Patterns Proven So Far

The three page pilots have converged on a useful Web ArtDeco page grammar:

1. Route-specific workbench framing is better than decorative hero composition.
2. Runtime state belongs near the primary work surface, not buried as incidental metadata.
3. Dense financial tables need review lenses or triage controls before they need more ornament.
4. User-facing copy should be Chinese-first and operational; internal English scaffolding should not leak.
5. ArtDeco gold should structure hierarchy; risk, PnL, stale, degraded, and error states should carry their own semantic emphasis.
6. Stable `data-test` hooks are part of design quality for routed operational pages.
7. Shared extraction should wait until repeated page patterns are compared side-by-side; the next extraction phase is that comparison, not immediate shared component code.

## 4. Closeout Status

| Item | Status | Recommended action |
|---|---|---|
| Trade positions slice | Committed in this scoped batch | No further action in this slice |
| OpenSpec change | Tasks complete, strict validation passed, archive ownership decision completed | Do not archive from root; root canonical spec belongs to earlier 2026-05-12 ArtDeco governance archives |
| GitNexus staged detect | Repo index addressable again, but staged detect still times out | Keep `.gitnexusignore`; investigate GitNexus detect performance separately before relying on it as a blocking gate |
| Shared component extraction | Deferred; documentation-only analysis completed | Use `docs/reports/tasks/2026-05-29-artdeco-page-pilot-extraction-analysis.md` as the approval boundary before any extraction proposal |
| Next routed page | `trade/Signals.vue` critique completed | Shape brief is the next design-only step; implementation still requires explicit approval |

## 5. Recommended Next Sequence

### Phase 0: Close Current Slice

Priority: P0.

Tasks:

- [ ] 0.1 Review the current target diff for `trade/Center.vue`, `trade/__tests__/Center.spec.ts`, `phase3-mainline-matrix.spec.ts`, and the three trade-position reports.
- [ ] 0.2 Rerun focused verification immediately before commit.
- [ ] 0.3 Decide whether to commit the trade positions slice now.
- [ ] 0.4 If committing, use a scoped commit such as `feat(web): craft ArtDeco trade positions review desk`.
- [ ] 0.5 Record the commit hash in `2026-05-29-artdeco-trade-positions-implementation-report.md`.

Recommended verification before commit:

```text
# Run from web/frontend/
npm run test -- src/views/trade/__tests__/Center.spec.ts
npx eslint src/views/trade/Center.vue
node scripts/check-artdeco-tokens.js --target-file src/views/trade/Center.vue
npm run type-check -- --pretty false
npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Positions" --project=chromium

# Run from repository root
git diff --check -- <target files>
```

GitNexus closeout:

- [x] 0.6 Add safe `.gitnexusignore` exclusions for generated Grafana / Prometheus local monitoring data.
- [x] 0.7 Rerun `gitnexus analyze --index-only --max-file-size 64 --worker-timeout 10` and confirm the repo is addressable again.
- [x] 0.8 Stage only target files and rerun `gitnexus_detect_changes(scope="staged")`.
- [ ] 0.9 Investigate staged detect timeout as a separate GitNexus performance/tooling task.

### Phase 1: OpenSpec Closeout

Priority: P0 after Phase 0.

Tasks:

- [x] 1.1 Run `openspec validate add-artdeco-impeccable-design-gate --strict`.
- [x] 1.2 Confirm `openspec/changes/add-artdeco-impeccable-design-gate/tasks.md` accurately reflects the completed governance-gate work.
- [x] 1.3 Decide whether this OpenSpec change should include only the Realtime pilot or the full three-page governance pilot.
- [x] 1.4 Run archive ownership preflight for the existing `openspec/specs/artdeco-design-governance/` path.
- [x] 1.5 Decide root canonical spec ownership for `openspec/specs/artdeco-design-governance/spec.md`.
- [ ] 1.6 Archive or merge the change only through a deliberate spec-merge task, not from the dirty root worktree.

Decision point:

- Current decision: treat `add-artdeco-impeccable-design-gate` as the governance gate; keep the three-page pilot evidence in task reports.
- Archive is deferred because `openspec/specs/artdeco-design-governance/` already exists as an untracked canonical spec path in the dirty worktree.
- Archive preflight report: `docs/reports/tasks/2026-05-29-artdeco-openspec-archive-ownership-preflight.md`.
- A clean archive candidate already exists in `.worktrees/artdeco-archive-preflight-de0c5b8c9` at `efa776cf0 chore(openspec): archive ArtDeco design gate change`, but root has a different untracked canonical spec with nine ArtDeco governance requirements.
- Ownership decision report: `docs/reports/tasks/2026-05-29-artdeco-spec-ownership-decision.md`.
- Root `openspec/specs/artdeco-design-governance/spec.md` is the combined canonical output of `2026-05-12-align-business-route-status-and-tooltip-surfaces` and `2026-05-12-align-artdeco-stateful-primitives-with-design`, not the current impeccable gate change.

### Phase 2: Extract Pattern Analysis

Priority: P1.

This should be documentation-only first. Phase 2 is the side-by-side comparison required by §3 item 7; its output is an extraction analysis / shape brief, not shared component implementation.

Recommended command intent:

```text
$impeccable extract Realtime Alerts Positions ArtDeco runtime workbench patterns
```

Tasks:

- [x] 2.1 Compare `market/Realtime.vue`, `risk/Alerts.vue`, and `trade/Center.vue`.
- [x] 2.2 Identify repeated structure across header bands, control rows, runtime strips, data panels, and table states.
- [x] 2.3 Decide which repetition is real enough to extract.
- [x] 2.4 Produce a documentation-only extraction analysis before touching shared components.

Output:

- `docs/reports/tasks/2026-05-29-artdeco-page-pilot-extraction-analysis.md`

Candidate extraction assets:

| Candidate | Priority | Reason |
|---|---|---|
| `ArtDecoRuntimeStatusStrip` | P1 | Repeated verified / refreshing / stale / degraded / error state grammar |
| `ArtDecoReviewSegments` | P1 | Repeated route-local triage control grammar |
| `ArtDecoDataWorkbenchHeader` | P2 | Useful but more page-specific; risk of over-generalization |
| `ArtDecoDataPanel` | P2 | Potential table/status shell, but needs one more page to prove API shape |

Extraction guardrail:

- Do not extract page-specific API, labels, financial semantics, or route-specific data transformation into shared components.

### Phase 3: Next Route Critique And Shape

Priority: P1.

Recommended next target:

```text
web/frontend/src/views/trade/Signals.vue
```

Why:

- 711 lines
- high table/reference density
- about 20 error-tagged lines in a line-based scan; identifier occurrence counts are higher
- 0 `data-test` references
- 4 `title` prop bindings
- direct fit with signal monitoring and trade workflow
- complements the positions page without broadening into system settings too early

Planned sequence:

- [x] 3.1 `$impeccable critique web/frontend/src/views/trade/Signals.vue`
- [x] 3.2 Save critique report under `docs/reports/tasks/`.
- [x] 3.3 `$impeccable shape trade signals ArtDeco signal trust desk`
- [ ] 3.4 Wait for explicit approval before implementation.
- [ ] 3.5 Implement only the approved slice.

Critique report:

- `docs/reports/tasks/2026-05-29-artdeco-trade-signals-critique.md`

Shape brief:

- `docs/reports/tasks/2026-05-29-artdeco-trade-signals-shape-brief.md`
- status: awaiting explicit user approval
- implementation gate: no Vue, SCSS, router, API, test, or shared component changes until approval

Critique verdict:

- good token discipline and real runtime-state foundations
- P0/P1 issues are desktop constraint drift via `@media`, missing route-level `data-test` hooks, runtime trust state not being prominent enough, and canonical route dependence on `artdeco-pages` internals
- no implementation should begin before a shape brief is approved

Secondary candidates after `trade/Signals.vue`:

| Candidate | Priority | Why |
|---|---|---|
| `web/frontend/src/views/trade/Reconciliation.vue` | P1 | Contains raw hex colors and reconciliation workflow risk; good token/governance target |
| `web/frontend/src/views/system/Settings.vue` | P1 | Operational settings page, high runtime/error density, no `data-test` hooks |
| `web/frontend/src/views/risk/Overview.vue` | P2 | Complements `risk/Alerts.vue` with broader risk posture |
| `web/frontend/src/views/data/FundFlow.vue` | P2 | Data-heavy table route, useful after trade/risk patterns stabilize |

### Phase 4: Verification Gate Hardening

Priority: P1/P2.

Tasks:

- [ ] 4.1 Add targeted Playwright coverage for new Trade Positions segment filters and filtered-empty state.
- [ ] 4.2 Add a route-level ArtDeco verification checklist for critique/shape/craft reports.
- [ ] 4.3 Define minimum `data-test` hooks expected on data-heavy pages.
- [ ] 4.4 Track `npx impeccable --json <page>` output in each implementation report.

## 6. Recommended Immediate Next Action

Do not start a new route yet.

The immediate next action should be:

1. Keep `add-artdeco-impeccable-design-gate` out of root archive mutation unless a separate spec-merge task is approved.
2. Treat `.worktrees/artdeco-archive-preflight-de0c5b8c9` / `efa776cf0` as the isolated archive candidate for this line.
3. Use the extraction analysis as the approval boundary before any shared component proposal.
4. Draft the `trade/Signals.vue` shape brief only if the user wants to continue the next design-only step.

Only after the shape brief is explicitly approved should any `trade/Signals.vue` implementation begin.
