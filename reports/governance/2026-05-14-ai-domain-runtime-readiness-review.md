# 07-高级分析与AI 域运行态成熟度验收报告

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

日期：2026-05-14
分支：`wip/root-dirty-20260403`
范围：线 B，只读核验 `7.1 机器学习策略`、`7.2 批量分析`、`7.3 情感分析`；不修改 `FUNCTION_TREE`。

## 结论

建议当前保持：

| 领域 | 当前状态 | 本次建议 |
|------|----------|----------|
| `07-高级分析与AI` | `🧪 实验性 / 50%` | 保持 `🧪 / 50%` |

理由：7.x 功能行已经具备较完整的实现证据和部分 live runtime 证据，但域级 evidence 尚未闭合。主要缺口不是“没有代码”，而是运行态稳定性、前端到后端 canonical 路径一致性、模型/数据/生产窗口依赖、以及域级治理口径仍存在不一致。

可在后续单独治理线中考虑升级到 `🚧 / 60%-65%`，但前提至少包括：

- 修复 `/ai/sentiment` 前端 API 双 `/api` 前缀导致的 404。
- 稳定 `/ai/ml` Playwright smoke，避免直达路由出现 skeleton/导航超时不确定性。
- 将 `07` 域级 API 前缀、catalog 覆盖路径与 canonical v1 路由对齐。
- 明确外部依赖项：训练数据、模型 artifact、生产训练/评估窗口、真实舆情源、批量任务生产调度边界。

## 当前 FUNCTION_TREE 状态

`docs/FUNCTION_TREE.md` 快速导航仍记录：

| 领域 | 状态 | 完成度 |
|------|------|--------|
| `07-高级分析与AI` | `🧪 实验性` | `50%` |

同一文件中的功能行已显示多项 `✅`：

| 子线 | 功能点 | 状态摘要 |
|------|--------|----------|
| `7.1 机器学习策略` | 特征工程、模型训练、预测推理 | 均为 `✅`；canonical 入口包括 `/api/v1/strategies/ml/train`、`/api/v1/strategies/ml/predict`、`/ai/ml` |
| `7.2 批量分析` | 批量回测、批量选股、批量监控 | 均为 `✅`；canonical 入口为 `/ai/batch` 与 `/api/v1/strategies/batch-analysis/*` |
| `7.3 情感分析` | 新闻情感、舆情监控 | 均为 `✅`；canonical 工作台为 `/ai/sentiment` |

域级仍为 `🧪 / 50%` 是合理的：`FUNCTION_TREE` 自身说明 `✅` 代表功能点有实现/验证/必要运行证据，但不自动等同于域级生产 readiness。域级需要同时看 implementation、verification、runtime、safety/governance 四类证据。

## 仓库路由与契约核验

### 前端路由

`web/frontend/src/router/index.ts` 中 AI 路由存在：

| 路由 | 组件 | meta API |
|------|------|----------|
| `/ai/sentiment` | `@/views/ai/Sentiment.vue` | `/api/v1/sentiment/market` |
| `/ai/ml` | `@/views/ai/MlWorkbench.vue` | `/api/v1/strategies/ml/runtime-status` |
| `/ai/batch` | `@/views/ai/BatchAnalysis.vue` | `/api/v1/strategies/batch-analysis/runtime-status` |

未认证访问三条路由均被前端守卫重定向到 `/login?redirect=...`，符合 `requiresAuth: true`。

### 后端 canonical v1 路由

后端聚合路径为：

| 子线 | 后端路由文件 | 实际 canonical 路径 |
|------|--------------|---------------------|
| `7.1` | `web/backend/app/api/v1/strategy/ml_workbench.py` 经 `/api/v1` + `/strategies` 挂载 | `/api/v1/strategies/ml/runtime-status`、`/models`、`/train`、`/predict`、`/models/{model_id}` |
| `7.2` | `web/backend/app/api/v1/strategy/batch_analysis.py` 经 `/api/v1` + `/strategies` 挂载 | `/api/v1/strategies/batch-analysis/runtime-status`、`/submit`、`/tasks`、`/tasks/{task_id}` |
| `7.3` | `web/backend/app/api/v1/analysis/sentiment.py` 经 `/api/v1` 直接挂载 | `/api/v1/sentiment/analyze`、`/stock/{symbol}`、`/market` |

注意：本次任务列出的 `/api/v1/analysis/sentiment/*` 在当前运行态返回 `404`。仓库实际 canonical 路径是 `/api/v1/sentiment/*`。这需要在后续审核中统一口径：要么更正文档/分配文本，要么提供兼容路由。

## 服务状态

PM2 与端口检查：

| 服务 | PM2 状态 | 端口 | 地址 |
|------|----------|------|------|
| `mystocks-backend` | `online` | `8020` | `http://localhost:8020` |
| `mystocks-frontend` | `online` | `3020` | `http://localhost:3020` |

## 后端 Live Probe

执行时间：2026-05-14 03:35-03:49 UTC
目标：`http://localhost:8020`

### 7.1 机器学习策略

