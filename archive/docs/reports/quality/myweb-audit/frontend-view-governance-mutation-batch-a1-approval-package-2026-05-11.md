# Frontend View Governance Mutation Batch A1 Approval Package

Date: 2026-05-11

Scope: approval package for the first controlled mutation batch under `openspec/changes/update-frontend-view-governance`.

This package is the final pre-approval artifact. It does not move files, edit runtime code, update tests, or change routes.

## Decision Needed

Choose exactly one A1 execution profile.

| Profile | Files | Included work | Risk | Recommendation |
| --- | --- | --- | --- | --- |
| A1-minimal | `web/frontend/src/views/PageTitleDemo.vue` | Move only this one root sandbox page after final reference check | Lowest | Recommended first archive workflow proof |
| A1-doc-linked | `PageTitleDemo.vue`, `MinimalTest.vue`, `Test.vue`, `KLineDemo.vue` | Move files plus update stale historical docs or mark references as historical | Medium | Use only if doc cleanup is explicitly desired now |

Recommended profile: A1-minimal.

Reason:

- It proves the archive workflow with the smallest possible blast radius.
- `PageTitleDemo.vue` has no active router/menu/pageConfig owner, no runtime source import, and no direct test/package guard found in the focused preflight.
- The other candidates have historical documentation references that should not be silently ignored under `architecture/STANDARDS.md`.

## A1-Minimal Proposed Mutation

Exact file:

- `web/frontend/src/views/PageTitleDemo.vue`

Proposed disposition:

- Move to governed frontend view archive location.
- Record successor as `no-successor-needed` unless final pre-move grep finds a live page-title feature owner.
- Do not edit router, menu, package scripts, or tests unless final grep discovers a hidden reference.

Current evidence:

- No current `router/index.ts` dynamic import found.
- No current `MenuConfig.ts` entry found.
- No current `pageConfig.ts` component owner found.
- No direct test/package guard found.
- Existing references are governance/inventory evidence plus file-local comment.

## A1-Doc-Linked Proposed Mutation

Exact files:

- `web/frontend/src/views/PageTitleDemo.vue`
- `web/frontend/src/views/MinimalTest.vue`
- `web/frontend/src/views/Test.vue`
- `web/frontend/src/views/KLineDemo.vue`

Required additional work:

- Identify and update or annotate stale historical docs that still mention old root/demo route experiments.
- Preserve history semantics: do not rewrite historical incident reports as if the old state never existed; add current-status notes instead.
- Record successor/no-successor-needed for each file.

Reason this is not the default:

- It turns a file archive batch into a documentation cleanup batch.
- It increases review scope without improving canonical business route safety.

## Explicit Non-Scope

Do not include:

- `ArtDecoTest.vue`: still coupled to `web/frontend/package.json` `lint:artdeco:changed` direct target-file guard.
- `OpenStockDemo.vue`: still referenced by module registry, feature docs, API mapping, and old demo ownership docs.
- `MarketDataDemo.vue`: still needs data/market absorption or no-successor decision.
- `SkeletonUsage.vue`, `DataVisualizationShowcase.vue`, `SmartDataSourceTest.vue`, `StockAnalysisDemo.vue`: direct test/script/static-shell guard coupling.
- `FreqtradeDemo.vue`, `TdxpyDemo.vue`, `PyprofilingDemo.vue`: demo parent shells with child/support assets.

## Required Final Pre-Move Checks

For A1-minimal:

```bash
rg -n "PageTitleDemo" web/frontend/src web/frontend/tests web/frontend/package.json docs openspec --glob '!**/.claude/**'
rg -n "@/views/PageTitleDemo|../PageTitleDemo\\.vue|./PageTitleDemo\\.vue" web/frontend/src web/frontend/tests --glob '!**/.claude/**'
rg -n "PageTitleDemo" web/frontend/src/router/index.ts web/frontend/src/layouts/MenuConfig.ts web/frontend/src/config/pageConfig.ts web/frontend/package.json --glob '!**/.claude/**'
```

For A1-doc-linked, repeat the same checks for:

```text
PageTitleDemo|MinimalTest|Test\\.vue|KLineDemo
```

## Required Post-Move Validation

Minimum:

```bash
openspec validate update-frontend-view-governance --strict
```

If package/test references are changed:

```bash
cd web/frontend && npm run lint:artdeco
cd web/frontend && npx vitest run tests/unit/workflows/ci-workflow-gates.spec.ts
```

If only `PageTitleDemo.vue` is moved and no test/package guard is touched, Vitest is not required by this package, but the final report must state that no runtime/test/package references were found.

## Approval Wording

To execute A1-minimal, use:

```text
批准执行 A1-minimal，仅处理 PageTitleDemo.vue，最终 grep 无隐藏引用后移动到受控 archive，不改 router/menu/package/test。
```

To execute A1-doc-linked, use:

```text
批准执行 A1-doc-linked，处理 PageTitleDemo.vue、MinimalTest.vue、Test.vue、KLineDemo.vue，并同步更新或标注相关历史文档引用。
```

Without one of these explicit approvals, `3.0` remains open and no mutation should occur.
