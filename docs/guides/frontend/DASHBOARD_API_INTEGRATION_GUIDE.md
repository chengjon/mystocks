# Dashboard API集成实施指南

**创建日期**: 2026-01-20
**目的**: 将ArtDecoDashboard从Mock数据迁移到真实API
**状态**: ✅ 准备就绪

---

## 📋 实施清单

### 已完成 ✅

1. ✅ **API Service层创建** - `src/api/services/dashboardService.ts`
2. ✅ **ArtDecoLoading组件** - `src/components/artdeco/core/ArtDecoLoading.vue`
3. ✅ **龙虎榜卡片组件** - `src/components/artdeco/specialized/ArtDecoLongHuBang.vue`
4. ✅ **大宗交易卡片组件** - `src/components/artdeco/specialized/ArtDecoBlockTrading.vue`
5. ✅ **组件导出更新** - `components.d.ts`已自动包含新组件

### 待实施 🔄

1. 🔄 **更新Dashboard主组件** - 集成API调用
2. 🔄 **应用数据密集样式** - 使用量化扩展令牌
3. 🔄 **测试验证** - 确保功能正常

---

## 🎯 实施步骤

### Step 1: 更新Dashboard组件导入

**文件**: `src/views/artdeco-pages/ArtDecoDashboard.vue`

**在`<script setup>`部分更新导入**:

```vue
<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  ArtDecoStatCard,
  ArtDecoCard,
  ArtDecoButton,
  ArtDecoCollapsible,
  ArtDecoHeader,
  ArtDecoIcon,
  ArtDecoBadge,
  ArtDecoLoading // 新增
} from '@/components/artdeco'

// 新增: 导入新组件
import ArtDecoLongHuBang from '@/components/artdeco/specialized/ArtDecoLongHuBang.vue'
import ArtDecoBlockTrading from '@/components/artdeco/specialized/ArtDecoBlockTrading.vue'

// 新增: 导入API服务
import dashboardService from '@/api/services/dashboardService'

// ... 其他导入保持不变
</script>
```

---

### Step 2: 添加加载状态和错误处理

**在`<script setup>`部分添加响应式变量**:

