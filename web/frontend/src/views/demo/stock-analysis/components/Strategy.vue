<template>
  <div class="card demo-card">
    <div class="card-header">
      <span class="card-title">🔍 股票筛选策略</span>
      <span class="badge badge-warning">文档</span>
    </div>

    <div class="content-section">
      <div class="section">
        <h3>📊 常用筛选策略</h3>
        <p>以下是一些经典的股票筛选策略示例:</p>

        <div class="accordion">
          <div
            v-for="(item, index) in strategyItems"
            :key="index"
            class="accordion-item"
          >
            <button
              class="accordion-header"
              :class="{ active: openItem === index }"
              @click="toggleItem(index)"
            >
              <span class="accordion-title">{{ item.title }}</span>
              <span class="accordion-icon">{{ openItem === index ? '−' : '+' }}</span>
            </button>
            <div v-if="openItem === index" class="accordion-content">
              <div class="strategy-content">
                <h4>策略说明</h4>
                <p>{{ item.description }}</p>

                <h4>代码实现</h4>
                <div class="code-wrapper">
                  <textarea readonly class="code-block" :value="item.code"></textarea>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="section">
        <h3>🎯 组合筛选示例</h3>
        <div class="code-wrapper">
          <textarea readonly class="code-block" :value="comprehensiveFilterCode"></textarea>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { STRATEGY_EXAMPLES, COMPREHENSIVE_FILTER_CODE } from '../code-examples'

const strategyItems = [
  {
    title: '1️⃣ 均线多头排列',
    description: '寻找 MA5 > MA10 > MA20 > MA60 的股票,表示短期、中期、长期趋势向上',
    code: STRATEGY_EXAMPLES.ma_bullish
  },
  {
    title: '2️⃣ MACD 金叉',
    description: 'MACD 快线上穿慢线,且 MACD 柱状图由负转正,通常是买入信号',
    code: STRATEGY_EXAMPLES.macd_golden
  },
  {
    title: '3️⃣ 放量突破',
    description: '价格突破前期高点,同时成交量放大,表示有资金介入',
    code: STRATEGY_EXAMPLES.breakout_volume
  },
  {
    title: '4️⃣ RSI 超卖反弹',
    description: 'RSI 指标从超卖区域回升,可能是反弹信号',
    code: STRATEGY_EXAMPLES.rsi_oversold
  },
  {
    title: '5️⃣ 底部放量',
    description: '股价处于低位,成交量突然放大,可能是主力建仓信号',
    code: STRATEGY_EXAMPLES.bottom_volume
  }
]

const openItem = ref<number | null>(0)
const comprehensiveFilterCode = COMPREHENSIVE_FILTER_CODE

const toggleItem = (index: number) => {
  openItem.value = openItem.value === index ? null : index
}
</script>

<style scoped lang="scss">
@use '../../../../styles/artdeco-tokens.scss' as *;

.content-section {
  padding: var(--artdeco-spacing-3) 0;
  line-height: 1.8;
}

.section {
  margin-bottom: calc(var(--artdeco-spacing-5) + var(--artdeco-spacing-2) + (var(--artdeco-spacing-px) * 2));

  &:last-child {
    margin-bottom: 0;
  }

  h3 {
    margin: 0 0 calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px)) 0;
    padding-left: var(--artdeco-spacing-3);
    border-left: calc(var(--artdeco-spacing-px) * 3) solid var(--artdeco-gold-primary);
    color: var(--artdeco-gold-primary);
    font-size: calc(var(--artdeco-text-base) + (var(--artdeco-spacing-px) * 2));
    font-weight: var(--artdeco-font-semibold);
    letter-spacing: var(--artdeco-tracking-wide);
  }

  p {
    margin: 0;
    color: var(--artdeco-fg-muted);
  }
}

.accordion {
  margin-top: var(--artdeco-spacing-5);
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);
}

.accordion-item {
  border-bottom: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 12%, transparent);

  &:last-child {
    border-bottom: none;
  }
}

.accordion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: var(--artdeco-spacing-4) var(--artdeco-spacing-5);
  border: none;
  background: color-mix(in srgb, var(--artdeco-gold-primary) 4%, var(--artdeco-bg-card));
  cursor: pointer;
  transition:
    background var(--artdeco-transition-quick) var(--artdeco-ease-out),
    border-color var(--artdeco-transition-quick) var(--artdeco-ease-out);

  &:hover {
    background: var(--artdeco-bg-elevated);
  }

  &.active {
    background: var(--artdeco-bg-elevated);
    border-left: calc(var(--artdeco-spacing-px) * 3) solid var(--artdeco-gold-primary);
  }
}

.accordion-title {
  color: var(--artdeco-fg-primary);
  font-size: var(--artdeco-text-sm);
  font-weight: var(--artdeco-font-medium);
}

.accordion-icon {
  color: var(--artdeco-gold-primary);
  font-size: calc(var(--artdeco-text-base) + (var(--artdeco-spacing-px) * 2));
  font-weight: 300;
}

.accordion-content {
  background: var(--artdeco-bg-global);
}

.strategy-content {
  padding: var(--artdeco-spacing-5);

  h4 {
    margin: 0 0 calc(var(--artdeco-spacing-3) - (var(--artdeco-spacing-px) * 2)) 0;
    color: var(--artdeco-fg-primary);
    font-size: var(--artdeco-text-sm);
    font-weight: var(--artdeco-font-semibold);

    &:nth-of-type(2) {
      margin-top: var(--artdeco-spacing-5);
    }
  }

  p {
    margin: 0;
    color: var(--artdeco-fg-muted);
  }
}

.code-wrapper {
  margin-top: calc(var(--artdeco-spacing-3) - (var(--artdeco-spacing-px) * 2));
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);
}

.code-block {
  display: block;
  width: 100%;
  min-height: calc((var(--artdeco-spacing-20) * 2) + var(--artdeco-spacing-10));
  padding: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
  overflow-x: auto;
  resize: vertical;
  white-space: pre;
  border: none;
  border-radius: var(--artdeco-radius-none);
  background: var(--artdeco-bg-elevated);
  color: var(--artdeco-fg-primary);
  font-family: var(--font-mono);
  font-size: calc(var(--artdeco-text-sm) - var(--artdeco-spacing-px));
  line-height: 1.6;
}
</style>
