# 数据源优化 V2 - 开发者文档

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

> **开发者文档说明**:
> 本文件用于提供某一局部主题的使用方法、操作步骤、背景说明或参考材料，帮助理解仓库中的具体实践。
> 其中的命令、路径、流程和示例应与 `architecture/STANDARDS.md`、当前代码实现及最新验证结果一并核对，不应单独视为共享规则或当前状态的唯一事实来源。

**最后更新**: 2026-05-05
**适用读者**: 维护 `DataSourceManagerV2`、治理层抓取链、指标链和相关测试的开发者

> **边界提醒（2026-05-05）**:
> 这份文档描述的是 `optimize-data-source-v2` 当前仓库内已经落地的实现、验证与扩展点。
> 若后续工作已经变成灰度发布、Prometheus/Grafana 持续观测、ROI/SLA 收证据或 OpenSpec 归档，
> 应直接进入 `docs/reports/tasks/optimize-data-source-v2-external-acceptance-handoff-2026-05-05.md`，
> 而不是继续在本地实现层寻找未闭合编码项。

---

## 1. 当前主链路

`optimize-data-source-v2` 当前的主链路可以概括为：

1. `src/core/data_source/base.py`
   - `DataSourceManagerV2` 初始化缓存、熔断器、registry 和 hook
2. `src/core/data_source/router.py`
   - `get_best_endpoint()` 负责路由选择
   - 当前已懒加载 `SmartRouter`
3. `src/core/data_source/handler.py`
   - `_call_endpoint()` 是真实出站调用逻辑
4. `src/core/data_source/monitoring.py`
   - 负责 `_record_success()` / `_record_failure()` 运行时统计
5. `src/core/data_source/metrics.py`
   - 负责 `datasource_*` 指标记录与 exposition
6. `src/governance/core/fetcher_bridge.py`
   - 治理层 `GovernanceDataFetcher`
   - 多 symbol 路径已接 `BatchProcessor`

---

## 2. 关键组件与职责

### 2.1 `SmartCache`

- 文件：`src/core/data_source/smart_cache.py`
- 角色：线程安全缓存层
- 已落地能力：
  - LRU
  - TTL
  - 软过期
  - 后台刷新
  - `ThreadPoolExecutor(max_workers=5)`

### 2.2 `CircuitBreaker`

- 文件：`src/core/data_source/circuit_breaker.py`
- 角色：保护单个 endpoint 免受级联故障
- 已落地能力：
  - `CLOSED / OPEN / HALF_OPEN`
  - 线程安全状态转换
  - 恢复探测

### 2.3 `DataQualityValidator`

- 文件：`src/core/data_source/data_quality_validator.py`
- 角色：数据质量多层检查
- 已落地能力：
  - 逻辑检查
  - 业务规则检查
  - 统计离群值检查
  - 跨源校验
- 当前还会通过 `GPUValidator.validate()` 以 `quality_summary` 形式回灌治理层

### 2.4 `SmartRouter`

- 文件：`src/core/data_source/smart_router.py`
- 角色：按性能、成本、负载、地域做多维度路由
- 当前默认权重：
  - `performance=0.4`
  - `cost=0.3`
  - `load=0.2`
  - `location=0.1`

### 2.5 `BatchProcessor`

- 文件：`src/core/data_source/batch_processor.py`
- 角色：治理层批量 K 线抓取并发执行器
- 当前特性：
  - `ThreadPoolExecutor`
  - `as_completed(..., timeout=...)`
  - timeout fail-fast
  - 异常隔离
  - `shutdown(wait=...)`

### 2.6 `DataLineageTracker`

- 文件：`src/governance/lineage/tracker.py`
- 角色：governance-side 轻量血缘追踪器
- 当前边界：
  - `networkx` 主链路已落地
  - `Neo4jLineageStore` 是 optional persistence
  - 未宣称已替换现有 `src/data_governance/lineage.py` API 真相源

### 2.7 `AdaptiveRateLimiter`

- 文件：`src/core/data_source/adaptive_rate_limiter.py`
- 角色：独立限流组件
- 当前边界：
  - 已有单元测试
  - 尚未默认接入 `DataSourceManagerV2` 主出站链

---

## 3. 公开入口与现行边界

### 3.1 包级导出

当前 `src/core/data_source/__init__.py` 只显式导出：

- `DataSourceManagerV2`
- `LRUCache`

这意味着：

