# Phase 1: 核心稳定性（1-2周）

> **使用说明**:
> 本文件用于记录当前 OpenSpec 变更的执行清单、操作步骤或协作约束，帮助跟踪实施过程。
> 其中勾选状态、执行顺序和局部说明仅代表任务推进视角，不应脱离 proposal、design、正式 specs、`architecture/STANDARDS.md` 与实际验证结果单独解读为最终事实。

> **Repo-Truth 对齐注记（2026-04-27）**:
> 本清单已按当前仓库实现复核，仅对有直接本地证据的项勾选。
> 当前关键事实漂移：
> - `src/core/data_source/smart_cache.py`、`circuit_breaker.py`、`data_quality_validator.py`、`smart_router.py`、`metrics.py`、`batch_processor.py` 已存在，但不同模块的接入完成度并不一致。
> - `src/core/data_source/base.py` 当前默认启用 `SmartCache`，同时仍保留 `use_smart_cache=False` 的 `LRUCache` 回退路径；每个 endpoint 的 `CircuitBreaker` 实例已创建，但 `_call_endpoint()` 实际调用链仍未完成熔断包装。
> - `src/core/data_source/router.py` 仍按“首个健康端点”返回，尚未接入 `SmartRouter`；`src/governance/core/fetcher_bridge.py` 仍是串行批量抓取，尚未切到 `BatchProcessor` 主路径。
> - `/metrics` 端点已存在，但当前暴露的是后端 performance middleware 指标面；`src/core/data_source/metrics.py` 默认仍使用独立 `CollectorRegistry`，不能机械视为“整条数据源指标链已完全并到全局 REGISTRY”。
> - `docs/guides/data-source/DATA_SOURCE_OPTIMIZATION_QUICK_REFERENCE.md` 当前主要覆盖 SmartCache / CircuitBreaker / DataQualityValidator，并未形成可直接复用的 `SmartRouter` 使用说明。
> - `docs/guides/data-source/DATA_SOURCE_MONITORING_GUIDE.md` 虽存在，但当前仍混用 `src/monitoring/data_source_metrics.py` + `scripts/runtime/start_metrics_server.py` 的独立指标链与后端 `/metrics` 暴露方式，并引用缺失的 Grafana / provisioning 路径，不能直接视为“监控使用说明已按当前实现更新完成”。
> - `grafana/dashboards/data-source-metrics.json` 与 `monitoring-stack/config/rules/data-source-alerts.yml` 当前本地缺失。

## 1. SmartCache 实现（3-4天）

- [x] 1.1 创建 `src/core/data_source/smart_cache.py` 文件
- [x] 1.2 实现 `SmartCache` 类（LRU + TTL + 后台刷新）
- [x] 1.3 添加 `threading.RLock` 保护并发访问
- [x] 1.4 实现 `_trigger_refresh()` 方法（启动后台线程）
- [x] 1.5 实现 `_run_refresh()` 方法（执行刷新逻辑）
- [x] 1.6 添加 `refreshing` set 防止重复刷新
- [x] 1.7 集成 `ThreadPoolExecutor(max_workers=5)` 限制并发刷新
- [x] 1.8 更新 `src/core/data_source/base.py` 替换 `LRUCache` 为 `SmartCache`
- [x] 1.9 编写单元测试 `tests/unit/test_smart_cache.py`
  - [x] 1.9.1 测试缓存命中（fresh data）
  - [x] 1.9.2 测试缓存过期触发预刷新
  - [x] 1.9.3 测试软过期（返回旧数据）
  - [x] 1.9.4 测试硬过期（返回 None）
  - [x] 1.9.5 测试 LRU 淘汰
  - [x] 1.9.6 测试并发访问（100线程并发）
  - [x] 1.9.7 测试后台刷新失败处理
  - [x] 1.9.8 测试线程池限制（max_workers=5）