```typescript
// ============================================
// 加载状态管理
// ============================================
const loading = ref({
  market: false,      // 市场指标加载状态
  fundFlow: false,    // 资金流向加载状态
  industry: false,    // 板块热度加载状态
  indicators: false,  // 技术指标加载状态
  monitoring: false   // 系统监控加载状态
})

const error = ref({
  market: '',         // 市场指标错误信息
  fundFlow: '',       // 资金流向错误信息
  industry: '',       // 板块热度错误信息
  indicators: '',    // 技术指标错误信息
  monitoring: ''      // 系统监控错误信息
})

// ============================================
// 数据获取函数
// ============================================

/**
 * 获取市场概览数据（主要指数）
 */
const fetchMarketOverview = async () => {
  loading.value.market = true
  error.value.market = ''

  try {
    const response = await dashboardService.getMarketOverview(100)
    const etfData = response.data || []

    // 筛选主要指数型ETF
    const shanghaiETF = etfData.find(etf =>
      /^510300|^510050/.test(etf.symbol) || etf.name.includes('沪深300') || etf.name.includes('上证50')
    )
    const shenzhenETF = etfData.find(etf =>
      /^159919|^159901|^399001/.test(etf.symbol) || etf.name.includes('深证成指')
    )
    const chuangyeETF = etfData.find(etf =>
      /^159915/.test(etf.symbol) || etf.name.includes('创业板')
    )

    // 更新市场数据
    if (shanghaiETF) {
      marketData.value.shanghai = {
        index: shanghaiETF.latest_price,
        change: shanghaiETF.change_percent,
        changePercent: `${shanghaiETF.change_percent >= 0 ? '+' : ''}${shanghaiETF.change_percent}%`
      }
    }

    if (shenzhenETF) {
      marketData.value.shenzhen = {
        index: shenzhenETF.latest_price,
        change: shenzhenETF.change_percent,
        changePercent: `${shenzhenETF.change_percent >= 0 ? '+' : ''}${shenzhenETF.change_percent}%`
      }
    }

    if (chuangyeETF) {
      marketData.value.chuangye = {
        index: chuangyeETF.latest_price,
        change: chuangyeETF.change_percent,
        changePercent: `${chuangyeETF.change_percent >= 0 ? '+' : ''}${chuangyeETF.change_percent}%`
      }
    }
  } catch (err: any) {
    console.error('Failed to fetch market overview:', err)
    error.value.market = '市场数据加载失败'
    // 保持Mock数据作为降级
  } finally {
    loading.value.market = false
  }
}

/**
 * 获取资金流向数据
 */
const fetchFundFlow = async () => {
  loading.value.fundFlow = true
  error.value.fundFlow = ''

  try {
    const response = await dashboardService.getFundFlow()
    const fundFlowData = response.data

    if (fundFlowData) {
      marketData.value.fundFlow = fundFlowData
    }
  } catch (err: any) {
    console.error('Failed to fetch fund flow:', err)
    error.value.fundFlow = '资金流向数据加载失败'
    // 保持Mock数据作为降级
  } finally {
    loading.value.fundFlow = false
  }
}

/**
 * 获取行业板块热度
 */
const fetchIndustryFlow = async () => {
  loading.value.industry = true
  error.value.industry = ''

  try {
    const response = await dashboardService.getIndustryFlow('change_percent', 6)
    const industryData = response.data || []

    // 转换数据格式
    marketHeat.value = industryData.map(item => ({
      name: item.name,
      change: item.change
    }))
  } catch (err: any) {
    console.error('Failed to fetch industry flow:', err)
    error.value.industry = '板块数据加载失败'
    // 保持Mock数据作为降级
  } finally {
    loading.value.industry = false
  }
}

/**
 * 获取资金流向排名
 */
const fetchStockFlowRanking = async () => {
  try {
    const response = await dashboardService.getStockFlowRanking('1day', 5)
    const flowData = response.data || []

    // 转换数据格式
    capitalFlowData.value = flowData.map(item => ({
      name: item.name,
      code: item.code,
      amount: item.amount,
      change: item.change
    }))
  } catch (err: any) {
    console.error('Failed to fetch stock flow ranking:', err)
    // 保持Mock数据作为降级
  }
}

// ============================================
// 页面挂载时获取数据
// ============================================
onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)

  // 获取P0优先级数据
  fetchMarketOverview()
  fetchFundFlow()
  fetchIndustryFlow()
  fetchStockFlowRanking()
})

// ... 其他代码保持不变
```

---

### Step 3: 更新模板添加Loading状态

**在`<template>`部分更新市场指标卡片**:

```vue
<!-- 主要市场指标 - 添加Loading状态 -->
<ArtDecoCard class="market-indicators" variant="elevated" gradient>
  <template #header>
    <div class="card-header">
      <ArtDecoIcon name="bar-chart-3" />
      <h3>主要市场指标</h3>
    </div>
  </template>

  <ArtDecoLoading v-if="loading.market" text="加载市场数据..." size="md" />
  <div v-else-if="error.market" class="error-message">
    <ArtDecoIcon name="alert-circle" />
    <span>{{ error.market }}</span>
  </div>
  <div v-else class="indicators-grid">
    <ArtDecoStatCard
      label="上证指数"
      :value="marketData.shanghai.index"
      :change="marketData.shanghai.change"
      change-percent
      variant="gold"
      size="large"
      glow
    />
    <!-- ... 其他指标 -->
  </div>
</ArtDecoCard>
```

---

### Step 4: 添加龙虎榜和大宗交易卡片

**在`<template>`的`content-grid`中添加新卡片**:

