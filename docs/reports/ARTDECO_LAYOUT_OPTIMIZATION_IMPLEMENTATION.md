# ArtDeco 布局优化实施代码

**配套文档**: `ARTDECO_LAYOUT_OPTIMIZATION_ANALYSIS.md`
**生成时间**: 2026-01-04
**实施方式**: 替换各页面 `<style scoped>` 区块

---

## 📋 实施说明

### 使用方法

对每个需要优化的页面:

1. 打开文件 `web/frontend/src/views/artdeco/[PAGE_NAME].vue`
2. 定位到 `<style scoped lang="scss">` 区块
3. **完全替换**为下方对应的优化代码
4. 保存文件，运行 TypeScript 检查

### 批量替换脚本 (可选)

```bash
#!/bin/bash
# optimize-artdeco-layouts.sh

PAGES=(
  "ArtDecoStrategyLab"
  "ArtDecoBacktestArena"
  "ArtDecoDataAnalysis"
  "ArtDecoDashboard"
  "ArtDecoMarketCenter"
)

for page in "${PAGES[@]}"; do
  echo "Optimizing $page..."
  # 手动复制粘贴优化代码
done
```

---

## 1️⃣ ArtDecoStrategyLab.vue - 优化样式

**替换位置**: 第 376-452 行

```scss
<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

// ========== 页面容器 ==========
.artdeco-strategy-lab {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-16);  // 128px - Section spacing
  padding: var(--artdeco-spacing-16) var(--artdeco-spacing-4);  // 128px 32px
  background: var(--artdeco-bg-primary);
  min-height: 100vh;
  max-width: 1400px;  // max-w-7xl
  margin: 0 auto;     // 居中对齐
}

// ========== 网格系统 ==========
.artdeco-grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);  // 对称2列
  gap: var(--artdeco-spacing-4);  // 32px - Standard grid gap
}

.artdeco-stats-triple {
  display: grid;
  grid-template-columns: repeat(3, 1fr);  // 对称3列
  gap: var(--artdeco-spacing-4);  // 32px - Consistent gap
}

// ========== 卡片和区块 ==========
.artdeco-filter-section {
  padding: var(--artdeco-spacing-4);  // 32px - Card padding
}

// ========== 分页 ==========
.artdeco-pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: var(--artdeco-spacing-8);  // 64px
  padding-top: var(--artdeco-spacing-4);  // 32px
  border-top: 1px solid rgba(212, 175, 55, 0.1);
}

// ========== 数据颜色 ==========
.text-mono {
  font-family: var(--artdeco-font-mono);
}

.data-rise {
  color: var(--artdeco-data-rise);
}

.data-fall {
  color: var(--artdeco-data-fall);
}

// ========== 响应式设计 ==========
@media (max-width: 1440px) {
  .artdeco-strategy-lab {
    gap: var(--artdeco-spacing-8);  // 64px - 减小间距
    padding: var(--artdeco-spacing-8) var(--artdeco-spacing-4);
  }

  .artdeco-grid-2 {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1080px) {
  .artdeco-stats-triple {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .artdeco-strategy-lab {
    gap: var(--artdeco-spacing-4);  // 32px - 移动端进一步减小
    padding: var(--artdeco-spacing-4) var(--artdeco-spacing-2);  // 32px 16px
  }
}
</style>
```

---

## 2️⃣ ArtDecoBacktestArena.vue - 优化样式

**替换位置**: 第 502-663 行

