# ArtDeco Phase 3 Migration Plan

**Date**: 2026-01-20
**Status**: Ready to Execute
**Estimated Time**: 1.5-2 hours
**Complexity**: Medium (33 components to move + import path updates)

---

## 📊 Current Structure

```
components/artdeco/
├── base/         (12 components) ✅ KEEP
├── specialized/  (30 components) ❌ REORGANIZE
├── advanced/     (10 components) ✅ KEEP
└── core/         (11 components) ✅ KEEP
```

## 🎯 Target Structure

```
components/artdeco/
├── base/          (12) - Atomic UI components
├── business/      (10) - Business logic components
├── charts/        (8)  - Chart/visualization components
├── trading/       (12) - Trading-specific components
├── advanced/      (10) - Advanced analysis components
└── core/          (11) - Core layout components
```

---

## 📋 Component Migration Map

### specialized/ → business/ (10 components)

**Business Logic & UI Components**:
1. ArtDecoAlertRule.vue → business/
2. ArtDecoBacktestConfig.vue → business/
3. ArtDecoButtonGroup.vue → business/
4. ArtDecoCodeEditor.vue → business/
5. ArtDecoDateRange.vue → business/
6. ArtDecoFilterBar.vue → business/
7. ArtDecoInfoCard.vue → business/
8. ArtDecoMechanicalSwitch.vue → business/
9. ArtDecoSlider.vue → business/
10. ArtDecoStatus.vue → business/

### specialized/ → charts/ (8 components)

**Chart & Visualization Components**:
1. CorrelationMatrix.vue → charts/
2. DepthChart.vue → charts/
3. DrawdownChart.vue → charts/
4. HeatmapCard.vue → charts/
5. PerformanceTable.vue → charts/
6. TimeSeriesChart.vue → charts/
7. ArtDecoKLineChartContainer.vue → charts/
8. ArtDecoRomanNumeral.vue → charts/

### specialized/ → trading/ (12 components)

**Trading-Specific Components**:
1. ArtDecoCollapsibleSidebar.vue → trading/
2. ArtDecoDynamicSidebar.vue → trading/
3. ArtDecoLoader.vue → trading/
4. ArtDecoOrderBook.vue → trading/
5. ArtDecoPositionCard.vue → trading/
6. ArtDecoRiskGauge.vue → trading/
7. ArtDecoSidebar.vue → trading/
8. ArtDecoStrategyCard.vue → trading/
9. ArtDecoTable.vue → trading/
10. ArtDecoTicker.vue → trading/
11. ArtDecoTickerList.vue → trading/
12. ArtDecoTopBar.vue → trading/
13. ArtDecoTradeForm.vue → trading/

---

## 🔧 Execution Steps

### Step 1: Create New Directory Structure
```bash
cd /opt/claude/mystocks_spec/web/frontend/src/components/artdeco
mkdir -p business charts trading
```

### Step 2: Move Components (git mv for history preservation)

**Business Components**:
```bash
git mv specialized/ArtDecoAlertRule.vue business/
git mv specialized/ArtDecoBacktestConfig.vue business/
git mv specialized/ArtDecoButtonGroup.vue business/
git mv specialized/ArtDecoCodeEditor.vue business/
git mv specialized/ArtDecoDateRange.vue business/
git mv specialized/ArtDecoFilterBar.vue business/
git mv specialized/ArtDecoInfoCard.vue business/
git mv specialized/ArtDecoMechanicalSwitch.vue business/
git mv specialized/ArtDecoSlider.vue business/
git mv specialized/ArtDecoStatus.vue business/
```

**Chart Components**:
```bash
git mv specialized/CorrelationMatrix.vue charts/
git mv specialized/DepthChart.vue charts/
git mv specialized/DrawdownChart.vue charts/
git mv specialized/HeatmapCard.vue charts/
git mv specialized/PerformanceTable.vue charts/
git mv specialized/TimeSeriesChart.vue charts/
git mv specialized/ArtDecoKLineChartContainer.vue charts/
git mv specialized/ArtDecoRomanNumeral.vue charts/
```

**Trading Components**:
```bash
git mv specialized/ArtDecoCollapsibleSidebar.vue trading/
git mv specialized/ArtDecoDynamicSidebar.vue trading/
git mv specialized/ArtDecoLoader.vue trading/
git mv specialized/ArtDecoOrderBook.vue trading/
git mv specialized/ArtDecoPositionCard.vue trading/
git mv specialized/ArtDecoRiskGauge.vue trading/
git mv specialized/ArtDecoSidebar.vue trading/
git mv specialized/ArtDecoStrategyCard.vue trading/
git mv specialized/ArtDecoTable.vue trading/
git mv specialized/ArtDecoTicker.vue trading/
git mv specialized/ArtDecoTickerList.vue trading/
git mv specialized/ArtDecoTopBar.vue trading/
git mv specialized/ArtDecoTradeForm.vue trading/
```

### Step 3: Create New Index Files

