# API Documentation Trunk

> **导航说明**:
> 本文件是导航页或索引页，不是当前仓库共享规则或实现状态的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及具体执行入口，再按职责分别参考根目录 `AGENTS.md` 与根目录 `CLAUDE.md`。

## Current Truth Precedence

1. `architecture/STANDARDS.md`
2. FastAPI routes + Pydantic schema + exported OpenAPI
3. `docs/api/README.md`
4. retained supporting documents under `docs/api/`

以下内容不得覆盖真实契约：

- 历史报告
- 旧计划
- 历史兼容索引
- 已退役的 legacy 文档

## Retained Canonical Surface

### Contract Truth

- `web/backend/app/api/`
- `web/backend/app/schemas/`
- [`openapi.json`](/opt/claude/mystocks_spec/docs/api/openapi.json)
- [`openapi.yaml`](/opt/claude/mystocks_spec/docs/api/openapi.yaml)

### Supporting API Navigation

- [`guides/development/`](/opt/claude/mystocks_spec/docs/api/guides/development/)
- [`guides/integration/INDEX.md`](/opt/claude/mystocks_spec/docs/api/guides/integration/INDEX.md)
- [`specifications/INDEX.md`](/opt/claude/mystocks_spec/docs/api/specifications/INDEX.md)
- [`testing/INDEX.md`](/opt/claude/mystocks_spec/docs/api/testing/INDEX.md)

### Retained Root Reference Documents

- [`API_CONTRACT_ARCHITECTURE_ANALYSIS.md`](/opt/claude/mystocks_spec/docs/api/API_CONTRACT_ARCHITECTURE_ANALYSIS.md)
- [`API_ENDPOINTS_STATISTICS_REPORT.md`](/opt/claude/mystocks_spec/docs/api/API_ENDPOINTS_STATISTICS_REPORT.md)
- [`ERROR_CODE_GUIDE.md`](/opt/claude/mystocks_spec/docs/api/ERROR_CODE_GUIDE.md)
- [`EXCEPTION_HANDLER_GUIDE.md`](/opt/claude/mystocks_spec/docs/api/EXCEPTION_HANDLER_GUIDE.md)
- [`VALIDATION_GUIDE.md`](/opt/claude/mystocks_spec/docs/api/VALIDATION_GUIDE.md)
- [`SWAGGER_UI_GUIDE.md`](/opt/claude/mystocks_spec/docs/api/SWAGGER_UI_GUIDE.md)

这些文件属于 retained supporting/reference surface，可帮助理解 API 系统，但不替代 code contract truth。

## Reader Routing

### If You Need Current API Truth

优先回到：

- FastAPI route definitions
- Pydantic schema definitions
- exported OpenAPI artifacts

### If You Need API Development Guidance

优先阅读：

- [`api_development_guidelines.md`](/opt/claude/mystocks_spec/docs/api/guides/development/api_development_guidelines.md)
- [`INDEX.md`](/opt/claude/mystocks_spec/docs/api/guides/integration/INDEX.md)
- [`api_acceptance_standards.md`](/opt/claude/mystocks_spec/docs/api/testing/compliance/api_acceptance_standards.md)
- [`api_specification.md`](/opt/claude/mystocks_spec/docs/api/specifications/core/api_specification.md)

### If You Need Historical Evidence

进入：

- `docs/api/reports/`
- `docs/reports/`

这些区域只应作为历史证据、里程碑记录或清理审计材料使用。

## Wave 1 Cleanup Status

- `docs/api/legacy-cn/` 已在 `2026-04-08` cleanup wave 中退役
- `docs/api/INDEX.md` 保留为 supporting transition index，不再维护为并行主入口
- 默认治理策略继续是 `delete/archive > rewrite`

## Related Governance Artifacts

- [documentation-system.md](/opt/claude/mystocks_spec/docs/overview/documentation-system.md)
- [2026-04-08-first-pass-inventory.md](/opt/claude/mystocks_spec/docs/reports/documentation-governance/2026-04-08-first-pass-inventory.md)
- [2026-04-08-decision-register.md](/opt/claude/mystocks_spec/docs/reports/documentation-governance/2026-04-08-decision-register.md)
