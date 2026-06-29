# B4.014 P0 — FundFlow 字段漂移修复验证完工

**Date**: 2026-06-29
**Author**: Claude (auto worklog)
**Status**: ✅ 完工 — Phase 1.1 第二批解锁
**Predecessor**: `b4-014-phase1-1-drift-fix-decision-matrix-2026-06-29.md`

---

## TL;DR

P0 漂移修复（方向 3 + 候选 a）已经过 API + 浏览器双层面验证落地。前端 FundFlow 页面在真实后端下成功渲染沪深区分、指数涨跌幅与个股排行数据。Phase 1.1 第二批（OpenStock 切换）解锁。

---

## 1. 落地 commits

| Commit | 内容 |
|---|---|
| `0a09b1a1f` | B4.014-P0: fix fundflow field drift (hsgt-summary + big-deal) — 删除失败 rename, 透明透传原始中文字段; north-stock 返回 501; mockApiClient 同步对齐 |
| `f746a42d0` | B4.014-P0: use INTERNAL_SERVER_ERROR for north-stock 501 — 修正 AttributeError: ErrorCodes.INTERNAL_ERROR 不存在 |

---

## 2. API 层验证（curl + JWT）

| Endpoint | 状态 | 字段验证 |
|---|---|---|
| `GET /api/akshare/market/fund-flow/hsgt-summary` | HTTP 200, 4 行 | 16 列中文宽表含 `板块/资金方向/成交净买额/指数涨跌幅/交易日` — 全部对齐前端 `fundFlowPageData.ts:105-111, 169` 真相源 |
| `GET /api/akshare/market/fund-flow/big-deal` | HTTP 200, 5000 行 | 10 列含 `symbol/股票简称/成交价格/成交量/成交额/大单性质/涨跌幅` — 对齐 `buildStockRanking` 期望 |
| `GET /api/akshare/market/fund-flow/north-stock/600519` | HTTP 200 success=false | 友好消息: "north-stock/600519 暂不可用: akshare.stock_hsgt_north_acc_flow_in_em 在 akshare 1.18.60 已移除, 待 OpenStock NORTHBOUND_HOLDING 切换恢复" |

**关键发现**: 浏览器验证期间发现 `ErrorCodes.INTERNAL_ERROR` 属性不存在 (实际为 `INTERNAL_SERVER_ERROR`)，commit `f746a42d0` 修正。

---

## 3. 浏览器层验证（Playwright + 真实后端）

**URL**: `http://localhost:3020/data/fund-flow` (VITE_APP_MODE=real, 无 mock)

### 渲染证据（来自 a11y snapshot）

**Fund Overview 卡片**:
- 沪股通净流入 / 深股通净流入 / 北向资金总额 / 主力净流入
- 变化字段: `+1.16% / +0.19% / +0.67% / +0%` ← **指数涨跌幅真实渲染**
- 主力净流入: `96,328.85` ← `成交净买额` 聚合真实数据

**Stock Ranking 表（11+ 行）**:
- 中控技术 688777 118.45 -0.50 +281.91
- 普冉股份 688766 737.20 1.40 +88.46
- 海天瑞声 688787 127.65 -2.24 +51.06
- 列: 排名/股票名称/代码/最新价/涨跌幅/资金流入/主力净额

### Console 状态
- 0 errors (仅 dashboard health/indicator 超时与 icon 警告，与 FundFlow 无关)
- 无 FundFlow fetch 错误

---

## 4. P0 修复范围回顾

| 文件 | 修改内容 | LOC |
|---|---|---|
| `src/adapters/akshare/market_adapter/fund_flow.py` | 删除 hsgt-summary/big-deal 的陈年 rename; north-stock 方法体改为返回空 DataFrame + 警告日志 | -55 +23 |
| `web/backend/app/api/akshare_market/fund_flow.py` | north-stock endpoint 改为返回 501 友好消息 (含 `INTERNAL_SERVER_ERROR` 修正) | -28 +11 |
| `web/frontend/src/api/mockApiClient.ts` | hsgt-summary / big-deal mock 对齐真相源中文宽表契约 | -14 +24 |

**总计**: 3 文件, ~+57 -97 LOC

---

## 5. Phase 1.1 第二批解锁条件

✅ **字段契约已稳定**: hsgt-summary + big-deal 真相源已是前端 mock 契约
✅ **浏览器验证通过**: FundFlow 页面真实后端渲染正常
✅ **north-stock 隔离**: 501 + TODO(B4.014-Phase1.1-batch2) 标记，由 OpenStock NORTHBOUND_HOLDING 接管
✅ **mock 已对齐**: 不会再掩盖未来切换时的字段漂移

**下一步**: Phase 1.1 第二批可以启动，切换 `fund_flow.py` 至 OpenStock `NORTHBOUND_FLOW` 类别（字段语义与 hsgt-summary 真相源一致）+ `NORTHBOUND_HOLDING` 类别（接管 north-stock）。

参考:
- `DOMAIN_MIGRATION_PLAYBOOK.md` §三 (Phase 1.1 第二批入口)
- `web/frontend/src/views/data/fundFlowPageData.ts` (真相源)

---

## 修订历史

- **2026-06-29 V1.0（初始）**: P0 验证完工，列 API + 浏览器两层证据，Phase 1.1 第二批解锁。
