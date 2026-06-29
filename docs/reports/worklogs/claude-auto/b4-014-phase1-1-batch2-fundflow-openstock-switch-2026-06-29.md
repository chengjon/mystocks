# B4.014 Phase 1.1 — FundFlow OpenStock 切换完工 (Batch 2)

**Date**: 2026-06-29
**Author**: Claude (auto worklog)
**Status**: ✅ 完工 — Phase 1.1 第二批落地，FundFlow 域 2 个端点切换至 OpenStock
**Predecessor**: `b4-014-p0-fundflow-drift-fix-verification-2026-06-29.md`

---

## TL;DR

Phase 1.1 第二批（FundFlow 域 OpenStock 切换）已完成。`hsgt-summary` 走
`NORTHBOUND_FLOW`，`north-stock/{symbol}` 走 `NORTHBOUND_HOLDING`，两个端点
均以中文宽表契约响应（前端真相源），并经过 API + 单元 + 浏览器三层验证。

Phase 1.1 全部 8 个子任务关闭，剩余 6 个 P2/P3 endpoint 待 OpenStock 中台补
类别后单独立项（见 `DOMAIN_MIGRATION_PLAYBOOK.md` §三）。

---

## 1. 落地 commits

| Commit | 内容 |
|---|---|
| `a40f38a0d` | B4.014-M1: switch fundflow hsgt-summary + north-stock to OpenStock — 2 文件, +197 −30 |
| `3c90212fb` | B4.014-M1: add API e2e tests for fundflow OpenStock switch — 6 测试用例 |

---

## 2. 改动文件清单

### 2.1 `web/backend/app/api/akshare_market/fund_flow.py`

| 区域 | 改动 |
|---|---|
| 顶部 helpers | 新增 `_build_openstock_client()` 工厂 + `_translate_northbound_flow_row()` + `_translate_northbound_holding_row()` 翻译函数 |
| `DEFAULT_OPENSTOCK_BASE_URL` | `http://192.168.123.104:8040` (与 `market_data_request.py` 对齐) |
| `get_hsgt_fund_flow_summary` handler | 替换为调用 `client.fetch("NORTHBOUND_FLOW", params={start_date, end_date})`，翻译为中文宽表 |
| `get_north_fund_stock` handler | 替换之前的 501 占位，调用 `client.fetch("NORTHBOUND_HOLDING", params={symbol})`，翻译为持股中文宽表 |
| OpenAPI 响应示例 | `INTERNAL_ERROR → INTERNAL_SERVER_ERROR`，`source: akshare → source: openstock` |

**Mixin 层不动**：`FundFlowMixin.get_stock_hsgt_*` 保持 akshare wrapper 不变，
其他 6 个 endpoint 不受影响。

### 2.2 `.env.example`

新增 OpenStock 配置段（与 `web/backend/.env` 对齐）：
- `OPENSTOCK_BASE_URL=http://192.168.123.104:8040`
- `OPENSTOCK_API_KEY=` (留空占位)
- `OPENSTOCK_TIMEOUT_SECONDS=5.0`

### 2.3 `tests/api/test_fund_flow_openstock.py` (新增, 334 行)

6 个端点级 e2e 测试，覆盖：
- ✅ 成功路径（NORTHBOUND_FLOW / NORTHBOUND_HOLDING 翻译正确）
- ✅ 空 data 路径（返回 DATA_NOT_FOUND）
- ✅ 上游异常路径（OpenStockClientError → INTERNAL_SERVER_ERROR，不抛 500）

测试边界：在 `_build_openstock_client` 处替换为 MagicMock + AsyncMock，
保留 FastAPI TestClient → router → handler → translator 全链路真实执行。

---

## 3. API 层验证 (curl + JWT)

| Endpoint | 状态 | 关键字段 |
|---|---|---|
| `GET /api/akshare/market/fund-flow/hsgt-summary?start_date=2026-06-20&end_date=2026-06-29` | HTTP 200, count=4, source=openstock | `板块/资金方向/成交净买额/指数涨跌幅/交易日` 全部对齐前端真相源 |
| `GET /api/akshare/market/fund-flow/north-stock/600519` | HTTP 200, count=50, source=openstock, fund_direction=north | 茅台 2017-03-16 起历史持股明细，`持股日期/持股数量/持股市值/持股比例/增持数量/增持金额` 齐全 |

**关键证据 (hsgt-summary 第一行)**:
```json
{"板块": "沪股通", "资金方向": "北向", "成交净买额": 0.0,
 "指数涨跌幅": 1.16, "交易日": "2026-06-29",
 "同期上涨家数": 930, "同期下跌家数": 668, "同期平盘家数": 38,
 "关联指数": "上证指数", "资金净流入": 0.0}
```

