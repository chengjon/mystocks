# Phase 1: 核心稳定性（1-2周）

## 1. SmartCache 实现（3-4天）

- [ ] 1.1 创建 `src/core/data_source/smart_cache.py` 文件
- [ ] 1.2 实现 `SmartCache` 类（LRU + TTL + 后台刷新）
- [ ] 1.3 添加 `threading.RLock` 保护并发访问
- [ ] 1.4 实现 `_trigger_refresh()` 方法（启动后台线程）
- [ ] 1.5 实现 `_run_refresh()` 方法（执行刷新逻辑）
- [ ] 1.6 添加 `refreshing` set 防止重复刷新
- [ ] 1.7 集成 `ThreadPoolExecutor(max_workers=5)` 限制并发刷新
- [ ] 1.8 更新 `src/core/data_source/base.py` 替换 `LRUCache` 为 `SmartCache`
- [ ] 1.9 编写单元测试 `tests/unit/test_smart_cache.py`
  - [ ] 1.9.1 测试缓存命中（fresh data）
  - [ ] 1.9.2 测试缓存过期触发预刷新
  - [ ] 1.9.3 测试软过期（返回旧数据）
  - [ ] 1.9.4 测试硬过期（返回 None）
  - [ ] 1.9.5 测试 LRU 淘汰
  - [ ] 1.9.6 测试并发访问（100线程并发）
  - [ ] 1.9.7 测试后台刷新失败处理
  - [ ] 1.9.8 测试线程池限制（max_workers=5）
- [ ] 1.10 性能测试：对比优化前后的缓存命中率和响应时间
- [ ] 1.11 代码审查：确保线程安全性和错误处理
- [ ] 1.12 更新文档：添加 SmartCache 使用说明

## 2. CircuitBreaker 实现（3-4天）

- [ ] 2.1 创建 `src/core/data_source/circuit_breaker.py` 文件
- [ ] 2.2 定义 `CircuitState` 枚举（CLOSED, OPEN, HALF_OPEN）
- [ ] 2.3 实现 `CircuitBreaker` 类
- [ ] 2.4 添加 `threading.Lock` 保护状态转换
- [ ] 2.5 实现 `call()` 方法（执行调用并自动熔断）
- [ ] 2.6 实现 `_should_attempt_reset()` 方法（检查是否超时）
- [ ] 2.7 实现 `_on_success()` 方法（成功回调）
- [ ] 2.8 实现 `_on_failure()` 方法（失败回调）
- [ ] 2.9 添加 `CircuitBreakerOpenError` 异常类
- [ ] 2.10 集成到 `src/core/data_source/base.py._call_endpoint()`
- [ ] 2.11 为每个 endpoint 创建独立的 CircuitBreaker 实例
- [ ] 2.12 编写单元测试 `tests/unit/test_circuit_breaker.py`
  - [ ] 2.12.1 测试 CLOSED 状态正常调用
  - [ ] 2.12.2 测试达到阈值后进入 OPEN 状态
  - [ ] 2.12.3 测试超时后进入 HALF_OPEN 状态
  - [ ] 2.12.4 测试试探成功后回到 CLOSED 状态
  - [ ] 2.12.5 测试试探失败后回到 OPEN 状态
  - [ ] 2.12.6 测试并发状态转换（10线程并发）
  - [ ] 2.12.7 测试剩余时间反馈
  - [ ] 2.12.8 测试可配置阈值
- [ ] 2.13 集成测试：模拟故障场景验证熔断器行为
- [ ] 2.14 代码审查：确保状态转换逻辑正确
- [ ] 2.15 更新文档：添加 CircuitBreaker 使用说明

## 3. DataQualityValidator 实现（3-4天）

- [ ] 3.1 创建 `src/core/data_source/data_quality_validator.py` 文件
- [ ] 3.2 实现 `DataQualityValidator` 类
- [ ] 3.3 实现 `_logic_check()` 方法（OHLC 基础逻辑）
- [ ] 3.4 实现 `_business_check()` 方法（业务规则）
  - [ ] 3.4.1 检测极端价格波动（>20%）
  - [ ] 3.4.2 检测异常成交量（>10倍均值）
  - [ ] 3.4.3 检测停牌数据
  - [ ] 3.4.4 检测零或负价格
- [ ] 3.5 实现 `_statistical_check()` 方法（3-sigma 异常检测）
- [ ] 3.6 实现 `_cross_source_check()` 方法（跨源验证）
- [ ] 3.7 实现 `validate()` 主方法（协调所有检查）
- [ ] 3.8 集成到 `src/governance/engine/gpu_validator.py`
- [ ] 3.9 编写单元测试 `tests/unit/test_data_quality_validator.py`
  - [ ] 3.9.1 测试 OHLC 逻辑验证（通过/失败场景）
  - [ ] 3.9.2 测试业务规则验证（极端价格、异常成交量、停牌）
  - [ ] 3.9.3 测试统计异常检测（3-sigma）
  - [ ] 3.9.4 测试跨源验证（一致性检查）
  - [ ] 3.9.5 测试验证汇总（summary）
  - [ ] 3.9.6 测试 GPU 加速验证（100,000行数据）
- [ ] 3.10 准备 100+ 测试用例数据（覆盖各种异常场景）
- [ ] 3.11 代码审查：确保验证逻辑完整
- [ ] 3.12 更新文档：添加 DataQualityValidator 使用说明

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

