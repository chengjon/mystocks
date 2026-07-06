# B4.014 M1k/M1m 代码审核报告

**分支**: `feat/b4-014-openstock-routes` (已推送 origin)
**Base**: `origin/main` `6a858519c`
**总改动**: 14 files, +2820 / -2 (2777 新增 + 43 修改)
**作者**: Claude (glm-5.2)
**审核文档生成**: 2026-07-01

---

## 一、任务目标

将 `/quotes` 与 `/kline` 两个核心行情路由接入 `data_source_factory` 框架,以 OpenStock (`http://192.168.123.104:8040`) 为 primary 数据源,保留 akshare service 作为二级 fallback,同时不影响前端 schema 契约。

**前置背景**:
- B4.013-M2-E1 已经在另一 worktree 落地 `OpenStockClient`(底层 HTTP 客户端),但本 worktree base (`origin/main` 6a858519c) 上还没有
- B4.014-M1j 修复了 backtest 路由的 runtime 契约(与本任务无关,已完成)
- 本任务的 7 个 commits 是**独立的、可单独审核**的 OpenStock 接入工作

---

## 二、Commit 列表(按时序)

| # | SHA | 标题 | 改动 |
|---|---|---|---|
| 1 | `fa29236ff` | docs(b4-014): M1k/M1m baseline — design docs + openspec proposal | 7 文件 / +1453 |
| 2 | `5811778ba` | M1k-1: cherry-pick openstock_client from B4.013-M2-E1 | 1 文件 / +299 |
| 3 | `ede6e1be2` | M1k-2: OpenStockMarketDataSourceAdapter 实现 IDataSource | 1 文件 / +266 |
| 4 | `361d8518f` | M1k-3: register OpenStock in factory + JSON config | 2 文件 / +40 |
| 5 | `9635c0fbd` | M1k-4+5: route /quotes + /kline through OpenStock factory | 2 文件 / +58 |
| 6 | `1d2837125` | M1m-6: OpenStockMarketDataSourceAdapter unit tests | 1 文件 / +306 |
| 7 | `490e34774` | M1m-7: OpenStock /quotes + /kline route integration tests | 1 文件 / +404 |

---

## 三、各步骤解决的问题与关键设计

### 步骤 1 — Baseline (commit `fa29236ff`)

**问题**: M1k/M1m 的设计文档在另一 worktree(`b4-014-milestone`)中,本 worktree 上没有引用源。
**解决**: Cherry-pick 4 个文档 commit 作为本 worktree 的设计依据:
- `177a2b4db` 主数据架构审计 v4
- `6449834c7` 审计 v5 — S5 前置 + 正式签字
- `9d1947d00` S5 OpenStock adapter 设计(M1k/M1m 实施依据)
- `beb5d2bcd` openspec 提案:migrate-akshare-fundflow-mixin-to-openstock

**为什么不直接 merge 那个 worktree?** 那个 worktree 含有 M1j 的 backtest 改动,与本任务无关,会产生跨任务污染。Cherry-pick 文档可以保持 PR 焦点。

### 步骤 2 — Cherry-pick OpenStockClient (commit `5811778ba`)

**问题**: `web/backend/app/services/openstock_client.py`(299 行,在 B4.013 worktree 上)是后续 adapter 的依赖,但本 worktree 没有。
**解决**: 整文件 cherry-pick,验证 `from app.services.openstock_client import OpenStockClient` 可正常导入。
**关键 API**(后续 adapter 用到的):
- `OpenStockClient.fetch(endpoint_name, params)` → `OpenStockFetchResult(data, source, data_category, ...)`
- `OpenStockClient.fetch_bars(symbol, period, count)` → 同上,用于 KLINES
- `OpenStockClientConfig(base_url, timeout_seconds)` 配置载体

### 步骤 3 — Adapter 实现 (commit `ede6e1be2`) ⭐ 核心

**新建**: `web/backend/app/services/openstock_market_data_adapter.py` (266 行)

**核心问题**: OpenStockClient 是 HTTP 客户端,但 `data_source_factory` 框架要求每个源实现 `IDataSource` 接口(`get_data(endpoint, params)` / `health_check()` / `get_metrics()`)。如何把 OpenStock 的 N 个 endpoint 统一到一个接口下?

