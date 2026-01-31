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
                <stop offset="0%" style="stop-color: #e74c3c; stop-opacity: 0.6" />
              </linearGradient>
              <linearGradient id="fundNegative" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="100%" style="stop-color: #27ae60; stop-opacity: 0.6" />
              </linearGradient>
              <rect x="20" y="60" width="25" height="80" fill="url(#fundPositive)" stroke="#E74C3C" stroke-width="1" />
              <rect x="55" y="40" width="25" height="80" fill="url(#fundPositive)" stroke="#E74C3C" stroke-width="1" />
              <rect x="90" y="20" width="25" height="80" fill="url(#fundPositive)" stroke="#E74C3C" stroke-width="1" />
              <rect x="125" y="80" width="25" height="20" fill="url(#fundPositive)" stroke="#E74C3C" stroke-width="1" />
              <rect x="160" y="60" width="25" height="40" fill="url(#fundPositive)" stroke="#E74C3C" stroke-width="1" />
              <rect x="195" y="40" width="25" height="60" fill="url(#fundPositive)" stroke="#E74C3C" stroke-width="1" />
              <rect x="230" y="20" width="25" height="20" fill="url(#fundPositive)" stroke="#E74C3C" stroke-width="1" />
            </svg>
        </div>
      </div>
    </ArtDecoCard>

    <ArtDecoCard title="个股资金流向排行" hoverable>
      <div class="ranking-controls">
        <div class="time-filters">
          <button
            v-for="filter in timeFilters"
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
import { ref, computed, onMounted } from 'vue'

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
  padding: 20px;
  background: linear-gradient(135deg, #f0f4e6 0%, #e9e8f8 100%);
}

.panel-title {
  font-size: 24px;
  font-weight: 600;
  color: #e74c3c;
  margin-bottom: 20px;
  text-align: center;
}

.fund-overview {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 30px;
}

.chart-card {
  grid-column: span 2;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
}

.chart-placeholder {
  height: 250px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.chart-title {
  font-size: 16px;
  color: #e74c3c;
  margin-bottom: 10px;
}

.chart-area {
  flex: 1;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  padding: 15px;
  overflow: hidden;
}

.ranking-card {
  grid-column: span 2;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
}

.ranking-controls {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.time-filters {
  display: flex;
  gap: 8px;
}

.filter-btn {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #e74c3c;
  cursor: pointer;
  transition: all 0.3s;
}

.filter-btn:hover {
  background: rgba(231, 76, 60, 1);
  transform: translateY(-2px);
}

.filter-btn.active {
  background: #e74c3c;
  color: #fff;
}

.ranking-select {
  width: 200px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #e74c3c;
}

.ranking-table {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr 1fr 1fr 1fr;
  padding: 12px;
  background: rgba(231, 76, 60, 0.1);
  font-weight: 600;
  color: #e74c3c;
  border-radius: 8px 8px 8px 0 0;
}

.table-body {
  max-height: 400px;
  overflow-y: auto;
}

.table-row {
  display: contents;
  padding: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.table-row:hover {
  background: rgba(231, 76, 60, 0.05);
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
  color: #e74c3c;
  margin-bottom: 4px;
}

.stock-code {
  font-size: 12px;
  color: rgba(231, 76, 60, 0.7);
}

.col-price {
  text-align: right;
  font-weight: 600;
  color: #e74c3c;
}

.col-change {
  text-align: center;
  font-weight: 600;
}

.col-change.rise {
  color: #e74c3c;
}

.col-change.fall {
  color: #27ae60;
}

.col-flow {
  text-align: center;
  font-weight: 600;
}

.col-flow.rise {
  color: #e74c3c;
}

.col-main {
  text-align: center;
  font-weight: 600;
}
</style>
