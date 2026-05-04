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

### 4.1 与 OpenSpec 剩余项的映射

| 分类 | OpenSpec task | 仍需的外部证据 |
|------|---------------|----------------|
| 部署激活 | `4.3` | 测试环境灰度部署记录 |
| live 观测 | `4.4` | 灰度期缓存命中率 / 成本 / 响应时间连续观测 |
| ROI 验收 | `4.5.2` | 与历史基线同口径的真实成本下降样本 |
| 人工监屏 | `6.11` | Grafana 浏览器页面实际渲染截图或验收记录 |
| 部署激活 | `8.3` | 10% 生产流量灰度发布记录 |
| live 观测 | `8.4` | P95 延迟 / 吞吐量 / 成本的生产灰度监控样本 |
| 人工监屏 | `8.5.2` | Grafana 仪表板正常显示的人工验收记录 |
| SLO 验收 | `8.5.4` | 真实灰度或生产窗口下 `P95 < 200ms` 观测值 |
| 部署扩量 | `8.7` | `50% -> 100%` 灰度扩量记录 |
| SLA 验收 | `11.2` | 连续可用性观测，支撑 `99.9%` 结论 |
| 部署激活 | `11.3` | Phase 3 组件生产部署记录 |
| live 观测 | `11.4` | 可用性与故障恢复时间的生产监控样本 |
| SLA 验收 | `11.5.3` | `99.9%` 可用性达成的正式验收记录 |
| 流程收尾 | `12.5` | 最终验收会议纪要 |
| 归档动作 | `12.7` | `openspec archive optimize-data-source-v2` 执行结果 |

> **说明**:
> 上表刻意把 repo-local 能完成的前置校验与真正的外部验收分开。即使本清单第 2、3 节全部通过，也不能直接勾选这些项。
>
> **现场阻塞事实（2026-05-05）**:
> - 本地 `docker start` 后，`mystocks-prometheus` 可在 `http://localhost:9090/-/ready` 返回 ready。
> - 但现存 `mystocks-grafana` 是历史容器，`docker inspect` 显示宿主机 `PortBindings` 为空；容器内部健康接口仅在 `127.0.0.1:3002/api/health` 成功，因此 `http://localhost:3000` 目前不能作为验收入口。
> - `http://localhost:9090/api/v1/targets` 当前显示 `mystocks-backend`、`mystocks-data-sources` 等 target 抓取的仍是 `host.docker.internal:8000/8001`，在当前 Linux + backend `8020` 环境下为 `down`。
> - 因此 `6.11` / `8.5.2` 的下一步不是补 repo-local 测试，而是先修复 Grafana 可达性和 Prometheus scrape target 漂移。

---

## 5. 推荐使用方式

1. 先读 [`DATA_SOURCE_DEVELOPER_GUIDE.md`](./DATA_SOURCE_DEVELOPER_GUIDE.md) 确认主链路与验证矩阵
2. 再读 [`DATA_SOURCE_OPERATIONS_MANUAL.md`](./DATA_SOURCE_OPERATIONS_MANUAL.md) 执行本地运维检查
3. 最后把外部部署与验收结果记录回 OpenSpec 台账
