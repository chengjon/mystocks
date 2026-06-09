# B4.011-M2c-HOLD OMC Workflow Guide No-Source Audit

Date: 2026-06-10

Mode: `no-source`

Branch: `wip/root-dirty-20260403`

Baseline HEAD: `4e41e45cc B4.011-M2c-B: close guides archive exact package`

Source edits authorized: `false`

Deletion-retirement authorized: `false`

## Purpose

This audit resolves the evidence status of the single hold item left from `B4.011-M2c-pre`:

- `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md`

The file was explicitly excluded from `M2c-A` and `M2c-B` because it had no active reparent match and no archive exact match. This report performs a read-only replacement/archive/reference check and records the next safe disposition.

## Findings

Current worktree state:

- `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md` is deleted in the working tree.
- The file still exists in `HEAD`.
- HEAD blob size: `3605` bytes.
- HEAD content hash: `7e7ac60e363f83c2`.

HEAD headings:

- `# OMC Workflow Guide（MyStocks）`
- `## 1. 快速开始`
- `## 2. 模型配置来源与同步`
- `## 3. 当前默认映射（基于 `omo_agents`）`
- `## 4. 故障排查（如 `Team "omc" does not exist`）`

Replacement/archive search:

- Same basename in current `docs/**`, `archive/**`, `governance/**`, `.governance/**`: `0`.
- Same content hash in current `docs/**`, `archive/**`, `governance/**`, `.governance/**`: `0`.
- Title references outside the deleted file: `0`.

Name references found:

- Only B4.011 governance cards and worklogs reference `OMC_WORKFLOW_GUIDE`.
- These references were created to mark the file as HOLD and do not prove replacement.

Git history sample:

- `833faa031 docs(guides): fold flat guide entries into domain folders` added `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md`.
- `39ed63efb chore: enforce markdown governance boundaries` modified it.

## Risk Assessment

The deletion is not safe to accept.

Reasons:

- No active replacement was found.
- No archive copy was found.
- No same-hash evidence exists anywhere in the reviewed docs/archive/governance tree.
- The file appears to document current/local OMC workflow setup, model mapping, and troubleshooting.
- The only current references are governance records explicitly warning not to process it with archive packages.

## Disposition

Recommended disposition:

- Preserve/restore the tracked file from `HEAD` in a dedicated docs-preserve package.

Do not:

- accept the deletion;
- archive it without a destination and exact path authorization;
- mix it with `docs/reports`, root `docs/superpowers`, active guide sidecars, source, tests, or scripts.

## Proposed Follow-up

Open a small docs-authorized package:

- `B4.011-M2c-HOLD-A: preserve OMC workflow guide`

Allowed action:

- Restore `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md` from `HEAD` or otherwise preserve its current tracked content.

Suggested gates:

- `git status --short -- docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md` shows no deletion after preservation.
- staged set contains only the OMC file plus governance metadata/worklog, if any.
- `git diff --cached --check`.
- GitNexus `verify-staged` low risk.
- OPENDOG fresh.

## Decision

`docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md` remains a HOLD item pending explicit preserve/restore authorization. No file restoration, deletion acceptance, archive add, source edit, test edit, or staging action was performed by this audit.