OpenStock 原始字段（`board_name / fund_direction / net_buy_amount /
index_change_pct / trade_date / up_count / down_count / ...`）经翻译函数
映射为前端中文宽表，同时保留 OpenStock 富信息作为附加列（`关联指数 /
同期上涨家数` 等），不丢失语义。

---

## 4. 单元 + 端点测试验证

```
pytest tests/api/test_fund_flow_openstock.py — 6 passed
pytest tests/services/openstock_client/test_northbound_flow_parsing.py — existing
pytest tests/services/openstock_client/test_northbound_holding_parsing.py — existing
forbidden_imports.py --path web/backend/app/api/akshare_market/fund_flow.py — PASS
```

---

## 5. 浏览器端到端验证 (Playwright, VITE_APP_MODE=real)

**URL**: `http://localhost:3020/data/fund-flow`

Playbook §4.2 FundFlow 域专属清单:

| 检查项 | 结果 |
|---|---|
| 沪股通净流入卡片 | ✅ "0.00" + 变化 +1.16% (与 OpenStock `index_change_pct=1.16` 一致) |
| 深股通净流入卡片 | ✅ "0.00" + 变化 +0.19% (与 OpenStock `index_change_pct=0.19` 一致) |
| 北向资金总额变化 | ✅ +0.67% ((1.16+0.19)/2 = 0.675, 三舍四入对齐) |
| 主力净流入 | ✅ 96,328.85 (big-deal 聚合真实数据) |
| 个股排行表 | ✅ 20 行真实数据 (中控技术 688777, 普冉股份 688766, 海天瑞声 688787, 华纳药厂 688799, ...) |
| RequestId 显式展示 | ✅ `a3e178eb-f653-44d7-b8a5-b8f493d21811` |
| Console errors | ✅ 0 |

**截图**: `docs/reports/worklogs/claude-auto/phase1-1-batch2-fundflow-verify.png`

---

## 6. Phase 1.1 全域总结

### 6.1 已迁移 (2/8)

| 端点 | OpenStock 类别 | 切换层 |
|---|---|---|
| `hsgt-summary` | `NORTHBOUND_FLOW` | endpoint 层 (本批次) |
| `north-stock/{symbol}` | `NORTHBOUND_HOLDING` | endpoint 层 (本批次) |

### 6.2 待迁移 (6/8, 待 OpenStock 中台补类别)

| 端点 | 缺失类别 | 优先级 |
|---|---|---|
| `hsgt-detail` | `NORTHBOUND_FLOW_DETAIL` | P2 |
| `north-daily` | `NORTHBOUND_DAILY_HISTORY` | P2 |
| `south-daily` | `SOUTHBOUND_DAILY_HISTORY` | P2 |
| `south-stock/{symbol}` | `SOUTHBOUND_HOLDING` | P2 |
| `hsgt-holdings/{symbol}` | `HSGT_INDIVIDUAL_HOLDING` | P3 |
| `big-deal` | `MARKET_BIG_DEAL_RANK` | P3 |

参考: `docs/guides/openstock-migration/DOMAIN_MIGRATION_PLAYBOOK.md` §三.

---

## 7. 收口判定

| 准则 | 状态 |
|---|---|
| SOT §三 "迁移必须自带收口条件" | ✅ 2 个端点完整切换 + 测试 + 浏览器验证 |
| SOT §七 "前端零感知" | ✅ 前端零改动 (契约对齐真相源) |
| 主线对齐 (页面能用) | ✅ FundFlow 页面渲染真实 OpenStock 数据 |
| 字段契约稳定 | ✅ source=openstock provenance 透传 |
| 上游异常容错 | ✅ OpenStockClientError → INTERNAL_SERVER_ERROR, 不抛 500 |

**Phase 1.1 (FundFlow 域)** 完结。

下一步建议:
- Phase 1.2 起按 `DOMAIN_MIGRATION_PLAYBOOK.md` §三 模板启动其他域
- OpenStock 中台若补齐 P2 类别, 可单独立项迁移剩余 4 个 P2 endpoint
- AkshareMarketDataAdapter Mixin 层迁移 (Task #11) 独立立项, 不影响 Phase 1.x 节奏

---

## 修订历史

- **2026-06-29 V1.0 (初始)**: Phase 1.1 第二批完工, 列 commits / 改动 / API+单元+浏览器 三层证据, Phase 1.1 域级总结.
