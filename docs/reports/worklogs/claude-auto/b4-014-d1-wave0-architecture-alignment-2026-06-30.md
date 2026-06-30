# Handoff: B4.014 Task #11 — D1 Wave 0 架构对齐

**日期**: 2026-06-30  
**会话**: 5bacdfb1 (Claude)  
**分支**: `feat/b4-014-fundflow-mixin-openspec-proposal`  
**提交**: `614290989` (Wave 0) / `af5036395` (审计)

---

## 本次完成

### 决策

**D1 — 完全回归提案（Mixin 层方案）** 已选定。理由：C1 数据源统一原则 > 短期节省工作量。Phase 1.1 服务层旁路已被抬升回 Mixin。

### 审计（af5036395）

- `docs/reports/analysis/2026-06-30-b4-014-task11-preflight-audit.md`
- 全仓库 OpenStockClient 调用点审计 + akshare 25 文件残留台账
- BLOCK_TRADE 误判撤回 + 5 处事实修正落地
- 中台缺口台账：6 个缺失类别（NORTHBOUND_FLOW_DETAIL 等）需同步 OpenStock 维护方

### Wave 0 架构对齐（614290989）

6 文件变更，15/15 测试通过：

| 文件 | 变更 |
|------|------|
| `src/adapters/akshare/market_adapter/_openstock.py` | **新建** — `_build_default_openstock_client()` 工厂 |
| `src/adapters/akshare/market_adapter/adapter.py` | `__init__` 增加 `openstock_client: OpenStockClient \| None = None` |
| `src/adapters/akshare/market_adapter/fund_flow.py` | 搬运 `_translate_northbound_flow_row` / `_translate_northbound_holding_row`；重写 2 个 Mixin 方法 |
| `web/backend/app/api/akshare_market/fund_flow.py` | 还原 hsgt-summary + north-stock 端点 → 调 adapter Mixin；删除 `_build_openstock_client` + 翻译 helpers |
| `tests/adapters/test_fund_flow_mixin.py` | **新建** — 9 个单测 |
| `tests/api/test_fund_flow_openstock.py` | monkeypatch 目标更新 |

### 架构变化

```
之前:  端点 → _build_openstock_client() → OpenStock    (绕过了 Mixin)
       Mixin → akshare（没人调）

现在:  端点 → adapter.get_*() → Mixin → self._openstock_client → OpenStock
```

### 测试结果

- Mixin 构造注入: 3/3 ✅
- Mixin 方法 stub (success/empty/error × 2): 6/6 ✅
- API e2e (hsgt-summary + north-stock): 6/6 ✅

---

## 待办（后续会话）

### P0 — 合并阻塞

| 事项 | 状态 |
|------|------|
| PR #488 评审 | 等待人工 review。审计文档 + Wave 0 commit 均为评审证据 |
| 浏览器冒烟验证 | 需运行中 OpenStock 中台 + 前后端服务（`hsgt-summary` + `north-stock/{symbol}` 两个端点） |

### P1 — Wave 1 正式实施

提案 `tasks.md` §3 的剩余子任务。Wave 0 已完成核心抬升，剩余：

- 3.5-3.6: 测试补充（已有 15 个测试，可增量）
- 3.7: 浏览器验证
- 3.8: 确认 import akshare 仅在 Wave 2/3 方法中使用（当前仍是，因为其他 7 个 Mixin 方法仍走 akshare）

### P2 — 解阻塞 Wave 2/3

中台缺口台账（审计 §5 P2）的 6 个类别需同步 OpenStock 维护方：
`NORTHBOUND_FLOW_DETAIL`, `NORTHBOUND_NET_FLOW`, `SOUTHBOUND_NET_FLOW`, `SOUTHBOUND_HOLDING`, `HSGT_HOLDINGS`, `MARKET_SENTIMENT`

### P3 — 独立议题

- `wip/root-dirty-20260403` 治理（与 OpenStock 解耦，独立会话）
- 注入规范统一（三种 OpenStockClient 构造形态 → 单一 Depends 工厂）

---

## 关键文件速查

| 用途 | 路径 |
|------|------|
| 审计文档 | `docs/reports/analysis/2026-06-30-b4-014-task11-preflight-audit.md` |
| Adapter 工厂 | `src/adapters/akshare/market_adapter/_openstock.py` |
| Adapter 入口 | `src/adapters/akshare/market_adapter/adapter.py` |
| FundFlowMixin | `src/adapters/akshare/market_adapter/fund_flow.py` |
| 端点路由 | `web/backend/app/api/akshare_market/fund_flow.py` |
| Mixin 单测 | `tests/adapters/test_fund_flow_mixin.py` |
| API 测试 | `tests/api/test_fund_flow_openstock.py` |
| 提案 tasks | `openspec/changes/migrate-akshare-fundflow-mixin-to-openstock/tasks.md` |
| 提案 design | `openspec/changes/migrate-akshare-fundflow-mixin-to-openstock/design.md` |
| 提案 spec | `openspec/changes/migrate-akshare-fundflow-mixin-to-openstock/specs/data-source-runtime-service/spec.md` |

---

## 后续会话启动命令

```bash
cd /opt/claude/mystocks_spec
git checkout feat/b4-014-fundflow-mixin-openspec-proposal
# 运行现有测试确认环境正常:
python3 -m pytest tests/adapters/test_fund_flow_mixin.py tests/api/test_fund_flow_openstock.py -v -q
```

## 禁止事项

- 不在脏工作区启动 Wave 1 实施（必须基于干净分支）
- 架构方向已是 D1，不接受 D2/D3 回退
- 不重做审计探索（已有 `af5036395`）
