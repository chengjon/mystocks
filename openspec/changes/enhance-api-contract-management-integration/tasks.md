## 1. Frontend Runtime Contract Validation

> **使用说明**:
> 本文件用于记录当前 OpenSpec 变更的执行清单、操作步骤或协作约束，帮助跟踪实施过程。
> 其中勾选状态、执行顺序和局部说明仅代表任务推进视角，不应脱离 proposal、design、正式 specs、`architecture/STANDARDS.md` 与实际验证结果单独解读为最终事实。

- [x] 1.1 Install Zod validation library for frontend
- [x] 1.2 Create RuntimeContractValidator class in unifiedApiClient.ts
- [x] 1.3 Implement OpenAPI to Zod schema converter
- [x] 1.4 Add contract validation interceptor to API client
- [x] 1.5 Create contract drift error handling and reporting
- [x] 1.6 Add unit tests for runtime validation
- [x] 1.7 Update error boundaries to handle contract validation errors

## 2. CI/CD Contract Validation Workflow
- [x] 2.1 Create .github/workflows/api-contract-validation.yml
- [x] 2.2 Add contract validation job triggered on backend API changes
- [x] 2.3 Implement automated TypeScript type generation in CI
  - `2026-05-14` repo-truth note: frontend type generation is canonicalized on `scripts/generate_frontend_types.py`; legacy `scripts/dev/generate-types/generate_ts_types.py` is now only a compatibility wrapper and rejects old external-tool flags (`--tool`, `--contracts-dir`, `--output-dir`).
- [x] 2.4 Add contract drift detection and failure on breaking changes
- [x] 2.5 Create contract validation reports and notifications
- [x] 2.6 Integrate with existing code-quality.yml workflow

## 3. Contract Test Integration
> **仓库事实校对（2026-05-14）**:
> 本仓库已经完成“主测试结构 + canonical support package + 遗留 compatibility wrapper”的 contract test 收敛。
> 已核对到的本地证据包括：
> - pytest marker / 契约测试支撑：`web/backend/app/api/contract/services/contract_testing.py`
> - 单元 / 集成契约测试入口：`tests/unit/contract/`、`tests/integration/contract/`
> - canonical support implementation：`tests/contract_support/`
> - legacy compatibility wrapper：`tests/contract/`
> - repo-truth guard：`tests/unit/contract/test_legacy_contract_tree_inventory.py`
> - alias correctness guard：`tests/unit/contract/test_contract_support_aliases.py`
> 因此 3.2 可按“真实 pytest case 已离开 legacy tree，support 主实现已迁入 canonical package，legacy tree 仅保留 thin wrapper”口径关闭。
> `2026-05-07` 补充：
> - 唯一仍位于 `tests/contract/` 的真实 pytest case `test_api_contract_schemathesis.py` 已迁入 `tests/integration/contract/`
> - `tests/contract/` 当前剩余内容以 support / compatibility module 为主，仍需后续继续拆出 misnamed framework modules，3.2 继续保持未完成（已由 `2026-05-14` 批次关闭）
> - 进一步 blast-radius 核对显示 `tests/contract/models.py` 的上游 fan-out 为 `HIGH`（direct=20），其直接依赖已扩散到 `tests/test_runner.py`、`tests/ai/*`、多个 `scripts/dev/analysis/*` 与部分 `src/algorithms/*`；因此 support-module 收敛不能再作为无审批的小型 rename / move 继续推进，需单独设计 canonical support package 与 compatibility shim 退场顺序
> - 该顺序与边界现已记录在 `openspec/changes/enhance-api-contract-management-integration/design.md`
> - `2026-05-07` 已完成第一批低风险 support-module canonicalization：`tests/contract_support/engine.py` 成为 `ContractTestEngine` 的 canonical home，`tests/contract/contract_engine.py` 已降级为 thin compatibility wrapper，并新增 `tests/unit/contract/test_contract_support_aliases.py` 保护 legacy import surface
> - `2026-05-14` 已完成 validator / executor / reporting / models / generator / reverse generator / split validator support migration；`tests/contract/` 现在只保留 thin compatibility wrapper / re-export，`tests/contract_support/` 成为唯一 support implementation home
> - 验证：`ruff check tests/contract tests/contract_support tests/unit/contract/test_contract_support_aliases.py tests/unit/contract/test_legacy_contract_tree_inventory.py`、`pytest --no-cov tests/integration/contract tests/unit/contract -q`、`openspec validate enhance-api-contract-management-integration --strict`

- [x] 3.1 Refactor contract tests to use pytest markers
- [x] 3.2 Move contract tests from tests/contract/ to main test structure
- [x] 3.3 Add contract test execution to CI pipeline
- [x] 3.4 Create contract test coverage reporting
- [x] 3.5 Implement contract test failure analysis and debugging tools

