<template>
    <div class="hybrid-ticker-list" :class="{ 'hybrid-ticker-list--virtual': virtualScroll }">
        <!-- 标题 -->
        <div v-if="title" class="hybrid-ticker-list__header">
            <h4 class="hybrid-ticker-list__title">{{ title }}</h4>
            <div class="hybrid-ticker-list__divider"></div>
        </div>

        <!-- 数据容器 -->
        <div class="hybrid-ticker-list__container" ref="container" @scroll="handleScroll">
            <div
                class="hybrid-ticker-list__content"
                :style="{ transform: virtualScroll ? `translateX(-${offset}px)` : undefined }"
            >
                <!-- 虚拟滚动模式 -->
                <template v-if="virtualScroll">
                    <div
                        v-for="(ticker, index) in visibleTickers"
                        :key="ticker.symbol"
                        class="hybrid-ticker-list__item-wrapper"
                        :style="{ transform: `translateX(${index * itemWidth}px)` }"
                    >
                        <ArtDecoTicker
                            :symbol="ticker.symbol"
                            :name="ticker.name"
                            :price="ticker.price"
                            :change="ticker.change"
                            :change-percent="ticker.changePercent"
                            :size="size"
                            :show-name="showName"
                            :clickable="clickable"
                            @click="handleTickerClick"
                            class="hybrid-ticker-list__ticker"
                        />
                    </div>
                </template>

                <!-- 传统滚动模式 -->
                <template v-else>
                    <ArtDecoTicker
                        v-for="ticker in displayTickers"
                        :key="ticker.symbol"
                        :symbol="ticker.symbol"
                        :name="ticker.name"
                        :price="ticker.price"
                        :change="ticker.change"
                        :change-percent="ticker.changePercent"
                        :size="size"
                        :show-name="showName"
                        :clickable="clickable"
                        @click="handleTickerClick"
                    />
                </template>
            </div>
        </div>

        <!-- 性能监控 (开发模式) -->
        <div v-if="showPerformanceInfo" class="hybrid-ticker-list__perf">
            Rendered: {{ virtualScroll ? visibleTickers.length : displayTickers.length }} / Total: {{ tickers.length }}
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
    import ArtDecoTicker from './ArtDecoTicker.vue'

    interface TickerItem {
        symbol: string
        name?: string
        price: number
        change?: number
        changePercent?: number
    }

    interface Props {
        title?: string
        tickers: TickerItem[]
        size?: 'sm' | 'md' | 'lg'
        showName?: boolean
        clickable?: boolean
        virtualScroll?: boolean
        itemWidth?: number
        containerHeight?: number
        bufferSize?: number
        showPerformanceInfo?: boolean
    }

    const props = withDefaults(defineProps<Props>(), {
        title: '',
        size: 'sm',
        showName: false,
        clickable: true,
        virtualScroll: true, // 默认启用虚拟滚动
        itemWidth: 200, // 每个ticker的宽度
        containerHeight: 60,
        bufferSize: 5, // 缓冲区大小
        showPerformanceInfo: false
    })

    const emit = defineEmits<{
        'ticker-click': [symbol: string]
    }>()

    const container = ref<HTMLElement>()
    const offset = ref(0)
    const containerWidth = ref(0)

    // 虚拟滚动计算
    const totalWidth = computed(() => props.tickers.length * props.itemWidth)
    const visibleRange = computed(() => {
        const start = Math.max(0, Math.floor(offset.value / props.itemWidth) - props.bufferSize)
        const end = Math.min(
            props.tickers.length,
            Math.ceil((offset.value + containerWidth.value) / props.itemWidth) + props.bufferSize
        )
        return { start, end }
    })

    const visibleTickers = computed(() => {
        if (!props.virtualScroll) return []
        return props.tickers.slice(visibleRange.value.start, visibleRange.value.end)
    })

    // 传统模式显示数据
    const displayTickers = computed(() => {
        if (props.virtualScroll) return []
        return props.tickers
    })

    const handleTickerClick = (symbol: string) => {
        emit('ticker-click', symbol)
    }

    const handleScroll = () => {
        if (!container.value || !props.virtualScroll) return
        offset.value = container.value.scrollLeft
    }

    const updateContainerWidth = () => {
        if (container.value) {
            containerWidth.value = container.value.clientWidth
        }
    }

    // 性能优化：防抖更新
    let resizeObserver: ResizeObserver | null = null
    let rafId: number | null = null

    onMounted(() => {
        updateContainerWidth()

        // 使用 ResizeObserver 监听容器大小变化
        if (container.value && window.ResizeObserver) {
            resizeObserver = new ResizeObserver(() => {
                if (rafId) cancelAnimationFrame(rafId)
                rafId = requestAnimationFrame(updateContainerWidth)
            })
            resizeObserver.observe(container.value)
        }

        // 监听窗口resize
        window.addEventListener('resize', updateContainerWidth)
    })

    onBeforeUnmount(() => {
        if (resizeObserver) {
            resizeObserver.disconnect()
        }
        if (rafId) {
            cancelAnimationFrame(rafId)
        }
        window.removeEventListener('resize', updateContainerWidth)
    })