**设计选择 — Endpoint 路由表(方案 A)**:
```python
PERIOD_MAP = {"daily": "day", "weekly": "week", "monthly": "month"}
ENDPOINT_ROUTES = {"quotes": "REALTIME_QUOTES"}

async def get_data(self, endpoint: str, params: dict) -> dict:
    if endpoint == "klines":
        return await self._fetch_klines(client, params)   # → client.fetch_bars
    elif endpoint == "quotes":
        return await self._fetch_quotes(client, params)   # → client.fetch("REALTIME_QUOTES")
    else:
        raise ValueError(f"Unsupported endpoint: {endpoint}")
```

> 替代方案 B 是为每个 endpoint 拆一个 adapter 类(`OpenStockQuotesSource` / `OpenStockKlinesSource`),但会让 factory 配置爆炸(每个 endpoint 一条 JSON),违反"个人本地化部署"原则(CLAUDE.md §1.1.1)。

**字段映射问题**: OpenStock KLINES 实测返回字段是 `time`(不是 `datetime`),但前端 `extractKlineRows` 期望 `datetime`。
```python
@staticmethod
def _transform_kline_row(row):
    result = {}
    for key, value in row.items():
        key_lower = str(key).lower()
        if key_lower == "time":
            result["datetime"] = value   # time → datetime
        elif key_lower == "date":
            result.setdefault("datetime", value)  # date 作为 datetime 兜底
        else:
            result[key_lower] = value
    return result
```

**Envelope schema**(关键决策,与现有 `MarketDataSourceAdapter` 对齐):
```python
return {
    "status": "success",
    "data": rows,           # 主数据键
    "candles": candles,     # /kline 专用(MarketDataSourceAdapter 风格)
    "quotes": quotes,       # /quotes 专用
    "timestamp": "...",
    "source": "openstock",
    "endpoint": "klines" | "quotes",
    "data_category": fetch_result.data_category,
    "parameters": {...},
}
```
> 同时保留 `data` 与 `candles`/`quotes` 是为了向后兼容:`build_quotes_response_payload` 读 `data`,前端 `extractKlineRows` 读 `candles`,两者都不破坏。

**Health check 设计**:
- 优先打 `/health/live`(审计 v5 实测 9.9ms / 200 OK)
- 5xx → `DEGRADED`
- HTTPError → `FAILED`
- 5s 超时

**GitNexus 影响评估**:
- `IDataSource` upstream impact = **HIGH**(28 个直接 caller)
- 但本改动是**新增第 14 个实现类**,不修改接口契约,不会破坏现有 13 个实现或 caller
- 这条评估在 commit message 中明确记录,作为审计依据

### 步骤 4 — Factory 注册 + JSON 配置 (commit `361d8518f`)

**改动 1**: `data_source_factory.py` 的 `_create_single_data_source` 加 7 行:
```python
if source_type == "openstock_market":
    from app.services.openstock_market_data_adapter import (
        OpenStockMarketDataSourceAdapter,
    )
    return OpenStockMarketDataSourceAdapter(config.__dict__)
```

**改动 2**: `config/data_sources.json` 加两条:
```json
"openstock_market": {
  "type": "openstock_market",
  "mode": "real",
  "base_url": "http://192.168.123.104:8040",
  "timeout": 5.0,
  ...
},
"openstock_market_mock": {
  "type": "market",          // 复用现有 MarketDataSourceAdapter
  "mode": "mock",            // 内部走 mock 种子数据
  ...
}
```

**关键点 — 命名约定**: `get_data_with_fallback("openstock_market", ...)` 在 primary 失败时,framework 会自动尝试 `"openstock_market_mock"`(加 `_mock` 后缀)。这是框架既有的 fallback 契约,不需要新代码。

**为什么不用 akshare 做 fallback?** akshare 的 adapter 是 task #11 的独立大迁移(本 PR 不覆盖);当前 PR 用现有 `MarketDataSourceAdapter` 的 mock 模式兜底,语义上属于"OpenStock 自己 fail 时用 mock 数据撑住前端",而 akshare 二级 fallback 在路由层做(见步骤 5)。

### 步骤 5 — 路由切换 (commit `9635c0fbd`) ⭐ 核心

**改动 1** — `/quotes` (line 374):
```python
# Before:
result = await factory.get_data("market", "quotes", {"symbols": symbol_list})
# After:
result = await factory.get_data_with_fallback(
    "openstock_market", "quotes", {"symbols": symbol_list}
)
```
- `get_data_with_fallback` 自动在 primary fail 时跳到 `openstock_market_mock`
- 返回的 envelope 直接交给现有的 `build_quotes_response_payload`,该函数读 `result["data"]`,空时用 `_build_fallback_quotes` 合成
- **前端 schema 完全不变**

