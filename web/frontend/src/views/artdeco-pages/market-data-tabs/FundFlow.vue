<template>
  <div class="fund-flow-panel">
    <h3 class="panel-title">资金流向分析</h3>
    
    <div class="fund-overview">
      <ArtDecoStatCard
        label="沪股通净流入"
        :value="fundData.shanghai.amount"
        :change="fundData.shanghai.change"
        change-percent
        variant="gold"
      />
      <ArtDecoStatCard
        label="深股通净流入"
        :value="fundData.shenzhen.amount"
        :change="fundData.shenzhen.change"
        change-percent
        variant="gold"
      />
      <ArtDecoStatCard
        label="北向资金总额"
        :value="fundData.north.amount"
        :change="fundData.north.change"
        change-percent
        :variant="fundData.north.change > 0 ? 'rise' : 'fall'"
      />
      <ArtDecoStatCard
        label="主力净流入"
        :value="fundData.main.amount"
        :change="fundData.main.change"
        change-percent
        variant="gold"
      />
    </div>

    <ArtDecoCard title="近30日资金流向趋势" hoverable>
      <div class="chart-placeholder">
        <div class="chart-title">资金流向趋势图</div>
        <div class="chart-area">
          <svg width="100%" height="200" viewBox="0 0 800 200" preserveAspectRatio="none">
            <defs>
              <linearGradient id="fundPositive" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color: var(--artdeco-up); stop-opacity: 60%" />
              </linearGradient>
              <linearGradient id="fundNegative" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="100%" style="stop-color: var(--artdeco-down); stop-opacity: 60%" />
              </linearGradient>
              <rect x="20" y="60" width="25" height="80" fill="url(#fundPositive)" stroke="var(--artdeco-up)" stroke-width="1" />
              <rect x="55" y="40" width="25" height="80" fill="url(#fundPositive)" stroke="var(--artdeco-up)" stroke-width="1" />
              <rect x="90" y="20" width="25" height="80" fill="url(#fundPositive)" stroke="var(--artdeco-up)" stroke-width="1" />
              <rect x="125" y="80" width="25" height="20" fill="url(#fundPositive)" stroke="var(--artdeco-up)" stroke-width="1" />
              <rect x="160" y="60" width="25" height="40" fill="url(#fundPositive)" stroke="var(--artdeco-up)" stroke-width="1" />
              <rect x="195" y="40" width="25" height="60" fill="url(#fundPositive)" stroke="var(--artdeco-up)" stroke-width="1" />
              <rect x="230" y="20" width="25" height="20" fill="url(#fundPositive)" stroke="var(--artdeco-up)" stroke-width="1" />
            </defs>
            </svg>
        </div>
      </div>
    </ArtDecoCard>

    <ArtDecoCard title="个股资金流向排行" hoverable>
      <div class="ranking-controls">
        <div class="time-filters">
          <button
            v-for="(filter, _idx) in timeFilters"
            :key="filter.key"
            class="filter-btn"
            :class="{ active: activeTimeFilter === filter.key }"
            @click="activeTimeFilter = filter.key"
          >
            {{ filter.label }}
          </button>
        </div>
        
        <ArtDecoSelect
          v-model="rankingType"
          :options="rankingOptions"
          placeholder="选择排序方式"
          class="ranking-select"
        />
      </div>

      <div class="ranking-table">
        <div class="table-header">
          <div class="col-rank">排名</div>
          <div class="col-stock">股票信息</div>
          <div class="col-price">最新价</div>
          <div class="col-change">涨跌幅</div>
          <div class="col-flow">资金流入</div>
          <div class="col-main">主力净额</div>
        </div>
        
        <div class="table-body">
          <div class="table-row" v-for="(stock, index) in stockRanking" :key="stock.code">
            <div class="col-rank">{{ index + 1 }}</div>
            <div class="col-stock">
              <div class="stock-name">{{ stock.name }}</div>
              <div class="stock-code">{{ stock.code }}</div>
            </div>
            <div class="col-price">¥{{ stock.price }}</div>
            <div class="col-change" :class="stock.change >= 0 ? 'rise' : 'fall'">
              {{ stock.change >= 0 ? '+' : '' }}{{ stock.change }}%
            </div>
            <div class="col-flow rise">+{{ stock.inflow }}亿</div>
            <div class="col-main rise">+{{ stock.mainForce }}亿</div>
          </div>
        </div>
      </div>
    </ArtDecoCard>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  stockCode: {
    type: String,
    required: false
  }
})

const activeTimeFilter = ref('today')
const rankingType = ref('by-inflow')

const timeFilters = [
  { key: 'today', label: '今日' },
  { key: 'yesterday', label: '昨日' },
  { key: 'week', label: '本周' },
  { key: 'month', label: '本月' }
]

const rankingOptions = [
  { key: 'by-inflow', label: '按资金流入' },
  { key: 'by-change', label: '按涨跌幅' },
  { key: 'by-market-cap', label: '按市值' }
]

const fundData = ref({
  shanghai: { amount: '28.6亿', change: 5.2 },
  shenzhen: { amount: '30.2亿', change: 8.9 },
  north: { amount: '58.8亿', change: 15.6 },
  main: { amount: '126.5亿', change: 68.0 }
})

