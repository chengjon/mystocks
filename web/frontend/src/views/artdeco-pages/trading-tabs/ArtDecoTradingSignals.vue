<template>
    <div class="artdeco-trading-signals">
        <!-- Corner decorations - Art Deco signature -->
        <div class="artdeco-trading-signals__corner artdeco-trading-signals__corner--tl"></div>
        <div class="artdeco-trading-signals__corner artdeco-trading-signals__corner--br"></div>

        <ArtDecoCard title="实时交易信号" hoverable>
            <div class="artdeco-trading-signals__table" role="table" aria-label="实时交易信号表">
                <div class="artdeco-trading-signals__header" role="rowgroup">
                    <div class="artdeco-trading-signals__col artdeco-trading-signals__col--select" role="columnheader">选择</div>
                    <div class="artdeco-trading-signals__col artdeco-trading-signals__col--id" role="columnheader">信号ID</div>
                    <div class="artdeco-trading-signals__col artdeco-trading-signals__col--time" role="columnheader">时间</div>
                    <div class="artdeco-trading-signals__col artdeco-trading-signals__col--symbol" role="columnheader">股票</div>
                    <div class="artdeco-trading-signals__col artdeco-trading-signals__col--type" role="columnheader">类型</div>
                    <div class="artdeco-trading-signals__col artdeco-trading-signals__col--strength" role="columnheader">强度</div>
                    <div class="artdeco-trading-signals__col artdeco-trading-signals__col--price" role="columnheader">价格</div>
                    <div class="artdeco-trading-signals__col artdeco-trading-signals__col--reason" role="columnheader">来源 / 理由</div>
                    <div class="artdeco-trading-signals__col artdeco-trading-signals__col--confidence" role="columnheader">置信度</div>
                    <div class="artdeco-trading-signals__col artdeco-trading-signals__col--actions" role="columnheader">操作</div>
                </div>
                <div v-if="signals.length === 0" class="artdeco-trading-signals__empty">
                    暂无实时交易信号
                </div>
                <div v-else class="artdeco-trading-signals__body" role="rowgroup">
                    <div class="artdeco-trading-signals__row" v-for="signal in signals" :key="signal.rowKey" role="row">
                        <div class="artdeco-trading-signals__col artdeco-trading-signals__col--select" role="cell">
                            <input
                                v-model="signal.selected"
                                type="checkbox"
                                :disabled="!signal.executionReady"
                                :aria-label="`选择信号 ${signal.id} ${signal.symbolName}`"
                            />
                        </div>
                        <div class="artdeco-trading-signals__col artdeco-trading-signals__col--id artdeco-trading-signals__numeric" role="cell">{{ signal.displayId }}</div>
                        <div class="artdeco-trading-signals__col artdeco-trading-signals__col--time artdeco-trading-signals__numeric" role="cell">
                            {{ signal.time }}
                        </div>
                        <div class="artdeco-trading-signals__col artdeco-trading-signals__col--symbol" role="cell">
                            <div class="artdeco-trading-signals__symbol-name">{{ signal.symbolName }}</div>
                            <div class="artdeco-trading-signals__symbol-code">{{ signal.symbol }}</div>
                        </div>
                        <div
                            class="artdeco-trading-signals__col artdeco-trading-signals__col--type"
                            :class="`artdeco-trading-signals__type--${signal.type}`"
                            role="cell"
                        >
                            {{ signal.typeText }}
                        </div>
                        <div class="artdeco-trading-signals__col artdeco-trading-signals__col--strength" role="cell">
                            <span class="artdeco-trading-signals__strength-label">{{ signal.strengthLabel }}</span>
                        </div>
                        <div class="artdeco-trading-signals__col artdeco-trading-signals__col--price artdeco-trading-signals__numeric" role="cell">
                            ¥{{ signal.price }}
                        </div>
                        <div class="artdeco-trading-signals__col artdeco-trading-signals__col--reason" role="cell">
                            {{ signal.reason }}
                        </div>
                        <div class="artdeco-trading-signals__col artdeco-trading-signals__col--confidence artdeco-trading-signals__numeric" role="cell">
                            <div v-if="signal.confidenceValue !== null" class="artdeco-trading-signals__confidence-bar">
                                <div
                                    class="artdeco-trading-signals__confidence-fill"
                                    :style="{ width: signal.confidenceValue + '%' }"
                                ></div>
                                <span class="artdeco-trading-signals__confidence-text">{{ signal.confidenceLabel }}</span>
                            </div>
                            <span v-else class="artdeco-trading-signals__confidence-pending">{{ signal.confidenceLabel }}</span>
                        </div>
                        <div class="artdeco-trading-signals__col artdeco-trading-signals__col--actions" role="cell">
                            <ArtDecoButton
                                variant="solid"
                                size="sm"
                                :disabled="!signal.executionReady"
                                :class="`artdeco-trading-signals__button--${signal.type}`"
                                @click="emit('execute', signal)"
                            >
                                {{ signal.type === 'buy' ? '买入' : signal.type === 'sell' ? '卖出' : '观察' }}
                            </ArtDecoButton>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>
    </div>
