<template>
  <div class="portfolio-monitor">
    <div class="portfolio-stats">
      <ArtDecoStatCard label="总资产" value="¥1,256,789" :change="12.5" change-percent variant="rise" />
      <ArtDecoStatCard label="今日盈亏" value="+¥8,450" :change="0.68" change-percent variant="rise" />
      <ArtDecoStatCard label="持仓仓位" value="65%" variant="gold" />
      <ArtDecoStatCard label="可用资金" value="¥439,339" variant="gold" />
    </div>

    <ArtDecoCard title="持仓明细" class="positions-card" style="margin-top: 24px;">
      <ArtDecoTable :columns="columns" :data="positions" />
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { ArtDecoStatCard, ArtDecoCard, ArtDecoTable } from '@/components/artdeco'

interface Props {
  positions: any[]
}

defineProps<Props>()

const columns = [
  { key: 'symbol', label: '代码' },
  { key: 'name', label: '名称' },
  { key: 'quantity', label: '持仓', align: 'right' },
  { key: 'cost', label: '成本', align: 'right' },
  { key: 'price', label: '现价', align: 'right' },
  { key: 'pnl', label: '盈亏', variant: 'color', align: 'right' }
]
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.portfolio-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--artdeco-spacing-4);
}
</style>
