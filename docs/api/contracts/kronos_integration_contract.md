# Kronos Integration Contract

> 范围：本文件只描述 MyStocks 暴露给调用方的 Kronos 代理契约，以及 MyStocks 对外部 Kronos 服务的消费约束。

## Endpoints

### `POST /api/v1/kronos/predict`

用途：

- 让 MyStocks 将标准化后的 OHLCV 历史序列提交给 Kronos 做未来 K 线预测

支持两种输入模式：

1. 直接提供 `candles`
2. 提供 `symbol`，由 MyStocks 先从本地日线读取，再转发给 Kronos

本地取数模式支持：

- `symbol + lookback (+ end_date)`
- `symbol + start_date + end_date`

主要限制：

- `candles <= 2048`
- `pred_len <= 120`
- `sample_count <= 10`
- `period` 目前只支持 `day` / `daily`

关键响应字段：

- `data.predictions`
- `data.confidence`
- `data.meta.model`
- `data.meta.device`
- `data.meta.degraded`
- `data.meta.cached`
- `data.meta.latency_ms`
- `data.meta.queue_wait_ms`

### `POST /api/v1/kronos/encode`

用途：

- 让 MyStocks 将历史 K 线编码成 Kronos token 序列

支持模式：

1. 直接提供 `candles`
2. 提供 `symbol` 走本地日线取数

关键响应字段：

- `data.s1_tokens`
- `data.s2_tokens`
- `data.reconstruction_error`
- `data.meta.degraded`
- `data.meta.cached`

### `GET /api/v1/kronos/status`

用途：

- 让前端、运维页或脚本通过 MyStocks 获取外部 Kronos 服务状态

关键响应字段：

- `data.health`
- `data.active_model`
- `data.loaded_models`
- `data.queue_depth`
- `data.requests_inflight`
- `data.version`
- `data.meta.device`
- `data.meta.degraded`
- `data.meta.latency_ms`

## Request Rules

### Canonical candle schema

每根 candle 使用以下字段：

- `timestamp`
- `open`
- `high`
- `low`
- `close`
- `volume`
- `amount`

规则：

- `timestamp` 统一为 ISO 8601 UTC
- `volume` 缺失时按 `0` 处理
- `amount` 缺失时由 MyStocks 以 `(open + high + low + close) / 4 * volume` 估算

### Local data mode rules

当不直接传 `candles` 时：

- 必须提供 `symbol`
- `period` 只能是 `day` 或 `daily`
- 若提供 `start_date`，则必须同时提供 `end_date`
- 若使用 `start_date + end_date` 范围模式，不允许再自定义 `lookback`

## Error Mapping

MyStocks 统一返回 `UnifiedResponse`。

### 404

场景：

- MyStocks 在本地找不到请求所需的日线数据

典型错误码：

- `KRONOS_LOCAL_DATA_NOT_FOUND`

### 422

场景：

- 请求参数在 MyStocks 侧校验失败
- 或外部 Kronos 返回客户端级错误

典型错误码：

- `VALIDATION_ERROR`
- `PARAM_ERROR`
- `MODEL_NOT_FOUND`

### 503

场景：

- 外部 Kronos 超时、不可用或网络失败

典型错误码：

- `TIMEOUT`
- `SERVICE_DOWN`
- `QUEUE_FULL`
- `GPU_ERROR`
- `KRONOS_BASE_URL_MISSING`

## Example: Predict By Date Range

```json
{
  "request_id": "predict-range-001",
  "model": "small",
  "symbol": "600519",
  "period": "day",
  "start_date": "2026-04-01",
  "end_date": "2026-04-17",
  "pred_len": 10,
  "sample_count": 1,
  "top_p": 0.9,
  "temperature": 1.0
}
```

## Example: Predict Success

```json
{
  "success": true,
  "code": 200,
  "message": "Kronos forecast completed",
  "data": {
    "predictions": [
      {
        "timestamp": "2026-04-17T10:00:00+00:00",
        "open": 10.4,
        "high": 10.6,
        "low": 10.2,
        "close": 10.5,
        "volume": 120000.0,
        "amount": 1250000.0
      }
    ],
    "confidence": 0.78,
    "meta": {
      "model": "small",
      "device": "cuda:0",
      "degraded": false,
      "cached": false,
      "latency_ms": 420,
      "queue_wait_ms": 18
    }
  }
}
```

## Example: Service Unavailable

```json
{
  "success": false,
  "code": 503,
  "message": "Kronos service request failed after 3 attempts: timeout",
  "data": null,
  "request_id": "predict-timeout-001",
  "errors": [
    {
      "field": null,
      "code": "TIMEOUT",
      "message": "Kronos service request failed after 3 attempts: timeout"
    }
  ]
}
```