**business/index.ts**:
```typescript
export { default as ArtDecoAlertRule } from './ArtDecoAlertRule.vue'
export { default as ArtDecoBacktestConfig } from './ArtDecoBacktestConfig.vue'
export { default as ArtDecoButtonGroup } from './ArtDecoButtonGroup.vue'
export { default as ArtDecoCodeEditor } from './ArtDecoCodeEditor.vue'
export { default as ArtDecoDateRange } from './ArtDecoDateRange.vue'
export { default as ArtDecoFilterBar } from './ArtDecoFilterBar.vue'
export { default as ArtDecoInfoCard } from './ArtDecoInfoCard.vue'
export { default as ArtDecoMechanicalSwitch } from './ArtDecoMechanicalSwitch.vue'
export { default as ArtDecoSlider } from './ArtDecoSlider.vue'
export { default as ArtDecoStatus } from './ArtDecoStatus.vue'
```

**charts/index.ts**:
```typescript
export { default as CorrelationMatrix } from './CorrelationMatrix.vue'
export { default as DepthChart } from './DepthChart.vue'
export { default as DrawdownChart } from './DrawdownChart.vue'
export { default as HeatmapCard } from './HeatmapCard.vue'
export { default as PerformanceTable } from './PerformanceTable.vue'
export { default as TimeSeriesChart } from './TimeSeriesChart.vue'
export { default as ArtDecoKLineChartContainer } from './ArtDecoKLineChartContainer.vue'
export { default as ArtDecoRomanNumeral } from './ArtDecoRomanNumeral.vue'
```

**trading/index.ts**:
```typescript
export { default as ArtDecoCollapsibleSidebar } from './ArtDecoCollapsibleSidebar.vue'
export { default as ArtDecoDynamicSidebar } from './ArtDecoDynamicSidebar.vue'
export { default as ArtDecoLoader } from './ArtDecoLoader.vue'
export { default as ArtDecoOrderBook } from './ArtDecoOrderBook.vue'
export { default as ArtDecoPositionCard } from './ArtDecoPositionCard.vue'
export { default as ArtDecoRiskGauge } from './ArtDecoRiskGauge.vue'
export { default as ArtDecoSidebar } from './ArtDecoSidebar.vue'
export { default as ArtDecoStrategyCard } from './ArtDecoStrategyCard.vue'
export { default as ArtDecoTable } from './ArtDecoTable.vue'
export { default as ArtDecoTicker } from './ArtDecoTicker.vue'
export { default as ArtDecoTickerList } from './ArtDecoTickerList.vue'
export { default as ArtDecoTopBar } from './ArtDecoTopBar.vue'
export { default as ArtDecoTradeForm } from './ArtDecoTradeForm.vue'
```

### Step 4: Update Main index.ts

```typescript
// ============================================
//   ARTDECO COMPONENT LIBRARY
//   ArtDeco 组件库主入口
// ============================================

// 基础UI组件
export * from './base'

// 核心分析组件
export * from './core'

// 高级分析组件
export * from './advanced'

// 业务组件 (NEW)
export * from './business'

// 图表组件 (NEW)
export * from './charts'

// 交易组件 (NEW)
export * from './trading'

// 专用功能组件 (DEPRECATED - use specific categories above)
// export * from './specialized' // REMOVE AFTER MIGRATION

// ... rest of file
```

### Step 5: Update Import Paths Across Codebase

**Files to Update** (search for `artdeco/specialized`):
```bash
cd /opt/claude/mystocks_spec/web/frontend
grep -r "artdeco/specialized" --include="*.vue" --include="*.ts" --include="*.js" src/
```

**Replacement Rules**:
- `from './specialized/XXX'` → Determine new location based on component
- `from '@/components/artdeco/specialized/XXX'` → Update to new category

---

## ⚠️ Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Import path errors | Medium | High | Automated find/replace + testing |
| Broken imports in views | Medium | High | Update all import paths systematically |
| TypeScript errors | Low | Medium | Type checking will catch issues |
| Git history loss | Low | Medium | Use `git mv` not `mv` |

---

## ✅ Validation Checklist

After migration:

- [ ] All components moved to new directories
- [ ] Old `specialized/` directory removed (if empty)
- [ ] New index.ts files created (business, charts, trading)
- [ ] Main index.ts updated
- [ ] All import paths updated across codebase
- [ ] No TypeScript errors
- [ ] No ESLint errors
- [ ] Components still importable from `@/components/artdeco`
- [ ] Test suite passes (if exists)

---

## 📊 Expected Results

**Before**:
- specialized/: 30 components (mixed responsibilities)
- Directory flatness: Low (all in one folder)

**After**:
- business/: 10 components (focused)
- charts/: 8 components (focused)
- trading/: 12 components (focused)
- Directory organization: High (3 logical categories)
- Developer experience: Improved (easier to find components)

---

## 🔄 Rollback Plan

If issues arise:

```bash
# Roll back component moves
git checkout HEAD -- components/artdeco/

# Or manually move back
cd components/artdeco
git mv business/* specialized/
git mv charts/* specialized/
git mv trading/* specialized/
rmdir business charts trading
```

---

**Generated**: 2026-01-20
**Author**: Claude Code
**Status**: Ready for execution
