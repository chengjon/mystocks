# ArtDeco Component Development Guide (V3.1 Governance Baseline)

本文档定义 MyStocks 项目中 ArtDeco 组件的工程标准与交付规范，适用于 v3/v3.1 治理基线。

## 1. 组件组织铁律

### 1.1 `components/[Domain]/`：稳定、可复用、跨页面
- 存放可复用的领域组件。
- 不绑定单页初始化逻辑。
- 需具备可测试性。

### 1.2 `[Domain]-tabs/`：页面级页签块、不可复用
- 存放页面专属 Tab 子面板。
- 不允许跨页面导出复用。
- 可包含该页面专属业务逻辑。

> `tabs/` 只放页面块，`components/` 只放可复用组件。

## 2. 物理目录映射

| 目录路径 | 属性 | 适用场景示例 |
|:---|:---|:---|
| `src/components/artdeco/base/` | 原子 UI | Button, Card, Input |
| `src/views/artdeco-pages/components/[domain]/` | 通用业务 | `ArtDecoRealtimeMonitor`, `ArtDecoRiskGauge` |
| `src/views/artdeco-pages/[domain]-tabs/` | 页面块 | `MarketFundFlowTab`, `StrategyConfigTab` |
| `src/components/artdeco/core/` | 框架级 | Header, Sidebar, Skeleton |

## 3. 工程编码标准

### 3.1 样式导入规范（强制）
必须使用 SCSS，并通过 token 系统定义颜色、间距与字体。

```vue
<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.your-component {
  background: var(--artdeco-bg-card);
  padding: var(--artdeco-spacing-4);
  color: var(--artdeco-gold-primary);
}
</style>
```

### 3.2 金融语义颜色
- 盈利/上涨：`var(--artdeco-profit)` 或 `var(--artdeco-rise)`
- 亏损/下跌：`var(--artdeco-loss)` 或 `var(--artdeco-down)`

### 3.3 响应式网格
优先使用统一 Mixin 保证断点一致性。

## 4. 可验证性核对表

提交 ArtDeco 变更前至少完成：
- [ ] 组件放置目录符合铁律。
- [ ] 颜色/间距/字体使用 `--artdeco-*` 变量。
- [ ] A 股红涨绿跌语义正确。
- [ ] 页面分拆边界清晰。
- [ ] `npx vue-tsc --noEmit` 通过。

---
**维护口径**: V3.1 Governance Baseline
**最后审核**: 2026-02-13
