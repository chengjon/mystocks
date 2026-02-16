<template>
  <div class="freqtrade-demo">

    <div class="page-header">
      <h1 class="page-title">FREQTRADE DEMO</h1>
      <p class="page-subtitle">CRYPTO TRADING BOT | BACKTESTING | STRATEGY OPTIMIZATION</p>
    </div>

    <div class="function-nav">
      <el-button
        v-for="(tab, _idx) in tabs"
        :key="tab.key"
        :type="activeTab === tab.key ? 'primary' : 'default'"
        @click="activeTab = tab.key"
      >
        {{ tab.icon }} {{ tab.label }}
      </el-button>
    </div>

    <FreqOverviewTab :active-tab="activeTab" :exchanges="exchanges" />
    <FreqStrategyTab :active-tab="activeTab" />
    <FreqBacktestTab :active-tab="activeTab" :metrics-data="metricsData" />
    <FreqConfigTab :active-tab="activeTab" />
    <FreqWebuiTab :active-tab="activeTab" :api-endpoints="apiEndpoints" />
    <FreqStatusTab :active-tab="activeTab" />
  </div>
</template>

<script setup lang="ts">
import FreqOverviewTab from './freqtrade-demo/FreqOverviewTab.vue'
import FreqStrategyTab from './freqtrade-demo/FreqStrategyTab.vue'
import FreqBacktestTab from './freqtrade-demo/FreqBacktestTab.vue'
import FreqConfigTab from './freqtrade-demo/FreqConfigTab.vue'
import FreqWebuiTab from './freqtrade-demo/FreqWebuiTab.vue'
import FreqStatusTab from './freqtrade-demo/FreqStatusTab.vue'

import { ref } from 'vue'

const activeTab = ref('overview')

const tabs = [
  { key: 'overview', label: '项目概览', icon: '📋' },
  { key: 'strategy', label: '策略开发', icon: '📝' },
  { key: 'backtest', label: '回测分析', icon: '📈' },
  { key: 'config', label: '配置说明', icon: '⚙️' },
  { key: 'webui', label: 'Web UI', icon: '🖥️' },
  { key: 'status', label: '集成状态', icon: '✅' }
]

const exchanges = [
  'Binance', 'OKX', 'Bybit', 'Kraken', 'Bitfinex',
  'Huobi', 'Gate.io', 'KuCoin', 'Coinbase Pro', 'Bitstamp'
]

const metricsData = [
  { metric: 'Total Profit', description: '总收益率', target: '> 0%' },
  { metric: 'Win Rate', description: '胜率(盈利交易占比)', target: '≥ 50%' },
  { metric: 'Profit Factor', description: '盈亏比(总盈利/总亏损)', target: '≥ 1.5' },
  { metric: 'Max Drawdown', description: '最大回撤', target: '< 30%' },
  { metric: 'Sharpe Ratio', description: '夏普比率(风险调整收益)', target: '≥ 1.0' },
  { metric: 'Sortino Ratio', description: '索提诺比率(下行风险调整收益)', target: '≥ 1.5' },
  { metric: 'Calmar Ratio', description: '卡玛比率(收益/最大回撤)', target: '≥ 3.0' },
  { metric: 'Total Trades', description: '总交易次数', target: '≥ 100' }
]

const apiEndpoints = [
  { method: 'GET', endpoint: '/api/v1/balance', description: '获取账户余额' },
  { method: 'GET', endpoint: '/api/v1/status', description: '获取机器人状态' },
  { method: 'GET', endpoint: '/api/v1/trades', description: '获取交易历史' },
  { method: 'GET', endpoint: '/api/v1/performance', description: '获取性能指标' },
  { method: 'POST', endpoint: '/api/v1/start', description: '启动交易' },
  { method: 'POST', endpoint: '/api/v1/stop', description: '停止交易' },
  { method: 'POST', endpoint: '/api/v1/forcebuy', description: '强制买入' },
  { method: 'POST', endpoint: '/api/v1/forcesell', description: '强制卖出' },
  { method: 'GET', endpoint: '/api/v1/logs', description: '获取日志' }
]
</script>
