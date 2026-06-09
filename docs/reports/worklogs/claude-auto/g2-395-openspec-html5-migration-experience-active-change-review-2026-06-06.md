# G2.395 OpenSpec HTML5 migration experience active-change review / no-source

## Boundary

Mode: `no-source`.

Scope is limited to:

`openspec/changes/implement-html5-migration-experience-optimization/`

This node reviews the dirty HTML5 migration active change and records whether it is ready for a formal acceptance package. It does not edit, restore, delete, stage, or commit any file.

Explicitly out of scope:

- `openspec/specs/**` modified active specs.
- Other OpenSpec active changes.
- Frontend source, tests, build output, or runtime assets.

## Evidence Summary

- Current HEAD: `5423b16a6 docs(openspec): update frontend restructure review tasks`.
- Staged files during this review: 0.
- Dirty shape:
  - `M openspec/changes/implement-html5-migration-experience-optimization/design.md`
  - `M openspec/changes/implement-html5-migration-experience-optimization/proposal.md`
  - `M openspec/changes/implement-html5-migration-experience-optimization/specs/html5-web-platform-optimization/spec.md`
  - `M openspec/changes/implement-html5-migration-experience-optimization/tasks.md`
  - `?? openspec/changes/implement-html5-migration-experience-optimization/tasks-review.md`
- Tracked diff size:
  - `design.md`: `+12/-1`
  - `proposal.md`: `+12/-1`
  - `spec.md`: `+10/-1`
  - `tasks.md`: `+516/-85`
- `openspec validate implement-html5-migration-experience-optimization --strict`: exit code 0.
- `openspec validate --changes --strict`: 16 passed, 0 failed.
- `openspec validate --specs --strict`: 47 passed, 0 failed.

## Content Review

The dirty set is internally shaped as a repo-truth disposition update:

- `design.md`, `proposal.md`, and the delta spec add current execution-boundary notes.
- The added notes explicitly prevent overclaiming: desktop-only scope, 7-domain menu truth, partial PWA closure, partial IndexedDB closure, placeholder worker boundaries, and unclosed rollout / monitoring / training evidence.
- `tasks.md` expands from 593 lines to 1024 lines and updates task evidence.
- `tasks.md` changes the task ledger from `56 done / 61 open` to `71 done / 48 open`.
- The delta spec remains structurally stable at `8` requirements and `20` scenarios.
- `tasks-review.md` records `APPROVE_WITH_NOTES` and keeps 2026-05-08 / 2026-05-10 / 2026-05-11 disposition history.

## Task Ledger Delta

The main task status movement is concentrated in evidence-backed closeout sections:

| Section | Old done/open | New done/open | Meaning |
|---|---:|---:|---|
| `1.2 Dependency Management` | `2/5` | `5/2` | Style gate and dependency evidence updated. |
| `1.3 Testing Infrastructure` | `7/1` | `11/0` | Coverage baseline and related stale-test fixes marked closed under narrower repo-local meaning. |
| `2.1 PWA Foundation Setup` | `3/2` | `4/1` | Desktop-only manifest asset consistency closed; active PWA plugin remains open. |
| `2.3 IndexedDB Integration` | `4/2` | `5/0` | Storage quota helper/browser-surface closure added. |
| `2.8 Accessibility Enhancements` | `0/5` | `1/4` | Accessibility tooling/audit evidence partially closed. |
| `3.1 Architecture Integration Validation` | `0/4` | `2/2` | Integration evidence partially closed. |
| `3.2 End-to-End Testing` | `0/4` | `1/3` | E2E evidence partially closed. |
| `3.3 Production Deployment Prep` | `1/3` | `2/2` | Build/static evidence partially closed. |
| `Functional Validation` | `2/3` | `3/2` | Validation evidence partially closed. |

## Reference Check

A path-reference scan found 109 referenced repo paths across the five dirty files.

Findings:

- Most referenced `docs/reports/quality/html5-migration-*.md` evidence files exist.
- Apparent missing `web/frontend/package.js` and `web/frontend/public/manifest.js` are scanner false positives caused by matching the `.js` prefix inside `.json`; the actual references are `package.json` and `manifest.json`.
- `web/frontend/dist/workers/protocol.js` and `web/frontend/public/workers/protocol.js` are intentionally missing in the task text and are documented as blockers.
- `web/frontend/src/views/monitoring/composables/useRiskDashboard.ts` is currently missing, but `tasks-review.md` still lists it as `confirmed`.

The missing `useRiskDashboard.ts` reference is not an OpenSpec validation failure, but it is a review-evidence drift. It should be resolved before accepting the whole HTML5 dirty package.

## Decision

Disposition: valid active change, not ready for immediate full acceptance.

Reasoning:

- OpenSpec structure validates.
- The dirty package mostly improves audit accuracy and prevents overclaiming.
- The package is large and crosses design, proposal, delta spec, task ledger, and review artifact.
- `tasks-review.md` is useful and should probably be included in the eventual package, but it contains at least one stale `confirmed` file reference that must be corrected or explicitly marked historical before acceptance.

## Recommended Next Nodes

1. `G2.396 openspec html5 migration review-evidence correction / spec-authorized`
   - Scope should be limited to `tasks-review.md` and, only if needed, the exact lines in `tasks.md` that reference `web/frontend/src/views/monitoring/composables/useRiskDashboard.ts`.
   - Goal: resolve whether the missing composable is historical, moved, or an invalid current evidence claim.
   - Required gates:
     - staged path allowlist
     - `openspec validate implement-html5-migration-experience-optimization --strict`
     - `openspec validate --changes --strict`
     - `git diff --cached --check`
     - GitNexus staged detection

2. `G2.397 openspec html5 migration experience active-change acceptance / spec-authorized`
   - Only after G2.396 resolves the stale evidence reference.
   - Candidate scope:
     - `design.md`
     - `proposal.md`
     - `specs/html5-web-platform-optimization/spec.md`
     - `tasks.md`
     - `tasks-review.md`
   - Do not stage `openspec/specs/**`.
   - Do not stage unrelated frontend source/test/build files.

## Residual Notes

The current active spec modifications under `openspec/specs/**` remain excluded and should continue through the active-spec residual inventory line from `G2.387`.
