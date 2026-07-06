# B4.014 OpenStock Routes 工作日志

**分支**: `feat/b4-014-openstock-routes`
**Base**: `origin/main` (`6a858519c`)
**PR**: https://github.com/chengjon/mystocks/pull/490
**完成日期**: 2026-07-01
**总改动**: 9 commits, 16 files, +3549 / -2

---

## 一、完成的工作

### 1.1 任务定位

将 `/api/v1/market/quotes` 与 `/api/v1/market/kline` 两个核心行情路由接入 `data_source_factory` 框架,以 OpenStock (`http://192.168.123.104:8040`) 为 primary,akshare service 作为 `/kline` 的二级 fallback,前端 schema 契约不变。

### 1.2 架构成果

```
/quotes → factory.get_data_with_fallback("openstock_market", "quotes", ...)
            ├─ primary:  OpenStockMarketDataSourceAdapter (real OpenStock)
            └─ fallback: openstock_market_mock (MarketDataSourceAdapter mock 模式)

/kline  → factory.get_data_with_fallback("openstock_market", "klines", ...)
            ├─ primary:  OpenStockMarketDataSourceAdapter
            ├─ fallback: openstock_market_mock
            └─ 路由层二级 fallback → service.get_a_stock_kline (akshare)
```

**业务语义不对称**(已确认合理):
- `/quotes` 一层 fallback 够用:mock 行情前端能渲染
- `/kline` 两层 fallback:mock K 线回测不能用,真业务必须 fallback 到 akshare 真实数据

### 1.3 9 个 Commits(按时序)

| # | SHA | 内容 |
|---|---|---|
| 1 | `fa29236ff` | docs baseline — 设计文档 + openspec 提案(cherry-pick 自另一 worktree) |
| 2 | `5811778ba` | cherry-pick `openstock_client.py` (299 行) — 适配器的 HTTP 客户端基础 |
| 3 | `ede6e1be2` | 新建 `OpenStockMarketDataSourceAdapter` (266 行) — 实现 IDataSource 接口 |
| 4 | `361d8518f` | factory 注册 + JSON 配置 — `source_type=="openstock_market"` 分支 + `openstock_market`/`openstock_market_mock` 双源 |
| 5 | `9635c0fbd` | 路由切换 — `/quotes` 改用 `get_data_with_fallback`,`/kline` 加路由层二级 akshare fallback |
| 6 | `1d2837125` | adapter 单测 18 个 — 覆盖 quotes/klines/health_check/metrics/transform 全路径 |
| 7 | `490e34774` | 集成测试 10 个 — `/quotes` + `/kline` + factory-level fallback 契约 |
| 8 | `a8435d86e` | CodeWhale 复核修复 — None/[] 区分、count 推算、coerce_rows warning + 3 个新测试 |
| 9 | `1b09a3626` | 审核文档 — 自审报告 + CodeWhale 第三方复核 |

### 1.4 关键设计决策

#### A. Endpoint 路由表(方案 A)
单 adapter 内部 if-elif 分发 endpoint → OpenStockClient 方法。避免为每个 endpoint 拆一个 adapter 类导致配置爆炸(符合 CLAUDE.md §1.1.1 个人本地化部署约束)。

#### B. Envelope 双键设计
adapter 返回 `{status, data, candles|quotes, source, endpoint, timestamp, parameters}`,同时保留 `data` 与 `candles`/`quotes`:
- `build_quotes_response_payload` 读 `data`
- 前端 `extractKlineRows` 读 `candles`
- 过渡期兼容,task #11 完成后可统一

#### C. 字段映射
OpenStock KLINES 返回 `time`,前端期望 `datetime`:
```python
if key_lower == "time":
    result["datetime"] = value
elif key_lower == "date":
    result.setdefault("datetime", value)  # date 兜底
```

#### D. Health check 用独立 httpx.AsyncClient
不复用 OpenStockClient 内部 client — 避免业务请求故障导致健康检查假阴性。

#### E. `/kline` count 推算(后期修复)
`start_date`/`end_date` 有值时按天数差推算;否则默认 60。OpenStock API 当前不支持日期范围查询,task #11 推动 OpenStock 改造。

