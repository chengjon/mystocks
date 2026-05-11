# Frontend View Governance A4 Root Test Sandbox Minimal Preflight

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: read-only preflight for `A4-root-test-sandbox-minimal-preflight`.

This preflight does not move files, edit runtime code, or retire tests.

## Candidate Files

- `web/frontend/src/views/MinimalTest.vue`
- `web/frontend/src/views/Test.vue`

## GitNexus Impact

| Target | Risk | Direct dependents | Affected processes |
| --- | --- | ---: | ---: |
| `MinimalTest.vue` | LOW | 0 | 0 |
| `Test.vue` | LOW | 0 | 0 |

## Source Summary

| File | Source behavior | Archive implication |
| --- | --- | --- |
| `MinimalTest.vue` | Minimal test page with timestamp and console-load/mount logs; scoped hardcoded demo styling | `no-successor-needed` if no route/test owner exists |
| `Test.vue` | Minimal Vue smoke page with local time update button and hardcoded demo styling | `no-successor-needed` if no route/test owner exists |

## Active Reference Checks

Focused commands:

```text
rg -n "MinimalTest|Test\\.vue|src/views/Test|src/views/MinimalTest|@/views/Test|@/views/MinimalTest|../Test\\.vue|../MinimalTest\\.vue|./Test\\.vue|./MinimalTest\\.vue" web/frontend/src web/frontend/tests web/frontend/package.json docs/reports/quality/myweb-audit openspec/changes/update-frontend-view-governance --glob '!**/.claude/**'
rg -n "MinimalTest|Test\\.vue|Test" web/frontend/src/router/index.ts web/frontend/src/layouts/MenuConfig.ts web/frontend/src/config web/frontend/package.json --glob '!**/.claude/**'
```

Findings:

- No active `router/index.ts` import or route owner was found for `MinimalTest.vue` or `Test.vue`.
- No active `MenuConfig.ts` owner was found for either file.
- No active `src/config` owner was found for either file.
- No direct `package.json` `lint:artdeco:changed` target was found for either file.
- No direct unit/e2e spec import or source read was found for either file.
- Remaining references are governance docs, historical inventory/guard-map records, A1/A4 planning artifacts, or broad false positives such as `SmartDataSourceTest.vue` and `TestPage.vue`.

## Archive Eligibility

| File | Code-path status | Function-tree status | Successor | Eligibility |
| --- | --- | --- | --- | --- |
| `MinimalTest.vue` | No active route/menu/config/package/test owner found | `重复冗余/test-sandbox` | `no-successor-needed` | Eligible for governed archive if approved |
| `Test.vue` | No active route/menu/config/package/test owner found | `重复冗余/test-sandbox` | `no-successor-needed` | Eligible for governed archive if approved |

## Explicit Exclusions

Do not include these files in the next move:

- `web/frontend/src/views/ArtDecoTest.vue`: package target-file guard remains.
- `web/frontend/src/views/DataVisualizationShowcase.vue`: direct package target and config specs remain.
- `web/frontend/src/views/KLineDemo.vue`: K-line absorption decision remains open.
- `web/frontend/src/views/MarketDataDemo.vue`: market/data absorption decision remains open.
- `web/frontend/src/views/SkeletonUsage.vue`: package, workflow, and tokenization guards remain.
- `web/frontend/src/views/SmartDataSourceTest.vue`: package target and root-demo style guard remain.
- `web/frontend/src/views/StockAnalysisDemo.vue`: direct static-shell spec/style guards remain.

## Recommended Mutation Batch

```text
A4-root-test-sandbox-minimal-archive
```

Recommended scope if approved:

- Move `web/frontend/src/views/MinimalTest.vue` to `archive/web/frontend/src/views/root-sandbox/test-sandbox/MinimalTest.vue`.
- Move `web/frontend/src/views/Test.vue` to `archive/web/frontend/src/views/root-sandbox/test-sandbox/Test.vue`.
- Add `archive/web/frontend/src/views/root-sandbox/test-sandbox/README.md`.
- Do not update router/menu/package/tests unless a final pre-move active-reference check reveals a direct owner.

## Next Task

```text
3.42 Decide whether to execute A4-root-test-sandbox-minimal-archive.
```