## 4. Intelligent Version Negotiation
> **仓库事实校对（2026-04-27）**:
> 当前版本协商链路已有明确实现基础：
> - 核心实现：`web/frontend/src/services/versionNegotiator.ts`
> - 兼容性检查 / 回退逻辑：`checkCompatibility()`、`negotiateVersion()`、`findFallbackVersion()`
> - breaking-change migration path：`calculateApiMigrationPath()` / `calculateMigrationPath()`
> - request adaptation primitive：`adaptApiRequestForVersion()` / `adaptRequestForVersion()`
> - HTTP client adaptation hook：`apiClient.ts` request interceptor 在显式目标版本 header 存在时调用 `adaptApiClientRequestForVersion()`
> - 组件消费：`web/frontend/src/components/common/ApiVersionManager.vue`
> - 单元测试：`web/frontend/src/services/__tests__/versionNegotiator.spec.ts`
> - backend contract integration tests：`tests/integration/contract/test_contract_*.py`
> 但以下目标仍未形成当前 repo-truth：
> - `web/frontend/src/api/unifiedApiClient.ts` 当前仍只是指向 `apiClient.ts` 的 legacy wrapper；实际自动适配入口已落在 canonical `apiClient.ts`
> - `tests/integration/contract/test_contract_*.py` 主要覆盖 backend contract service / generator / validator；`web/frontend/src/services/__tests__/versionNegotiator.spec.ts` 覆盖 frontend version negotiation unit path；`web/frontend/src/api/__tests__/versionNegotiation.integration.test.ts` 覆盖 public `apiClient.get()` integration path
> - 因此当前已能同时证实 unit tests 与 frontend integration path
> `2026-05-14` 补充：`calculateApiMigrationPath()` 已支持 incompatible major-version path 计算，`adaptApiRequestForVersion()` 已能生成版本 header 与同域 endpoint prefix 适配结果；随后已抽出 `versionNegotiationPolicy.ts`，并由 `apiClient.ts` request interceptor 接入显式目标版本请求的 endpoint/header 自动适配。该批次关闭 4.3，并补齐 4.5 所需的 integration evidence。

- [x] 4.1 Extend versionNegotiator.ts with compatibility checking
- [x] 4.2 Implement migration path calculation for breaking changes
- [x] 4.3 Add automatic client adaptation for version differences
- [x] 4.4 Create version negotiation error handling and fallback strategies
- [x] 4.5 Add version negotiation unit tests and integration tests

## 5. Contract Impact Analysis Tools
> **仓库事实校对（2026-04-27）**:
> 目前未在 `web/backend/app/api/contract/services/`、前端 API / 组件目录或相关测试中找到 `ContractImpactAnalyzer`、impact analysis API/UI、migration effort estimation 的当前实现证据。
> 历史分析文档中有方案草图，但不能当作当前代码事实。
> `2026-05-15` 补充：后端已新增 `web/backend/app/api/contract/services/impact_analyzer.py`，提供纯 service 级 `ContractImpactAnalyzer.analyze_specs()` / `analyze_diff()`，当前覆盖 endpoint/schema/client 影响识别、风险汇总与迁移工作量估算；并已通过 `POST /api/contracts/impact` 暴露只读影响分析 API。尚未接入前端 UI 或通知。

- [x] 5.1 Create ContractImpactAnalyzer service in backend
- [ ] 5.2 Implement frontend impact assessment for contract changes
- [x] 5.3 Add migration effort estimation algorithms
- [x] 5.4 Create impact analysis API endpoints
- [ ] 5.5 Add impact analysis UI components to frontend
- [ ] 5.6 Implement automated impact notifications

## 6. Monitoring and Metrics Enhancement
> **仓库事实校对（2026-04-27）**:
> 当前可以确认已有 API contract validation workflow，
> 但未找到专门面向 contract validation success rate / drift incidents / Grafana coverage dashboard / health-check contract status / alerting 的现行实现闭环。
> 需要特别区分以下“相邻但不足以勾选”的证据：
> - `.github/workflows/deploy.yml`、`e2e-testing.yml`、`ci-cd-with-type-checking.yml` 中的 health checks 属于通用部署/运行健康检查，不是 contract health monitoring
> - `docs/reports/api_split/api_health.json`、`api_refresh-health.json` 等是 API 文档拆分产物，不是 contract validation 监控面板或 incident tracking
> - repo 中存在 `/metrics` 与 Prometheus 基础设施，但未见 contract-specific metrics/alert names 的现行接线
> 因此本节暂不勾选，避免把工作流存在误写成监控体系完成。

- [ ] 6.1 Add contract validation success rate metrics to Prometheus
- [ ] 6.2 Implement contract drift incident tracking
- [ ] 6.3 Create contract validation coverage dashboards in Grafana
- [ ] 6.4 Add contract health monitoring to existing health checks
- [ ] 6.5 Implement contract validation failure alerting

