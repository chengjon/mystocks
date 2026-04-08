# Guides Supporting Wave 3

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/` 根 subtree `keep-supporting` 决策的收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

## Why

- `docs/guides/README.md` 与 `docs/guides/INDEX.md` 已在前序波次被收成 transition / secondary index
- 各 guide family 也已按 concern 逐步收口
- decision register 里 `docs/guides/` 根 subtree 仍停留在 `open`

## Current Role

- `docs/guides/` 当前是 supporting surface
- 它负责把读者按 concern 分流到：
  - `ai-tools/`
  - `frontend/`
  - `web/`
  - `typescript/`
  - `pm2/`
  - `openspec-cmd/`
  - `multi-cli-tasks/`
  - `onboarding/`
  - `governance/`
  - `documentation/`
- 它不再承担 docs 根 trunk 角色

## Why Keep Supporting Instead Of Deleting

- 该 subtree 仍有高 inbound usage，尤其来自：
  - AI / agent 指南
  - `docs/testing/`
  - 历史 plans / reports / task artifacts
- 因此当前正确动作不是 subtree-wide delete，而是保持 family-routed supporting surface

## Outcome

- `docs/guides/` 根 subtree 的 register 状态与当前事实对齐
- docs 根 trunk 仍然是 `docs/README.md`
- guides 根入口继续存在，但只承担 concern-routing/supporting 角色

## Validation

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_guides_readme_navigation_links_use_current_canonical_paths \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_guides_root_remains_supporting_surface_not_docs_trunk \
  -q -o addopts=''

python scripts/compliance/markdown_governance_gate.py --root-dir . \
  docs/reports/documentation-governance/2026-04-08-guides-supporting-wave3.md \
  docs/reports/documentation-governance/2026-04-08-decision-register.md

python scripts/governance/audit_documentation_system.py --root-dir . --format text
```
