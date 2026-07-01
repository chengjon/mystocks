# B4.014 OpenStock 生产路径烟测审计

**审计人**: Claude (glm-5.2)
**审计日期**: 2026-07-01
**审计对象**: PR #490 (`feat/b4-014-openstock-routes`) 在真实 OpenStock 上的行为
**结论**: ⚠️ **PR 当前状态不应合入 main — 3 个 showstopper + 2 个高优**

---

## 一、烟测环境

- **OpenStock 实例**: `http://192.168.123.104:8040`
- **健康检查**: `/health/live` 9.7ms / 200 OK ✅
- **真实端点**(从 openapi.json 拉取):
  ```
  POST /data/fetch       — 通用类别拉取(REALTIME_QUOTES 等)
  POST /data/bars        — K 线专用
  POST /data/batch       — 批量
  POST /data/snapshot    — 快照
  POST /routing/best     — 最优路由决策
  GET  /sources          — 类别列表(实测 65+ categories)
  GET  /diagnostics      — 缓存/熔断/延迟诊断
  ```
- **adapter 的调用路径**: ✅ 正确(`client.fetch` → POST `/data/fetch`;`client.fetch_bars` → POST `/data/bars`)

---

## 二、5 个发现(按时序)

### 发现 #1 — `symbols` 参数名错误 [SHOWSTOPPER]

**adapter 代码** (`openstock_market_data_adapter.py:155`):
```python
fetch_params["symbols"] = symbols_str  # 复数,逗号分隔
```

**真实 OpenStock 行为**(8 种参数名 probe):
| 参数名 | 类型 | 结果 |
|---|---|---|
| `params.symbols` (string) | `"000001"` | ❌ 50 条全市场热点 |
| `params.symbol` (string) | `"000001"` | ✅ **1 条 sz000001** |
| `params.codes` | `"000001"` | ❌ 50 条 |
| `params.stocks` | `"000001"` | ❌ 50 条 |
| `params.symbols` (list) | `["000001"]` | ❌ 50 条 |
| 顶层 `symbols` / `symbol` | — | ❌ 50 条 |

**结论**: OpenStock `REALTIME_QUOTES` 用 **`symbol`(单数,字符串)**,不是 `symbols`。adapter 当前传的参数被完全忽略。

**生产影响**: 用户在前端查 000001 行情 → 后端走 OpenStock → 拿到 50 条无关热点 → `build_quotes_response_payload` 把它们当合法数据返回 → 前端展示错的股票。

**修复**:
```python
# adapter _fetch_quotes 改为单 symbol 模式
fetch_params["symbol"] = symbols_str  # 单数
# 如果路由传多 symbol,需要循环调用 + 合并,或问 OpenStock 是否支持 list
```

### 发现 #2 — `/quotes` 字段 schema mismatch [SHOWSTOPPER]

**OpenStock 真实字段**(REALTIME_QUOTES):
```
symbol, name, price, pct_chg, change, volume, amount, open, high, low,
prev_close, turnover_rate, pe_dynamic, pb, market_cap, float_market_cap,
bid1_price, bid1_volume, ask1_price, ask1_volume
```

**前端期望字段**(从 `build_quotes_response_payload` / 现有 mock schema):
```
symbol, price, change, change_percent, volume
```

**adapter `_transform_quote_row`** 只做大小写归一,不做字段映射:
```python
return {str(k).lower(): v for k, v in row.items()}
```

**生产影响**:
- 前端 `change_percent` 字段拿不到(OpenStock 给 `pct_chg`)
- 前端可能拿到多余的 `bid1_price` / `pe_dynamic` 等字段(无害但脏)

**修复**:
```python
@staticmethod
def _transform_quote_row(row):
    if not isinstance(row, Mapping):
        return {}
    lowered = {str(k).lower(): v for k, v in row.items()}
    # 字段名映射
    if "pct_chg" in lowered and "change_percent" not in lowered:
        lowered["change_percent"] = lowered["pct_chg"]
    return lowered
```

### 发现 #3 — `/klines` 时间字段是 ISO8601 全时间戳 [HIGH]

**OpenStock 真实返回**:
```json
{"symbol": "sz000001", "time": "2026-06-29T15:00:00+08:00", "open": ..., "period": "day"}
```

**adapter mock 测试用**:
```json
{"time": "2026-06-01", "open": ..., "close": ...}
```

**adapter `_transform_kline_row`** 把 `time` 原样塞 `datetime`:
```python
if key_lower == "time":
    result["datetime"] = value  # "2026-06-29T15:00:00+08:00"
```

