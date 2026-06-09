# optimize-data-source-v2 外部验收交接文档

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **交接目的**:
> 本文档面向后续执行灰度发布、live 观测、SLA/ROI 验收和归档动作的接手者。
> 它不替代 OpenSpec、部署脚本或运行时事实；共享口径仍以 `architecture/STANDARDS.md`、`openspec/changes/optimize-data-source-v2/tasks.md` 和实际执行结果为准。

**最后更新**: 2026-05-05
**对应 OpenSpec change**: `optimize-data-source-v2`
**当前进度**: `openspec list` 显示 `108/120 tasks`

---

## 1. 当前状态概览

这条线的 **repo-local 实现已经收口**，但 **外部验收尚未完成**。

当前已经明确的边界：

- 仓库内实现、repo-local 回归、本地 benchmark、本机 PM2 和本机 Prometheus 证据都已收齐
- 剩余未闭合项全部依赖外部部署、灰度流量、持续观测、会议纪要或正式 archive 时机
- 当前 canonical PM2 public routes 里，没有现成 HTTP 路由会自然穿过 `DataSourceManagerV2` 的 endpoint-local cache
- 因此，如果后续还想拿到 **PM2 public-route cache hit/miss** 证据，这不再是“继续排查现有路由”，而是新的已审批行为变更

---

## 2. 已完成事实

截至 2026-05-05，下面这些事实已经成立：

- `openspec validate optimize-data-source-v2 --strict` 通过
- Phase 1 repo-local 组件、测试和 synthetic performance 证据已落盘
- Phase 2 repo-local 组件、监控链路、Grafana/Prometheus 资产引用一致性和本机 Prometheus proof 已落盘
- Phase 3 repo-local 可选组件和回归已落盘
- canonical PM2 backend `http://localhost:8020/metrics` 已能暴露 `datasource_*`
- canonical PM2 runtime + Prometheus 已能观测：
  - `datasource_api_calls_total`
  - `datasource_api_latency_seconds`
  - `datasource_api_cost_estimated`
- manager-driven repeated call 已能在 repo-local 证明：
  - `datasource_cache_hits_total`
  - `datasource_cache_misses_total`

关键真相源：

- [tasks.md](/opt/claude/mystocks_spec/openspec/changes/optimize-data-source-v2/tasks.md)
- [REPO_LOCAL_STATUS.md](/opt/claude/mystocks_spec/openspec/changes/optimize-data-source-v2/REPO_LOCAL_STATUS.md)
- [ITERATION_CLOSEOUT_2026-05-05.md](/opt/claude/mystocks_spec/openspec/changes/optimize-data-source-v2/ITERATION_CLOSEOUT_2026-05-05.md)
- [DATA_SOURCE_OPTIMIZATION_DEPLOYMENT_CHECKLIST.md](/opt/claude/mystocks_spec/docs/guides/data-source/DATA_SOURCE_OPTIMIZATION_DEPLOYMENT_CHECKLIST.md)
- [DATA_SOURCE_MONITORING_GUIDE.md](/opt/claude/mystocks_spec/docs/guides/data-source/DATA_SOURCE_MONITORING_GUIDE.md)
- [DATA_SOURCE_OPTIMIZATION_V2_LOCAL_PROMETHEUS_RUNTIME_PROOF_2026-05-05.md](/opt/claude/mystocks_spec/docs/reports/DATA_SOURCE_OPTIMIZATION_V2_LOCAL_PROMETHEUS_RUNTIME_PROOF_2026-05-05.md)

---

## 3. 剩余外部项

当前剩余项应按下面四类理解，而不是当作仓库内开发 backlog：

### 3.1 部署激活

- `4.3` 测试环境灰度部署
- `8.3` 生产灰度发布
- `11.3` Phase 3 生产部署

### 3.2 live 观测

- `4.4` 监控缓存命中率 / API 调用成本 / 响应时间
- `8.4` 监控 P95 延迟 / 吞吐量 / 成本
- `11.4` 监控可用性 / 恢复时间

### 3.3 ROI / SLA 验收

- `4.5.2` API 调用成本降低 `40%`
- `8.5.4` 真实灰度或生产窗口下 `P95 < 200ms`
- `11.2` 验证 `99.9%` 可用性
- `11.5.3` 系统可用性达到 `99.9%`

### 3.4 流程收尾

- `8.7` 灰度扩量 `50% -> 100%`
- `12.5` 最终验收会议
- `12.7` `openspec archive optimize-data-source-v2`

---

## 4. 当前环境约束

接手前必须知道这几个现实约束：

1. 当前 PM2 backend 环境仍是 `USE_MOCK_DATA=true`
   这意味着本机现状不构成真实灰度或真实 ROI 验收窗口。

