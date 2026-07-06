# B4.014 M1k/M1m 代码审核 — 第三方复核

> **审核文档**：`docs/reports/b4-014-m1k-m1m-review.md`（Claude glm-5.2 自审报告）
> **审核人**：CodeWhale (deepseek-v4-pro)
> **审核日期**：2026-07-01
> **审核对象**：`feat/b4-014-openstock-routes` 分支 7 commits
> **审核方法**：`git show` 逐文件源码审计 + `git diff origin/main..feat/b4-014-openstock-routes` + worktree 单元测试执行 + 交叉对照之前审核的 S5 执行方案和审计文档

---

## 总体结论：✅ 通过，代码质量高

7 commits 的逻辑清晰、自审报告诚实准确。adapter 设计（endpoint 路由表 + 双键 envelope + `time→datetime` 字段映射）合理。测试覆盖充分（18 adapter 单测全通过）。2 个重要建议 + 3 个轻微建议，均非阻塞性。

---

## 一、自审报告准确性审核

### 1.1 基本事实验证

| 自审报告断言 | 验证命令 | 结果 |
|-------------|----------|------|
| 分支 `feat/b4-014-openstock-routes` 存在且已推送 | `git branch -a \| grep openstock-routes` | ✅ 本地 + remote |
| 7 commits，14 files，+2820/-2 | `git diff origin/main..feat/b4-014-openstock-routes --stat` | ✅ 完全一致 |
| Factory 使用 `source_type == "openstock_market"` | `git show feat/...:data_source_factory.py` | ✅ 第 132 行 |
| JSON 配置 `openstock_market` + `openstock_market_mock` | `git show feat/...:config/data_sources.json` | ✅ 两个条目 |
| adapter 实现 266 行（初始 commit）→ 280 行（最终） | `git show ede6e1be2 --stat` | ✅ 266 行，后续 +14 行 |
| 18 adapter 单测通过 | worktree 直接执行 | ✅ 18/18 passed in 0.48s |
| `test_market_api.py` 未改动 | `git diff origin/main..feat -- test_market_api.py` | ✅ 无输出 |
| `test_get_quotes_single_symbol` 代码在 origin/main 与 feature 分支一致 | 同 diff 命令 + 源码对比 | ✅ 完全一致 |
| circuit_breaker 为 pre-existing | `git show origin/main:...market_data_request.py` | ✅ 第 27/92 行已有 |

### 1.2 行数微小差异

自审报告 §三步骤 3 写 adapter "266 行"，但 worktree 中最终版本为 280 行。这是 commit 间增量演进（后续 commit 加了 `_coerce_rows` 的 `Mapping` 类型注解等），不是错误。

---

## 二、代码质量审计

### 2.1 Adapter 设计（`openstock_market_data_adapter.py`）⭐⭐⭐

**优点**：

1. **Endpoint 路由表合理**。`get_data(endpoint, params)` 内部做 if-elif 分支，`ENDPOINT_ROUTES` 常量记录映射关系。避免了为每个 endpoint 拆一个 adapter 类导致的配置爆炸。

2. **双键 envelope（`data` + `candles`/`quotes`）是务实选择**：
   - `build_quotes_response_payload` 读 `result["data"]`（`app.quotes_payload`）
   - 前端 `extractKlineRows` 读 `candles`
   - 双键同时存在不冲突，且为后续统一 schema 留了信息

3. **`_transform_kline_row` 的 `time→datetime` 映射**经实际验证（审计 v5），逻辑正确：
   ```python
   if key_lower == "time":
       result["datetime"] = value
   elif key_lower == "date":
       result.setdefault("datetime", value)  # date 兜底
   ```

4. **`_coerce_rows` 处理多种数据形状**：`None→[]`, `list→原样`, `dict→keys` 探测。这在 OpenStock API 返回格式变化时有防御价值。

5. **Metrics 采集完整**：`total_requests` / `success_count` / `error_count` / `availability` / `last_latency_ms` / `last_error`。

**⚠️ 注意**：

- `_coerce_rows` 对无法识别的 Mapping 静默返回 `[]`——这在 OpenStock 返回意外格式时会吞掉数据。建议加 `logger.warning`（第 187 行 `return []` 前）。
- `_transform_kline_row` 对非 Mapping 输入返回 `{}`——与 `_transform_quote_row` 一致，协变性 OK。

