# Worklogs Wave 3

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/worklogs/` 在同日再次复发后的第三轮 bounded 收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件只记录一次最小纠偏动作，不把该平行目录提升为新的 family wave。

## Why

- `docs/reports/worklogs/` 仍是 canonical historical worklog trunk
- `docs/worklogs/claude-auto/2026-04-09.md` 在 wave 2 之后再次被重新生成
- 本次重新生成的文件不是空重复件，而是携带了 3 条尚未并入 canonical trunk 的新增记录

## Changes

- 将 `docs/worklogs/claude-auto/2026-04-09.md` 的 3 条新增记录并入 `docs/reports/worklogs/claude-auto/2026-04-09.md`
- 删除重新出现的平行目录 `docs/worklogs/`
- 不改动 root navigation，因为 `docs/INDEX.md` 当前仍只指向 `docs/reports/worklogs/`
- 不新增测试条目，因为现有 hygiene 测试已覆盖“`docs/worklogs/` 不得存在”
- 在 `AGENTS.md` 与 `CLAUDE.md` 补充执行层约束，明确 Claude Auto / Agent 自动 worklog 只能写入 `docs/reports/worklogs/claude-auto/`

## Gate Check

- canonical replacement:
  - `docs/reports/worklogs/claude-auto/2026-04-09.md`
- active navigation:
  - `docs/INDEX.md` 继续只暴露 `reports/worklogs/`
- retained content:
  - 08:18 的原始记录继续保留
  - 13:44、14:54、17:08 三条后续记录已补并入 canonical trunk

## Expected Effect

- 同日复发的 `docs/worklogs/` 再次被收口回 canonical worklog trunk
- 本次没有丢失新增 worklog 内容
- 对外部/会话级自动记录器新增了明确落点约束，降低继续回流到 `docs/worklogs/` 的概率
- 后续若该目录仍继续被自动生成，应继续追查真正生成源，而不是继续依赖人工并回