#### F. None vs [] 区分(后期修复)
OpenStock 返回 `[]`(停牌股票合法空响应)不触发 fallback;返回 `None`(真失败)才跳 akshare。

### 1.5 测试覆盖

| 层级 | 文件 | 用例数 | 结果 |
|---|---|---|---|
| Adapter 单测 | `test_openstock_market_data_adapter.py` | 18 | ✅ 18/18 |
| 路由集成 | `test_openstock_market_routes_integration.py` | 13 | ✅ 13/13 |
| 回归 | `test_market_api.py` | 25 | ✅ 24/25(1 pre-existing akshare mock seed,与本 PR 无关) |
| 第三方审核 | CodeWhale (deepseek-v4-pro) | — | ✅ 通过(2 重要 + 3 轻微,全部修复) |

**集成测试关键技术细节**:
- 三种 patch 边界:lazy import → patch 源模块;module-level import → patch 路由模块;包 `__init__` re-export → patch 包属性
- MagicMock + AsyncMock 桩 factory,避免真实 HTTP/DB
- TestClient + dependency_overrides 桩 auth

---

## 二、第三方审核闭环

CodeWhale(deepseek-v4-pro)做了独立源码审计,在 commit `a8435d86e` 中闭环修复:

| # | 严重度 | 问题 | 修复 |
|---|---|---|---|
| 1 | 重要 | `/kline` count=60 硬编码,忽略 start_date/end_date | 按天数差推算 daily/weekly/monthly |
| 2 | 重要 | 空 candles 误触发 fallback(停牌合法空响应) | 区分 None 与 [] |
| 3 | 轻微 | `_coerce_rows` 无法识别 Mapping 静默吞数据 | 加 logger.warning |
| 4 | 轻微 | 自审报告行数小偏差(266→280,commit 间演进) | 文档说明 |
| 5 | 轻微 | 集成测试在 worktree 缺 .env 无法运行 | 文档说明环境需求 |

审核文档:
- 自审:`docs/reports/b4-014-m1k-m1m-review.md`(408 行)
- CodeWhale 复核:`docs/reports/worklogs/claude-auto/B4_014_M1K_M1M_REVIEW_AUDIT_2026-07-01.md`

---

## 三、明确排除的工作

| 项目 | 任务 ID | 状态 | 说明 |
|---|---|---|---|
| `AkshareMarketDataSourceAdapter` 大型迁移 | #11 | pending | 把 akshare 也包成 IDataSource,合并到 factory 内。届时路由层二级 fallback 可简化,factory dispatch 改注册表模式 |
| OpenSpec `migrate-akshare-fundflow-mixin-to-openstock` 审批 | — | pending | commit 1 cherry-pick 了提案,等用户走 OpenSpec 流程批准 |
| 浏览器烟测前端 K 线 / 行情页面 | — | P1 可选 | 需本地起 backend |
| 真实 OpenStock `/quotes?symbols=000001` curl 验证 | — | P1 可选 | 绕过测试 mock,确认生产路径 |
| Factory dispatch 重构成注册表模式 | — | 后续 | task #11 完成后一起做 |
| `test_get_quotes_single_symbol` akshare mock seed 修复 | — | 不在本 PR | pre-existing,与本 PR 0 关联 |

---

## 四、下一步工作计划

### P0 — 立即(等 PR review)

- [ ] **用户审核 PR #490** — 重点关注 commit 8 的 None/[] 区分逻辑是否符合业务预期(停牌股票场景)
- [ ] PR 合入 main 后,关闭 task #42、task #52 等相关任务

### P1 — 推荐(可与 P0 并行,验证生产路径)

- [ ] **真实 OpenStock curl 烟测**:
  ```bash
  curl "http://192.168.123.104:8040/quotes?symbols=000001"
  curl "http://192.168.123.104:8040/klines?symbol=000001&period=day&count=10"
  ```
  确认 OpenStock 真实返回与 adapter envelope schema 一致