- `SmartCache`、`SmartRouter`、`BatchProcessor`、`AdaptiveRateLimiter` 等都属于“可直接 import 的内部组件”，但不是包级稳定 API 面。
- 如果后续希望把它们升级为稳定公共 surface，应单独变更 `__init__.py` 与相应文档。

### 3.2 双轨与相邻能力

开发时必须保留以下区分：

- 运行时 `/metrics` 与 `src/core/data_source/metrics.py` 不是同一层东西
- `DataLineageTracker` 与 `src/data_governance/lineage.py` 不是同一套实现
- `AdaptiveRateLimiter` 已存在，但不是默认出站限流主链

---

## 4. 扩展点

### 4.1 新增数据源 endpoint

先看：

- [`NEW_API_SOURCE_INTEGRATION_GUIDE.md`](./NEW_API_SOURCE_INTEGRATION_GUIDE.md)
- [`DATA_SOURCE_ENDPOINT_REGISTRATION_GUIDE.md`](./DATA_SOURCE_ENDPOINT_REGISTRATION_GUIDE.md)

同时注意：

- endpoint shape 需要兼容 `router.py` 当前读取的平铺字段与 `config` 嵌套字段
- 若需要参与 `SmartRouter` 评分，应补齐 `source_type`、`location`、`priority`、`cost.is_free` 等信息

### 4.2 增加新的质量检查

主要入口：

- `src/core/data_source/data_quality_validator.py`

同步要求：

- 更新 `ValidationSummary` 相关断言
- 更新 `tests/unit/test_data_quality_validator.py`
- 若治理层需要看摘要，确认 `tests/unit/test_gpu_validator_integration.py` 仍通过

### 4.3 调整路由权重或规则

主要入口：

- `src/core/data_source/smart_router.py`
- `src/core/data_source/router.py`

同步要求：

- 更新 `tests/unit/test_smart_router.py`
- 更新 `tests/unit/test_smart_router_integration.py`
- 如涉及性能假设，再跑 `tests/performance/test_smart_router_ab_benchmark.py`

### 4.4 调整批量抓取行为

主要入口：

- `src/core/data_source/batch_processor.py`
- `src/governance/core/fetcher_bridge.py`

同步要求：

- 更新 `tests/integration/test_batch_processing.py`
- 更新 `src/governance/tests/test_fetcher_bridge.py`
- 如涉及吞吐量假设，再跑 `tests/performance/test_batch_processor_throughput.py`

---

## 5. 推荐验证矩阵

### 5.1 Phase 1

```bash
pytest \
  tests/unit/test_smart_cache.py \
  tests/unit/test_circuit_breaker.py \
  tests/unit/test_circuit_breaker_integration.py \
  tests/unit/test_data_quality_validator.py \
  tests/unit/test_gpu_validator_integration.py \
  -q --no-cov
```

### 5.2 Phase 2

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

### 5.3 可选组件

```bash
pytest \
  tests/unit/test_governance/test_data_lineage_tracker.py \
  tests/integration/test_data_lineage_tracker_integration.py \
  tests/unit/test_adaptive_rate_limiter.py \
  -q --no-cov
```

### 5.4 本地 benchmark

```bash
pytest tests/performance/test_phase1_datasource_benchmark.py -q --no-cov --run-performance
pytest tests/performance/test_smart_router_ab_benchmark.py -q --no-cov --run-performance
pytest tests/performance/test_batch_processor_throughput.py -q --no-cov --run-performance
```

---

## 6. 当前开发红线

1. 不要把历史报告里的“预期收益”写回当前代码注释或文档，除非有本地或部署侧新证据。
2. 不要把 `AdaptiveRateLimiter` 或 `DataLineageTracker` 误写成默认主链已启用。
3. 不要把 Grafana / Prometheus 文件存在，误写成页面已验收。
4. 如果修改 `handler.py:_call_endpoint()`、`router.py:get_best_endpoint()`、`base.py:DataSourceManagerV2._call_endpoint()` 这些符号，必须先走 GitNexus impact 分析。

---

## 7. 推荐阅读顺序

1. [`DATA_SOURCE_OPTIMIZATION_QUICK_REFERENCE.md`](./DATA_SOURCE_OPTIMIZATION_QUICK_REFERENCE.md)
2. [`DATA_SOURCE_MONITORING_GUIDE.md`](./DATA_SOURCE_MONITORING_GUIDE.md)
3. [`DATA_SOURCE_OPERATIONS_MANUAL.md`](./DATA_SOURCE_OPERATIONS_MANUAL.md)
4. `src/core/data_source/base.py`
5. `src/core/data_source/router.py`
6. `src/core/data_source/handler.py`