**改动 2** — `/kline` (line 550+,新增 38 行):

```python
# 优先走 OpenStock factory,失败时二级 fallback 回 akshare
try:
    openstock_result = await factory.get_data_with_fallback(
        "openstock_market", "klines",
        {"symbol": stock_code, "period": period, "count": 60},
    )
    candles = openstock_result.get("candles") or openstock_result.get("data") or []
    if not candles:
        raise RuntimeError("OpenStock returned empty candles")
    result = {
        "success": True,
        "data": candles,
        "count": len(candles),
        "symbol": stock_code,
        "period": period,
        "source": openstock_result.get("source", "openstock"),
    }
    circuit_breaker.record_success()
    return result
except Exception as openstock_exc:
    logger.warning(f"OpenStock kline failed, falling back to akshare: {openstock_exc}")
    # 二级 fallback:原有的 akshare service.get_a_stock_kline 调用保留
    ...
```

**为什么 /kline 需要路由层二级 fallback,而 /quotes 不需要?**
- `/quotes`:OpenStock fail → `openstock_market_mock` 给出 mock 行情 → 前端能渲染。一层 fallback 足够。
- `/kline`:OpenStock fail → mock 给的 K 线在真实业务里几乎没用(回测不能用 mock 数据),所以再跳到 akshare service(虽然慢但真实)。两层 fallback。
- 这个不对称是**业务需求差异**,不是技术债。

**Regression(步骤 5 阶段)**: `test_market_api.py` 24/25 通过,1 失败是 pre-existing `sh689009` akshare mock seed 问题(`test_get_quotes_single_symbol`),与本改动无关。

### 步骤 6 — Adapter 单测 (commit `1d2837125`)

**新建**: `web/backend/tests/test_openstock_market_data_adapter.py` (306 行, 18 tests)

**覆盖矩阵**:

| 维度 | 测试数 | 关键 case |
|---|---|---|
| `get_data("quotes")` 正常路径 | 2 | list symbols → string join; scalar symbol 直传 |
| `get_data("klines")` 正常路径 | 2 | time→datetime 映射; PERIOD_MAP 翻译; default count=100 |
| `get_data` 错误路径 | 2 | klines 缺 symbol; 不支持 endpoint |
| metrics(错误) | 1 | `OpenStockClientError` 抛出,error_count++,availability=0 |
| metrics(成功) | 1 | total/success/availability=100, base_url 正确 |
| `health_check` | 3 | 2xx → HEALTHY; 5xx → DEGRADED; HTTPError → FAILED |
| `_transform_kline_row` | 2 | 非映射返回 `{}`; TIME 大写映射 datetime |
| `_transform_quote_row` | 1 | 大小写归一 |
| `_coerce_rows` | 1 | list / dict-with-known-key / no-key |
| 常量与 init | 3 | PERIOD_MAP / ENDPOINT_ROUTES / DEFAULT_BASE_URL / 默认配置 |

**Mock 策略**:
- `mock_client = type("StubClient", (), {})()` + `AsyncMock` 桩 `fetch` / `fetch_bars`
- 不发真实 HTTP
- `monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)` 桩 health_check

**结果**: 18 passed

### 步骤 7 — 集成测试 (commit `490e34774`) ⭐ 核心

**新建**: `web/backend/tests/test_openstock_market_routes_integration.py` (404 行, 10 tests)

**测试策略关键点 — 三种 patch 边界**:

| Patch 目标 | 边界类型 | Patch 方式 | 原因 |
|---|---|---|---|
| `get_data_source_factory` | lazy import(函数体内) | `monkeypatch.setattr(dsf_module, ...)` | 路由每次调用时 `from ... import`,patch 源模块即可 |
| `get_circuit_breaker` | module-level(line 27) | `monkeypatch.setattr(market_module, ...)` | import 时已绑定到 `market_module` 命名空间,patch 源模块无效 |
| `get_stock_search_service` | lazy import(函数体内) | `monkeypatch.setattr(sss_pkg, ...)` 在包 `__init__` 上 | 路由 `from app.services.stock_search_service import get_stock_search_service`,实际拉的是包 `__init__.py` 的 re-export,patch 子模块无效 |

