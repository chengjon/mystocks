# Frontend ArtDeco Test Sandbox Archive

> **导航说明**:
> 本文件是导航页或索引页，不是当前仓库共享规则或实现状态的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及具体执行入口，再按职责分别参考根目录 `AGENTS.md` 与根目录 `CLAUDE.md`。

Date: 2026-05-11

Governing change: `openspec/changes/update-frontend-view-governance`

## Archived Files

| Archived file | Original path | Lifecycle status | Successor | Reason |
| --- | --- | --- | --- | --- |
| `ArtDecoTest.vue` | `web/frontend/src/views/ArtDecoTest.vue` | `archive-candidate/demo-sandbox` | `no-successor-needed` | No active router/menu owner or direct Vue test owner found; page was a local ArtDeco component visual smoke shell. |

## Retired Direct Guard

The archive batch also retired only this direct package target-file guard:

```text
node scripts/check-artdeco-tokens.js --target-file src/views/ArtDecoTest.vue --changed-from-git
```

All other `lint:artdeco:changed` entries remain out of scope.

## Restore Rule

If a future change needs an ArtDeco component showcase page, define a formal route or documented demo entry, owner, and active test coverage before restoring this file from archive.