2. 当前 host `3000` 端口被外部进程占用过
   最近一次 Grafana live 验收使用的是 `GRAFANA_PORT=3301` / `GRAFANA_ROOT_URL=http://localhost:3301` 的 host override；
   repo 默认配置仍保持 `3000`。

3. 当前 public route inventory 已明确
   - `POST /api/v1/data-sources/{endpoint_name}/test` 是 direct handler instrumentation
   - `/backtest/*` 当前走 `DataService`
   - `/api/v1/strategy/backtest/run` 只落库并起 mock timeseries 后台任务

4. 因为第 3 条，public-route cache hit/miss 证据不再属于本条 change 的 repo-local 未完成项
   若确有业务需要，必须新开已审批行为变更。

---

## 5. 推荐执行顺序

建议按下面顺序推进，不要跳步勾选：

1. 先完成 `4.3`
   在真实测试环境激活变更，确认使用的不是本机 mock-only 前提。

2. 再做 `4.4` 和 `4.5.2`
   先拿连续观测，再判断成本结论是否成立。

3. 然后做 `8.3`
   进入生产灰度发布。

4. 再做 `8.4` 和 `8.5.4`
   用真实灰度窗口判断 `P95`、吞吐量和成本，不接受本机 synthetic 或短窗口 mock 结果替代。

5. 再做 `8.7`
   从 `50%` 扩量到 `100%`。

6. 再做 `11.2 / 11.3 / 11.4 / 11.5.3`
   这是正式 SLA 和可用性验收阶段。

7. 最后做 `12.5 / 12.7`
   验收会议和 OpenSpec archive 必须基于前面证据齐备。

---

## 6. 每类任务需要的证据

### 6.1 部署激活

至少记录：

- 执行日期
- 部署环境
- 发布命令或发布系统记录
- 发布后服务地址
- 发布后健康检查结果

### 6.2 live 观测

至少记录：

- Prometheus 查询语句
- 查询窗口
- 环境名称
- 监控截图或导出结果
- 是否真实流量而非 mock 流量

### 6.3 ROI / SLA 验收

至少记录：

- 与历史基线同口径的比较方法
- 样本时间窗口
- 使用的指标定义
- 结论是否满足 task 门槛
- 若未满足，不能“近似勾选”

### 6.4 流程收尾

至少记录：

- 最终验收会议纪要路径
- archive 执行命令
- archive commit hash

---

## 7. 现场命令入口

### 7.1 OpenSpec 与状态确认

```bash
openspec validate optimize-data-source-v2 --strict
openspec list | rg "optimize-data-source-v2"
```

### 7.2 PM2 / 服务状态

```bash
pm2 jlist
curl http://localhost:8020/health/ready
curl -I http://localhost:3020/
```

### 7.3 监控栈验通

```bash
env GRAFANA_PORT=3301 GRAFANA_ROOT_URL=http://localhost:3301 \
  bash config/monitoring-stack/verify_monitoring.sh
```

### 7.4 Prometheus 查询样例

```bash
curl "http://localhost:9090/api/v1/query?query=datasource_api_calls_total"
curl "http://localhost:9090/api/v1/query?query=datasource_api_cost_estimated"
curl "http://localhost:9090/api/v1/query?query=histogram_quantile(0.95,sum by (le)(rate(datasource_api_latency_seconds_bucket[5m])))"
```

---

## 8. 更新规则

后续接手者在关闭外部项时，建议同时更新这些位置：

1. [tasks.md](/opt/claude/mystocks_spec/openspec/changes/optimize-data-source-v2/tasks.md)
2. [DATA_SOURCE_OPTIMIZATION_DEPLOYMENT_CHECKLIST.md](/opt/claude/mystocks_spec/docs/guides/data-source/DATA_SOURCE_OPTIMIZATION_DEPLOYMENT_CHECKLIST.md)
3. 相关报告文档，放在 `docs/reports/` 下
4. Graphiti memory

不要做的事：

- 不要用 repo-local synthetic benchmark 代替灰度/生产验收
- 不要把 mock route 的短窗口 Prometheus 样本写成真实 ROI 结论
- 不要把 public-route cache hit/miss 缺失继续当成“还没修完的 plumbing”

---

## 9. 当前结论

`optimize-data-source-v2` 现在不是“继续写代码”的问题，而是“按外部验收顺序收证据”的问题。

如果后续目标仍然是这条 change 的闭合，最自然的下一步是：

1. 在真实测试或灰度环境完成 `4.3`
2. 立刻开始 `4.4` / `4.5.2` 的连续观测
3. 证据足够后再推进 `8.x` 和 `11.x`

如果后续目标变成 **PM2 public-route cache hit/miss live proof**，那应该单独起一个新的已审批行为变更，而不是继续把它塞进当前 closeout 范围。
