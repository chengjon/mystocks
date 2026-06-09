# PM2 Guide Family

> **导航说明**:
> 本文件是 `docs/guides/pm2/` 的 transition index，不是当前仓库统一运行基线、E2E 主入口或共享规则的唯一事实来源。
> 若涉及环境一致性、默认服务地址、审批门禁或仓库级共享规则，请优先阅读 [`architecture/STANDARDS.md`](../../../architecture/STANDARDS.md)；若涉及当前运维主线，再结合 [`docs/operations/README.md`](../../operations/README.md) 与 [`docs/testing/TESTING_GUIDE.md`](../../testing/TESTING_GUIDE.md)。

## Current Entry Order

这一 family 当前角色是 `supporting`，用于 PM2 / tmux / Playwright 运维与测试专题说明，不承担仓库级 trunk。推荐阅读顺序：

1. [`PM2_INTEGRATION_TEST_WORKFLOW.md`](./PM2_INTEGRATION_TEST_WORKFLOW.md)
2. [`PM2_PLAYWRIGHT_TESTING_GUIDE.md`](./PM2_PLAYWRIGHT_TESTING_GUIDE.md)
3. [`PM2_QUICK_START_GUIDE.md`](./PM2_QUICK_START_GUIDE.md)
4. [`PM2_TMUX_LNV_COLLABORATION_GUIDE.md`](./PM2_TMUX_LNV_COLLABORATION_GUIDE.md)
5. 再按需进入历史审核意见

## Active Supporting Guides

- [`PM2_INTEGRATION_TEST_WORKFLOW.md`](./PM2_INTEGRATION_TEST_WORKFLOW.md)
  - 当前仓库前后端整合后的 PM2 集成测试执行入口
- [`PM2_PLAYWRIGHT_TESTING_GUIDE.md`](./PM2_PLAYWRIGHT_TESTING_GUIDE.md)
  - PM2 部署与 Playwright 自动化测试主指南
- [`PM2_QUICK_START_GUIDE.md`](./PM2_QUICK_START_GUIDE.md)
  - PM2 / tmux / lnav 快速启动入口
- [`PM2_TMUX_LNV_COLLABORATION_GUIDE.md`](./PM2_TMUX_LNV_COLLABORATION_GUIDE.md)
  - PM2 / tmux / lnav 协作开发与运维执行细则

## Retained Historical References

- [`PM2_PLAYWRIGHT_TESTING_GUIDE_REVIEW.md`](./PM2_PLAYWRIGHT_TESTING_GUIDE_REVIEW.md)
  - 历史审核意见和反馈记录，保留作审计参考

## Retention Rule

- 该 family 当前保留为 `supporting`，不升级为新的 canonical docs trunk
- 根导航只应暴露当前常用入口，历史审核意见统一通过本 index 进入
- 若后续 review 文档入链继续下降，再按 bounded batch 单独评估 archive/delete
