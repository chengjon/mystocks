<template>
    <div class="artdeco-ticker" :class="[sizeClass, { clickable }]" @click="handleClick">
        <!-- 股票代码 -->
        <div class="ticker-symbol">{{ symbol }}</div>

        <!-- 股票名称 -->
        <div v-if="showName && name" class="ticker-name">{{ name }}</div>

        <!-- 价格 -->
        <div class="ticker-price" :class="priceClass">
            {{ formattedPrice }}
        </div>

        <!-- 涨跌幅 -->
        <div v-if="showChange" class="ticker-change" :class="changeClass">
            <span class="change-arrow">{{ changeArrow }}</span>
            <span class="change-value">{{ formattedChange }}</span>
        </div>

        <!-- 成交量/成交额 -->
        <div v-if="showVolume && volume" class="ticker-volume">
            {{ formattedVolume }}
        </div>

        <!-- 状态指示器 -->
        <div v-if="showStatus" class="ticker-status">
            <span class="status-dot" :class="statusClass"></span>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { computed } from 'vue'

    interface Props {
        symbol: string
        name?: string
        price: number
        change?: number
        changePercent?: number
        volume?: number | string
        size?: 'sm' | 'md' | 'lg'
        clickable?: boolean
        showName?: boolean
        showChange?: boolean
        showVolume?: boolean
        showStatus?: boolean
        status?: 'up' | 'down' | 'flat'
    }

    const props = withDefaults(defineProps<Props>(), {
        name: '',
        change: 0,
        changePercent: 0,
        volume: '',
        size: 'md',
        clickable: false,
        showName: true,
        showChange: true,
        showVolume: false,
        showStatus: false,
        status: 'flat'
    })

    const emit = defineEmits<{
        click: [symbol: string]
    }>()

    // 尺寸类名
    const sizeClass = computed(() => `artdeco-ticker--${props.size}`)

    // 价格类名
    const priceClass = computed(() => {
        if (props.change > 0) return 'price-up'
        if (props.change < 0) return 'price-down'
        return 'price-flat'
    })

    // 涨跌幅类名
    const changeClass = computed(() => {
        if (props.change > 0) return 'change-up'
        if (props.change < 0) return 'change-down'
        return 'change-flat'
    })

    // 箭头符号
    const changeArrow = computed(() => {
        if (props.change > 0) return '▲'
        if (props.change < 0) return '▼'
        return '●'
    })

    // 状态类名
    const statusClass = computed(() => {
        return `status-${props.status}`
    })

    // 格式化价格
    const formattedPrice = computed(() => {
        return props.price.toFixed(2)
    })

    // 格式化涨跌幅
    const formattedChange = computed(() => {
        const prefix = props.change >= 0 ? '+' : ''
        return `${prefix}${props.changePercent?.toFixed(2) || 0}%`
    })

    // 格式化成交量
    const formattedVolume = computed(() => {
        if (!props.volume) return ''
        const vol = typeof props.volume === 'string' ? parseFloat(props.volume) : props.volume
        if (vol >= 100000000) {
            return `${(vol / 100000000).toFixed(2)}亿`
        } else if (vol >= 10000) {
            return `${(vol / 10000).toFixed(2)}万`
        }
        return vol.toLocaleString('zh-CN')
    })

    // 点击处理
    const handleClick = () => {
        if (props.clickable) {
            emit('click', props.symbol)
        }
    }
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    // ============================================
    //   ART DECO TICKER - 股票行情组件
    //   用于仪表盘、行情条、股票卡片
    // ============================================

    .artdeco-ticker {
        display: inline-flex;
        align-items: center;
        gap: var(--artdeco-spacing-2);
        padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
        background: var(--artdeco-bg-card);
        border: 1px solid var(--artdeco-border-default);
        font-family: var(--artdeco-font-body);

        &.clickable {
            cursor: pointer;
            transition: all var(--artdeco-transition-base);

            &:hover {
                border-color: var(--artdeco-gold-primary);
                box-shadow: var(--artdeco-glow-subtle);
                transform: translateY(-2px);
            }
        }
    }

    // ============================================
    //   SIZE VARIANTS - 尺寸变体
    // ============================================

    .artdeco-ticker--sm {
        padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
        gap: var(--artdeco-spacing-1);

        .ticker-symbol {
            font-size: var(--artdeco-text-xs);
        }

        .ticker-price {
            font-size: var(--artdeco-text-sm);
        }

        .ticker-change {
            font-size: var(--artdeco-text-xs);
        }
    }

    .artdeco-ticker--md {
        .ticker-symbol {
            font-size: var(--artdeco-text-sm);
        }

        .ticker-price {
            font-size: var(--artdeco-text-base);
        }

        .ticker-change {
            font-size: var(--artdeco-text-sm);
        }
    }

    .artdeco-ticker--lg {
        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
        gap: var(--artdeco-spacing-3);

        .ticker-symbol {
            font-size: var(--artdeco-text-base);
        }

        .ticker-price {
            font-size: var(--artdeco-text-lg);
        }

        .ticker-change {
            font-size: var(--artdeco-text-base);
        }
    }

    // ============================================
    //   TYPOGRAPHY - 排版样式
    // ============================================

    .ticker-symbol {
        font-family: var(--artdeco-font-display);
        font-weight: 700;
        color: var(--artdeco-gold-primary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .ticker-name {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-sm);
        color: var(--artdeco-fg-muted);
        max-width: 80px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .ticker-price {
        font-family: var(--artdeco-font-mono);
        font-weight: 700;
        font-variant-numeric: tabular-nums;
        min-width: 70px;
        text-align: right;

        &.price-up {
            color: var(--artdeco-up);
        }

        &.price-down {
            color: var(--artdeco-down);
        }

        &.price-flat {
            color: var(--artdeco-fg-secondary);
        }
    }

    .ticker-change {
        font-family: var(--artdeco-font-mono);
        font-weight: 600;
        font-variant-numeric: tabular-nums;
        display: inline-flex;
        align-items: center;
        gap: 2px;
        padding: 2px 6px;
        border-radius: var(--artdeco-radius-none);

        &.change-up {
            color: var(--artdeco-up);
            background: rgba(255, 82, 82, 0.1);
        }

        &.change-down {
            color: var(--artdeco-down);
            background: rgba(0, 230, 118, 0.1);
        }

        &.change-flat {
            color: var(--artdeco-fg-muted);
            background: rgba(184, 184, 184, 0.1);
        }
    }

    .change-arrow {
        font-size: 0.8em;
    }

    .ticker-volume {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
    }

    // ============================================
    //   STATUS INDICATOR - 状态指示器
    // ============================================

    .ticker-status {
        margin-left: var(--artdeco-spacing-2);
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: block;

        &.status-up {
            background: var(--artdeco-up);
            box-shadow: 0 0 8px var(--artdeco-up);
        }

        &.status-down {
            background: var(--artdeco-down);
            box-shadow: 0 0 8px var(--artdeco-down);
        }

        &.status-flat {
            background: var(--artdeco-fg-muted);
        }
    }
</style>
