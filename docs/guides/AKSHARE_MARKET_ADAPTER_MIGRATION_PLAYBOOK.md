# Playbook: AkshareMarketDataAdapter → OpenStock 迁移立项

> **Status**: PROPOSAL — 待 OpenSpec 走 proposal 流程审批
> **Owner**: B4.014 follow-up batch
> **Created**: 2026-07-03
> **Origin**: B4.014 task #11 (deferred from first-batch scope)
> **Estimated effort**: ~3-5 个 PR / 2-3 周（独立 worktree）

---

## 0. 背景与边界

### 为什么独立立项

B4.014 第一批只迁了 `get_timeseries_source × 3`（kline/quotes 路由），把 `AkshareMarketDataAdapter`（板块、资金流、新闻、公告、研报、财务预测）这一坨**留作第二批**：

- 体积大：6 子模块、1521 LOC（实测；任务卡里写的 1825 是历史估值）、~30 个 async 方法
- 消费者多：`web/backend/app/api/akshare_market/` 下 6 个路由文件依赖它（analysis / boards / stock_info / szse / fund_flow / sse）
- 每方法都需做 payload 映射 + response reshape — 不是机械替换

混入第一批会让 B4.014 PR 膨胀、回归不可控。独立批次 + 独立 PR 序列更稳。

### 不在本 playbook 范围

- `get_timeseries_source` 链路（已 B4.014 完成）
- `market_data_service_v2.py` 整体废弃（依赖本批完成后才能做）
- OpenStock 上游新增类别的能力扩展（如果发现缺口，单独立 backend 项）

---

## 1. 现状盘点（已 verified）

### 1.1 Adapter 源码（`src/adapters/akshare/market_adapter/`）

| 文件 | LOC | 职责 |
|---|---:|---|
| `__init__.py` | 7 | 导出聚合 |
| `adapter.py` | 52 | 顶层 adapter 类，组合各 mixin |
| `board_sector.py` | 332 | 板块行情、板块K线、板块成份股 |
| `forecast_analysis.py` | 186 | 财务预测、研报、业绩预告 |
| `fund_flow.py` | 358 | 北向资金、个股主力、大单、板块资金流 |
| `market_overview.py` | 233 | 大盘总览、涨跌停统计、市场温度 |
| `stock_profile.py` | 157 | 个股基础信息、行业分类 |
| `stock_sentiment.py` | 196 | 新闻、公告、舆情热度 |
| **total** | **1521** | |

### 1.2 消费者（`web/backend/app/api/akshare_market/`）

6 个路由文件引用 `AkshareMarketDataAdapter` / `market_adapter`：

- `analysis.py` — 业绩预告 / 研报 / 财务预测
- `boards.py` — 板块行情 / 板块成份 / 板块K线
- `stock_info.py` — 个股基础信息
- `szse.py` — 深交所专属接口
- `fund_flow.py` — 资金流（已被 B4.014 第一批部分迁走，但仍有残留）
- `base.py` / `sse.py` — 共享 base / SSE 流

> **Note**: 不在这 6 个里但应核查 — `web/frontend/src/api/*` 调用路径；如有 router 直接绕过 adapter 调 akshare，单独登记。

### 1.3 OpenStock 上游能力（`src/adapters/akshare.py`）

任务卡里声明 OpenStock 已暴露 9 个相关类别：

`SECTOR_KLINES` / `SECTOR_CONSTITUENTS` / `SECTOR_FUND_FLOW` / `FUND_FLOW` / `STOCK_NEWS` / `ANNOUNCEMENTS` / `RESEARCH_REPORTS` / `FINANCIAL_STATEMENTS` / `FORECAST_DATA`

**P0 verification gate**：在本批启动前，**先跑一遍 OpenStock 真实集成测试**确认每个类别都返回非空数据。任何一类在上游返回空 → 立项延期，先修上游。

```bash
# 验证脚本（参考 web/backend/tests/test_openstock_real_integration.py）
for cat in SECTOR_KLINES SECTOR_CONSTITUENTS SECTOR_FUND_FLOW FUND_FLOW \
           STOCK_NEWS ANNOUNCEMENTS RESEARCH_REPORTS \
           FINANCIAL_STATEMENTS FORECAST_DATA; do
    pytest -k "${cat}_returns_data" --no-cov -n 0
done
```

如果跑下来某类别缺测试，先补测试再启动迁移。

---

## 2. 迁移策略：模块切片 + 双跑对比

### 2.1 切片顺序（按消费者复杂度排序，先易后难）

| Phase | 模块 | LOC | 消费者 | 风险 |
|---|---|---:|---|---|
| **P1** | `stock_profile.py` | 157 | `stock_info.py` | 低 — 字段稳定 |
| **P2** | `market_overview.py` | 233 | `analysis.py`、`boards.py` | 中 — 涨跌停统计口径多变 |
| **P3** | `board_sector.py` | 332 | `boards.py` | 中 — 板块成份股要 reshape |
| **P4** | `stock_sentiment.py` | 196 | `analysis.py` | 低 |
| **P5** | `forecast_analysis.py` | 186 | `analysis.py` | 中 — 业绩预告字段漂移 |
| **P6** | `fund_flow.py` | 358 | `fund_flow.py`、`sse.py` | **高** — 已被 B4.014 部分迁，需先理清残留 |