- [ ] **浏览器烟测**:本地起 backend(`uvicorn app.main:app --port 8020`)+ frontend,验证 K 线/行情页面渲染
- [ ] 验证停牌股票(如 `600519` 停牌日)是否正确返回空 candles 而非触发 akshare fallback

### P2 — 后续任务(独立立项)

- [ ] **Task #11: AkshareMarketDataSourceAdapter 大型迁移**
  - 把 akshare 包成 IDataSource 实现
  - 注册到 factory,JSON 加 `akshare_market` 源
  - `/kline` 路由层二级 fallback 可简化为 factory 内部 fallback
  - Factory dispatch 改注册表模式(`source_type → adapter_class` 字典)
- [ ] **OpenSpec 审批 `migrate-akshare-fundflow-mixin-to-openstock`**
  - 走 `openspec/AGENTS.md` 流程
  - 批准后开始 FundFlow 域迁移
- [ ] **OpenStock API 改造**(若 OpenStock 团队接受)
  - 支持 `/klines?start_date=...&end_date=...` 日期范围查询
  - 届时 adapter 可直接传日期,count 推算逻辑可移除

### P3 — 技术债治理(非紧急)

- [ ] `libtmux.pytest_plugin` 与 pytest 不兼容 — `libtmux/pytest_plugin.py:53` 把 mark 装到 fixture,新 pytest 已禁用。建议 `pip uninstall libtmux` 或固定 pytest 版本
- [ ] `test_market_api.py::test_get_quotes_single_symbol` akshare mock seed `sh689009` 问题 — 独立 task 修
- [ ] Worktree 缺 `.env` 导致 `app.core.config.settings` SystemExit — 建议在 worktree 创建脚本里 symlink 主仓库 `.env`,或在 `conftest.py` 加测试环境 fallback

---

## 五、验证命令(供后续复跑)

```bash
cd /opt/claude/mystocks_spec/.claude/worktrees/b4-014-openstock-routes/web/backend
set -a && source /opt/claude/mystocks_spec/.env && set +a

# 全量回归
python -m pytest tests/test_openstock_market_data_adapter.py \
                 tests/test_openstock_market_routes_integration.py \
                 tests/test_market_api.py \
                 -p no:libtmux --no-cov -n 0
# 预期: 18 + 13 + 24 passed, 1 failed (pre-existing)
```

---

## 六、GitNexus 影响评估(最终)

| 改动 symbol | impact | 实际影响 |
|---|---|---|
| `IDataSource` (新增第 14 个实现) | HIGH upstream (28 callers) | 不破坏接口,callers 不受影响 |
| `_create_single_data_source` (factory dispatch) | LOW (5 symbols, factory 内部) | 新增分支,不影响其他 dispatch |
| `get_a_stock_kline` (/kline fallback) | MEDIUM (3 callers) | 路由层调用方式不变,从 primary 降级为 secondary |

每个 commit 前 `detect_changes` 都跑过,无意外 symbol 被改动。

---

## 七、关键文件清单

| 类型 | 路径 | 行数 |
|---|---|---|
| Adapter | `web/backend/app/services/openstock_market_data_adapter.py` | 285 |
| Client | `web/backend/app/services/openstock_client.py` | 299 |
| Factory 改动 | `web/backend/app/services/data_source_factory/data_source_factory.py` | +7 |
| 路由改动 | `web/backend/app/api/market/market_data_request.py` | +56/-2 |
| JSON 配置 | `config/data_sources.json` | +33 |
| Adapter 单测 | `web/backend/tests/test_openstock_market_data_adapter.py` | 306 |
| 路由集成测试 | `web/backend/tests/test_openstock_market_routes_integration.py` | 481 |
| 自审报告 | `docs/reports/b4-014-m1k-m1m-review.md` | 408 |
| CodeWhale 复核 | `docs/reports/worklogs/claude-auto/B4_014_M1K_M1M_REVIEW_AUDIT_2026-07-01.md` | 218 |
| **本文档** | `docs/reports/worklogs/claude-auto/B4_014_OPENSTOCK_ROUTES_WORKLOG_2026-07-01.md` | — |

---

**🎉 B4.014 S5 OpenStock primary 接入 + 多源 fallback 路由改造完成。等 PR review。**
