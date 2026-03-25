# ArtDeco Grid系统快速参考指南

**版本**: 1.0
**最后更新**: 2026-01-22
**目标用户**: Vue.js开发者
**阅读时间**: 5分钟

---

## 📐 核心概念

ArtDeco Grid系统提供了一套完整的响应式Grid布局方案，用于快速构建一致的页面布局。

### 设计原则

1. **语义优先** - 优先使用语义化Grid类（`.charts-section`, `.summary-section`等）
2. **响应式** - 所有Grid类自动响应：4列→3列→2列→1列
3. **间距统一** - 使用ArtDeco间距令牌（`--artdeco-spacing-*`）
4. **移动端无关** - 仅优化桌面端（1280px+）

---

## 🎯 语义化Grid类（推荐使用）

### 1. `.charts-section` - 图表区域（3列Grid）

**用途**: Dashboard图表、技术指标卡片
**列数**: 3列 → 2列 → 1列（响应式）
 **最小宽度**: 280px
 **间距**: var(--artdeco-spacing-6) (24px)

```vue
<!-- ✅ 推荐：使用语义化类 -->
<section class="charts-section">
  <ArtDecoStatCard label="指标1" />
  <ArtDecoStatCard label="指标2" />
  <ArtDecoStatCard label="指标3" />
</section>
```

**实际应用**:
- 技术指标概览（RSI、MACD、KDJ等）
- 系统监控状态（API响应、内存使用等）
- Dashboard主图表区域

---

### 2. `.summary-section` - 统计摘要（4列Grid）

**用途**: 关键指标统计卡片
**列数**: 4列 → 3列 → 2列 → 1列（响应式）
**最小宽度**: 250px
**间距**: var(--artdeco-spacing-6) (24px)

```vue
<section class="summary-section">
  <ArtDecoStatCard label="沪股通净流入" :value="28.6" />
  <ArtDecoStatCard label="深股通净流入" :value="30.2" />
  <ArtDecoStatCard label="北向资金总额" :value="58.8" />
  <ArtDecoStatCard label="主力净流入" :value="126.5" />
</section>
```

**实际应用**:
- 资金流向概览（沪股通、深股通、北向资金、主力）
- 市场主要指数（上证、深证、创业板）
- 关键统计指标（涨跌家数、成交金额等）

---

### 3. `.flow-section` - 资金流向（2列Grid）

**用途**: 左右对比、资金流向卡片
**列数**: 2列 → 1列（响应式）
**最小宽度**: 350px
**间距**: var(--artdeco-spacing-6) (24px)

```vue
<section class="flow-section">
  <ArtDecoCard title="资金流向">
    <!-- 内容 -->
  </ArtDecoCard>
  <ArtDecoCard title="市场情绪">
    <!-- 内容 -->
  </ArtDecoCard>
</section>
```

**实际应用**:
- 资金流向 + 市场情绪（左右对比）
- 买入 + 卖出订单对比
- 龙虎榜 + 大宗交易对比

---

### 4. `.heatmap-section` - 板块热力图（自适应Grid）

**用途**: 板块热度、标签云、自适应卡片
**列数**: 自动填充（auto-fill）
**最小宽度**: 120px
**间距**: var(--artdeco-spacing-4) (16px)

```vue
<section class="heatmap-section">
  <div class="heat-item" v-for="sector in sectors" :key="sector.name">
    <div class="sector-name">{{ sector.name }}</div>
    <div class="sector-change">{{ sector.change }}%</div>
    <div class="heat-bar">
      <div class="heat-fill" :style="{ width: sector.change * 2 + '%' }"></div>
    </div>
  </div>
</section>
```

**实际应用**:
- 板块热度展示（人工智能、新能源汽车等）
- 标签云、关键词卡片
- 自适应小卡片布局

---

### 5. `.pool-section` - 股票池（卡片Grid）

**用途**: 股票列表、卡片式网格
**列数**: 自动填充（auto-fill, minmax(300px, 1fr)）
**最小宽度**: 300px
**间距**: var(--artdeco-spacing-4) (16px)

