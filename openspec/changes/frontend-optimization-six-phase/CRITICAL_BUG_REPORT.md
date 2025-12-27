# CRITICAL BUG: A股 Color Convention Error

**Severity**: 🔴 **CRITICAL** - Must fix before approval
**Found**: 2025-12-26
**Status**: ❌ NOT FIXED

---

## The Bug

The proposal defines A股 colors **BACKWARDS**:

### Proposal (WRONG):
```scss
// design.md line 120-122
--color-up: #00E676;          // ❌ WRONG! Green = UP
--color-down: #FF5252;        // ❌ WRONG! Red = DOWN
```

### Correct A股 Convention:
```scss
// ✅ CORRECT
--color-up: #FF5252;          // RED = 涨 (UP)
--color-down: #00E676;        // GREEN = 跌 (DOWN)
```

---

## Why This Matters

In **Chinese A-Share Market (中国A股)**:
- 🔴 **RED = 涨 (UP/GAIN)** - Price increase
- 🟢 **GREEN = 跌 (DOWN/LOSS)** - Price decrease

**This is OPPOSITE to international markets!**

Every Chinese trader expects:
- Red → 涨 (profit, good)
- Green → 跌 (loss, bad)

If you use green=up, **every user will be confused**.

---

## Cultural Context

**China**:
- Red = good fortune, celebration, success (红色吉祥)
- Green = can mean infidelity, negative meanings
- "大红大紫" = very prosperous

**Trading Terminology**:
- "大涨" (big rise) → always RED
- "暴跌" (big crash) → always GREEN

---

## Impact

**User Impact**: 🔴 **CRITICAL**
- 100% of Chinese users will be confused
- Trading decisions could be delayed due to confusion
- Professional credibility lost

**Brand Impact**: 🔴 **CRITICAL**
- Shows lack of market understanding
- Amateurish impression
- Competitors will have advantage

---

## Files to Fix

### 1. openspec/changes/frontend-optimization-six-phase/design.md

**Lines 120-122** (WRONG):
```scss
// A股 Market Colors (Green=Up, Red=Down)  ❌
--color-up: #00E676;          // Up - bright green
--color-down: #FF5252;        // Down - bright red
```

**Change to** (CORRECT):
```scss
// A股 Market Colors (RED=UP, GREEN=DOWN)  ✅
--color-up: #FF5252;          // Up - bright RED (涨)
--color-down: #00E676;        // Down - bright GREEN (跌)
```

### 2. openspec/changes/frontend-optimization-six-phase/proposal.md

Search for any color references and fix.

### 3. openspec/changes/frontend-optimization-six-phase/tasks.md

**Task T1.1** - Update color description.

### 4. All future implementation code

Use correct convention:
```vue
<!-- ✅ CORRECT A股 color usage -->
<template>
  <span :class="priceClass" class="price">{{ price }}</span>
  <span :class="changeClass" class="change">{{ changePercent }}%</span>
</template>

<script setup>
import { computed } from 'vue'

// ✅ RED=UP, GREEN=DOWN for A股
const priceClass = computed(() => {
  if (price > prevPrice) return 'market-up'    // RED for 涨
  if (price < prevPrice) return 'market-down'  // GREEN for 跌
  return 'market-flat'  // GRAY for 平
})
</script>

<style scoped>
.market-up { color: var(--color-market-up); }    /* RED */
.market-down { color: var(--color-market-down); }  /* GREEN */
.market-flat { color: var(--color-market-flat); }  /* GRAY */
</style>
```

---

## Quick Reference

| Context | Color | Hex | Meaning |
|---------|-------|-----|---------|
| **Price ↑ (上涨)** | 🔴 RED | `#FF5252` | 涨 (UP/GAIN) |
| **Price ↓ (下跌)** | 🟢 GREEN | `#00E676` | 跌 (DOWN/LOSS) |
| **Price → (平盘)** | ⚪ GRAY | `#B0B3B8` | 平 (FLAT) |
| **涨停 (Limit Up)** | 🔴🔴 RED | `#FF5252` | +10%/+20% |
| **跌停 (Limit Down)** | 🟢🟢 GREEN | `#00E676` | -10%/-20% |

---

## Semantic Colors (Separate!)

**IMPORTANT**: Keep UI state colors separate from market colors:

```scss
// Market colors (A股: RED=UP, GREEN=DOWN)
--color-market-up: #FF5252;      // 涨 (RED)
--color-market-down: #00E676;    // 跌 (GREEN)
--color-market-flat: #B0B3B8;    // 平 (GRAY)

// UI semantic colors (international standard)
--color-success: #00C853;        // Operation success
--color-danger: #FF1744;         // Operation error
--color-warning: #FFAB00;        // Warning
--color-info: #00B0FF;           // Information
```

**Usage**:
```vue
<!-- ✅ Use market colors for price changes -->
<span class="text-market-up">+10.25%</span>  <!-- RED for gain -->

<!-- ✅ Use semantic colors for UI states -->
<el-alert type="success">操作成功</el-alert>  <!-- GREEN for success -->
```

---

## Verification Checklist

After fixing, verify:

- [ ] design.md has correct colors
- [ ] proposal.md has correct colors
- [ ] tasks.md Task T1.1 has correct colors
- [ ] All color examples use RED=UP, GREEN=DOWN
- [ ] Semantic colors separated from market colors
- [ ] A股 terminology correct (涨跌停, T+1, etc.)
- [ ] Chinese comments use correct terms

---

## Resources

**See full technical review**: `TECHNICAL_IMPLEMENTATION_REVIEW.md`

**Key sections**:
- Section 1: Critical bug details
- Section 2: A股-specific requirements
- Section 3: Vue 3 + TypeScript examples
- Section 4: K-line chart implementation

---

## Approval Status

**Cannot approve until this bug is fixed!**

This is a **critical cultural and market convention error** that would make the application unusable for the target audience (Chinese A股 traders).

**Estimated time to fix**: 30 minutes

**Fix locations**:
1. design.md (lines 120-122)
2. proposal.md (color references)
3. tasks.md (Task T1.1)
4. All future code examples

---

**Found by**: Claude Code (Frontend Development Specialist)
**Date**: 2025-12-26
**Priority**: 🔴 CRITICAL - BLOCKS APPROVAL
