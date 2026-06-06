# Code Quality Specification

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

## Purpose

定义 MyStocks 项目的代码质量治理基线与执行门禁，覆盖代码结构、文档可维护性、审查修复流程、构建失败语义、技术债冻结与测试有效性要求，确保仓库在持续迭代中保持可验证、可审计、可收敛的工程质量标准。
## Requirements
### Requirement: Python Class Structure Integrity
所有 Python 类定义 MUST 保持正确的缩进结构，确保类方法正确定义在类作用域内。

#### Scenario: Class method indentation
- **WHEN** 定义 Python 类时
- **THEN** 所有类方法 SHALL 缩进到类定义内部
- **AND** MUST 使用一致的缩进层级（4个空格）

#### Scenario: Class structure validation
- **WHEN** 进行代码审查或质量检查
- **THEN** 开发者 MUST 使用 AST 解析验证类结构
- **AND** MUST 确认 `__init__` 和其他核心方法在类内部

### Requirement: Documentation Link Validity
项目文档（特别是 README.md）中的所有本地链接 MUST 指向存在的文件。

#### Scenario: Link verification
- **WHEN** 创建或更新文档链接
- **THEN** 链接目标文件 MUST 存在
- **AND** 链接路径 SHALL 相对于项目根目录正确

#### Scenario: Link validation tools
- **WHEN** 维护文档
- **THEN** 开发者 SHALL 提供自动化工具验证链接有效性
- **AND** 工具 MUST 返回正确的退出码（0=成功，1=失败）

### Requirement: GPU Documentation Path Accuracy
所有 GPU 相关文档引用 MUST 使用正确的路径 `src/gpu/api_system/`。

#### Scenario: GPU path references
- **WHEN** 引用 GPU 系统文档
- **THEN** 开发者 MUST 使用路径 `src/gpu/api_system/`
- **AND** MUST NOT 使用过时的 `gpu_api_system/` 路径

### Requirement: Code Review Response Protocol
当收到代码审查报告时，开发团队 MUST 按照严格流程进行修复和验证。

#### Scenario: Critical issue resolution
- **WHEN** Codex 审查发现 Critical 问题
- **THEN** 开发者 MUST 立即修复并验证
- **AND** MUST 使用可执行的验证脚本确认修复有效

#### Scenario: Validation scripts
- **WHEN** 创建验证脚本
- **THEN** 脚本 MUST 使用 `set -e` 确保失败时退出
- **AND** MUST NOT 使用 `|| echo` 吞掉错误
- **AND** MUST 返回正确的退出码

### Requirement: Build and Type-Check Gate Consistency
仓库的主构建链路 MUST 对类型检查失败保持一致的失败语义，禁止通过吞错方式放行类型错误。

#### Scenario: Frontend build and type-check alignment
- **WHEN** 前端主链路执行构建与检查
- **THEN** `vue-tsc --noEmit` MUST 以非零退出码阻断失败
- **AND** MUST NOT 使用 `|| true`、`|| echo` 或等价方式吞掉类型检查错误

#### Scenario: Required checks for merge
- **WHEN** 提交合并请求（PR/MR）
- **THEN** build、type-check、test SHALL 作为必需检查项
- **AND** 任一检查失败 MUST 阻断合并

### Requirement: Technical Debt Baseline Freeze
项目 MUST 维护技术债基线并执行“新增不增量”策略。

#### Scenario: Baseline snapshot and comparison
- **WHEN** 执行 CI 质量门
- **THEN** 系统 MUST 比较当前指标与已冻结基线（type errors、suppressions、skip/xfail）
- **AND** 当前分支新增债务 SHALL NOT 高于基线

#### Scenario: Baseline update policy
- **WHEN** 需要更新基线
- **THEN** 基线更新 MUST 通过治理评审并记录原因
- **AND** 常规迭代中基线 SHOULD 仅下降不应上升

### Requirement: Suppression and TODO Exception Lifecycle
所有抑制注释与技术债占位标记 MUST 可审计、可到期、可清理。

#### Scenario: New suppression metadata
- **WHEN** 新增 `@ts-ignore`、`@ts-expect-error`、`as any`、`# type: ignore` 或同类抑制
- **THEN** MUST 绑定 `owner`、`issue`、`ttl`、`reason`、`remediation_plan`
- **AND** 未满足元数据要求 MUST 被 CI 阻断