- [ ] 1.10 性能测试：对比优化前后的缓存命中率和响应时间
- [ ] 1.11 代码审查：确保线程安全性和错误处理
- [x] 1.12 更新文档：添加 SmartCache 使用说明

## 2. CircuitBreaker 实现（3-4天）

- [x] 2.1 创建 `src/core/data_source/circuit_breaker.py` 文件
- [x] 2.2 定义 `CircuitState` 枚举（CLOSED, OPEN, HALF_OPEN）
- [x] 2.3 实现 `CircuitBreaker` 类
- [x] 2.4 添加 `threading.Lock` 保护状态转换
- [x] 2.5 实现 `call()` 方法（执行调用并自动熔断）
- [x] 2.6 实现 `_should_attempt_reset()` 方法（检查是否超时）
- [x] 2.7 实现 `_on_success()` 方法（成功回调）
- [x] 2.8 实现 `_on_failure()` 方法（失败回调）
- [x] 2.9 添加 `CircuitBreakerOpenError` 异常类
- [x] 2.10 集成到 `src/core/data_source/base.py._call_endpoint()`
  - [x] Repo-truth（2026-05-01）：当前仓库的 `DataSourceManagerV2._call_endpoint()` 是 `src/core/data_source/base.py` 中的薄转发层，真实调用逻辑位于 `src/core/data_source/handler.py:_call_endpoint()`；该 delegate 现已在执行 `handler.fetch(...)` 前接入 `self.circuit_breakers[endpoint_name].call(...)`。验证见 `tests/unit/test_circuit_breaker_integration.py`、`src/governance/tests/test_fetcher_bridge.py`、`tests/unit/adapters/test_runtime_data_source_regressions.py`。
- [x] 2.11 为每个 endpoint 创建独立的 CircuitBreaker 实例
- [x] 2.12 编写单元测试 `tests/unit/test_circuit_breaker.py`
  - [x] 2.12.1 测试 CLOSED 状态正常调用
  - [x] 2.12.2 测试达到阈值后进入 OPEN 状态
  - [x] 2.12.3 测试超时后进入 HALF_OPEN 状态
  - [x] 2.12.4 测试试探成功后回到 CLOSED 状态
  - [x] 2.12.5 测试试探失败后回到 OPEN 状态
  - [x] 2.12.6 测试并发状态转换（10线程并发）
  - [x] 2.12.7 测试剩余时间反馈
  - [x] 2.12.8 测试可配置阈值
- [x] 2.13 集成测试：模拟故障场景验证熔断器行为
  - [x] Repo-truth（2026-05-01）：`tests/unit/test_circuit_breaker_integration.py` 当前已覆盖两类主调用链故障场景：首次失败后被 `CircuitBreakerOpenError` 短路，以及超时后经 `src/core/data_source/handler.py:_call_endpoint()` 主链路恢复成功；配套状态机验证见 `tests/unit/test_circuit_breaker.py` 的 OPEN / HALF_OPEN / recover / reopen 用例。
- [ ] 2.14 代码审查：确保状态转换逻辑正确
- [x] 2.15 更新文档：添加 CircuitBreaker 使用说明

## 3. DataQualityValidator 实现（3-4天）

- [x] 3.1 创建 `src/core/data_source/data_quality_validator.py` 文件
- [x] 3.2 实现 `DataQualityValidator` 类
- [x] 3.3 实现 `_logic_check()` 方法（OHLC 基础逻辑）
- [x] 3.4 实现 `_business_check()` 方法（业务规则）
  - [x] 3.4.1 检测极端价格波动（>20%）
  - [x] 3.4.2 检测异常成交量（>10倍均值）
  - [x] 3.4.3 检测停牌数据
  - [x] 3.4.4 检测零或负价格
