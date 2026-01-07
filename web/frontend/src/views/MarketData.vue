<template>
  <div class="market-data-view">
    <div class="page-header">
      <h1 class="page-title">市场数据</h1>
      <p class="page-subtitle">MARKET DATA | FUND FLOW | ETF | CHIP RACE | LONG HU BANG</p>
      <div class="decorative-line"></div>
    </div>

    <div class="card main-card">
      <div class="tabs-container">
        <button
          v-for="tab in tabs"
          :key="tab.name"
          class="tab-button"
          :class="{ active: activeTab === tab.name }"
          @click="activeTab = tab.name"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-primary)'" stroke-width="2">
            <path v-if="tab.name === 'fund-flow'" d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
            <polyline v-else-if="tab.name === 'etf'" points="22,12 18,12 15,21 9,3 6,12 2,12"></polyline>
            <path v-else-if="tab.name === 'chip-race'" d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            <path v-else d="M4 15s1-1 4-1 5 2 8 2 8-6 9-6-9s-4-9-4-9 5 2 8 2 8-6 9-6 9z"></path>
          </svg>
          <span>{{ tab.label }}</span>
        </button>
      </div>

      <div class="tab-content">
        <FundFlowPanel v-if="activeTab === 'fund-flow'" />
        <ETFDataPanel v-else-if="activeTab === 'etf'" />
        <ChipRacePanel v-else-if="activeTab === 'chip-race'" />
        <LongHuBangPanel v-else-if="activeTab === 'lhb'" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import FundFlowPanel from '@/components/market/FundFlowPanel.vue'
import ETFDataPanel from '@/components/market/ETFDataPanel.vue'
import ChipRacePanel from '@/components/market/ChipRacePanel.vue'
import LongHuBangPanel from '@/components/market/LongHuBangPanel.vue'

const activeTab = ref('fund-flow')

const tabs = [
  { name: 'fund-flow', label: '资金流向' },
  { name: 'etf', label: 'ETF行情' },
  { name: 'chip-race', label: '竞价抢筹' },
  { name: 'lhb', label: '龙虎榜' }
]
</script>

<style scoped lang="scss">

.market-data-view {
  padding: 20px;
  min-height: 100vh;
  background: var(--bg-primary);
  background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(212, 175, 55, 0.02) 10px, rgba(212, 175, 55, 0.02) 11px);
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 30px 0;
  position: relative;

  .page-title {
    font-family: var(--font-display);
    font-size: 32px;
    color: var(--gold-primary);
    text-transform: uppercase;
    letter-spacing: 4px;
    margin: 0 0 8px 0;
  }

  .page-subtitle {
    font-family: var(--font-body);
    font-size: 12px;
    color: var(--gold-muted);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin: 0;
  }

  .decorative-line {
    width: 200px;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--gold-primary), transparent);
    margin: 20px auto 0;

    &::before {
      content: '';
      position: absolute;
      bottom: -6px;
      left: 50%;
      transform: translateX(-50%);
      width: 60px;
      height: 1px;
      background: linear-gradient(90deg, transparent, var(--gold-muted), transparent);
    }
  }
}

.main-card {
  background: var(--bg-secondary);
  border: 1px solid var(--gold-dim);
  position: relative;
  border-radius: 0;

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: 16px;
    height: 16px;
    border: 2px solid var(--gold-primary);
  }

  &::before {
    top: 12px;
    left: 12px;
    border-right: none;
    border-bottom: none;
  }

  &::after {
    bottom: 12px;
    right: 12px;
    border-left: none;
    border-top: none;
  }
}

.tabs-container {
  display: flex;
  gap: 2px;
  border-bottom: 1px solid var(--gold-dim);
  padding: 0 20px;
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 15px 25px;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  color: var(--text-muted);
  font-family: var(--font-display);
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  top: 1px;

  &:hover {
    color: var(--gold-primary);
    background: rgba(212, 175, 55, 0.05);
  }

  &.active {
    color: var(--gold-primary);
    border-bottom-color: var(--gold-primary);
    background: rgba(212, 175, 55, 0.08);
  }
}

.tab-content {
  padding: 20px;
  min-height: 500px;
}

@media (max-width: 768px) {
  .market-data-view {
    padding: 10px;
  }

  .page-header {
    padding: 20px 0;

    .page-title {
      font-size: 24px;
      letter-spacing: 2px;
    }

    .page-subtitle {
      font-size: 10px;
      letter-spacing: 2px;
    }
  }

  .main-card {
    padding: 15px;
  }

  .tabs-container {
    padding: 0 10px;
    flex-wrap: wrap;

    .tab-button {
      padding: 12px 16px;
      font-size: 11px;
      letter-spacing: 0.5px;
      flex: 1;
      justify-content: center;
    }
  }

  .tab-content {
    padding: 15px;
    min-height: 400px;
  }
}
</style>
