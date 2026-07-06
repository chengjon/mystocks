# S5 OpenStock Adapter 设计文档（M1k/M1m 重建实施依据）

> **日期**：2026-07-01
> **状态**：已与用户确认设计选型，待实施
> **依据**：`main-data-architecture-audit-2026-06-30.md` §9 (v5) S5 拍板
> **范围**：M1k（行情路由接入）+ M1m（合约桥接）一次性设计

---

## 一、目标

把 OpenStock 作为上游 primary 数据源接入 main 的 `data_source_factory` 多源骨架，符合用户方向更正："OpenStock 优先 + 多源保留"。不动 factory 多源骨架框架代码，通过新增 adapter + 配置注册实现。

## 二、关键设计决策（用户已确认）

| 决策点 | 选型 | 理由 |
|---|---|---|
| Adapter 接口契约 | 方案 A：endpoint 路由表内部映射 | `get_data(endpoint, params)` 内部路由到 `OpenStockClient.fetch_bars / fetch` |
| factory 注册策略 | X3 变种：`openstock_market` 独立 source_type | 不污染现有 `MarketDataSourceAdapter`，primary/fallback 语义明确 |
| Fallback 机制 | γ：利用现有 `{source_name}_mock` 约定 | 不动 factory 框架代码，配置层把 `openstock_market_mock` 注册为 `MarketDataSourceAdapter` |
| `/kline` 二级 fallback | 路由层捕获 factory 异常后调 `stock_search_service.get_a_stock_kline`（akshare） | `MarketDataSourceAdapter` 无 `klines` endpoint |

## 三、组件清单

### 3.1 新增文件

| 文件 | 内容 | 行数估算 |
|---|---|---|
| `web/backend/app/services/openstock_market_data_adapter.py` | `OpenStockMarketDataSourceAdapter(IDataSource)` 实现 | ~180 |

### 3.2 修改文件

| 文件 | 改动 | 行数估算 |
|---|---|---|
| `web/backend/app/services/data_source_factory/data_source_factory.py` | `_create_single_data_source` 新增 `source_type == "openstock_market"` 分支 | +5 |
| `config/data_sources.json` | 新增 `openstock_market`（primary）和 `openstock_market_mock`（fallback，type=`market` 复用现有 adapter）两个数据源配置项 | +30 |
| `web/backend/app/api/market/market_data_request.py` | `/quotes` 路由从 `factory.get_data("market", "quotes", ...)` 改为 `factory.get_data_with_fallback("openstock_market", "quotes", ...)`；`/kline` 路由从直连 `stock_search_service` 改为 `factory.get_data_with_fallback("openstock_market", "klines", ...)` + 异常时二级 fallback 到 stock_search_service | +30/-10 |

### 3.3 Cherry-pick 文件（从 B4.014 分支）

| 文件 | 来源 commit | 内容 |
|---|---|---|
| `web/backend/app/services/openstock_client.py` | B4.014 分支 `c31cd51a6` 之前已存在 | OpenStockClient + OpenStockClientConfig + 异常层级 |

## 四、`OpenStockMarketDataSourceAdapter` 设计

### 4.1 类骨架