- [x] 3.5 实现 `_statistical_check()` 方法（3-sigma 异常检测）
- [x] 3.6 实现 `_cross_source_check()` 方法（跨源验证）
- [x] 3.7 实现 `validate()` 主方法（协调所有检查）
- [x] 3.8 集成到 `src/governance/engine/gpu_validator.py`
  - [x] Repo-truth（2026-05-01）：`src/governance/engine/gpu_validator.py:GPUValidator.validate()` 当前保持原有 `ohlc/missing/suspension` 规则返回不变，并额外追加序列化后的 `quality_summary`；其摘要来自 `src/core/data_source/data_quality_validator.py:DataQualityValidator`，验证见 `tests/unit/test_gpu_validator_integration.py`。当前集成是治理层补充质量摘要，不等于把 GPUValidator 提升为全仓库唯一数据质量真相源。
- [x] 3.9 编写单元测试 `tests/unit/test_data_quality_validator.py`
  - [x] 3.9.1 测试 OHLC 逻辑验证（通过/失败场景）
  - [x] 3.9.2 测试业务规则验证（极端价格、异常成交量、停牌）
  - [x] 3.9.3 测试统计异常检测（3-sigma）
  - [x] 3.9.4 测试跨源验证（一致性检查）
  - [x] 3.9.5 测试验证汇总（summary）
  - [ ] 3.9.6 测试 GPU 加速验证（100,000行数据）
- [ ] 3.10 准备 100+ 测试用例数据（覆盖各种异常场景）
- [ ] 3.11 代码审查：确保验证逻辑完整
- [x] 3.12 更新文档：添加 DataQualityValidator 使用说明

## 4. Phase 1 验收和部署（1-2天）

- [ ] 4.1 运行所有单元测试和并发测试
- [ ] 4.2 性能测试：对比优化前后的基准指标
- [ ] 4.3 灰度部署到测试环境
- [ ] 4.4 监控关键指标（缓存命中率、API 调用成本、响应时间）
- [ ] 4.5 验收确认：
  - [ ] 4.5.1 缓存命中率 > 80%
  - [ ] 4.5.2 API 调用成本降低 40%
  - [ ] 4.5.3 响应时间减少 50%（500ms → 250ms）
  - [ ] 4.5.4 所有单元测试通过
  - [ ] 4.5.5 并发测试通过
- [ ] 4.6 修复发现的问题
- [ ] 4.7 准备 Phase 2 环境

---

# Phase 2: 能力提升（1个月）

## 5. SmartRouter 实现（5-7天）

> **局部事实说明（2026-04-27）**:
> `SmartRouter` 本体已经具备权重参数（`performance_weight=0.4`、`cost_weight=0.3`、`load_weight=0.2`、`location_weight=0.1`）和对应测试，但 `src/core/data_source/router.py` 当前仍未把该组件接入主路由选择链路，因此 5.8 继续保留未完成。

- [x] 5.1 创建 `src/core/data_source/smart_router.py` 文件
- [x] 5.2 实现 `SmartRouter` 类
- [x] 5.3 实现 `_score_by_performance()` 方法（P50/P95/P99 + 成功率）
- [x] 5.4 实现 `_adjust_by_cost()` 方法（成本优化）
- [x] 5.5 实现 `_adjust_by_load()` 方法（负载均衡）
- [x] 5.6 实现 `_adjust_by_location()` 方法（地域感知）
- [x] 5.7 实现 `route()` 主方法（多维度决策）
- [x] 5.8 集成到 `src/core/data_source/router.py.get_best_endpoint()`
  - [x] Repo-truth（2026-05-01）：`src/core/data_source/router.py:get_best_endpoint()` 现已懒加载 `SmartRouter`，将 endpoint `config` 平铺为顶层运行字段后调用 `smart_router.route(...)`，同时保留原有 `config` 嵌套结构；验证见 `tests/unit/test_smart_router_integration.py`、`tests/unit/test_smart_router.py`、`src/governance/tests/test_fetcher_bridge.py`、`tests/unit/adapters/test_runtime_data_source_regressions.py`。
