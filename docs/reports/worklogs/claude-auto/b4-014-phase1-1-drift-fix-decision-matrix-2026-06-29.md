# B4.014 Phase 1.1 — 漂移修复决策矩阵 (P0 决策辅助)

**Date**: 2026-06-29
**Author**: Claude (auto worklog)
**Status**: 决策辅助材料 — 用户决策前不应启动任何代码改动
**Predecessor**: `b4-014-phase1-1-frontend-backend-field-drift-finding-2026-06-29.md`

---

## TL;DR

本文件是对前置 worklog §3 "迁移策略如何调整"三个候选方向的细化对比，**仅基于已掌握证据**整理，不需要再读新文件。用户决策后才能启动 P0 漂移修复与 Phase 1.1 第二批。

---

## 1. 已掌握证据回顾

### 后端实际响应字段

**`GET /api/akshare/market/fund-flow/hsgt-summary`** (`src/adapters/akshare/market_adapter/fund_flow.py:33-42`):

```
date              # 日期 (YYYY-MM-DD)
north_money       # 北向资金净流入
south_money       # 南向资金净流入
daily_quota       # 当日额度
daily_balance     # 当日余额
daily_used_quota  # 当日使用额度
start_date        # 查询参数透传
end_date          # 查询参数透传
query_timestamp   # pd.Timestamp.now()
```

**`GET /api/akshare/market/fund-flow/north-stock/{symbol}`** (`fund_flow.py:184-193`):

```
symbol                # 股票代码
date                  # 日期
hold_amount           # 持股数量
hold_market_value     # 持股市值
hold_change_amount    # 持股变化数量
hold_change_value     # 持股变化市值
fund_direction        # 固定 "north"
query_timestamp       # pd.Timestamp.now()
```

### 前端期望字段

**`web/frontend/src/views/data/fundFlowPageData.ts:105-111, 169`** 消费:

```
板块           # '沪股通' | '深股通'
资金方向       # '北向' | '南向'
成交净买额     # 数值
指数涨跌幅     # 数值 (百分比)
交易日         # 日期字符串
```

### 字段对照 (hsgt-summary)

| 前端期望 | 后端实际 | 语义对应 | 数据保真度 |
|---|---|---|---|
| `板块` (沪股通/深股通) | ❌ 不存在 | 后端只给"北向/南向"汇总，不区分沪深 | **后端缺信息** |
| `资金方向` (北向/南向) | `north_money` / `south_money` (列名即方向) | 后端把方向编码进列名，前端期望独立字段 | 结构差异 |
| `成交净买额` | `north_money` / `south_money` (数值) | 数值在，但需要按 `资金方向` 选择对应列 | 字段重命名 |
| `指数涨跌幅` | ❌ 不存在 | 后端完全不返回指数数据 | **后端缺信息** |
| `交易日` | `date` | 仅字段名差异 | 字段重命名 |

**关键发现**: 后端缺 `板块` (沪/深区分) 和 `指数涨跌幅` 两个字段。这**不是单纯的字段重命名问题，是后端返回的数据维度少于前端期望**。

---

## 2. 三个候选方向细化对比

### 方向 1 — 按前端期望对齐 (OpenStock → 中文字段)

**实施动作**:
- 切换层加字段翻译: `board_name→板块, fund_direction→资金方向, net_buy_amount→成交净买额, index_change_pct→指数涨跌幅, trade_date→交易日`
- OpenStock `NORTHBOUND_FLOW` 实测返回 `board_name` 含 `沪股通/深股通` 区分 ✅ (前端期望可满足)
- OpenStock `NORTHBOUND_FLOW` 实测返回 `index_change_pct` ✅ (前端期望可满足)
- 前端零改动

**优势**:
- 完成后前端 FundFlow 页面立即正常工作 (OpenStock 字段语义比当前后端更丰富)
- Phase 1.1 一次性完成"漂移修复 + 数据源迁移"
- 前端零改动符合 SOT §七 "前端零感知"

**劣势**:
- 中文字段名不符合编程惯例 (但仓库已有先例, 例如 K 线接口也是中文字段)
- 等于"以前端 mock 契约为真相源", 后端契约被改写
- 若未来再加新接口, 中文契约会成为迁移负担

**风险**: 中
- OpenStock 字段必须能 100% 满足前端期望 (实测显示可以, 但需完整验证)

**预估 LOC**: ~50 (业务切换 + 映射层 + 单测)

---

### 方向 2 — 按后端实际对齐 (OpenStock 英文直接透传, 修前端)

**实施动作**:
- 切换层 OpenStock 英文字段直接输出
- 改 `fundFlowPageData.ts:105-111, 169` 改为消费 `board_name/fund_direction/net_buy_amount/index_change_pct/trade_date`
- 同步改 mock 数据 (`mockApiClient.ts:105` 区域) 与 dashboardService 测试
- 同步改 OpenAPI 响应示例

**优势**:
- 长期最干净的契约 (英文 snake_case 是仓库主流惯例)
- 一次彻底清理 mock 与真实后端的脱节

**劣势**:
- 违反 SOT §七 "前端零感知" (Phase 1.x 不应改前端)
- 前端改动跨多文件 (FundFlow.vue, fundFlowPageData.ts, dashboardService.ts, mockApiClient.ts, 多个 .spec.ts)
- PR 范围爆炸, review 难度高
- 上下文消耗大, 不适合本会话余量

**风险**: 高
- 前端跨多文件改, 容易漏改 mock 或测试
- 改完后仍需完整浏览器验证

