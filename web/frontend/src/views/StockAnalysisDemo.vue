<template>
  <div class="stock-analysis-demo">

    <PageHeader
      title="STOCK ANALYSIS DEMO"
      subtitle="A-SHARE STOCK SCREENING | BACKTESTING | TECHNICAL ANALYSIS"
    />

    <div class="art-deco-nav">
      <div
        v-for="tab in tabs"
        :key="tab.key"
        class="nav-item"
        :class="{ 'is-active': activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        <span class="nav-icon">{{ tab.icon }}</span>
        <span class="nav-label">{{ tab.label }}</span>
      </div>
    </div>

    <StockOverviewTab v-show="activeTab === 'overview'" :activeTab="activeTab" />
    <StockDataTab 
      v-show="activeTab === 'data'" 
      :activeTab="activeTab" 
      :fileFormatData="fileFormatData" 
      :dayStructureData="dayStructureData" 
      :dayParserCode="dayParserCode" 
    />
    <StockStrategyTab v-show="activeTab === 'strategy'" :activeTab="activeTab" />
    <StockBacktestTab v-show="activeTab === 'backtest'" :activeTab="activeTab" :backtestMetrics="backtestMetrics" />
    <StockRealtimeTab v-show="activeTab === 'realtime'" :activeTab="activeTab" />
    <StockStatusTab v-show="activeTab === 'status'" :activeTab="activeTab" />
  </div>
</template>

<script setup lang="ts">
import StockOverviewTab from './stock-analysis/StockOverviewTab.vue'
import StockDataTab from './stock-analysis/StockDataTab.vue'
import StockStrategyTab from './stock-analysis/StockStrategyTab.vue'
import StockBacktestTab from './stock-analysis/StockBacktestTab.vue'
import StockRealtimeTab from './stock-analysis/StockRealtimeTab.vue'
import StockStatusTab from './stock-analysis/StockStatusTab.vue'

import { ref } from 'vue'
import { PageHeader } from '@/components/shared'

interface TabItem {
  key: string
  label: string
  icon: string
}

interface FileFormatItem {
  type: string
  extension: string
  recordSize: string
  description: string
}

interface DayStructureItem {
  offset: string
  size: string
  type: string
  field: string
  description: string
}

interface BacktestMetricItem {
  metric: string
  description: string
}

const activeTab = ref<string>('overview')

const tabs: TabItem[] = [
  { key: 'overview', label: '项目概览', icon: '📋' },
  { key: 'data', label: '数据解析', icon: '📂' },
  { key: 'strategy', label: '筛选策略', icon: '🔍' },
  { key: 'backtest', label: '回测系统', icon: '📈' },
  { key: 'realtime', label: '实时监控', icon: '⏰' },
  { key: 'status', label: '集成状态', icon: '✅' }
]

// Code examples as string constants to avoid Vue template parsing issues
const dayParserCode = `import struct
import pandas as pd
from datetime import datetime

def parse_tdx_day_file(file_path):
    """
    解析通达信日线数据文件 (.day)

    Returns:
        pd.DataFrame: 包含 OHLCV 据的 DataFrame
    """
    data = []

    with open(file_path, 'rb') as f:
        while True:
            # 读取32字节
            record = f.read(32)
            if len(record) != 32:
                break

            # 解析数据 (小端序)
            fields = struct.unpack('<IIIIIfII', record)

            date = fields[0]  # YYYYMMDD 格式
            open_price = fields[1] / 100.0
            high_price = fields[2] / 100.0
            low_price = fields[3] / 100.0
            close_price = fields[4] / 100.0
            amount = fields[5]  # 成交额
            volume = fields[6]  # 成交量

            # 转换日期格式
            date_str = str(date)
            date_obj = datetime.strptime(date_str, '%Y%m%d')

            data.append({
                'date': date_obj,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume,
                'amount': amount
            })

    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)
    return df

# 使用示例
df = parse_tdx_day_file('D:/tdx/vipdoc/sh/lday/sh600000.day')
print(df.head())
print(f"总共 {len(df)} 条记录")`

const fileFormatData: FileFormatItem[] = [
  { type: '日线', extension: '.day', recordSize: '32字节', description: '每条记录包含日期、OHLC、成交量和成交额' },
  { type: '分钟线', extension: '.lc1', recordSize: '32字节', description: '1分钟K线数据' },
  { type: '5分钟线', extension: '.lc5', recordSize: '32字节', description: '5分钟K线数据' },
  { type: '财务数据', extension: '.gbbq', recordSize: '变长', description: '股本变迁、除权除息数据' }
]

const dayStructureData: DayStructureItem[] = [
  { offset: '0-3', size: '4', type: 'uint32', field: 'date', description: '日期 (YYYYMMDD 格式)' },
  { offset: '4-7', size: '4', type: 'uint32', field: 'open', description: '开盘价 (需除以100)' },
  { offset: '8-11', size: '4', type: 'uint32', field: 'high', description: '最高价 (需除以100)' },
  { offset: '12-15', size: '4', type: 'uint32', field: 'low', description: '最低价 (需除以100)' },
  { offset: '16-19', size: '4', type: 'uint32', field: 'close', description: '收盘价 (需除以100)' },
  { offset: '20-23', size: '4', type: 'float', field: 'amount', description: '成交额 (元)' },
  { offset: '24-27', size: '4', type: 'uint32', field: 'volume', description: '成交量 (手)' },
  { offset: '28-31', size: '4', type: 'uint32', field: 'reserved', description: '保留字段' }
]

const backtestMetrics: BacktestMetricItem[] = [
  { metric: 'Total Returns', description: '总收益率' },
  { metric: 'Annual Returns', description: '年化收益率' },
  { metric: 'Max Drawdown', description: '最大回撤' },
  { metric: 'Sharpe Ratio', description: '夏普比率 (风险调整后收益)' },
  { metric: 'Sortino Ratio', description: '索提诺比率 (下行风险调整后收益)' },
  { metric: 'Win Rate', description: '胜率 (盈利交易占比)' },
  { metric: 'Profit Factor', description: '盈亏比 (总盈利/总亏损)' },
  { metric: 'Total Trades', description: '总交易次数' },
  { metric: 'Average Holding Days', description: '平均持仓天数' }
]
</script>


<style scoped>
@import './styles/StockAnalysisDemo';
</style>
