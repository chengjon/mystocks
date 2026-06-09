# Frontend View Governance Lessons Absorption - 2026-05-10

## Scope

This note records which historical lessons from the Vue governance history were absorbed into the current `update-frontend-view-governance` OpenSpec change.

No frontend runtime code was changed.

## Source Documents

| Document | Role |
|---|---|
| `docs/reports/quality/myweb-audit/frontend-view-governance-history-2026-05-10.md` | Historical task index and snapshot context |
| `docs/reports/quality/myweb-audit/frontend-view-governance-lessons-learned-2026-05-10.md` | Actionable lessons and spec improvement suggestions |

## Absorbed Lessons

| Lesson | Action Taken |
|---|---|
| S1: Add frontend entry truth | Added `index.html -> /src/main-standard.ts -> router/index.ts` to design and frontend-routing delta |
| S2: Require successor/rationale for archive candidates | Added `successor page` or `no-successor-needed` requirement |
| S3: Build guard map before classification | Added Step 0 and directory-governance guard-map requirement |
| S4: Add route status + guard status | Added auxiliary dimensions: `active/redirect/dead` and `mainline-guarded/spec-guarded/unguarded` |
| S5: Include test/spec migration in archive checklist | Added mainline-gate and other spec migration requirements |
| S6: Distinguish governance complete vs merge ready | Added completion semantics to design and directory-governance delta |
| S7: Treat mainline-gate specs as high-priority hidden references | Added explicit guard-map and archive-blocking rules for `*-mainline-gate.spec.ts` |

## Verification Notes

- Current runtime entry still loads `/src/main-standard.ts` from `web/frontend/index.html`.
- Current root-level frontend entry variants are not present under `web/frontend/src/` beyond `main-standard.ts`; the historical "multiple main variants" lesson remains useful as a defensive rule.
- `*-mainline-gate.spec.ts` files are present and should be treated as guard evidence before archive moves.
- Historical view counts are snapshots. The latest inventory batch measured 272 `views/**/*.vue` files and 42 routed view imports.

## Updated Artifacts

| Artifact | Change |
|---|---|
| `docs/superpowers/specs/2026-05-10-frontend-view-governance-design.md` | Added entry truth, guard map, dual labels, successor/rationale, archive checklist, completion states |
| `openspec/changes/update-frontend-view-governance/design.md` | Added same governance decisions in OpenSpec design |
| `openspec/changes/update-frontend-view-governance/tasks.md` | Added Step 0 guard-map tasks and expanded classification/mutation tasks |
| `openspec/changes/update-frontend-view-governance/specs/frontend-routing/spec.md` | Added runtime entry truth chain requirement |
| `openspec/changes/update-frontend-view-governance/specs/directory-governance/spec.md` | Added guard map, dual status, successor/rationale, and completion semantics requirements |

## Validation

```bash
openspec validate update-frontend-view-governance --strict
```

Result: passed.