**预估 LOC**: ~200 (后端切换 ~30 + 前端字段消费改造 ~80 + mock 与测试同步 ~90)

---

### 方向 3 — 暂停迁移, 先单独 P0 修漂移 (推荐)

**实施动作 (分两步)**:

**步骤 A (P0 漂移修复, 独立 PR)**:
- 选定真相源 (推荐前端 mock 契约, 因为前端期望语义更完整)
- 改 `fund_flow.py` 两个 endpoint, 让响应字段对齐真相源 (中文字段名 + 沪深区分 + 指数涨跌幅)
- 同步对齐 mock 数据
- 浏览器验证 FundFlow 页面真正能消费真实后端数据
- **此步骤不切换数据源, 仍走 akshare** —— 因为 akshare `stock_hsgt_fund_flow_summary_em` 原始返回就含沪深区分与指数涨跌幅, 是当前 `fund_flow.py:33-42` 的 rename 操作丢了信息

**步骤 B (Phase 1.1 第二批, 独立 PR)**:
- 步骤 A 完成且 FundFlow 页面在真实后端正常工作后启动
- 切换 OpenStock, 因为 OpenStock 字段语义与步骤 A 的真相源一致, 切换无漂移

**优势**:
- 步骤 A 范围最小 (~30 LOC 后端 + mock 对齐), 单 PR 可控
- 步骤 A 修复后 FundFlow 页面立即可用, 用户可见价值最高
- 步骤 B 在已稳定的契约上做数据源切换, 风险最低
- 符合 SOT §三 "迁移必须自带收口条件"
- 符合 CLAUDE.md "主线优先于细节治理"

**劣势**:
- 拆两个 PR, 总耗时更长
- 步骤 A 仍依赖 akshare (但这是当前事实, 没有制造新债务)

**风险**: 低
- 每个步骤独立可验证, 半途失败不会留下半切换状态

**预估 LOC**: 步骤 A ~50, 步骤 B ~50 (与方向 1 相同)

---

## 3. 推荐方案重申

**推荐方向 3 (步骤 A + 步骤 B 分两次)**。

理由:
1. **SOT §三 红线**: "迁移必须自带收口条件" — 在漂移基础上叠加迁移, 等于在不知道真相源的情况下引入新数据源, 违反此原则
2. **CLAUDE.md 主线对齐**: FundFlow 页面字段漂移是主线阻塞, 必须先修主线, 再推迁移
3. **步骤 A 的关键发现**: akshare 原始数据本身就含沪深区分与指数涨跌幅, 当前漂移是**后端 `fund_flow.py:33-42` 的字段 rename 操作人为丢失信息**导致的, 不是数据源问题。修复步骤 A 不需要换数据源, 只需把 rename 改对
4. **风险隔离**: 步骤 A 不动数据源, 步骤 B 不动字段契约, 两步各自独立可验证

---

## 4. 步骤 A 真相源候选 (待用户确认)

如果用户选方向 3, 步骤 A 的真相源还需选定。两个候选:

### 候选 a — 前端 mock 契约 (推荐)

字段: `板块/资金方向/成交净买额/指数涨跌幅/交易日`

**理由**:
- 前端期望含沪深区分 (`板块`) 和指数涨跌幅, 信息维度更丰富
- akshare 原始数据可满足 (说明 `stock_hsgt_fund_flow_summary_em` 原始返回就是中文且含这些字段)
- 修后端只需删掉错误的 rename 操作, 改为透传原始字段
- 切换 OpenStock 时, OpenStock 字段语义与之对齐

### 候选 b — 重设计统一契约

字段: `board_name/fund_direction/net_buy_amount/index_change_pct/trade_date` (OpenStock 风格)

**理由**:
- 长期最干净
- 但需要改前端 + mock + 测试 (等同方向 2 的范围)

**推荐**: 候选 a (前端 mock 契约), 与方向 3 的范围一致。

---

## 5. 决策后的下一步动作清单

用户选定方向后:

### 如果选方向 3 + 候选 a (强推荐)

下次会话:
1. 启动 backend+frontend, 关闭 mock, 复现 FundFlow 页面当前 broken 状态, 截图存证
2. 修 `fund_flow.py:33-42` 删除错误的字段 rename, 让响应字段对齐前端 mock 契约 (含沪深区分与指数涨跌幅)
3. 同步检查 `mockApiClient.ts:105` 区域, 确认 mock 与新契约一致
4. 浏览器验证 FundFlow 页面在真实后端正常工作
5. 提交 P0 漂移修复 PR
6. P0 PR 合入后启动 Phase 1.1 第二批 (OpenStock 切换)

### 如果选方向 1

下次会话:
1. 启动 OpenStock + backend+frontend, 复现页面状态
2. 修 `fund_flow.py` 切换 hsgt-summary 与 north-stock 至 OpenStock, 加英文→中文字段翻译
3. 6 个未迁移 endpoint 加 TODO 注释
4. 写 API e2e 测试 + 浏览器验证
5. 提交 Phase 1.1 完整 PR

### 如果选方向 2

下次会话:
1. 启动 backend+frontend, 复现页面状态
2. 修 `fund_flow.py` 切换 OpenStock 英文字段直接透传
3. 改前端 5+ 文件 (`fundFlowPageData.ts`, `FundFlow.vue`, `dashboardService.ts`, `mockApiClient.ts`, 多个 .spec.ts)
4. 浏览器验证
5. 提交跨前后端大 PR

---

## 修订历史

- **2026-06-29 V1.0（初始）**: 决策矩阵首版, 重申方向 3 + 候选 a 推荐, 列出三方向的细化对比与下一步动作清单.
