# Web Dev Transition Wave 2

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/web-dev/` 兼容壳的第二轮收口执行，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档 trunk、治理口径或执行入口，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

## Why

- wave 1 之后，`docs/web-dev/` 已不再是活动导航入口
- 但主干 hook 指南、taxonomy 与仓库测试仍把 `docs/web-dev/` 当成受支持路径
- 在这些依赖仍存在时，不能安全删除兼容壳

## Changes

- 将 `.claude/hooks/post-tool-use-web-dev-file-tracker.sh` 的路径过滤移除 `docs/web-dev/*`
- 将 `docs/guides/hooks/WEB_DEV_HOOKS_GUIDE.md` 与 `docs/guides/hooks/web-dev-hooks-guide.md` 的主干说明切换到 `docs/guides/hooks/`
- 从 `config/governance/documentation-taxonomy.yaml` 移除 `docs/web-dev/*.md` 兼容分类，并同步 `tests/unit/scripts/test_audit_documentation_system.py`
- 更新 `tests/unit/scripts/test_repository_hygiene_paths.py`，不再要求 `docs/web-dev/` 存在
- 从 `docs/INDEX.md` 移除 `docs/web-dev/GUIDE.md` 兼容入口
- 删除 `docs/web-dev/` 目录

## Gate Check

- canonical replacement:
  - `docs/guides/hooks/WEB_DEV_HOOKS_GUIDE.md`
  - `docs/guides/hooks/web-dev-hooks-guide.md`
- runtime/config dependency:
  - tracked hook filter 已切换完成
- test dependency:
  - taxonomy audit 与 repository hygiene 断言已切换完成
- active navigation:
  - 已清理完成

## Expected Effect

- `docs/web-dev/` 不再以兼容壳形式残留在活动树
- Web Hook / 工作流说明完全并入 `docs/guides/hooks/`
- taxonomy 不再容忍 `docs/web-dev/` 重新出现；若后续被重建，将直接表现为治理回归
