# B4.014 Phase 1.1 — 第一批交付（白名单 + 单元解析测试 + Playbook 框架）

**Date**: 2026-06-29
**Author**: Claude (auto worklog)
**Status**: 第一批完成 — 白名单准入闭环已就绪；未触碰 `fund_flow.py`，无运行时风险
**Predecessor**:
- `b4-014-phase0-openstock-sot-2026-06-29.md`（SOT V1.0 发布）
- `b4-014-task11-akshare-adapter-migration-scoping-2026-06-29.md`（Task #11 活体盘点）

---

## TL;DR

Phase 1.1 FundFlow 域迁移按用户授权拆分为两个独立可提交批次。**本会话完成第一批**，包括：

1. `DEFAULT_SUPPORTED_CATEGORIES` 扩展 `NORTHBOUND_FLOW` + `NORTHBOUND_HOLDING`，含端点映射行内注释（3 LOC）
2. 单元解析测试 ×2，共 17 个测试用例，全部通过（536 LOC）
3. `DOMAIN_MIGRATION_PLAYBOOK.md` V1.0 框架，含 FundFlow 域未迁移接口清单（197 LOC）
4. 本 worklog

**总 diff**: ~736 LOC（含测试桩 JSON 字面量）。**零业务代码改动**，运行时风险为零。

**第二批**（`fund_flow.py` 切换 + API e2e + CI lint + 浏览器 e2e + 完成 worklog）由下次会话执行，启动入口见 §四。

---

## 1. 为什么拆两批

最初计划 Phase 1.1 一次性交付（8 工作项 ~1300 LOC）。会话推进到白名单扩展 + live OpenStock 字段探测后，识别出两个边界：

1. **SOT §五.2 准入闭环不可拆**：白名单 + 单元测试 + 业务切换必须同 PR，但白名单 + 单元测试 + 业务切换是不同风险等级的动作（白名单=声明能力、业务切换=改运行时行为）。把它拆成"先声明能力、后改行为"两个 PR，可以让 review 难度与回滚成本最低。

2. **上下文预算约束**：截至本会话点，上下文已使用约 70%，剩余 6 工作项（fund_flow.py 切换 + API e2e + Playbook + CI lint + 浏览器 e2e + worklog）若一次性推进极易中途耗尽，留下"半切换"的中间状态——前端在同一个 PR 内会看到行为不一致。

用户授权采用"第一批"策略（参考会话内 AskUserQuestion 选项 a）。本 worklog 即该批次的完成记录。

---

## 2. 第一批交付详表

### 2.1 白名单扩展（3 LOC，已暂存）

文件: `web/backend/app/services/openstock_client.py:10-21`

```python
DEFAULT_SUPPORTED_CATEGORIES = (
    "REALTIME_QUOTES",
    "KLINES",
    "FUND_FLOW",
    "SECTOR_FUND_FLOW",
    "DRAGON_TIGER",
    "BLOCK_TRADE",
    "ETF_SPOT",
    # Phase 1.1 fund-flow domain (B4.014):
    "NORTHBOUND_FLOW",     # /api/akshare/market/fund-flow/hsgt-summary
    "NORTHBOUND_HOLDING",  # /api/akshare/market/fund-flow/north-stock/{symbol}
)
```

- 行内注释明确每个类别对应的 endpoint 路径
- `_validate_category()` 在客户端层做第一次拦截（不在白名单 → `OpenStockUnsupportedCategory`），无需新增代码
- 服务端 422 + `Unsupported data_category` 由 `_raise_for_error()` 做第二次拦截，双层防护

### 2.2 单元解析测试 ×2（17 用例，全部通过）

**`tests/services/openstock_client/test_northbound_flow_parsing.py`**（255 LOC，8 个测试）

覆盖场景:
- `test_northbound_flow_normal_payload_preserves_all_normalized_fields` — 正常 payload 全字段保留
- `test_northbound_flow_empty_data_list_is_valid` — 空 data 列表合法
- `test_northbound_flow_partial_missing_optional_fields_tolerated` — 可选字段缺失容忍
- `test_northbound_flow_null_optional_fields_preserved_as_none` — 可选字段 null 保留
- `test_northbound_flow_integer_fields_coerced_to_float_via_optional_float` — int 字段透传
- `test_northbound_flow_missing_data_key_raises_invalid_response` — 缺 data 键报错
- `test_northbound_flow_metadata_latency_and_staleness_parsed_as_float` — latency/staleness 解析