```scss
<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

// ========== 页面容器 ==========
.artdeco-backtest-arena {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-16);  // 128px
  padding: var(--artdeco-spacing-16) var(--artdeco-spacing-4);
  background: var(--artdeco-bg-primary);
  min-height: 100vh;
  max-width: 1400px;
  margin: 0 auto;
}

// ========== 网格系统 ==========
.artdeco-grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);  // 对称4列
  gap: var(--artdeco-spacing-4);  // 32px
}

.artdeco-grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);  // 对称2列
  gap: var(--artdeco-spacing-4);  // 32px
}

// ========== 指标区块 ==========
.artdeco-metrics-section {
  padding: var(--artdeco-spacing-4);  // 32px
}

.artdeco-metrics-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);  // 对称6列
  gap: var(--artdeco-spacing-4);  // 32px
}

.metric-item {
  text-align: center;
  padding: var(--artdeco-spacing-4);  // 32px
  background: rgba(212, 175, 55, 0.05);
  border: 1px solid var(--artdeco-accent-gold);
  border-radius: var(--artdeco-radius-sm);
}

.metric-label {
  display: block;
  font-size: var(--artdeco-font-size-small);
  color: var(--artdeco-fg-muted);
  margin-bottom: var(--artdeco-spacing-1);  // 8px
}

.metric-value {
  display: block;
  font-size: var(--artdeco-font-size-h3);
  font-family: var(--artdeco-font-mono);
  font-weight: 700;
  color: var(--artdeco-accent-gold);
}

// ========== 信号区块 ==========
.artdeco-signals-section {
  padding: var(--artdeco-spacing-4);  // 32px
}

.artdeco-signals-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);  // 对称2列
  gap: var(--artdeco-spacing-4);  // 32px
}

.signal-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--artdeco-spacing-2);  // 16px
  padding: var(--artdeco-spacing-4);  // 32px
  background: rgba(212, 175, 55, 0.03);
  border: 1px solid var(--artdeco-accent-gold);
  border-radius: var(--artdeco-radius-sm);
}

.signal-count {
  font-size: var(--artdeco-font-size-h2);
  font-weight: 700;
  color: var(--artdeco-accent-gold);
}

.signal-stats {
  margin-top: var(--artdeco-spacing-2);  // 16px
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--artdeco-spacing-1);  // 8px
}

.stat-label {
  font-size: var(--artdeco-font-size-small);
  color: var(--artdeco-fg-muted);
}

.stat-value {
  font-size: var(--artdeco-font-size-body);
  font-weight: 600;
  font-family: var(--artdeco-font-mono);
}

// ========== 表格区块 ==========
.artdeco-table-section {
  padding: var(--artdeco-spacing-4);  // 32px
}

// ========== 分页 ==========
.artdeco-pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: var(--artdeco-spacing-8);  // 64px
  padding-top: var(--artdeco-spacing-4);  // 32px
  border-top: 1px solid rgba(212, 175, 55, 0.1);
}

// ========== 文本样式 ==========
.text-mono {
  font-family: var(--artdeco-font-mono);
}

.data-rise {
  color: var(--artdeco-data-rise);
}

.data-fall {
  color: var(--artdeco-data-fall);
}

// ========== 响应式设计 ==========
@media (max-width: 1440px) {
  .artdeco-grid-4 {
    grid-template-columns: repeat(2, 1fr);  // 保持偶数列
  }

  .artdeco-backtest-arena {
    gap: var(--artdeco-spacing-8);  // 64px
    padding: var(--artdeco-spacing-8) var(--artdeco-spacing-4);
  }
}

@media (max-width: 1080px) {
  .artdeco-grid-2 {
    grid-template-columns: 1fr;
  }

  .artdeco-metrics-grid {
    grid-template-columns: repeat(3, 1fr);  // 对称3列
  }
}

@media (max-width: 768px) {
  .artdeco-grid-2,
  .artdeco-grid-4 {
    grid-template-columns: 1fr;
  }

  .artdeco-metrics-grid {
    grid-template-columns: repeat(2, 1fr);  // 对称2列
  }

  .artdeco-signals-grid {
    grid-template-columns: 1fr;
  }

  .artdeco-backtest-arena {
    gap: var(--artdeco-spacing-4);  // 32px
    padding: var(--artdeco-spacing-4) var(--artdeco-spacing-2);
  }
}
</style>
```

---

## 3️⃣ ArtDecoDataAnalysis.vue - 优化样式

**替换位置**: 第 558-654 行

