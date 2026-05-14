# 2026-05-14 ML Workbench Release Evidence

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Scope

This note records the release evidence for the repo-local `7.1 模型训练 / 预测推理` workbench closeout.

## Canonical Facts

- `FUNCTION_TREE` marks `7.1 机器学习策略 -> 模型训练` as `✅`.
- `FUNCTION_TREE` marks `7.1 机器学习策略 -> 预测推理` as `✅`.
- The canonical frontend entry is `/ai/ml`.
- The canonical backend route family is `/api/v1/strategies/ml/*`.
- The legacy `/api/ml/models/*` family remains compatibility-only.

## Evidence Chain

- `openspec/specs/ml-training-prediction/spec.md`
- `openspec/specs/frontend-routing/spec.md`
- `openspec/specs/function-tree-governance/spec.md`
- `web/backend/tests/test_v1_ml_workbench_contract.py`
- `web/frontend/tests/e2e/ai-ml-workbench.spec.ts`
- `tests/unit/governance/test_function_tree_doc_sync.py`
- `tests/unit/governance/test_function_tree_catalog.py`

## Verification Results

- `pytest --no-cov web/backend/tests/test_v1_ml_workbench_contract.py -q`
  - `24 passed`
- `pytest --no-cov tests/unit/governance/test_function_tree_doc_sync.py tests/unit/governance/test_function_tree_catalog.py -q`
  - `19 passed`
- `openspec validate --specs --strict`
  - `47 passed, 0 failed`

## Operational Notes

- This note is a release evidence record only.
- It does not change `FUNCTION_TREE`.
- It does not re-open implementation work for `7.1`.
- Remaining follow-up work should focus on publish/change-log consistency and domain-level governance review, not feature reimplementation.
