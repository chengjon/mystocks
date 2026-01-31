<template>
  <ArtDecoCard title="龙虎榜" hoverable variant="elevated">
    <template #header>
      <div class="card-header">
        <ArtDecoIcon name="trophy" />
        <h4>龙虎榜</h4>
        <div class="header-extra">
          <ArtDecoBadge variant="gold" size="sm">{{ date }}</ArtDecoBadge>
        </div>
      </div>
    </template>

    <ArtDecoLoading v-if="loading" text="加载中..." size="sm" />
    <div v-else-if="error" class="error-message">
      <ArtDecoIcon name="alert-circle" />
      <span>{{ error }}</span>
    </div>
    <div v-else class="long-hu-content">
      <div class="long-hu-list">
        <div
          v-for="item in longHuData"
          :key="item.code"
          class="long-hu-item"
          :class="{ 'is-up': item.change_percent >= 0 }"
        >
          <div class="stock-info">
            <div class="stock-name">{{ item.name }}</div>
            <div class="stock-code">{{ item.code }}</div>
          </div>
          <div class="long-hu-reason">{{ item.reason }}</div>
          <div class="long-hu-amount" :class="{ 'is-up': item.amount > 0 }">
            {{ formatAmount(item.amount) }}
          </div>
          <div class="long-hu-change" :class="item.change_percent >= 0 ? 'quant-up' : 'quant-down'">
            {{ item.change_percent >= 0 ? '+' : '' }}{{ item.change_percent }}%
          </div>
        </div>
      </div>
    </div>
  </ArtDecoCard>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ArtDecoCard, ArtDecoIcon, ArtDecoBadge } from '@/components/artdeco'
import { ArtDecoLoading } from '@/components/artdeco/core'
import dashboardService from '@/api/services/dashboardService'

interface LongHuBangItem {
  code: string
  name: string
  reason: string
  amount: number
  change_percent: number
}

const loading = ref(true)
const error = ref('')
const longHuData = ref<LongHuBangItem[]>([])

// 今日日期
const date = computed(() => {
  const today = new Date()
  return today.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
})

// 格式化金额（万→亿）
const formatAmount = (amount: number): string => {
  if (Math.abs(amount) >= 10000) {
    return (amount / 10000).toFixed(2) + '亿'
  }
  return amount.toFixed(0) + '万'
}

// 获取龙虎榜数据
const fetchLongHuBang = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await dashboardService.getLongHuBang(undefined, 10)
    longHuData.value = response.data || []
  } catch (err: any) {
    console.error('Failed to fetch long-hu-bang:', err)
    error.value = '数据加载失败'
    // 使用Mock数据作为降级
    longHuData.value = [
      { code: '600519', name: '贵州茅台', reason: '涨幅偏离值达7%', amount: 125000, change_percent: 7.2 },
      { code: '000001', name: '平安银行', reason: '换手率达20%', amount: 89000, change_percent: 5.3 },
      { code: '300750', name: '宁德时代', reason: '跌幅偏离值达7%', amount: -95000, change_percent: -6.8 },
      { code: '600036', name: '招商银行', reason: '连续三个交易日内涨幅偏离值累计达20%', amount: 78000, change_percent: 4.5 },
      { code: '000002', name: '万科A', reason: '当日涨幅偏离值达7%', amount: 65000, change_percent: 6.2 }
    ]
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchLongHuBang()
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';
@import '@/styles/artdeco-quant-extended.scss';

.card-header {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-3);

  h4 {
    flex: 1;
    margin: 0;
    font-family: var(--artdeco-font-heading);
    font-size: var(--artdeco-text-lg);
    font-weight: var(--artdeco-font-semibold);
    color: var(--artdeco-gold-primary);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
  }

  .header-extra {
    display: flex;
    gap: var(--artdeco-spacing-2);
  }
}

.error-message {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-8);
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
}

.long-hu-content {
  .long-hu-list {
    display: flex;
    flex-direction: column;
    gap: var(--artdeco-dense-gap-xs);
  }

  .long-hu-item {
    display: grid;
    grid-template-columns: 2fr 3fr 2fr 1.5fr;
    gap: var(--artdeco-dense-gap-xs);
    align-items: center;
    padding: var(--artdeco-dense-padding-sm);
    background: var(--artdeco-bg-card);
    border: 1px solid var(--artdeco-border-default);
    border-radius: var(--artdeco-radius-none);
    transition: all var(--artdeco-transition-base) var(--artdeco-ease-out);

    &:hover {
      border-color: var(--artdeco-gold-primary);
      box-shadow: var(--artdeco-glow-subtle);
      transform: translateX(4px);
    }

    .stock-info {
      .stock-name {
        font-family: var(--artdeco-font-body);
        font-weight: var(--artdeco-font-semibold);
        font-size: var(--artdeco-text-data-sm);
        color: var(--artdeco-fg-primary);
        margin-bottom: 2px;
      }

      .stock-code {
        font-family: var(--artdeco-font-data);
        font-size: var(--artdeco-text-data-xs);
        color: var(--artdeco-fg-muted);
      }
    }

    .long-hu-reason {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-text-data-xs);
      color: var(--artdeco-fg-muted);
      line-height: var(--artdeco-leading-snug);
    }

    .long-hu-amount {
      font-family: var(--artdeco-font-data);
      font-weight: var(--artdeco-font-semibold);
      font-size: var(--artdeco-text-data-sm);
      text-align: right;
      color: var(--artdeco-fg-primary);

      &.is-up {
        color: var(--artdeco-up);
      }
    }

    .long-hu-change {
      font-family: var(--artdeco-font-data);
      font-weight: var(--artdeco-font-semibold);
      font-size: var(--artdeco-text-data-sm);
      text-align: right;
    }
  }
}
</style>