```python
class OpenStockMarketDataSourceAdapter(IDataSource):
    """OpenStock 市场数据源适配器 - 把 OpenStockClient 接入 data_source_factory"""

    PERIOD_MAP = {"daily": "day", "weekly": "week", "monthly": "month"}
    ENDPOINT_ROUTES = {"quotes": "REALTIME_QUOTES", "klines": "fetch_bars"}

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.source_type = "openstock_market"
        self.name = config.get("name", "OpenStock Market Data Source")
        self._client: Optional[OpenStockClient] = None
        self._metrics = DataSourceMetrics()
        # config 字段: base_url, api_key, timeout_seconds

    async def _get_client(self) -> OpenStockClient:
        if self._client is None:
            self._client = OpenStockClient(OpenStockClientConfig(...))
        return self._client

    async def get_data(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        params = params or {}
        client = await self._get_client()
        try:
            if endpoint == "klines":
                raw = await client.fetch_bars(
                    symbol=params["stock_code"],
                    period=self.PERIOD_MAP.get(params.get("period", "daily"), "day"),
                    count=params.get("count", 60),
                )
                rows = self._transform_klines(raw)
            elif endpoint == "quotes":
                raw = await client.fetch(
                    "REALTIME_QUOTES",
                    params={"symbols": ",".join(params["symbols"]) if isinstance(params.get("symbols"), list) else params.get("symbols", "")},
                )
                rows = self._transform_quotes(raw)
            else:
                raise ValueError(f"Unsupported endpoint: {endpoint}")
            return {"success": True, "data": rows, "source": "openstock", "count": len(rows)}
        except OpenStockClientError as e:
            self._metrics.record_error(str(e))
            raise  # 让 factory 的 _mock fallback 接管
        finally:
            # 不每次 aclose，长连接复用；factory cleanup 时统一 aclose
            pass

    async def health_check(self) -> HealthStatus:
        # 调 OpenStock /health/live
        ...

    def get_metrics(self) -> Dict[str, Any]:
        ...

    def _transform_klines(self, raw: OpenStockFetchResult) -> List[Dict[str, Any]]:
        """OpenStock KLINES 字段 → 前端 KLineRow 期望字段"""
        # time -> datetime, open/high/low/close/volume 直传
        rows = raw.payload.get("bars", []) or raw.payload.get("data", [])
        return [
            {
                "datetime": r.get("time"),
                "open": r.get("open"),
                "high": r.get("high"),
                "low": r.get("low"),
                "close": r.get("close"),
                "volume": r.get("volume"),
            }
            for r in rows
        ]

    def _transform_quotes(self, raw: OpenStockFetchResult) -> List[Dict[str, Any]]:
        """OpenStock REALTIME_QUOTES 字段 → 现有 build_quotes_response_payload 期望"""
        # 字段映射对齐 main build_quotes_response_payload 的输入
        ...
```

### 4.2 endpoint 路由表

| endpoint（路由调） | OpenStock 调用 | 字段映射 |
|---|---|---|
| `quotes` | `client.fetch("REALTIME_QUOTES", params={"symbols": ...})` | OpenStock 标准字段（symbol/price/open/high/low/...）→ 现有 `build_quotes_response_payload` 期望 |
| `klines` | `client.fetch_bars(symbol, period, count=60)` | `time→datetime`，OHLCV 直传 |

### 4.3 错误转换

| OpenStockClient 异常 | adapter 行为 |
|---|---|
| `OpenStockProviderUnavailable` | raise（让 factory fallback 到 `openstock_market_mock` = `MarketDataSourceAdapter`） |
| `OpenStockTimeout` | raise（同上） |
| `OpenStockUnsupportedCategory` | raise ValueError（编程错误，不应 fallback） |
| `OpenStockInvalidResponse` | raise（数据损坏，应让 fallback 接管） |

## 五、factory 注册

### 5.1 `data_source_factory.py` 改动

```python
# 在 _create_single_data_source 中新增
if source_type == "openstock_market":
    return OpenStockMarketDataSourceAdapter(config.__dict__)
```

导入：

```python
from app.services.openstock_market_data_adapter import OpenStockMarketDataSourceAdapter
```

### 5.2 `config/data_sources.json` 新增

```json
"openstock_market": {
  "name": "OpenStock Market Data Source",
  "type": "openstock_market",
  "enabled": true,
  "mode": "real",
  "base_url": "http://192.168.123.104:8040",
  "api_key": "",
  "timeout_seconds": 5.0,
  "health_check_interval": 60.0,
  "fallback_enabled": true,
  "cache_enabled": true,
  "cache_ttl": 10
},
"openstock_market_mock": {
  "name": "OpenStock Market Fallback (MarketDataSourceAdapter)",
  "type": "market",
  "enabled": true,
  "mode": "real",
  "base_url": null,
  "timeout": 30.0,
  "fallback_enabled": false,
  "cache_enabled": true,
  "cache_ttl": 10
}
```

**关键**：`openstock_market_mock` 的 `type` 是 `"market"`，factory 会创建 `MarketDataSourceAdapter` 实例——这就是 fallback 目标。

## 六、路由改动

### 6.1 `/quotes` 路由

**改前**（main 现状）：

```python
result = await factory.get_data("market", "quotes", {"symbols": symbol_list})
```

**改后**：

```python
result = await factory.get_data_with_fallback("openstock_market", "quotes", {"symbols": symbol_list})
# primary: OpenStockMarketDataSourceAdapter.get_data("quotes", ...)
# fallback: 自动跳 openstock_market_mock = MarketDataSourceAdapter.get_data("quotes", ...)
```

### 6.2 `/kline` 路由

**改前**（main 现状，直连 akshare）：

```python
service = get_stock_search_service()
result = service.get_a_stock_kline(symbol=stock_code, period=period, adjust=adjust, start_date=start_date, end_date=end_date)
```

