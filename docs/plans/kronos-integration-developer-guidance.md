# Kronos Integration Developer Guidance

> 目的：本文件面向 `/opt/claude/Kronos` 项目的开发人员，说明 MyStocks 对 Kronos 侧开发的接口、运行时和运维期望。
>
> 范围：仅描述为了更好服务 MyStocks 而建议 Kronos 提供的能力与契约，不要求 Kronos 实现 MyStocks 业务逻辑。

## 1. 目标

Kronos 侧不需要为 MyStocks 适配业务逻辑，但需要提供一个稳定、可预测、可运维的外部推理服务契约，让 MyStocks 能把它当作可靠的高性能推理依赖来使用。

Kronos 侧优先做这 4 件事：

1. 提供稳定的 HTTP 推理接口
2. 保持 MCP 与 HTTP 共用同一套内部 runtime
3. 固化请求/响应 schema，避免字段漂移
4. 明确在线推理与离线训练/回测隔离

MyStocks 最关心的是：

- 接口是否稳定
- 字段是否固定
- 超时、错误码、降级是否明确
- 版本升级是否兼容

## 2. 接口建议

Kronos 第一阶段建议只正式支持两个接口：

1. `POST /v1/kronos/predict`
2. `POST /v1/kronos/encode`

不建议一开始暴露太多分析类接口，否则容易把服务面做散。

### 2.1 `predict` 请求建议

```json
{
  "request_id": "optional-client-id",
  "model": "small",
  "candles": [
    {
      "timestamp": "2026-04-17T09:30:00Z",
      "open": 10.1,
      "high": 10.5,
      "low": 10.0,
      "close": 10.3,
      "volume": 123456,
      "amount": 1260000
    }
  ],
  "pred_len": 20,
  "sample_count": 5,
  "top_p": 0.9,
  "temperature": 1.0
}
```

建议：

- `candles` 字段顺序固定
- `timestamp` 格式固定为 ISO 8601 UTC
- `volume`、`amount` 允许缺失，但服务端要有明确补齐规则
- `pred_len`、`sample_count` 要有硬上限

### 2.2 `predict` 响应建议

```json
{
  "success": true,
  "code": 0,
  "message": "ok",
  "data": {
    "predictions": [
      {
        "timestamp": "2026-04-17T10:00:00Z",
        "open": 10.4,
        "high": 10.6,
        "low": 10.2,
        "close": 10.5,
        "volume": 120000,
        "amount": 1250000
      }
    ],
    "confidence": 0.78
  },
  "meta": {
    "model": "small",
    "device": "cuda:0",
    "degraded": false,
    "cached": false,
    "latency_ms": 420,
    "queue_wait_ms": 18,
    "batch_size": 4
  },
  "request_id": "optional-client-id",
  "timestamp": "2026-04-17T10:00:01Z"
}
```

MyStocks 特别需要这些字段：

- `degraded`
- `cached`
- `latency_ms`
- `queue_wait_ms`
- `model`
- `device`

### 2.3 `encode` 请求/响应建议

请求结构与 `predict` 基本一致，只是不带预测参数。

响应至少返回：

- `s1_tokens`
- `s2_tokens`
- `reconstruction_error`

## 3. 错误码建议

Kronos 侧请固定错误码，不要只返回文本错误。

推荐至少有这几个：

- `PARAM_ERROR`
- `GPU_ERROR`
- `QUEUE_FULL`
- `TIMEOUT`
- `SERVICE_DOWN`
- `MODEL_NOT_READY`

建议返回结构统一：

```json
{
  "success": false,
  "code": "TIMEOUT",
  "message": "interactive request timeout",
  "details": {},
  "request_id": "xxx",
  "timestamp": "2026-04-17T10:00:01Z"
}
```

## 4. 运行时建议

### 4.1 只做在线推理

Kronos 在线服务不要混入：

- 训练
- 微调
- 回测

这些必须独立进程或独立服务，否则 MyStocks 的交互请求会被拖慢。

### 4.2 模型常驻

- `Kronos-small` 启动即加载
- `Kronos-base` 懒加载
- `base` 长时间空闲自动卸载

### 4.3 批处理

Kronos 已有 `predict_batch()` 能力，建议服务端真正用起来。

建议按以下条件分桶：

- `model`
- `lookback length`
- `pred_len`
- `sample_count`

建议使用 20-50ms 小窗口聚合请求。

### 4.4 优先级

请求分两类：

- `interactive`
- `batch`

交互请求优先，不要被批任务饿死。

## 5. 性能与保护建议

### 5.1 必须有硬限制

- `pred_len` 最大值
- `sample_count` 最大值
- `candles` 最大长度
- 最大并发数
- 最大 `batch size`

### 5.2 必须有超时

建议：

- `interactive <= 1.5s`
- `batch <= 10s`

超时后应快速失败，不要挂死连接。

### 5.3 降级必须明确

当 GPU 利用率或显存压力过高时：

- 先拒绝 `batch`
- 保留 `interactive`
- 可降级到 `mini`
- 在响应中返回 `degraded: true`

## 6. 可观测性建议

Kronos 侧建议至少暴露这些指标：

- `request_total`
- `request_inflight`
- `queue_depth`
- `queue_wait_ms`
- `inference_latency_ms`
- `gpu_utilization`
- `gpu_memory_used_mb`
- `cache_hit_rate`
- `degraded_total`
- `timeout_total`
- `oom_total`

如果没有这些指标，MyStocks 很难判断问题在网络、队列还是 GPU。

## 7. 兼容性建议

Kronos 侧建议遵守这些约束：

- HTTP schema 版本化，例如 `/v1/...`
- MCP 和 HTTP 共用同一 runtime，不要双实现
- 新增字段可以，删除字段要谨慎
- 字段名一旦发布，尽量不改
- 模型名保持有限枚举，如 `mini` / `small` / `base`

## 8. 对 MyStocks 最关键的配合点

如果 Kronos 侧优先完成这 6 件事，对接会顺很多：

1. 固定 `predict` 和 `encode` 两个接口
2. 固定 JSON schema
3. 固定错误码
4. 返回 `degraded` / `cached` / `latency_ms` / `queue_wait_ms`
5. 保证在线推理和离线任务隔离
6. 提供一份正式的接口文档和示例请求

## 9. 建议交付物

建议 Kronos 团队输出这些文档：

- `Kronos API Contract.md`
- `Kronos Error Codes.md`
- `Kronos Runtime SLA.md`
- `Kronos Deployment Guide.md`

## 10. 结论

Kronos 若要更好服务 MyStocks，不需要理解 MyStocks 的业务细节，而需要在“稳定接口、明确错误、低延迟在线推理、清晰运行边界”四个方面做到工程化收敛。

MyStocks 侧最核心的诉求不是“更多模型功能”，而是：

- 可稳定调用
- 可预测返回
- 可观测
- 可升级而不破坏兼容性

只要 Kronos 侧把这些基础能力打牢，对接成本就会显著下降。
