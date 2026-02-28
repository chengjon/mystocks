<template>
  <div class="industry-analysis-page">
    <div class="page-header">
      <h2 class="section-title">板块动向分析</h2>
      <ArtDecoButton variant="outline" size="sm" @click="refreshBoards">刷新板块</ArtDecoButton>
    </div>

    <div class="stats-grid">
      <ArtDecoStatCard label="活跃板块" :value="stats.activeBoards" variant="gold" />
      <ArtDecoStatCard label="上涨板块" :value="stats.risingBoards" variant="rise" />
      <ArtDecoStatCard label="领涨强度" :value="`${stats.leadStrength}%`" variant="gold" />
      <ArtDecoStatCard label="回撤板块" :value="stats.fallingBoards" variant="fall" />
    </div>

    <div class="content-grid">
      <ArtDecoCard title="板块热度排行" hoverable>
        <ArtDecoTable :columns="boardColumns" :data="boardRows" />
      </ArtDecoCard>

      <ArtDecoCard title="资金轮动快照" hoverable>
        <div class="rotation-list">
          <div class="rotation-item" v-for="item in rotationRows" :key="item.name">
            <div class="name">{{ item.name }}</div>
            <div class="meta">{{ item.window }}</div>
            <div class="value" :class="item.flow > 0 ? 'rise' : 'fall'">
              {{ item.flow > 0 ? '+' : '' }}{{ item.flow }} 亿
            </div>
          </div>
        </div>
      </ArtDecoCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { ArtDecoButton, ArtDecoCard, ArtDecoStatCard, ArtDecoTable } from '@/components/artdeco'

const stats = reactive({
  activeBoards: 37,
  risingBoards: 22,
  leadStrength: 78,
  fallingBoards: 9
})

const boardColumns = [
  { key: 'rank', label: '排名', width: '80px' },
  { key: 'name', label: '板块' },
  { key: 'change', label: '涨跌幅', variant: 'color' },
  { key: 'turnover', label: '成交额(亿)' },
  { key: 'netInflow', label: '主力净流入(亿)', variant: 'color' }
]

const boardRows = [
  { rank: 1, name: 'AI算力', change: '+4.18%', turnover: 532.6, netInflow: '+28.3' },
  { rank: 2, name: '半导体设备', change: '+3.42%', turnover: 418.1, netInflow: '+17.6' },
  { rank: 3, name: '机器人', change: '+2.95%', turnover: 289.4, netInflow: '+12.8' },
  { rank: 4, name: '新能源储能', change: '-1.12%', turnover: 166.2, netInflow: '-4.1' }
]

const rotationRows = [
  { name: 'AI算力', window: '近1日', flow: 12.4 },
  { name: '高股息', window: '近3日', flow: 7.1 },
  { name: '光伏', window: '近5日', flow: -5.7 },
  { name: '军工', window: '近10日', flow: 3.8 }
]

function refreshBoards() {
  stats.activeBoards += 1
}
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.industry-analysis-page {
  padding: var(--artdeco-spacing-6);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-6);
}

.section-title {
  margin: 0;
  font-size: var(--artdeco-text-2xl);
  color: var(--artdeco-gold-primary);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-6);
}

.content-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: var(--artdeco-spacing-4);
}

.rotation-list {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-3);
}

.rotation-item {
  border: 1px solid var(--artdeco-border-default);
  padding: var(--artdeco-spacing-3);

  .name {
    color: var(--artdeco-fg-primary);
    font-weight: 600;
  }

  .meta {
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-xs);
    margin-top: 2px;
  }

  .value {
    margin-top: var(--artdeco-spacing-2);
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-base);
  }

  .value.rise {
    color: var(--artdeco-rise);
  }

  .value.fall {
    color: var(--artdeco-down);
  }
}
</style>
