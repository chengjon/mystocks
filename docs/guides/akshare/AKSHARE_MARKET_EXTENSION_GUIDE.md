# AkShare 市场扩充接口使用指南

> **权威来源声明**:
> 本文件是 `expand-akshare-data-sources` 的专题使用说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及当前实现事实，请同步核对 `openspec/changes/expand-akshare-data-sources/tasks.md`、当前代码与定向测试结果。

> **开发者文档说明**:
> 本文件用于说明当前仓库内已经落地的 AkShare 市场扩充接口如何使用、当前缺口在哪里，以及更新频率 / 缓存边界应如何理解。

**最后更新**: 2026-05-04
**适用范围**: `src/adapters/akshare/market_adapter/` 与 `web/backend/app/api/akshare_market/`

---

## 1. 当前已实现范围

当前 change 已落地的接口范围是：

- 第 1 节：市场总貌
- 第 2 节：个股信息
- 第 3 节：资金流向
- 第 4 节：预测和分析
- 第 5 节：板块和行业
- 第 6 节：已补齐 `stock_hot_follow_xq`、`stock_board_change_em`、`stock_zt_pool_em`、`stock_dt_pool_em`、`stock_strong_pool_em`、`stock_changes_em`、`stock_new_em`

当前仍技术性缺失、但已排除出 runtime scope 的第 6 节条目：

- `stock_news_main_em`

当前已退役的第 6 节条目：

- `stock_weak_pool_em`

除 `stock_dt_pool_em -> stock_zt_pool_dtgc_em`、`stock_strong_pool_em -> stock_zt_pool_strong_em` 与 `stock_new_em -> stock_zt_pool_sub_new_em` 这三条已批准并落地的官方改名映射外，剩余缺口当前不是“忘记接线”，而是本地 `akshare` 环境里未检出可直接接受的实现，不能拿近似接口替代。`stock_news_main_em` 当前已作为 excluded item 收口，`stock_weak_pool_em` 则已基于业务决策与上游缺口正式收口为 retired item。

### 1.1 当前门禁快照

2026-05-03 在当前环境实跑：

```bash
python scripts/dev/quality_gate/run_akshare_market_gates.py \
  --output-dir /tmp/akshare-market-gates
```

结果是：

- 本地 `akshare` 版本：`1.18.60`
- 追踪函数总数：`9`
- 当前可用：`7`
- 当前缺失：`1`
- 当前已退役：`1`
- repo-truth violation：`0`
- 统一门禁结果：`pass=true`

当前唯一 `missing` 项对应 `stock_news_main_em`，但它已在 OpenSpec 与 repo-truth 中正式标记为 excluded，不再阻塞第 6 节运行时收口。

当前 availability 报告的分辨口径是：

- `native`：同名函数直接可用
- `mapped`：命中已批准的官方改名映射，当前包括 `stock_dt_pool_em -> stock_zt_pool_dtgc_em`、`stock_strong_pool_em -> stock_zt_pool_strong_em` 与 `stock_new_em -> stock_zt_pool_sub_new_em`
- `retired`：业务已决定不再承接，且当前本地 `akshare` 无同名函数或已批准官方候选
- `missing`：既没有同名函数，也没有已批准映射

当前 `summary.help_candidate_functions` 仍只保留尚未批准的人工评估线索：

- `stock_news_main_em` -> `stock_news_main_cx`

额外已考虑但不映射到当前第 6 节条目的官方 pool 函数：

- `stock_zt_pool_previous_em`：昨日涨停股池
- `stock_zt_pool_zbgc_em`：炸板股池

这些提示只用于“本地包里是否存在相近能力”的审计参考；除已批准映射项外，不自动计为已实现。

## 2. 当前入口分布

### 2.1 Adapter 入口

- 聚合类：`src/adapters/akshare/market_adapter/adapter.py`
- 情绪 / 监控类方法：`src/adapters/akshare/market_adapter/stock_sentiment.py`

本轮新增 / 当前推荐关注的 7 个方法是：

- `get_stock_hot_follow_xq(symbol="最热门")`
- `get_stock_board_change_em()`
- `get_stock_zt_pool_em(date)`
- `get_stock_dt_pool_em(date)`
- `get_stock_strong_pool_em(date)`
- `get_stock_new_em(date)`
- `get_stock_changes_em(symbol="大笔买入")`

### 2.2 API 路由入口

本轮新增 / 当前推荐关注的实时监控路由位于：

- `web/backend/app/api/akshare_market/sentiment_monitor.py`

公开路径：

