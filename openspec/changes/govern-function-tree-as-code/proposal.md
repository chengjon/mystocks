# Change: Govern Function Tree As Code

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


## Why

`docs/FUNCTION_TREE.md` 目前已经承担业务能力总线职责，但它仍是人读文档，不是机器可校验事实。与此同时，`mainline_scope_gate.py` 只校验 task card、OpenSpec、scope 和 drift，尚未消费功能树映射，也没有解决治理基础设施自身如何通过同一套门禁自举的问题。

这使得功能树可以导航和沟通，却还不能稳定地约束、拦截和审计功能归属、入口变化与跨域声明。

## What Changes

1. 新增 machine-readable function-tree catalog 与 schema：
   - 在 `governance/function-tree/` 中维护稳定的 `domain_id`、`node_id`、`coverage_paths` 与分类入口。
   - 引入保留域 `meta-governance`，承接治理基础设施的自举改动。

2. 扩展 mainline task card：
   - 新增 `function_tree` 结构块，声明 `domain_id`、`node_id`、`affected_entrypoints`、`update_status`、`secondary_domains`、`exemption_reason`。
   - 明确 task card 是唯一机器事实源，PR 模板仅做 reviewer 镜像。

3. 扩展 `mainline_scope_gate.py`：
   - 校验 catalog + task card + git diff 的一致性。
   - 对 mirrored business domains 强制同步义务。
   - 允许 `meta-governance` 自举而不强制业务 `FUNCTION_TREE` 同步。

4. 对齐人读治理文档：
   - 为 `docs/FUNCTION_TREE.md` 中被镜像的业务域补齐稳定 ID。
   - 更新 `FEATURE_MANAGEMENT_WORKFLOW`、`AI_QUICK_START` 与 PR 模板的说明。

5. 补齐 focused governance tests，覆盖 catalog、schema、scope gate 与 doc sync。

## Impact

- **Affected specs**: `function-tree-governance`（新增）
- **Affected code**:
  - `governance/function-tree/**`
  - `governance/mainline/schemas/ai-task-card.schema.json`
  - `governance/mainline/templates/ai-task-card.yaml`
  - `governance/mainline/scripts/mainline_scope_gate.py`
  - `governance/mainline/spec/ai-development-mainline-governance-spec.md`
  - `docs/FUNCTION_TREE.md`
  - `docs/guides/governance/FEATURE_MANAGEMENT_WORKFLOW.md`
  - `docs/guides/ai-tools/AI_QUICK_START.md`
  - `.github/pull_request_template.md`
  - `tests/unit/governance/**`
  - `tests/fixtures/governance/**`

- **Breaking changes**: 无现有业务 API breaking change，但会收紧治理门禁输入要求。
- **Primary risks**:
  - catalog 与 `FUNCTION_TREE` 文档同步口径漂移；
  - scope gate 若误判 coverage/entrypoint，会放大治理噪音；
  - task card 新字段若约束过强，可能阻塞治理基础设施自身迭代。
