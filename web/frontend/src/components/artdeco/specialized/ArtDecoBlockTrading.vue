<template>
  <ArtDecoCard title="大宗交易" hoverable variant="elevated">
    <template #header>
      <div class="card-header">
        <ArtDecoIcon name="briefcase" />
        <h4>大宗交易</h4>
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
    <div v-else class="block-trading-content">
      <div class="block-trading-list">
        <div
          v-for="item in blockTradingData"
          :key="item.code"
          class="block-trading-item"
        >
          <div class="stock-info">
            <div class="stock-name">{{ item.name }}</div>
            <div class="stock-code">{{ item.code }}</div>
          </div>
          <div class="trade-price">
            <div class="price-label">成交价</div>
            <div class="price-value quant-data-display">¥{{ item.price.toFixed(2) }}</div>
          </div>
          <div class="trade-amount">
            <div class="amount-label">成交额</div>
            <div class="amount-value quant-data-display">{{ formatAmount(item.amount) }}</div>
          </div>
          <div class="trade-parties">
            <div class="party">
              <div class="party-label">买方</div>
              <div class="party-name">{{ item.buyer }}</div>
            </div>
            <div class="party-divider">→</div>
            <div class="party">
              <div class="party-label">卖方</div>
              <div class="party-name">{{ item.seller }}</div>
            </div>
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

interface BlockTradingItem {
  code: string
  name: string
  price: number
  amount: number
  buyer: string
  seller: string
}

const loading = ref(true)
const error = ref('')
const blockTradingData = ref<BlockTradingItem[]>([])

// 今日日期
const date = computed(() => {
  const today = new Date()
  return today.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
})

// 格式化金额（元→万元）
const formatAmount = (amount: number): string => {
  if (amount >= 10000) {
    return (amount / 10000).toFixed(2) + '亿'
  }
  return (amount / 10000).toFixed(2) + '万'
}

// 获取大宗交易数据
const fetchBlockTrading = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await dashboardService.getBlockTrading(undefined, 10)
    blockTradingData.value = response.data || []
  } catch (err: any) {
    console.error('Failed to fetch block-trading:', err)
    error.value = '数据加载失败'
    // 使用Mock数据作为降级
    blockTradingData.value = [
      {
        code: '600519',
        name: '贵州茅台',
        price: 1850.00,
        amount: 250000000,
        buyer: '机构专用',
        seller: '中信证券总部'
      },
      {
        code: '300750',
        name: '宁德时代',
        price: 245.60,
        amount: 180000000,
        buyer: '机构专用',
        seller: '国泰君安总部'
      },
      {
        code: '600036',
        name: '招商银行',
        price: 38.45,
        amount: 120000000,
        buyer: '机构专用',
        seller: '海通证券总部'
      },
      {
        code: '000001',
        name: '平安银行',
        price: 12.85,
        amount: 95000000,
        buyer: '机构专用',
        seller: '申万宏源总部'
      },
      {
        code: '000002',
        name: '万科A',
        price: 18.90,
        amount: 88000000,
        buyer: '机构专用',
        seller: '广发证券总部'
      }
    ]
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchBlockTrading()
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

.block-trading-content {
  .block-trading-list {
    display: flex;
    flex-direction: column;
    gap: var(--artdeco-dense-gap-xs);
  }

  .block-trading-item {
    display: grid;
    grid-template-columns: 1.5fr 1fr 1.2fr 2fr;
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

    .trade-price {
      text-align: center;

      .price-label {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-data-xs);
        color: var(--artdeco-fg-muted);
        margin-bottom: 2px;
      }

      .price-value {
        font-weight: var(--artdeco-font-semibold);
        color: var(--artdeco-fg-primary);
      }
    }

    .trade-amount {
      text-align: center;

      .amount-label {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-data-xs);
        color: var(--artdeco-fg-muted);
        margin-bottom: 2px;
      }

      .amount-value {
        font-weight: var(--artdeco-font-semibold);
        color: var(--artdeco-gold-primary);
      }
    }

    .trade-parties {
      display: flex;
      align-items: center;
      gap: var(--artdeco-dense-gap-xs);
      text-align: center;

      .party {
        flex: 1;

        .party-label {
          font-family: var(--artdeco-font-body);
          font-size: var(--artdeco-text-data-xs);
          color: var(--artdeco-fg-muted);
          margin-bottom: 2px;
        }

        .party-name {
          font-family: var(--artdeco-font-body);
          font-size: var(--artdeco-text-data-xs);
          color: var(--artdeco-fg-primary);
          line-height: var(--artdeco-leading-snug);
        }
      }

      .party-divider {
        color: var(--artdeco-gold-dim);
        font-size: var(--artdeco-text-data-sm);
      }
    }
  }
}
</style>
