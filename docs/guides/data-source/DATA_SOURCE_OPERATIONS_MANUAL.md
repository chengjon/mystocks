# 数据源优化 V2 - 运维手册

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

> **运维手册说明**:
> 本文件用于提供某一局部主题的使用方法、操作步骤、背景说明或参考材料，帮助理解仓库中的具体实践。
> 其中的命令、路径、流程和示例应与 `architecture/STANDARDS.md`、当前代码实现及最新验证结果一并核对，不应单独视为共享规则或当前状态的唯一事实来源。

**最后更新**: 2026-05-05
**适用范围**: `optimize-data-source-v2` 当前 repo-owned 能力  
**相关文档**:
- [`DATA_SOURCE_MONITORING_GUIDE.md`](./DATA_SOURCE_MONITORING_GUIDE.md)
- [`DATA_SOURCE_OPTIMIZATION_QUICK_REFERENCE.md`](./DATA_SOURCE_OPTIMIZATION_QUICK_REFERENCE.md)
- [`DATA_SOURCE_OPTIMIZATION_DEPLOYMENT_CHECKLIST.md`](./DATA_SOURCE_OPTIMIZATION_DEPLOYMENT_CHECKLIST.md)
- [`../../reports/tasks/optimize-data-source-v2-external-acceptance-handoff-2026-05-05.md`](../../reports/tasks/optimize-data-source-v2-external-acceptance-handoff-2026-05-05.md)

> **边界提醒（2026-05-05）**:
> 本手册当前只覆盖 `optimize-data-source-v2` 已落地的 repo-owned 运行与验证入口。
> 若问题已经进入灰度部署、live 观测、ROI/SLA 验收、最终会议或 archive 时序，请直接转到
> `docs/reports/tasks/optimize-data-source-v2-external-acceptance-handoff-2026-05-05.md`，
> 不要继续把这些事项当作仓库内编码或本地测试任务处理。

---

## 1. 当前运维对象

本变更当前在仓库中落地的主要对象有：

1. `SmartCache`
2. `CircuitBreaker`
3. `DataQualityValidator`
4. `SmartRouter`
5. `BatchProcessor`
6. `datasource_*` Prometheus 指标族
7. 数据源监控 dashboard / alert rule 配置

需要单独保留认知的是：

- 运行时主 `GET /metrics` 与 `src/core/data_source/metrics.py` 仍是双轨关系；
- Grafana / Prometheus 的文件存在，不等于浏览器展示和抓取链路已部署验收；
- `AdaptiveRateLimiter` 和 governance-side `DataLineageTracker` 已存在，但尚未默认接入主调用链。

---

## 2. 关键文件与路径

| 类型 | 路径 | 作用 |
|------|------|------|
| 运行时 manager | `src/core/data_source/base.py` | `DataSourceManagerV2` 初始化与 hook 入口 |
| 主调用逻辑 | `src/core/data_source/handler.py` | `_call_endpoint()` 真正出站位置 |
| 路由选择 | `src/core/data_source/router.py` | `get_best_endpoint()` |
| 缓存 | `src/core/data_source/smart_cache.py` | SmartCache 实现 |
| 熔断 | `src/core/data_source/circuit_breaker.py` | CircuitBreaker 实现 |
| 数据质量 | `src/core/data_source/data_quality_validator.py` | 多层质量验证 |
| 指标 | `src/core/data_source/metrics.py` | `datasource_*` 指标族 |
| 监控配置 | `config/monitoring-stack/grafana-dashboards/data_source_monitoring.json` | Grafana dashboard |
| 告警规则 | `config/monitoring-stack/config/rules/data-source-alerts.yml` | Prometheus rules |

---

## 3. 日常运维检查

### 3.1 快速健康检查

先确认运行时后端仍可访问：

```bash
curl http://localhost:8020/health
curl http://localhost:8020/metrics | head
```

如果服务未起，不要直接判断“数据源优化失效”；先恢复后端基础可用性。

### 3.2 验证 `datasource_*` 指标族

优先用本地测试确认 repo-owned 指标链仍完整：

```bash
pytest tests/unit/test_metrics.py tests/unit/test_data_source_metrics_integration.py -q --no-cov
```

