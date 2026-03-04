<template>
  <div class="qm-market-realtime">
    <QuantMatrixShellCard title="关注标的">
      <ul class="qm-market-realtime__watchlist">
        <li v-for="item in watchlist" :key="item.symbol">
          <span>{{ item.symbol }}</span>
          <span :class="item.change >= 0 ? 'is-up' : 'is-down'">{{ item.change >= 0 ? '+' : '' }}{{ item.change }}%</span>
        </li>
      </ul>
    </QuantMatrixShellCard>

    <QuantMatrixShellCard title="实时快照">
      <table class="qm-market-realtime__table">
        <thead>
          <tr>
            <th>代码</th>
            <th>名称</th>
            <th>最新价</th>
            <th>涨跌幅</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.symbol">
            <td>{{ row.symbol }}</td>
            <td>{{ row.name }}</td>
            <td>{{ row.price }}</td>
            <td :class="row.change >= 0 ? 'is-up' : 'is-down'">
              {{ row.change >= 0 ? '+' : '' }}{{ row.change }}%
            </td>
          </tr>
        </tbody>
      </table>
    </QuantMatrixShellCard>
  </div>
</template>

<script setup lang="ts">
import QuantMatrixShellCard from '@/components/quant-matrix/base/QuantMatrixShellCard.vue'

const watchlist = [
  { symbol: '000001.SH', change: 0.43 },
  { symbol: '399001.SZ', change: -0.26 },
  { symbol: '399006.SZ', change: 0.92 }
]

const rows = [
  { symbol: '600519.SH', name: '贵州茅台', price: 1750.3, change: 1.15 },
  { symbol: '000858.SZ', name: '五粮液', price: 150.1, change: 0.42 },
  { symbol: '300750.SZ', name: '宁德时代', price: 201.7, change: -0.84 }
]
</script>

<style scoped lang="scss">
@import '@/styles/quant-matrix/views/quant-matrix-market-realtime.scss';
</style>
