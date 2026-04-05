<template>
  <div class="card demo-card">
    <div class="card-header">
      <span class="card-title">📈 回测系统</span>
      <span class="badge badge-warning">文档</span>
    </div>

    <div class="content-section">
      <div class="section">
        <h3>🔧 回测框架: RQAlpha</h3>
        <p>Stock-Analysis 集成了 RQAlpha 回测框架,提供专业的策略回测能力:</p>

        <div class="cards-grid">
          <div class="sub-card">
            <h4>✨ RQAlpha 特性</h4>
            <ul class="feature-list">
              <li>事件驱动回测引擎</li>
              <li>支持多种订单类型</li>
              <li>完整的交易成本模拟</li>
              <li>丰富的性能指标分析</li>
              <li>可视化回测报告</li>
            </ul>
          </div>

          <div class="sub-card">
            <h4>📊 支持的策略类型</h4>
            <ul class="feature-list">
              <li>日频策略</li>
              <li>分钟频策略</li>
              <li>事件驱动策略</li>
              <li>多品种策略</li>
              <li>期货/期权策略</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="section">
        <h3>💻 回测代码示例</h3>
        <div class="tabs">
          <div class="tab-headers">
            <button
              v-for="(label, key) in tabLabels"
              :key="key"
              class="tab-btn"
              :class="{ active: activeTab === key }"
              @click="activeTab = key"
            >
              {{ label }}
            </button>
          </div>
          <div class="tab-content">
            <textarea readonly class="code-block" :value="backtestExamples[activeTab]"></textarea>
          </div>
        </div>
      </div>

      <div class="section">
        <h3>📊 回测结果指标</h3>
        <table class="table">
          <thead>
            <tr>
              <th width="200">指标</th>
              <th>说明</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in backtestMetrics" :key="index">
              <td><code>{{ item.metric }}</code></td>
              <td>{{ item.description }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { BACKTEST_METRICS } from '../config'
import { BACKTEST_EXAMPLES } from '../code-examples'

const backtestMetrics = BACKTEST_METRICS
const backtestExamples: Record<string, string> = BACKTEST_EXAMPLES

const activeTab = ref('simple')

const tabLabels = {
  simple: '简单策略',
  multi_stock: '多股票策略',
  run_backtest: '运行回测'
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

.cards-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--artdeco-spacing-5);
  margin-top: var(--artdeco-spacing-5);
}

.sub-card {
  padding: var(--artdeco-spacing-5);
  background: color-mix(in srgb, var(--artdeco-gold-primary) 4%, var(--artdeco-bg-card));
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);

  h4 {
    margin: 0 0 calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px)) 0;
    color: var(--artdeco-fg-primary);
    font-size: calc(var(--artdeco-text-sm) + var(--artdeco-spacing-px));
    font-weight: var(--artdeco-font-semibold);
  }
}

.feature-list {
  margin: 0;
  padding-left: var(--artdeco-spacing-5);
  color: var(--artdeco-fg-muted);

  li {
    margin: calc(var(--artdeco-spacing-2) - (var(--artdeco-spacing-px) * 2)) 0;
  }
}

.tabs {
  margin-top: var(--artdeco-spacing-5);
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);
}

.tab-headers {
  display: flex;
  background: color-mix(in srgb, var(--artdeco-gold-primary) 4%, var(--artdeco-bg-card));
  border-bottom: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 12%, transparent);
}

.tab-btn {
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-6);
  border: none;
  border-right: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 12%, transparent);
  background: none;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  cursor: pointer;
  transition:
    background var(--artdeco-transition-quick) var(--artdeco-ease-out),
    color var(--artdeco-transition-quick) var(--artdeco-ease-out);

  &:last-child {
    border-right: none;
  }

  &:hover {
    background: var(--artdeco-bg-elevated);
  }

  &.active {
    background: var(--artdeco-bg-global);
    color: var(--artdeco-gold-primary);
    font-weight: var(--artdeco-font-medium);
  }
}

.tab-content {
  background: var(--artdeco-bg-global);
}

.code-block {
  display: block;
  width: 100%;
  min-height: calc((var(--artdeco-spacing-20) * 3) + var(--artdeco-spacing-10));
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
