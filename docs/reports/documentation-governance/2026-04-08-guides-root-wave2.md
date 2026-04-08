# Guides Root Wave 2

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/README.md` 与 `docs/guides/INDEX.md` 的收口登记，不代表当前仓库共享规则或唯一事实来源。
> 若需确认当前文档 trunk、治理口径或执行入口，请优先以 `architecture/STANDARDS.md`、`docs/README.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/README.md` 与 `docs/guides/INDEX.md` 的收口登记波次。

## Why

- `docs/guides/README.md` 与 `docs/guides/INDEX.md` 在更早波次里已经被改成 transition index
- 但 decision register 里这条仍保留为 `open`
- 当前需要补做的是 execution gate 收口，而不是再次重写这两个入口文件

## Current State

- `docs/README.md` 是 `docs/` 的 canonical trunk
- `docs/guides/README.md` 现在只做按 concern 分流的 transition index
- `docs/guides/INDEX.md` 现在只做 secondary index / compatibility entrypoint
- `docs/guides/` 不再承担并行 canonical trunk 的角色

## Validation

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_active_documentation_entry_guides_no_longer_point_to_removed_quickstart_and_start_here_files \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_guides_readme_navigation_links_use_current_canonical_paths \
  -q -o addopts=''

python scripts/compliance/markdown_governance_gate.py --root-dir . \
  docs/reports/documentation-governance/2026-04-08-guides-root-wave2.md \
  docs/reports/documentation-governance/2026-04-08-decision-register.md

python scripts/governance/audit_documentation_system.py --root-dir . --format text
```

## Result

- decision register 里的 `docs/guides/README.md` + `docs/guides/INDEX.md` 已从 `open` 收口为已执行
- 本波次不再改动根 guide 入口正文，只确认既有 transition-index 形态已满足当前治理要求
- 后续若某个 guide family 还存在平行真相风险，应继续按 family 逐波次治理，而不是重新把 `docs/guides/` 拉回总入口角色
