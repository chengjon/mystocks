# 2026-03-04 运行日志问题修复交接说明

## 1. 任务背景

根据 `PM2` 运行日志（重点：`/root/.pm2/logs/mystocks-frontend-out.log`、`/root/.pm2/logs/mystocks-backend-out.log`）对前后端运行期问题进行分级修复，并完成回归验证，形成可交接结果。

当前运行真值端口：
- Frontend: `3020`
- Backend: `8020`

---

## 2. 本次已完成工作

### 2.1 P0 修复：`/api/v1/strategy/strategies` 递归导致 500

**现象**
- 后端日志长期出现 `maximum recursion depth exceeded`
- 接口 `/api/v1/strategy/strategies` 返回 `500`

**根因**
- `web/backend/app/api/strategy_management/get_monitoring_db.py` 的 `list_strategies` 在 Mock 失败时 `return await list_strategies(...)`，导致递归重入直至栈溢出。

**修复**
- 将“Mock失败后的降级”改为：直接进入真实数据库分支，不再自调用。
- 同时补充错误日志和监控记录参数，避免异常路径丢失上下文。

**相关文件**
- `web/backend/app/api/strategy_management/get_monitoring_db.py`
- `web/backend/tests/test_strategy_list_fallback.py`（新增）

---

### 2.2 P0 修复：`/trade/terminal` 页面接口不可用导致错误泛洪

**现象**
- 页面调用 `/api/trading/*` 系列接口（当前未挂载）出现 404。
- 前端重复 `console.error`，形成日志噪音与告警泛洪。

**修复**
- 为 `useTradingDashboard` 增加降级机制：
  - 404/网络错误时注入 fallback 数据（交易状态、策略列表、市场快照、风险指标）。
  - 同一不可用接口只告警一次。
  - 对 404 接口做“不可用缓存”，后续直接走 fallback，减少重复请求。
- 将高频失败日志从错误级降为可控告警路径。

**相关文件**
- `web/frontend/src/views/composables/useTradingDashboard.ts`
- `web/frontend/src/views/composables/__tests__/useTradingDashboard.spec.ts`（新增）

---

### 2.3 P1 修复：`/api/v1/data-sources/config` 路由冲突导致 404

**现象**
- 前端访问 `/api/v1/data-sources/config` 时会被后端 `/{endpoint_name}` 抢匹配，返回 `接口不存在: config`。

**修复**
- 前端读取改为 `/api/v1/data-sources/config/`（尾斜杠），避开冲突。
- 保留写入接口路径不变。

**相关文件**
- `web/frontend/src/api/index.ts`
- `web/frontend/src/api/__tests__/monitoringApi.spec.ts`（新增）

---

## 3. 验证与结果

### 3.1 单项验证

- `npm --prefix web/frontend run type-check`：通过
- `npm --prefix web/frontend run test -- src/views/composables/__tests__/useTradingDashboard.spec.ts`：通过
- `npm --prefix web/frontend run test -- src/api/__tests__/monitoringApi.spec.ts`：通过
- `pytest -q --no-cov web/backend/tests/test_strategy_list_fallback.py`：通过

### 3.2 门禁与综合回归

- `bash scripts/run_e2e_pm2.sh`：通过（`8/8`）
- `bash scripts/tests/test/run-comprehensive-tests.sh`：通过（`35/35`）
- 最新综合报告：
  - `logs/tests/test-report-20260304-011004.md`

### 3.3 日志验收结论（关键）

- `/api/v1/strategy/strategies`：
  - 历史为 500（递归栈溢出）
  - 修复后已出现稳定 200（例如 `2026-03-04 01:04` 之后记录）
- `/api/v1/data-sources/config/`：
  - 持续 200
- 前端日志中未再检出：
  - `Failed to load trading data`
  - `Failed to load strategy performance`
  - `Failed to load market data`
  - `Failed to load risk data`

---

## 4. 变更文件清单（本次任务核心）

### Backend
- `web/backend/app/api/strategy_management/get_monitoring_db.py`（修改）
- `web/backend/tests/test_strategy_list_fallback.py`（新增）

### Frontend
- `web/frontend/src/views/composables/useTradingDashboard.ts`（修改）
- `web/frontend/src/views/composables/__tests__/useTradingDashboard.spec.ts`（新增）
- `web/frontend/src/api/index.ts`（修改）
- `web/frontend/src/api/__tests__/monitoringApi.spec.ts`（新增）

---

## 5. 当前遗留问题（交接重点）

### 5.1 `/api/trading/*` 仍为 404（已做前端降级，不阻塞运行）

仍未挂载（或不可用）的接口包括：
- `/api/trading/status`
- `/api/trading/strategies/performance`
- `/api/trading/market/snapshot`
- `/api/trading/risk/metrics`

当前状态：
- 前端已降级可用，不再错误泛洪。
- 后端日志仍能看到少量首次请求 404（正常，因未提供真实路由）。

建议后续：
1. 修复 `trading_monitor` 依赖链（此前直接挂载会触发模块缺失），恢复真实路由；或
2. 将页面切换到当前已存在的 `/api/v1/trade/*` 等可用域接口，统一契约。

### 5.2 其他历史债务（本轮未处理）

- 个别 trade 相关旧接口如 `/api/v1/trade/positions`、`/api/v1/trade/signals` 在日志中仍有 404 记录。
- 不属于本轮“运行阻塞”问题，但建议纳入下一批接口对齐清单。

---

## 6. 可直接执行的后续动作建议

1. 以 `FRONTEND_OPTIMIZATION_STRATEGY_V3` 为上位策略，启动“交易域 API 对齐”专项（路由、菜单、页面契约统一）。
2. 对 `/api/trading/*` 制定二选一路线（恢复后端路由 vs 前端改用现有路由）并固化到文档与 CI 校验。
3. 将本次新增的 3 个测试用例纳入默认回归集合，避免后续回归复发。

---

## 7. 结论

本次任务已完成“运行期高优先问题收敛”：
- 修复了一个真实后端 500 根因（递归栈溢出）。
- 修复了一个真实路由冲突导致的 404（`config`）。
- 收敛了交易页接口缺失引发的前端错误泛洪。
- 门禁与综合回归全部通过，当前系统可稳定运行并具备可交接状态。