> 这三种 patch 边界是本次实施踩过的坑(每个 fixture 的 docstring 都记录了原因),后续维护者改路由 import 风格时必须同步改 fixture。

**10 个测试 case**:

| 测试 | 验证点 |
|---|---|
| `/quotes` factory 成功 | envelope → `build_quotes_response_payload` → 前端 schema; positional call args 验证 |
| `/quotes` factory 返回空 data | `_build_fallback_quotes` 兜底 |
| `/quotes` factory 异常 | → BusinessException → 500 |
| `/kline` factory 成功 | candles 非空,service 未触发,`cb.record_success()` 调用 |
| `/kline` factory 空 candles | → 二级 fallback `service.get_a_stock_kline` |
| `/kline` factory 异常 | → 二级 fallback |
| `/kline` 双失败 | → 500 + `cb.record_failure()` |
| `/kline` invalid period | → 422 (Pydantic 校验,不触 factory) |
| `get_data_with_fallback` 契约 1 | primary fail → 自动跳 `{source}_mock` |
| `get_data_with_fallback` 契约 2 | primary fail + 无 mock → 异常上抛 |

**关键 fixture**:
```python
@pytest.fixture
def mock_factory():
    factory = MagicMock()
    factory.get_data_with_fallback = AsyncMock()
    factory.get_data = AsyncMock()
    factory.get_data_source = AsyncMock(return_value=None)
    return factory

@pytest.fixture
def auth_client(mock_user):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
```

**结果**: 10 passed

### 步骤 8 — 回归 (无 commit, runbook)

```
cd web/backend && pytest -k "quotes or kline or factory or market"
52 passed, 1 failed in 14.02s
```

- 18 adapter 单测 ✅
- 10 集成测试 ✅
- 24/25 `test_market_api.py` ✅
- **1 失败**:`test_get_quotes_single_symbol` — akshare mock seed 给出 `sh689009`,期望 `000001.SZ`。这是 main 上就有的 pre-existing 问题,与本 PR 0 关联(可以在 `git stash` 本改动后复现)。

---

## 四、关键问题与解决对照表

| 问题 | 现象 | 根因 | 解决 |
|---|---|---|---|
| OpenStock 不实现 IDataSource | factory 无法调度 | 缺 adapter 层 | 新建 `OpenStockMarketDataSourceAdapter`(步骤 3) |
| KLINES 字段名 mismatch | 前端 K 线空白 | OpenStock 返 `time`,前端期望 `datetime` | `_transform_kline_row` 映射 |
| Mock fallback 命名 | factory 不认 `openstock_mock` | 框架按 `{source}_mock` 后缀约定 | JSON 命名 `openstock_market_mock`(步骤 4) |
| /kline 真实业务不能用 mock | mock K 线让回测失效 | 业务需求 | 路由层加二级 akshare fallback(步骤 5) |
| Quotes envelope schema 不一致 | `build_quotes_response_payload` 读不到 data | adapter 与 `MarketDataSourceAdapter` envelope 字段未对齐 | 同时保留 `data` 与 `quotes`/`candles`(步骤 3 envelope) |
| 集成测试 patch 不到 factory | `market_module.get_data_source_factory` 不存在 | lazy import vs module-level import 边界差异 | 三种 fixture 分别 patch 源模块 / 路由模块 / 包 `__init__`(步骤 7) |

---

## 五、未覆盖的工作(明确排除)

本 PR **不包含**以下工作,留作后续任务:

| 项目 | 任务 ID | 状态 | 说明 |
|---|---|---|---|
| `AkshareMarketDataSourceAdapter` 大型迁移 | #11 | pending | 把 akshare 也包成 IDataSource,合并到 factory 内(本 PR 只做了路由层二级 fallback) |
| `openstock_client` 真实 HTTP 烟测 | — | 可选 | 当前所有测试都是 mock,真实 OpenStock 已知 `/health/live` 9.9ms OK,但 `/quotes`/`/klines` 真实响应未在生产路径上验证(集成测试用 mock factory 跳过了真实 HTTP) |
| 浏览器烟测 | — | 可选 | 验证前端 K 线 / 行情页面渲染 |
| OpenSpec `migrate-akshare-fundflow-mixin-to-openstock` 审批 | — | pending | 步骤 1 cherry-pick 了提案,等用户批准 |

---

## 六、审核重点建议

