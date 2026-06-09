# Mock 数据系统历史快照

> **历史快照说明**:
> 本文件保留 2025 年底早期 Mock 系统整理阶段的说明脉络，仅作为历史背景参考，不再作为当前 Mock/Real 数据治理、切换流程或实现边界的主入口。
>
> 当前有效入口请优先阅读：
> - [`INDEX.md`](./INDEX.md)
> - [`MOCK_DATA_USAGE_RULES.md`](./MOCK_DATA_USAGE_RULES.md)
> - [`MOCK_REAL_DATA_SWITCHING_GUIDE.md`](./MOCK_REAL_DATA_SWITCHING_GUIDE.md)
>
> 若涉及仓库级共享规则、审批门禁或当前主线治理口径，请以 [`architecture/STANDARDS.md`](../../../architecture/STANDARDS.md) 和 [`openspec/specs/api-integration/spec.md`](../../../openspec/specs/api-integration/spec.md) 为准。

## 为什么保留

- 该文件记录了仓库早期将前端 `web/frontend/src/mock/` 与后端 `src/mock/` 作为专题资产集中梳理时的历史认知。
- 它能帮助理解为何仓库中仍存在较多 page-level mock 文件、桥接脚本和旧页面引用。
- 它不再代表当前主线的“Mock 使用规则”或“Mock/Real 切换流程”。

## 当前应如何理解 Mock

- Mock 的主要作用是前后端解耦开发与测试稳定性，不是通用兜底成功路径。
- 对已进入 `verified` 的页面，主线要求是真实接口优先，失败时显式暴露 `loading / error / empty / request id`，不得对同一路径静默回退 mock。
- 对仍处于 `pending` 的页面，可以保留壳层、加载态、错误态、空态和 blocker 登记，但不得臆造契约字段。

以上口径分别对应：

- [`architecture/STANDARDS.md`](../../architecture/STANDARDS.md)
- [`openspec/specs/api-integration/spec.md`](../../../openspec/specs/api-integration/spec.md)

## 与当前仓库的关系

- 仓库中仍可见 `src/mock/`、`src/data_sources/mock/`、`web/backend/app/mock/`、`web/frontend/src/mock/` 等实现与测试资产。
- 这些资产说明 Mock 系统并未消失，但当前治理重点已经从“统一描述所有 Mock 文件”转向“明确 Mock 的允许场景、禁止场景和真实接口主链边界”。
- 因此，当前读者不应再把“Mock 文件数量”“接口总数”“覆盖率”“服务正常运行”等旧统计值视为当前事实。

## 历史内容范围

此文件过去主要覆盖：

- 早期双层 Mock 架构说明
- page-level mock 文件清单
- 早期桥接脚本与导入模式
- 若干旧页面与旧统计口径

这些内容已经不再维护为 current truth。

## 迁移后的阅读路径

如果你现在要做的是：

- 理解 Mock 使用边界：看 [`MOCK_DATA_USAGE_RULES.md`](./MOCK_DATA_USAGE_RULES.md)
- 了解如何切换 Mock/Real：看 [`MOCK_REAL_DATA_SWITCHING_GUIDE.md`](./MOCK_REAL_DATA_SWITCHING_GUIDE.md)
- 浏览整个专题文档家族：看 [`INDEX.md`](./INDEX.md)

## 保留策略

- 当前状态：`historical retention`
- 默认用途：历史背景和旧实现线索
- 后续策略：若 inbound links 继续下降，可再评估 archive/delete，而不是继续把本文件补写成主指南
