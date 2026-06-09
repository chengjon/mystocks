# Frontend View Governance A1-Minimal Execution Runbook

Date: 2026-05-11

Scope: execution runbook for the proposed A1-minimal mutation batch.

This runbook is not execution approval and does not move files. It records exact steps to execute after explicit approval.

## Approved-When Statement

Do not execute until the user explicitly approves:

```text
批准执行 A1-minimal，目标目录使用 archive/web/frontend/src/views/root-sandbox/，仅移动 PageTitleDemo.vue 并添加 archive README，不改 router/menu/package/test。
```

## Current Final Reference Snapshot

Latest grep:

```bash
rg -n "PageTitleDemo" web/frontend/src web/frontend/tests web/frontend/package.json docs openspec --glob '!**/.claude/**'
```

Current interpretation:

- Active source/test/package references: none found except the file itself under `web/frontend/src/views/PageTitleDemo.vue`.
- Governance/report references: present and expected.
- Historical cleanup report reference: present in `docs/reports/codebase-cleanup-2026-03-29.md`; this is historical evidence, not active runtime ownership.

## Execution Steps After Approval

1. Re-run final active reference checks.

```bash
rg -n "PageTitleDemo" web/frontend/src web/frontend/tests web/frontend/package.json --glob '!**/.claude/**'
rg -n "@/views/PageTitleDemo|../PageTitleDemo\\.vue|./PageTitleDemo\\.vue" web/frontend/src web/frontend/tests --glob '!**/.claude/**'
rg -n "PageTitleDemo" web/frontend/src/router/index.ts web/frontend/src/layouts/MenuConfig.ts web/frontend/src/config/pageConfig.ts web/frontend/package.json --glob '!**/.claude/**'
```

Expected:

- First command returns only `web/frontend/src/views/PageTitleDemo.vue` if the file still exists.
- Second command returns no import references.
- Third command returns no route/menu/pageConfig/package references.

2. Create target directory.

```bash
mkdir -p archive/web/frontend/src/views/root-sandbox
```

3. Move the file.

```bash
mv web/frontend/src/views/PageTitleDemo.vue archive/web/frontend/src/views/root-sandbox/PageTitleDemo.vue
```

4. Add archive manifest.

Create `archive/web/frontend/src/views/root-sandbox/README.md` with:

```markdown
# Frontend View Root Sandbox Archive

Date: 2026-05-11

Governing change: `openspec/changes/update-frontend-view-governance`

## Archived Files

| Archived file | Original path | Lifecycle status | Successor | Reason |
| --- | --- | --- | --- | --- |
| `PageTitleDemo.vue` | `web/frontend/src/views/PageTitleDemo.vue` | `archive-candidate/root-demo-sandbox` | `no-successor-needed` | No active router/menu/pageConfig/source/test/package owner found during A1-minimal preflight. |

## Validation

- `openspec validate update-frontend-view-governance --strict`
- active reference grep after move
```

5. Re-run active reference checks.

```bash
rg -n "PageTitleDemo" web/frontend/src web/frontend/tests web/frontend/package.json --glob '!**/.claude/**'
rg -n "@/views/PageTitleDemo|../PageTitleDemo\\.vue|./PageTitleDemo\\.vue" web/frontend/src web/frontend/tests --glob '!**/.claude/**'
rg -n "PageTitleDemo" web/frontend/src/router/index.ts web/frontend/src/layouts/MenuConfig.ts web/frontend/src/config/pageConfig.ts web/frontend/package.json --glob '!**/.claude/**'
```

Expected after move:

- No active source/test/package references.
- No route/menu/pageConfig references.

6. Validate OpenSpec.

```bash
openspec validate update-frontend-view-governance --strict
```

7. Optional GitNexus scope check.

Because A1-minimal is a file move outside active runtime code and no symbol is edited, symbol impact is not expected to be useful. If the move is staged for commit, run staged change detection before commit:

```bash
git add web/frontend/src/views/PageTitleDemo.vue archive/web/frontend/src/views/root-sandbox/PageTitleDemo.vue archive/web/frontend/src/views/root-sandbox/README.md
gitnexus_detect_changes(scope="staged")
```

## Rollback Steps

If a hidden active reference appears after the move:

```bash
mv archive/web/frontend/src/views/root-sandbox/PageTitleDemo.vue web/frontend/src/views/PageTitleDemo.vue
```

Then remove the archive README only if it contains no other archived files:

```bash
rm archive/web/frontend/src/views/root-sandbox/README.md
rmdir archive/web/frontend/src/views/root-sandbox
```

Do not use destructive git reset. Preserve unrelated dirty worktree changes.

## Completion Criteria

A1-minimal is complete only when:

- `PageTitleDemo.vue` is moved to `archive/web/frontend/src/views/root-sandbox/PageTitleDemo.vue`.
- Archive README records original path, lifecycle status, successor, and validation.
- No active source/test/package/router/menu/pageConfig references remain.
- `openspec validate update-frontend-view-governance --strict` passes.
- Final report states actual command results.

## Non-Scope

- No changes to `router/index.ts`.
- No changes to `MenuConfig.ts`.
- No changes to `web/frontend/package.json`.
- No movement of `MinimalTest.vue`, `Test.vue`, `KLineDemo.vue`, `ArtDecoTest.vue`, `OpenStockDemo.vue`, `MarketDataDemo.vue`, or demo parent shells.
