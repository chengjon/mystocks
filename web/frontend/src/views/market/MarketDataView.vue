<template>
  <div class="market-data-view">

    <div class="card header-card">
      <div class="header-content">
        <button class="back-button" @click="goBack">
          <svg class="market-data-icon back-button__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12,19 5,12 12,5"></polyline>
          </svg>
        </button>

        <div class="header-title-section">
          <div class="header-icon">
            <svg class="market-data-icon header-icon__glyph" viewBox="0 0 24 24" fill="none" stroke="currentColor">
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
          v-for="(tab, _idx) in tabs"
          :key="tab.name"
          class="tab-button"
          :class="{ active: activeTab === tab.name }"
          @click="activeTab = tab.name"
        >
          <svg class="market-data-icon tab-button__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
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
@use '@/styles/artdeco-tokens.scss' as *;

.market-data-view {
  @include artdeco-crosshatch-bg;
  position: relative;
  min-height: 100vh;
  padding: var(--artdeco-spacing-5);
  overflow: hidden;

  &::before {
    content: '';
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    opacity: 0.04;
    background-image:
      repeating-linear-gradient(
        45deg,
        transparent,
        transparent calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) * 2),
        color-mix(in srgb, var(--artdeco-gold-primary) 2%, transparent) calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) * 2),
        color-mix(in srgb, var(--artdeco-gold-primary) 2%, transparent) calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) * 3)
      ),
      repeating-linear-gradient(
        -45deg,
        var(--artdeco-gold-primary) 0,
        var(--artdeco-gold-primary) var(--artdeco-spacing-px),
        transparent var(--artdeco-spacing-px),
        transparent calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) * 2)
      );
  }
}

.market-data-icon {
  flex-shrink: 0;
  stroke-width: calc(var(--artdeco-spacing-px) * 2);
}

.card {
  position: relative;
  z-index: 1;
  background: var(--artdeco-bg-card);
  border: var(--artdeco-spacing-px) solid var(--artdeco-gold-dim);
  border-radius: var(--artdeco-radius-none);

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: var(--artdeco-spacing-4);
    height: var(--artdeco-spacing-4);
    border: calc(var(--artdeco-spacing-px) * 2) solid var(--artdeco-gold-primary);
  }

  &::before {
    top: var(--artdeco-spacing-3);
    left: var(--artdeco-spacing-3);
    border-right: none;
    border-bottom: none;
  }

  &::after {
    right: var(--artdeco-spacing-3);
    bottom: var(--artdeco-spacing-3);
    border-top: none;
    border-left: none;
  }
}

.header-card {
  margin-bottom: var(--artdeco-spacing-5);
  padding:
    var(--artdeco-spacing-5)
    calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1) + var(--artdeco-spacing-px) * 2);

  .header-content {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-5);
  }

  .back-button {
    width: var(--artdeco-spacing-10);
    height: var(--artdeco-spacing-10);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--artdeco-gold-primary);
    background: var(--artdeco-gold-opacity-10);
    border: var(--artdeco-spacing-px) solid var(--artdeco-gold-dim);
    cursor: pointer;
    transition: all var(--artdeco-transition-base) var(--artdeco-ease-out);

    &:hover {
      color: var(--artdeco-bg-global);
      background: var(--artdeco-gold-primary);
    }
  }

  .back-button__icon {
    width: var(--artdeco-spacing-5);
    height: var(--artdeco-spacing-5);
  }

  .header-title-section {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-3);
    flex: 1;
  }

  .header-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--artdeco-gold-primary);
  }

  .header-icon__glyph {
    width: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1));
    height: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1));
  }

  .header-title {
    margin: 0;
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-display);
    font-size: var(--artdeco-text-xl);
    font-weight: var(--artdeco-font-semibold);
    letter-spacing: calc(var(--artdeco-spacing-px) * 2);
    text-transform: uppercase;
  }

  .header-info {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-4);
  }

  .status-badge {
    padding:
      calc(var(--artdeco-spacing-1) + var(--artdeco-spacing-px) * 2)
      calc(var(--artdeco-spacing-3) + var(--artdeco-spacing-px) * 2);
    background: color-mix(in srgb, var(--artdeco-down) 15%, transparent);
    border: var(--artdeco-spacing-px) solid var(--artdeco-down);
    color: var(--artdeco-down);
    font-family: var(--artdeco-font-display);
    font-size: var(--artdeco-text-compact-xs);
    letter-spacing: var(--artdeco-spacing-px);
    text-transform: uppercase;

    &.live {
      background: color-mix(in srgb, var(--artdeco-down) 15%, transparent);
      border-color: var(--artdeco-down);
      color: var(--artdeco-down);
    }
  }

  .time-display {
    color: var(--artdeco-fg-muted);
    font-family: var(--artdeco-font-mono);
    font-size: calc(var(--artdeco-text-compact-xs) + var(--artdeco-spacing-px) * 2);
  }
}