- [x] 5.9 添加配置项：权重（performance=0.4, cost=0.3, load=0.2, location=0.1）
- [x] 5.10 编写单元测试 `tests/unit/test_smart_router.py`
  - [x] 5.10.1 测试性能评分计算
  - [x] 5.10.2 测试成本优化（免费源优先）
  - [x] 5.10.3 测试负载均衡（避免过载）
  - [x] 5.10.4 测试地域感知（最近节点）
  - [x] 5.10.5 测试多维度综合评分
- [ ] 5.11 A/B 测试：对比新旧路由策略的性能差异
- [ ] 5.12 代码审查：确保路由逻辑正确
- [x] 5.13 更新文档：添加 SmartRouter 使用说明
  - [x] Repo-truth（2026-05-01）：`docs/guides/data-source/DATA_SOURCE_OPTIMIZATION_QUICK_REFERENCE.md` 现已补充 `SmartRouter` 当前接入方式、默认权重、endpoint 兼容 shape、懒加载路由链路与现阶段边界说明；该文档对齐了 `src/core/data_source/router.py:get_best_endpoint()` 与 `src/core/data_source/smart_router.py` 的当前实现，不再只停留在 Phase 1 三组件说明。

## 6. Prometheus 监控集成（5-7天）

> **局部事实说明（2026-04-27）**:
> `web/backend/app/main.py` 当前已通过 `metrics_endpoint()` 暴露 `/metrics`，其底层使用的是后端 performance middleware 的全局 Prometheus registry。
> 但 `src/core/data_source/metrics.py` 默认仍创建独立 `CollectorRegistry`，因此“路由级全局 REGISTRY”与“数据源指标全量统一到全局 REGISTRY”应分开理解。
>
> **Repo-truth 补充（2026-04-28）**:
> - `src/core/data_source/base.py` 中 `DataSourceManagerV2._call_endpoint()` 仅委托 `src/core/data_source/handler.py:_call_endpoint()`；后者当前只调用 `_record_success()` / `_record_failure()`，而这两个方法在 `base.py` 里仍是 `pass` 存根，因此 6.5 不能按“已完成数据源指标埋点接入”勾选。
> - 当前未找到 `grafana/dashboards/data-source-metrics.json`、`monitoring-stack/config/rules/data-source-alerts.yml`、`tests/unit/test_metrics.py` 这些任务原文直接点名的产物，因此 6.7 / 6.8 / 6.9 继续保持未完成。

- [x] 6.1 创建 `src/core/data_source/metrics.py` 文件
- [x] 6.2 定义 Prometheus 指标（Histogram, Counter, Gauge）
  - [x] 6.2.1 `datasource_api_latency_seconds` (Histogram)
  - [x] 6.2.2 `datasource_api_calls_total` (Counter)
  - [x] 6.2.3 `datasource_data_quality` (Gauge)
  - [x] 6.2.4 `datasource_cache_hits_total` (Counter)
  - [x] 6.2.5 `datasource_cache_misses_total` (Counter)
  - [x] 6.2.6 `datasource_circuit_breaker_state` (Gauge)
  - [x] 6.2.7 `datasource_api_cost_estimated` (Gauge)
- [x] 6.3 实现 `track_api_call()` 装饰器
- [x] 6.4 实现 `DataSourceMetrics` 类（指标收集器）
- [x] 6.5 在 `DataSourceManagerV2._call_endpoint()` 添加指标埋点
  - [x] Repo-truth（2026-05-01）：当前 `src/core/data_source/handler.py:_call_endpoint()` 继续通过 `self._record_success()` / `self._record_failure()` 进入 `src/core/data_source/base.py` hook；这些 hook 现已委托到 `src/core/data_source/monitoring.py` 的运行时统计逻辑，并同步调用 `src/core/data_source/metrics.py:get_metrics()` 记录 `datasource_api_calls_total` / `datasource_api_latency_seconds` / `datasource_circuit_breaker_state`。验证见 `tests/unit/test_data_source_metrics_integration.py`、`tests/unit/test_circuit_breaker_integration.py`、`src/governance/tests/test_fetcher_bridge.py`、`tests/unit/adapters/test_runtime_data_source_regressions.py`。