#### Scenario: TODO/FIXME/HACK metadata
- **WHEN** 新增 TODO/FIXME/HACK 占位标记
- **THEN** MUST 包含 `owner`、`issue`、`ttl`
- **AND** 裸标记（无元数据）MUST 视为违规

#### Scenario: TTL expiration enforcement
- **WHEN** 抑制项、例外项或 skip/xfail 到达 TTL
- **THEN** CI MUST 将其标记为失败
- **AND** 仅允许通过正式例外审批续期

### Requirement: Test Effectiveness Guardrail
测试体系 MUST 优先保证有效性，避免“通过但未验证核心逻辑”。

#### Scenario: Placeholder assertion prevention
- **WHEN** 新增或修改测试用例
- **THEN** MUST NOT 使用 `assert True` 作为最终断言
- **AND** 关键路径测试 MUST 包含可验证业务行为的断言

#### Scenario: Skip/XFail governance
- **WHEN** 新增 `skip`/`xfail`
- **THEN** MUST 绑定 `issue`、`owner`、`ttl` 与恢复条件
- **AND** 无期限或无追踪信息的 skip/xfail MUST 被阻断

### Requirement: Debt Remediation Wave Planning
技术债修复 MUST 采用分阶段波次执行，并对每个阶段定义验收标准。

#### Scenario: Stage A stop-bleeding acceptance
- **WHEN** 完成 Stage A（质量信号对齐）
- **THEN** no-new-debt 门禁 MUST 生效
- **AND** build/type-check/test 语义 MUST 对齐

#### Scenario: Stage B risk-reduction acceptance
- **WHEN** 完成 Stage B（高风险存量清偿）
- **THEN** 前端关键路径 suppressions、后端 placeholder、测试占位断言 MUST 出现可量化下降
- **AND** 需提供阶段性治理报告

#### Scenario: Stage C institutionalization acceptance
- **WHEN** 完成 Stage C（机制硬化）
- **THEN** TTL 自动失效、周报/KPI、基线复盘机制 MUST 进入常态运行
- **AND** 例外审批流程 MUST 可审计

### Requirement: ArtDeco Batch Verification Evidence
ArtDeco P0/P1 optimization work SHALL produce batch-level verification evidence instead of generic pass/fail summaries.

#### Scenario: Batch verification execution
- **WHEN** an optimization batch completes implementation
- **THEN** it SHALL run `npm --prefix web/frontend run type-check`
- **AND** it SHALL run the batch's targeted Playwright suites
- **AND** any route or layout touching batch SHALL also run `scripts/run_e2e_pm2.sh`

#### Scenario: Batch verification reporting
- **WHEN** verification results are reported for an optimization batch
- **THEN** the report SHALL include the executed command, browser project, suite names, and pass/fail/skip counts
- **AND** it SHALL identify whether each failure is newly introduced or pre-existing debt

### Requirement: ArtDeco Token Compliance
ArtDeco page optimization SHALL preserve token-based styling as the only allowed source for visual primitives.

#### Scenario: Page style cleanup
- **WHEN** an ArtDeco page or shared ArtDeco component is modified during optimization
- **THEN** colors, spacing, and semantic rise/fall styles SHALL reference `web/frontend/src/styles/artdeco-tokens.scss`
- **AND** newly introduced hardcoded visual values SHALL be treated as quality regressions

### Requirement: API File-Level Test Governance
The project SHALL maintain file-level API test suites as the canonical grouped verification surface for API route modules, and SHALL use documented closeout evidence to distinguish completed mainline salvage from unrelated dirty-worktree hygiene.

#### Scenario: Route module is covered by file-level tests
- **WHEN** an API route module is promoted into the canonical test baseline
- **THEN** the repository SHALL provide a corresponding file-level suite under `tests/api/file_tests/`
- **AND** that suite SHALL verify the route module through grouped endpoint assertions or contract-aligned checks

#### Scenario: Mainline salvage is closed without reopening on root-dirty noise
- **WHEN** the planned file-test salvage batches have already merged on mainline
- **THEN** the project SHALL record a closeout artifact for the salvage line
- **AND** formatting-equivalent or user-owned dirty-worktree drift SHALL be treated as separate hygiene work instead of reopening the closed salvage change

### Requirement: Frontend Data Access Discipline Gates
The project SHALL define phased discipline checks for frontend data-access regressions during and after migration.

