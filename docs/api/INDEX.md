# API Secondary Index

> **导航说明**:
> 本文件是导航页或索引页，不是当前仓库共享规则或实现状态的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及具体执行入口，再按职责分别参考根目录 `AGENTS.md` 与根目录 `CLAUDE.md`。

## Use This Index For

- 快速跳转到保留的 supporting 子树
- 查找 API guides / testing / specifications 的局部入口
- 从旧链接平滑过渡到 `docs/api/README.md`

## Preferred Entrypoints

- [README.md](README.md)
- [guides/development/](guides/development)
- [guides/integration/INDEX.md](guides/integration/INDEX.md)
- [specifications/INDEX.md](specifications/INDEX.md)
- [testing/INDEX.md](testing/INDEX.md)
- [reports/milestones/README.md](reports/milestones/README.md)

## Retired Paths

以下路径已从 active API index 中移除，不再作为推荐入口：

- `docs/api/legacy-cn/`
- `docs/api/legacy-cn/03-API与功能文档/`

## Governance

- Canonical trunk: [`README.md`](README.md)
- Contract truth: FastAPI routes + Pydantic schema + OpenAPI exports
- Default cleanup bias: `delete/archive > rewrite`