```scss
<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

// ========== 页面容器 ==========
.artdeco-data-analysis {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-16);  // 128px
  padding: var(--artdeco-spacing-16) var(--artdeco-spacing-4);
  background: var(--artdeco-bg-primary);
  min-height: 100vh;
  max-width: 1400px;
  margin: 0 auto;
}

// ========== 筛选区块 ==========
.artdeco-filter-section {
  padding: var(--artdeco-spacing-4);  // 32px
}

// ========== 图表网格 ==========
.artdeco-grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);  // 对称3列
  gap: var(--artdeco-spacing-4);  // 32px
}

.artdeco-chart-container {
  width: 100%;
  height: 350px;  // 统一图表高度
}

.chart-controls {
  display: flex;
  gap: var(--artdeco-spacing-2);  // 16px - 内部控件间距
  margin-bottom: var(--artdeco-spacing-4);  // 32px
  justify-content: flex-end;

  .artdeco-button.active {
    background: var(--artdeco-accent-gold);
    color: var(--artdeco-bg-primary);
    border-color: var(--artdeco-accent-gold);
  }
}

// ========== 表格区块 ==========
.artdeco-table-section {
  padding: var(--artdeco-spacing-4);  // 32px
}

// ========== 分页 ==========
.artdeco-pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: var(--artdeco-spacing-8);  // 64px
  padding-top: var(--artdeco-spacing-4);  // 32px
  border-top: 1px solid rgba(212, 175, 55, 0.1);
}

// ========== 数据颜色 ==========
.text-mono {
  font-family: var(--artdeco-font-mono);
}

.data-rise {
  color: var(--artdeco-data-rise);
}

.data-fall {
  color: var(--artdeco-data-fall);
}

// ========== 响应式设计 ==========
@media (max-width: 1440px) {
  .artdeco-grid-3 {
    grid-template-columns: repeat(2, 1fr);  // 对称2列
  }

  .artdeco-data-analysis {
    gap: var(--artdeco-spacing-8);  // 64px
    padding: var(--artdeco-spacing-8) var(--artdeco-spacing-4);
  }
}

@media (max-width: 1080px) {
  .artdeco-grid-3 {
    grid-template-columns: 1fr;
  }

  .artdeco-chart-container {
    height: 300px;  // 移动端减小图表高度
  }
}

@media (max-width: 768px) {
  .chart-controls {
    flex-direction: column;
  }

  .artdeco-chart-container {
    height: 280px;  // 小屏进一步减小
  }

  .artdeco-data-analysis {
    gap: var(--artdeco-spacing-4);  // 32px
    padding: var(--artdeco-spacing-4) var(--artdeco-spacing-2);
  }
}
</style>
```

---

## 4️⃣ ArtDecoDashboard.vue - 优化样式

**替换位置**: 第 309-486 行

```scss
<style scoped lang="scss">
@import '@/styles/artdeco/artdeco-theme.css';

// ========== 页面容器 ==========
.artdeco-dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-8);  // 64px - Dashboard 特有（较小）
  padding: var(--artdeco-spacing-4);  // 32px
  max-width: 1400px;
  margin: 0 auto;
}

// ========== 统计卡片网格 ==========
.artdeco-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);  // 对称4列
  gap: var(--artdeco-spacing-4);  // 32px
}

// ========== 主布局 ==========
.artdeco-main-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: var(--artdeco-spacing-4);  // 32px
}

.main-column {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-4);  // 32px
}

.bottom-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);  // 对称2列
  gap: var(--artdeco-spacing-4);  // 32px
}

// ========== 卡片样式 ==========
.artdeco-card {
  background: var(--artdeco-bg-card);
  border: 2px solid var(--artdeco-gold-dim);
  padding: var(--artdeco-spacing-4);  // 32px ✅
  position: relative;
}

.artdeco-card h3 {
  margin: 0 0 var(--artdeco-spacing-4) 0;  // 32px ✅
  font-family: var(--artdeco-font-display);
  font-size: 1.1rem;
  color: var(--artdeco-gold-primary);
  letter-spacing: 0.2em;  // 添加字间距
  text-transform: uppercase;
}

.artdeco-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-4);  // 32px
}

.artdeco-card-header h3 { margin-bottom: 0; }

.artdeco-chart { height: 400px; }
.artdeco-chart-sm { height: 300px; }

// ========== 策略控制 ==========
.strategy-controls {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-4);  // 32px ✅
}

.control-divider {
  height: 1px;
  background: var(--artdeco-gold-dim);
  opacity: 0.3;
}

.strategy-status-box {
  margin-top: var(--artdeco-spacing-2);  // 16px
  padding: var(--artdeco-spacing-4);  // 32px
  background: rgba(10, 12, 14, 0.5);
  border-left: 3px solid var(--artdeco-silver-muted);
  transition: all 0.5s;
}

.strategy-status-box.active {
  border-left-color: var(--artdeco-gold-primary);
  background: rgba(212, 175, 55, 0.05);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);  // 16px
  font-size: 0.8rem;
  color: var(--artdeco-silver-dim);
}

.active .status-indicator { color: var(--artdeco-gold-primary); }

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--artdeco-silver-muted);
}

.active .status-dot {
  background: var(--artdeco-gold-primary);
  box-shadow: 0 0 8px var(--artdeco-gold-primary);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.4; }
  100% { opacity: 1; }
}

// ========== 侧边栏 ==========
.side-column {
  display: flex;
  flex-direction: column;
}

.side-panel-header {
  padding: var(--artdeco-spacing-4);  // 32px
  border-bottom: 1px solid var(--artdeco-gold-dim);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.side-panel-header h3 {
  margin: 0;
  font-size: 1rem;
}

.symbol-tag {
  background: var(--artdeco-gold-dim);
  color: var(--artdeco-gold-primary);
  padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);  // 4px 8px
  font-family: var(--artdeco-font-mono);
  font-size: 0.75rem;
  font-weight: 600;
}

.side-panel-footer {
  padding: var(--artdeco-spacing-4) var(--artdeco-spacing-5);  // 32px 20px → 统一为 32px
  border-top: 1px solid var(--artdeco-gold-dim);
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);  // 16px
}

.info-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--artdeco-silver-dim);
}

.text-mono {
  font-family: var(--artdeco-font-mono);
  color: var(--artdeco-silver-text);
}

// ========== 响应式设计 ==========
@media (max-width: 1440px) {
  .artdeco-main-layout {
    grid-template-columns: 1fr;
  }
  .side-column {
    flex-direction: row;
    gap: var(--artdeco-spacing-4);  // 32px
  }
  .side-column > * { flex: 1; }
}

@media (max-width: 1080px) {
  .artdeco-stats-grid {
    grid-template-columns: repeat(2, 1fr);  // 对称2列
  }
  .bottom-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .artdeco-stats-grid {
    grid-template-columns: 1fr;
  }
  .side-column {
    flex-direction: column;
  }

  .artdeco-dashboard {
    gap: var(--artdeco-spacing-4);  // 32px
    padding: var(--artdeco-spacing-4) var(--artdeco-spacing-2);
  }
}
</style>
```

