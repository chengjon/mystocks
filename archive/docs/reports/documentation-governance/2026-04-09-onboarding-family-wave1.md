# Onboarding Family Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/onboarding/` 的第一轮 bounded 复核，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录一次 family-level keep review，而不是收薄根导航后的删除/归档动作。

## Why

- `docs/guides/onboarding/` 当前角色是 `supporting`，不是仓库级 trunk
- 该 family 当前只剩 `DEVELOPER_GUIDE.md` 与 `USER_GUIDE.md` 两份有效文档
- 两份文档都仍有现实入链，且 `docs/INDEX.md` 当前暴露面已经是最小可接受集合

## Decision

- `docs/guides/onboarding/` 当前判定为 `keep-supporting`
- 本轮不执行额外根导航收薄，只把 family index 从生成型索引改为显式 transition index

## Changes

- 将 `docs/guides/onboarding/INDEX.md` 改写为 family transition index
- 明确 `DEVELOPER_GUIDE.md` 与 `USER_GUIDE.md` 的当前阅读顺序和保留理由
- 不修改 `docs/INDEX.md`，因为当前根导航已无冗余 leaf 暴露

## Gate Check

- canonical replacement:
  - 无新增 replacement；当前仍由 `DEVELOPER_GUIDE.md` 与 `USER_GUIDE.md` 共同承担 onboarding supporting role
- family transition index:
  - `docs/guides/onboarding/INDEX.md`
- active navigation:
  - `docs/INDEX.md` 维持最小暴露面，仅保留 onboarding family 的 2 份有效入口
- retention duty:
  - 两份文档均仍有现实引用，当前不得删除

## Expected Effect

- `onboarding/` family 从“生成型目录页”升级为明确的 transition index
- 后续治理可以直接从已定义的 family 角色继续推进，而不需要重新判定该 family 是否应保留
- 当前治理焦点可继续前移到 `data-interface/` 与 `data-source/`
