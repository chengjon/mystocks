# B4.014 OpenStock 生产路径烟测审计

**审计人**: Claude (glm-5.2)
**审计日期**: 2026-07-01
**审计对象**: PR #490 (`feat/b4-014-openstock-routes`) 在真实 OpenStock 上的行为
**结论**: ⚠️ **PR 当前状态不应合入 main — 2 个 showstopper + 2 个高优**

> 📝 **2026-07-01 修订**:本文档吸收第三方审核意见(`B4_014_OPENSTOCK_PROD_AUDIT_REVIEW_2026-07-01.md`)做了 5 处改进:发现 #5 标签从 `[OK]` 改为 `[LOW]`;CodeWhale 归因精确化;task #53 加上 GitHub Issue 定位;工作量估算细化;新增第七节「修复后复验计划」。同时在第二轮 probe 中更正了发现 #4 的实际机制(非"静默 fallback",而是 adapter 用错参数触发的副作用)。

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
| `params.symbols` (string) | `"000001"` | ❌ 50 条全市场热点(`sh689009` 等,完全无关) |
| `params.symbol` (string) | `"000001"` | ✅ **1 条 sz000001** |
| `params.codes` | `"000001"` | ❌ 50 条 |
| `params.stocks` | `"000001"` | ❌ 50 条 |
| `params.symbols` (list) | `["000001"]` | ❌ 50 条 |
| 顶层 `symbols` / `symbol` | — | ❌ 50 条 |

**结论**: OpenStock `REALTIME_QUOTES` 用 **`symbol`(单数,字符串)**,不是 `symbols`。adapter 当前传的参数被完全忽略 → OpenStock 视为"未传 symbol" → 返回默认 50 条热点。

**生产影响**: 用户在前端查 000001 行情 → 后端走 OpenStock → 拿到 50 条无关热点 → `build_quotes_response_payload` 把它们当合法数据返回 → 前端展示错的股票。

**修复**:
```python
# adapter _fetch_quotes 改为单 symbol 模式
fetch_params["symbol"] = symbols_str  # 单数
# 路由层当前传 ["000001"] 列表形态 — 见发现 #1 的"调用方确认"
```

**调用方确认**:路由层 `market_data_request.py` 当前 `symbol_list = ["000001"]` 或 `["000001", "600519"]`,adapter 收到 list 时需要循环调用(每次单 symbol)或仅取第一个,见决策点 #4。

### 发现 #2 — `/quotes` 字段 schema mismatch [SHOWSTOPPER]

**OpenStock 真实字段**(REALTIME_QUOTES,20 字段):
```
symbol, name, price, pct_chg, change, volume, amount,
open, high, low, prev_close, turnover_rate, pe_dynamic, pb,
market_cap, float_market_cap, bid1_price, bid1_volume,
ask1_price, ask1_volume
```

**前端 quotes 消费者字段**(`build_quotes_response_payload` + `_build_fallback_quotes` + `marketAdapter.ts` + `Realtime.vue`):
```
symbol, name, price, change, change_percent, volume, amount
```

**字段对照表**:

