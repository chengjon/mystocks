<template>
  <div class="artdeco-strategy-lab">
    <!-- Strategy Statistics -->
    <div class="artdeco-grid-2">
      <div class="artdeco-card">
        <h3>策略概览</h3>
        <div class="artdeco-stats-triple">
          <div>
            <div class="artdeco-stat-value">{{ strategyStats.total }}</div>
            <div class="artdeco-stat-label">总策略数</div>
          </div>
          <div>
            <div class="artdeco-stat-value artdeco-data-rise">{{ strategyStats.running }}</div>
            <div class="artdeco-stat-label">运行中</div>
          </div>
          <div>
            <div class="artdeco-stat-value artdeco-data-fall">{{ strategyStats.paused }}</div>
            <div class="artdeco-stat-label">已暂停</div>
          </div>
        </div>
      </div>

      <div class="artdeco-card">
        <h3>策略表现</h3>
        <div class="artdeco-stats-triple">
          <div>
            <div class="artdeco-stat-value artdeco-data-rise">+{{ strategyStats.bestReturn }}%</div>
            <div class="artdeco-stat-label">最佳收益</div>
          </div>
          <div>
            <div class="artdeco-stat-value artdeco-data-rise">+{{ strategyStats.avgReturn }}%</div>
            <div class="artdeco-stat-label">平均收益</div>
          </div>
          <div>
            <div class="artdeco-stat-value artdeco-data-fall">{{ strategyStats.maxDrawdown }}%</div>
            <div class="artdeco-stat-label">最大回撤</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Strategy List -->
    <div class="artdeco-card">
      <h3>策略列表</h3>
      <table class="artdeco-table">
        <thead>
          <tr>
            <th>策略名称</th>
            <th>类型</th>
            <th>状态</th>
            <th>收益率</th>
            <th>夏普比率</th>
            <th>最大回撤</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="strategy in strategies" :key="strategy.name">
            <td style="font-weight: 600;">{{ strategy.name }}</td>
            <td>{{ strategy.type }}</td>
            <td>
              <span
                class="artdeco-badge"
                :class="strategy.status === 'running' ? 'artdeco-badge-success' : 'artdeco-badge-warning'"
              >
                {{ strategy.status === 'running' ? '运行中' : '已暂停' }}
              </span>
            </td>
            <td
              style="font-family: var(--artdeco-font-mono);"
              :class="strategy.return >= 0 ? 'artdeco-data-rise' : 'artdeco-data-fall'"
            >
              {{ strategy.return >= 0 ? '+' : '' }}{{ strategy.return }}%
            </td>
            <td style="font-family: var(--artdeco-font-mono);">{{ strategy.sharpe }}</td>
            <td style="font-family: var(--artdeco-font-mono);" class="artdeco-data-fall">
              {{ strategy.drawdown }}%
            </td>
            <td>{{ strategy.created }}</td>
            <td>
              <button
                class="artdeco-btn artdeco-btn-secondary"
                style="padding: 6px 12px; font-size: 0.75rem; margin-right: var(--artdeco-space-xs);"
                @click="editStrategy(strategy.name)"
              >
                编辑
              </button>
              <button
                class="artdeco-btn artdeco-btn-secondary"
                style="padding: 6px 12px; font-size: 0.75rem;"
                @click="backtestStrategy(strategy.name)"
              >
                回测
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// Types
interface Strategy {
  name: string
  type: string
  status: 'running' | 'paused'
  return: number
  sharpe: number
  drawdown: number
  created: string
}

// State
const strategyStats = ref({
  total: 12,
  running: 8,
  paused: 4,
  bestReturn: 23.5,
  avgReturn: 8.7,
  maxDrawdown: -5.2
})

const strategies = ref<Strategy[]>([
  { name: '双均线突破策略', type: '趋势跟踪', status: 'running', return: 15.6, sharpe: 1.85, drawdown: -8.2, created: '2024-01-15' },
  { name: 'MACD金叉策略', type: '技术指标', status: 'running', return: 23.5, sharpe: 2.12, drawdown: -5.2, created: '2024-02-20' },
  { name: 'RSI超卖策略', type: '均值回归', status: 'paused', return: 8.9, sharpe: 1.45, drawdown: -12.3, created: '2024-03-10' },
  { name: '板块轮动策略', type: '行业轮动', status: 'running', return: 18.7, sharpe: 1.92, drawdown: -7.8, created: '2024-04-05' },
  { name: '低波动率策略', type: '风险控制', status: 'running', return: 12.3, sharpe: 2.05, drawdown: -4.5, created: '2024-05-12' }
])

// Methods
function editStrategy(name: string) {
  console.log('Edit strategy:', name)
  // Navigate to edit page or show modal
}

function backtestStrategy(name: string) {
  console.log('Backtest strategy:', name)
  // Navigate to backtest arena
}
</script>

<style scoped>
@import '@/styles/artdeco/artdeco-theme.css';

.artdeco-strategy-lab {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-space-lg);
}

.artdeco-grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--artdeco-space-lg);
}

.artdeco-card {
  background: var(--artdeco-bg-card);
  border: 2px solid var(--artdeco-gold-primary);
  padding: var(--artdeco-space-lg);
  position: relative;
}

.artdeco-card::before {
  content: '';
  position: absolute;
  top: 4px;
  left: 4px;
  right: 4px;
  bottom: 4px;
  border: 1px solid rgba(212, 175, 55, 0.3);
  pointer-events: none;
}

.artdeco-card h3 {
  font-family: var(--artdeco-font-display);
  font-size: 1rem;
  font-weight: 600;
  color: var(--artdeco-gold-primary);
  margin-bottom: var(--artdeco-space-md);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.artdeco-stats-triple {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--artdeco-space-md);
  text-align: center;
}

.artdeco-stat-value {
  font-size: 2rem;
  color: var(--artdeco-gold-primary);
  font-family: var(--artdeco-font-mono);
  margin-bottom: var(--artdeco-space-xs);
}

.artdeco-stat-label {
  font-size: 0.875rem;
  color: var(--artdeco-silver-dim);
}

.artdeco-table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--artdeco-font-mono);
  font-size: 0.875rem;
}

.artdeco-table th {
  background: var(--artdeco-bg-header);
  color: var(--artdeco-gold-primary);
  font-family: var(--artdeco-font-display);
  font-weight: 600;
  text-align: left;
  padding: 12px var(--artdeco-space-md);
  border-bottom: 2px solid var(--artdeco-gold-primary);
}

.artdeco-table td {
  padding: 12px var(--artdeco-space-md);
  border-bottom: 1px solid var(--artdeco-gold-dim);
  color: var(--artdeco-silver-text);
}

.artdeco-table tr:hover td {
  background: var(--artdeco-bg-hover);
}

.artdeco-badge {
  display: inline-block;
  padding: 4px 12px;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 2px;
}

.artdeco-badge-success {
  background: var(--artdeco-rise);
  color: white;
}

.artdeco-badge-warning {
  background: var(--artdeco-warning);
  color: white;
}

.artdeco-data-rise {
  color: var(--artdeco-rise);
}

.artdeco-data-fall {
  color: var(--artdeco-fall);
}

@media (max-width: 768px) {
  .artdeco-grid-2 {
    grid-template-columns: 1fr;
  }
}
</style>