**生产影响**: 前端 K 线图组件可能期望 `"2026-06-29"` 短日期,收到 ISO8601 会渲染异常或时区错乱。**需要前端确认**。

**修复**(待与前端对齐):
```python
# 方案 A: 截断到日期
if key_lower == "time":
    result["datetime"] = str(value)[:10]  # "2026-06-29"
# 方案 B: 完整 ISO8601 透传,前端处理
```

### 发现 #4 — 空/错误 symbol 不返回空 [HIGH]

**测试**:
```
POST /data/fetch {"data_category": "REALTIME_QUOTES", "params": {"symbol": "999999"}}
→ 200 OK, 50 条热点(同 symbols=000001 的 fallback 行为)
```

**OpenStock 行为**: 找不到指定 symbol 时,静默 fallback 到全市场热点(50 条 cap)。

**adapter 期望**: 空响应 → 触发 factory fallback → mock 源。

**生产影响**:
- 用户输错股票代码 → 后端拿 50 条热点 → 前端展示错的(同发现 #1)
- factory fallback 永远不会触发
- 路由层 `if not candles` 检查不到空

**修复**(adapter 层):
```python
# adapter _fetch_quotes 收到结果后,过滤出实际请求的 symbol
if symbols_str:
    requested = set(symbols_str.split(","))
    quotes = [q for q in quotes if q.get("symbol") in requested or _normalize(q["symbol"]) in requested]
```

### 发现 #5 — `/klines` symbol 接受裸代码 [OK]

**OpenStock 行为**:
```
POST /data/bars {"symbol": "000001", "period": "day", "count": 3}
→ 200 OK, 3 条,symbol 返回 "sz000001"(加交易所前缀)
```

**adapter 代码** ✅ 正确:
```python
fetch_bars(symbol="000001", period="day", count=3)
```

**唯一小问题**: 返回的 `symbol` 是 `sz000001`,前端可能期望 `000001`。需要在 `_transform_kline_row` 加去前缀逻辑(类似 quotes)。

---

## 三、综合诊断

### 集成测试为什么没发现?

集成测试(`test_openstock_market_routes_integration.py`)用 `MagicMock` 桩 factory,**完全不调用真实 OpenStock**。adapter 单测(`test_openstock_market_data_adapter.py`)桩 `OpenStockClient.fetch`/`fetch_bars`,**也不发真实 HTTP**。

→ **测试覆盖了"adapter 与 OpenStockClient 接口契约",没覆盖"adapter 与真实 OpenStock 行为契约"**。

### PR 当前状态是否应合 main?

**❌ 不应该合**。发现 #1 + #2 是生产 showstopper:用户查行情会拿到错的股票 + 错的字段。CodeWhale 复核也没发现这些(它做的是源码审计,没发真实 HTTP)。

---

## 四、修复方案

### 方案 A — 本 PR 内修复(推荐)

**新增 commit `B4.014-M1m-9: production smoke fixes`**:

1. `_fetch_quotes` 改 `symbol`(单数)+ 过滤逻辑(发现 #1, #4)
2. `_transform_quote_row` 加 `pct_chg → change_percent` 映射(发现 #2)
3. `_transform_kline_row` 处理 ISO8601 时间 + 去 symbol 前缀(发现 #3, #5)
4. 加真实 OpenStock 集成测试(可选,标记 `@pytest.mark.integration`,默认 skip)

**预估**: ~50 行代码改动 + 5-8 个测试 case

### 方案 B — 标记 PR 为 draft,task #53 跟踪

把 PR #490 改 draft 状态,新建 task #53(已建)独立修复,修完再 mark ready。

### 方案 C — 合 main 后立即热修

不推荐 — 一旦合 main,任何人 pull 都会拿到坏行为。

---

## 五、待用户决策

1. **方案 A / B / C**?
2. **发现 #3 的 ISO8601 时间处理**:截断到日期 vs 完整透传 vs 前端处理?
3. **是否需要加真实 OpenStock 集成测试**(标记 `@pytest.mark.integration` skip 默认)?
4. **`/quotes` 多 symbol 支持**:OpenStock 看来不直接支持 `symbol=000001,600519`。要循环调用还是只支持单 symbol?

---

## 六、复现命令

```python
# 在任意能访问 192.168.123.104 的机器
import urllib.request, json
req = urllib.request.Request(
    "http://192.168.123.104:8040/data/fetch",
    data=json.dumps({"data_category": "REALTIME_QUOTES",
                     "params": {"symbol": "000001"}}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
print(json.loads(urllib.request.urlopen(req, timeout=10).read()))
```
