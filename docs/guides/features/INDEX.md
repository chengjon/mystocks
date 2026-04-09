# Features Guide Family

> **导航说明**:
> 本文件是 `docs/guides/features/` 的 transition index，不是仓库共享规则、当前功能实现边界或唯一特性真相源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 [`architecture/STANDARDS.md`](/opt/claude/mystocks_spec/architecture/STANDARDS.md)；若涉及当前实现状态，再结合根目录 `AGENTS.md` 与实际代码核对。

## Current Entry Order

这一 family 当前角色是 `supporting`，用于保留 feature 相关的故障排查、实现说明与历史修复总结，不承担仓库级 trunk。推荐阅读顺序：

1. [`TRADINGVIEW_TROUBLESHOOTING.md`](./TRADINGVIEW_TROUBLESHOOTING.md)
2. 再按需进入热力图实现、自选股分组实现、问财菜单修复和 TradingView 修复总结

## Active Supporting Guides

- [`TRADINGVIEW_TROUBLESHOOTING.md`](./TRADINGVIEW_TROUBLESHOOTING.md)
  - TradingView 图表加载故障排查指南

## Retained Specialized References

- [`STOCK_HEATMAP_IMPLEMENTATION.md`](./STOCK_HEATMAP_IMPLEMENTATION.md)
  - 股票热力图实现总结
- [`TRADINGVIEW_FIX_SUMMARY.md`](./TRADINGVIEW_FIX_SUMMARY.md)
  - TradingView 图表加载问题修复总结
- [`WATCHLIST_GROUP_IMPLEMENTATION.md`](./WATCHLIST_GROUP_IMPLEMENTATION.md)
  - 自选股分组功能实现说明
- [`WENCAI_MENU_FIX.md`](./WENCAI_MENU_FIX.md)
  - 问财菜单缺失问题修复

## Retention Rule

- 该 family 当前保留为 `supporting`，不升级为新的 canonical docs trunk
- 根导航只暴露仍有直接使用价值的故障排查入口，其余实现/修复材料统一通过本 index 进入
- 若后续实现总结和历史修复材料入链继续下降，再按 bounded batch 单独评估 archive/delete