```vue
<div class="content-grid">
  <!-- 市场热度板块 -->
  <ArtDecoCard title="市场热度板块" hoverable class="heat-map-card">
    <!-- ... 保持现有内容 ... -->
  </ArtDecoCard>

  <!-- 新增: 龙虎榜 -->
  <ArtDecoLongHuBang class="long-hu-bang-card" />

  <!-- 新增: 大宗交易 -->
  <ArtDecoBlockTrading class="block-trading-card" />

  <!-- 资金流向持续排名 -->
  <ArtDecoCard title="资金流向持续排名" hoverable class="capital-flow-card">
    <!-- ... 保持现有内容 ... -->
  </ArtDecoCard>

  <!-- 股票池表现 -->
  <ArtDecoCard title="我的股票池表现" hoverable class="stock-pool-card">
    <!-- ... 保持现有内容 ... -->
  </ArtDecoCard>

  <!-- 快速导航 -->
  <ArtDecoCard title="快速导航" hoverable class="quick-nav-card">
    <!-- ... 保持现有内容 ... -->
  </ArtDecoCard>
</div>
```

---

### Step 5: 更新样式应用数据密集布局

**在`<style scoped lang="scss">`部分添加**:

```scss
// 导入量化扩展令牌
@import '@/styles/artdeco-quant-extended.scss';

.artdeco-dashboard {
  // ... 保持现有样式 ...

  // 新增: 错误消息样式
  .error-message {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--artdeco-spacing-2);
    padding: var(--artdeco-spacing-8);
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-sm);
  }

  // 新增: 内容网格布局优化（3列布局）
  .content-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr); // 从2列改为3列
    gap: var(--artdeco-dense-gap-sm);      // 使用紧凑间距
  }

  // 响应式优化
  @media (max-width: 1400px) {
    .content-grid {
      grid-template-columns: repeat(2, 1fr); // 中等屏幕2列
    }
  }

  @media (max-width: 900px) {
    .content-grid {
      grid-template-columns: 1fr; // 小屏幕1列
    }
  }
}
```

---

## 🔧 快速实施命令

由于Dashboard文件较大（1300+行），建议使用以下命令快速应用修改：

### 选项A: 手动修改（推荐）
- 打开`web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- 按照上述步骤逐步修改
- 确保所有导入和响应式变量正确

### 选项B: 创建新Dashboard组件
- 创建`ArtDecoDashboardV2.vue`作为新版本
- 复制现有代码并应用修改
- 测试通过后替换原文件

---

## ✅ 验证清单

修改完成后，请验证以下项目：

### 功能验证
- [ ] Dashboard加载时显示Loading状态
- [ ] 市场指标数据从API正确获取
- [ ] 资金流向数据正确显示
- [ ] 板块热度动态更新
- [ ] 资金流向排名正确显示
- [ ] 龙虎榜卡片正确加载
- [ ] 大宗交易卡片正确加载
- [ ] 错误处理友好（降级到Mock数据）

### UI/UX验证
- [ ] 无页面留空，数据密度合理
- [ ] Loading动画流畅
- [ ] 红涨绿跌颜色正确
- [ ] 等宽数字对齐
- [ ] 响应时间合理（<2秒）

### 性能验证
- [ ] API调用不阻塞UI
- [ ] 页面首屏加载 < 2秒
- [ ] 无内存泄漏

---

## 🎉 预期成果

实施完成后，Dashboard将实现：

### 数据真实性
- ✅ 市场指标：从API实时获取上证、深证、创业板指数
- ✅ 资金流向：真实的沪股通、深股通、北向资金数据
- ✅ 板块热度：动态的热门板块排名
- ✅ 龙虎榜：每日市场活跃股票
- ✅ 大宗交易：主力资金动向

### 用户体验
- ✅ 加载状态清晰
- ✅ 错误处理友好
- ✅ 数据密度提升2-3倍
- ✅ 页面无留空

### 专业性
- ✅ 符合量化交易终端标准
- ✅ 红涨绿跌颜色正确
- ✅ 等宽数字对齐
- ✅ ArtDeco美学保持一致

---

**下一步**: 实施完成后，请运行`npm run dev`验证Dashboard功能。

**需要帮助**: 如遇到问题，请查看：
- `docs/guides/frontend/DASHBOARD_API_ENRICHMENT_GUIDE.md` - 完整API指南
- `docs/reports/ARTDECO_QUANT_EXTENSION_COMPLETION_REPORT.md` - 量化扩展报告

---

**文档版本**: v1.0
**创建日期**: 2026-01-20