.main-card {
  position: relative;
}

.tabs-container {
  display: flex;
  gap: calc(var(--artdeco-spacing-px) * 2);
  padding: 0 var(--artdeco-spacing-5);
  overflow-x: auto;
  border-bottom: var(--artdeco-spacing-px) solid var(--artdeco-gold-dim);
}

.tab-button {
  position: relative;
  top: var(--artdeco-spacing-px);
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
  padding:
    calc(var(--artdeco-spacing-3) + var(--artdeco-spacing-px) * 3)
    calc(var(--artdeco-spacing-5) + var(--artdeco-spacing-1) + var(--artdeco-spacing-px));
  color: var(--artdeco-fg-muted);
  background: transparent;
  border: none;
  border-bottom: calc(var(--artdeco-spacing-px) * 3) solid transparent;
  cursor: pointer;
  font-family: var(--artdeco-font-display);
  font-size: calc(var(--artdeco-text-compact-xs) + var(--artdeco-spacing-px) * 2);
  letter-spacing: var(--artdeco-spacing-px);
  text-transform: uppercase;
  transition: all var(--artdeco-transition-base) var(--artdeco-ease-out);
  white-space: nowrap;

  &:hover {
    color: var(--artdeco-gold-primary);
    background: var(--artdeco-gold-opacity-05);
  }

  &.active {
    color: var(--artdeco-gold-primary);
    background: var(--artdeco-gold-opacity-08);
    border-bottom-color: var(--artdeco-gold-primary);
  }
}

.tab-button__icon {
  width: var(--artdeco-spacing-4);
  height: var(--artdeco-spacing-4);
}

.tab-content {
  position: relative;
  z-index: 1;
  padding: var(--artdeco-spacing-5);
  min-height: calc(var(--artdeco-spacing-24) * 5 + var(--artdeco-spacing-5));
}

@media (width <= calc(var(--artdeco-spacing-16) * 12)) {
  .market-data-view {
    padding: calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) * 2);
  }

  .header-card {
    padding: calc(var(--artdeco-spacing-3) + var(--artdeco-spacing-px) * 3);

    .header-content {
      flex-wrap: wrap;
      gap: var(--artdeco-spacing-3);
    }

    .back-button {
      width: calc(var(--artdeco-spacing-8) + var(--artdeco-spacing-1));
      height: calc(var(--artdeco-spacing-8) + var(--artdeco-spacing-1));
    }

    .header-title {
      font-size: var(--artdeco-text-compact-lg);
      letter-spacing: var(--artdeco-spacing-px);
    }

    .header-info {
      width: 100%;
      flex-wrap: wrap;
      gap: var(--artdeco-spacing-2);
    }

    .time-display {
      font-size: var(--artdeco-text-compact-xs);
    }
  }

  .main-card {
    padding: calc(var(--artdeco-spacing-3) + var(--artdeco-spacing-px) * 3);
  }

  .tabs-container {
    padding: 0 calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) * 2);
  }

  .tab-button {
    padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
    font-size: var(--artdeco-text-compact-xs);
    letter-spacing: calc(var(--artdeco-spacing-px) / 2);
  }

  .tab-content {
    padding: calc(var(--artdeco-spacing-3) + var(--artdeco-spacing-px) * 3);
    min-height: calc(var(--artdeco-spacing-24) * 4 + var(--artdeco-spacing-4));
  }
}
</style>
