# B4.014 Phase 1.1 — FundFlow 前后端字段漂移重大发现

**Date**: 2026-06-29
**Author**: Claude (auto worklog)
**Status**: 阻塞（P0）— Phase 1.1 第二批启动前必须用户决策
**Predecessor**: `b4-014-phase1-1-batch1-allowlist-tests-playbook-2026-06-29.md`

---

## TL;DR

Phase 1.1 第二批启动前的字段映射准备工作发现：**前端 `FundFlow.vue` 消费的字段名（中文）与后端实际响应字段名（英文）完全不匹配**。这意味着 FundFlow 页面**当前可能已经处于 broken 状态**，与 OpenStock 迁移无关。

迁移工作无法继续推进，必须先解决漂移问题。需要用户决策：是先修复漂移（让前端真正能消费后端数据），还是绕过漂移（迁移时按前端预期字段名输出，等于"按错误的契约对齐"）。

---

## 1. 证据链

### 1.1 后端原 akshare 方法实际返回字段

**`get_stock_hsgt_fund_flow_summary_em`**（`src/adapters/akshare/market_adapter/fund_flow.py:33-42`）:

```python
df = df.rename(columns={
    "日期": "date",
    "北向资金": "north_money",
    "南向资金": "south_money",
    "当日额度": "daily_quota",
    "当日余额": "daily_balance",
    "当日使用额度": "daily_used_quota",
})
```

返回列: `date / north_money / south_money / daily_quota / daily_balance / daily_used_quota / start_date / end_date / query_timestamp`

**`get_stock_hsgt_north_acc_flow_in_em`**（`src/adapters/akshare/market_adapter/fund_flow.py:184-193`）:

```python
df = df.rename(columns={
    "股票代码": "symbol",
    "日期": "date",
    "持股数量": "hold_amount",
    "持股市值": "hold_market_value",
    "持股变化数量": "hold_change_amount",
    "持股变化市值": "hold_change_value",
})
df["fund_direction"] = "north"
```

返回列: `symbol / date / hold_amount / hold_market_value / hold_change_amount / hold_change_value / fund_direction / query_timestamp`

### 1.2 前端 `FundFlow.vue` 实际消费字段

`web/frontend/src/views/data/fundFlowPageData.ts:105-111, 169`:

```typescript
const shanghaiRow = summaryRows.find((row) => row.板块 === '沪股通')
const shenzhenRow = summaryRows.find((row) => row.板块 === '深股通')
const northRows = summaryRows.filter((row) => row.资金方向 === '北向')
const northAmount = northRows.reduce((sum, row) => sum + parseNumber(row.成交净买额), 0)
const northChange = northRows.reduce((sum, row) => sum + parseNumber(row.指数涨跌幅), 0) / northRows.length
// ...
const date = typeof row.交易日 === 'string' ? row.交易日 : ''
```

消费字段: `板块 / 资金方向 / 成交净买额 / 指数涨跌幅 / 交易日`

### 1.3 漂移对比

| 接口 | 后端实际返回 | 前端期望 | 漂移 |
|---|---|---|---|
| `hsgt-summary` | `date, north_money, south_money, daily_quota, daily_balance, daily_used_quota` | `板块, 资金方向, 成交净买额, 指数涨跌幅, 交易日` | **完全不一致** |
| `north-stock/{symbol}` | `symbol, date, hold_amount, hold_market_value, hold_change_amount, hold_change_value, fund_direction` | （前端 FundFlow.vue 未消费此接口） | 不适用 |

`hsgt-summary` 接口前端消费的 `板块/资金方向/成交净买额/指数涨跌幅/交易日` 字段在**后端响应里根本不存在**。`parseNumber(undefined)` 会得到 `NaN`，`buildFundOverview()` 会返回全 NaN 的数据，前端图表显示为空或 0。

### 1.4 mock 数据可能掩盖了问题

`web/frontend/src/api/mockApiClient.ts:105` 含 `/akshare/market/fund-flow/hsgt-summary` 的 mock 路由。开发环境可能一直走 mock 数据（mock 用前端期望的中文字段名），掩盖了真实后端响应与前端期望的漂移。

---

## 2. 推论