---

## 5️⃣ ArtDecoMarketCenter.vue - 优化样式 (模板)

**注意**: 此页面未在本次分析中读取，以下为推荐的标准模板

```scss
<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

// ========== 页面容器 ==========
.artdeco-market-center {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-16);  // 128px
  padding: var(--artdeco-spacing-16) var(--artdeco-spacing-4);
  background: var(--artdeco-bg-primary);
  min-height: 100vh;
  max-width: 1400px;
  margin: 0 auto;
}

// ========== 网格系统 (根据实际需求调整) ==========
.artdeco-grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--artdeco-spacing-4);  // 32px
}

.artdeco-grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--artdeco-spacing-4);  // 32px
}

// ========== 区块样式 ==========
.artdeco-section {
  padding: var(--artdeco-spacing-4);  // 32px
}

.artdeco-pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: var(--artdeco-spacing-8);  // 64px
  padding-top: var(--artdeco-spacing-4);  // 32px
  border-top: 1px solid rgba(212, 175, 55, 0.1);
}

// ========== 响应式设计 ==========
@media (max-width: 1440px) {
  .artdeco-market-center {
    gap: var(--artdeco-spacing-8);  // 64px
    padding: var(--artdeco-spacing-8) var(--artdeco-spacing-4);
  }

  .artdeco-grid-3 {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1080px) {
  .artdeco-grid-2,
  .artdeco-grid-3 {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .artdeco-market-center {
    gap: var(--artdeco-spacing-4);  // 32px
    padding: var(--artdeco-spacing-4) var(--artdeco-spacing-2);
  }
}
</style>
```

---

## 🔍 Token 系统增强建议

在应用上述优化代码前，建议先增强 `artdeco-tokens.scss`:

### 文件: `web/frontend/src/styles/artdeco-tokens.scss`

