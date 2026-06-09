# Frontend View Governance Mutation Batch A1 Hidden Reference Preflight

Date: 2026-05-11

Scope: hidden-reference preflight for proposed A1 root sandbox triage.

This is a pre-mutation evidence document only. It does not approve archive movement, deletion, test retirement, package-script edits, or route changes.

## Command Inputs

Focused broad search:

```bash
rg -n "MinimalTest|Test\\.vue|KLineDemo|PageTitleDemo|ArtDecoTest|OpenStockDemo|MarketDataDemo" web/frontend/src web/frontend/tests web/frontend/package.json docs openspec --glob '!**/.claude/**'
```

Focused source import search:

```bash
rg -n "@/views/(MinimalTest|Test|KLineDemo|PageTitleDemo|ArtDecoTest|OpenStockDemo|MarketDataDemo)|../(MinimalTest|Test|KLineDemo|PageTitleDemo|ArtDecoTest|OpenStockDemo|MarketDataDemo)\\.vue|./(MinimalTest|Test|KLineDemo|PageTitleDemo|ArtDecoTest|OpenStockDemo|MarketDataDemo)\\.vue" web/frontend/src web/frontend/tests --glob '!**/.claude/**'
```

Focused route/menu/script search:

```bash
rg -n "MinimalTest|KLineDemo|PageTitleDemo|ArtDecoTest|OpenStockDemo|MarketDataDemo" web/frontend/src/router/index.ts web/frontend/src/layouts/MenuConfig.ts web/frontend/src/config/pageConfig.ts web/frontend/package.json --glob '!**/.claude/**'
```

## Preflight Findings

| File | Runtime source import found | Route/menu/pageConfig found | Test/package guard found | Docs/spec references found | A1 decision |
| --- | --- | --- | --- | --- | --- |
| `web/frontend/src/views/MinimalTest.vue` | No active import found | No current route/menu/pageConfig owner found | No direct test/package guard found | Yes: testing/diagnosis historical docs include examples and old route snippets | Not archive-approved until docs disposition is recorded |
| `web/frontend/src/views/Test.vue` | No active import found | No current route/menu/pageConfig owner found | No direct test/package guard found | Yes: historical test reports mention old root route and `Test.vue` diagnosis | Not archive-approved until docs disposition is recorded |
| `web/frontend/src/views/KLineDemo.vue` | No active import found | No current route/menu/pageConfig owner found | No direct test/package guard found | Yes: historical integration/build/inventory docs mention K-line demo | Not archive-approved until docs disposition is recorded |
| `web/frontend/src/views/PageTitleDemo.vue` | No active import found | No current route/menu/pageConfig owner found | No direct test/package guard found | Only current governance/inventory evidence found in focused pass | Strongest A1 candidate, but still needs approval before movement |
| `web/frontend/src/views/ArtDecoTest.vue` | No active import found | No current route/menu/pageConfig owner found | Yes: `lint:artdeco:changed` direct `--target-file src/views/ArtDecoTest.vue` | Yes: historical frontend fix/testing docs | Exclude from A1 mutation unless package-script guard and docs are handled in same approved batch |
| `web/frontend/src/views/OpenStockDemo.vue` | No active import found | No current route/menu/pageConfig owner found | No direct root-page test guard found; separate `views/demo/OpenStockDemo.vue` style test exists and must not be confused | Yes: module registry, feature guides, API mapping, old E2E/inventory docs | Exclude from A1; needs feature-doc/module-registry ownership decision |
| `web/frontend/src/views/MarketDataDemo.vue` | No active import found | No current route/menu/pageConfig owner found | No direct test/package guard found | Yes: inventory/governance docs; contains API demo/fallback-literal risk | Hold for absorption/no-successor decision, not first archive move |

## Important Distinctions

- `web/frontend/src/views/OpenStockDemo.vue` and `web/frontend/src/views/demo/OpenStockDemo.vue` are distinct files. The existing `openstock-demo-style-source.spec.ts` reads `src/views/demo/OpenStockDemo.vue`, not the root page.
- `ArtDecoTest.vue` has an active package-script guard through `web/frontend/package.json`, so moving it would require same-batch script/test updates.
- Historical docs are not runtime imports, but `architecture/STANDARDS.md` explicitly includes docs references in cleanup decisions. They need disposition rather than being ignored.

## Candidate Shrink Result

The original A1 proposal should be narrowed before execution:

| Status | Files |
| --- | --- |
| Possible A1 final candidate after explicit approval | `PageTitleDemo.vue` |
| Possible A1 candidates only if docs disposition is included | `MinimalTest.vue`, `Test.vue`, `KLineDemo.vue` |
| Exclude from A1 | `ArtDecoTest.vue`, `OpenStockDemo.vue`, `MarketDataDemo.vue` |

## Required Before Mutation

- Decide whether A1 is intended to update stale documentation references or to move only files with no non-governance docs references.
- If documentation updates are allowed, list the exact docs to update for `MinimalTest.vue`, `Test.vue`, and `KLineDemo.vue`.
- If documentation updates are not allowed, restrict A1 to `PageTitleDemo.vue` only.
- Obtain explicit mutation approval before any `mv`, archive move, package-script edit, or test edit.

## Preflight Conclusion

`请继续` is sufficient to continue evidence collection, but it is not sufficient to satisfy the project approval boundary for mutation. A1 remains a proposed batch, not an approved archive move. The safest next step is either:

- approve a documentation-inclusive A1 batch for `PageTitleDemo.vue`, `MinimalTest.vue`, `Test.vue`, and `KLineDemo.vue`; or
- approve a minimal A1 batch for `PageTitleDemo.vue` only.
