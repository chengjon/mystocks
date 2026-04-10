## 1. Implementation

> **使用说明**:
> 本文件用于记录当前 OpenSpec 变更的执行清单、操作步骤或协作约束，帮助跟踪实施过程。
> 其中勾选状态、执行顺序和局部说明仅代表任务推进视角，不应脱离 proposal、design、正式 specs、`architecture/STANDARDS.md` 与实际验证结果单独解读为最终事实。

- [x] 1.1 完成 `Gate-0` ArtDeco 治理校对：统一 `Container-Tab` 架构、`components/[domain]` 与 `[domain]-tabs` 边界、`router/menu/API/tokens` SSOT
- [x] 1.2 为全部 `P0/P1` 页面建立批次矩阵，并标记 `container-only`、`tab-only`、`needs-domain-component-extraction`、`needs-token-cleanup`、`api-pending-blocked`
- [x] 1.3 执行 `P0-A` 市场核心批次：`Market-Realtime`、`Market-Technical`
- [x] 1.4 执行 `P0-B` 入口壳层批次：`Login`、`DealingRoom`
- [x] 1.5 执行 `P1-A` 市场数据域批次：`Market-LHB`、`Data-Industry`、`Data-Concept`、`Data-FundFlow`、`Data-Indicator`
- [x] 1.6 执行 `P1-B` 信号与持仓共享组件批次：`Watchlist-Signals`、`Strategy-Signals`、`Trade-Signals`、`Trade-Positions`、`Trade-Portfolio`、`Risk-PnL`
- [x] 1.7 执行 `P1-C` 策略主链批次：`Strategy-Repo`、`Strategy-Parameters`、`Strategy-Backtest`
- [x] 1.8 执行 `P1-D` 风控主链批次：`Risk-Management`、`Risk-Overview`、`Risk-StopLoss`、`Risk-Alerts`
- [x] 1.9 执行 `P1-E` 自选与交易边缘批次：`Watchlist-Manage`、`Watchlist-Screener`、`Trade-Terminal`、`Trade-History`
- [x] 1.10 执行 `P2` 页面收口批次：`Strategy-GPU`、`Strategy-Opt`、`Strategy-Pos`、`Risk-News`、`System-Config`、`System-Health`、`System-API`、`System-Data`
- [x] 1.11 按批次补齐 `type-check`、`smoke`、`E2E`、页面/API 状态回写与阻塞登记
- [x] 1.12 输出验证结果、服务状态、遗留风险与 `API pending` 阻塞清单
