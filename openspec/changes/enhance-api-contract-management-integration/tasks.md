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
- [x] 2.4 Add contract drift detection and failure on breaking changes
- [x] 2.5 Create contract validation reports and notifications
- [x] 2.6 Integrate with existing code-quality.yml workflow

## 3. Contract Test Integration
> **仓库事实校对（2026-04-27）**:
> 本仓库已经形成“主测试结构 + 遗留 contract 目录并存”的局面。
> 已核对到的本地证据包括：
> - pytest marker / 契约测试支撑：`web/backend/app/api/contract/services/contract_testing.py`
> - 单元 / 集成契约测试入口：`tests/unit/contract/`、`tests/integration/contract/`
> - 遗留目录仍保留：`tests/contract/`
> 因此 3.2 不能勾选为完成；当前更接近“部分迁移已发生，但旧真相源未完全退场”。

- [x] 3.1 Refactor contract tests to use pytest markers
- [ ] 3.2 Move contract tests from tests/contract/ to main test structure
- [x] 3.3 Add contract test execution to CI pipeline
- [x] 3.4 Create contract test coverage reporting
- [x] 3.5 Implement contract test failure analysis and debugging tools

## 4. Intelligent Version Negotiation
> **仓库事实校对（2026-04-27）**:
> 当前版本协商链路已有明确实现基础：
> - 核心实现：`web/frontend/src/services/versionNegotiator.ts`
> - 兼容性检查 / 回退逻辑：`checkCompatibility()`、`negotiateVersion()`、`findFallbackVersion()`
> - 组件消费：`web/frontend/src/components/common/ApiVersionManager.vue`
> - 单元测试：`web/frontend/src/services/__tests__/versionNegotiator.spec.ts`
> 但以下目标仍未形成当前 repo-truth：
> - 未发现显式的 breaking-change migration path 计算与转换步骤执行
> - 未发现自动 client adaptation 层
> - 未发现独立的 integration tests；当前仅能证实 unit tests

- [x] 4.1 Extend versionNegotiator.ts with compatibility checking
- [ ] 4.2 Implement migration path calculation for breaking changes
- [ ] 4.3 Add automatic client adaptation for version differences
- [x] 4.4 Create version negotiation error handling and fallback strategies
- [ ] 4.5 Add version negotiation unit tests and integration tests

## 5. Contract Impact Analysis Tools
> **仓库事实校对（2026-04-27）**:
> 目前未在 `web/backend/app/api/contract/services/`、前端 API / 组件目录或相关测试中找到 `ContractImpactAnalyzer`、impact analysis API/UI、migration effort estimation 的当前实现证据。
> 历史分析文档中有方案草图，但不能当作当前代码事实。

- [ ] 5.1 Create ContractImpactAnalyzer service in backend
- [ ] 5.2 Implement frontend impact assessment for contract changes
- [ ] 5.3 Add migration effort estimation algorithms
- [ ] 5.4 Create impact analysis API endpoints
- [ ] 5.5 Add impact analysis UI components to frontend
- [ ] 5.6 Implement automated impact notifications

## 6. Monitoring and Metrics Enhancement
> **仓库事实校对（2026-04-27）**:
> 当前可以确认已有 API contract validation workflow，
> 但未找到专门面向 contract validation success rate / drift incidents / Grafana coverage dashboard / health-check contract status / alerting 的现行实现闭环。
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
> 但这些文件大多是历史分析、实施过程记录或 API 参考，不足以直接证明“当前 canonical developer guide / impact analysis usage guide / 培训闭环”已完成。

- [x] 7.1 Update API_CONTRACT_INTEGRATION_ASSESSMENT.md with implementation details
  - Repo-truth note: 该 assessment 文档已包含实现现状、CI/CD 集成、runtime validation、version negotiation 与 impact analysis 方案细节，但它仍是历史分析/评估材料，不应替代当前 canonical developer guide。
- [ ] 7.2 Create runtime contract validation developer guide
- [ ] 7.3 Add contract testing best practices documentation
- [ ] 7.4 Create contract impact analysis usage guide
- [ ] 7.5 Organize contract management training session

## 8. Validation and Testing
> **仓库事实校对（2026-04-27）**:
> 已能确认的局部验证包括：
> - 前端 runtime validator / version negotiator 的单元测试
> - `.github/workflows/api-contract-validation.yml` 的 CI 入口
> - 后端 contract service 的 import / OpenAPI generation / regression gate 校验步骤
> 但当前仓库中尚未形成可直接指向本 change 的
> end-to-end contract validation、CI 实跑结果、impact analysis accuracy、runtime validation performance、security review 的最新 closeout 证据。

- [ ] 8.1 Perform end-to-end contract validation testing
- [ ] 8.2 Test CI/CD integration with contract validation
- [ ] 8.3 Validate contract impact analysis accuracy
- [ ] 8.4 Perform performance testing for runtime validation
- [ ] 8.5 Conduct security review of contract validation implementation
