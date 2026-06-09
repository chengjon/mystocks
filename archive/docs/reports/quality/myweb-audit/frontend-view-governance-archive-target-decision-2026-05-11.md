# Frontend View Governance Archive Target Decision

Date: 2026-05-11

Scope: archive target decision needed before executing A1 mutation under `openspec/changes/update-frontend-view-governance`.

This document is a pre-execution decision note. It does not move files or approve mutation.

## Findings

Relevant current specs:

- `openspec/specs/file-organization/spec.md` says historical or frozen documents/artifacts SHALL be archived under top-level `archive/`.
- `openspec/specs/file-organization/spec.md` says active route pages SHALL NOT be moved into `deprecated/` while still referenced by router truth, generated page-config truth, or governed inventory truth.
- Historical `openspec/changes/restructure-frontend-directory/specs/frontend-structure/spec.md` proposed `src/views/deprecated/`, but the current repository does not contain `web/frontend/src/views/deprecated/`.

Filesystem check:

- `find web/frontend/src/views -maxdepth 2 -type d | rg "archive|deprecated|converted"` found no current `views/archive`, `views/deprecated`, or `converted.archive` directory.
- Top-level `archive/` exists and is already used for historical repository assets and documentation snapshots.

## Decision Problem

A1-minimal proposes moving `web/frontend/src/views/PageTitleDemo.vue`.

Before moving, the project must decide whether frontend view archive means:

| Option | Target | Pros | Cons |
| --- | --- | --- | --- |
| T1 | `archive/web/frontend/src/views/root-sandbox/PageTitleDemo.vue` | Aligns with top-level lifecycle archive rule; avoids keeping archived source under active `src/views`; easy to block from router imports | Requires creating a new archive subtree |
| T2 | `web/frontend/src/views/deprecated/demo/PageTitleDemo.vue` | Aligns with old restructure proposal text | Directory does not currently exist; keeps archived code under active source tree; may affect tooling/lint scans |
| T3 | `web/frontend/src/views/archive/PageTitleDemo.vue` | Short path and hinted by old guard-map references | Directory does not currently exist; active source tree may still be importable; weaker lifecycle separation |

Recommended target: T1.

Reason:

- It follows current `file-organization` lifecycle rule for historical assets under top-level `archive/`.
- It avoids creating a new active-source `deprecated` convention from an older proposal snapshot.
- It makes router/menu import prevention easier because archived files are outside `web/frontend/src/views`.

## Proposed A1-Minimal Target

If A1-minimal is approved, move:

```text
web/frontend/src/views/PageTitleDemo.vue
```

to:

```text
archive/web/frontend/src/views/root-sandbox/PageTitleDemo.vue
```

Add a small manifest next to the moved file:

```text
archive/web/frontend/src/views/root-sandbox/README.md
```

The manifest should record:

- original path
- move date
- governing OpenSpec change
- lifecycle status: `archive-candidate/root-demo-sandbox`
- successor: `no-successor-needed`
- validation commands and results

## Required Guard After Move

Because the archive target is outside `web/frontend/src/views`, the immediate import risk is lower, but the post-move report must still confirm:

- `router/index.ts` has no `PageTitleDemo` reference.
- `MenuConfig.ts` has no `PageTitleDemo` reference.
- `pageConfig.ts` has no `PageTitleDemo` reference.
- `web/frontend/package.json` has no `PageTitleDemo` target-file guard.
- `rg -n "PageTitleDemo" web/frontend/src web/frontend/tests web/frontend/package.json` returns no active source/test/package references.

## Approval Boundary

This target decision should be considered part of A1 approval.

Recommended execution approval wording:

```text
批准执行 A1-minimal，目标目录使用 archive/web/frontend/src/views/root-sandbox/，仅移动 PageTitleDemo.vue 并添加 archive README，不改 router/menu/package/test。
```

Without explicit approval, no file should be moved.
