<template>
  <div class="market-data-view">

    <div class="card header-card">
      <div class="header-content">
        <button class="back-button" @click="goBack">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-primary)'" stroke-width="2">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12,19 5,12 12,5"></polyline>
          </svg>
        </button>

        <div class="header-title-section">
          <div class="header-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-primary)'" stroke-width="2">
              <path d="M3 3v18h18"></path>
              <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"></path>
            </svg>
          </div>
          <h1 class="header-title">市场数据</h1>
        </div>

        <div class="header-info">
          <span class="status-badge live">实时数据</span>
          <span class="time-display">{{ currentTime }}</span>
        </div>
      </div>
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
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" :stroke="'currentColor'" stroke-width="2">
            <path v-if="tab.name === 'fund-flow'" d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
            <polyline v-else-if="tab.name === 'etf-data'" points="22,12 18,12 15,21 9,3 6,12 2,12"></polyline>
            <path v-else-if="tab.name === 'chip-race'" d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            <path v-else d="M4 15s1-1 4-1 5 2 8 2 8-6 9-6-9s-4-9-4-9 5 2 8 2 8-6 9-6 9z"></path>
          </svg>
          <span>{{ tab.label }}</span>
        </button>
      </div>

      <div class="tab-content">
        <FundFlowPanel v-if="activeTab === 'fund-flow'" />
        <ETFDataTable v-else-if="activeTab === 'etf-data'" />
        <ChipRaceTable v-else-if="activeTab === 'chip-race'" />
        <LongHuBangTable v-else-if="activeTab === 'longhubang'" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'

import FundFlowPanel from '@/components/market/FundFlowPanel.vue'
import ETFDataTable from '@/components/market/ETFDataTable.vue'
import ChipRaceTable from '@/components/market/ChipRaceTable.vue'
import LongHuBangTable from '@/components/market/LongHuBangTable.vue'

const router = useRouter()
const activeTab = ref('fund-flow')
const currentTime = ref('')

const goBack = () => {
  router.back()
}

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const tabs = [
  { name: 'fund-flow', label: '资金流向' },
  { name: 'etf-data', label: 'ETF行情' },
  { name: 'chip-race', label: '竞价抢筹' },
  { name: 'longhubang', label: '龙虎榜' }
]

let timeInterval = null

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
})

onBeforeUnmount(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped lang="scss">

.market-data-view {
  min-height: 100vh;
  padding: 20px;
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

.card {
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

.header-card {
  position: relative;
  z-index: 1;
  margin-bottom: 20px;
  padding: 20px 30px;

  .header-content {
    display: flex;
    align-items: center;
    gap: 20px;
  }

  .back-button {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(212, 175, 55, 0.1);
    border: 1px solid var(--gold-dim);
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      background: var(--gold-primary);

      svg {
        stroke: var(--bg-primary);
      }
    }
  }

  .header-title-section {
    display: flex;
    align-items: center;
    gap: 12px;
    flex: 1;
  }

  .header-icon {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .header-title {
    font-family: var(--font-display);
    font-size: 24px;
    color: var(--gold-primary);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 0;
    font-weight: 600;
  }

  .header-info {
    display: flex;
    align-items: center;
    gap: 16px;

    .status-badge {
      padding: 6px 14px;
      background: rgba(0, 230, 118, 0.15);
      border: 1px solid var(--fall);
      color: var(--fall);
      font-family: var(--font-display);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 1px;

      &.live {
        background: rgba(0, 230, 118, 0.15);
        border-color: var(--fall);
        color: var(--fall);
      }
    }

    .time-display {
      font-family: var(--font-mono);
      font-size: 13px;
      color: var(--text-muted);
    }
  }
}

.main-card {
  position: relative;
  z-index: 1;
}

.tabs-container {
  display: flex;
  gap: 2px;
  border-bottom: 1px solid var(--gold-dim);
  padding: 0 20px;
  overflow-x: auto;
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
  white-space: nowrap;

  svg {
    stroke: var(--text-muted);
  }

  &:hover {
    color: var(--gold-primary);

    svg {
      stroke: var(--gold-primary);
    }

    background: rgba(212, 175, 55, 0.05);
  }

  &.active {
    color: var(--gold-primary);
    border-bottom-color: var(--gold-primary);
    background: rgba(212, 175, 55, 0.08);

    svg {
      stroke: var(--gold-primary);
    }
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

  .header-card {
    padding: 15px;

    .header-content {
      flex-wrap: wrap;
      gap: 12px;
    }

    .back-button {
      width: 36px;
      height: 36px;
    }

    .header-title-section {
      .header-title {
        font-size: 18px;
        letter-spacing: 1px;
      }
    }

    .header-info {
      flex-wrap: wrap;
      gap: 8px;
      width: 100%;

      .time-display {
        font-size: 11px;
      }
    }
  }

  .main-card {
    padding: 15px;
  }

  .tabs-container {
    padding: 0 10px;

    .tab-button {
      padding: 12px 16px;
      font-size: 11px;
      letter-spacing: 0.5px;
    }
  }

  .tab-content {
    padding: 15px;
    min-height: 400px;
  }
}
</style>