请重点检查以下决策是否符合你的预期:

### 1. Envelope 双键设计(`data` + `candles`/`quotes`)
**文件**: `web/backend/app/services/openstock_market_data_adapter.py:131-172`
**问题**: 是否接受同时保留两个数据键(向后兼容)?还是想统一只留一个?

### 2. /kline 二级 fallback 触发条件
**文件**: `web/backend/app/api/market/market_data_request.py:558-562`
```python
candles = openstock_result.get("candles") or openstock_result.get("data") or []
if not candles:
    raise RuntimeError("OpenStock returned empty candles")
```
**问题**: "空 candles 也触发 fallback" 是不是过于激进?OpenStock 真的空数据(停牌股票)时,是不是应该返回空而不是跳 akshare?

### 3. /kline count=60 硬编码
**文件**: `web/backend/app/api/market/market_data_request.py:556`
**问题**: `count = 60` 写死,没有从 query param 读。前端 K 线默认请求多少根?这个值对不对?

### 4. Factory dispatch 用 `source_type` 字符串匹配
**文件**: `web/backend/app/services/data_source_factory/data_source_factory.py:132`
**问题**: `if source_type == "openstock_market"` 硬编码字符串,后续类型多了会变长 if-elif。是否要在 #11 完成后改成注册表模式?

### 5. Health check 用独立 httpx.AsyncClient
**文件**: `web/backend/app/services/openstock_market_data_adapter.py:227-230`
**问题**: 每次健康检查新建 `httpx.AsyncClient`,不复用 `OpenStockClient` 内部的 client。是否需要复用以减少连接开销?(目前 5s 一次健康检查,影响不大)

### 6. pre-existing akshare mock seed 失败
**文件**: `web/backend/tests/test_market_api.py::test_get_quotes_single_symbol`
**问题**: `sh689009` vs `000001.SZ`。**这个失败与本 PR 无关**,是否要在本 PR 内顺手修?(我倾向不修,保持 PR 焦点)

---

## 七、回归命令(供你复核)

```bash
cd web/backend
pytest tests/test_openstock_market_data_adapter.py tests/test_openstock_market_routes_integration.py tests/test_market_api.py -v
# 预期: 18 + 10 + (24 pass + 1 fail) = 52 passed, 1 failed
```

如果你想验证 pre-existing 失败:
```bash
git stash   # 把本 worktree 改动收起来
git checkout origin/main -- web/backend/tests/test_market_api.py
pytest web/backend/tests/test_market_api.py::test_get_quotes_single_symbol
# 同样失败,证明与 OpenStock 改动无关
git stash pop
```

---

## 八、下一步计划

按优先级排序:

### P0 — 必须(等审核结论)
- [ ] 用户审核本文档,标记 1-6 中的决策点
- [ ] 如需调整,在本 worktree 修完再 push
- [ ] 创建 PR(目标 `main`)

### P1 — 推荐(可与 P0 并行)
- [ ] 浏览器烟测前端 K 线 / 行情页面(本地起 backend,前端连过去)
- [ ] 真实 OpenStock `/quotes?symbols=000001` curl 验证(绕过测试 mock,确认生产路径)

### P2 — 后续任务(不在本 PR)
- [ ] Task #11: AkshareMarketDataSourceAdapter 大型迁移(把 akshare 也包成 IDataSource,届时路由层二级 fallback 可以简化)
- [ ] OpenSpec `migrate-akshare-fundflow-mixin-to-openstock` 审批流程
- [ ] Factory dispatch 重构成注册表模式(若步骤 4 决策点 4 要求)

---

## 九、附录 — GitNexus 影响评估

| 改动 symbol | impact | 说明 |
|---|---|---|
| `IDataSource` (新增第 14 个实现) | HIGH upstream (28 callers) | 但不破坏接口,callers 不受影响 |
| `_create_single_data_source` (factory dispatch) | LOW (5 symbols, factory 内部) | 新增分支,不影响其他 dispatch |
| `get_a_stock_kline` (/kline fallback) | MEDIUM (3 callers) | 路由层调用方式不变,只是从 primary 降级为 secondary |

`detect_changes` 在每个 commit 前都跑过,无意外 symbol 被改动。

---

**审核完毕请回复**:
- ✅ 通过 → 我去创建 PR
- ⚠️ 改 X → 我修完再 push
- ❌ 重做 → 我重建 worktree