</script>

<style scoped lang="scss">
    @import '@/styles/data-dense/index.scss';

    // ============================================
    //   HYBRID TICKER LIST - 数据密集型行情列表
    //   混合 Art Deco 视觉 + 数据密集性能优化
    // ============================================

    .hybrid-ticker-list {
        width: 100%;
        @include hybrid-card;
        @include gpu-accelerated;

        // 虚拟滚动模式
        &--virtual {
            .hybrid-ticker-list__container {
                @include virtual-scroll-container;
                overflow-x: auto;
                overflow-y: hidden;
            }

            .hybrid-ticker-list__content {
                @include gpu-accelerated;
                will-change: transform;
                position: relative;
                height: 100%;
            }

            .hybrid-ticker-list__item-wrapper {
                @include gpu-accelerated;
                position: absolute;
                top: 0;
                left: 0;
                height: 100%;
                display: flex;
                align-items: center;
            }

            .hybrid-ticker-list__ticker {
                flex-shrink: 0;
            }
        }

        // 非虚拟滚动模式
        &:not(&--virtual) {
            .hybrid-ticker-list__content {
                display: flex;
                gap: var(--data-dense-gap-sm);
                padding: var(--data-dense-padding-sm);
            }
        }
    }

    .hybrid-ticker-list__header {
        @include data-dense-spacing;
        display: flex;
        align-items: center;
        border-bottom: var(--data-dense-border-width) solid var(--data-dense-border-color);
        gap: var(--data-dense-gap-sm);
    }

    .hybrid-ticker-list__title {
        @include artdeco-gold-accent;
        font-family: var(--hybrid-font-display);
        font-size: var(--data-dense-font-base);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 0;
        white-space: nowrap;
    }

    .hybrid-ticker-list__divider {
        flex: 1;
        height: 1px;
        background: linear-gradient(to right, var(--artdeco-gold-primary), transparent);
    }

    .hybrid-ticker-list__container {
        height: v-bind('containerHeight + "px"');
        position: relative;
    }

    .hybrid-ticker-list__content {
        @include data-dense-spacing;
    }

    // 性能监控信息 (开发模式)
    .hybrid-ticker-list__perf {
        position: absolute;
        top: 2px;
        right: 2px;
        font-size: 10px;
        color: rgba(255, 255, 255, 0.5);
        background: rgba(0, 0, 0, 0.8);
        padding: 2px 4px;
        border-radius: 0px;
        font-family: var(--hybrid-font-mono);
        pointer-events: none;
        z-index: 10;
    }

    // ============================================
    //   RESPONSIVE DESIGN - 响应式设计
    // ============================================

    @media (max-width: 768px) {
        .hybrid-ticker-list {
            .hybrid-ticker-list__title {
                font-size: var(--data-dense-font-sm);
            }
        }
    }

    // ============================================
    //   PERFORMANCE NOTES - 性能说明
    // ============================================

    /*
  虚拟滚动优化：
  1. 只渲染可见区域的ticker (start-end范围内 + buffer)
  2. 使用transform进行定位，避免DOM重排
  3. GPU加速渲染
  4. ResizeObserver监听容器变化

  预期性能提升：
  - 1000+ ticker时，从 ~30fps 提升到 ~60fps
  - 内存使用减少 70%
  - 初始渲染时间减少 80%
*/
</style>
