# PM2 Family Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/pm2/` 导航暴露面的第一轮 bounded 收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/pm2/` 导航暴露面的第一轮 bounded 收口。

## Why

- `docs/guides/pm2/` 当前角色是 `supporting`，不是仓库级 trunk
- `docs/INDEX.md` 仍把 `pm2` family 的全部叶子文档平铺到根导航
- 其中 `PM2_PLAYWRIGHT_TESTING_GUIDE_REVIEW.md` 更适合作为历史审核意见，而不是主入口

## Changes

- 将 `docs/guides/pm2/INDEX.md` 改写为 family transition index
- 收薄 `docs/INDEX.md` 中 PM2 family 的根导航
- 根导航现在优先保留：
  - `guides/pm2/INDEX.md`
  - `guides/pm2/PM2_PLAYWRIGHT_TESTING_GUIDE.md`
  - `guides/pm2/PM2_QUICK_START_GUIDE.md`
  - `guides/pm2/PM2_TMUX_LNV_COLLABORATION_GUIDE.md`
  - `Supporting Guides` -> `guides/pm2/INDEX.md`
- 将 `PM2_PLAYWRIGHT_TESTING_GUIDE_REVIEW.md` 收回到 family index 内部阅读

## Gate Check

- canonical replacement:
  - `docs/guides/pm2/PM2_PLAYWRIGHT_TESTING_GUIDE.md`
  - `docs/guides/pm2/PM2_QUICK_START_GUIDE.md`
  - `docs/guides/pm2/PM2_TMUX_LNV_COLLABORATION_GUIDE.md`
- family transition index:
  - `docs/guides/pm2/INDEX.md`
- active navigation:
  - `docs/INDEX.md` 已减少对 PM2 family 历史叶子文档的直接暴露
- retention duty:
  - review 文档继续保留为历史审核记录

## Expected Effect

- 根导航不再把 review 文档误读为当前 PM2 主入口
- 读者先进入执行指南和 quick start，再按需查看历史审核意见
- 后续如 review 文档入链继续下降，可继续单独评估 archive/delete