```vue
<section class="pool-section">
  <StockCard v-for="stock in stocks" :key="stock.code" :stock="stock" />
</section>
```

**实际应用**:
- 自选股池展示
- 策略选股列表
- 股票卡片网格

---

### 6. `.nav-section` - 导航卡片（3列Grid，紧凑间距）

**用途**: 快速导航、功能入口
**列数**: 3列（固定）
**最小宽度**: 1fr
**间距**: var(--artdeco-spacing-4) (16px)

```vue
<nav class="nav-section">
  <NavLinkCard v-for="link in navLinks" :key="link.path" :link="link" />
</nav>
```

**实际应用**:
- Dashboard快速导航卡片
- 功能入口菜单
- 快捷方式区域

---

## 🛠️ 工具类（高级使用）

### 基础Grid工具类

| 类名 | 用途 | 列数 | 响应式 |
|------|------|------|--------|
| `.artdeco-grid-2` | 2列Grid | 2列 | 2→1 |
| `.artdeco-grid-3` | 3列Grid | 3列 | 3→2→1 |
| `.artdeco-grid-4` | 4列Grid | 4列 | 4→3→2→1 |
| `.artdeco-grid-auto` | 自适应Grid | auto-fill | 自动 |
| `.artdeco-grid-cards` | 卡片Grid | minmax(300px, 1fr) | 自动 |

### 间距工具类

| 类名 | 间距值 | 用途 |
|------|--------|------|
| `.gap-2` | 8px | 紧凑间距 |
| `.gap-3` | 12px | 小间距 |
| `.gap-4` | 16px | 标准间距 |
| `.gap-6` | 24px | 大间距 |
| `.gap-8` | 32px | 超大间距 |

### 对齐工具类

| 类名 | 用途 |
|------|------|
| `.grid-start` | 左对齐 |
| `.grid-center` | 居中对齐 |
| `.grid-end` | 右对齐 |
| `.grid-stretch` | 拉伸填充 |

---

## 📋 最佳实践

### ✅ 推荐做法

1. **优先使用语义化类**
   ```vue
   <!-- ✅ 好：语义化类 -->
   <section class="charts-section">
     <ArtDecoStatCard label="指标1" />
     <ArtDecoStatCard label="指标2" />
   </section>
   ```

2. **使用语义化HTML标签**
   ```vue
   <!-- ✅ 好：使用section -->
   <section class="summary-section">...</section>

   <!-- ❌ 差：使用div -->
   <div class="summary-section">...</div>
   ```

3. **保持简洁**
   ```vue
   <!-- ✅ 好：直接使用Grid类 -->
   <section class="charts-section">...</section>

   <!-- ❌ 差：自定义Grid样式 -->
   <div class="my-custom-grid">...</div>
   ```

### ❌ 避免做法

1. **不要硬编码Grid样式**
   ```vue
   <!-- ❌ 差：硬编码Grid -->
   <div style="display: grid; grid-template-columns: repeat(3, 1fr);">...</div>
   ```

2. **不要重复定义Grid模式**
   ```scss
   // ❌ 差：重复定义
   .my-indicators-grid {
     display: grid;
     grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
     gap: 16px;
   }

   // ✅ 好：使用现有语义类
   .indicators-container {
     @extend .charts-section;
   }
   ```

3. **不要忽略响应式**
   ```vue
   <!-- ❌ 差：固定列数 -->
   <div style="display: grid; grid-template-columns: repeat(3, 1fr);">

   <!-- ✅ 好：自动响应 -->
   <section class="charts-section">
   ```

---

## 🔄 迁移指南

### 从自定义Grid类迁移到语义化类

| 旧的自定义类 | 替换为 | 原因 |
|-------------|--------|------|
| `.fund-flow-grid` | `.summary-section` | 4列统计卡片 |
| `.indicators-grid` | `.charts-section` | 3列指标卡片 |
| `.monitoring-grid` | `.charts-section` | 多个监控项 |
| `.market-sentiment-grid` | `.flow-section` | 2列对比卡片 |