**改后**（OpenStock primary，factory fallback 到 MarketDataSourceAdapter，再二级 fallback 到 stock_search_service）：

```python
try:
    result = await factory.get_data_with_fallback(
        "openstock_market", "klines",
        {"stock_code": stock_code, "period": period, "count": 60}
    )
    # OpenStock 返回字段已映射为 datetime/OHLCV
except Exception as openstock_err:
    # OpenStock 失败 且 MarketDataSourceAdapter 不支持 klines endpoint
    # 二级 fallback: akshare 直连
    logger.warning(f"OpenStock + MarketDataSource fallback both failed for klines: {openstock_err}, falling back to akshare")
    service = get_stock_search_service()
    result = service.get_a_stock_kline(
        symbol=stock_code, period=period, adjust=adjust,
        start_date=start_date, end_date=end_date,
    )
    # akshare 中文列名 → 前端 KLineRow 字段映射在 stock_search_service 内部已做
```

## 七、Cherry-pick `openstock_client.py`

从 B4.014 分支 cherry-pick `web/backend/app/services/openstock_client.py`（约 315 行）：

```bash
git cherry-pick <commit-that-introduced-openstock_client>
# 或直接 git checkout feat/b4-014-milestone -- web/backend/app/services/openstock_client.py
```

**前置条件**：`httpx==0.27.0` 已在 `requirements.txt` 第 53 行声明（审计 §5.6 已验证）。

## 八、测试策略（M1m 范围）

### 8.1 单测（新增）

| 测试文件 | 覆盖 |
|---|---|
| `tests/test_openstock_market_data_adapter.py` | `get_data("quotes")`、`get_data("klines")`、`_transform_klines` 字段映射（time→datetime）、`_transform_quotes`、health_check、4 种异常分支 |

### 8.2 复用现有测试

- `tests/test_openstock_client.py`（10 个 coroutine 测试）—— 已覆盖 OpenStockClient 本体
- `tests/test_data_adapter_regression.py` —— 运行确认 `MarketDataSourceAdapter` fallback 不被破坏
- `tests/test_data_api_regression.py` —— 运行确认 `/quotes` API 响应 schema 不变

### 8.3 集成测试

新增 `tests/test_market_routes_openstock_integration.py`：
- `/quotes` 走 OpenStock primary → 200
- `/quotes` OpenStock down → fallback 到 MarketDataSourceAdapter → 200
- `/kline` 走 OpenStock primary → 200，响应字段含 `datetime/open/high/low/close/volume`
- `/kline` OpenStock down → 二级 fallback 到 stock_search_service → 200

## 九、实施顺序（按依赖）

| 步骤 | 任务 | 预估 | 阻塞 |
|---|---|---|---|
| 1 | cherry-pick `openstock_client.py` | 0.5h | 无 |
| 2 | 新建 `OpenStockMarketDataSourceAdapter` | 3–5h | 步骤 1 |
| 3 | factory 注册 + `config/data_sources.json` | 1h | 步骤 2 |
| 4 | `/quotes` 路由改 | 0.5h | 步骤 3 |
| 5 | `/kline` 路由改 + 二级 fallback | 1h | 步骤 3 |
| 6 | 单测（adapter） | 2h | 步骤 2 |
| 7 | 集成测试 | 1–2h | 步骤 4/5 |
| 8 | 回归（运行现有测试套件） | 0.5h | 步骤 7 |
| **合计** | | **9.5–12h** | |

## 十、验收标准

1. ✅ `/quotes` primary 走 OpenStock，HTTP 200 返回有效行情
2. ✅ `/quotes` OpenStock 服务停时自动 fallback 到 MarketDataSourceAdapter，HTTP 200
3. ✅ `/kline` primary 走 OpenStock，HTTP 200 返回字段含 `datetime/open/high/low/close/volume`
4. ✅ `/kline` OpenStock + MarketDataSource 双失败时二级 fallback 到 akshare，HTTP 200
5. ✅ `test_openstock_market_data_adapter.py` 全绿
6. ✅ `test_data_adapter_regression.py`、`test_data_api_regression.py`、`test_openstock_client.py` 全绿
7. ✅ factory `get_available_sources()` 包含 `openstock_market` 和 `openstock_market_mock`

## 十一、未覆盖（独立 PR）

- M1n Playbook 重新定义（"非 OpenStock adapter 必须在 factory 注册并标记为 fallback"）
- Wave 0 FundFlowMixin（FundFlow 域独立于行情域）
- `/health/ready` 超时根因诊断
- handoff 文档错误修订（§4.1 表）