- `GET /api/akshare/market/stock/hot-follow/xq`
- `GET /api/akshare/market/stock/zt-pool/em`
- `GET /api/akshare/market/stock/dt-pool/em`
- `GET /api/akshare/market/stock/strong-pool/em`
- `GET /api/akshare/market/stock/new/em`
- `GET /api/akshare/market/stock/changes/em`
- `GET /api/akshare/market/board/change/em`

### 2.3 扩展前的标准门禁入口

在继续实现任何第 6 节缺口前，先运行统一门禁：

```bash
python scripts/dev/quality_gate/run_akshare_market_gates.py \
  --output-dir /tmp/akshare-market-gates
```

优先关注 3 份报告：

- `/tmp/akshare-market-gates/akshare-market-function-availability.json`
- `/tmp/akshare-market-gates/akshare-market-repo-truth-gate.json`
- `/tmp/akshare-market-gates/akshare-market-gates-summary.json`

其中 availability 报告新增可读字段：

- `functions[].help_candidates`
- `functions[].resolution_status`
- `summary.retired_functions`
- `summary.help_candidate_functions`

若只想拆分定位，再单独运行叶子脚本。MyStocks 这一侧只负责校验与审计，不自动生成业务代码，也不补第三方替代实现。

## 3. 使用示例

### 3.1 股票热度排行

```bash
curl "http://localhost:8888/api/akshare/market/stock/hot-follow/xq?symbol=最热门"
```

可选 `symbol`:

- `最热门`
- `本周新增`

### 3.2 盘口异动

```bash
curl "http://localhost:8888/api/akshare/market/stock/changes/em?symbol=大笔买入"
```

当前仓库只保证把 query 原样透传给 `akshare.stock_changes_em(symbol=...)`。可用值应以当前安装的 `akshare` 版本为准。

### 3.3 涨停股池

```bash
curl "http://localhost:8888/api/akshare/market/stock/zt-pool/em?date=20241008"
```

该接口要求显式传入交易日 `date`，格式为 `YYYYMMDD`。

### 3.4 跌停股池

```bash
curl "http://localhost:8888/api/akshare/market/stock/dt-pool/em?date=20241011"
```

该接口对外仍保持 canonical 名称 `stock_dt_pool_em`，内部映射到本地 `akshare.stock_zt_pool_dtgc_em(date=...)`。

### 3.5 强势股池

```bash
curl "http://localhost:8888/api/akshare/market/stock/strong-pool/em?date=20241011"
```

该接口对外仍保持 canonical 名称 `stock_strong_pool_em`，内部映射到本地 `akshare.stock_zt_pool_strong_em(date=...)`。

### 3.6 次新股池

```bash
curl "http://localhost:8888/api/akshare/market/stock/new/em?date=20241011"
```

该接口对外仍保持 canonical 名称 `stock_new_em`，内部映射到本地 `akshare.stock_zt_pool_sub_new_em(date=...)`。

### 3.7 板块异动

```bash
curl "http://localhost:8888/api/akshare/market/board/change/em"
```

该接口无 query 参数。

## 4. 更新频率与缓存边界

### 4.1 更新频率真相源

当前更新频率以 `config/data_sources_registry.yaml` 中对应 entry 的 `update_frequency` 为准：

- `akshare_stock_hot_follow_xq`: `hourly`
- `akshare_stock_board_change_em`: `realtime`
- `akshare_stock_zt_pool_em`: `realtime`
- `akshare_stock_dt_pool_em`: `realtime`
- `akshare_stock_strong_pool_em`: `realtime`
- `akshare_stock_new_em`: `realtime`
- `akshare_stock_changes_em`: `realtime`

### 4.2 缓存边界

当前仓库没有为这组接口单独落一套 AkShare 专题缓存层。

这意味着：

- 当前可确认的缓存语义主要是“配置层面的 `update_frequency` 元数据”
- `tests/api/file_tests/test_akshare_market_api.py::test_smart_cache_integration` 仍只是 file-level placeholder，不应被解读为这组接口已有专属缓存闭环
- 若后续要把这些接口接入明确缓存策略，应单独补：
  - runtime cache 入口
  - cache invalidation 规则
  - focused tests
  - 文档回写

## 5. 开发时的 repo-truth 边界

扩 AkShare 市场接口时，必须同时更新：

1. adapter 方法
2. API 路由
3. `config/data_sources_registry.yaml`
4. focused tests
5. OpenSpec 台账
6. 专题文档

禁止的做法：

- 用“名称相近”的 AkShare 函数顶替缺失的同名函数，然后直接勾任务
- 绕开 gate / repo-truth，私下把未批准候选升级成运行时映射
- 只改 registry 或只改 API，不补 adapter / tests
- 把历史 `AKSHARE_INTERFACE_MAPPING.md` 当成当前实现完成证据
