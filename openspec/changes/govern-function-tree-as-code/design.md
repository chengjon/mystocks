## Context

> **设计方案说明**:
> 本文件用于记录某项变更的设计思路、结构拆分、实现取舍或技术路径，属于方案设计层材料。
> 它不是共享规则正文，也不直接代表当前仓库已落地状态；落地判断应结合 `architecture/STANDARDS.md`、对应 proposal/tasks、审批结果与实际代码验证。


当前治理体系已经有 `task card + scope + drift + OpenSpec` 门禁，但“功能归属”仍停留在 `docs/FUNCTION_TREE.md` 的自由文本层。
首个将功能树机器化的 PR 又天然会改动治理基础设施，因此必须在规则里保留自举路径，避免强迫治理改动伪装成业务域改动。

## Goals / Non-Goals

- Goals:
  - 将功能树升级为“文档总线 + 机器索引 + scope gate 校验”
  - 让 task card 成为唯一机器事实源
  - 保留 `meta-governance` 自举规则
  - 只对被镜像的业务域强制 `FUNCTION_TREE` 文档同步
- Non-Goals:
  - 本次不做 GitNexus / 代码图谱双向校验
  - 本次不把 PR 文本本身作为门禁真值
  - 本次不自动生成 `docs/FUNCTION_TREE.md`

## Decisions

- Decision: 保留 `docs/FUNCTION_TREE.md` 作为人读总线，同时新增 `governance/function-tree/catalog.yaml` 与 `schema.json` 作为机器索引。
  - Alternatives considered: 直接解析 Markdown 表格；被拒绝，因为自由文本和表格结构不稳定。

- Decision: 将 `function_tree` 结构块加入 task card schema/template。
  - Alternatives considered: 继续复用 PR 模板自由文本；被拒绝，因为无法作为机器门禁事实源。

- Decision: 在 `mainline_scope_gate.py` 内直接扩展 function-tree 校验。
  - Alternatives considered: 新建并行脚本；被拒绝，因为会引入第二套门禁入口。

- Decision: 引入 `meta-governance` 保留域，并设为 `mirror_to_function_tree: false`。
  - Alternatives considered: 要求治理改动硬映射业务域；被拒绝，因为会让规则自相矛盾。

## Risks / Trade-offs

- catalog 需要人工维护，但获得了稳定 ID 与可审查 diff。
- mirrored domain 的同步校验会提高治理严格度，但只约束被镜像业务域，避免首版过度收紧。
- scope gate 需要兼顾 `coverage_paths` 与 `entrypoints`，否则容易把文档和治理伴生改动误判为越界。

## Migration Plan

1. 创建标准 OpenSpec change。
2. 新增 catalog/schema，并建立业务域与 `meta-governance` 的最小真值。
3. 扩展 task card schema/template 与 reviewer-facing PR mirror。
4. 扩展 `mainline_scope_gate.py`，接入 function-tree 校验与自举规则。
5. 为 mirrored business domains 在 `docs/FUNCTION_TREE.md` 中补齐稳定 ID，并补充配套文档说明。
6. 用 focused governance tests 和 `openspec validate --strict` 验证整条治理链。

## Open Questions

- Phase 1 对 `fix` / `cleanup` 的入口命中策略要收紧到什么程度？
- 未来与 GitNexus 对接时，是否需要把 `coverage_paths` 拆成更细粒度的代码图谱节点？