### 迁移步骤

1. **识别自定义Grid类**
   ```bash
   grep -r "display: grid" src/views/
   ```

2. **分析Grid模式**
   - 列数：2列、3列、4列？
   - 用途：图表、统计、流向？
   - 间距：多少px？

3. **选择对应的语义类**
   - 3列 → `.charts-section`
   - 4列 → `.summary-section`
   - 2列 → `.flow-section`

4. **替换并验证**
   ```vue
   <!-- 替换前 -->
   <div class="my-custom-grid">...</div>

   <!-- 替换后 -->
   <section class="charts-section">...</section>
   ```

5. **删除不再使用的自定义样式**
   ```scss
   // 删除自定义Grid定义
   .my-custom-grid { /* ... */ }
   ```

---

## 📊 Grid系统对比表

| 特性 | 语义化Grid类 | 工具类 | 自定义Grid |
|------|-------------|--------|-----------|
| **易用性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **维护性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **一致性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **灵活性** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **推荐度** | ✅ 首选 | ⚠️ 补充 | ❌ 避免 |

---

## 💡 使用场景速查

| 场景 | 推荐类 | 示例 |
|------|--------|------|
| **Dashboard主图表** | `.charts-section` | 3个K线图 |
| **资金流向统计** | `.summary-section` | 4个资金指标 |
| **市场情绪对比** | `.flow-section` | 2个对比卡片 |
| **板块热度** | `.heatmap-section` | 自适应板块卡片 |
| **自选股池** | `.pool-section` | 股票卡片网格 |
| **快速导航** | `.nav-section` | 导航卡片 |
| **特殊布局** | `.artdeco-grid-*` | 自定义布局 |

---

## 🎨 样式覆盖（高级）

如果需要覆盖默认样式：

```vue
<style scoped lang="scss">
.my-container {
  // 继承语义化Grid布局
  @extend .charts-section;

  // 覆盖特定样式
  gap: var(--artdeco-spacing-8); // 增大间距

  // 添加自定义样式
  .my-item {
    border: 2px solid var(--artdeco-gold-primary);
  }
}
</style>
```

---

## 📚 相关文档

- **Grid系统完整文档**: `docs/api/ARTDECO_TRADING_CENTER_OPTIMIZED_V3.1.md`
- **Grid系统实现**: `web/frontend/src/styles/artdeco-grid.scss`
- **ArtDeco设计令牌**: `web/frontend/src/styles/artdeco-tokens.scss`
- **布局优化提案**: `docs/reports/ARTDECO_LAYOUT_OPTIMIZATION_PROPOSAL.md`

---

## 🔧 常见问题

### Q1: 什么时候使用语义类vs工具类？

**A**:
- **优先使用语义类**（`.charts-section`, `.summary-section`）- 对应明确的业务场景
- **工具类作为补充**（`.artdeco-grid-3`, `.gap-4`）- 特殊布局需求

### Q2: 如何自定义Grid间距？

**A**: 使用间距工具类或覆盖样式：
```vue
<!-- 方式1: 添加gap工具类 -->
<section class="charts-section gap-8">...</section>

<!-- 方式2: 覆盖样式 -->
<style scoped>
.custom-charts {
  @extend .charts-section;
  gap: var(--artdeco-spacing-8);
}
</style>
```

### Q3: Grid系统支持移动端吗？

**A**: 不支持。本项目仅支持桌面端（1280px+），Grid系统的响应式仅针对不同桌面屏幕尺寸，不考虑移动端适配。

### Q4: 如何处理奇数个元素？

**A**: Grid系统自动处理：
```vue
<!-- 3列Grid，5个元素 -->
<section class="charts-section">
  <div>元素1</div>
  <div>元素2</div>
  <div>元素3</div>
  <div>元素4</div>  <!-- 自动换行 -->
  <div>元素5</div>
</section>
```

---

**文档维护**: Grid系统团队
**反馈渠道**: 项目Issues
**版本历史**:
- v1.0 (2026-01-22): 初始版本