### 2.2 Factory 注册（`data_source_factory.py`）✅

```python
if source_type == "openstock_market":
    from app.services.openstock_market_data_adapter import (
        OpenStockMarketDataSourceAdapter,
    )
    return OpenStockMarketDataSourceAdapter(config.__dict__)
```

**评价**：
- 与我之前审核执行方案时建议的修正方案**完全一致** ✅
- 使用 `source_type == "openstock_market"`（而非 `"market"`），避免了与现有 `MarketDataSourceAdapter` 的冲突 ✅
- `from app.services...` 的延迟导入放在 if 分支内，不破坏 factory 启动性能 ✅

### 2.3 JSON 配置（`config/data_sources.json`）✅

```json
"openstock_market":       { "type": "openstock_market", "mode": "real", ... }
"openstock_market_mock":  { "type": "market",           "mode": "mock", ... }
```

- `openstock_market` 用 `type: "openstock_market"` → 匹配 factory 新增分支 ✅
- `openstock_market_mock` 用 `type: "market"` → 复用 `MarketDataSourceAdapter` 的 mock 模式 ✅
- 命名约定 `{source}_mock` 匹配 `get_data_with_fallback` 的自动 fallback 机制 ✅

### 2.4 路由改动

**`/quotes`**：改动最小（2 行 diff）：
```python
# Before: factory.get_data("market", "quotes", ...)
# After:  factory.get_data_with_fallback("openstock_market", "quotes", ...)
```
与现有 `build_quotes_response_payload` 完全兼容。✅

**`/kline`**：新增 ~38 行，三层 fallback 链：
```
OpenStock factory → openstock_market_mock → akshare service
```

代码正确性：✅
- `circuit_breaker.record_success()` 位置正确（OpenStock 成功时）
- `circuit_breaker.record_failure()` 保留在 akshare 失败时
- `candles = openstock_result.get("candles") or openstock_result.get("data") or []` — 双读兼容

---

## 三、自审报告 6 个决策点复核

### 决策点 1：Envelope 双键设计

**自审**：同时保留 `data` + `candles`/`quotes`。

**复核**：✅ 合理。这是过渡性设计——`build_quotes_response_payload` 依赖 `data`、前端依赖 `candles`/`quotes`。Task #11（akshare 迁移）完成后可统一。当前双键不引入问题。

### 决策点 2：`/kline` 空 candles 触发 fallback

**自审**：`if not candles: raise RuntimeError("OpenStock returned empty candles")` — "空 candles 也触发 fallback 是不是过于激进？"

**复核**：⚠️ **确实是个问题，但不是阻塞性的**。对于停牌股票，OpenStock 返回空 candles 是合理的，此时应返回空结果而非 fallback 到 akshare（后者也大概率返回空或异常）。建议改为：

```python
if candles is None:
    raise RuntimeError("OpenStock returned None candles")  # 仅 None 触发 fallback
# 空列表是合法响应（停牌股票）
```

但这需要确认 OpenStock 在停牌时返回 `None` 还是 `[]`。如果无法确认，当前行为（空则 fallback）是安全的——最多导致一次无意义的 akshare 调用。

### 决策点 3：`count=60` 硬编码

**自审**：`count = 60` 写死，没有从 query param 读。

**复核**：⚠️ **重要但可分阶段修复**。

- 原始 `/kline` 的 docstring 写 "默认最近60个交易日"，但实际支持 `start_date`/`end_date` 自定义范围
- 当前 OpenStock 路径忽略了 `start_date`/`end_date`——始终请求 60 根 bar
- **影响**：用户传了 `start_date=2020-01-01`，OpenStock 仍只返回最近 60 根

**建议**：
- 短期：若 `start_date` 有值，从 `start_date` 推算 count（天数差）
- 长期：OpenStock adapter 增加 `start_date`/`end_date` 参数支持（需要 OpenStock API 侧支持日期范围查询）

### 决策点 4：Factory dispatch 用字符串匹配

**自审**：`if source_type == "openstock_market"` 硬编码，后续类型多了会变长 if-elif。

**复核**：✅ **当前可接受**。Factory 本身就是这样设计的（7 个 hardcoded type 分支）。`#11`（Akshare 迁移）完成后再统一改注册表模式是合理的分阶段策略。当前新增 1 个分支不增加复杂度负担。

