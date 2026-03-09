## ADDED Requirements

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