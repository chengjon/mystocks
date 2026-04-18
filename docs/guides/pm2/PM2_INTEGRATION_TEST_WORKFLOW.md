# PM2 Integration Test Workflow

> **导航说明**:
> 本文件是当前仓库本地 PM2 集成测试执行说明，服务于前后端整合后的日常验证。
> 若涉及仓库级共享规则、审批门禁或环境一致性，请先回到 [`architecture/STANDARDS.md`](/opt/claude/mystocks_spec/architecture/STANDARDS.md)；若涉及历史 PM2 专题说明，再结合本 family 其他 supporting guides。

## Scope

本工作流只固化两条当前确认的测试链：

1. `gate`
   - 提交前快速门禁
   - 用于前端静态检查 + 独立 PM2 E2E 门禁
2. `regression`
   - 长链集成回归
   - 用于 PM2 持续运行实例上的业务冒烟与后端 pytest

核心原则：

- `scripts/run_e2e_pm2.sh` 只作为独立门禁使用
- 手动 `pm2 start ecosystem.test.config.js` 的长链，不嵌套调用 `scripts/run_e2e_pm2.sh`
- 测试前统一清理脏 PM2 进程，避免 WIP worktree 端口污染
- 复用当前开发 PM2 环境前，先 `pm2 save`；测试结束后执行 `pm2 resurrect`

## Canonical Commands

### Gate

```bash
bash scripts/run_pm2_integration_workflow.sh gate
```

该模式会执行：

- `pm2 stop all && pm2 delete all`
- `cd web/frontend && npm run type-check`
- `cd web/frontend && npm run test`
- `bash scripts/run_e2e_pm2.sh`

### Regression

```bash
bash scripts/run_pm2_integration_workflow.sh regression
```

该模式会执行：

- `pm2 stop all && pm2 delete all`
- `pm2 start ecosystem.test.config.js`
- 健康检查：
  - `http://localhost:8020/health`
  - `http://localhost:8020/api/health/ready`
  - `http://localhost:3020/`
- `cd web/frontend && PLAYWRIGHT_EXTERNAL_FRONTEND=1 npm run test:e2e:business-smoke`
- `pytest --no-cov -q web/backend/tests/test_api_integration.py web/backend/tests/test_auth.py`
- 输出 PM2 状态与最近日志

### All

```bash
bash scripts/run_pm2_integration_workflow.sh all
```

顺序执行 `gate` 后再执行 `regression`。

## Why The Flow Is Split

拆成两条链是为了避免 PM2 生命周期冲突。

[`scripts/run_e2e_pm2.sh`](/opt/claude/mystocks_spec/scripts/run_e2e_pm2.sh) 自带：

- `pm2 delete all`
- `pm2 start ecosystem.test.config.js`
- 健康轮询
- 测试完成后再次 `pm2 delete all`

因此它不能夹在已经手动启动 PM2 的长链中间，否则会直接重置服务上下文，导致后续 `business-smoke` 与 `pytest` 失效。

## Operator Checklist

执行共享 PM2 集成测试前后，按这份顺序检查：

1. `pm2 save`
2. 只运行 `gate` 或 `regression`，不要在共享会话里直接跑 `all`
3. 确认 `8020` / `3020` 端口空闲，或明确接受脚本接管当前测试基座
4. 运行脚本后确认 `pm2 list` 出现：
   - `mystocks-backend`
   - `mystocks-frontend`
5. 确认健康检查通过：
   - `curl --silent --fail --max-time 10 http://localhost:8020/health`
   - `curl --silent --fail --max-time 10 http://localhost:3020/`
6. 测试完成后执行 `pm2 resurrect`
7. 再次执行 `pm2 list`，确认环境回到测试前保存态

## Latest Verified Baseline

最近一次人工实测时间：`2026-04-19 01:29:55 +0800`

执行链：

- `pm2 save`
- `bash scripts/run_pm2_integration_workflow.sh regression`
- `pm2 resurrect`
- `cd web/frontend && npm run type-check`

实测结果：

- PM2 服务在线：
  - `mystocks-backend` -> `http://localhost:8020`
  - `mystocks-frontend` -> `http://localhost:3020`
- 健康检查通过：
  - `http://localhost:8020/health`
  - `http://localhost:8020/api/health/ready`
  - `http://localhost:3020/`
- 前端类型检查：`vue-tsc --noEmit` 通过
- Playwright：
  - 命令：`PLAYWRIGHT_EXTERNAL_FRONTEND=1 npm run test:e2e:business-smoke`
  - 浏览器项目：`chromium`
  - 结果：`41 passed / 0 failed / 0 skipped`
- 后端 pytest：
  - 命令：`pytest --no-cov -q web/backend/tests/test_api_integration.py web/backend/tests/test_auth.py`
  - 结果：`46 passed / 0 failed / 18 skipped`

注意：

- 前端类型生成阶段仍会打印历史冲突自动修复与 warning，这是当前仓库既有现象，不等于本轮回归失败。
- 后端在技术分析真实数据抓取失败时可能出现 warning；当前已降级为 warning，不阻塞 PM2 回归。

## Reporting Baseline

每次执行后，结果汇报至少包含：

- PM2 进程状态：`mystocks-backend`、`mystocks-frontend`
- 服务地址：`http://localhost:8020`、`http://localhost:3020`
- 执行模式：`gate` / `regression` / `all`
- 实际执行命令
- 前端类型检查结果
- Vitest 结果
- Playwright 浏览器项目与通过/失败/跳过数量
- 后端 pytest 结果

## Related Files

- [`scripts/run_pm2_integration_workflow.sh`](/opt/claude/mystocks_spec/scripts/run_pm2_integration_workflow.sh)
- [`scripts/run_e2e_pm2.sh`](/opt/claude/mystocks_spec/scripts/run_e2e_pm2.sh)
- [`ecosystem.test.config.js`](/opt/claude/mystocks_spec/ecosystem.test.config.js)
- [`web/frontend/package.json`](/opt/claude/mystocks_spec/web/frontend/package.json)