#### Scenario: Coexistence period is active
- **WHEN** frontend data migration is still in coexistence phase
- **THEN** discipline checks MAY run in non-blocking or report-only mode
- **AND** they SHALL identify direct forbidden patterns without preventing approved coexistence work

#### Scenario: Cleanup-stage enforcement begins
- **WHEN** migration closure criteria are met for the targeted frontend data paths
- **THEN** discipline checks SHALL block newly introduced forbidden patterns
- **AND** the checks SHALL at minimum cover silent catch suppression, unregistered direct data-access regressions, or equivalent approved rules

### Requirement: Frontend Migration Closeout Evidence
The project SHALL require closeout evidence before removing legacy frontend data-access paths or promoting discipline checks to blocking status.

#### Scenario: Legacy path is retired
- **WHEN** a legacy frontend data-access path is proposed for retirement
- **THEN** closeout evidence SHALL identify the verified replacement path and its verification artifacts
- **AND** it SHALL distinguish active canonical paths from compatibility-retained or cleanup-ready paths

### Requirement: Closure Wave Evidence Contract
The project SHALL require explicit evidence artifacts before a Q2 closure wave is marked complete.

#### Scenario: Closure wave claims completion
- **WHEN** a cross-cutting architecture, safety, or governance wave is marked complete
- **THEN** the completion record SHALL identify the verified truth source, affected scope, executed validations, and unresolved follow-up items
- **AND** it SHALL distinguish delivered closure from deferred backlog items

#### Scenario: Closure evidence is reviewed
- **WHEN** reviewers inspect a closure wave
- **THEN** they SHALL be able to identify what was verified in code, what was verified in docs, and what remains assumption or follow-up
- **AND** the evidence SHALL be sufficient to reject narrative-only completion claims

### Requirement: Static Analysis Formal Remeasure Governance

The project SHALL execute `backend_static_code_analysis` baseline refreshes through a formal remeasure batch that preserves canonical field semantics and emits reviewable evidence before any baseline mutation.

#### Scenario: Formal remeasure batch is executed
- **WHEN** the project reruns `backend_static_code_analysis` for governance purposes
- **THEN** it SHALL use the approved snapshot builder or an explicitly reviewed replacement
- **AND** it SHALL emit a raw snapshot artifact and a delta summary against the canonical baseline

#### Scenario: Raw snapshot artifact is baseline-shaped
- **WHEN** a formal remeasure batch emits a raw static-analysis snapshot
- **THEN** that artifact SHALL expose the same field set as the canonical `backend_static_code_analysis` block
- **AND** any additional helper metadata SHALL be clearly separated from the canonical field payload

#### Scenario: Field semantics are preserved during remeasure
- **WHEN** a formal remeasure batch is proposed or executed
- **THEN** it SHALL document how each baseline field is produced
- **AND** it SHALL NOT silently redefine existing field semantics as part of the measurement run

### Requirement: Static Analysis Evidence Freshness

Observed static-analysis evidence SHALL be treated as expiring measurement evidence rather than as durable truth.

#### Scenario: Observed snapshot becomes stale by time
- **WHEN** an observed static-analysis snapshot is older than `7` calendar days unless explicitly overridden by governance decision
- **THEN** it SHALL be treated as stale evidence
- **AND** it SHALL NOT be used as the promote basis without rerunning the formal remeasure batch

#### Scenario: Observed snapshot becomes stale by drift
- **WHEN** repository drift affects the analyzed backend API paths, the snapshot builder, or the governing measurement configuration
- **THEN** previously observed static-analysis evidence SHALL be treated as stale
- **AND** the project SHALL require a fresh remeasure before baseline adoption is reviewed

### Requirement: Static Analysis Two-Step Approval Boundary

The project SHALL separate approval to execute a static-analysis remeasure from approval to adopt its results into the canonical baseline.

#### Scenario: Remeasure is approved without promote
- **WHEN** reviewers approve execution of a static-analysis remeasure batch
- **THEN** that approval SHALL authorize evidence collection and result reporting only
- **AND** it SHALL NOT authorize mutation of the canonical baseline or canonical exception records

#### Scenario: Promote is approved after review
- **WHEN** a static-analysis remeasure result is proposed for baseline adoption
- **THEN** the promote approval SHALL explicitly reference the reviewed snapshot and result summary
- **AND** it SHALL state whether the remeasure was a scheduled refresh or a drift-triggered refresh
- **AND** it SHALL be recorded as a separate decision from the remeasure execution approval