| Probe | 结果 | 关键数据 |
|-------|------|----------|
| `GET /api/v1/strategies/ml/runtime-status` | `200 OK` | `service_available=true`，`model_backend=runtime_registry`，`lightgbm/sklearn/joblib` 均 available，`model_dir_writable=true` |
| `GET /api/v1/strategies/ml/models` | `200 OK` | `models=[]`，`total=0` |

判断：

- 运行时服务、依赖和模型目录可用。
- 当前没有已注册/已训练模型 artifact，无法证明“域级可持续训练/推理运行窗口”已闭合。
- 预测语义为 analytical output，不代表交易指令，这一点符合安全边界。

### 7.2 批量分析

| Probe | 结果 | 关键数据 |
|-------|------|----------|
| `GET /api/v1/strategies/batch-analysis/runtime-status` | `200 OK` | `service_available=true`，`runtime_backend=runtime_batch_registry`，`max_symbols=20`，支持 `batch_backtest/batch_screening/batch_monitoring` |
| `GET /api/v1/strategies/batch-analysis/tasks` | `200 OK` | 能列出 runtime registry 内任务 |
| `POST /api/v1/strategies/batch-analysis/submit` without CSRF | `403` | `CSRF_TOKEN_MISSING`，符合安全中间件要求 |
| `GET /api/csrf-token` + 带 `X-CSRF-Token` 重试 submit | `200 OK` | 生成 `batch_a12ab62b4ca9`，`status=completed`，`completed_symbols=2`，`failed_symbols=0`，`candidate_count=1` |
| `GET /api/v1/strategies/batch-analysis/tasks/{task_id}` | `200 OK` | 可读回提交任务详情 |

判断：

- 运行态可用，且能通过正式 CSRF 流程完成一次 batch screening。
- 后端明确标记 `warnings=["first_batch_runtime_registry_only"]` 和提交结果 `warnings=["first_batch_not_production_scheduler"]`。
- 这支持功能行 `✅`，但不支持域级升级为“生产化”：当前只是 runtime registry 证据，不是生产 scheduler mutation、实时进度流、自动处置闭环。

### 7.3 情感分析

| Probe | 结果 | 关键数据 |
|-------|------|----------|
| `GET /api/v1/analysis/sentiment/market` | `404` | 任务分配文本路径不存在 |
| `GET /api/v1/sentiment/market` | `200 OK` | `sentiment=positive`，`average_sentiment=0.435`，`coverage=6`，`positive_ratio=0.6667` |
| `GET /api/v1/sentiment/stock/0700.HK?days=7` | `200 OK` | `mentions=3`，`average_sentiment=0.84`，`trend=positive` |
| `POST /api/v1/sentiment/analyze` without CSRF | `403` | `CSRF_TOKEN_MISSING` |
| `GET /api/csrf-token` + fresh `X-CSRF-Token` 重试 analyze | `200 OK` | `sentiment=positive`，`confidence=0.65`，返回关键词短语 |

判断：

- 后端 canonical `/api/v1/sentiment/*` 运行态可用。
- `/api/v1/analysis/sentiment/*` 与当前 repo truth 不一致。
- 情感分析目前基于规则词典与内存 seeded history，能支持工作台 smoke 和功能级验收，但不能证明真实舆情源、生产数据窗口、持续更新链路已闭合。

## 前端 Smoke

浏览器：`/usr/bin/google-chrome-stable`，Playwright headless。
认证：登录页 demo 账户 `admin / admin123`，登录后得到 `auth_token` 和 `auth_user`。

### 未认证访问

| 路由 | 结果 |
|------|------|
| `/ai/ml` | `200` 后重定向到 `/login?redirect=/ai/ml` |
| `/ai/batch` | `200` 后重定向到 `/login?redirect=/ai/batch` |
| `/ai/sentiment` | `200` 后重定向到 `/login?redirect=/ai/sentiment` |

符合 `requiresAuth: true`。

### 认证后访问

| 路由 | Smoke 结果 | 关键观察 |
|------|------------|----------|
| `/ai/ml` | 不稳定 | 一次序列 smoke 可渲染出“模型训练 / 预测”“训练配置”“模型列表”“预测推理”“结果摘要”，正文包含 `runtime_registry`、`SVM: available`、`LightGBM: available`；但直达复测多次出现 skeleton/正文为空或导航 timeout。需要作为域级 runtime 稳定性缺口处理。 |
| `/ai/batch` | 通过 | 渲染“批量分析”“任务配置”“任务列表”“结果摘要”“标的结果”，请求 `/api/v1/strategies/batch-analysis/runtime-status`、`/tasks`、`/tasks/{task_id}` 返回 `200`。 |
| `/ai/sentiment` | 部分通过 | 页面渲染“情感分析工作台”“市场情绪概览”“个股情绪趋势”“文本情感分析”；但浏览器实际请求出现 `404 /api/api/v1/sentiment/market`，页面正文出现“同步异常”。 |

通用前端噪声：

- `Pinia not ready, skip session restore this round`
- `Security init timed out (non-blocking)`
- `Global error: SyntaxError: Need to install with app.use function`，来源为 `vue-i18n`
- `ArtDecoIcon` 若干 icon fallback warning

