## MODIFIED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: Response Wrapper Implementation

The backend API SHALL ensure all FastAPI route handlers that are added or
modified in backend API modules declare an OpenAPI response model using
`UnifiedResponse[...]` or
`UnifiedPaginatedResponse[...]` unless the route is explicitly classified as a
legacy raw/control-plane exception with documented justification.

The declared response model MUST match the successful response envelope exposed
to callers. If the migration requires changing a response payload shape, the
same change MUST include endpoint-level regression coverage and an OpenAPI diff
record.

#### Scenario: Modified route file enters the commit gate

- **GIVEN** a backend API route file is staged for commit
- **WHEN** the route contains HTTP decorators such as `@router.get`,
  `@router.post`, `@router.put`, or `@router.delete`
- **THEN** each changed route declaration MUST use
  `response_model=UnifiedResponse[...]` or
  `response_model=UnifiedPaginatedResponse[...]`
- **AND** `UnifiedResponse Contract Guard` MUST report `errors=0` for the staged
  route file set.

#### Scenario: Runtime unblock touches a route file with historical contract debt

- **GIVEN** a runtime import fix requires editing a route file
- **AND** that file contains historical route response-model debt
- **WHEN** the runtime fix is prepared for commit
- **THEN** the route response-model debt MUST be resolved in a separate
  route-contract lane or the runtime fix MUST remain uncommitted
- **AND** the runtime lane MUST NOT bypass the guard with `--no-verify`.
