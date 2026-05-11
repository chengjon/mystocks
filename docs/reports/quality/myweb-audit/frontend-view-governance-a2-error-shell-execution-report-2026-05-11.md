# Frontend View Governance A2 Error Shell Execution Report

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: `A2-archive` mutation batch for `openspec/changes/update-frontend-view-governance`.

## Executed Change

Moved error demo shell assets from active source tree to governed archive:

```text
web/frontend/src/views/errors/Forbidden.vue
web/frontend/src/views/errors/NetworkError.vue
web/frontend/src/views/errors/ServiceUnavailable.vue
web/frontend/src/views/errors/styles/ServiceUnavailable.scss
```

Archive target:

```text
archive/web/frontend/src/views/errors/
```

Moved direct guard specs from active tests to governed archive:

```text
web/frontend/tests/unit/config/errors-mainline-gate.spec.ts
web/frontend/tests/unit/config/errors-forbidden-style-source.spec.ts
web/frontend/tests/unit/config/errors-network-style-source.spec.ts
web/frontend/tests/unit/config/errors-service-unavailable-style-source.spec.ts
```

Archive target:

```text
archive/web/frontend/tests/unit/config/errors/
```

Updated `web/frontend/package.json`:

- Removed `node scripts/check-artdeco-tokens.js --target-dir src/views/errors --changed-from-git` from `lint:artdeco:changed`.

No changes were made to:

- `web/frontend/src/router/index.ts`
- `web/frontend/src/layouts/MenuConfig.ts`
- `web/frontend/src/config/pageConfig.ts`
- `web/frontend/src/views/Login.vue`
- `web/frontend/src/views/NotFound.vue`

## Pre-Move Evidence

- GitNexus upstream impact for `Forbidden.vue`, `NetworkError.vue`, and `ServiceUnavailable.vue`: LOW, 0 direct dependents, 0 affected processes.
- No active router, menu, or pageConfig owner was found for `Forbidden`, `NetworkError`, or `ServiceUnavailable`.
- Direct active blockers were limited to `web/frontend/package.json` changed-scope lint guard and four direct unit guard specs.

## Validation Results

```bash
openspec validate update-frontend-view-governance --strict
```

Result:

- Passed.

```bash
rg -n "views/errors|errors/Forbidden|errors/NetworkError|errors/ServiceUnavailable|src/views/errors" web/frontend/src web/frontend/tests web/frontend/package.json --glob '!**/.claude/**'
rg -n "@/views/errors|../errors/|./errors/" web/frontend/src web/frontend/tests --glob '!**/.claude/**'
rg -n "Forbidden|NetworkError|ServiceUnavailable" web/frontend/src/router/index.ts web/frontend/src/layouts/MenuConfig.ts web/frontend/src/config/pageConfig.ts web/frontend/package.json --glob '!**/.claude/**'
```

Result:

- All three active-reference checks returned no matches.

```bash
node -e "const fs=require('fs'); const pkg=fs.readFileSync('web/frontend/package.json','utf8'); if(pkg.includes('src/views/errors')) process.exit(1); console.log('package guard no longer references src/views/errors')"
test ! -e web/frontend/src/views/errors
```

Result:

- Passed.

```bash
cd web/frontend && npm run lint:artdeco:changed
```

Result:

- Failed before any `src/views/errors` target because the current dirty worktree has pre-existing ArtDeco literal violations under `src/views/advanced-analysis/*`.
- This is not an A2 regression: A2 removed `src/views/errors` from `lint:artdeco:changed`, and the post-move active-reference checks confirm no active error-shell references remain.

```bash
gitnexus_detect_changes(scope="staged")
```

Result:

- Risk: LOW.
- Changed files: 13.
- Changed symbols: `web/frontend/package.json`.
- Affected processes: 0.

## Completion Decision

A2 is governance-complete for the approved archive scope, but not a clean global frontend lint closeout because `lint:artdeco:changed` is currently blocked by unrelated existing `advanced-analysis` ArtDeco token debt.
