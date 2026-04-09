# UI/UX Pro Max Artifact Cleanup Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/ui-ux-pro-max/` 所做的 bounded 清理，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录一次基于用户澄清触发的 artifact cleanup，而不是新的 guide family 保留动作。

## Why

- 用户明确说明 `ui-ux-pro-max` 本质上是 skill 以及运行该 skill 后产生的一组文件
- 这组文件的原始意图是辅助现有 web 端做美化和优化，不承担仓库文档系统的长期导航、门禁或路由职责
- 因此它不应继续作为 `docs/INDEX.md` 的主导航项，也不应被 hygiene 测试固化为活跃 guide family

## Decision

- `docs/guides/ui-ux-pro-max/` 判定为 `delete`
- 当前 docs concern 下的替代真相源不是另一组 Markdown guide，而是项目内 skill 源文件：
  - `.codex/skills/ui-ux-pro-max/SKILL.md`
- 历史治理记录仅保留本执行报告，不保留该 family 作为 active docs surface

## Changes

- 从 `docs/INDEX.md` 移除 `Ui Ux Pro Max` 根导航暴露
- 从 hygiene 测试中移除把 `ui-ux-pro-max` 当作活跃 docs family 的守护断言
- 删除 `docs/guides/ui-ux-pro-max/` 下的 skill 运行产物文档

## Gate Check

- active navigation:
  - `docs/INDEX.md` 已不再暴露 `guides/ui-ux-pro-max/`
- hygiene guard:
  - 测试已改为防止该目录重新作为 active docs family 回流
- residual references:
  - 历史报告中残留的路径仅作为历史快照保留，不再构成 active docs routing

## Expected Effect

- 文档系统不再把 skill 运行产物误导为仓库级 guide family
- 后续若再次运行同名 skill，新增产物也不应自动并入 `docs/INDEX.md` 或 hygiene 主守护
- active docs surface 继续集中在真正承担流程、运行、治理或功能说明职责的 trunks / families
