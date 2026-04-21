# Frontend PR Gate Quick Reference

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## Scope

Use this sheet when a change touches any of these:

- `web/frontend/**`
- `.github/workflows/frontend-testing.yml`
- `.github/workflows/e2e-testing.yml`
- `.github/workflows/visual-testing.yml`

Primary references:

- [Frontend test and CI gate overview](/opt/claude/mystocks_spec/docs/testing/e2e/README.md)
- [PM2 integration workflow](/opt/claude/mystocks_spec/docs/guides/pm2/PM2_INTEGRATION_TEST_WORKFLOW.md)
- [PR template](/opt/claude/mystocks_spec/.github/pull_request_template.md)

## Runtime Gate Entry Points

优先使用仓库级脚本入口，不要在收口阶段手工拼装散装命令。

1. 正式 PM2 运行门禁：

```bash
bash scripts/run_frontend_runtime_baseline.sh
```

适用场景：
- Layout、路由、共享壳层、导航骨架、主业务链
- 需要一次性确认结构性语法、类型基线、PM2 健康、实际 E2E/axe/pytest、匿名 API、监控鉴权性能

输出目录：
- `reports/analysis/frontend-runtime-gate/<timestamp>/`
- `reports/analysis/api-performance-gate/<timestamp>/`
- `reports/analysis/api-monitoring-auth-gate/<timestamp>/`
- `reports/analysis/runtime-quality-summary/<timestamp>/`

2. 容器运行 smoke：

```bash
bash scripts/run_containerized_runtime_smoke.sh
```

适用场景：
- `Dockerfile`、`docker-compose.yml`、Nginx、镜像依赖装配
- 容器健康、readiness、首页可达性、`/api/metrics/health`、Prometheus 指标快照

输出目录：
- `reports/analysis/docker-runtime-smoke/<timestamp>/`

3. 统一交付摘要：

```bash
bash scripts/run_runtime_quality_summary.sh
```

适用场景：
- 汇总最近一次 PM2 baseline
- 在 `DOCKER_RUNTIME_DIR` 已提供时，把 Docker observability 一并附加到同一份摘要

输出目录：
- `reports/analysis/runtime-quality-summary/<timestamp>/`

4. 本地复现 CI downstream 交付摘要：

```bash
bash scripts/run_runtime_delivery_summary_local.sh
```

适用场景：
- 本地重建 CI `runtime-delivery-summary` / `runtime-delivery-bundle`
- 复现 `PM2-only`、`Docker-only`、`PM2 + Docker` 三种聚合路径

输出目录：
- `reports/analysis/runtime-quality-summary-ci-local/`
- `reports/analysis/runtime-ci-bundle-combined-local/`

## Fine-Grained Commands

Run from `web/frontend` unless noted otherwise.

```bash
npm run test:unit:stable
npm run test:e2e:selectors

PLAYWRIGHT_EXTERNAL_FRONTEND=1 \
FRONTEND_BASE_URL=http://127.0.0.1:3020 \
E2E_FRONTEND_URL=http://127.0.0.1:3020 \
BACKEND_BASE_URL=http://127.0.0.1:8020 \
E2E_BACKEND_URL=http://127.0.0.1:8020 \
npm run test:e2e:business-smoke

PLAYWRIGHT_EXTERNAL_FRONTEND=1 \
FRONTEND_BASE_URL=http://127.0.0.1:3020 \
E2E_FRONTEND_URL=http://127.0.0.1:3020 \
npm run test:e2e:axe

npm run test:e2e:lighthouse
npm run test:visual:dashboard
npm run test:visual:charts
npm run test:type-ceiling
```

## What Reviewers Should See

- `runtime_gate_entrypoint`: which top-level script was used
- `runtime_summary_artifact`: summary path or local CI summary path
- `runtime_bundle_artifact`: bundle index path when local CI rebuild is used
- `unit_gate`: file count and total passed tests from `test:unit:stable`
- `selector_gate`: pass/fail and any violating file
- `business_smoke_gate`: browser/project plus passed/failed/skipped
- `a11y_gate`: browser/project plus passed/failed/skipped
- `lighthouse_gate`: audited URLs, `finalDisplayedUrl`, category scores
- `visual_gate_dashboard`: browser/project plus passed/failed
- `visual_gate_charts`: browser/project plus passed/failed
- `cross_browser_evidence`: `firefox` / `webkit` smoke results or workflow run reference
- `type_ceiling_evidence`: current errors, configured ceiling, baseline file

## PM2 Status

Always report service availability explicitly:

- `mystocks-backend`: `http://localhost:8020`
- `mystocks-frontend`: `http://localhost:3020`
- Docker smoke must remain on备用端口，不得把容器结果冒充为 PM2 正式门禁：`http://localhost:8021` / `http://localhost:3021`

If the verification reuses a shared PM2 session, follow the save and restore sequence in [PM2 integration workflow](/opt/claude/mystocks_spec/docs/guides/pm2/PM2_INTEGRATION_TEST_WORKFLOW.md) instead of manually mixing `run_e2e_pm2.sh` with a long-running PM2 chain.

## Reviewer Heuristics

- If `selector_gate` fails, do not waive it casually. New E2E code must prefer `getByRole`, `getByText`, `getByTestId`.
- If `lighthouse_gate` reports protected pages landing on `/login`, that route’s performance evidence is invalid.
- If only `test:e2e:stable` ran, do not label it as “full E2E”.
- If visual baselines changed, verify whether the change belongs to `dashboard`, `charts`, or both groups.

## PR Template Fields

When the PR is frontend-relevant, fill all of these in `.github/pull_request_template.md`:

- `frontend_gate_scope`
- `pm2_status`
- `unit_gate`
- `selector_gate`
- `business_smoke_gate`
- `a11y_gate`
- `lighthouse_gate`
- `visual_gate_dashboard`
- `visual_gate_charts`
- `cross_browser_evidence`
- `type_ceiling_evidence`