const stockRanking = ref([
  { code: '600519', name: '贵州茅台', price: '1850.00', change: 2.1, inflow: '12.5', mainForce: '8.9' },
  { code: '300750', name: '宁德时代', price: '245.60', change: 3.5, inflow: '8.9', mainForce: '6.7' },
  { code: '600028', name: '中国石化', price: '4.85', change: -1.8, inflow: '-5.2', mainForce: '-3.1' },
  { code: '000002', name: '万科A', price: '18.90', change: -0.9, inflow: '-3.1', mainForce: '-2.2' },
  { code: '600036', name: '招商银行', price: '38.45', change: 1.2, inflow: '6.7', mainForce: '4.5' }
])

const loadFundFlowData = async () => {
  try {
    const response = await fetch(`/api/fund-flow/${props.stockCode}`)
    fundData.value = response.data
  } catch (error) {
    console.error('Failed to load fund flow data:', error)
  }
}

onMounted(() => {
  loadFundFlowData()
})
</script>

<style scoped>
.fund-flow-panel {
  padding: var(--artdeco-spacing-5);
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--artdeco-gold-primary) 8%, var(--artdeco-bg-primary)) 0%,
    color-mix(in srgb, var(--artdeco-fg-primary) 6%, var(--artdeco-bg-primary)) 100%
  );
}

.panel-title {
  font-size: var(--artdeco-text-xl);
  font-weight: 600;
  color: var(--artdeco-gold-primary);
  margin-bottom: var(--artdeco-spacing-5);
  text-align: center;
}

.fund-overview {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-8);
}

.chart-card {
  grid-column: span 2;
  background: color-mix(in srgb, var(--artdeco-fg-primary) 5%, transparent);
  border-radius: var(--artdeco-radius-lg);
  padding: var(--artdeco-spacing-5);
}

.chart-placeholder {
  height: var(--artdeco-spacing-20);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.chart-title {
  font-size: var(--artdeco-text-base);
  color: var(--artdeco-gold-primary);
  margin-bottom: var(--artdeco-spacing-2);
}

.chart-area {
  flex: 1;
  background: color-mix(in srgb, var(--artdeco-fg-primary) 2%, transparent);
  border-radius: var(--artdeco-radius-md);
  padding: var(--artdeco-spacing-4);
  overflow: hidden;
}

.ranking-card {
  grid-column: span 2;
  background: color-mix(in srgb, var(--artdeco-fg-primary) 5%, transparent);
  border-radius: var(--artdeco-radius-lg);
  padding: var(--artdeco-spacing-5);
}

.ranking-controls {
  display: flex;
  gap: var(--artdeco-spacing-3);
  margin-bottom: var(--artdeco-spacing-5);
}

.time-filters {
  display: flex;
  gap: var(--artdeco-spacing-2);
}

.filter-btn {
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
  background: color-mix(in srgb, var(--artdeco-fg-primary) 10%, transparent);
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-spacing-2);
  color: var(--artdeco-gold-primary);
  cursor: pointer;
  transition: all var(--artdeco-transition-quick);
}

.filter-btn:hover {
  background: var(--artdeco-gold-primary);
  color: var(--artdeco-bg-primary);
  transform: translateY(calc(var(--artdeco-spacing-px) * -2));
}

.filter-btn.active {
  background: var(--artdeco-gold-primary);
  color: var(--artdeco-bg-primary);
}

.ranking-select {
  width: calc(var(--artdeco-spacing-20) * 2.5);
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
  background: color-mix(in srgb, var(--artdeco-fg-primary) 5%, transparent);
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-spacing-2);
  color: var(--artdeco-gold-primary);
}

.ranking-table {
  background: color-mix(in srgb, var(--artdeco-fg-primary) 2%, transparent);
  border-radius: var(--artdeco-spacing-2);
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  padding: var(--artdeco-spacing-3);
  background: var(--artdeco-gold-opacity-10);
  font-weight: 600;
  color: var(--artdeco-gold-primary);
  border-radius: var(--artdeco-spacing-2) var(--artdeco-spacing-2) var(--artdeco-spacing-2) 0 0;
}

.table-body {
  max-height: calc(var(--artdeco-spacing-20) * 5);
  overflow-y: auto;
}

.table-row {
  display: contents;
  padding: var(--artdeco-spacing-3);
  border-bottom: 1px solid var(--artdeco-gold-opacity-10);
}

.table-row:hover {
  background: var(--artdeco-gold-opacity-05);
}

.col-rank {
  text-align: center;
  font-weight: 600;
}

.col-stock {
  text-align: left;
}

.stock-name {
  font-weight: 600;
  color: var(--artdeco-gold-primary);
  margin-bottom: var(--artdeco-spacing-1);
}

.stock-code {
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
}

.col-price {
  text-align: right;
  font-weight: 600;
  color: var(--artdeco-gold-primary);
}

.col-change {
  text-align: center;
  font-weight: 600;
}

.col-change.rise {
  color: var(--artdeco-up);
}

.col-change.fall {
  color: var(--artdeco-down);
}

.col-flow {
  text-align: center;
  font-weight: 600;
}

.col-flow.rise {
  color: var(--artdeco-up);
}

.col-main {
  text-align: center;
  font-weight: 600;
}
</style>