- [x] 6.6 在 `web/backend/app/main.py` 集成 `/metrics` 端点
  - [x] 6.6.1 添加 `/metrics` 路由
  - [x] 6.6.2 返回 Prometheus exposition 格式
  - [x] 6.6.3 使用全局 REGISTRY
- [ ] 6.7 创建 Grafana 仪表板配置
  - [ ] 6.7.1 创建 `grafana/dashboards/data-source-metrics.json`
  - [ ] 6.7.2 添加 API 延迟面板（P50/P95/P99）
  - [ ] 6.7.3 添加成功率面板
  - [ ] 6.7.4 添加缓存命中率面板
  - [ ] 6.7.5 添加熔断器状态面板
  - [ ] 6.7.6 添加 API 成本面板
- [x] 6.8 编写单元测试 `tests/unit/test_metrics.py`
  - [x] 6.8.1 测试指标记录（成功/失败）
  - [x] 6.8.2 测试延迟 histogram
  - [x] 6.8.3 测试缓存 hit/miss 计数
  - [x] 6.8.4 测试熔断器状态 gauge
  - [x] Repo-truth（2026-05-01）：已新增 `tests/unit/test_metrics.py`，覆盖 `record_api_call()` 成功/失败计数、`get_avg_latency()`、缓存命中率与 `record_circuit_breaker_state()`。补测过程中确认 `src/core/data_source/metrics.py:get_avg_latency()` 原先错误依赖 Histogram 私有字段；现已改为基于 `collect().samples` 的 `_sum/_count` 样本计算平均值。验证见 `tests/unit/test_metrics.py`、`tests/unit/test_data_source_metrics_integration.py`。
- [ ] 6.9 配置 Prometheus 告警规则
  - [ ] 6.9.1 创建 `monitoring-stack/config/rules/data-source-alerts.yml`
  - [ ] 6.9.2 添加成功率 < 95% 告警
  - [ ] 6.9.3 添加 P95 延迟 > 500ms 告警
  - [ ] 6.9.4 添加熔断器开启告警
  - [ ] 6.9.5 添加缓存命中率 < 50% 告警
- [ ] 6.10 验证 Prometheus 指标可查询
- [ ] 6.11 验证 Grafana 仪表板正常显示
- [ ] 6.12 代码审查：确保指标命名符合 Prometheus 规范
- [ ] 6.13 更新文档：添加监控使用说明
  - [ ] Repo-truth：`docs/guides/data-source/DATA_SOURCE_MONITORING_GUIDE.md` 存在，但当前口径仍包含缺失路径 `monitoring-stack/grafana-dashboards/data_source_monitoring.json`、`monitoring-stack/provisioning/dashboards/`，且未清晰对齐 `web/backend/app/main.py` 现有 `/metrics`（performance middleware）与 `src/core/data_source/metrics.py` / `src/monitoring/data_source_metrics.py` 的双轨现状，因此暂不视为已完成更新。

## 7. BatchProcessor 实现（5-7天）

> **局部事实说明（2026-04-27）**:
> `src/core/data_source/batch_processor.py` 已实现线程池、分组、`submit()` / `as_completed()`、超时控制和 `shutdown()`，但当前 spec 与任务语义聚焦的是治理层批量抓取主路径。
> `src/governance/core/fetcher_bridge.py` 仍保留串行 `fetch_batch_kline()`，对应测试 `src/governance/tests/test_fetcher_bridge.py` 也仍围绕串行行为编写，因此本段暂不因“已有组件文件”而机械勾选。

