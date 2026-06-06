<script setup lang="ts">
    import { computed, getCurrentInstance, onMounted, ref } from 'vue'
    import { ArtDecoButton, ArtDecoCard, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
    import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
    import { apiClient } from '@/api/apiClient'
    import { extractTradesPayload, toTradingHistoryRows } from '@/views/artdeco-pages/trading-tabs/tradingDataTransform'

    export interface TradeHistory {
        id: string | number
        time: string
        symbol: string
        symbolName: string
        type: 'buy' | 'sell'
        typeText: string
        price: number
        quantity: number
        amount: number
        fee: number
        status: 'completed' | 'pending' | 'cancelled'
        statusText: string
    }

    const props = defineProps<{
        history?: TradeHistory[]
        loading?: boolean
    }>()

    const internalHistory = ref<TradeHistory[]>([])
    const hasLoaded = ref(false)
    const staleError = ref<string | null>(null)
    const hasVerifiedHistorySnapshot = ref(false)
    const lastVerifiedRequestId = ref('')
    const lastVerifiedProcessTime = ref('')
    const instance = getCurrentInstance()
    const { exec, loading: apiLoading, error, lastRequestId, lastProcessTime } = useArtDecoApi()

    const isEmbedded = computed(() => {
        const rawProps = instance?.vnode.props
        return Boolean(rawProps && ('history' in rawProps || 'loading' in rawProps))
    })

    const displayHistory = computed(() => {
        if (Array.isArray(props.history) && props.history.length > 0) {
            return props.history
        }
        return internalHistory.value
    })

    const effectiveLoading = computed(() => props.loading ?? apiLoading.value)
    const isPendingFirstLoad = computed(() => !isEmbedded.value && !hasLoaded.value)
    const isLoadingState = computed(() => effectiveLoading.value || isPendingFirstLoad.value)
    const showSummaryPlaceholders = computed(() => {
        if (isEmbedded.value) {
            return false
        }

        if (!hasVerifiedHistorySnapshot.value) {
            return true
        }

        return false
    })
    const completedCount = computed(() => displayHistory.value.filter((trade) => trade.status === 'completed').length)
    const pendingCount = computed(() => displayHistory.value.filter((trade) => trade.status === 'pending').length)
    const cancelledCount = computed(() => displayHistory.value.filter((trade) => trade.status === 'cancelled').length)
    const totalAmount = computed(() => `¥${displayHistory.value.reduce((sum, trade) => sum + Number(trade.amount || 0), 0).toFixed(0)}`)
    const displayRequestId = computed(() => {
        if (showSummaryPlaceholders.value) {
            return 'N/A'
        }

        return lastVerifiedRequestId.value || 'N/A'
    })
    const displayProcessTime = computed(() => {
        if (showSummaryPlaceholders.value) {
            return 'N/A'
        }

        if (!lastVerifiedProcessTime.value) {
            return 'N/A'
        }

        const value = Number.parseFloat(lastVerifiedProcessTime.value)
        if (Number.isNaN(value)) {
            return lastVerifiedProcessTime.value
        }

        return `${value.toFixed(2)}ms`
    })
    const displayRowCount = computed(() => (showSummaryPlaceholders.value ? '--' : String(displayHistory.value.length)))
    const displayCompletedCount = computed(() => (showSummaryPlaceholders.value ? '--' : String(completedCount.value)))
    const displayPendingCount = computed(() => (showSummaryPlaceholders.value ? '--' : String(pendingCount.value)))
    const displayCancelledCount = computed(() => (showSummaryPlaceholders.value ? '--' : String(cancelledCount.value)))
    const displayTotalAmount = computed(() => (showSummaryPlaceholders.value ? '--' : totalAmount.value))
    const pageStatusText = computed(() => {
        if (staleError.value) return '刷新异常'
        if (error.value) return displayHistory.value.length > 0 ? '刷新异常' : '拉取失败'
        if (isLoadingState.value) return '同步中'
        return displayHistory.value.length > 0 ? '历史已加载' : '暂无历史'
    })
    const pageStatusType = computed(() => {
        if (staleError.value || error.value) return 'warning'
        if (pendingCount.value > 0) return 'warning'
        return displayHistory.value.length > 0 ? 'success' : 'info'
    })
    const runtimeMessage = computed(() => {
        if (staleError.value) {
            return `${staleError.value}，当前仍展示上次成功同步的交易历史记录。`
        }
        if (error.value) {
            return displayHistory.value.length > 0
                ? `${error.value}，当前仍展示上次成功同步的交易历史记录。`
                : `${error.value}，当前显示空历史状态。`
        }
        if (isLoadingState.value) return '交易历史同步中...'
        if (displayHistory.value.length === 0) return '暂无成交记录。'
        return ''
    })

    const loadHistory = async () => {
        staleError.value = null
        const responseData = await exec(() => apiClient.get('/v1/trade/trades'), { silent: true })
        if (!responseData) {
            if (hasVerifiedHistorySnapshot.value) {
                staleError.value = error.value || '交易历史接口失败'
            }
            hasLoaded.value = true
            return
        }
        internalHistory.value = toTradingHistoryRows(extractTradesPayload(responseData))
        hasVerifiedHistorySnapshot.value = true
        lastVerifiedRequestId.value = lastRequestId.value || lastVerifiedRequestId.value
        lastVerifiedProcessTime.value = lastProcessTime.value || lastVerifiedProcessTime.value
        hasLoaded.value = true
    }

    function formatSignedCurrency(value: number): string {
        return `¥${value}`
    }

    onMounted(() => {
        if (!Array.isArray(props.history) || props.history.length === 0) {
            void loadHistory()
        }
    })
</script>

<template>
    <div class="artdeco-trading-history" :class="{ 'is-embedded': isEmbedded }">
        <section v-if="!isEmbedded" class="hero-shell artdeco-card-shell">
            <div class="hero-rail">
                <div class="hero-copy">
                    <span class="hero-eyebrow">trade ledger desk</span>
                    <div class="hero-meta">
                        <span>REQ_ID: {{ displayRequestId }}</span>
                        <span>TIME: {{ displayProcessTime }}</span>
                        <span>ROWS: {{ displayRowCount }}</span>
                    </div>
                </div>
            </div>

            <ArtDecoHeader
                title="交易历史工作台"
                subtitle="统一查看历史成交、金额结构和订单状态，形成交易域的复盘入口"
                :show-status="true"
                :status-text="pageStatusText"
                :status-type="pageStatusType"
            >
                <template #actions>
                    <ArtDecoButton variant="outline" size="sm" :loading="effectiveLoading" @click="loadHistory">
                        <template #icon>
                            <ArtDecoIcon name="refresh" />
                        </template>
                        刷新历史
                    </ArtDecoButton>
                </template>
            </ArtDecoHeader>
        </section>

        <section v-if="!isEmbedded" class="stats-strip artdeco-card-shell">
            <ArtDecoStatCard label="总笔数" :value="displayRowCount" variant="gold" :show-change="false" />
            <ArtDecoStatCard label="已成交" :value="displayCompletedCount" variant="rise" :show-change="false" />
            <ArtDecoStatCard label="待成交" :value="displayPendingCount" variant="gold" :show-change="false" />
            <ArtDecoStatCard label="成交总额" :value="displayTotalAmount" variant="gold" :show-change="false" />
        </section>

        <section :class="isEmbedded ? 'embedded-shell' : 'content-shell artdeco-card-shell'">
            <div v-if="!isEmbedded" class="content-shell-header">
                <div class="content-shell-copy">
                    <span class="content-shell-kicker">historical execution route</span>
                    <h2 class="content-shell-title">成交记录与状态面板</h2>
                    <p class="content-shell-subtitle">从订单状态、成交金额到个股记录，形成完整的历史复盘工作流。</p>
                </div>
                <div class="content-shell-meta">
                    <span>COMPLETED: {{ displayCompletedCount }}</span>
                    <span>CANCELLED: {{ displayCancelledCount }}</span>
                </div>
            </div>

            <ArtDecoCard title="交易历史记录" hoverable>
                <div class="artdeco-trading-history__scroll-hint">移动端可横向滚动查看更多列。</div>
                <p v-if="runtimeMessage" class="artdeco-trading-history__status-message" aria-live="polite">{{ runtimeMessage }}</p>
                <div class="artdeco-trading-history__table" role="table" aria-label="交易历史表" :aria-busy="isLoadingState ? 'true' : 'false'">
                    <div class="artdeco-trading-history__header" role="rowgroup">
                        <div class="artdeco-trading-history__col artdeco-trading-history__col--time" role="columnheader">时间</div>
                        <div class="artdeco-trading-history__col artdeco-trading-history__col--symbol" role="columnheader">股票</div>
                        <div class="artdeco-trading-history__col artdeco-trading-history__col--type" role="columnheader">类型</div>
                        <div class="artdeco-trading-history__col artdeco-trading-history__col--price" role="columnheader">价格</div>
                        <div class="artdeco-trading-history__col artdeco-trading-history__col--quantity" role="columnheader">数量</div>
                        <div class="artdeco-trading-history__col artdeco-trading-history__col--amount" role="columnheader">金额</div>
                        <div class="artdeco-trading-history__col artdeco-trading-history__col--fee" role="columnheader">手续费</div>
                        <div class="artdeco-trading-history__col artdeco-trading-history__col--status" role="columnheader">状态</div>
                    </div>
                    <div v-if="error && displayHistory.length === 0" class="artdeco-trading-history__empty artdeco-trading-history__empty--error">
                        <p>交易历史拉取失败，当前无法展示真实记录。</p>
                        <ArtDecoButton variant="outline" size="sm" @click="loadHistory">
                            <template #icon>
                                <ArtDecoIcon name="refresh" />
                            </template>
                            重试
                        </ArtDecoButton>
                    </div>
                    <div v-else-if="displayHistory.length === 0" class="artdeco-trading-history__empty">
                        {{ isLoadingState ? '交易历史同步中...' : '暂无历史成交记录' }}
                    </div>
                    <div v-else class="artdeco-trading-history__body" role="rowgroup">
                        <div class="artdeco-trading-history__row" v-for="trade in displayHistory" :key="trade.id" role="row">
                            <div class="artdeco-trading-history__col artdeco-trading-history__col--time artdeco-trading-history__numeric" role="cell">
                                {{ trade.time }}
                            </div>
                            <div class="artdeco-trading-history__col artdeco-trading-history__col--symbol" role="cell">
                                <div class="artdeco-trading-history__symbol-name">{{ trade.symbolName }}</div>
                                <div class="artdeco-trading-history__symbol-code">{{ trade.symbol }}</div>
                            </div>
                            <div
                                class="artdeco-trading-history__col artdeco-trading-history__col--type"
                                :class="`artdeco-trading-history__type--${trade.type}`"
                                role="cell"
                            >
                                {{ trade.typeText }}
                            </div>
                            <div class="artdeco-trading-history__col artdeco-trading-history__col--price artdeco-trading-history__numeric" role="cell">
                                {{ formatSignedCurrency(trade.price) }}
                            </div>
                            <div class="artdeco-trading-history__col artdeco-trading-history__col--quantity artdeco-trading-history__numeric" role="cell">
                                {{ trade.quantity }}
                            </div>
                            <div class="artdeco-trading-history__col artdeco-trading-history__col--amount artdeco-trading-history__numeric" role="cell">
                                {{ formatSignedCurrency(trade.amount) }}
                            </div>
                            <div class="artdeco-trading-history__col artdeco-trading-history__col--fee artdeco-trading-history__numeric" role="cell">
                                {{ formatSignedCurrency(trade.fee) }}
                            </div>
                            <div
                                class="artdeco-trading-history__col artdeco-trading-history__col--status"
                                :class="`artdeco-trading-history__status--${trade.status}`"
                                role="cell"
                            >
                                {{ trade.statusText }}
                            </div>
                        </div>
                    </div>
                </div>
            </ArtDecoCard>
        </section>
    </div>
</template>

<style scoped lang="scss">
    @use '@/styles/artdeco-tokens.scss' as *;
    @use '@/styles/artdeco-patterns.scss' as *;

    .artdeco-trading-history {
        --artdeco-trading-history-col-time: calc(
            var(--artdeco-spacing-10) * 3 + var(--artdeco-spacing-5) + var(--artdeco-spacing-5) / 2
        );
        --artdeco-trading-history-col-symbol: calc(var(--artdeco-spacing-24) + var(--artdeco-spacing-6));
        --artdeco-trading-history-col-type: calc(
            var(--artdeco-spacing-10) + var(--artdeco-spacing-5) + var(--artdeco-spacing-5) / 2
        );
        --artdeco-trading-history-col-price: var(--artdeco-spacing-20);
        --artdeco-trading-history-col-amount: calc(var(--artdeco-spacing-20) + var(--artdeco-spacing-5));
        --artdeco-trading-history-table-width: calc(
            var(--artdeco-spacing-20) * 8 + var(--artdeco-spacing-24) + var(--artdeco-spacing-6)
        );
        --artdeco-trading-history-body-height: calc(var(--artdeco-spacing-20) * 5);
        --artdeco-trading-history-corner-size: var(--artdeco-spacing-4);
        --artdeco-trading-history-border-width: calc(var(--artdeco-spacing-1) / 2);
        position: relative;
        width: 100%;
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-6);

        @include artdeco-stepped-corners(var(--artdeco-spacing-2));
        @include artdeco-geometric-corners(
            $color: var(--artdeco-gold-primary),
            $size: var(--artdeco-trading-history-corner-size),
            $border-width: var(--artdeco-trading-history-border-width)
        );
        @include artdeco-hover-lift-glow;
    }

    .artdeco-trading-history.is-embedded {
        gap: var(--artdeco-spacing-4);
    }

    .hero-shell,
    .stats-strip,
    .content-shell,
    .embedded-shell {
        width: 100%;
    }

    .hero-shell,
    .content-shell {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-5);
    }

    .hero-rail,
    .content-shell-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: var(--artdeco-spacing-4);
        flex-wrap: wrap;
    }

    .hero-copy,
    .content-shell-copy {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-2);
    }

    .hero-eyebrow,
    .content-shell-kicker {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-xs);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wider);
        color: var(--artdeco-gold-dim);
    }

    .hero-meta,
    .content-shell-meta {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-3);
        flex-wrap: wrap;
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
    }

    .stats-strip {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: var(--artdeco-spacing-4);
    }

    .content-shell-title {
        margin: 0;
        font-family: var(--artdeco-font-display);
        font-size: var(--artdeco-text-xl);
        color: var(--artdeco-fg-primary);
    }

    .content-shell-subtitle {
        margin: 0;
        color: var(--artdeco-fg-muted);
        font-size: var(--artdeco-text-sm);
        line-height: var(--artdeco-leading-relaxed);
    }

    .artdeco-trading-history__table {
        width: 100%;
        overflow-x: auto;
    }

    .artdeco-trading-history__status-message,
    .artdeco-trading-history__scroll-hint {
        margin: 0 0 var(--artdeco-spacing-3);
        color: var(--artdeco-fg-muted);
        font-size: var(--artdeco-text-sm);
    }

    .artdeco-trading-history__scroll-hint {
        display: none;
    }

    .artdeco-trading-history__header {
        display: grid;
        grid-template-columns:
            var(--artdeco-trading-history-col-time)
            var(--artdeco-trading-history-col-symbol)
            var(--artdeco-trading-history-col-type)
            var(--artdeco-trading-history-col-price)
            var(--artdeco-trading-history-col-price)
            var(--artdeco-trading-history-col-amount)
            var(--artdeco-trading-history-col-price)
            var(--artdeco-trading-history-col-price);
        gap: var(--artdeco-spacing-2);
        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
        background: var(--artdeco-bg-elevated);
        border-bottom: 1px solid var(--artdeco-border-default);
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
        font-weight: 600;
        color: var(--artdeco-fg-muted);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
        min-width: var(--artdeco-trading-history-table-width);
    }

    .artdeco-trading-history__body {
        max-height: var(--artdeco-trading-history-body-height);
        overflow-y: auto;
    }

    .artdeco-trading-history__empty {
        padding: var(--artdeco-spacing-6);
        color: var(--artdeco-fg-muted);
        font-size: var(--artdeco-text-sm);
        text-align: center;
    }

    .artdeco-trading-history__empty--error {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--artdeco-spacing-3);
        color: var(--artdeco-warning);
    }

    .artdeco-trading-history__row {
        display: grid;
        grid-template-columns:
            var(--artdeco-trading-history-col-time)
            var(--artdeco-trading-history-col-symbol)
            var(--artdeco-trading-history-col-type)
            var(--artdeco-trading-history-col-price)
            var(--artdeco-trading-history-col-price)
            var(--artdeco-trading-history-col-amount)
            var(--artdeco-trading-history-col-price)
            var(--artdeco-trading-history-col-price);
        gap: var(--artdeco-spacing-2);
        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
        border-bottom: 1px solid var(--artdeco-border-default);
        align-items: center;
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-sm);
        min-width: var(--artdeco-trading-history-table-width);
        transition: all var(--artdeco-transition-base);

        &:hover {
            background: var(--artdeco-bg-elevated);
        }
    }

    .artdeco-trading-history__symbol-name {
        font-weight: 600;
        color: var(--artdeco-fg-primary);
    }

    .artdeco-trading-history__symbol-code {
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
    }

    .artdeco-trading-history__type--buy {
        color: var(--artdeco-up);
        font-weight: 600;
    }

    .artdeco-trading-history__type--sell {
        color: var(--artdeco-down);
        font-weight: 600;
    }

    .artdeco-trading-history__numeric {
        font-family: var(--artdeco-font-mono);
        font-variant-numeric: tabular-nums;
    }

    .artdeco-trading-history__status {
        font-weight: 600;
        padding: calc(var(--artdeco-spacing-1) / 2) var(--artdeco-spacing-2);
        font-size: var(--artdeco-text-xs);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);

        &.artdeco-trading-history__status--completed {
            background: color-mix(in srgb, var(--artdeco-up) 10%, transparent);
            color: var(--artdeco-up);
        }

        &.artdeco-trading-history__status--pending {
            background: color-mix(in srgb, var(--artdeco-gold-light) 10%, transparent);
            color: var(--artdeco-gold-primary);
        }

        &.artdeco-trading-history__status--cancelled {
            background: color-mix(in srgb, var(--artdeco-down) 10%, transparent);
            color: var(--artdeco-down);
        }
    }

    .artdeco-trading-history__corner {
        position: absolute;
        width: var(--artdeco-trading-history-corner-size);
        height: var(--artdeco-trading-history-corner-size);
        border-color: var(--artdeco-gold-primary);
        border-style: solid;
        opacity: 40%;
        transition: opacity var(--artdeco-transition-base);
        z-index: 1;
    }

    .artdeco-trading-history__corner--tl {
        top: calc(var(--artdeco-spacing-px) * -1);
        left: calc(var(--artdeco-spacing-px) * -1);
        border-width: var(--artdeco-trading-history-border-width) 0 0 var(--artdeco-trading-history-border-width);
    }

    .artdeco-trading-history__corner--br {
        bottom: calc(var(--artdeco-spacing-px) * -1);
        right: calc(var(--artdeco-spacing-px) * -1);
        border-width: 0 var(--artdeco-trading-history-border-width) var(--artdeco-trading-history-border-width) 0;
    }

    @media (width <= 75rem) {
        .stats-strip {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }

    @media (width <= 48rem) {
        .stats-strip {
            grid-template-columns: 1fr;
        }

        .hero-meta,
        .content-shell-meta {
            width: 100%;
        }

        .artdeco-trading-history__scroll-hint {
            display: block;
        }
    }
</style>
