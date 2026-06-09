# B4.011-M1 Docs Archive/Reorg Truth No-Source Audit

Date: 2026-06-09

Mode: `no-source`

Branch: `wip/root-dirty-20260403`

Baseline HEAD: `fdffe958b B4.010-M3: close frontend tooling static governance`

Source edits authorized: `false`

## Purpose

B4.010 is closed and active FUNCTION_TREE gates are empty. The next highest-value dirty family is not frontend source; it is the documentation archive/reorganization residue around `docs/reports`, `docs/guides`, and `docs/superpowers`.

This audit starts the next governance domain as a read-only truth pass. It classifies the dirty state, identifies archive evidence, and proposes follow-up authorization batches. It does not accept deletions, stage files, modify source, or change runtime behavior.

## Hard Boundary

In scope for this audit:

- `docs/reports/**`
- `archive/docs/reports/**` as ignored archive evidence only
- `docs/guides/**`
- `archive/docs/guides-merged/**` as ignored archive evidence only
- `docs/superpowers/**`
- `archive/docs/superpowers/**` as ignored archive evidence only
- Docs-only sidecars under `docs/api`, `docs/agents`, `docs/operations`, `docs/plans`, and `docs/overview` for inventory only

Out of scope:

- `web/frontend/src/**`
- `web/frontend/tests/**`
- `src/**`
- `web/backend/**`
- `tests/**`
- `scripts/**`
- `reports/**` root governance/analysis artifacts except as separate future candidate
- `.omc`, `TASK*`, local tool runtime state
- ST-HOLD / B4.006
- `marketKlineData`
- `web/frontend/src/App.vue`
- `web/frontend/src/layouts/archive/BaseLayout.vue`
- `web/frontend/tests/unit/config/trading-style-normalization.spec.ts`
- Any cleanup, deletion acceptance, source/test edit, route/view/store/API change, or runtime behavior change

## Current Gate State

- Active FUNCTION_TREE gates: none.
- Git staged files: `0`.
- GitNexus status: indexed/current HEAD match `fdffe958b60ea76c3418511a510cb74f98ab51e9`; staged diff is fresh.
- OPENDOG verification: `fresh`; failing runs `0`; cleanup blockers `0`; refactor blockers `0`.
- Dirty records observed in worktree: `1663`.

## Dirty Family Inventory

| Family | Dirty records | Status mix | Initial read |
| --- | ---: | --- | --- |
| `docs/reports/**` | 701 | `681 D`, `7 M`, `13 ??` | Large archive/disposition family; deletions have matching ignored archive copies. Modified/untracked root docs must not be mixed with deletion acceptance. |
| `archive/docs/reports/**` | filesystem 3795 files | ignored by `.gitignore:256 archive/` | Archive evidence exists but is invisible to normal `git status`; later commits would require exact `git add -f` scope if accepted. |
| `docs/guides/**` | 110 | `58 D`, `21 M`, `31 ??` | Mixed guide reorg. This is not a simple exact archive move; needs mapping table before any deletion or forced archive commit. |
| `archive/docs/guides-merged/**` | filesystem 31 files | ignored by `.gitignore:256 archive/` | Archive evidence exists, but category roots changed, so relative-path matching is not sufficient. |
| `docs/superpowers/**` | 6 | `6 D` | Small exact archive-retirement candidate; all six deleted paths have matching ignored archive copies. |
| `archive/docs/superpowers/**` | filesystem 27 files | ignored by `.gitignore:256 archive/` | Archive evidence exists; six deleted active files match exactly under the archive. |
| Docs sidecars: `docs/api`, `docs/agents`, `docs/operations`, `docs/plans`, `docs/overview` | 21 | `14 M`, `7 ??` | Docs-only drift, but not part of the archive/deletion batch unless separately authorized. |

## Archive Evidence

`docs/reports`:

- Deleted active docs: `681`.
- Archive files under `archive/docs/reports`: `3795`.
- Exact relative-path archive matches for deleted active docs: `681 / 681`.
- Missing archive matches: `0`.

`docs/superpowers`:

- Deleted active docs: `6`.
- Archive files under `archive/docs/superpowers`: `27`.
- Exact relative-path archive matches for deleted active docs: `6 / 6`.
- Missing archive matches: `0`.

`docs/guides`:

- Deleted active docs: `58`.
- Archive files under `archive/docs/guides-merged`: `31`.
- Exact relative-path comparison is not meaningful because the archive root changes category layout.
- Needs explicit source-to-destination mapping before any deletion-retirement or archive acceptance.

## Risk Assessment

Low/medium:

- `docs/superpowers` six-file deletion family appears fully archived and small enough for a focused deletion-retirement authorization.

Medium:

- `docs/reports` has strong archive evidence for the 681 deleted tracked files, but it is a large batch and archive targets are ignored. It should be handled as a dedicated docs archive/deletion-retirement package with forced archive staging only if explicitly authorized.

Medium/high:

- `docs/guides` combines deleted paths, modified paths, untracked replacement paths, and category reparenting. It needs a mapping table and probably separate subfamilies: `ai-tools`, `data-source`, `templates`, and `legacy merged archive`.

Out-of-scope high risk:

- Source, test, backend, frontend, and scripts dirty groups remain present but are not part of this domain. They must not be folded into documentation archive commits.

## Proposed B4.011 Batch Plan

1. `B4.011-M1` no-source audit: this report plus FUNCTION_TREE evidence only.
2. `B4.011-M2a` docs/reports archive proof package: authorize exact `docs/reports` deletion-retirement plus forced archive path scope, or defer if the archive should stay local-only.
3. `B4.011-M2b` docs/superpowers archive proof package: authorize the six exact active deletions plus corresponding archive evidence.
4. `B4.011-M2c` docs/guides mapping audit: produce source-to-destination decision table before any file movement/deletion is accepted.
5. `B4.011-M2d` docs sidecars and modified root report docs: review as docs-authorized content updates, not deletion-retirement.
6. `B4.011-M3` full docs archive/reorg closeout: staged set empty or exactly authorized; GitNexus fresh; OPENDOG fresh; worktree residuals explicitly deferred.

## Gate Recommendation

Open FUNCTION_TREE node:

- Program: `.governance/programs/artdeco-web-design-governance`
- Node id: `b4-docs-archive-reorg-truth`
- Title: `Docs archive/reorg truth and dirty disposition`
- Status target after this report: `evidence-prepared`
- Source edits: unauthorized

Next human authorization should be one of:

- Approve `B4.011-M2a` for `docs/reports` archive/deletion-retirement handling.
- Approve `B4.011-M2b` first for the smaller `docs/superpowers` exact archive-retirement batch.
- Keep all archive deletions deferred and request a deeper guide mapping audit first.

## Verification Commands Used

- `git branch --show-current`
- `git log -1 --oneline`
- `git diff --cached --name-status`
- `git diff --name-status`
- `git ls-files --others --exclude-standard`
- `git check-ignore -v -- archive/docs/...`
- `node .gitnexus/run.cjs status --json`
- `OPENDOG verification --id mystocks --json`
- FUNCTION_TREE gate/status inspection

## Decision

B4.011 should proceed as a documentation archive/reorganization governance line, not as a frontend/source cleanup line.

No source edits, test edits, deletion acceptance, or staging actions were performed in this audit.