- [ ] 7.1 更新 `src/governance/core/fetcher_bridge.py`
- [ ] 7.2 在 `__init__()` 创建 `ThreadPoolExecutor(max_workers=10)`
- [ ] 7.3 实现 `fetch_batch_kline()` 并发版本
- [ ] 7.4 按数据源分组请求
- [ ] 7.5 使用 `executor.submit()` 并发执行
- [ ] 7.6 使用 `as_completed()` 收集结果
- [ ] 7.7 添加超时控制（`future.result(timeout=30)`）
- [ ] 7.8 实现异常隔离（单个失败不影响其他）
- [ ] 7.9 实现 `shutdown()` 方法（优雅关闭）
- [ ] 7.10 编写单元测试 `tests/integration/test_batch_processing.py`
  - [ ] 7.10.1 测试并发获取（100个symbol）
  - [ ] 7.10.2 测试超时控制（单个请求超时）
  - [ ] 7.10.3 测试异常隔离（部分失败）
  - [ ] 7.10.4 测试优雅关闭
  - [ ] 7.10.5 测试 DataSourceManager 保持同步
- [ ] 7.11 性能测试：对比优化前后的吞吐量
- [ ] 7.12 代码审查：确保线程安全和资源清理
- [ ] 7.13 更新文档：添加批处理使用说明

## 8. Phase 2 验收和部署（1-2天）
> **局部事实说明（2026-04-28）**:
> 本阶段多数开放项依赖完整测试闭环、灰度/生产部署与外部运行结果，而不是单纯本地代码存在即可关闭。
> 当前本地仓库尚不能直接证明：
> - 已对当前实现跑完“所有单元测试和集成测试”并通过
> - 已完成 10%→50%→100% 的灰度部署链路
> - 已在真实部署环境下拿到 P95 / 吞吐量 / 成本验收数据
> 因此 8.1-8.7 继续保持未完成更符合当前 repo-truth。

- [ ] 8.1 运行所有单元测试和集成测试
- [ ] 8.2 性能测试：验证吞吐量提升 3-5 倍
- [ ] 8.3 灰度部署到生产环境（10% 流量）
- [ ] 8.4 监控关键指标（P95 延迟、吞吐量、成本）
- [ ] 8.5 验收确认：
  - [ ] 8.5.1 Prometheus 指标可查询
  - [ ] 8.5.2 Grafana 仪表板正常显示
  - [ ] 8.5.3 批量获取性能提升 3-5 倍
  - [ ] 8.5.4 P95 延迟 < 200ms
  - [ ] 8.5.5 所有单元测试通过
- [ ] 8.6 修复发现的问题
- [ ] 8.7 逐步扩大灰度范围（50% → 100%）

---

# Phase 3: 高级特性（2-3个月，可选）

## 9. DataLineageTracker 实现（可选）
> **局部事实说明（2026-04-28）**:
> 当前仓库已存在“通用数据血缘能力”的相邻实现：
> - 核心模型与追踪器：`src/data_governance/lineage.py` 中的 `LineageTracker` / `LineageStorage`
> - 数据源集成：`src/core/data_source/lineage_integration.py` 中的 `LineageIntegrationMixin`
> - API 暴露：`web/backend/app/api/data_lineage.py`
> - 单元/API测试：`tests/unit/test_governance/test_lineage.py`、`tests/api/file_tests/test_data_lineage_api.py`
> 但它并不等于本提案原文目标：当前未落地 `src/governance/lineage/tracker.py`、未出现名为 `DataLineageTracker` 的类、未见 `networkx` 构建此专题血缘图主链路、也未见 Neo4j 存储闭环。
> 因此 9.1-9.8 继续保留未完成，避免把“相邻能力已存在”误写成“本 change 的 Phase 3 目标已按原路径与语义完成”。

- [ ] 9.1 创建 `src/governance/lineage/tracker.py` 文件
- [ ] 9.2 实现 `DataLineageTracker` 类
- [ ] 9.3 实现 `record_lineage()` 方法（记录数据血缘）
- [ ] 9.4 实现 `trace_lineage()` 方法（追溯血缘）
- [ ] 9.5 使用 `networkx` 构建血缘图
- [ ] 9.6 实现Neo4j 存储逻辑（可选）
- [ ] 9.7 编写单元测试和集成测试
- [ ] 9.8 更新文档：添加数据血缘使用说明

