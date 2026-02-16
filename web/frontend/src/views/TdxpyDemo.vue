<template>
  <div class="tdxpy-demo">

    <div class="page-header">
      <h1 class="page-title">TDPXY DEMO</h1>
      <p class="page-subtitle">PYTONGDAXIN | REAL-TIME DATA | HISTORICAL DATA</p>
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

    <TdxOverviewTab v-show="activeTab === 'overview'" :active-tab="activeTab" />
    <TdxInstallTab
      v-show="activeTab === 'install'"
      :active-tab="activeTab"
      :standard-servers="standardServers"
      :extended-servers="extendedServers"
    />
    <TdxApiTab
      v-show="activeTab === 'api'"
      :active-tab="activeTab"
      :quote-fields="quoteFields"
      :kline-types="klineTypes"
    />
    <TdxExportTab v-show="activeTab === 'export'" :active-tab="activeTab" />
    <TdxStatusTab v-show="activeTab === 'status'" :active-tab="activeTab" />
  </div>
</template>

<script setup lang="ts">
import TdxOverviewTab from './tdxpy-demo/TdxOverviewTab.vue'
import TdxInstallTab from './tdxpy-demo/TdxInstallTab.vue'
import TdxApiTab from './tdxpy-demo/TdxApiTab.vue'
import TdxExportTab from './tdxpy-demo/TdxExportTab.vue'
import TdxStatusTab from './tdxpy-demo/TdxStatusTab.vue'

import { ref } from 'vue'

const activeTab = ref('overview')

const tabs = [
  { key: 'overview', label: '项目概览', icon: '📋' },
  { key: 'install', label: '安装配置', icon: '⚙️' },
  { key: 'api', label: 'API 示例', icon: '💻' },
  { key: 'export', label: '数据导出', icon: '💾' },
  { key: 'status', label: '集成状态', icon: '✅' }
]

const standardServers = [
  { ip: '119.147.212.81', port: '7709', location: '深圳电信' },
  { ip: '114.80.63.12', port: '7709', location: '上海电信' },
  { ip: '60.12.136.250', port: '7709', location: '杭州电信' },
  { ip: '115.238.90.165', port: '7709', location: '南京电信' }
]

const extendedServers = [
  { ip: '106.14.95.149', port: '7727', location: '上海' },
  { ip: '119.147.164.60', port: '7727', location: '深圳' },
  { ip: '47.103.48.45', port: '7727', location: '杭州' }
]

const quoteFields = [
  { field: 'code', description: '股票代码' },
  { field: 'name', description: '股票名称' },
  { field: 'price', description: '当前价格' },
  { field: 'open', description: '开盘价' },
  { field: 'high', description: '最高价' },
  { field: 'low', description: '最低价' },
  { field: 'pre_close', description: '昨收价' },
  { field: 'percent', description: '涨跌幅 (%)' },
  { field: 'vol', description: '成交量' },
  { field: 'amount', description: '成交额' },
  { field: 'bid1-bid5', description: '五档委买价' },
  { field: 'ask1-ask5', description: '五档委卖价' }
]

const klineTypes = [
  { code: 4, type: '日线', description: '每日K线数据' },
  { code: 5, type: '周线', description: '每周K线数据' },
  { code: 6, type: '月线', description: '每月K线数据' },
  { code: 7, type: '5分钟', description: '5分钟K线数据' },
  { code: 8, type: '15分钟', description: '15分钟K线数据' },
  { code: 9, type: '30分钟', description: '30分钟K线数据' },
  { code: 10, type: '60分钟', description: '60分钟K线数据' },
  { code: 11, type: '1分钟', description: '1分钟K线数据' }
]
</script>