1. **当前 `FundFlow.vue` 在生产环境（走真实后端）可能显示为空数据或 NaN**。这是一个 P0 主线阻塞，远比 OpenStock 迁移更紧急。
2. **Phase 1.1 第二批"切换 OpenStock + 加字段映射"的策略需要重新评估**。原本的"中→英映射"假设基于"后端原返回中文"，但事实是后端原返回英文。映射方向其实是反的。
3. **OpenStock 返回的英文字段（`board_name/fund_direction/net_buy_amount/index_change_pct/trade_date`）反而更接近前端期望的语义**——但仍需做 `board_name→板块、fund_direction→资金方向、net_buy_amount→成交净买额、index_change_pct→指数涨跌幅、trade_date→交易日` 的英→中翻译，才能让前端正常消费。

---

## 3. 需要用户决策的问题

### 问题 A：是否先验证当前生产环境 FundFlow 页面状态？

启动 backend + frontend（关闭 mock），打开 `/data/fund-flow`，截图查看实际渲染结果。如果显示全 0 或 NaN，证实漂移已存在。

### 问题 B：迁移策略如何调整？

三个候选方向：

**方向 1 — 按前端期望对齐（OpenStock → 中文键名映射）**
- 切换层把 OpenStock 英文字段翻译为前端期望的中文字段名（`board_name→板块` 等）
- 前端零改动
- 副作用：等于"按前端错误契约对齐"，未来修前端时还要再改一次
- 适用前提：用户希望 Phase 1.1 仅"切换数据源不破坏现状"，漂移留待后续 P0 修复

**方向 2 — 按后端实际对齐（OpenStock 英文字段直接透传，修前端）**
- 切换层 OpenStock 英文字段直接输出
- 同步修 `fundFlowPageData.ts` 改为消费 `board_name/fund_direction/net_buy_amount/index_change_pct/trade_date`
- 副作用：本批次范围爆炸（前端改动），违反 SOT §七"前端零感知"
- 适用前提：用户接受一次性修复漂移，作为 Phase 1.1 的一部分

**方向 3 — 暂停迁移，先单独 P0 修漂移**
- 不动 OpenStock 迁移
- 单独立项修前后端字段漂移，建立一份"真实可用"的契约
- 然后再启动 Phase 1.1 第二批
- 适用前提：用户认为漂移是 P0、不能在漂移基础上做迁移

### 问题 C：mock 数据是否需要同步处理？

如果 mock 一直在掩盖问题，需要在 PR 中明确 mock 是否同步对齐到新契约。

---

## 4. 推荐方案

**推荐方向 3（暂停迁移，先修漂移）**，理由：

1. **SOT §三 "迁移必须自带收口条件"**: "如果无法说明旧层怎么退场，就不能引入新的平行层"。在不知道前端真实期望的情况下切换 OpenStock，等于在漂移的基础上叠加迁移，未来回滚与诊断都困难。
2. **CLAUDE.md "主线对齐"红线**: "系统可用性为最高验收标准"。FundFlow 页面字段漂移属于主线阻塞，必须先于迁移修复。
3. **CLAUDE.md "禁止超前修复未来未启用功能"**: 反向解读——已经发现主线阻塞时必须先修主线，再推迁移。

**修漂移的最小动作**:
- 启动 backend+frontend 验证当前 FundFlow 页面真实状态（截图存证）
- 决策"以哪一方为真相源"（推荐以前端 mock 数据的字段契约为真相源，因为前端期望更详细，包含沪股通/深股通/北向/南向区分）
- 改 `fund_flow.py` 的两个 endpoint 让响应字段对齐真相源
- 同步确认 mock 数据与真相源一致
- 完成后重启 Phase 1.1 第二批

---

## 5. Phase 1.1 第二批启动 checklist 更新

原 `b4-014-phase1-1-batch1-allowlist-tests-playbook-2026-06-29.md` §四 的"第二批启动入口"必须先经过本 worklog 的用户决策才能继续。**禁止在漂移未解决前直接切换 fund_flow.py**。

---

## 修订历史

- **2026-06-29 V1.0（初始）**: 第二批启动前发现前后端字段漂移，列出三方向决策选项，推荐方向 3。等待用户授权。