</template>

<script setup lang="ts">
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
    import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'

    export interface TradingSignal {
        rowKey: string
        id?: string | null
        displayId: string
        selected?: boolean
        time: string
        symbol: string
        symbolName: string
        type: 'buy' | 'sell' | 'hold'
        typeText: string
        strengthLabel: string
        price: number
        reason: string
        confidenceValue: number | null
        confidenceLabel: string
        executionReady: boolean
    }

    defineProps<{
        signals: TradingSignal[]
    }>()

    const emit = defineEmits<{
        (e: 'execute', signal: TradingSignal): void
    }>()
</script>

<style scoped lang="scss">
    @use '@/styles/artdeco-tokens.scss' as *;
    @use '@/styles/artdeco-patterns.scss' as *;

    .artdeco-trading-signals {
        --artdeco-trading-signals-col-select: calc(var(--artdeco-spacing-10) + var(--artdeco-spacing-5));
        --artdeco-trading-signals-col-id: var(--artdeco-spacing-20);
        --artdeco-trading-signals-col-time: calc(
            var(--artdeco-spacing-24) + var(--artdeco-spacing-10) + var(--artdeco-spacing-3) + calc(var(--artdeco-spacing-1) / 2)
        );
        --artdeco-trading-signals-col-symbol: calc(var(--artdeco-spacing-24) + var(--artdeco-spacing-6));
        --artdeco-trading-signals-col-type: calc(
            var(--artdeco-spacing-16) + var(--artdeco-spacing-1) + calc(var(--artdeco-spacing-1) / 2)
        );
        --artdeco-trading-signals-col-strength: calc(var(--artdeco-spacing-20) + var(--artdeco-spacing-5));
        --artdeco-trading-signals-col-reason: calc(var(--artdeco-spacing-24) + var(--artdeco-spacing-6));
        --artdeco-trading-signals-table-width: calc(
            var(--artdeco-spacing-32) * 8 + var(--artdeco-spacing-16) + var(--artdeco-spacing-3)
        );
        --artdeco-trading-signals-body-height: calc(var(--artdeco-spacing-20) * 5);
        --artdeco-trading-signals-corner-size: var(--artdeco-spacing-4);
        --artdeco-trading-signals-border-width: calc(var(--artdeco-spacing-1) / 2);
        position: relative;
        width: 100%;

        // Art Deco signature: stepped corners
        @include artdeco-stepped-corners(var(--artdeco-spacing-2));

        // Geometric corner decorations
        @include artdeco-geometric-corners(
            $color: var(--artdeco-gold-primary),
            $size: var(--artdeco-trading-signals-corner-size),
            $border-width: var(--artdeco-trading-signals-border-width)
        );

        // Theatrical hover effect
        @include artdeco-hover-lift-glow;
    }

    .artdeco-trading-signals__table {
        width: 100%;
        overflow-x: auto;
    }

    .artdeco-trading-signals__header {
        display: grid;
        grid-template-columns:
            var(--artdeco-trading-signals-col-select)
            var(--artdeco-trading-signals-col-id)
            var(--artdeco-trading-signals-col-time)
            var(--artdeco-trading-signals-col-symbol)
            var(--artdeco-trading-signals-col-type)
            var(--artdeco-trading-signals-col-strength)
            var(--artdeco-trading-signals-col-id)
            var(--artdeco-trading-signals-col-reason)
            var(--artdeco-trading-signals-col-reason)
            var(--artdeco-trading-signals-col-strength);
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
        min-width: var(--artdeco-trading-signals-table-width);
    }

    .artdeco-trading-signals__body {
        max-height: var(--artdeco-trading-signals-body-height);
        overflow-y: auto;
    }

    .artdeco-trading-signals__empty {
        padding: var(--artdeco-spacing-6);
        color: var(--artdeco-fg-muted);
        font-size: var(--artdeco-text-sm);
        text-align: center;
    }

    .artdeco-trading-signals__row {
        display: grid;
        grid-template-columns:
            var(--artdeco-trading-signals-col-select)
            var(--artdeco-trading-signals-col-id)
            var(--artdeco-trading-signals-col-time)
            var(--artdeco-trading-signals-col-symbol)
            var(--artdeco-trading-signals-col-type)
            var(--artdeco-trading-signals-col-strength)
            var(--artdeco-trading-signals-col-id)
            var(--artdeco-trading-signals-col-reason)
            var(--artdeco-trading-signals-col-reason)
            var(--artdeco-trading-signals-col-strength);
        gap: var(--artdeco-spacing-2);
        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
        border-bottom: 1px solid var(--artdeco-border-default);
        align-items: center;
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-sm);
        min-width: var(--artdeco-trading-signals-table-width);
        transition: all var(--artdeco-transition-base);

        &:hover {
            background: var(--artdeco-bg-elevated);
        }
    }

    .artdeco-trading-signals__symbol-name {
        font-weight: 600;
        color: var(--artdeco-fg-primary);
    }

    .artdeco-trading-signals__symbol-code {
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
    }

    .artdeco-trading-signals__numeric {
        font-family: var(--artdeco-font-mono);
        font-variant-numeric: tabular-nums;
    }

    .artdeco-trading-signals__type--buy {
        color: var(--artdeco-up);
        font-weight: 600;
    }

    .artdeco-trading-signals__type--sell {
        color: var(--artdeco-down);
        font-weight: 600;
    }

    .artdeco-trading-signals__type--hold {
        color: var(--artdeco-gold-primary);
        font-weight: 600;
    }

    .artdeco-trading-signals__strength-label {
        font-family: var(--artdeco-font-mono);
        color: var(--artdeco-fg-primary);
    }

    .artdeco-trading-signals__confidence-bar {
        position: relative;
        width: 100%;
        height: var(--artdeco-spacing-5);
        background: var(--artdeco-bg-elevated);
        border-radius: var(--artdeco-radius-none);
        overflow: hidden;
    }

    .artdeco-trading-signals__confidence-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--artdeco-gold-primary), var(--artdeco-up));
        transition: width var(--artdeco-transition-base);
    }

    .artdeco-trading-signals__confidence-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-xs);
        font-weight: 600;
        color: var(--artdeco-fg-primary);
    }

    .artdeco-trading-signals__confidence-pending {
        color: var(--artdeco-fg-muted);
        font-size: var(--artdeco-text-xs);
    }

    .artdeco-trading-signals__button--buy {
        --button-bg: var(--artdeco-up);
        --button-color: white;
    }

    .artdeco-trading-signals__button--sell {
        --button-bg: var(--artdeco-down);
        --button-color: white;
    }

    .artdeco-trading-signals__button--hold {
        --button-bg: var(--artdeco-gold-dim);
        --button-color: var(--artdeco-fg-primary);
    }

    // Corner decorations
    .artdeco-trading-signals__corner {
        position: absolute;
        width: var(--artdeco-trading-signals-corner-size);
        height: var(--artdeco-trading-signals-corner-size);
        border-color: var(--artdeco-gold-primary);
        border-style: solid;
        opacity: 40%;
        transition: opacity var(--artdeco-transition-base);
        z-index: 1;
    }

    .artdeco-trading-signals__corner--tl {
        top: calc(var(--artdeco-spacing-px) * -1);
        left: calc(var(--artdeco-spacing-px) * -1);
        border-width: var(--artdeco-trading-signals-border-width) 0 0 var(--artdeco-trading-signals-border-width);
    }

    .artdeco-trading-signals__corner--br {
        bottom: calc(var(--artdeco-spacing-px) * -1);
        right: calc(var(--artdeco-spacing-px) * -1);
        border-width: 0 var(--artdeco-trading-signals-border-width) var(--artdeco-trading-signals-border-width) 0;
    }
</style>
