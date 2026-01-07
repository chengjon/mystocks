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

.content-section {
  padding: 10px 0;
  line-height: 1.8;
}

.section {
  margin-bottom: 30px;

  &:last-child {
    margin-bottom: 0;
  }

  h3 {
    margin: 0 0 15px 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--primary);
    border-left: 3px solid var(--primary);
    padding-left: 12px;
  }

  p {
    margin: 0;
    color: var(--text-secondary);
  }
}

.accordion {
  margin-top: 20px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.accordion-item {
  border-bottom: 1px solid var(--border);

  &:last-child {
    border-bottom: none;
  }
}

.accordion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 16px 20px;
  background: var(--bg-secondary);
  border: none;
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    background: var(--bg-dark);
  }

  &.active {
    background: var(--bg-dark);
    border-left: 3px solid var(--primary);
  }
}

.accordion-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.accordion-icon {
  font-size: 18px;
  color: var(--primary);
  font-weight: 300;
}

.accordion-content {
  background: var(--bg-primary);
}

.strategy-content {
  padding: 20px;

  h4 {
    margin: 0 0 10px 0;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);

    &:nth-of-type(2) {
      margin-top: 20px;
    }
  }

  p {
    margin: 0;
    color: var(--text-secondary);
  }
}

.code-wrapper {
  margin-top: 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.code-block {
  display: block;
  background: var(--bg-dark);
  border: none;
  border-radius: 0;
  padding: 15px;
  font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre;
  color: var(--text-primary);
  width: 100%;
  min-height: 200px;
  resize: vertical;
}
</style>
