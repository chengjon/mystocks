# Frontend View Checklist - Settings Static Shells - 2026-05-10

## Scope

This is a read-only redundant-page checklist batch for:

- `web/frontend/src/views/settings/General.vue`
- `web/frontend/src/views/settings/Notifications.vue`
- `web/frontend/src/views/settings/Security.vue`
- `web/frontend/src/views/settings/Theme.vue`

No files were moved, archived, or deleted.

## Shared Metadata

| Field | Value |
|---|---|
| Current directory | `web/frontend/src/views/settings/` |
| Previous historical classification | Unrouted secondary settings child pages repaired into honest static shells |
| Previous classification source | `docs/reports/quality/myweb-audit/audit-20260426-02/pages/settings-test-static-shells-truth-audit.md` |
| Previous classification upheld or changed? | Upheld |
| Route status | `dead` |
| Guard status | `mainline-guarded` |
| Proposed lifecycle status | `candidate-review` |
| Reviewer | Codex |
| Review date | 2026-05-10 |

## Page Summary

| Page | Current content | Canonical handoff | Lifecycle decision |
|---|---|---|---|
| `settings/General.vue` | Honest static shell, no independent settings semantics | `/system/config` | `candidate-review` |
| `settings/Notifications.vue` | Honest static shell, no independent notification semantics | `/system/config` | `candidate-review` |
| `settings/Security.vue` | Honest static shell, no independent auth/security semantics | `/system/config` | `candidate-review` |
| `settings/Theme.vue` | Honest static shell, no independent theme semantics | `/system/config` | `candidate-review` |

## Truth-Source Checks

| Check | Result | Evidence |
|---|---|---|
| Dynamically imported by `router/index.ts` | No | Not in current routed view import set |
| Reachable through compatibility route or alias | No | No route alias found |
| Represented by `MenuConfig.ts` | No | Current menu uses `/system/config`, not `/settings/*` |
| Intentional hidden route, blank page, detail page, or special shell | No active route; yes historical static shell | Files intentionally degrade to `legacy-static-shell` with `/system/config` handoff |
| Referenced by layout tabs, page registries, generated page config | No active runtime reference found | Guard map shows no runtime source refs for these four files |
| Referenced by docs/runtime string links/examples expected to work | Yes, historical docs/audit references | Guard map shows docs references and prior audit artifacts |

## Functional Coverage Checks

| Check | Result | Evidence |
|---|---|---|
| Workflow not covered by canonical route page | No current evidence | Text states each child page is not connected to canonical verified truth |
| Visible business-domain capability | No | `/system/config` is canonical system configuration surface |
| Selector behavior, tab orchestration, or cross-slice state | No | Files contain static template and scoped CSS only |
| Domain calculation rules | No | No script logic |
| Compatibility behavior for tests/docs/historical links | Yes | Existing specs assert honest static shell semantics |

## Reusable Asset Checks

| Asset class | Present? | Absorption target / rationale |
|---|---|---|
| Reusable UI component | No | Simple repeated static shell markup only |
| Shared composable or API normalization | No | No script imports |
| Request provenance, freshness, runtime status | No | Static shell only |
| Metric cards, KPI grid, stats strip, summary logic | No | Static shell only |
| Table columns, filters, selectors, query schema | No | Static shell only |
| Domain calculation rule | No | Static shell only |

## Guard And Test Checks

Discovery commands used:

```bash
rg -n "src/views/settings|@/views/settings|views/settings|settings/(General|Notifications|Security|Theme)|General.vue|Notifications.vue|Security.vue|Theme.vue" web/frontend/src web/frontend/tests docs --glob '!**/.claude/**'
sed -n '1,220p' web/frontend/tests/unit/config/settings-mainline-gate.spec.ts
sed -n '1,220p' web/frontend/tests/unit/config/settings-style-normalization.spec.ts
```

| Check | Result | Evidence |
|---|---|---|
| Referenced by `*-mainline-gate.spec.ts` | Yes | `settings-mainline-gate.spec.ts` requires `--target-dir src/views/settings --changed-from-git` |
| Imported or read by other `*.spec.ts` | Yes | `settings-style-normalization.spec.ts` reads all four files |
| Test asserts style/class/route/runtime behavior | Yes | Test asserts `legacy-static-shell`, `canonical /system/config`, token spacing, and absence of placeholder UI |
| Relevant guard migrated to canonical successor | No | Guard still points at `src/views/settings` |
| Guard retirement rationale recorded | No | Not yet recorded; required before archive |

## Successor Decision

| Field | Value |
|---|---|
| Canonical successor page | `web/frontend/src/views/system/Settings.vue` via `/system/config` |
| Successor covers all useful functionality? | Yes for system configuration truth; no need to preserve child-page independent semantics |
| Missing functionality to absorb | None identified from these static shells |
| No-successor-needed rationale | Not applicable because `/system/config` is the successor |

## Redundant Eligibility Gate

| Required condition | Result | Evidence |
|---|---|---|
| Not part of active routed-page baseline | Pass | Not in router dynamic import set |
| Not represented by visible menu | Pass | Menu uses `/system/config` |
| Not an intentional hidden route or special shell | Fail | They are intentional guarded legacy static shells |
| Provides no unique business-domain function coverage | Pass | Static handoff shells only |
| All useful assets absorbed or explicitly rejected | Pass | No reusable assets identified |
| No active static import reference | Pass | No runtime source refs found |
| No active dynamic import reference | Pass | No router refs found |
| No layout tab or page registry reference | Pass | No active runtime registry refs found |
| No page-config reference | Pass | No active page-config ref found |
| No documentation or example link expected to work | Fail / unresolved | Historical audit/docs references still exist |
| No runtime string-link or feature-flag reference | Pass | None found |
| No test guard or spec reference, or migration/retirement recorded | Fail | `settings-mainline-gate.spec.ts` and `settings-style-normalization.spec.ts` still guard them |
| Successor or `no-successor-needed` rationale recorded | Pass | `/system/config` recorded as successor |

## Final Decision

| Field | Value |
|---|---|
| Lifecycle decision | Keep as `candidate-review` |
| Execution action | Needs guard/test retirement or migration decision before any archive proposal |
| Archive target | None approved |
| Archive batch ID / approval reference | None |

## Conclusion

These four settings child pages are not useful as product pages, but they are still guarded historical static shells. They are not `archive-candidate` until:

1. `settings-mainline-gate.spec.ts` is migrated or retired.
2. `settings-style-normalization.spec.ts` is migrated or retired.
3. Historical docs are either updated to point at `/system/config` or marked historical-only.
4. The redundant eligibility gate is re-run and all rows pass.

