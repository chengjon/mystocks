# Accessibility Spec Delta

## ADDED Requirements

### Requirement: Semantic HTML Navigation
所有导航菜单 MUST 使用语义化 HTML 元素，确保键盘导航和屏幕阅读器兼容性。

#### Scenario: Button-based navigation
- **WHEN** 创建可点击的菜单项
- **THEN** 开发者 MUST 使用 `<button>` 元素而非 `<div>`
- **AND** MUST 添加适当的 `aria-expanded` 和 `aria-controls` 属性

#### Scenario: Native navigation semantics
- **WHEN** 实现嵌套导航结构
- **THEN** 父级切换控件 MUST 使用语义化 `<button>`
- **AND** 子级导航 MUST 使用语义化链接（如 `<a>` / `<router-link>`）

### Requirement: Keyboard Focus Management
焦点管理系统 MUST 正确处理可折叠菜单和滚动容器。

#### Scenario: Visible items only
- **WHEN** 计算可聚焦菜单项
- **THEN** 系统 MUST 仅包含当前可见的菜单项
- **AND** MUST 排除折叠/隐藏的子菜单项

#### Scenario: Native focus order
- **WHEN** 使用浏览器原生键盘导航
- **THEN** 系统 MUST 遵循原生焦点顺序（Tab/Shift+Tab）
- **AND** 隐藏项 MUST NOT 可聚焦

### Requirement: Icon Mapping Completeness
所有使用的图标 MUST 在 `ArtDecoIcon` 组件的 `ICON_MAP` 中定义。

#### Scenario: Icon validation
- **WHEN** 使用新图标名
- **THEN** 开发者 MUST 先在 `ICON_MAP` 中定义图标路径
- **OR** MUST 使用已定义的图标别名

#### Scenario: Icon fallback
- **WHEN** 图标未定义
- **THEN** 系统 MUST 显示警告而非空白
- **AND** MUST 提供回退图标

### Requirement: Reduced Motion Support
所有动画效果 MUST 尊重用户的 `prefers-reduced-motion` 偏好设置。

#### Scenario: Animation disable
- **WHEN** 用户启用 reduced-motion
- **THEN** 系统 MUST 禁用所有持续动画（如脉冲动画）
- **AND** MUST 禁用大范围 hover 动画

#### Scenario: Fallback behavior
- **WHEN** reduced-motion 启用
- **THEN** 动画 MUST 立即完成或完全禁用
- **AND** MUST 保留功能状态变化（如展开/收起）

### Requirement: Platform-Adaptive Keyboard Shortcuts
快捷键显示 MUST 根据用户操作系统平台自适应显示正确的修饰键符号。

#### Scenario: Platform detection
- **WHEN** 显示快捷键提示
- **THEN** 系统 MUST 检测操作系统平台
- **AND** Mac 显示 ⌘, Windows/Linux 显示 Ctrl

#### Scenario: Unified display
- **WHEN** 快捷键需要跨平台显示
- **THEN** 系统 MAY 使用通用格式 "⌘/Ctrl"
- **OR** MUST 动态切换显示

### Requirement: CSS Token Consistency
所有样式代码 MUST 使用 CSS 设计令牌，禁止硬编码颜色值。

#### Scenario: Token usage
- **WHEN** 定义颜色或样式
- **THEN** 开发者 MUST 使用 CSS 变量（如 `var(--artdeco-gold-primary)`）
- **AND** MUST NOT 使用硬编码的 hex 或 rgba 值

#### Scenario: Token extensibility
- **WHEN** 需要新样式令牌
- **THEN** 开发者 MUST 在 `artdeco-tokens.scss` 中添加令牌定义
- **AND** MUST 使用语义化命名（如 `--menu-item-active`）

## MODIFIED Requirements

### Requirement: Route Compatibility Assurance
路由变更 MUST 维持向后兼容性，不破坏现有深链和收藏夹。

#### Scenario: Path preservation
- **WHEN** 重命名或重构路由
- **THEN** 开发者 MUST 保留旧路径作为别名
- **OR** MUST 不改变现有路径
- **AND** MUST NOT 声称"100%兼容"如果存在破坏性变更

## REMOVED Requirements

无

## RENAMED Requirements

无
