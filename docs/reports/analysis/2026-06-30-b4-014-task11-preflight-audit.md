# B4.014 Task #11 OpenSpec 提案 — 修正版预检审计

**日期**: 2026-06-30
**作者**: Claude (session 5bacdfb1)
**状态**: v3 — Wave 1 已完成 + 中台缺口实测修正（6→3 硬需求 + 3 设计决策）
**关联提案**: `openspec/changes/migrate-akshare-fundflow-mixin-to-openstock/` (PR #488)
**关联分支**: `feat/b4-014-fundflow-mixin-openspec-proposal` (HEAD `2e12e593d`)
**前序文档**:
- `docs/reports/analysis/2026-06-30-b4-014-branch-b-strategy-realignment.md` (v2)
- `docs/reports/analysis/2026-06-30-b4-014-branch-b-strategy-realignment-REVIEW.md` (CodeWhale 审核)

---

## 0. 审计修正声明（重要）

### 0.1 撤回：BLOCK_TRADE 缺失白名单的判断

**先前错误声明**: "BLOCK_TRADE 未在 `DEFAULT_SUPPORTED_CATEGORIES` 中，是隐藏的运行时异常风险，建议 P0 立即修复。"

**实证复核**（`web/backend/app/services/openstock_client.py:10-21`）:

```python
DEFAULT_SUPPORTED_CATEGORIES = (
    "REALTIME_QUOTES",
    "KLINES",
    "FUND_FLOW",
    "SECTOR_FUND_FLOW",
    "DRAGON_TIGER",
    "BLOCK_TRADE",         # ← 第 6 项，存在
    "ETF_SPOT",
    # Phase 1.1 fund-flow domain (B4.014):
    "NORTHBOUND_FLOW",
    "NORTHBOUND_HOLDING",
)
```

`BLOCK_TRADE` 在白名单第 6 项，**无运行时阻断 bug**，**无需 P0 修复**。

### 0.2 误判根因

先前用 `grep` 检索白名单时只匹配了部分关键字且未回看上下文，把"未在 first-5 命中"误判为"不存在"。本次审计所有事实点均通过 `Read` + `grep` 双重核对，并对每个声明附行号。

### 0.3 影响范围

- **撤回**: 用户基于先前审计给出的 P0 优先级（"补充 BLOCK_TRADE 至 DEFAULT_SUPPORTED_CATEGORIES"）
- **保留**: 其他审计发现（架构分歧、akshare 残留、缺失中台类别、注入规范技术债）经复核均成立
- **改进**: 本文档把所有可量化清单（调用点、文件、行号、类别对照）以可验证表格呈现，作为 PR #488 评审与中台需求同步的事实底稿

### 0.4 v3 修正（2026-06-30 实测，会话 5bacdfb1）

**触发**: Wave 1 完工后，对活中台 `http://192.168.123.104:8040` 70 个已注册类别做 POST `/data/fetch` 实测，发现 §2.3 与 §5 P2 的"6 个类别全阻塞"前提部分错误。

**修正项**:
1. `BLOCK_TRADE` 不能映射 `get_stock_fund_flow_big_deal` — 业务语义不同（大宗交易 vs 盘口大单）。正确候选是 `DRAGON_TIGER`，但同样存在语义差异（龙虎榜 vs 大单成交），归入"设计决策"而非"可直接启动"。
2. §5 P2 的 6 项缺失修正为：3 项真正缺失（P2.A）+ 3 项有候选但语义不同（P2.B）。
3. `HSGT_HOLDINGS` / `MARKET_SENTIMENT` 撤出 P2（`get_stock_cyq_em` 不在本提案范围）。

**保留**: §1（OpenStockClient 调用链路）、§3（akshare 残留台账）、§4（架构 D1/D2/D3 决策记录）、§6（参考文件清单）均不变。

---

## 1. OpenStockClient 全调用链路 & 注入规范审计

### 1.1 生产调用点清单（3 处文件，均位于 `web/backend/`）

| # | 文件 | 行号 | 调用形态 | 层级 | 业务域 |
|---|------|-----|---------|------|--------|
| P1 | `web/backend/app/services/market_data_service_v2.py` | L67, L77-80 | `_build_openstock_client()` 工厂 + `OpenStockClient(OpenStockClientConfig(...))` | 服务层（V2） | SECTOR_FUND_FLOW / FUND_FLOW / ETF_SPOT / DRAGON_TIGER / BLOCK_TRADE |
| P2 | `web/backend/app/api/akshare_market/fund_flow.py` | L21, L37-38 | `_build_openstock_client()` 工厂 + `OpenStockClient(OpenStockClientConfig(...))` | 路由层（fund_flow 端点） | NORTHBOUND_FLOW / NORTHBOUND_HOLDING |
| P3 | `web/backend/app/api/market/market_data_request.py` | L49, L60-61 | `get_openstock_market_client() -> OpenStockClient`（FastAPI Depends 工厂） | 路由层（market_data 端点） | 通用消费客户端 |

**关键发现**:
- **`src/` 目录无任何 OpenStockClient 调用点**（grep `OpenStockClient\|openstock_client` 在 `src/` 零命中）
- 这与提案要求（"FundFlowMixin 持有 OpenStockClient，所有 fund-flow 数据经 Mixin 翻译"）**根本性偏离**
- 当前所有消费流量走的是 **服务层 + 路由层**，Mixin 层仍是纯 akshare 实现（见 §4）

### 1.2 三种注入形态并存（技术债）

| 形态 | 位置 | 说明 | 一致性 |
|------|------|------|--------|
| (a) 服务层内置工厂 | `market_data_service_v2.py:49` `self._openstock_client_factory: Callable[[], OpenStockClient] = self._build_openstock_client` | 服务类自己持有工厂与实例 | 服务层方案 |
| (b) 路由层独立工厂 | `fund_flow.py:21` `def _build_openstock_client() -> OpenStockClient` | 路由文件本地函数，每个端点自行 build | 路由层方案 |
| (c) 路由层 Depends 工厂 | `market_data_request.py:49` `def get_openstock_market_client() -> OpenStockClient` | 标准 FastAPI 依赖注入 | 标准 DI 方案 |

**问题**: 同一仓库三种客户端构造形态并存，没有统一规范。
- (a) 与 OpenSpec 提案 §specs 的 "AkshareMarketAdapter 构造函数接受 `openstock_client: OpenStockClient \| None`" 不一致（提案要求在 adapter 层注入，不是在 service 层）
- (b) 在端点函数中直接 `client = _build_openstock_client()`，绕过服务层抽象，无生命周期管理
- (c) 是三者中最规范的，但仅服务于 `market_data_request.py` 一个文件

### 1.3 测试调用点清单（4 文件，全部使用构造函数直接注入）

| 文件 | 用途 |
|------|------|
| `tests/backend/test_openstock_client.py` | 客户端本身的单元测试（7 处构造） |
| `tests/services/openstock_client/test_northbound_flow_parsing.py` | NORTHBOUND_FLOW 解析测试 |
| `tests/services/openstock_client/test_northbound_holding_parsing.py` | NORTHBOUND_HOLDING 解析测试 |
| 其他 e2e 测试 | 通过 `_FakeOpenStockClient` stub 注入 |

测试侧的注入规范相对统一（构造函数 + Config 对象），但生产代码与之不一致。

---

## 2. 支持类别核对（修正版）

### 2.1 客户端白名单完整列表（9 项，已实证）

| # | 类别 | 来源注释 |
|---|------|---------|
| 1 | `REALTIME_QUOTES` | 基础类别 |
| 2 | `KLINES` | 基础类别 |
| 3 | `FUND_FLOW` | 基础类别 |
| 4 | `SECTOR_FUND_FLOW` | 基础类别 |
| 5 | `DRAGON_TIGER` | 基础类别 |
| 6 | `BLOCK_TRADE` | 基础类别（先前误判已撤回） |
| 7 | `ETF_SPOT` | 基础类别 |
| 8 | `NORTHBOUND_FLOW` | Phase 1.1 fund-flow domain (B4.014) |
| 9 | `NORTHBOUND_HOLDING` | Phase 1.1 fund-flow domain (B4.014) |

### 2.2 业务实际消费类别（5 项，已实证 grep）

| 类别 | 消费点 | 文件:行号 |
|------|-------|----------|
| `REALTIME_QUOTES` | `market_data_request.py` Depends 路径直调 `client.fetch` | `market_data_request.py:555` |
| `SECTOR_FUND_FLOW` | `market_data_service_v2._fetch_openstock_records` × 2 | `market_data_service_v2.py:160, 618` |
| `FUND_FLOW` | `market_data_service_v2._fetch_openstock_records` | `market_data_service_v2.py:322` |
| `ETF_SPOT` | `market_data_service_v2._fetch_openstock_records` | `market_data_service_v2.py:401` |
| `DRAGON_TIGER` | `market_data_service_v2._fetch_openstock_records` | `market_data_service_v2.py:513` |
| `BLOCK_TRADE` | `market_data_service_v2._fetch_openstock_records` | `market_data_service_v2.py:884` |
| `NORTHBOUND_FLOW` | `fund_flow.py` 端点直调 | `fund_flow.py:370` |
| `NORTHBOUND_HOLDING` | `fund_flow.py` 端点直调 | `fund_flow.py:545` |

**实际消费 8 个类别**（白名单 9 项中，仅 `KLINES` 当前没有 grep 命中的消费点；该类别可能通过其他路径使用或为预留能力，需在 Wave 1 启动前由中台或前端确认是否仍需保留）。

> 修正记录（v1 → v2）: 原文错误声称 `REALTIME_QUOTES` 与 `KLINES` 均无 grep 命中消费点。经复核 `market_data_request.py:555` 有明确的 `await client.fetch("REALTIME_QUOTES", params={"symbols": symbol_list})` 调用，原文系 grep 正则过窄（未匹配 `client.fetch("..."` 这类字符串字面量调用形态）导致漏检索。仅 `KLINES` 的"无消费点"声明成立。

### 2.3 OpenSpec 提案所需类别 vs 中台现状缺口台账

提案 `tasks.md` 与 `proposal.md` 共声明 8 个 FundFlowMixin 方法需迁移到 OpenStock：

| Mixin 方法（fund_flow.py） | 行号 | 提案映射类别 | 中台支持 | 状态 |
|---------------------------|-----|-------------|---------|------|
| `get_stock_hsgt_fund_flow_summary_em` | L23 | `NORTHBOUND_FLOW` | ✅ 白名单 + Wave 1 已迁移 (commit `614290989`) | **Wave 1 完成** |
| `get_stock_hsgt_north_acc_flow_in_em` | L93 | `NORTHBOUND_HOLDING` | ✅ 白名单 + Wave 1 已迁移 (commit `614290989`) | **Wave 1 完成** |
| `get_stock_hsgt_fund_flow_detail_em` | L115 | `NORTHBOUND_FLOW_DETAIL` (原计划) | ⚠️ `FUND_FLOW` 存在但语义不同（个股 vs 大盘） | Wave 2 — 设计决策 |
| `get_stock_hsgt_north_net_flow_in_em` | L153 | `NORTHBOUND_DAILY_HISTORY` (原计划) | ❌ 真正缺失 | Wave 2 — 阻塞 |
| `get_stock_hsgt_south_net_flow_in_em` | L190 | `SOUTHBOUND_DAILY_HISTORY` (原计划) | ❌ 真正缺失 | Wave 2 — 阻塞 |
| `get_stock_hsgt_south_acc_flow_in_em` | L227 | `SOUTHBOUND_HOLDING` (原计划) | ❌ 真正缺失 | Wave 2 — 阻塞 |
| `get_stock_hsgt_hold_stock_em` | L265 | `HSGT_INDIVIDUAL_HOLDING` (原计划) | ⚠️ `INSTITUTION_HOLDING` 存在但语义不同（机构 vs 参与者） | Wave 3 — 设计决策 |
| `get_stock_fund_flow_big_deal` | L305 | `MARKET_BIG_DEAL_RANK` (原计划) | ⚠️ `DRAGON_TIGER` 存在但语义不同（龙虎榜 vs 大单成交） | Wave 3 — 设计决策 |

> **注**: `get_stock_cyq_em` (筹码分布) 不在本提案范围内（独立 Mixin 域）。

**修正记录（v2 → v3, 2026-06-30 实测）**: 原表 v2 声明 `get_stock_fund_flow_big_deal` → `BLOCK_TRADE` 已就绪、Wave 3 可启动 — 这是错的。`BLOCK_TRADE` 是大宗交易（机构间场外），与 `stock_fund_flow_big_deal`（盘口大单成交）业务语义不同，**不能直接替代**。正确映射候选是 `DRAGON_TIGER`（龙虎榜），但同样存在语义差异，需要设计决策。

**统计（v3 实测修正后）**:
- ✅ Wave 1 完成: **2 个方法**（已合并 commit `614290989`，PR #488 等待评审）
- ❌ Wave 2 真正阻塞: **3 个方法**（4.6/4.7/4.8 — 需 OpenStock 中台扩展 3 个新类别）
- ⚠️ Wave 2/3 设计决策: **3 个方法**（4.5/5.3/5.4 — 中台有候选类别但语义不同，需对齐前端契约）
- 修正前 (v2) 错误声称的 BLOCK_TRADE 已就绪、6 个全阻塞均不成立

**结论**: 提案 Wave 1（2 方法）已完成；Wave 2（4 方法）= 3 个硬阻塞 + 1 个设计决策；Wave 3（2 方法）= 2 个设计决策；`import akshare` 移除仍需 Wave 2/3 全部完工。

---

## 3. 全仓库 Akshare 硬依赖残留台账（按 Mixin 业务域分组）

**实证**: `grep -rn "^import akshare\|^from akshare" src/ web/backend/app/ --include="*.py"` 命中 **25 个文件**（先前估计 28+，本次精确化为 25）。

### 3.1 `src/adapters/akshare/market_adapter/` — 6 个 Mixin 类（提案核心范围）

| 文件 | 行号 | 业务域 | 提案归属 |
|------|-----|--------|---------|
| `board_sector.py` | L7 | 板块/行业 | **Task #11 后续 Wave** |
| `fund_flow.py` | L7 | 资金流（8 方法） | **Task #11 当前 Wave 1/2/3 范围** |
| `forecast_analysis.py` | L7 | 预测分析 | 后续迁移 |
| `market_overview.py` | L7 | 市场总览 | 后续迁移 |
| `stock_sentiment.py` | L7 | 个股情绪 | 后续迁移 |
| `stock_profile.py` | L9 | 个股画像 | 后续迁移 |
| `adapter.py` | — | Mixin 聚合类 | 与上述同步 |

### 3.2 `src/adapters/akshare/` — 顶层业务模块（11 个文件）

| 文件 | 行号 | 业务域 |
|------|-----|--------|
| `market_data.py` | L10 | 市场数据 |
| `stock_info.py` | L11 | 股票基本信息 |
| `realtime_data.py` | L4 | 实时行情 |
| `index_daily.py` | L3 | 指数日线 |
| `industry_data.py` | L3 | 行业数据 |
| `fund_flow.py` | L9 | 资金流（与 market_adapter 同名但不同层） |
| `stock_basic.py` | L4 | 股票基础信息 |
| `market_overview.py` | L11 | 市场总览（同名） |
| `stock_daily.py` | L4 | 股票日线 |
| `financial_data.py` | L10 | 财务数据 |
| `legacy_market_data.py` | L15 | 遗留市场数据 |

### 3.3 `src/adapters/akshare/misc_data/` 与 `modules/` — 子目录

| 文件 | 行号 | 业务域 |
|------|-----|--------|
| `misc_data/get_ths_industry_names.py` | L3 | 同花顺行业名 |
| `misc_data/get_futures_index_daily.py` | L3 | 期货指数日线 |
| `modules/stock_info.py` | L8 | 股票信息（模块版） |
| `modules/fund_flow.py` | L8 | 资金流（模块版） |
| `modules/market_overview/market_overview.py` | L8 | 市场总览（嵌套模块） |

### 3.4 `src/adapters/` 顶层与其他 — 3 个文件

| 文件 | 行号 | 用途 |
|------|-----|------|
| `src/adapters/akshare_proxy_adapter.py` | L27 | akshare 代理适配器 |
| `src/adapters/akshare_adapter.py` | L30 | akshare 主适配器 |
| `src/adapters/financial/index_daily.py` | L5 | 财务指数日线 |

### 3.5 残留台账总结

- **总计 25 个生产文件**包含 `import akshare` 顶层导入
- **Task #11 Wave 1/2/3 直接覆盖**: 仅 `market_adapter/fund_flow.py`（1 个文件，8 方法）
- **Task #11 后续 Wave 覆盖**: 其余 5 个 `market_adapter/*.py` Mixin 文件
- **Task #11 范围外**: `src/adapters/akshare/` 顶层 11 + 子目录 5 + 顶层 3 = 19 个文件
- **结论**: 即使 Task #11 完整落地，仓库仍有 24/25 个 akshare 残留文件（约 96%）

---

## 4. 核心架构分歧：服务层（现状） vs Mixin 层（提案标准）

### 4.1 现状（服务层方案）

```
路由层 (fund_flow.py)
   ↓ _build_openstock_client() + 路由层直调 OpenStockClient
   ↓ 或 ↓
服务层 (market_data_service_v2.py)
   ↓ _fetch_openstock_records(data_category, params)
   ↓
OpenStockClient (openstock_client.py)
   ↓ HTTP /data/fetch
OpenStock 中台
```

**特征**:
- 翻译逻辑（OpenStock 规范字段 → akshare-era 字段名）位于 `market_data_service_v2.py` 内部
- `AkshareMarketAdapter` 的 `FundFlowMixin` 仍 `import akshare as ak`，未被使用方消费
- 路由层有 6 处直接调用 Mixin 方法（`fund_flow.py:419, 457, 496, 599, 642, 683`），但这些方法的内部实现是 akshare 直连

### 4.2 提案标准（Mixin 层方案）

```
路由层 (fund_flow.py)
   ↓ Depends(get_market_data_service)
服务层 (market_data_service_v2.py)
   ↓ adapter.get_stock_hsgt_fund_flow_summary_em(...)
Mixin 层 (market_adapter/fund_flow.py)
   ↓ self._openstock_client.fetch(...)
   ↓ 翻译：OpenStock 规范字段 → akshare-era 字段
OpenStockClient
OpenStock 中台
```

**特征**:
- `AkshareMarketAdapter.__init__` 接受 `openstock_client: OpenStockClient | None`
- `FundFlowMixin` 所有方法使用 `self._openstock_client` 而非 `import akshare`
- 服务层与路由层**不再直接 new OpenStockClient**，仅通过 adapter 接口消费
- `aclose()` 协议管理客户端生命周期（默认构造的关闭，注入的不关闭）

### 4.3 三维对比

| 维度 | 服务层方案（现状） | Mixin 层方案（提案） |
|------|-----------------|--------------------|
| **改造成本** | 低（仅服务层一处） | 高（adapter 构造函数 + 9 方法翻译 + 服务层调用方迁移 + 路由层 Depends 重构） |
| **短期上线速度** | 快（已有 5 业务函数在服务层跑） | 慢（Wave 1 需重写 2 方法 + 调整构造链 + 改路由） |
| **长期对齐 C1（数据源统一）** | ⚠️ 部分（OpenStock 是消费源，但 Mixin 仍可走 akshare 后门） | ✅ 完全（akshare 在 Mixin 中禁用，强制单一来源） |
| **能否清理 akshare 依赖** | ❌ 不能（Mixin 仍 `import akshare`，路由层 6 处调用仍走 akshare） | ✅ 能（Wave 3 落地后，`fund_flow.py` 顶层 `import akshare` 可移除，触发 `forbidden_imports.py` 门禁） |
| **测试可注入性** | 中（服务层工厂可替换） | 高（adapter 构造函数接受 `openstock_client` 参数，单元测试可注入 stub） |
| **未来扩展（其他 Mixin 迁移）** | 每个域都要在服务层重复翻译逻辑 | 翻译逻辑封装在 Mixin 内，新域只需迁移 Mixin，服务层零改动 |

### 4.4 关键决策点

**问题**: 提案 §design.md 与 §specs/spec.md 明确要求 Mixin 层方案，但当前 B4.014 工作副本已经把 5 个业务函数落地在服务层方案上。

**三种处置路径**（需用户决策）:

| 路径 | 动作 | 风险 | 收益 |
|------|------|------|------|
| **D1 完全回归提案** | 把服务层 5 个业务函数迁移回 Mixin，删 `_fetch_openstock_records` | 高（已合入 d6209dc0a 的工作需部分回退） | 长期架构干净，提案 spec 不变 |
| **D2 修订提案承认现状** | 把提案 §design.md 改为"服务层方案"，删除 adapter 注入相关 spec 条目 | 中（PR #488 需重写，spec 与现状对齐） | 短期节省工作量，长期偏离 C1 |
| **D3 混合方案** | Wave 1 按提案 Mixin 方案，服务层方案保留作为已落地的"快速通道" | 高（两套方案并存，更脏） | 不推荐 |

**审计员建议（仅供参考，不替代决策）**: D1。理由：
1. 服务层方案违反提案的核心架构原则（Mixin 持有客户端）
2. 服务层方案的"5 个业务函数"中，4 个映射的 Mixin 方法仍在 akshare 路径上，未真正实现 C1 统一
3. 提案已通过 `openspec validate --strict`，spec 是 SOT，现状应回归 spec 而非反之

---

## 5. 后续分阶段处置清单

### P1 — 架构评审议题（PR #488 评审期间决策）

| # | 议题 | 决策方 | 阻塞 |
|---|------|-------|------|
| P1.1 | 服务层方案 vs Mixin 层方案（§4.4 D1/D2/D3） | 用户 | Wave 1 启动前必须决策 |
| P1.2 | `KLINES` 在白名单但当前无 grep 命中消费点，是否仍需保留（`REALTIME_QUOTES` 已确认在 `market_data_request.py:555` 消费，不属此项） | 用户 + 中台 | 不阻塞 Wave 1 |
| P1.3 | 路由层 `_build_openstock_client()` (fund_flow.py) 是否合并为全局 Depends 工厂 | 用户 | 不阻塞 Wave 1 |

### P2 — OpenStock 中台需求同步（Wave 2/3 解阻塞前提）

**v3 修正（2026-06-30 实测后）**: 原清单 6 项中，3 项有等价中台类别，仅 3 项真正缺失。

#### P2.A — 真正缺失，需中台新增（3 项，硬阻塞 Wave 2）

| # | 缺失类别 | 对应 Mixin 方法 | 业务语义 | 实测验证 |
|---|---------|----------------|---------|---------|
| P2.A.1 | `NORTHBOUND_DAILY_HISTORY` | `get_stock_hsgt_north_net_flow_in_em` (4.6) | 北向资金每日净流入时间序列 | `POST /data/fetch` 70 类别中无匹配 |
| P2.A.2 | `SOUTHBOUND_DAILY_HISTORY` | `get_stock_hsgt_south_net_flow_in_em` (4.7) | 南向资金每日净流入时间序列 | 同上 |
| P2.A.3 | `SOUTHBOUND_HOLDING` | `get_stock_hsgt_south_acc_flow_in_em` (4.8) | 南向资金持股明细（按 symbol） | 同上（`INSTITUTION_HOLDING` 语义不符） |

#### P2.B — 有候选类别但语义不同，需设计决策（3 项）

| # | akshare 方法 | 中台候选 | 语义差异 | 决策路径 |
|---|-------------|---------|---------|---------|
| P2.B.1 | `get_stock_hsgt_fund_flow_detail_em` (4.5) | `FUND_FLOW`（个股，120 行 @600519） | FUND_FLOW 是个股主力/超大单/大单/中单/小单净流入；原方法是沪深港通大盘明细 | (a) 重谈前端契约 (b) 中台新增 `NORTHBOUND_FLOW_DETAIL` |
| P2.B.2 | `get_stock_hsgt_hold_stock_em` (5.3) | `INSTITUTION_HOLDING`（2115 行 @600519） | INSTITUTION_HOLDING 是机构持仓（fund/holder_count）；原方法是沪深港通参与者持股（participant_name/market_type） | (a) 重谈前端契约 (b) 中台新增 `HSGT_INDIVIDUAL_HOLDING` |
| P2.B.3 | `get_stock_fund_flow_big_deal` (5.4) | `DRAGON_TIGER`（2115 行 @2026-06） | DRAGON_TIGER 是龙虎榜（top trader 排名）；原方法是盘口大单成交 | (a) 重谈前端契约 (b) 中台新增 `MARKET_BIG_DEAL_RANK` |

**修正撤回**: v2 清单中的 `HSGT_HOLDINGS`（P2.5）与 `MARKET_SENTIMENT`（P2.6，对应 `get_stock_cyq_em`）不在本提案范围内，从 P2 移除。`get_stock_cyq_em`（筹码分布）属于独立 Mixin 域。

**推荐处置（默认）**: P2.B 全部走路径 (b) — 中台新增类别匹配 akshare-era 语义。理由：
1. 前端契约是真相源，不应为迁移而变更
2. 已确认中台有新增类别的能力（70 个已上线）
3. (a) 路径会引入前端工作 + 风险扩散

**动作**: 把 P2.A 的 3 项硬需求 + P2.B 的 3 项设计决策同步给 OpenStock 中台维护方。

### P3 — 注入规范重构（架构一致性）

| # | 重构项 | 优先级 |
|---|-------|-------|
| P3.1 | 统一三种 OpenStockClient 构造形态（服务层工厂 / 路由层工厂 / 路由层 Depends）为单一 Depends 工厂 | 中 |
| P3.2 | 删除 `fund_flow.py:21` 的 `_build_openstock_client()`，改为 `Depends(get_openstock_market_client)` | 中 |
| P3.3 | `market_data_service_v2.py` 的 `self._openstock_client_factory` 与 adapter 注入方案对齐（若 D1 选定） | 高（D1 选定时）/ 不适用（D2 选定时） |

### P4 — Wave 1 启动前置（提案合并后）

| # | 任务 | 来源 |
|---|------|------|
| P4.1 | 重新统计 Mixin 方法调用点（main 与 B4.014 分支可能不同） | `tasks.md §1 pre-flight audit` |
| P4.2 | 确认 OpenStock 中台 `NORTHBOUND_FLOW` / `NORTHBOUND_HOLDING` 数据可用性 | Phase 1.1 已验证 |
| P4.3 | 准备单元测试桩（`_FakeOpenStockClient`） | 现有 e2e 测试已有 |
| P4.4 | Wave 1 实施 7 个子任务（tasks.md §3.1-3.8） | 提案 |

---

## 6. 参考文件清单（已验证存在）

### 6.1 本审计依赖的实证来源
- `web/backend/app/services/openstock_client.py` — 客户端实现（315 行）
- `web/backend/app/services/market_data_service_v2.py` — 服务层消费实现
- `web/backend/app/api/akshare_market/fund_flow.py` — 路由层消费实现
- `web/backend/app/api/market/market_data_request.py` — Depends 工厂
- `src/adapters/akshare/market_adapter/fund_flow.py` — FundFlowMixin 源（akshare 直连）

### 6.2 提案与上游文档
- `openspec/changes/migrate-akshare-fundflow-mixin-to-openstock/proposal.md`
- `openspec/changes/migrate-akshare-fundflow-mixin-to-openstock/tasks.md`
- `openspec/changes/migrate-akshare-fundflow-mixin-to-openstock/design.md`
- `openspec/changes/migrate-akshare-fundflow-mixin-to-openstock/specs/data-source-runtime-service/spec.md`

### 6.3 前序分析
- `docs/reports/analysis/2026-06-30-b4-014-branch-b-strategy-realignment.md` (v2)
- `docs/reports/analysis/2026-06-30-b4-014-branch-b-strategy-realignment-REVIEW.md`
- `.planning/HANDOFF.json`
- `.planning/.continue-here.md`

### 6.4 工作日志
- `docs/reports/worklogs/claude-auto/b4-014-phase1-1-batch2-fundflow-openstock-switch-2026-06-29.md`
- `docs/reports/worklogs/claude-auto/b4-014-p0-fundflow-drift-fix-verification-2026-06-29.md`

---

## 7. 审计结论

| 维度 | 状态 |
|------|------|
| 提案 Wave 1 执行性 | ✅ **已完成**（commit `614290989`，2 方法已迁移，PR #488 评审中） |
| 提案 Wave 2 执行性 | ⚠️ **3 方法硬阻塞 + 1 方法待设计决策**（v3 修正：原 v2 声明"4 方法全阻塞"是错的） |
| 提案 Wave 3 执行性 | ⚠️ **2 方法待设计决策**（v3 修正：原 v2 声明"BLOCK_TRADE 可启动"是错的，BLOCK_TRADE 语义不符） |
| 架构方向（提案 vs 现状） | ✅ **D1 已选定**（Mixin 层方案，Wave 0 抬升已落地） |
| 注入规范一致性 | ❌ 三种形态并存，技术债（P3 待处理） |
| 仓库 akshare 残留 | 25 文件，Task #11 覆盖 1/25（fund_flow Mixin）；Wave 1 后已减 2 个 ak.* 调用点 |
| 提案 spec 准确性 | ✅ `openspec validate --strict` 通过，spec 是 SOT |
| PR #488 合并阻塞 | 仅人工 review，无技术阻塞 |

**下一步建议**:
1. PR #488 评审期间，把 v3 实测修正告知 reviewer（中台缺口从 6 项修正为 3 项硬需求 + 3 项设计决策）
2. 把 §5 P2.A 的 3 项硬需求 + P2.B 的 3 项设计决策同步给 OpenStock 中台维护方
3. PR #488 合并后，新提案推进 Wave 2/3（避免单 PR 承载过多变更）
4. wip/root-dirty-20260403 治理与 OpenStock 议题解耦，独立会话处理

---

**审核请求**: 本修正版审计已撤回 BLOCK_TRADE 误判，所有事实点附行号可验证。请审阅是否接受，或是否需要补充其他维度。本文件可直接用于 PR #488 评审参考、中台需求同步、分域迁移排期。
