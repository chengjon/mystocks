# AkShare 市场扩充接口使用指南

> **权威来源声明**:
> 本文件是 `expand-akshare-data-sources` 的专题使用说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及当前实现事实，请同步核对 `openspec/changes/expand-akshare-data-sources/tasks.md`、当前代码与定向测试结果。

> **开发者文档说明**:
> 本文件用于说明当前仓库内已经落地的 AkShare 市场扩充接口如何使用、当前缺口在哪里，以及更新频率 / 缓存边界应如何理解。

**最后更新**: 2026-05-03  
**适用范围**: `src/adapters/akshare/market_adapter/` 与 `web/backend/app/api/akshare_market/`

---

## 1. 当前已实现范围

当前 change 已落地的接口范围是：

- 第 1 节：市场总貌
- 第 2 节：个股信息
- 第 3 节：资金流向
- 第 4 节：预测和分析
- 第 5 节：板块和行业
- 第 6 节：仅补齐 `stock_hot_follow_xq`、`stock_board_change_em`、`stock_zt_pool_em`、`stock_changes_em`

当前仍未落地的第 6 节接口：

- `stock_news_main_em`
- `stock_dt_pool_em`
- `stock_strong_pool_em`
- `stock_weak_pool_em`
- `stock_new_em`

这些缺口当前不是“忘记接线”，而是本地 `akshare` 环境里未检出对应同名函数，不能拿近似接口替代。

## 2. 当前入口分布

### 2.1 Adapter 入口

- 聚合类：`src/adapters/akshare/market_adapter/adapter.py`
- 情绪 / 监控类方法：`src/adapters/akshare/market_adapter/stock_sentiment.py`

本轮新增的 4 个方法是：

- `get_stock_hot_follow_xq(symbol="最热门")`
- `get_stock_board_change_em()`
- `get_stock_zt_pool_em(date)`
- `get_stock_changes_em(symbol="大笔买入")`

### 2.2 API 路由入口

本轮新增 / 当前推荐关注的实时监控路由位于：

- `web/backend/app/api/akshare_market/sentiment_monitor.py`

公开路径：

- `GET /api/akshare/market/stock/hot-follow/xq`
- `GET /api/akshare/market/stock/zt-pool/em`
- `GET /api/akshare/market/stock/changes/em`
- `GET /api/akshare/market/board/change/em`

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

### 3.4 板块异动

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
- `akshare_stock_changes_em`: `realtime`

### 4.2 缓存边界

当前仓库没有为这 3 个接口单独落一套 AkShare 专题缓存层。

这意味着：

- 当前可确认的缓存语义主要是“配置层面的 `update_frequency` 元数据”
- `tests/api/file_tests/test_akshare_market_api.py::test_smart_cache_integration` 仍只是 file-level placeholder，不应被解读为这 3 个接口已有专属缓存闭环
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
- 只改 registry 或只改 API，不补 adapter / tests
- 把历史 `AKSHARE_INTERFACE_MAPPING.md` 当成当前实现完成证据
