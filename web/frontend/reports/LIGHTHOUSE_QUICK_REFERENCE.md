# Lighthouse Audit Quick Reference Guide

**For**: MyStocks Frontend Development Team
**Purpose**: Quick guide to run performance audits
**Last Updated**: 2025-12-26

---

## 5-Minute Quick Start

### Step 1: Start Dev Server
```bash
cd web/frontend
npm run dev
# Wait for: "Local: http://localhost:3000/"
```

### Step 2: Open Chrome DevTools
- Navigate to http://localhost:3000/dashboard
- Press `F12` (Windows/Linux) or `Cmd+Option+I` (Mac)
- Click **Lighthouse** tab

### Step 3: Run Audit
- Select: Performance ✓ | Accessibility ✓ | Best Practices ✓ | SEO ✓
- Device: Desktop
- Click **Analyze page load**
- Wait 30-60 seconds

### Step 4: Save Report
- Click **Save report** → Save HTML
- Click **Export JSON** → Save JSON

---

## Priority Pages to Audit

### Must Test (Critical)
1. `/dashboard` - Main entry point
2. `/market/list` - Data table view
3. `/market/realtime` - WebSocket updates
4. `/analysis` - Interactive charts

### Should Test (Important)
5. `/market-data/fund-flow`
6. `/market-data/longhubang`
7. `/settings`
8. `/risk-monitor/overview`

### Nice to Test
9. `/strategy-hub/management`
10. `/backtesting/new`

---

## Target Scores

| Metric | Target | Current (Estimated) |
|--------|--------|---------------------|
| Performance | 85+ | 60-70 |
| Accessibility | 90+ | 80-85 |
| Best Practices | 90+ | 75-80 |
| SEO | 80+ | 70-75 |

### Core Web Vitals

| Metric | Target | Good | Needs Fix |
|--------|--------|------|-----------|
| FCP | < 1.8s | < 1.8s | > 3.0s |
| LCP | < 2.5s | < 2.5s | > 4.0s |
| TBT | < 200ms | < 200ms | > 600ms |
| CLS | < 0.1 | < 0.1 | > 0.25 |

---

## Quick Fixes (Top 5)

### 1. ECharts Tree-Shaking (+15 pts)
```javascript
// Don't: import all ECharts
import * as echarts from 'echarts'

// Do: import only what you need
import { use } from 'echarts/core'
import { LineChart, BarChart } from 'echarts/charts'
import { GridComponent } from 'echarts/components'
use([LineChart, BarChart, GridComponent])
```

### 2. Skeleton Screens (+10 pts)
```vue
<template>
  <div v-if="loading">
    <SkeletonScreen />
  </div>
  <div v-else>
    <ActualContent />
  </div>
</template>
```

### 3. Image Optimization (+5 pts)
```vue
<img
  :src="imageSrc"
  width="800"
  height="600"
  loading="lazy"
  decoding="async"
/>
```

### 4. Request Caching (+8 pts)
```javascript
const cache = new Map()
async function fetchWithCache(url) {
  if (cache.has(url)) {
    return cache.get(url)
  }
  const data = await fetch(url).then(r => r.json())
  cache.set(url, data)
  return data
}
```

### 5. Lazy Loading Routes (+12 pts)
```javascript
// Already done! Check router config
const Dashboard = () => import('@/views/Dashboard.vue')
```

---

## Using CLI Scripts

### Run All Audits (Batch)
```bash
cd web/frontend
./scripts/run-lighthouse-audits.sh
```

### Run Single Page
```bash
npx lighthouse http://localhost:3000/dashboard \
  --output=html \
  --output=json \
  --output-path=./reports/dashboard.html \
  --only-categories=performance,accessibility,best-practices,seo
```

---

## CI/CD Integration

### GitHub Actions
Add to `.github/workflows/`:
```yaml
name: Lighthouse CI
on: [pull_request]
jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Lighthouse CI
        uses: treosh/lighthouse-ci-action@v9
        with:
          urls: |
            http://localhost:3000/dashboard
            http://localhost:3000/market/list
```

---

## Report Organization

```
web/frontend/reports/
├── lighthouse-dashboard-20251226.html
├── lighthouse-dashboard-20251226.json
├── lighthouse-market-list-20251226.html
├── lighthouse-summary-20251226.json
└── LIGHTHOUSE_AUDIT_REPORT.md (detailed analysis)
```

---

## Common Issues & Solutions

### Issue: "Unable to connect to Chrome"
**Solution**: Use Chrome DevTools instead of CLI

### Issue: Low Performance Score (< 60)
**Solution**: Check bundle size, enable code splitting, implement lazy loading

### Issue: Poor Accessibility (< 80)
**Solution**: Check color contrast, add ARIA labels, test with screen reader

### Issue: Layout Shift (CLS > 0.1)
**Solution**: Add image dimensions, use skeleton screens, reserve space for ads

---

## Next Steps

1. ✅ Run manual audits on all 9 priority pages
2. ✅ Document scores in summary table
3. ✅ Identify top 3 performance bottlenecks
4. ✅ Implement Phase 2 optimizations
5. ✅ Re-audit and measure improvements

**Expected Improvement**: +20-25 points (Performance 60 → 85+)

---

## Resources

- **Full Report**: `web/frontend/reports/LIGHTHOUSE_AUDIT_REPORT.md`
- **Lighthouse Docs**: https://github.com/GoogleChrome/lighthouse
- **Web Vitals**: https://web.dev/vitals/
- **Vue Performance**: https://vuejs.org/guide/best-practices/performance.html

---

**Questions?** Check the detailed report or ask in the development channel.