这两组测试分别覆盖：

- `src/core/data_source/metrics.py` 的本地 registry / exposition
- `DataSourceManagerV2` hook 是否真的把调用结果写进指标链

### 3.3 验证 dashboard / alert rule 引用一致性

```bash
pytest tests/performance/test_validate_monitoring_prometheus_references.py -q --no-cov
```

这项验证的结论是：

- dashboard / rule 文件引用的指标名与当前代码中声明的指标族一致；
- 它不等同于 Grafana 浏览器页面已经渲染正常。

### 3.4 Phase 1 本地回归

```bash
pytest \
  tests/unit/test_smart_cache.py \
  tests/unit/test_circuit_breaker.py \
  tests/unit/test_circuit_breaker_integration.py \
  tests/unit/test_data_quality_validator.py \
  tests/unit/test_gpu_validator_integration.py \
  -q --no-cov
```

### 3.5 Phase 2 本地回归

```bash
pytest \
  tests/unit/test_smart_router.py \
  tests/unit/test_smart_router_integration.py \
  tests/unit/test_metrics.py \
  tests/unit/test_data_source_metrics_integration.py \
  tests/integration/test_batch_processing.py \
  src/governance/tests/test_fetcher_bridge.py \
  -q --no-cov
```

---

## 4. 常见告警与排查

### 4.1 缓存命中率异常下降

优先排查：

1. `SmartCache` 是否被显式关闭为 `use_smart_cache=False`
2. `refresh_threshold` / `default_ttl` 是否被改坏
3. `refresh_failures` 是否持续增长

可用验证：

```bash
pytest tests/unit/test_smart_cache.py -q --no-cov
```

### 4.2 熔断器频繁 OPEN

优先排查：

1. 下游 endpoint 是否真实失败
2. `handler.py:_call_endpoint()` 的异常路径是否被新代码吞掉
3. `failure_threshold` / `recovery_timeout` 是否被错误调整

可用验证：

```bash
pytest tests/unit/test_circuit_breaker.py tests/unit/test_circuit_breaker_integration.py -q --no-cov
```

### 4.3 数据质量摘要异常

优先排查：

1. `DataQualityValidator.validate()` 返回 shape 是否变化
2. `GPUValidator.validate()` 是否仍追加 `quality_summary`
3. 输入 OHLCV 数据是否缺列或异常

可用验证：

```bash
pytest tests/unit/test_data_quality_validator.py tests/unit/test_gpu_validator_integration.py -q --no-cov
```

### 4.4 批量抓取吞吐退化

优先排查：

1. `GovernanceDataFetcher` 是否仍走 `BatchProcessor`
2. `BatchProcessor` 的 `max_workers` / `timeout` 是否被改坏
3. endpoint 解析是否发生重复调用

可用验证：

```bash
pytest tests/integration/test_batch_processing.py src/governance/tests/test_fetcher_bridge.py -q --no-cov
```

### 4.5 路由结果不符合预期

优先排查：

1. endpoint 输入 shape 是否仍含 `config` 与平铺字段
2. `SmartRouter` 的性能统计是否有值
3. `cost.is_free`、`location`、`priority` 等字段是否丢失

可用验证：

```bash
pytest tests/unit/test_smart_router.py tests/unit/test_smart_router_integration.py -q --no-cov
```

---

## 5. 运维边界

当前手册能够覆盖的是：

- repo-owned 组件仍然存在且本地回归可过；
- `datasource_*` 指标族与 dashboard / alert rule 的引用关系仍一致；
- 常见退化场景的第一轮排查入口。

当前手册**不能替代**以下外部动作：

- Grafana 页面浏览器内人工验收
- Prometheus 实际抓取链路部署
- 灰度环境与生产环境发布
- `8.x` / `11.x` / `12.5-12.7` 的会议、发布、归档

---

## 6. 推荐收口顺序

如果后续继续推进外部验收，建议顺序是：

1. 先跑本地 repo-owned 回归
2. 再验证 `/metrics` 与指标引用一致性
3. 再做 Grafana / Prometheus 部署侧验证
4. 最后再记录灰度、生产与项目归档证据
