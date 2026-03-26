<template>
    <div class="artdeco-orderbook">
        <!-- Asks (Sells) - Top down from Ask 5 to Ask 1 -->
        <div class="artdeco-orderbook-section asks">
            <div v-for="(order, index) in reversedAsks" :key="'ask-' + (5 - index)" class="artdeco-orderbook-row">
                <span class="row-label text-fall">卖 {{ 5 - index }}</span>
                <span class="row-price">{{ formatPrice(order.price) }}</span>
                <span class="row-volume">{{ order.volume }}</span>
                <div class="artdeco-depth-bar depth-fall" :style="{ width: calculateWidth(order.volume) }"></div>
            </div>
        </div>

        <!-- Spread / Current Price -->
        <div class="artdeco-orderbook-meta">
            <div class="current-price" :class="priceChangeClass">
                {{ formatPrice(currentPrice) }}
                <span class="price-arrow">{{ currentPrice >= lastClose ? '▲' : '▼' }}</span>
            </div>
            <div class="price-details">
                <span>幅 {{ priceChangePercent }}%</span>
            </div>
        </div>

        <!-- Bids (Buys) - Top down from Bid 1 to Bid 5 -->
        <div class="artdeco-orderbook-section bids">
            <div v-for="(order, index) in bids" :key="'bid-' + (index + 1)" class="artdeco-orderbook-row">
                <span class="row-label text-rise">买 {{ index + 1 }}</span>
                <span class="row-price">{{ formatPrice(order.price) }}</span>
                <span class="row-volume">{{ order.volume }}</span>
                <div class="artdeco-depth-bar depth-rise" :style="{ width: calculateWidth(order.volume) }"></div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { computed } from 'vue'

    interface OrderItem {
        price: number
        volume: number
    }

    interface Props {
        asks: OrderItem[] // 卖单
        bids: OrderItem[] // 买单
        currentPrice: number
        lastClose: number
        maxVolume?: number
    }

    const props = withDefaults(defineProps<Props>(), {
        maxVolume: 0
    })

    const reversedAsks = computed(() => [...props.asks].reverse())

    const actualMaxVolume = computed(() => {
        if (props.maxVolume > 0) return props.maxVolume
        const allVolumes = [...props.asks, ...props.bids].map(o => o.volume)
        return Math.max(...allVolumes, 1)
    })

    const priceChangePercent = computed(() => {
        if (!props.lastClose) return '0.00'
        return (((props.currentPrice - props.lastClose) / props.lastClose) * 100).toFixed(2)
    })

    const priceChangeClass = computed(() => {
        if (props.currentPrice > props.lastClose) return 'text-rise'
        if (props.currentPrice < props.lastClose) return 'text-fall'
        return 'text-flat'
    })

    function formatPrice(price: number) {
        return price.toFixed(2)
    }

    function calculateWidth(volume: number) {
        return `${(volume / actualMaxVolume.value) * 100}%`
    }
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens';

    .artdeco-orderbook {
      background: var(--artdeco-bg-card);
      border: 1px solid var(--artdeco-gold-opacity-20);
      padding: var(--artdeco-spacing-2);
      font-family: var(--artdeco-font-mono);
      width: 100%;
    }

    .artdeco-orderbook-section {
      display: flex;
      flex-direction: column;
    }

    .artdeco-orderbook-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
      position: relative;
      height: var(--artdeco-spacing-6);
      z-index: 1;
    }

    .artdeco-orderbook-row:hover {
      background: var(--artdeco-gold-opacity-05);
    }

    .row-label {
      font-size: var(--artdeco-font-size-sm); // Compact small size
      width: var(--artdeco-spacing-10);
    }

    .row-price {
      flex: 1;
      text-align: left;
      padding-left: calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) + var(--artdeco-spacing-px));
      font-weight: 600;
      color: var(--artdeco-fg-secondary);
    }

    .row-volume {
      text-align: right;
      color: var(--artdeco-silver-dim);
      font-size: var(--artdeco-font-size-sm); // Compact small size
    }

    .artdeco-depth-bar {
      position: absolute;
      top: calc(var(--artdeco-spacing-px) + var(--artdeco-spacing-px));
      bottom: calc(var(--artdeco-spacing-px) + var(--artdeco-spacing-px));
      right: 0;
      opacity: 15%;
      z-index: -1;
      transition: width 0.3s ease-out;
    }

    .depth-fall { background: var(--artdeco-down); }
    .depth-rise { background: var(--artdeco-up); }

    .artdeco-orderbook-meta {
      margin: var(--artdeco-spacing-3) 0;
      padding: var(--artdeco-spacing-2);
      border-top: 1px solid var(--artdeco-gold-opacity-20);
      border-bottom: 1px solid var(--artdeco-gold-opacity-20);
      text-align: center;
    }

    .current-price {
      font-size: var(--artdeco-font-size-md); // Compact emphasis size
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: var(--artdeco-spacing-2);
    }

    .price-details {
      font-size: var(--artdeco-font-size-sm); // Compact small size
      color: var(--artdeco-fg-muted);
      margin-top: var(--artdeco-spacing-1);
    }

    .text-rise { color: var(--artdeco-up); }
    .text-fall { color: var(--artdeco-down); }
    .text-flat { color: var(--artdeco-fg-muted); }

    .price-arrow { font-size: var(--artdeco-font-size-sm); } // Compact small size
</style>
