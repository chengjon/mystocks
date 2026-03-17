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

.cards-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-top: 20px;
}

.sub-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 20px;

  h4 {
    margin: 0 0 15px 0;
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
  }
}

.feature-list {
  margin: 0;
  padding-left: 20px;
  color: var(--text-secondary);

  li {
    margin: 6px 0;
  }
}

.tabs {
  margin-top: 20px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.tab-headers {
  display: flex;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
}

.tab-btn {
  padding: 12px 24px;
  background: none;
  border: none;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  border-right: 1px solid var(--border);

  &:last-child {
    border-right: none;
  }

  &:hover {
    background: var(--bg-dark);
  }

  &.active {
    background: var(--bg-primary);
    color: var(--primary);
    font-weight: 500;
  }
}

.tab-content {
  background: var(--bg-primary);
}

.code-block {
  display: block;
  background: var(--bg-dark);
  border: none;
  border-radius: 0;
  padding: 15px;
  font-family: 'SF Mono', Monaco, Consolas, monospace;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre;
  color: var(--text-primary);
  width: 100%;
  min-height: 300px;
  resize: vertical;
}
</style>
