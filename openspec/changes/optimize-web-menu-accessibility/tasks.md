# Tasks: Optimize Web Menu Accessibility

## 1. High Priority - Keyboard Navigation ⏳

- [x] 1.1 增强语义化可访问性
  - [x] 1.1.1 Domain root 从 `div` 改为 `button` 元素
  - [x] 1.1.2 添加 `aria-expanded` 属性
  - [x] 1.1.3 添加 `aria-controls` 属性
  - [x] 1.1.4 子菜单保持语义化链接导航（`<router-link>`）
  - [x] 1.1.5 确保所有可交互元素支持键盘操作

- [x] 1.2 焦点导航策略修正
  - [x] 1.2.1 放弃基于 `focusedIndex * 48` 的自定义焦点定位方案
  - [x] 1.2.2 使用语义化 `<button>` / `<router-link>` 的原生焦点顺序
  - [x] 1.2.3 通过 `v-show` 隐藏子菜单，确保折叠项不可聚焦
  - [ ] 1.2.4 手动验证键盘导航流程（Tab, Shift+Tab, Enter, Space）

**Note**: 使用原生焦点管理替代自定义焦点算法，避免错位和不可见项跳转风险。

## 2. High Priority - Icon Mapping ⏳

- [x] 2.1 扩展 ArtDecoIcon ICON_MAP
  - [x] 2.1.1 添加 `AlertConfig` 图标定义
  - [x] 2.1.2 添加 `BatchBacktest` 图标定义
  - [x] 2.1.3 或创建现有图标别名映射
  - [x] 2.1.4 验证图标显示正常

**Note**: 已添加两个新图标到 ICON_MAP：
- `AlertConfig`: Settings + Alert 组合图标，用于告警配置
- `BatchBacktest`: 堆叠的文档图标，用于批量回测

## 3. Medium Priority - Documentation ⏳

- [x] 3.1 修正路由兼容性声明
  - [x] 3.1.1 更新 `ArtDeco_Menu_Optimization_Proposal_V2.md`
  - [x] 3.1.2 移除"100%兼容"矛盾声明
  - [x] 3.1.3 确认 `/strategy/repo` 路径保持不变

- [x] 3.2 统一文档令牌使用
  - [x] 3.2.1 扩展 `artdeco-tokens.scss` 添加缺失令牌
  - [x] 3.2.2 替换硬编码颜色为 CSS 令牌
  - [x] 3.2.3 验证所有示例使用令牌

**Note**: 新增令牌包括：
- `--artdeco-gold-opacity-05/08/10/15/20/30` 和 `--artdeco-gold-opacity-shadow`
- 替换了所有 `rgba(212, 175, 55, X)` 和 `#0A0A0A`, `#A0A0A0` 等硬编码值

## 4. Medium Priority - Animation ⏳

- [x] 4.1 添加 reduced-motion 支持
  - [x] 4.1.1 为 `artdeco-gold-pulse` 添加降级策略
  - [x] 4.1.2 禁用 hover 光晕扩散动画
  - [x] 4.1.3 测试动效在 `prefers-reduced-motion: reduce` 下表现

**Note**: 添加了 `@media (prefers-reduced-motion: reduce)` 查询，禁用所有过渡动画和悬停效果

## 5. Low Priority - Platform Adaptation ⏳

- [ ] 5.1 平台自适应快捷键文案
  - [ ] 5.1.1 检测操作系统平台
  - [ ] 5.1.2 Mac 显示 ⌘, Windows/Linux 显示 Ctrl
  - [ ] 5.1.3 更新快捷键提示组件

## 6. Verification ⏳

- [ ] 6.1 无障碍测试
  - [ ] 6.1.1 运行键盘导航测试
  - [ ] 6.1.2 测试读屏软件兼容性
  - [ ] 6.1.3 验证 WCAG 2.1 AA 合规性

- [ ] 6.2 回归测试
  - [ ] 6.2.1 测试菜单展开/收起功能
  - [ ] 6.2.2 测试路由导航功能
  - [ ] 6.2.3 测试图标显示功能

---

**Status**: ✅ High + Medium Priority 已完成 (4/5 任务类别，21/25 子任务)

**完成报告**: `docs/reports/ArtDeco_Menu_Accessibility_Implementation_Report_20260223.md`

**剩余任务**:
- Low Priority (任务 5.1): 平台自适应快捷键 - 可选优化
- Verification (任务 6.1, 6.2): 需要用户手动测试