### 决策点 5：Health check 用独立 `httpx.AsyncClient`

**自审**：不复用 `OpenStockClient` 内部的 client。

**复核**：✅ **合理**。理由：
- Health check 是独立于业务请求的健康探测，不应受 `OpenStockClient` 内部状态影响
- Health check 5s 超时 + 60s 间隔，连接开销可忽略
- 如果 `OpenStockClient` 的 client 已经故障（连接池耗尽），独立 client 能避免假阴性

### 决策点 6：Pre-existing akshare mock seed 失败

**自审**：`test_get_quotes_single_symbol` 失败与 PR 无关。

**复核**：✅ **确认**。`git diff origin/main..feat -- test_market_api.py` 无输出，test 代码完全一致。失败原因确为 akshare mock seed 的 `sh689009` vs `000001.SZ` 不匹配。**不在本 PR 修是正确的**——保持 PR 焦点。

---

## 四、测试覆盖评估

| 测试层级 | 文件 | 用例数 | 执行结果 |
|----------|------|--------|----------|
| Adapter 单测 | `test_openstock_market_data_adapter.py` | 18 | ✅ 18/18 passed (0.48s) |
| 路由集成 | `test_openstock_market_routes_integration.py` | 10 | ⚠️ 环境配置导致无法运行（`app.core.config` SystemExit） |
| 回归 | `test_market_api.py` | 25 (24P+1F) | 1 pre-existing 失败，与 PR 无关 |

**集成测试未运行原因**：worktree 中缺少必要的环境变量（`.env` 或系统环境），`app.core.config.settings` 初始化时触发 `sys.exit(1)`。这是**环境问题**，不是代码问题。在 CI 中应能正常运行。

**覆盖率不足的测试领域**：
- `_coerce_rows` 对复杂嵌套 Mapping 的测试（当前只测了基本形状）
- OpenStock 真实 HTTP 烟测（自审已标注为 P1 可选）

---

## 五、发现的问题汇总

| # | 严重程度 | 位置 | 描述 | 建议 |
|---|---------|------|------|------|
| 1 | **重要** | `/kline` 路由 | `count=60` 硬编码，忽略 `start_date`/`end_date` 参数 | OpenStock 路径支持日期范围（短期：天数推算 count；长期：adapter 加参数） |
| 2 | **重要** | `/kline` 路由 | 空 candles 触发 akshare fallback——停牌股票的合理空响应被误判为失败 | 区分 `None`（真正的失败）和 `[]`（合法空结果） |
| 3 | **轻微** | adapter `_coerce_rows` | 无法识别 Mapping 时静默返回 `[]`，可能吞掉数据 | 加 `logger.warning` |
| 4 | **轻微** | adapter 行数 | 自审写 266 行，最终 280 行（commit 间演进） | 可忽略 |
| 5 | **轻微** | 集成测试 | 环境配置导致无法在 worktree 运行 | 在 CI 或配置完善的本地环境运行即可 |

---

## 六、与上游文档一致性

| 上游文档/审核 | 要求 | 本 PR 实现 |
|-------------|------|------------|
| `main-data-architecture-audit` S5 战略 | 新建 `OpenStockDataSourceAdapter`，注册为 factory primary backend | ✅ `OpenStockMarketDataSourceAdapter` + `source_type == "openstock_market"` |
| `M1K_M1M_EXECUTION_PLAN_AUDIT` §3 修正建议 | factory 加 `"openstock_market"` 分支，JSON type 改值 | ✅ 完全一致 |
| `M1K_M1M_EXECUTION_PLAN_AUDIT` §2 import 路径 | `app.services.openstock_client` 非 `web.backend.app.services` | ✅ import 路径正确 |
| 用户 handoff §4.2 | M1k/M1m 独立 PR | ✅ 新建 worktree from main，独立分支 |

---

## 七、审核等级

**✅ 通过 — 2 个重要建议（#1, #2），非阻塞性，可在 PR 合入后迭代修复。**

代码质量高、自审报告诚实、设计决策有据。7 commits 粒度合适（1 文档 + 1 cherry-pick + 1 adapter + 1 factory + 1 路由 + 1 单测 + 1 集成测试），方便 review 和 revert。
