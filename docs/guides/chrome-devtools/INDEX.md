# Chrome Devtools Guide Family

> **导航说明**:
> 本文件是 `docs/guides/chrome-devtools/` 的 transition index，不是仓库共享规则、当前调试执行口径或唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 [`architecture/STANDARDS.md`](/opt/claude/mystocks_spec/architecture/STANDARDS.md)；若涉及具体执行入口，再结合根目录 `AGENTS.md`、当前代码与最新验证结果核对。

## Current Entry Order

这一 family 当前角色是 `supporting`，用于保留 Chrome DevTools MCP、WSL2 远程调试和项目测试指引，不承担仓库级 trunk。推荐阅读顺序：

1. [`CHROME_DEVTOOLS_MCP_GUIDE.md`](./CHROME_DEVTOOLS_MCP_GUIDE.md)
2. [`chrome-devtools-wsl2-guide.md`](./chrome-devtools-wsl2-guide.md)
3. [`mystocks-chromedevtools-testing-guide.md`](./mystocks-chromedevtools-testing-guide.md)
4. 再按需进入修复与方案总结文档

## Active Supporting Guides

- [`CHROME_DEVTOOLS_MCP_GUIDE.md`](./CHROME_DEVTOOLS_MCP_GUIDE.md)
  - Chrome DevTools MCP 集成与快速使用入口
- [`chrome-devtools-wsl2-guide.md`](./chrome-devtools-wsl2-guide.md)
  - WSL2 远程调试配置指南
- [`mystocks-chromedevtools-testing-guide.md`](./mystocks-chromedevtools-testing-guide.md)
  - MyStocks 项目测试实践入口

## Retained Specialized References

- [`CHROME_DEVTOOLS_MCP_FIX_GUIDE.md`](./CHROME_DEVTOOLS_MCP_FIX_GUIDE.md)
  - Chrome DevTools MCP 问题修复指南
- [`CHROME_DEVTOOLS_MCP_SOLUTION.md`](./CHROME_DEVTOOLS_MCP_SOLUTION.md)
  - Chrome DevTools MCP 完整解决方案总结

## Retention Rule

- 该 family 当前保留为 `supporting`，不升级为新的 canonical docs trunk
- 根导航只保留 MCP 使用、WSL2 配置和项目测试这 3 个直接入口，修复与方案总结统一通过本 index 进入
- 若后续 fix/solution 材料的实际入链继续下降，可继续按 bounded batch 单独评估 archive/delete
