<template>
  <div class="qm-strategy-repo">
    <QuantMatrixShellCard title="策略仓库">
      <table class="qm-strategy-repo__table">
        <thead>
          <tr>
            <th>策略</th>
            <th>状态</th>
            <th>近30日收益</th>
            <th>最大回撤</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.name">
            <td>{{ row.name }}</td>
            <td>
              <span class="qm-chip" :class="`qm-chip--${row.status}`">{{ row.statusText }}</span>
            </td>
            <td :class="row.pnl >= 0 ? 'is-up' : 'is-down'">{{ row.pnl >= 0 ? '+' : '' }}{{ row.pnl }}%</td>
            <td>{{ row.drawdown }}%</td>
          </tr>
        </tbody>
      </table>
    </QuantMatrixShellCard>
  </div>
</template>

<script setup lang="ts">
import QuantMatrixShellCard from '@/components/quant-matrix/base/QuantMatrixShellCard.vue'

const rows = [
  { name: '趋势跟随-Alpha', status: 'active', statusText: '运行中', pnl: 8.4, drawdown: -3.2 },
  { name: '均值回归-Beta', status: 'queued', statusText: '排队中', pnl: 3.1, drawdown: -1.4 },
  { name: '事件驱动-Gamma', status: 'paused', statusText: '已暂停', pnl: -0.8, drawdown: -4.6 }
]
</script>

<style scoped lang="scss">
@import '@/styles/quant-matrix/views/quant-matrix-strategy-repo.scss';
</style>
