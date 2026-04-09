# Chrome Devtools Family Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/chrome-devtools/` 导航暴露面的第一轮 bounded 收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/chrome-devtools/` 导航暴露面的第一轮 bounded 收口。

## Why

- `docs/guides/chrome-devtools/` 当前角色是 `supporting`，不是仓库级 trunk
- `docs/INDEX.md` 仍把 MCP 使用、WSL2 配置、项目测试、修复总结和完整方案全部平铺暴露
- 这会让高频入口与 fix/solution 类总结处于同一优先级

## Changes

- 将 `docs/guides/chrome-devtools/INDEX.md` 改写为 family transition index
- 收薄 `docs/INDEX.md` 中 Chrome Devtools family 的根导航
- 根导航现在优先保留：
  - `guides/chrome-devtools/INDEX.md`
  - `guides/chrome-devtools/CHROME_DEVTOOLS_MCP_GUIDE.md`
  - `guides/chrome-devtools/chrome-devtools-wsl2-guide.md`
  - `guides/chrome-devtools/mystocks-chromedevtools-testing-guide.md`
  - `Supporting Guides` -> `guides/chrome-devtools/INDEX.md`
- 将 `CHROME_DEVTOOLS_MCP_FIX_GUIDE.md` 与 `CHROME_DEVTOOLS_MCP_SOLUTION.md` 收回到 family index 内部阅读

## Gate Check

- canonical replacement:
  - 无新增 canonical trunk；该 family 继续保持 `supporting`
- family transition index:
  - `docs/guides/chrome-devtools/INDEX.md`
- active navigation:
  - `docs/INDEX.md` 已减少对 fix/solution leaf docs 的直接暴露
- retention duty:
  - `CHROME_DEVTOOLS_MCP_FIX_GUIDE.md`
  - `CHROME_DEVTOOLS_MCP_SOLUTION.md`
  - 以上文档继续保留为 specialized/reference docs

## Expected Effect

- 根导航优先展示 Chrome DevTools MCP 使用、WSL2 远程调试和 MyStocks 项目测试入口
- fix/solution 总结不再与主入口平级暴露，但仍可通过 family index 进入
- 后续若这些总结材料的实际入链继续下降，可继续逐份评估 archive/delete
