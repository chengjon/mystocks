# Frontend View Governance A1-Minimal Execution Report

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: approved A1-minimal mutation batch for `openspec/changes/update-frontend-view-governance`.

## Executed Change

Moved:

```text
web/frontend/src/views/PageTitleDemo.vue
```

to:

```text
archive/web/frontend/src/views/root-sandbox/PageTitleDemo.vue
```

Added archive manifest:

```text
archive/web/frontend/src/views/root-sandbox/README.md
```

No changes were made to:

- `web/frontend/src/router/index.ts`
- `web/frontend/src/layouts/MenuConfig.ts`
- `web/frontend/src/config/pageConfig.ts`
- `web/frontend/package.json`
- frontend tests

## Reference Checks

Post-move active reference checks:

```bash
rg -n "PageTitleDemo" web/frontend/src web/frontend/tests web/frontend/package.json --glob '!**/.claude/**'
rg -n "@/views/PageTitleDemo|../PageTitleDemo\\.vue|./PageTitleDemo\\.vue" web/frontend/src web/frontend/tests --glob '!**/.claude/**'
rg -n "PageTitleDemo" web/frontend/src/router/index.ts web/frontend/src/layouts/MenuConfig.ts web/frontend/src/config/pageConfig.ts web/frontend/package.json --glob '!**/.claude/**'
```

Result:

- All three commands returned no matches.
- No active source, test, package, route, menu, or pageConfig reference remains.

## Validation

Command:

```bash
openspec validate update-frontend-view-governance --strict
```

Result:

```text
Change 'update-frontend-view-governance' is valid
```

## Git / Archive Note

The target files exist on disk:

```text
archive/web/frontend/src/views/root-sandbox/PageTitleDemo.vue
archive/web/frontend/src/views/root-sandbox/README.md
```

Current `.gitignore` ignores top-level `archive/`:

```text
.gitignore:213:archive/
```

Therefore, if this batch is later staged for commit, the archive files must be force-added:

```bash
git add -f archive/web/frontend/src/views/root-sandbox/PageTitleDemo.vue archive/web/frontend/src/views/root-sandbox/README.md
```

The source removal appears as:

```text
D web/frontend/src/views/PageTitleDemo.vue
```

## Completion Decision

A1-minimal is governance-complete for the approved scope:

- `PageTitleDemo.vue` has been removed from active `web/frontend/src/views`.
- It has been retained under the governed top-level archive target.
- No active route/menu/test/package references remain.
- OpenSpec validation passes.

No broader A1 files were moved.
