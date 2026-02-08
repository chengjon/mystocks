<template>
  <div class="auction-analysis">
    <div class="auction-overview">
      <ArtDecoStatCard
        label="竞价成交金额"
        value="1,256亿"
        change="12.3"
        change-percent
        variant="gold"
      />
      <ArtDecoStatCard
        label="涨停家数"
        value="68家"
        change="15"
        change-percent
        variant="rise"
      />
      <ArtDecoStatCard
        label="炸板率"
        value="23.5%"
        change="-5.2"
        change-percent
        variant="fall"
      />
      <ArtDecoStatCard
        label="平均涨幅"
        value="8.7%"
        change="2.1"
        change-percent
        variant="gold"
      />
    </div>

    <ArtDecoCard title="竞价抢筹分析" hoverable class="auction-card">
      <ArtDecoTable :columns="columns" :data="auctionData" />
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { ArtDecoStatCard, ArtDecoCard, ArtDecoTable } from '@/components/artdeco'

interface Props {
  auctionData: any[]
}

defineProps<Props>()

const columns = [
  { key: 'rank', label: '排名', width: '60px' },
  { key: 'name', label: '股票信息' },
  { key: 'price', label: '最新价', align: 'right' },
  { key: 'change', label: '涨跌幅', variant: 'color', align: 'right' },
  { key: 'volume', label: '成交量', align: 'right' },
  { key: 'amount', label: '成交额', align: 'right' },
  { key: 'robRate', label: '抢筹度', variant: 'progress' }
]
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.auction-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-6);
}
</style>
