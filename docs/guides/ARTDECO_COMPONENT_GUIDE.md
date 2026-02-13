# ArtDeco Component Development Guide (V3.1 Governance Baseline)

本文档定义了 MyStocks 项目中 ArtDeco 风格组件的工程标准与交付规范，并作为 V3.1 Governance Baseline 的开发准入文档。

## 1. 组件组织铁律 (Architectural Iron Law)

为防止分拆过程中的目录膨胀与逻辑耦合，必须严格遵守以下确权定义：

### 1.1 `components/[Domain]/` —— 稳定、可复用、跨页面
*   **存放内容**: 领域内通用业务组件；可被多个页面、多个 Tabs 复用；纯展示或纯逻辑封装，不绑定特定页面。
*   **核心规则**:
    *   **必须可复用**: 严禁存放仅某个特定 Tab 专属的代码。
    *   **无页面逻辑**: 禁止写页面级初始化或复杂的全局状态修改逻辑。
    *   **稳定可测试**: 必须具备良好的单元测试基础。

### 1.2 `[Domain]-tabs/` —— 页面级、页签块、不可复用
*   **存放内容**: 属于某个业务页面的子面板/子路由；业务逻辑重、一次性、页面专属。
*   **核心规则**:
    *   **专属分拆**: 仅用于拆分超大 Vue 文件，不做通用组件。
    *   **禁止外导**: 严禁被该页面以外的任何页面 `import`。
    *   **逻辑闭环**: 允许包含该 Tab 专属的复杂业务逻辑。

> **⚠️ 铁律**: `tabs/` 目录只放 “页面块”，`components/` 只放 “可复用组件”。

## 2. 物理目录映射 (Physical Mapping)

| 目录路径 | 属性 | 适用场景示例 |
|:---|:---|:---|
| `src/components/artdeco/base/` | 原子 UI | Button, Card, Input |
| `src/views/artdeco-pages/components/[domain]/` | 通用业务 | `ArtDecoRealtimeMonitor`, `ArtDecoRiskGauge` |
| `src/views/artdeco-pages/[domain]-tabs/` | 页面块 | `MarketFundFlowTab`, `StrategyConfigTab` |
| `src/components/artdeco/core/` | 框架级 | Header, Sidebar, Skeleton |

## 3. 工程编码标准 (Engineering Standards)

### 2.1 样式导入规范 (强制)
必须使用 SCSS 且必须通过令牌系统定义样式。禁止使用内联样式或硬编码颜色。
```vue
<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.your-component {
  background: var(--artdeco-bg-card);
  padding: var(--artdeco-spacing-4);
  color: var(--artdeco-accent-gold);
}
</style>
```

### 2.2 金融语义颜色
在显示盈亏数据时，必须调用语义别名：
*   **盈利/上涨**: 使用 `var(--artdeco-profit)` 或 `var(--artdeco-rise)`
*   **亏损/下跌**: 使用 `var(--artdeco-loss)` 或 `var(--artdeco-down)`

### 2.3 响应式网格
优先使用全局 Mixin 实现布局，确保在各断点下的一致性：
```scss
.stats-grid {
  @include artdeco-grid(4, var(--artdeco-spacing-4));
}
```

## 3. 可验证性核对表 (Definition of Done)

在提交任何 ArtDeco 相关变更前，必须自测以下项目：
- [ ] **物理一致性**: 新组件是否放在了正确的分类目录下？
- [ ] **令牌完整性**: 是否所有颜色和间距都使用了 `--artdeco-*` 变量？
- [ ] **A 股符合度**: 涨跌幅颜色是否符合“红涨绿跌”规范？
- [ ] **分拆有效性**: 大型 Vue 文件是否已按 Tab 有效分拆，且父组件正确下发配置？
- [ ] **编译验证**: `npx vue-tsc --noEmit` 是否零错误？

---
**维护者**: Frontend Architecture Team
**治理口径**: V3.1 Governance Baseline
**最后审核**: 2026-02-08 (V3.1 Governance Baseline)
