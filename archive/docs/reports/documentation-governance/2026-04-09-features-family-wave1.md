# Features Family Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/features/` 导航暴露面的第一轮 bounded 收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/features/` 导航暴露面的第一轮 bounded 收口。

## Why

- `docs/guides/features/` 当前角色是 `supporting`，不是仓库级 trunk
- `docs/INDEX.md` 仍把热力图实现、自选股分组实现、问财菜单修复、TradingView 修复总结和故障排查全部平铺暴露
- 这会让历史实现/修复总结看起来与当前仍可直接使用的排障入口处于同一优先级

## Changes

- 将 `docs/guides/features/INDEX.md` 改写为 family transition index
- 收薄 `docs/INDEX.md` 中 Features family 的根导航
- 根导航现在优先保留：
  - `guides/features/INDEX.md`
  - `guides/features/TRADINGVIEW_TROUBLESHOOTING.md`
  - `Supporting Guides` -> `guides/features/INDEX.md`
- 将热力图实现、自选股分组实现、问财菜单修复和 TradingView 修复总结收回到 family index 内部阅读

## Gate Check

- canonical replacement:
  - `docs/guides/features/TRADINGVIEW_TROUBLESHOOTING.md`
- family transition index:
  - `docs/guides/features/INDEX.md`
- active navigation:
  - `docs/INDEX.md` 已减少对 Features family 历史实现和修复 leaf docs 的直接暴露
- retention duty:
  - `STOCK_HEATMAP_IMPLEMENTATION.md`
  - `TRADINGVIEW_FIX_SUMMARY.md`
  - `WATCHLIST_GROUP_IMPLEMENTATION.md`
  - `WENCAI_MENU_FIX.md`
  - 以上文档继续保留为 supporting/reference docs

## Expected Effect

- 根导航不再把 Features family 的实现总结和历史修复误读为主入口
- 读者先进入 TradingView 故障排查，再按需查看热力图实现、自选股分组和问财菜单修复等专题材料
- 后续若这些实现/修复说明入链继续下降，可继续逐份评估 archive/delete