- [ ] 5.1 创建 `src/core/data_source/smart_router.py` 文件
- [ ] 5.2 实现 `SmartRouter` 类
- [ ] 5.3 实现 `_score_by_performance()` 方法（P50/P95/P99 + 成功率）
- [ ] 5.4 实现 `_adjust_by_cost()` 方法（成本优化）
- [ ] 5.5 实现 `_adjust_by_load()` 方法（负载均衡）
- [ ] 5.6 实现 `_adjust_by_location()` 方法（地域感知）
- [ ] 5.7 实现 `route()` 主方法（多维度决策）
- [ ] 5.8 集成到 `src/core/data_source/router.py.get_best_endpoint()`
- [ ] 5.9 添加配置项：权重（performance=0.4, cost=0.3, load=0.2, location=0.1）
- [ ] 5.10 编写单元测试 `tests/unit/test_smart_router.py`
  - [ ] 5.10.1 测试性能评分计算
  - [ ] 5.10.2 测试成本优化（免费源优先）
  - [ ] 5.10.3 测试负载均衡（避免过载）
  - [ ] 5.10.4 测试地域感知（最近节点）
  - [ ] 5.10.5 测试多维度综合评分
- [ ] 5.11 A/B 测试：对比新旧路由策略的性能差异
- [ ] 5.12 代码审查：确保路由逻辑正确
- [ ] 5.13 更新文档：添加 SmartRouter 使用说明

## 6. Prometheus 监控集成（5-7天）

- [ ] 6.1 创建 `src/core/data_source/metrics.py` 文件
- [ ] 6.2 定义 Prometheus 指标（Histogram, Counter, Gauge）
  - [ ] 6.2.1 `datasource_api_latency_seconds` (Histogram)
  - [ ] 6.2.2 `datasource_api_calls_total` (Counter)
  - [ ] 6.2.3 `datasource_data_quality` (Gauge)
  - [ ] 6.2.4 `datasource_cache_hits_total` (Counter)
  - [ ] 6.2.5 `datasource_cache_misses_total` (Counter)
  - [ ] 6.2.6 `datasource_circuit_breaker_state` (Gauge)
  - [ ] 6.2.7 `datasource_api_cost_estimated` (Gauge)
- [ ] 6.3 实现 `track_api_call()` 装饰器
- [ ] 6.4 实现 `DataSourceMetrics` 类（指标收集器）
- [ ] 6.5 在 `DataSourceManagerV2._call_endpoint()` 添加指标埋点
- [ ] 6.6 在 `web/backend/app/main.py` 集成 `/metrics` 端点
  - [ ] 6.6.1 添加 `/metrics` 路由
  - [ ] 6.6.2 返回 Prometheus exposition 格式
  - [ ] 6.6.3 使用全局 REGISTRY
- [ ] 6.7 创建 Grafana 仪表板配置
  - [ ] 6.7.1 创建 `grafana/dashboards/data-source-metrics.json`
  - [ ] 6.7.2 添加 API 延迟面板（P50/P95/P99）
  - [ ] 6.7.3 添加成功率面板
  - [ ] 6.7.4 添加缓存命中率面板
  - [ ] 6.7.5 添加熔断器状态面板
  - [ ] 6.7.6 添加 API 成本面板
- [ ] 6.8 编写单元测试 `tests/unit/test_metrics.py`
  - [ ] 6.8.1 测试指标记录（成功/失败）
  - [ ] 6.8.2 测试延迟 histogram
  - [ ] 6.8.3 测试缓存 hit/miss 计数
  - [ ] 6.8.4 测试熔断器状态 gauge
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

## 7. BatchProcessor 实现（5-7天）

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

- [ ] 9.1 创建 `src/governance/lineage/tracker.py` 文件
- [ ] 9.2 实现 `DataLineageTracker` 类
- [ ] 9.3 实现 `record_lineage()` 方法（记录数据血缘）
- [ ] 9.4 实现 `trace_lineage()` 方法（追溯血缘）
- [ ] 9.5 使用 `networkx` 构建血缘图
- [ ] 9.6 实现Neo4j 存储逻辑（可选）
- [ ] 9.7 编写单元测试和集成测试
- [ ] 9.8 更新文档：添加数据血缘使用说明

## 10. AdaptiveRateLimiter 实现（可选）

- [ ] 10.1 创建 `src/core/data_source/adaptive_rate_limiter.py` 文件
- [ ] 10.2 实现 `AdaptiveRateLimiter` 类
- [ ] 10.3 实现基于错误率的动态速率调整
- [ ] 10.4 实现 `acquire()` 方法（获取许可）
- [ ] 10.5 实现 `record_error()` 和 `record_success()` 方法
- [ ] 10.6 添加速率配置（initial_rate=10, min_rate=1, max_rate=100）
- [ ] 10.7 编写单元测试
- [ ] 10.8 更新文档：添加限流使用说明

## 11. Phase 3 验收和部署（可选）

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

- [ ] 12.1 完整的性能压测报告
- [ ] 12.2 成本节约分析报告（对比优化前后）
- [ ] 12.3 运维手册（监控、告警、故障排查）
- [ ] 12.4 开发者文档（API 使用、配置说明）
- [ ] 12.5 最终验收会议
- [ ] 12.6 项目总结和经验教训
- [ ] 12.7 归档 OpenSpec 变更（`openspec archive optimize-data-source-v2`）