**`tests/services/openstock_client/test_northbound_holding_parsing.py`**（281 LOC，9 个测试）

覆盖场景:
- `test_northbound_holding_normal_payload_preserves_all_fields` — 正常 payload 全字段保留
- `test_northbound_holding_null_optional_fields_preserved_as_none` — `add_shares`/`add_amount`/`holding_market_cap_change` null 保留（live probe 确认这些字段频繁为 null）
- `test_northbound_holding_empty_data_list_is_valid` — 空 data 列表合法
- `test_northbound_holding_accepts_normalized_symbol_prefixes` — `sh600519`/`sz000001`/`sh601318`/`sz300750` 前缀参数化测试
- `test_northbound_holding_partial_fields_tolerated` — 部分字段缺失容忍
- `test_northbound_holding_missing_data_key_raises_invalid_response` — 缺 data 键报错
- `test_northbound_holding_metadata_route_and_latency_parsed` — route_decision_id/latency/staleness 解析

**测试目录路径遵循 SOT §五.2 强制要求**:
- 旧目录: `tests/backend/test_openstock_client.py`（基线测试，未触动）
- 新目录: `tests/services/openstock_client/`（含 `__init__.py` + 两个测试文件），符合 SOT 路径规范

**执行结果**:
```
$ python -m pytest tests/services/openstock_client/ -v
17 passed
```

### 2.3 Playbook 框架（197 LOC）

文件: `docs/guides/openstock-migration/DOMAIN_MIGRATION_PLAYBOOK.md` V1.0

包含章节:
- §零 问题背景
- §一 单域迁移标准步骤（7 步）
- §二 迁移自检核对清单（11 项 checkbox）
- §三 **未迁移接口 & 中台能力需求清单**（含 FundFlow 域 6 条登记）
- §四 浏览器端到端验证清单
- §五 PR 拆分阈值
- §六 本手册未覆盖的事项

**§三 FundFlow 域清单**（关键产出）:

| 端点路径 | 缺失 OpenStock 类别 | 优先级 |
|---|---|---|
| `/api/akshare/market/fund-flow/hsgt-detail` | `NORTHBOUND_FLOW_DETAIL` | P2 |
| `/api/akshare/market/fund-flow/north-daily` | `NORTHBOUND_DAILY_HISTORY` | P2 |
| `/api/akshare/market/fund-flow/south-daily` | `SOUTHBOUND_DAILY_HISTORY` | P2 |
| `/api/akshare/market/fund-flow/south-stock/{symbol}` | `SOUTHBOUND_HOLDING` | P2 |
| `/api/akshare/market/fund-flow/hsgt-holdings/{symbol}` | `HSGT_INDIVIDUAL_HOLDING` | P3 |
| `/api/akshare/market/fund-flow/big-deal` | `MARKET_BIG_DEAL_RANK` | P3 |

Phase 1.1 该域 8 个 endpoint 中，2 个已具备迁移条件，6 个需 OpenStock 中台补类别（不在本仓库权限内，需走 OpenSpec 提案到 `openstock/openspec/`）。

---

## 3. 验证

- `python -m pytest tests/services/openstock_client/test_northbound_flow_parsing.py tests/services/openstock_client/test_northbound_holding_parsing.py -v` → 17 passed
- `git diff web/backend/app/services/openstock_client.py` → 仅 3 行新增，无修改其他逻辑
- `git diff web/backend/app/api/akshare_market/fund_flow.py` → 空（未触动业务代码）
- `docs/guides/openstock-migration/DOMAIN_MIGRATION_PLAYBOOK.md` → 可读、章节齐全、含 FundFlow §三 清单

---

## 4. 第二批启动入口（下次会话）

### 4.1 第二批交付工作项清单

| # | 工作项 | 文件 / 路径 | 预估 LOC | 风险 |
|---:|---|---|---:|---|
| 1 | 切换 `fund_flow.py:257` `hsgt-summary` endpoint | `web/backend/app/api/akshare_market/fund_flow.py` | ~30 | 中 |
| 2 | 切换 `fund_flow.py:411` `north-stock/{symbol}` endpoint | 同上 | ~30 | 中 |
| 3 | 给其余 6 个 endpoint 加 `TODO(B4.014-Phase1.1-gap)` 注释 | 同上 | ~12 | 低 |
| 4 | API e2e 测试 | `tests/api/test_fund_flow_openstock.py` | ~200 | 低 |
| 5 | CI lint 脚本 | `scripts/linting/forbidden_imports.py` | ~150 | 低 |
| 6 | 浏览器 e2e + 截图 | `FundFlow.vue` 手测 | — | 中 |
| 7 | 完成 worklog | `docs/reports/worklogs/claude-auto/b4-014-phase1-1-batch2-fundflow-switch-2026-06-29.md` | ~200 | 低 |

