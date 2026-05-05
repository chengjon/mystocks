# 数据源优化 V2 - 本机 Prometheus Runtime 证据（2026-05-05）

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **本机证据说明**:
> 本文件记录的是 `PM2 backend -> /metrics -> Prometheus scrape -> PromQL` 在本机环境中的一次可复现证据链。
> 它可以证明 canonical `datasource_*` 指标已经进入当前监控主链，但不等同于灰度/生产窗口的持续观测、SLA 验收或 ROI 验收。

**采样时间**: `2026-05-05 10:48:41 CST` 起  
**采样环境**: `/opt/claude/mystocks_spec` 本机 PM2 + 本机 Prometheus  
**后端地址**: `http://localhost:8020`  
**Prometheus 地址**: `http://localhost:9090`  
**流量类型**: `mock.daily_kline` 手动测试路由，合法 `JWT + CSRF` 请求

---

## 1. 证据目标

本次只验证以下链路：

1. `mystocks-backend` PM2 进程已运行新代码
2. `GET /metrics` 暴露 canonical `datasource_*`
3. Prometheus 正在抓取 canonical PM2 backend `8020`
4. 一次真实请求后，PromQL 能查询到 `datasource_*` 时间序列

不验证：

- 真实灰度或生产流量
- 持续时间足够长的 SLA / ROI 结论
- `8.4` / `8.5.4` / `11.2` / `11.5.3` 这类外部验收项

---

## 2. 触发步骤

### 2.1 获取 CSRF Token

```bash
curl -s http://localhost:8020/api/csrf-token
```

### 2.2 触发一笔手动数据源测试请求

```bash
curl -s -X POST http://localhost:8020/api/v1/data-sources/mock.daily_kline/test \
  -H "Authorization: Bearer <jwt>" \
  -H "X-CSRF-Token: <csrf>" \
  -H "Content-Type: application/json" \
  -d '{"test_params":{"symbol":"000001","start_date":"20240102","end_date":"20240103","period":"daily"}}'
```

### 2.3 等待 Prometheus 至少完成一轮 scrape

```bash
sleep 20
```

### 2.4 查询 Prometheus

```bash
curl -s http://localhost:9090/api/v1/targets
curl -sG http://localhost:9090/api/v1/query \
  --data-urlencode 'query=datasource_api_calls_total{endpoint="mock.daily_kline",status="success"}'
curl -sG http://localhost:9090/api/v1/query \
  --data-urlencode 'query=histogram_quantile(0.95, sum by (le) (rate(datasource_api_latency_seconds_bucket{endpoint="mock.daily_kline"}[5m])))'
curl -sG http://localhost:9090/api/v1/query \
  --data-urlencode 'query=sum(rate(datasource_api_calls_total{endpoint="mock.daily_kline",status="success"}[5m]))'
```

---

## 3. 实际结果

### 3.1 Targets 状态

本次采样时，Prometheus `activeTargets` 中以下 job 为 `health="up"`：

- `mystocks-backend` -> `host.docker.internal:8020`
- `mystocks-data-sources` -> `host.docker.internal:8001`
- `node`
- `prometheus`
- `tempo-metrics`

### 3.2 Counter 查询

查询：

```promql
datasource_api_calls_total{endpoint="mock.daily_kline",status="success"}
```

返回：

- `job="mystocks-backend"`
- `instance="host.docker.internal:8020"`
- `value="3"`

这证明 canonical PM2 backend 的 `datasource_api_calls_total` 已被 Prometheus 抓到。

### 3.3 P95 延迟查询

查询：

```promql
histogram_quantile(
  0.95,
  sum by (le) (
    rate(datasource_api_latency_seconds_bucket{endpoint="mock.daily_kline"}[5m])
  )
)
```

返回：

- `value="0.00475"`

即本次短窗口下的本机 P95 约为 `4.75ms`。

### 3.4 请求速率查询

查询：

```promql
sum(rate(datasource_api_calls_total{endpoint="mock.daily_kline",status="success"}[5m]))
```

返回：

- `value="0.003508771929824561"`

这只是短窗口下的本机观测值，不具备业务吞吐量结论意义。

### 3.5 成本样本查询

查询：

```promql
datasource_api_cost_estimated{endpoint="mock.daily_kline"}
```

返回：

- `value="0"`

解释：

- 这不是“真实 API 成本已降到 0”，而是 `mock.daily_kline` 当前在 registry 中显式声明为 free endpoint，并通过 `cost.estimated_cny_per_call=0.0` 进入了 canonical runtime metrics 链路。
- 这条样本的意义是：`PM2 backend -> /metrics -> Prometheus scrape -> PromQL` 现在已经能承载显式成本指标，包括 `0.0` free sample。

---

## 4. 当前能安全宣称的结论

1. `mystocks-backend` 的 canonical PM2 `/metrics` 已暴露 `datasource_*` 指标
2. Prometheus 已在当前监控栈中成功抓取 `host.docker.internal:8020`
3. `datasource_api_calls_total`、`datasource_api_latency_seconds_bucket`、`datasource_api_cost_estimated` 的 PromQL 查询已跑通
4. `PM2 backend -> /metrics -> Prometheus scrape -> PromQL` 当前主链已在本机完成端到端验证

---

## 5. 当前不能安全宣称的结论

以下结论本报告都不能支持：

- `8.4` 已完成
- `8.5.4` 已完成
- `11.2` 或 `11.5.3` 的 `99.9%` 可用性结论
- 真实灰度/生产窗口下的 P95、吞吐量、成本下降

原因：

- 当前流量是本机 `mock.daily_kline` 手动请求
- 采样窗口很短
- 没有真实灰度流量
- 没有连续观测周期
- 当前只有显式 free/mock zero-cost sample，没有真实付费成本样本

---

## 6. 推荐用途

这份报告适合用于：

- 支撑 repo-truth 文档与 OpenSpec 台账
- 证明 canonical metrics 主链已打通
- 为后续灰度/生产验收提供“本机起点证据”

不适合用于：

- 直接关闭外部验收项
- 代替 SLA/ROI 报告
- 代替最终验收会议纪要