这些并非全部由 AI 域引入，但它们会降低域级 smoke 的可信度。尤其是 `/ai/sentiment` 的 `404 /api/api/v1/sentiment/market` 是 AI 域路径实错，不应忽略。

## 发现的问题

### 1. Sentiment 前端 API 双前缀

`web/frontend/src/api/aiSentiment.ts` 通过 `@/utils/request.ts` 发请求，而 `request.ts` 的 dev 默认 `API_BASE_URL` 为 `/api`。但 `aiSentiment.ts` 传入的是完整 `/api/v1/sentiment/...`：

- `POST /api/v1/sentiment/analyze`
- `GET /api/v1/sentiment/stock/{symbol}`
- `GET /api/v1/sentiment/market`

运行态变成 `/api/api/v1/sentiment/market`，返回 `404`。这解释了 `/ai/sentiment` 页面虽能渲染框架，但出现“同步异常”。

建议后续修复为与 `mlWorkbench.ts`、`batchAnalysis.ts` 一致的 client 风格，例如传 `/v1/sentiment/...` 或改用同一 `apiClient`。

### 2. 任务分配文本与实际 sentiment API 路径不一致

实际后端路径是 `/api/v1/sentiment/*`，不是 `/api/v1/analysis/sentiment/*`。如果治理口径要求 analysis namespace，应单独建兼容路由或发起小型治理调整；否则应更新验收口径和报告模板。

### 3. 7.1 ML 运行时具备依赖，但无已注册模型

`runtime-status` 显示：

- `service_available=true`
- `model_backend=runtime_registry`
- `lightgbm/sklearn/joblib` 可用
- `model_dir_writable=true`

但 `models.total=0`。因此 7.1 可以认定 repo-local first-batch 功能完成，却不能作为域级成熟度升级依据。升级前应补充：

- 至少一个可加载模型 artifact 或受控训练产物。
- 训练数据来源、训练窗口、评估指标与失效/回滚策略。
- 模型输出与交易执行之间的明确隔离。

### 4. 7.2 是 runtime registry，不是生产调度闭环

批量分析 submit 能通过，但返回 warnings：

- `first_batch_runtime_registry_only`
- `first_batch_not_production_scheduler`

这说明功能行 `✅` 是合理的，但域级仍应保留实验属性，直到 production scheduler mutation、实时进度、任务持久化、审计和异常恢复边界明确。

### 5. 域级治理口径仍有漂移

`docs/FUNCTION_TREE.md` 的 07 域级 API 前缀仍写：

- `/api/v1/advanced-analysis/*`
- `/api/v1/algorithms/*`
- `/api/ml/*`
- `/api/gpu/*`

但 7.1/7.2/7.3 的 canonical v1 运行态实际包括：

- `/api/v1/strategies/ml/*`
- `/api/v1/strategies/batch-analysis/*`
- `/api/v1/sentiment/*`

`governance/function-tree/catalog.yaml` 中 7.2/7.3 节点也仍偏旧路径，例如 `advanced_analysis.py`、`algorithms.py`、`quant-matrix/**`，未完全反映 `/ai/batch`、`/ai/sentiment` 与 canonical v1 路由。这是治理证据未闭合，而不是功能缺失。

## 外部依赖项拆分建议

如果后续要把 07 域从 `🧪` 推进到 `🚧`，建议明确拆出以下外部依赖，不把它们混入“继续开发 7.1”：

| 依赖项 | 影响 |
|--------|------|
| 可复现训练数据集 | 证明模型训练不是仅接口可调 |
| 至少一个受控模型 artifact | 支撑 `/models`、`/models/{id}`、`/predict` 的持续 smoke |
| 生产训练/评估窗口 | 明确何时训练、如何评估、何时失效 |
| 真实新闻/公告/舆情源 | 把规则/seeded history 与真实数据链路分层 |
| 批量任务持久化与调度策略 | 区分 runtime registry demo 与 production scheduler |
| 运行态 E2E 套件 | 用稳定浏览器验收替代人工 smoke |

## 推荐后续工作

本报告不建议直接修改 `FUNCTION_TREE`。建议拆成三个小步骤：

1. `fix-ai-sentiment-client-paths`：修复 `/api/api/v1/sentiment/*`，补一个前端 API 单测或 smoke 断言。
2. `stabilize-ai-ml-route-smoke`：让 `/ai/ml` 直达路由在已认证浏览器中稳定出现业务正文，并记录 API 请求结果。
3. `align-ai-domain-governance-status`：若前两项闭合，再单独提出 `FUNCTION_TREE`/catalog/状态调整审核材料，考虑从 `🧪 / 50%` 升级到 `🚧 / 60%-65%`。

## 最终判断

本次只读验收支持以下判断：

- 7.1、7.2、7.3 的“功能行 ✅”总体有依据，因为已有 canonical 页面、后端 API、CSRF 下的 live probe，以及安全语义。
- 07 域级继续保持 `🧪 / 50%` 也有依据，因为域级 runtime 和 governance 尚未闭合。
- 不建议开“继续开发 7.1”大线；更合适的是修复路径一致性、稳定 smoke、明确外部依赖，再单独走很小的状态调整审批线。