**预估总 diff**: ~600 LOC + 浏览器手测截图

### 4.2 第二批启动 checklist

下次会话启动时按此 checklist 顺序执行：

1. **读取上下文**:
   - `architecture/standards/openstock-consumer-boundary-sot.md`（SOT V1.0）
   - `docs/guides/openstock-migration/DOMAIN_MIGRATION_PLAYBOOK.md`（本批次产出）
   - 本 worklog
   - `web/backend/app/api/akshare_market/fund_flow.py:257` 与 `:411` 上下文

2. **切换前 live 字段对照**（已在本会话探测，下次会话复用）:

   **`NORTHBOUND_FLOW`** (`/fund-flow/hsgt-summary`):
   ```
   trade_date | flow_type | board_name | fund_direction | trade_status
   net_buy_amount | fund_net_inflow | balance | up_count | down_count
   flat_count | related_index | index_change_pct
   ```
   原 akshare 方法 `get_stock_hsgt_fund_flow_summary_em(start_date, end_date)` 返回 DataFrame，列名近似需现场对照（多半是中文列名）。

   **`NORTHBOUND_HOLDING`** (`/fund-flow/north-stock/{symbol}`):
   ```
   symbol | trade_date | close | change_pct | holding_shares
   holding_market_cap | holding_shares_ratio | add_shares | add_amount
   holding_market_cap_change
   ```
   原 akshare 方法 `get_stock_hsgt_north_acc_flow_in_em(symbol)` 返回 DataFrame，列名需现场对照。

3. **切换原则**:
   - 保留原 endpoint 路径、请求参数（`symbol`、`start_date`、`end_date`）、响应中文键名不变
   - 把 `df = await akshare_market_adapter.<method>(...)` 替换为 `result = await openstock_client.fetch("NORTHBOUND_FLOW", params={...})`
   - 字段映射: OpenStock 英文 snake_case → 现有响应中文键名（按 DataFrame 列名映射）
   - 保留 `try/except Exception` 与 `create_error_response(ErrorCodes.INTERNAL_ERROR, ...)` 形态

4. **浏览器验证标准**: 见 Playbook §四.2 FundFlow 域专属清单。

5. **PR 描述必须包含**: OpenStock 正常响应截图 + OpenStock 不可用降级截图（用 `OPENSTOCK_BASE_URL=http://127.0.0.1:9999` 模拟不可达）。

### 4.3 第二批的禁止动作

- ❌ 删除 `AkshareMarketDataAdapter.fund_flow` mixin — 第三批 cleanup 范围，本批不动
- ❌ 修改路由路径 — Phase 3 路径统一才动
- ❌ 切换本批次未在 §四.1 列出的 endpoint — 走 Phase 1.2+ 后续 PR
- ❌ 修改 OpenStock 客户端代码 — 本批只动业务层

---

## 5. 本批次与 SOT 的对应关系

| SOT 章节 | 本批次实现 |
|---|---|
| SOT §五.2 单元解析测试 | `tests/services/openstock_client/test_northbound_{flow,holding}_parsing.py` |
| SOT §五.3 准入例外 | 未使用，本批次无白名单例外 |
| SOT §九 迁移操作手册 | `docs/guides/openstock-migration/DOMAIN_MIGRATION_PLAYBOOK.md` V1.0 |
| SOT §七 路由路径方案 | 第二批业务切换时遵守，本批次未涉及 |
| SOT §八 CI 强制校验 | 第二批交付 `scripts/linting/forbidden_imports.py`，本批次未涉及 |

**SOT §五.2 准入闭环状态**: 第一批已完成"白名单 + 单元测试"两部分，业务切换与 API e2e 在第二批完成。整个 Phase 1.1 PR 合入时仍是一个 atomic PR（用户授权分两批执行 ≠ 拆为两个 PR）。

---

## 修订历史

- **2026-06-29 V1.0（初始）**: 第一批交付完成。3 LOC 白名单 + 536 LOC 测试 + 197 LOC Playbook。运行时风险零，可直接进入第二批启动 checklist。
