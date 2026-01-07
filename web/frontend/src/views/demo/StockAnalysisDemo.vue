<template>
  <div class="stock-analysis-demo">

    <div class="page-header">
      <h1 class="page-title">Stock-Analysis</h1>
      <p class="page-subtitle">STOCK ANALYSIS | QUANTITATIVE SCREENING | BACKTESTING</p>
      <div class="decorative-line"></div>
    </div>

    <div class="card main-card">
      <div class="tabs-container">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-button"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          <span class="tab-icon">{{ tab.icon }}</span>
          <span class="tab-label">{{ tab.label }}</span>
        </button>
      </div>

      <div class="tab-content">
        <component :is="currentComponent" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineAsyncComponent } from 'vue'
import { TABS } from './stock-analysis/config'

const Overview = defineAsyncComponent(() => import('./stock-analysis/components/Overview.vue'))
const DataParsing = defineAsyncComponent(() => import('./stock-analysis/components/DataParsing.vue'))
const Strategy = defineAsyncComponent(() => import('./stock-analysis/components/Strategy.vue'))
const Backtest = defineAsyncComponent(() => import('./stock-analysis/components/Backtest.vue'))
const Realtime = defineAsyncComponent(() => import('./stock-analysis/components/Realtime.vue'))
const Status = defineAsyncComponent(() => import('./stock-analysis/components/Status.vue'))

const activeTab = ref('overview')
const tabs = TABS

const componentMap: Record<string, any> = {
  overview: Overview,
  data: DataParsing,
  strategy: Strategy,
  backtest: Backtest,
  realtime: Realtime,
  status: Status
}

const currentComponent = computed(() => {
  return componentMap[activeTab.value] || Overview
})
</script>

<style scoped lang="scss">

.stock-analysis-demo {
  padding: 20px;
  min-height: 100vh;
  background: var(--bg-primary);
  background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(212, 175, 55, 0.02) 10px, rgba(212, 175, 55, 0.02) 11px);
}

  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.04;
  background-image:
    repeating-linear-gradient(45deg, var(--gold-primary) 0px, var(--gold-primary) 1px, transparent 1px, transparent 10px),
    repeating-linear-gradient(-45deg, var(--gold-primary) 0px, var(--gold-primary) 1px, transparent 1px, transparent 10px);
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
  padding: 20px;
  z-index: 1;

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
  gap: 4px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--gold-dim);
  flex-wrap: wrap;
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: transparent;
  border: 1px solid var(--gold-dim);
  color: var(--text-muted);
  font-family: var(--font-display);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
  cursor: pointer;
  border-radius: 0;
  transition: all 0.3s ease;

  .tab-icon {
    font-size: 14px;
  }

  &:hover {
    color: var(--gold-primary);
    border-color: var(--gold-primary);
    background: rgba(212, 175, 55, 0.05);
  }

  &.active {
    color: var(--bg-primary);
    background: var(--gold-primary);
    border-color: var(--gold-primary);
  }
}

.tab-content {
  position: relative;
  z-index: 1;
}

@media (max-width: 768px) {
  .stock-analysis-demo {
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
    flex-direction: column;

    .tab-button {
      width: 100%;
      justify-content: center;
    }
  }
}
</style>
