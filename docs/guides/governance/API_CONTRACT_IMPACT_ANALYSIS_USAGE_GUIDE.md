# API Contract Impact Analysis Usage Guide

> **使用说明**:
> 本文件说明当前仓库里“可实际使用”的 contract impact analysis 工作流，不等于 OpenSpec 目标态里的完整 analyzer 平台。
> 若涉及共享规则，请优先遵循 [`architecture/STANDARDS.md`](/opt/claude/mystocks_spec/architecture/STANDARDS.md)；若涉及契约事实，则以运行时 OpenAPI 与当前后端 contract 路由实现为准。

## Scope Of This Guide

当前仓库里，已经能直接使用的是“diff-based impact analysis”：

- 比较两个契约版本差异
- 识别 breaking / non-breaking changes
- 用 validate 接口对新 spec 做 breaking change 检查
- 用 sync report 盘点 code-to-db contract surface

当前仓库里，还**没有**可直接确认的：

- dedicated `ContractImpactAnalyzer` backend service
- frontend impact assessment UI
- migration effort estimation algorithm closeout
- automated impact notifications closeout

因此本 guide 只覆盖当前已实现的 diff-based workflow，不把 5.x 目标态误写成已落地。

## Current Entry Points

后端 contract routes：
- [`routes.py`](/opt/claude/mystocks_spec/web/backend/app/api/contract/routes.py)

核心服务：
- [`diff_engine.py`](/opt/claude/mystocks_spec/web/backend/app/api/contract/services/diff_engine.py)
- [`validator.py`](/opt/claude/mystocks_spec/web/backend/app/api/contract/services/validator.py)
- [`version_manager.py`](/opt/claude/mystocks_spec/web/backend/app/api/contract/services/version_manager.py)

## Available Operations

### 1. Compare two stored contract versions

路由：
- `POST /api/contracts/diff`

用途：
- 查看两个持久化 contract version 的差异
- 得到 `total_changes`、`breaking_changes`、`non_breaking_changes`
- 查看逐项 `diffs`

这是当前最接近“impact analysis” 的已实现能力。

### 2. Validate a candidate spec against an older version

路由：
- `POST /api/contracts/validate`

关键字段：
- `check_breaking_changes`
- `compare_to_version_id`

用途：
- 在提交或发布前，先用候选 spec 对比既有版本
- 提前识别 breaking changes，而不是只做语法校验

### 3. Inspect sync surface

路由：
- `GET /api/contracts/sync/report`

用途：
- 看当前 code-to-db contract sync 会覆盖哪些 contract / endpoint
- 辅助判断 impact scope，而不是直接给出 consumer migration 计划

## Recommended Workflow

推荐按这个顺序做：

1. 找到当前 active version
   - `GET /api/contracts/versions/{name}/active`
2. 比较相邻版本差异
   - `POST /api/contracts/diff`
3. 对候选 spec 做 validate
   - `POST /api/contracts/validate`
4. 看 sync report 是否出现意料外 endpoint
   - `GET /api/contracts/sync/report`
5. 最后再回到 consumer side 手工确认
   - frontend type generation
   - backend route tests
   - contract integration tests

## Example Usage

### Compare two versions

```json
POST /api/contracts/diff
{
  "from_version_id": 12,
  "to_version_id": 13
}
```

重点看：
- `breaking_changes`
- `diffs[*].path`
- `diffs[*].description`

### Validate a new spec against an old one

```json
POST /api/contracts/validate
{
  "spec": { "...": "candidate openapi spec" },
  "check_breaking_changes": true,
  "compare_to_version_id": 12
}
```

重点看：
- `valid`
- `error_count`
- `warning_count`
- `results[*].category`

## Reading The Output

当 `diff` 或 `validate` 返回 breaking change 时，当前推荐的人工判断口径是：

1. 先看 path / method 是否被删除或改签
2. 再看 required 字段、响应结构、状态码示例是否被收紧
3. 最后回到 consumer surface：
   - frontend generated types
   - backend integration tests
   - any downstream docs / playbooks

当前仓库没有自动 consumer blast-radius 计算，所以这一步仍需人工 review。

## What This Guide Does Not Claim

- 不声称当前仓库已经有完整的 `ContractImpactAnalyzer`
- 不声称已有 migration effort 估算或 impact notification 自动化
- 不声称当前 diff 结果已经自动映射到 frontend UI / store / composable 级影响范围

如果后续 5.x 真正实现，再把本 guide 升级为“full impact analysis guide”；在那之前，它只代表当前可用的 diff-based workflow。