## 7. Documentation and Training
> **仓库事实校对（2026-04-27）**:
> 当前存在与该专题相关的历史/说明文档，例如：
> - `docs/reports/API_CONTRACT_INTEGRATION_ASSESSMENT.md`
> - `docs/reports/API_CONTRACT_INTEGRATION_OPENSPEC_IMPLEMENTATION.md`
> - `docs/api/CONTRACT_TESTING_API.md`
> - `docs/api/CONTRACT_MANAGEMENT_API.md`
> - `docs/standards/OPENAPI_CONTRACT_GOVERNANCE.md`
> - `docs/reports/README_API_CONTRACT.md`
> 但这些文件大多是历史分析、实施过程记录或 API 参考，不足以直接证明“当前 canonical developer guide / impact analysis usage guide / 培训闭环”已完成。
> 进一步核对后可明确区分：
> - `docs/api/CONTRACT_TESTING_API.md` 明确声明其类签名与示例主要保留早期框架历史快照，不再作为当前实现真值
> - `docs/api/CONTRACT_MANAGEMENT_API.md` 主要是 API 端点使用文档，且声明端点/示例如未复核应视为参考或历史材料
> - `docs/standards/OPENAPI_CONTRACT_GOVERNANCE.md` 是仓库级 OpenAPI 治理细则，不等于本 change 所要求的 runtime validation developer guide / impact analysis usage guide
> - `docs/reports/README_API_CONTRACT.md` 是 2025-12-29 的 Phase 6 报告索引，不是当前培训闭环或现行操作手册
> `2026-05-07` 补充：
> 当前已补齐一组 current-state canonical guides：
> - `docs/guides/governance/API_CONTRACT_RUNTIME_VALIDATION_DEVELOPER_GUIDE.md`
> - `docs/guides/governance/API_CONTRACT_TESTING_BEST_PRACTICES.md`
> - `docs/guides/governance/API_CONTRACT_IMPACT_ANALYSIS_USAGE_GUIDE.md`
> 它们明确区分了当前已实现链路与未实现目标态，因此 7.2-7.4 现可按 repo-truth 关闭；7.5 仍属于外部培训动作，继续保持未完成。

- [x] 7.1 Update API_CONTRACT_INTEGRATION_ASSESSMENT.md with implementation details
  - Repo-truth note: 该 assessment 文档已包含实现现状、CI/CD 集成、runtime validation、version negotiation 与 impact analysis 方案细节，但它仍是历史分析/评估材料，不应替代当前 canonical developer guide。
- [x] 7.2 Create runtime contract validation developer guide
  - Repo-truth result: current-state developer guide now lives at `docs/guides/governance/API_CONTRACT_RUNTIME_VALIDATION_DEVELOPER_GUIDE.md`, and explicitly documents the current backend validator + CI gate chain plus the frontend `unifiedApiClient.ts` legacy-wrapper boundary.
- [x] 7.3 Add contract testing best practices documentation
  - Repo-truth result: canonical testing guidance now lives at `docs/guides/governance/API_CONTRACT_TESTING_BEST_PRACTICES.md`, including current directory truth (`tests/integration/contract`, `tests/unit/contract`, retained `tests/contract`) and recommended validation commands.
- [x] 7.4 Create contract impact analysis usage guide
  - Repo-truth result: current diff-based usage guide now lives at `docs/guides/governance/API_CONTRACT_IMPACT_ANALYSIS_USAGE_GUIDE.md`; it documents the implemented `/api/contracts/diff`, `/api/contracts/validate`, and `/api/contracts/sync/report` workflow without overstating the still-missing `ContractImpactAnalyzer` target state.
- [ ] 7.5 Organize contract management training session

## 8. Validation and Testing
> **仓库事实校对（2026-04-27）**:
> 已能确认的局部验证包括：
> - 前端 runtime validator / version negotiator 的单元测试
> - `.github/workflows/api-contract-validation.yml` 的 CI 入口
> - 后端 contract service 的 import / OpenAPI generation / regression gate 校验步骤
> - `tests/integration/contract/test_contract_executor.py`、`test_contract_generator.py`、`test_contract_validator.py` 这类 backend 集成测试
> 但仍需避免把“存在 CI 工作流和 backend contract tests”误写成更高层闭环：
> - workflow 中生成 `contract_validation_report.md` 只是 CI 报告模板与 artifact 逻辑，当前仓库并未保存一次可直接复核的最新实跑结果
> - backend contract integration tests 不等于“前端 runtime validator + backend contract + CI gate”的端到端链路验证
> - 当前未找到 runtime contract validator 的独立性能测试报告或基准脚本归档，不能支撑 8.4
> - `docs/standards/security/SECURITY_BEST_PRACTICES.md` 属于通用安全规范，不等于本专题实现已完成针对 contract validation 的专项 security review / sign-off
> 但当前仓库中尚未形成可直接指向本 change 的
> end-to-end contract validation、CI 实跑结果、impact analysis accuracy、runtime validation performance、security review 的最新 closeout 证据。

- [ ] 8.1 Perform end-to-end contract validation testing
- [ ] 8.2 Test CI/CD integration with contract validation
- [ ] 8.3 Validate contract impact analysis accuracy
- [ ] 8.4 Perform performance testing for runtime validation
- [ ] 8.5 Conduct security review of contract validation implementation