## 10. AdaptiveRateLimiter 实现（可选）
> **局部事实说明（2026-04-28）**:
> 当前仓库未找到 `src/core/data_source/adaptive_rate_limiter.py` 或 `AdaptiveRateLimiter` 类的现行实现。
> 现有 `_record_success()` / 监控计数逻辑主要分布于 `src/core/data_source/base.py`、`handler.py`、`monitoring.py`，属于既有监控/状态记录能力，不等于“基于错误率动态调节许可速率”的自适应限流器。
> 文档与历史 proposal 中虽有 `AdaptiveRateLimiter` 草图，但不能作为当前代码完成证据。
> 因此 10.1-10.8 继续保持未完成。

- [ ] 10.1 创建 `src/core/data_source/adaptive_rate_limiter.py` 文件
- [ ] 10.2 实现 `AdaptiveRateLimiter` 类
- [ ] 10.3 实现基于错误率的动态速率调整
- [ ] 10.4 实现 `acquire()` 方法（获取许可）
- [ ] 10.5 实现 `record_error()` 和 `record_success()` 方法
- [ ] 10.6 添加速率配置（initial_rate=10, min_rate=1, max_rate=100）
- [ ] 10.7 编写单元测试
- [ ] 10.8 更新文档：添加限流使用说明

## 11. Phase 3 验收和部署（可选）
> **局部事实说明（2026-04-28）**:
> Phase 3 的两项核心能力 `DataLineageTracker` / `AdaptiveRateLimiter` 当前都未按本提案原路径落地，
> 因而 11.1-11.6 不能在当前仓库状态下推进为“仅剩部署或验收”。
> 该段应视为未来可选阶段的外部运行与验收门禁，而非当前代码库里的待勾选收尾项。

- [ ] 11.1 运行所有单元测试和集成测试
- [ ] 11.2 性能测试：验证系统可用性达到 99.9%
- [ ] 11.3 部署到生产环境
- [ ] 11.4 监控关键指标（可用性、故障恢复时间）
- [ ] 11.5 验收确认：
  - [ ] 11.5.1 数据血缘追踪功能可用
  - [ ] 11.5.2 自适应限流正常运行
  - [ ] 11.5.3 系统可用性达到 99.9%
  - [ ] 11.5.4 所有测试通过
- [ ] 11.6 修复发现的问题

---

# 总体验收

## 12. 项目收尾（1周）
> **局部事实说明（2026-04-28）**:
> 当前仓库内可见的是局部指南与历史报告，例如：
> - `docs/guides/data-source/DATA_SOURCE_OPTIMIZATION_QUICK_REFERENCE.md`
> - `docs/guides/data-source/DATA_SOURCE_MONITORING_GUIDE.md`
> - `docs/guides/data-source/DATA_SOURCE_OPTIMIZATION_DEPLOYMENT_CHECKLIST.md`
> 但它们不足以直接证明以下收尾物已经形成：
> - 面向当前实现的完整性能压测报告 / 成本节约分析
> - 与现行 `/metrics` / 双轨指标实现对齐的运维手册
> - 覆盖本 change 全量能力的开发者文档
> - 最终验收会议、项目总结、以及 `openspec archive optimize-data-source-v2` 已执行
> 因此 12.1-12.7 当前继续保持未完成。

- [ ] 12.1 完整的性能压测报告
- [ ] 12.2 成本节约分析报告（对比优化前后）
- [ ] 12.3 运维手册（监控、告警、故障排查）
- [ ] 12.4 开发者文档（API 使用、配置说明）
- [ ] 12.5 最终验收会议
- [ ] 12.6 项目总结和经验教训
- [ ] 12.7 归档 OpenSpec 变更（`openspec archive optimize-data-source-v2`）
