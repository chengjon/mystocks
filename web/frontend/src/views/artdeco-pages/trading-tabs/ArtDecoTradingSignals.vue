<template>
    <div class="artdeco-trading-signals">
        <!-- Corner decorations - Art Deco signature -->
        <div class="artdeco-trading-signals__corner artdeco-trading-signals__corner--tl"></div>
        <div class="artdeco-trading-signals__corner artdeco-trading-signals__corner--br"></div>

        <ArtDecoCard title="实时交易信号" hoverable>
            <div class="artdeco-trading-signals__table">
                <div class="artdeco-trading-signals__header">
                    <div class="artdeco-trading-signals__col artdeco-trading-signals__col--select">选择</div>
                    <div class="artdeco-trading-signals__col artdeco-trading-signals__col--id">信号ID</div>
                    <div class="artdeco-trading-signals__col artdeco-trading-signals__col--time">时间</div>
                    <div class="artdeco-trading-signals__col artdeco-trading-signals__col--symbol">股票</div>
                    <div class="artdeco-trading-signals__col artdeco-trading-signals__col--type">类型</div>
                    <div class="artdeco-trading-signals__col artdeco-trading-signals__col--strength">强度</div>
                    <div class="artdeco-trading-signals__col artdeco-trading-signals__col--price">价格</div>
                    <div class="artdeco-trading-signals__col artdeco-trading-signals__col--reason">理由</div>
                    <div class="artdeco-trading-signals__col artdeco-trading-signals__col--confidence">置信度</div>
                    <div class="artdeco-trading-signals__col artdeco-trading-signals__col--actions">操作</div>
                </div>
                <div class="artdeco-trading-signals__body">
                    <div class="artdeco-trading-signals__row" v-for="signal in signals" :key="signal.id">
                        <div class="artdeco-trading-signals__col artdeco-trading-signals__col--select">
                            <input type="checkbox" v-model="signal.selected" />
                        </div>
                        <div class="artdeco-trading-signals__col artdeco-trading-signals__col--id">{{ signal.id }}</div>
                        <div class="artdeco-trading-signals__col artdeco-trading-signals__col--time">
                            {{ signal.time }}
                        </div>
                        <div class="artdeco-trading-signals__col artdeco-trading-signals__col--symbol">
                            <div class="artdeco-trading-signals__symbol-name">{{ signal.symbolName }}</div>
                            <div class="artdeco-trading-signals__symbol-code">{{ signal.symbol }}</div>
                        </div>
                        <div
                            class="artdeco-trading-signals__col artdeco-trading-signals__col--type"
                            :class="`artdeco-trading-signals__type--${signal.type}`"
                        >
                            {{ signal.typeText }}
                        </div>
                        <div class="artdeco-trading-signals__col artdeco-trading-signals__col--strength">
                            <div class="artdeco-trading-signals__strength">
                                <span
                                    v-for="i in 5"
                                    :key="i"
                                    class="artdeco-trading-signals__star"
                                    :class="{ 'artdeco-trading-signals__star--filled': i <= signal.strength }"
                                >
                                    ★
                                </span>
                            </div>
                        </div>
                        <div class="artdeco-trading-signals__col artdeco-trading-signals__col--price">
                            ¥{{ signal.price }}
                        </div>
                        <div class="artdeco-trading-signals__col artdeco-trading-signals__col--reason">
                            {{ signal.reason }}
                        </div>
                        <div class="artdeco-trading-signals__col artdeco-trading-signals__col--confidence">
                            <div class="artdeco-trading-signals__confidence-bar">
                                <div
                                    class="artdeco-trading-signals__confidence-fill"
                                    :style="{ width: signal.confidence + '%' }"
                                ></div>
                                <span class="artdeco-trading-signals__confidence-text">{{ signal.confidence }}%</span>
                            </div>
                        </div>
                        <div class="artdeco-trading-signals__col artdeco-trading-signals__col--actions">
                            <ArtDecoButton
                                variant="solid"
                                size="sm"
                                :class="`artdeco-trading-signals__button--${signal.type}`"
                            >
                                {{ signal.type === 'buy' ? '买入' : '卖出' }}
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
        id: number
        selected?: boolean
        time: string
        symbol: string
        symbolName: string
        type: 'buy' | 'sell'
        typeText: string
        strength: number
        price: number
        reason: string
        confidence: number
    }

    defineProps<{
        signals: TradingSignal[]
    }>()
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';
    @import '@/styles/artdeco-patterns.scss';

    .artdeco-trading-signals {
        position: relative;
        width: 100%;

        // Art Deco signature: stepped corners
        @include artdeco-stepped-corners(8px);

        // Geometric corner decorations
        @include artdeco-geometric-corners($color: var(--artdeco-gold-primary), $size: 16px, $border-width: 2px);

        // Theatrical hover effect
        @include artdeco-hover-lift-glow;
    }

    .artdeco-trading-signals__table {
        width: 100%;
        overflow-x: auto;
    }

    .artdeco-trading-signals__header {
        display: grid;
        grid-template-columns: 60px 80px 150px 120px 70px 100px 80px 120px 120px 100px;
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
        min-width: 1100px;
    }

    .artdeco-trading-signals__body {
        max-height: 400px;
        overflow-y: auto;
    }

    .artdeco-trading-signals__row {
        display: grid;
        grid-template-columns: 60px 80px 150px 120px 70px 100px 80px 120px 120px 100px;
        gap: var(--artdeco-spacing-2);
        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
        border-bottom: 1px solid var(--artdeco-border-default);
        align-items: center;
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-sm);
        min-width: 1100px;
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

    .artdeco-trading-signals__type--buy {
        color: var(--artdeco-up);
        font-weight: 600;
    }

    .artdeco-trading-signals__type--sell {
        color: var(--artdeco-down);
        font-weight: 600;
    }

    .artdeco-trading-signals__strength {
        display: flex;
        gap: 2px;
    }

    .artdeco-trading-signals__star {
        color: var(--artdeco-fg-muted);
        font-size: var(--artdeco-text-xs);

        &.artdeco-trading-signals__star--filled {
            color: var(--artdeco-gold-primary);
        }
    }

    .artdeco-trading-signals__confidence-bar {
        position: relative;
        width: 100%;
        height: 20px;
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

    .artdeco-trading-signals__button--buy {
        --button-bg: var(--artdeco-up);
        --button-color: white;
    }

    .artdeco-trading-signals__button--sell {
        --button-bg: var(--artdeco-down);
        --button-color: white;
    }

    // Corner decorations
    .artdeco-trading-signals__corner {
        position: absolute;
        width: 16px;
        height: 16px;
        border-color: var(--artdeco-gold-primary);
        border-style: solid;
        opacity: 0.4;
        transition: opacity var(--artdeco-transition-base);
        z-index: 1;
    }

    .artdeco-trading-signals__corner--tl {
        top: -1px;
        left: -1px;
        border-width: 2px 0 0 2px;
    }

    .artdeco-trading-signals__corner--br {
        bottom: -1px;
        right: -1px;
        border-width: 0 2px 2px 0;
    }
</style>
