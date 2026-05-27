# Track: Core Split And Compatibility Wrappers

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: active track summary
- Prepared at: `2026-05-27T15:32:41+08:00`
- Base HEAD checked: `3b8f95945fcb489316ddfaf919835d372122fa5f`

Boundary note: this track summary does not authorize Core Batch 2 source edits,
wrapper deletion, docs/API edits, or compatibility removal.

## Track Role

This track owns backend Core helper/package splits that retain compatibility
wrappers while active consumers migrate to canonical package paths.

## Current Gate

Core Batch 2 remains blocked until the OpenSpec task and shared evidence gates
have explicit disposition. Ambiguous wording is not enough to start another
helper split.

Required disposition before Batch 2:

- the relevant OpenSpec task is checked complete with evidence, or
- it remains open with an explicit non-blocking note, owner, and scope, and
- the next helper batch has a concrete module selection packet, allowed paths,
  tests, rollback, and stale-checkout reconciliation.

## Compatibility Wrapper Rule

Do not equate every compatibility wrapper with deletion debt. A wrapper may be:

- active and documented
- runtime-only and hidden from schema
- retained as migration shim
- ready for deletion after consumer proof
- retired

Deletion requires current consumer evidence and an approved retirement decision.