**每个 Phase = 1 个独立 PR**，互不阻塞。建议在 worktree `b4-014-akshare-migration-p{N}` 里开发，PR base 是 `feat/b4-014-openstock-routes` 而非 `main`（保持 B4.014 大批次可追溯）。

### 2.2 每个 Phase 的标准 PR 清单

每个 Phase 的 PR 必须包含：

1. **Mapping 表**（在 PR description 里）：
   ```
   adapter_method → OpenStockClient.fetch_data(category=X, params=Y)
   旧 response 字段 → 新 response 字段
   ```
2. **单测更新**：`tests/test_<module>_migration.py` 至少覆盖 happy path + 1 个 edge case
3. **真实集成探针**：用 `@pytest.mark.integration` 跑 OpenStock 真实端点，对照旧 akshare 端点的返回
4. **回归 browser smoke**：受影响的前端页面（参考 myweb-audit audit-20260702-01 已覆盖的页面清单）跑 5 维度最小回归
5. **Debt 登记**：如某方法字段无法 1:1 映射，登记到 `docs/reports/quality/BUG_LESSONS_LEARNED.md` 而非静默兜底

### 2.3 双跑对比模式（前 2 个 Phase 强制启用）

P1/P2 在切流量到 OpenStock 之前，先在 adapter 内部跑 **双源对比**：

```python
async def get_stock_profile(self, code: str):
    legacy = await self._legacy_akshare_profile(code)  # 旧实现
    new = await self.openstock_client.fetch_data(
        category=StockCategory.STOCK_PROFILE,
        params={"symbol": code}
    )
    self._compare_fields(legacy, new, ["name", "industry", "list_date", ...])
    return new  # 用新源；任何字段不一致 warn-log + 登记到 debt
```

P1/P2 完成后，若字段一致率 ≥ 95%，可关闭双跑（避免长期 2 倍上游压力）。

---

## 3. 风险与回滚

### 3.1 主要风险

| 风险 | 触发场景 | 缓解 |
|---|---|---|
| **OpenStock 上游字段漂移** | akshare 升级后字段名变 | 双跑对比阶段先暴露 |
| **板块成份股 reshape 复杂** | 上游返股票代码无前缀，旧逻辑要补 sh/sz | mapping 表显式列出，禁止默认行为 |
| **fund_flow 字段已在 B4.014 部分漂移** | hsgt/big-deal 已在 P1.1-4 改过 | P6 启动前先做 `git log -- fund_flow.py` 审计 |
| **SSE 流断流** | `sse.py` 用 adapter 推送，切换期双订阅 | P6 单独留出半天做 SSE 压测 |

### 3.2 回滚

每个 Phase 的 PR 必须可独立 revert。具体手段：

- 保留旧 adapter mixin 类名（`AkshareFundFlowMixin`、`OpenStockFundFlowMixin`），路由层通过 factory 切换
- factory 配置：`config/data_sources.json` 加 `market_adapter_provider: "akshare" | "openstock"`
- 任一 Phase 出问题 → revert 单 PR + factory 切回 akshare，不影响其他 Phase

---

## 4. 验收门槛（Definition of Done）

每个 Phase 的 PR 合并前必须满足：

- [ ] 单测：新模块 ≥ 90% line coverage
- [ ] 集成测试：OpenStock 真实端点 ≥ 1 个 happy path + 1 个 edge case
- [ ] Browser smoke：受影响页面 5 维度（route/functional/data-state/visual/a11y）pass
- [ ] 双跑字段一致率（仅 P1/P2）：≥ 95%
- [ ] PR description 含 mapping 表
- [ ] myweb-audit closeout：该批页面的 closeout-checklist 全绿

整体（6 个 Phase 全部合并后）：

- [ ] `src/adapters/akshare/market_adapter/` 整目录标记 `@deprecated`
- [ ] `web/backend/app/api/akshare_market/` 路由层全部走 factory
- [ ] `market_data_service_v2.py` 可单独退役（独立 PR）

---

## 5. 不做的事（Out of Scope）

- ❌ 重写路由层 API 契约（路由返回格式保持不变，前端零改动）
- ❌ 引入新的 cache 层 / queue 层
- ❌ 性能优化（除非字段映射天然带来 ≥ 2x 提速）
- ❌ 修复 akshare 上游 bug（如发现，登记后单独立项）
- ❌ 删除 `market_data_service_v2.py`（依赖本批完成后再退役）

---

## 6. 立项审批门槛

**进入实施前的硬门槛**：

1. ✅ 本 playbook 通过 OpenSpec `proposal` 流程审批
2. ✅ §1.3 的 OpenStock 9 类别验证测试全绿（如缺测试先补）
3. ✅ 在 `openspec/changes/<change-id>/` 创建正式 change spec
4. ✅ 与 backend 团队确认 P6 fund_flow 与 B4.014 第一批残留不冲突

通过后，开 worktree `b4-014-akshare-migration-p1` 启动 P1。

---

**Last updated**: 2026-07-03
**Authors**: Claude (glm-5.2) + JohnC
**Source**: B4.014 task #11
