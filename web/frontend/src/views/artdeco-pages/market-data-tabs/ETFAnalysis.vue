<template>
  <div class="etf-analysis">
    <div class="etf-overview">
      <ArtDecoStatCard label="ETF总成交额" value="2,345亿" :change="18.5" change-percent variant="gold" />
      <ArtDecoStatCard label="杠杆ETF成交" value="856亿" :change="25.3" change-percent variant="rise" />
      <ArtDecoStatCard label="沪深300ETF" value="4.25%" :change="1.2" change-percent variant="rise" />
      <ArtDecoStatCard label="创业板ETF" value="-2.1%" :change="-0.8" change-percent variant="fall" />
    </div>

    <ArtDecoCard title="热门ETF排行" hoverable class="etf-ranking-card">
      <div class="etf-list">
        <div class="etf-item" v-for="etf in etfRanking" :key="etf.code">
          <div class="etf-info">
            <div class="etf-name">{{ etf.name }}</div>
            <div class="etf-code">{{ etf.code }}</div>
            <div class="etf-type">{{ etf.type }}</div>
          </div>
          <div class="etf-performance">
            <div class="etf-price">¥{{ etf.price }}</div>
            <div class="etf-change" :class="etf.change >= 0 ? 'rise' : 'fall'">
              {{ etf.change >= 0 ? '+' : '' }}{{ etf.change }}%
            </div>
            <div class="etf-volume">{{ etf.volume }}亿</div>
          </div>
        </div>
      </div>
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { ArtDecoStatCard, ArtDecoCard } from '@/components/artdeco'

interface Props {
  etfRanking: any[]
}

defineProps<Props>()
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.etf-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-6);
}

.etf-list {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-3);
}

.etf-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--artdeco-spacing-4);
  background: var(--artdeco-bg-card);
  border: 1px solid rgba(212, 175, 55, 0.1);
  border-radius: var(--artdeco-radius-none);
  transition: all var(--artdeco-transition-base);

  &:hover {
    border-color: var(--artdeco-gold-primary);
    box-shadow: var(--artdeco-glow-subtle);
  }

  .etf-info {
    .etf-name {
      font-family: var(--artdeco-font-body);
      font-weight: 600;
      color: var(--artdeco-fg-primary);
      margin-bottom: 2px;
    }

    .etf-code {
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-text-sm);
      color: var(--artdeco-fg-muted);
    }

    .etf-type {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-text-xs);
      color: var(--artdeco-gold-primary);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);
    }
  }

  .etf-performance {
    text-align: right;

    .etf-price {
      font-family: var(--artdeco-font-mono);
      font-weight: 600;
      color: var(--artdeco-fg-primary);
    }

    .etf-change {
      font-family: var(--artdeco-font-mono);
      font-weight: 700;
      font-size: var(--artdeco-text-sm);

      &.rise { color: var(--artdeco-up); }
      &.fall { color: var(--artdeco-down); }
    }

    .etf-volume {
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-text-sm);
      color: var(--artdeco-fg-muted);
    }
  }
}
</style>
