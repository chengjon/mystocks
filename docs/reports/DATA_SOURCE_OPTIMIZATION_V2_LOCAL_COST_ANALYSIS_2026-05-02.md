# 数据源优化 V2 - 本地成本节约分析（2026-05-02）

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **本地分析说明**:
> 本文件是阶段性总结、报告、状态、修复记录、验证结果或交付回执，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内统计值、完成状态、结论、验证结果和修复结论如未重新复核，应视为历史快照，不得直接当作当前事实。

**分析日期**: 2026-05-02  
**分析环境**: `WSL 上的 Ubuntu 24.04.4 LTS`  
**核心口径**: 严格区分“已测代理指标”与“待部署验证收益”

---

## 1. 当前仓库里与成本相关的能力

| 能力 | 当前作用 | 代码锚点 |
|------|----------|----------|
| SmartCache | 减少调用方感知阻塞，提升命中率 | `src/core/data_source/smart_cache.py` |
| SmartRouter | 在路由决策中引入成本维度 | `src/core/data_source/smart_router.py` |
| BatchProcessor | 提高批量获取吞吐量 | `src/core/data_source/batch_processor.py` |
| 成本指标 | 暴露 `datasource_api_cost_estimated` | `src/core/data_source/metrics.py` |

---

## 2. 已测代理指标

### 2.1 SmartCache 命中率与延迟代理

来自 `tests/performance/test_phase1_datasource_benchmark.py` 同源 helper 的本地采样：

| 指标 | Baseline | Optimized | 解释 |
|------|----------|-----------|------|
| `hit_rate` | `0.50` | `1.00` | 更高命中率意味着更多读取被缓存屏蔽 |
| `avg_latency_ms` | `7.575` | `0.088` | 调用方阻塞时间显著降低 |
| loader 调用次数 | `5` | `5` | 该 workload 下未直接证明后台 reload 次数减少 |

结论：

- 当前本地证据支持“缓存层改善了读取体验与命中率”。
- 当前本地证据**不支持**“后台 API 调用总数已经按确定比例下降”。

### 2.2 SmartRouter 成本偏好

当前 `SmartRouter` 已实现多维度评分，其中包含成本维度：

- `cost_weight=0.3`
- endpoint shape 支持 `cost.is_free`

本地 A/B benchmark 证明它会做 richer decision，但没有直接产出“每个源的真实费用账单差异”。  
因此，当前能说的是：

- 仓库已经具备“把免费源偏好编码进决策逻辑”的能力；
- 尚未具备“基于 live endpoint mix 计算出真实人民币节省值”的证据。

### 2.3 成本指标可观测性

`src/core/data_source/metrics.py` 已声明：

- `datasource_api_cost_estimated`

这意味着部署后具备积累成本估算时序的基础。  
但在当前仓库内，还没有：

- 长周期样本；
- 生产 Prometheus 抓取值；
- 与历史月账单的对照表。

---

## 3. 当前可以安全宣称的成本结论

1. 当前代码已经具备成本优化的三个基础杠杆：
   - 更高缓存命中率
   - 免费源偏好路由
   - 成本指标可观测性
2. 当前本地 benchmark 更强地证明了“延迟屏蔽”和“吞吐量提升”，弱于直接证明“后台调用量下降”。
3. 因此，本地最稳妥的成本结论应降级为：
   - **存在明确的成本优化机制**
   - **存在可用于后续生产计量的成本指标**
   - **尚无足够本地证据写出真实金额或百分比节省**

---

## 4. 当前不能安全宣称的结论

以下结论在当前 repo-truth 下都不能写成已达成事实：

- “API 调用成本已降低 40%”
- “月度费用节省 ¥X”
- “年度节省 ¥Y”
- “免费源路由已经在真实流量中稳定覆盖 Z% 请求”

原因是缺少以下部署侧证据：

- 真实 endpoint mix
- 真实日/周/月调用量
- `datasource_api_cost_estimated` 的持续采样
- 与历史成本基线的同口径对比

---

## 5. 建议的部署期计量方法

要把本地能力变成正式成本结论，后续至少需要补齐：

1. **采集真实成本指标**
   - 按 endpoint 聚合 `datasource_api_cost_estimated`
   - 至少覆盖一周连续采样

2. **采集真实命中率**
   - 记录 `datasource_cache_hits_total`
   - 记录 `datasource_cache_misses_total`
   - 输出按 endpoint 的 hit rate

3. **采集真实路由分布**
   - 记录 SmartRouter 最终选择的 endpoint
   - 统计 free / paid source 占比

4. **做同口径对照**
   - 优化前基线周期
   - 优化后观测周期
   - 同市场时段、同接口集合、同采样窗口

---

## 6. 本地成本分析结论

这份报告可以支持 `12.2` 的 repo-local 交付物闭合，因为它已经明确回答：

- 当前仓库有哪些成本优化机制；
- 当前本地证据能支撑哪些结论；
- 当前本地证据不能支撑哪些结论；
- 后续部署期要补什么数据才能变成正式 ROI 报告。

但它**不能替代**最终财务或生产收益验收。
