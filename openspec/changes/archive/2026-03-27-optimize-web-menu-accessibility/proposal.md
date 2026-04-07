# Change: Optimize Web Menu Accessibility

> **历史计划说明**:
> 本文件记录某次历史提案、计划或分工设想，反映的是当时准备推动的方向与范围，而非当前已生效事实。
> 若其内容与现行 `architecture/STANDARDS.md`、当前 `openspec/specs/`、已归档结论或实际实现不一致，应以 `architecture/STANDARDS.md`、当前 `openspec/specs/` 正式规格与实际实现为准，并将已归档结论仅视为历史背景。


## Why

基于用户反馈，当前 ArtDeco Web 菜单系统存在 8 个无障碍和可用性问题，影响用户体验和 WCAG 2.1 合规性。

**关键问题**:
1. 键盘导航缺乏语义化可访问性 - Tab 流与读屏语义不完整
2. 焦点定位算法会错位并跳转到不可见项
3. 新增图标名未在图标映射中定义
4. 路由兼容性声明与实际冲突
5. 动效方案未覆盖 `prefers-reduced-motion`
6. 文档内治理口径自相矛盾
7. 快捷键文案偏 Mac (⌘K/⌘B)
8. 菜单优化提案相关调整

## What Changes

- **High Priority**: 增强键盘导航无障碍性
  - Domain root 从 `div` 改为语义化 `button` 元素
  - 添加完整的 ARIA 属性 (`aria-expanded`, `aria-controls`)
  - 实现 WCAG 2.1 AA 级别键盘导航规范

- **High Priority**: 焦点导航策略修正
  - 移除基于固定高度的自定义焦点算法方案
  - 使用语义化元素的原生焦点顺序（Tab/Shift+Tab）
  - 通过隐藏状态保证不可见项不可聚焦

- **High Priority**: 扩展 ArtDecoIcon ICON_MAP
  - 添加 `AlertConfig`, `BatchBacktest` 等新图标定义
  - 或使用现有相似图标别名

- **Medium Priority**: 修正路由兼容性
  - 保持 `/strategy/repo` 路径不变（确保向后兼容）
  - 更新提案文档移除"100%兼容"矛盾声明

- **Medium Priority**: 添加 reduced-motion 支持
  - 为动效添加 `@media (prefers-reduced-motion: reduce)` 降级策略
  - 禁用持续脉冲动画和 hover 光晕扩散

- **Medium Priority**: 统一文档令牌使用
  - 将硬编码颜色替换为 CSS 令牌
  - 扩展 `artdeco-tokens.scss` 添加缺失令牌

- **Low Priority**: 平台自适应快捷键文案
  - 检测平台并显示对应快捷键符号（Mac: ⌘, Windows/Linux: Ctrl）

## Impact

- **Affected specs**: `accessibility` (新增)
- **Affected code**:
  - `web/frontend/src/components/artdeco/trading/ArtDecoCollapsibleSidebar.vue`
  - `web/frontend/src/components/artdeco/core/ArtDecoIcon.vue`
  - `web/frontend/src/styles/artdeco-tokens.scss`
  - `docs/reports/ArtDeco_Menu_Optimization_Proposal_V2.md`

- **Breaking changes**: 无（向后兼容）

- **Migration required**: 无

## Related

- **Original Proposal**: `docs/reports/ArtDeco_Menu_Optimization_Proposal_V2.md`
- **User Feedback**: 8 个详细反馈点（已记录在对话历史中）
- **Related Change**: `fix-codex-review-critical-issues` (已完成)

## Status

✅ **已批准并实施** - High + Medium Priority 已完成，Low/Verification 作为后续任务