```scss
// ========== ArtDeco Design Tokens ==========

// Spacing System (明确数值)
$artdeco-spacing-1: 8px;    // 元素内部微小间距
$artdeco-spacing-2: 16px;   // 紧凑间距
$artdeco-spacing-4: 32px;   // 标准间距 - 网格、卡片间隙
$artdeco-spacing-8: 64px;   // 大间距 - Dashboard节间距
$artdeco-spacing-16: 128px; // Section间距 - 页面节间距

// Containers
$artdeco-container-max-width: 1400px;  // max-w-7xl
$artdeco-container-padding: 32px;

// Breakpoints
$artdeco-breakpoint-lg: 1440px;
$artdeco-breakpoint-md: 1080px;
$artdeco-breakpoint-sm: 768px;

// Typography
$artdeco-font-display: 'Marcellus', serif;
$artdeco-font-body: 'Josefin Sans', sans-serif;
$artdeco-font-mono: 'IBM Plex Mono', monospace;

// Font Sizes
$artdeco-font-size-h1: 3rem;     // 48px
$artdeco-font-size-h2: 2.25rem;  // 36px
$artdeco-font-size-h3: 1.75rem;  // 28px
$artdeco-font-size-body: 1rem;   // 16px
$artdeco-font-size-small: 0.875rem;  // 14px

// Letter Spacing
$artdeco-tracking-widest: 0.2em;  // 标题
$artdeco-tracking-wider: 0.1em;   // 副标题
$artdeco-tracking-normal: 0;      // 正文

// Colors
$artdeco-bg-primary: #0A0A0A;     // Obsidian Black
$artdeco-accent-gold: #D4AF37;    // Metallic Gold
$artdeco-data-rise: #C94042;      // 红涨
$artdeco-data-fall: #3D9970;      // 绿跌

// Border Radius
$artdeco-radius-sm: 4px;
$artdeco-radius-md: 8px;
$artdeco-radius-lg: 12px;

// Mixins
@mixin artdeco-container {
  max-width: $artdeco-container-max-width;
  margin: 0 auto;
  padding: 0 $artdeco-container-padding;
}

@mixin artdeco-section {
  padding: $artdeco-spacing-16 0;
}

@mixin artdeco-card {
  padding: $artdeco-spacing-4;
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-accent-gold);
}

// Export as CSS custom properties
:root {
  --artdeco-spacing-1: #{$artdeco-spacing-1};
  --artdeco-spacing-2: #{$artdeco-spacing-2};
  --artdeco-spacing-4: #{$artdeco-spacing-4};
  --artdeco-spacing-8: #{$artdeco-spacing-8};
  --artdeco-spacing-16: #{$artdeco-spacing-16};

  --artdeco-font-display: #{$artdeco-font-display};
  --artdeco-font-body: #{$artdeco-font-body};
  --artdeco-font-mono: #{$artdeco-font-mono};

  --artdeco-bg-primary: #{$artdeco-bg-primary};
  --artdeco-accent-gold: #{$artdeco-accent-gold};
  --artdeco-data-rise: #{$artdeco-data-rise};
  --artdeco-data-fall: #{$artdeco-data-fall};
}
```

---

## ✅ 验证清单

应用优化代码后，请验证:

- [ ] TypeScript 编译无错误
- [ ] ESLint 检查通过
- [ ] 布局在不同屏幕尺寸下正常 (1920, 1440, 1080, 768, 375px)
- [ ] 网格切换响应式正确
- [ ] 卡片间距一致
- [ ] 页面居中对齐
- [ ] 无横向滚动条

---

## 🚀 快速实施步骤

1. **备份当前代码**
   ```bash
   cd web/frontend/src/views/artdeco
   mkdir -p .backup
   cp *.vue .backup/
   ```

2. **增强 Token 系统**
   ```bash
   # 复制上面提供的 token 增强代码到 artdeco-tokens.scss
   ```

3. **逐页替换样式**
   - 打开页面文件
   - 定位 `<style scoped>` 区块
   - 完全替换为对应优化代码

4. **验证**
   ```bash
   cd web/frontend
   npm run lint
   npm run build
   ```

5. **提交**
   ```bash
   git add .
   git commit -m "feat: 优化ArtDeco页面布局一致性

   - 标准化间距系统 (128px/32px/16px)
   - 添加容器宽度限制和居中对齐
   - 统一网格间隙为32px
   - 改进响应式断点逻辑
   - 符合ArtDeco设计系统规范
   "
   ```

---

**文档版本**: v1.0
**最后更新**: 2026-01-04
**配套文档**: `ARTDECO_LAYOUT_OPTIMIZATION_ANALYSIS.md`