| OpenStock 字段 | 前端期望字段 | 状态 |
|---|---|---|
| `symbol` (`sz000001`) | `symbol` (`000001`) | ⚠️ 需去前缀(见发现 #5) |
| `name` | `name` | ✅ |
| `price` | `price` | ✅ |
| `pct_chg` | **`change_percent`** | ❌ **缺映射** |
| `change` | `change` | ✅ |
| `volume` | `volume` | ✅ |
| `amount` | `amount` | ✅ |
| `open/high/low` | — | 🟢 可透传,无害 |
| `prev_close` | — | 🟢 可透传,无害 |
| 其他(`turnover_rate` 等) | — | 🟢 可透传,无害 |

**adapter `_transform_quote_row`** 只做大小写归一,不做字段映射:
```python
return {str(k).lower(): v for k, v in row.items()}
```

**生产影响**:前端 `change_percent` 字段拿不到(OpenStock 给 `pct_chg`) → 涨跌幅展示为空。

**修复**:
```python
@staticmethod
def _transform_quote_row(row):
    if not isinstance(row, Mapping):
        return {}
    lowered = {str(k).lower(): v for k, v in row.items()}
    # 字段名映射(OpenStock → 前端期望)
    if "pct_chg" in lowered and "change_percent" not in lowered:
        lowered["change_percent"] = lowered["pct_chg"]
    # symbol 去前缀(见发现 #5)
    sym = lowered.get("symbol")
    if isinstance(sym, str) and len(sym) >= 8 and sym[:2] in ("sz", "sh", "bj") and sym[2:].isdigit():
        lowered["symbol"] = sym[2:]
    return lowered
```

### 发现 #3 — `/klines` 时间字段是 ISO8601 全时间戳 [HIGH]

**OpenStock 真实返回**:
```json
{"symbol": "sz000001", "time": "2026-06-30T15:00:00+08:00", "open": ..., "period": "day"}
```

**adapter mock 测试用**:
```json
{"time": "2026-06-01", "open": ..., "close": ...}
```

**adapter `_transform_kline_row`** 把 `time` 原样塞 `datetime`:
```python
if key_lower == "time":
    result["datetime"] = value  # "2026-06-30T15:00:00+08:00"
```

**前端消费者**:`marketKlineData.ts` `extractKlineRows` 用 `Date.parse(value)` 解析 datetime。`Date.parse` 在主流浏览器支持 ISO8601,但**会做 UTC 时区转换**,可能导致 `2026-06-30T15:00:00+08:00` 在某些 timezone 设置下偏移到 `2026-06-30` 或 `2026-07-01`。

**生产影响**:K 线图日期可能错位一天,**取决于前端日期解析库与浏览器 timezone**。

**修复**(待与前端确认决策点 #2):
```python
# 方案 A(推荐): adapter 层截断到日期,前端无感知
if key_lower == "time":
    sval = str(value)
    result["datetime"] = sval[:10]  # "2026-06-30"
# 方案 B: 完整 ISO8601 透传,前端处理
```

### 发现 #4 — 空/错误 symbol 不返回空 [HIGH]

> 📝 **2026-07-01 第二轮 probe 更正**:第一版审计误以为 OpenStock 对错 symbol "静默 fallback 到 50 条热点"。第二轮 probe 确认:50 条热点是**发现 #1 的副作用**(adapter 用错 `symbols` 复数参数 → OpenStock 视为未传 symbol → 返热点)。修了 #1 后,OpenStock 对错 symbol 的真实行为是 **503 provider_unavailable**,对空 symbol 是 **0 条空列表**,均不会返热点。

**OpenStock 真实行为**(用对的 `symbol` 单数后):
| 输入 | 行为 |
|---|---|
| `symbol="000001"` (合法) | ✅ 1 条 `sz000001` |
| `symbol="999999"` (非法) | ❌ 503 `provider_unavailable: invalid code` |
| `symbol=""` (空串) | ✅ 0 条空列表 |
| `params={}` (无 symbol 字段) | ✅ 0 条空列表 |

**修复 #1 后的实际影响**:
- 用户输错代码(如 999999) → OpenStock 返 503 → adapter 抛异常 → factory 跳 mock 源 → mock 源 `_build_fallback_quotes` 用 fallback 行情返
- 这个链路是**可接受的**(factory fallback 设计目的就是这个)

**所以发现 #4 的修复变成**:确认 #1 修了之后,异常路径触发 mock fallback 是否符合产品预期。**不需要在 adapter 加 client-side filter**(原审计建议已废)。

**唯一保留的轻微修复**:adapter 收到 503 时,异常应携带"symbol 不存在"语义,便于 mock fallback 决策。当前 `OpenStockProviderUnavailable` 异常已经包含足够信息,无需额外改。

### 发现 #5 — symbol 前缀 `sz000001` vs `000001` [LOW]

> 📝 **标签修订**:第一版标 `[OK]` 但正文说"需要改",矛盾。改为 `[LOW]` —— 不改也能用(OpenStock 接受 bare code),但返回的 `symbol` 带前缀,前端展示不一致。

**OpenStock 行为**:
```
POST /data/bars {"symbol": "000001", "period": "day", "count": 3}
→ 200 OK, 3 条,symbol 返回 "sz000001"(加交易所前缀)
```

**adapter 代码** ✅ 输入侧正确:
```python
fetch_bars(symbol="000001", period="day", count=3)  # bare code 可接受
```

**问题在输出侧**:返回的 `symbol` 是 `sz000001`,前端可能期望 `000001`。

**修复**(安全的去前缀,避免 `lstrip` 误剥):
```python
@staticmethod
def _strip_exchange_prefix(symbol_value):
    """去掉 sz/sh/bj 前缀,带校验。避免 lstrip 误剥 sh 开头的合法代码。"""
    if not isinstance(symbol_value, str):
        return symbol_value
    if len(symbol_value) >= 8 and symbol_value[:2] in ("sz", "sh", "bj") and symbol_value[2:].isdigit():
        return symbol_value[2:]
    return symbol_value
```

应用在 `_transform_kline_row` 和 `_transform_quote_row` 两处。

---

## 三、综合诊断

### 集成测试为什么没发现?

集成测试(`test_openstock_market_routes_integration.py`)用 `MagicMock` 桩 factory,**完全不调用真实 OpenStock**。adapter 单测(`test_openstock_market_data_adapter.py`)桩 `OpenStockClient.fetch`/`fetch_bars`,**也不发真实 HTTP**。

→ **测试覆盖了"adapter 与 OpenStockClient 接口契约",没覆盖"adapter 与真实 OpenStock 行为契约"**。

### CodeWhale 复核为什么也没发现?

CodeWhale 的源码审计验证了 **adapter ↔ OpenStockClient 的接口契约对齐**(方法签名、参数传递、字段归一),但未覆盖 **adapter ↔ 真实 OpenStock 的运行时行为契约**(参数名 `symbol` vs `symbols`、字段名 `pct_chg` vs `change_percent`、ISO8601 时间戳格式)——这正是本次烟测补上的缺口。源码审计无法替代 runtime 烟测,两者是互补关系。

### PR 当前状态是否应合 main?

**❌ 不应该合**。发现 #1 + #2 是生产 showstopper:用户查行情会拿到错的股票 + 错的字段。

---

## 四、修复方案

### 方案 A — 本 PR 内修复(推荐) ✅ 已采纳

**新增 commit `B4.014-M1n: production smoke fixes`**:

1. `_fetch_quotes` 改 `symbol`(单数)(发现 #1)
2. `_transform_quote_row` 加 `pct_chg → change_percent` 映射 + symbol 去前缀(发现 #2, #5)
3. `_transform_kline_row` 处理 ISO8601 时间(`[:10]` 截断)+ 去 symbol 前缀(发现 #3, #5)
4. 加真实 OpenStock 集成测试(标记 `@pytest.mark.integration`,默认 skip)
5. ~~client-side filter for 50-hot fallback~~ (作废,见发现 #4 更正)

**预估工作量**(细化):
- adapter 核心修复(3 个 transform 方法):~40 行
- 真实集成测试 fixture + skip 逻辑:~50 行
- 多 symbol 边界处理(决策点 #4):~20-30 行(取决于方案)
- 总计:~110-120 行代码 + 8-10 个测试 case

### 方案 B — 标记 PR 为 draft,task #53 跟踪

把 PR #490 改 draft 状态,**GitHub Issue #53**(本仓库 task tracker,见 `TASK.md` §53)独立修复,修完再 mark ready。

### 方案 C — 合 main 后立即热修

不推荐 — 一旦合 main,任何人 pull 都会拿到坏行为。

---

## 五、待用户决策(已决策)

1. ✅ **方案 A / B / C** → **A** (审核建议 + 用户确认)
2. ✅ **发现 #3 的 ISO8601 时间处理** → **方案 A(adapter 层 `[:10]` 截断到日期)**,前端无感知最稳
3. ✅ **是否需要加真实 OpenStock 集成测试** → **是**,标记 `@pytest.mark.integration` skip 默认,提供 `OPENSTOCK_BASE_URL` 环境变量激活
4. ✅ **`/quotes` 多 symbol 支持** → **adapter 层循环调用**(每次单 symbol,合并结果),保留前端多 symbol 入参契约不变

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

---

## 七、修复后复验计划

修完代码后,跑以下 probe 矩阵确认 5 个 fixes 都生效。每个 probe 都必须有"修复前 vs 修复后"的对比。

### Probe 1: 发现 #1 — symbol 参数名

```python
# 修复前: 50 条热点
# 修复后: 1 条 sz000001
probe("/data/fetch",
       {"data_category":"REALTIME_QUOTES","params":{"symbol":"000001"}},
       "should return 1 sz000001")
```
**验收**: count == 1 且 `data[0].symbol == "sz000001"`

### Probe 2: 发现 #2 — change_percent 字段

```python
# 修复前: result.quotes[0] 没有 change_percent 字段
# 修复后: 有 change_percent 字段(值来自 pct_chg)
```
**验收**: `quotes[0]["change_percent"]` 存在且为数字

### Probe 3: 发现 #3 — ISO8601 截断

```python
# 修复前: candles[0].datetime == "2026-06-30T15:00:00+08:00"
# 修复后: candles[0].datetime == "2026-06-30"
```
**验收**: `len(candles[0]["datetime"]) == 10`

### Probe 4: 发现 #4 — 错 symbol 行为

```python
# 修复后: symbol=999999 → 503 provider_unavailable → factory 跳 mock fallback
# 验收链路:factory mock 返回 _build_fallback_quotes 合成行情
```
**验收**: 路由层收到 mock 源的 fallback 行情,前端能渲染

### Probe 5: 发现 #5 — symbol 去前缀

```python
# 修复前: quotes[0].symbol == "sz000001"
# 修复后: quotes[0].symbol == "000001"
```
**验收**: 路由层返回的 quotes[0].symbol 不带 `sz/sh/bj` 前缀

### 集成测试

```bash
cd web/backend
set -a && source /opt/claude/mystocks_spec/.env && set +a

# 单测 + 集成测试(无真实 HTTP)
python -m pytest tests/test_openstock_market_data_adapter.py \
                 tests/test_openstock_market_routes_integration.py \
                 -p no:libtmux --no-cov -n 0

# 真实 OpenStock 集成测试(可选)
OPENSTOCK_BASE_URL=http://192.168.123.104:8040 \
python -m pytest tests/test_openstock_real_integration.py \
                 -p no:libtmux --no-cov -n 0 -m integration
```
