# AdaptiveRateLimiter 使用说明

## 适用范围

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。

本指南说明 `src/core/data_source/adaptive_rate_limiter.py` 中新增的 `AdaptiveRateLimiter`。

它的定位是：

- 为 `optimize-data-source-v2` 的 `10.x` 提供独立的自适应节流组件
- 基于近期错误率动态调整 `current_rate`
- 在 `acquire()` 时按 `permits / current_rate` 控制最小时间间隔

## 当前边界

当前 repo-truth 是：

- `AdaptiveRateLimiter` 已经作为独立组件落地
- 已有单元测试覆盖初始化、降速、升速、节流和错误率边界
- 当前**没有**自动接入 `DataSourceManagerV2` / `handler.py` / `monitoring.py` 主链

也就是说，这一批证明的是“组件可用”，不是“主数据源管理流程已默认启用自适应限流”。

## 核心参数

```python
AdaptiveRateLimiter(
    initial_rate=10,
    min_rate=1,
    max_rate=100,
    adjustment_factor=0.1,
)
```

参数含义：

- `initial_rate`
  - 初始速率，单位 `req/s`
- `min_rate`
  - 最低限速
- `max_rate`
  - 最高限速
- `adjustment_factor`
  - 每次调整比例

## 调整规则

当前实现规则：

- `error_rate > 0.1`
  - 触发降速
- `error_rate < 0.01`
  - 触发加速
- `min_rate <= current_rate <= max_rate`
  - 始终保持边界约束

错误率更新规则：

- `record_error(delta)`
  - 累加错误率，最大不超过 `1.0`
- `record_success(delta)`
  - 降低错误率，最小不低于 `0.0`

## 最小示例

```python
from src.core.data_source.adaptive_rate_limiter import AdaptiveRateLimiter

limiter = AdaptiveRateLimiter(
    initial_rate=10,
    min_rate=1,
    max_rate=100,
    adjustment_factor=0.1,
)

limiter.acquire()

try:
    # 执行外部请求
    response = call_remote_api()
except Exception:
    limiter.record_error()
    raise
else:
    limiter.record_success()
```

## `acquire()` 语义

- `acquire(permits=1)`
  - 申请一个请求许可
- `acquire(permits=n)`
  - 按 `n / current_rate` 计算最小间隔

这意味着：

- `current_rate=10` 且 `permits=1`
  - 最小间隔约 `0.1s`
- `current_rate=10` 且 `permits=2`
  - 最小间隔约 `0.2s`

## 适合的下一步接入方式

如果后续要把它接入主链，建议优先考虑：

1. 以 endpoint 为粒度挂到 `DataSourceManagerV2`
2. 在成功/失败路径分别调用 `record_success()` / `record_error()`
3. 让 `acquire()` 发生在真正出站请求之前

当前这三步还没有在仓库里自动完成。
