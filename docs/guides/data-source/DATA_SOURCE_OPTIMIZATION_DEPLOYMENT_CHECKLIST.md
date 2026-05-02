# 数据源优化 V2 - 部署检查清单

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

> **检查清单说明**:
> 本文件用于提供某一局部主题的使用方法、操作步骤、背景说明或参考材料，帮助理解仓库中的具体实践。
> 其中的命令、路径、流程和示例应与 `architecture/STANDARDS.md`、当前代码实现及最新验证结果一并核对，不应单独视为共享规则或当前状态的唯一事实来源。

**最后更新**: 2026-05-02  
**配套文档**:
- [`DATA_SOURCE_OPERATIONS_MANUAL.md`](./DATA_SOURCE_OPERATIONS_MANUAL.md)
- [`DATA_SOURCE_DEVELOPER_GUIDE.md`](./DATA_SOURCE_DEVELOPER_GUIDE.md)
- [`DATA_SOURCE_MONITORING_GUIDE.md`](./DATA_SOURCE_MONITORING_GUIDE.md)
- [`DATA_SOURCE_OPTIMIZATION_QUICK_REFERENCE.md`](./DATA_SOURCE_OPTIMIZATION_QUICK_REFERENCE.md)

---

## 1. 交付物核对

- [x] `src/core/data_source/smart_cache.py`
- [x] `src/core/data_source/circuit_breaker.py`
- [x] `src/core/data_source/data_quality_validator.py`
- [x] `src/core/data_source/smart_router.py`
- [x] `src/core/data_source/metrics.py`
- [x] `src/core/data_source/batch_processor.py`
- [x] `src/core/data_source/adaptive_rate_limiter.py`
- [x] `src/governance/lineage/tracker.py`
- [x] `config/monitoring-stack/grafana-dashboards/data_source_monitoring.json`
- [x] `config/monitoring-stack/config/rules/data-source-alerts.yml`

> **边界提醒**:
> 上述文件存在，只代表 repo-owned 资产已落盘；不代表它们都已经进入 live deployment 或浏览器内人工验收。

---

## 2. 部署前本地验证

### 2.1 Phase 1 回归

- [ ] 运行：
  ```bash
  pytest \
    tests/unit/test_smart_cache.py \
    tests/unit/test_circuit_breaker.py \
    tests/unit/test_circuit_breaker_integration.py \
    tests/unit/test_data_quality_validator.py \
    tests/unit/test_gpu_validator_integration.py \
    -q --no-cov
  ```

### 2.2 Phase 2 回归

- [ ] 运行：
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

### 2.3 可选能力回归

- [ ] 运行：
  ```bash
  pytest \
    tests/unit/test_governance/test_data_lineage_tracker.py \
    tests/integration/test_data_lineage_tracker_integration.py \
    tests/unit/test_adaptive_rate_limiter.py \
    -q --no-cov
  ```

### 2.4 本地 benchmark

- [ ] 运行：
  ```bash
  pytest tests/performance/test_phase1_datasource_benchmark.py -q --no-cov --run-performance
  pytest tests/performance/test_smart_router_ab_benchmark.py -q --no-cov --run-performance
  pytest tests/performance/test_batch_processor_throughput.py -q --no-cov --run-performance
  ```

---

## 3. 监控与观测

- [ ] 后端运行时 `/metrics` 可访问
  ```bash
  curl http://localhost:8020/metrics | head
  ```

- [ ] `datasource_*` 本地指标测试通过
  ```bash
  pytest tests/unit/test_metrics.py tests/unit/test_data_source_metrics_integration.py -q --no-cov
  ```

- [ ] dashboard / alert rule 与当前指标族引用一致
  ```bash
  pytest tests/performance/test_validate_monitoring_prometheus_references.py -q --no-cov
  ```

- [ ] 若需要独立 exporter，再单独验证 `scripts/runtime/start_metrics_server.py`

> **边界提醒**:
> 以上验证仍不等于 Grafana 浏览器页面已正常显示；`6.11` 仍需部署侧人工验收。

---

## 4. 外部门禁（本清单不代替）

以下事项不因本清单完成而自动关闭：

- [ ] 灰度部署到测试/生产环境
- [ ] 实时监控命中率、成本、P95、吞吐量
- [ ] Grafana 页面人工验收
- [ ] 最终验收会议
- [ ] 项目总结会议
- [ ] `openspec archive optimize-data-source-v2`

---

## 5. 推荐使用方式

1. 先读 [`DATA_SOURCE_DEVELOPER_GUIDE.md`](./DATA_SOURCE_DEVELOPER_GUIDE.md) 确认主链路与验证矩阵
2. 再读 [`DATA_SOURCE_OPERATIONS_MANUAL.md`](./DATA_SOURCE_OPERATIONS_MANUAL.md) 执行本地运维检查
3. 最后把外部部署与验收结果记录回 OpenSpec 台账
