# 数据源优化 V2 - 本地性能压测报告（2026-05-02）

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **本地报告说明**:
> 本文件是阶段性总结、报告、状态、修复记录、验证结果或交付回执，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内统计值、完成状态、结论、验证结果和修复结论如未重新复核，应视为历史快照，不得直接当作当前事实。

**采样日期**: 2026-05-02  
**采样环境**: `WSL 上的 Ubuntu 24.04.4 LTS`  
**采样范围**: SmartCache、BatchProcessor、SmartRouter、监控引用一致性  
**结论口径**: 仅声明本地 synthetic / stub workload 下的可复跑观察值

---

## 1. 证据来源

| 主题 | 主要锚点 | 本地验证方式 |
|------|----------|-------------|
| Phase 1 cache 优化前后对比 | `tests/performance/test_phase1_datasource_benchmark.py`、`tests/performance/test_smart_cache_benchmark.py` | 复跑 benchmark helper，并提取 `hit_rate` / `avg_latency_ms` |
| BatchProcessor 吞吐量 | `tests/performance/test_batch_processor_throughput.py` | 复跑 60-symbol stub workload |
| SmartRouter A/B | `tests/performance/test_smart_router_ab_benchmark.py` | 复跑 legacy priority sort vs `SmartRouter.route()` |
| 监控资产引用一致性 | `tests/performance/test_validate_monitoring_prometheus_references.py` | 依赖测试保证 dashboard / alert rule 与 `datasource_*` 指标族一致 |

---

## 2. SmartCache 本地基准

### 2.1 采样方式

- 代码锚点：
  - `tests/performance/test_phase1_datasource_benchmark.py`
  - `tests/performance/test_smart_cache_benchmark.py`
- 本次额外采样重用了同一组 helper：
  - `BlockingTtlBaselineCache`
  - `exercise_cache(...)`
  - `make_loader()`

### 2.2 观测值

| 指标 | Baseline | Optimized | 观察 |
|------|----------|-----------|------|
| `hit_rate` | `0.50` | `1.00` | 命中率提升 `+0.50` |
| `avg_latency_ms` | `7.575` | `0.088` | 平均读取延迟下降约 `98.8%` |
| loader 调用次数 | `5` | `5` | 本工作负载下，后台刷新保留了相同 reload 次数 |

### 2.3 解释边界

- 这组结果证明：当前 `SmartCache + soft expiry + background refresh` 在本地 synthetic access pattern 下，显著降低了调用方感知延迟，并提高了命中率。
- 它**不证明**真实环境里 API 调用总次数已经按同比例下降。
- 当前这个 workload 下，baseline 与 optimized 的 loader 调用次数相同，说明 `SmartCache` 在这组样本里主要提供的是“延迟屏蔽”，不是“绝对减少后台刷新次数”的直接证据。

---

## 3. BatchProcessor 本地吞吐量

### 3.1 采样方式

- 代码锚点：`tests/performance/test_batch_processor_throughput.py`
- 工作负载：
  - `60` 个 symbol
  - `ThroughputFetcher.fetch_kline()` 每次固定 sleep `0.02s`
  - `BatchProcessor(max_workers=10, timeout=1.0)`

### 3.2 观测值

| 指标 | 数值 |
|------|------|
| `batch_elapsed_s` | `0.127` |
| `serial_elapsed_s` | `1.230` |
| `speedup_x` | `9.66x` |
| `batch_errors` | `0` |
| `batch_count` | `60` |

### 3.3 解释边界

- 这证明当前治理层批量抓取主路径在本地 stub workload 下，吞吐量明显优于串行基线。
- 它支持 `7.11` 的 repo-local benchmark 结论。
- 它**不等同于** `8.2` / `8.5.3` 需要的真实部署吞吐量验收，也不能直接外推到真实数据源网络延迟、限流和源端不稳定场景。

---

## 4. SmartRouter A/B 本地观察

### 4.1 采样方式

- 代码锚点：`tests/performance/test_smart_router_ab_benchmark.py`
- 对比对象：
  - legacy：`priority + data_quality_score` 排序
  - optimized：`SmartRouter.route(...)`

### 4.2 观测值

| 指标 | 数值 |
|------|------|
| `legacy_elapsed_s` | `0.0104` |
| `smart_elapsed_s` | `0.0903` |
| `ratio` | `8.70x` |
| `legacy_selected` | `endpoint_0` |
| `smart_selected` | `endpoint_6` |

### 4.3 解释边界

- 当前 `SmartRouter` 的目标不是“单次纯排序计算更快”，而是引入性能、成本、负载、地域四个维度的 richer decision。
- 因此这项 benchmark 的可用结论是：
  - `SmartRouter.route()` 的本地计算开销明显高于 legacy 简单排序；
  - 但仍落在测试里约束的 `smart_elapsed < legacy_elapsed * 20` 安全范围内；
  - 路由收益需要放到真实 endpoint 质量和成本差异中评估，不能仅用 CPU 时间判断。

---

## 5. 监控资产一致性

当前已有 repo-local 测试覆盖：

- `tests/performance/test_validate_monitoring_prometheus_references.py::test_datasource_monitoring_assets_reference_declared_datasource_metrics`

它验证以下三者之间的引用一致性：

- `src/core/data_source/metrics.py`
- `config/monitoring-stack/grafana-dashboards/data_source_monitoring.json`
- `config/monitoring-stack/config/rules/data-source-alerts.yml`

本地可宣称的结论是：

- dashboard / alert rule 文件存在；
- 它们引用的 `datasource_*` 指标与当前代码中声明的指标族一致。

仍不能宣称的结论是：

- Grafana 页面已在浏览器里正常显示；
- Prometheus 实际抓取链路已在部署环境验收完成。

---

## 6. 本地性能结论

当前仓库已经具备以下 repo-local 证据：

1. `SmartCache` 在 synthetic workload 下显著降低了调用方感知延迟，并把命中率从 `0.50` 提升到 `1.00`。
2. `BatchProcessor` 在 60-symbol stub workload 下达到约 `9.66x` 的批量吞吐提升。
3. `SmartRouter` 已接入主路由链路，但其收益是“更丰富的 routing decision”，不是更低的本地排序 CPU 时间。
4. 数据源监控 dashboard / alert rule 与 `datasource_*` 指标族的引用关系已经被本地测试绑定。

当前仓库**尚不具备**以下证据：

- 灰度环境或生产环境下的端到端性能收益
- `4.5.1` / `4.5.2` / `4.5.3` 的最终业务阈值达成
- `6.11` 的真实 Grafana 页面渲染验收
- `8.x` / `11.x` / `12.5-12.7` 的部署、会议与归档收尾

因此，这份报告可用于完成 `12.1` 的**本地压测报告交付物**，但不能代替外部验收门禁。
