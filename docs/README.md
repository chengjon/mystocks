# Documentation Trunks

> **导航说明**:
> 本文件是仓库文档系统的主干入口，用于把人和 AI 导向当前有效的文档真相源。
> 它不是运行时代码、API 契约或 OpenSpec 能力本身；但在文档导航层面，它是当前 `docs/` 的 canonical entrypoint。

## Purpose

在进入具体文档子树前，先回答四个问题：

1. 当前 concern 的 canonical trunk 是什么
2. 哪些文档只是 supporting material
3. 哪些目录是 historical evidence
4. 哪些历史文档应走 `archive/delete`，而不是继续逐份重写

详细规则见 [documentation-system.md](overview/documentation-system.md)。

## Canonical Trunks

| Concern | Canonical trunk | Use this for |
|---|---|---|
| 仓库级工程规则 | [`architecture/STANDARDS.md`](../architecture/STANDARDS.md) | 审批门禁、迁移收口、删除标准、共享规则 |
| 当前能力真相 | [`openspec/specs/`](../openspec/specs) | 已建成/已治理能力的正式要求 |
| 已批准待实施变更 | [`openspec/changes/`](../openspec/changes) | 变更 proposal、design、tasks、spec deltas |
| API 契约真相 | `FastAPI routes + Pydantic Schema + /openapi.json` | 接口字段、参数、响应语义 |
| 运维 / runbooks | [`docs/operations/README.md`](operations/README.md) | 部署、监控、故障处理、运行流程 |
| 测试 / 验证指南 | [`docs/testing/README.md`](testing/README.md) | 测试策略、E2E、质量门禁、测试运行 |
| API 文档导航 | [`docs/api/README.md`](api/README.md) | API 文档入口与导航，但不覆盖真实契约 |
| 历史证据 | [`docs/reports/README.md`](reports/README.md) | 历史报告、验证记录、审计证据 |

## Reader Routing

- 要看共享规则、审批门禁、迁移/删除判定：先看 [`architecture/STANDARDS.md`](../architecture/STANDARDS.md)
- 要看“当前系统要求是什么”：先看 [`openspec/specs/`](../openspec/specs)
- 要看“当前批准但未完成的变更”：先看 [`openspec/changes/`](../openspec/changes)
- 要看 API 真实契约：回到 FastAPI 路由、Pydantic schema 与导出的 OpenAPI
- 要看运行和值班资料：进入 [`docs/operations/README.md`](operations/README.md)
- 要看测试策略和执行方法：进入 [`docs/testing/README.md`](testing/README.md)
- 要看历史报告：进入 [`docs/reports/README.md`](reports/README.md)，不要把报告当 current truth

## Governance Principles

当前文档治理采用四条原则：

1. `trunk-first, not leaf-first`
2. `delete invalid/stale docs aggressively`
3. `keep only current, architecturally truthful docs`
4. `AI-friendly hierarchy`

## Lifecycle Reminder

只有 canonical trunks 允许表达当前真相。

其余文档默认属于以下角色之一：

- `supporting`
- `report`
- `plan`
- `generated_reference`
- `archive_candidate`
- `delete_candidate`

当历史文档已有 canonical replacement 且无保留义务时，默认策略是：

```text
delete/archive > rewrite
```

## Reader Paths

不同角色的推荐阅读路径。这些路径是对上方 Canonical Trunks 的导航辅助，不替代 trunk map 本身。

| 角色 | 推荐路径 |
|------|---------|
| 新加入的开发者 | 本文档 → [根 PRODUCT.md](../PRODUCT.md) → [guides/onboarding/](guides/onboarding/) → 按技术栈进入 guides/ 子目录 |
| 前端开发者 | [guides/frontend/](guides/frontend/) → [api/](api/) → [standards/](standards/) (设计系统) |
| 后端开发者 | [guides/data-source/](guides/data-source/) → [api/](api/) → [operations/](operations/) |
| 运维 | [operations/](operations/) → [testing/](testing/) |
| AI 助手 | 本文档 → [architecture/STANDARDS.md](../architecture/STANDARDS.md) → 按需进入各 trunk |

## Related Entrypoints

- [documentation-system.md](overview/documentation-system.md)
- [docs/overview/README.md](overview/README.md)
- [openspec/project.md](../openspec/project.md)
- [PRODUCT.md](../PRODUCT.md) — 产品真相 (canonical)
