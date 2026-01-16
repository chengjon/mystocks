<template>
    <div class="artdeco-signal-monitoring-metrics">
        <!-- Corner decorations - Art Deco signature -->
        <div class="artdeco-signal-monitoring-metrics__corner artdeco-signal-monitoring-metrics__corner--tl"></div>
        <div class="artdeco-signal-monitoring-metrics__corner artdeco-signal-monitoring-metrics__corner--br"></div>

        <div class="artdeco-signal-monitoring-metrics__grid">
            <ArtDecoCard title="信号质量分析" hoverable>
                <div class="artdeco-signal-monitoring-metrics__quality">
                    <div class="artdeco-signal-monitoring-metrics__row">
                        <span class="artdeco-signal-monitoring-metrics__label">胜率 (胜/负)</span>
                        <span class="artdeco-signal-monitoring-metrics__value">
                            {{ quality.wins }}/{{ quality.losses }}
                        </span>
                    </div>
                    <div class="artdeco-signal-monitoring-metrics__row">
                        <span class="artdeco-signal-monitoring-metrics__label">平均盈利</span>
                        <span
                            class="artdeco-signal-monitoring-metrics__value artdeco-signal-monitoring-metrics__value--rise"
                        >
                            ¥{{ quality.avgProfit }}
                        </span>
                    </div>
                    <div class="artdeco-signal-monitoring-metrics__row">
                        <span class="artdeco-signal-monitoring-metrics__label">平均亏损</span>
                        <span
                            class="artdeco-signal-monitoring-metrics__value artdeco-signal-monitoring-metrics__value--fall"
                        >
                            ¥{{ quality.avgLoss }}
                        </span>
                    </div>
                    <div class="artdeco-signal-monitoring-metrics__row">
                        <span class="artdeco-signal-monitoring-metrics__label">盈亏比</span>
                        <span
                            class="artdeco-signal-monitoring-metrics__value artdeco-signal-monitoring-metrics__value--gold"
                        >
                            {{ quality.profitLossRatio }}
                        </span>
                    </div>
                    <div class="artdeco-signal-monitoring-metrics__row">
                        <span class="artdeco-signal-monitoring-metrics__label">最大连续盈利</span>
                        <span
                            class="artdeco-signal-monitoring-metrics__value artdeco-signal-monitoring-metrics__value--rise"
                        >
                            {{ quality.maxWinStreak }}
                        </span>
                    </div>
                    <div class="artdeco-signal-monitoring-metrics__row">
                        <span class="artdeco-signal-monitoring-metrics__label">最大连续亏损</span>
                        <span
                            class="artdeco-signal-monitoring-metrics__value artdeco-signal-monitoring-metrics__value--fall"
                        >
                            {{ quality.maxLossStreak }}
                        </span>
                    </div>
                </div>
            </ArtDecoCard>

            <ArtDecoCard title="信号类型分布" hoverable>
                <div class="artdeco-signal-monitoring-metrics__distribution">
                    <div class="artdeco-signal-monitoring-metrics__item" v-for="type in types" :key="type.name">
                        <div class="artdeco-signal-monitoring-metrics__type-info">
                            <div class="artdeco-signal-monitoring-metrics__type-name">{{ type.name }}</div>
                            <div class="artdeco-signal-monitoring-metrics__type-desc">{{ type.description }}</div>
                        </div>
                        <div class="artdeco-signal-monitoring-metrics__type-stats">
                            <div class="artdeco-signal-monitoring-metrics__type-count">{{ type.count }}</div>
                            <div class="artdeco-signal-monitoring-metrics__type-accuracy">{{ type.accuracy }}%</div>
                        </div>
                    </div>
                </div>
            </ArtDecoCard>
        </div>
    </div>
</template>

<script setup lang="ts">
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'

    export interface SignalQuality {
        wins: number
        losses: number
        avgProfit: number
        avgLoss: number
        profitLossRatio: string
        maxWinStreak: number
        maxLossStreak: number
    }

    export interface SignalType {
        name: string
        description: string
        count: number
        accuracy: number
    }

    defineProps<{
        quality: SignalQuality
        types: SignalType[]
    }>()
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';
    @import '@/styles/artdeco-patterns.scss';

    .artdeco-signal-monitoring-metrics {
        position: relative;
        width: 100%;
        margin-bottom: var(--artdeco-spacing-4);

        @include artdeco-stepped-corners(8px);

        @include artdeco-geometric-corners($color: var(--artdeco-gold-primary), $size: 16px, $border-width: 2px);

        @include artdeco-hover-lift-glow;
    }

    .artdeco-signal-monitoring-metrics__grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--artdeco-spacing-4);
        padding: var(--artdeco-spacing-4);

        @media (max-width: 900px) {
            grid-template-columns: 1fr;
        }
    }

    .artdeco-signal-monitoring-metrics__quality {
        .artdeco-signal-monitoring-metrics__row {
            display: flex;
            justify-content: space-between;
            padding: var(--artdeco-spacing-3) 0;
            border-bottom: 1px solid var(--artdeco-border-default);

            &:last-child {
                border-bottom: none;
            }
        }

        .artdeco-signal-monitoring-metrics__label {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            color: var(--artdeco-fg-muted);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
        }

        .artdeco-signal-monitoring-metrics__value {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-sm);
            font-weight: 600;
            color: var(--artdeco-fg-primary);

            &.artdeco-signal-monitoring-metrics__value--rise {
                color: var(--artdeco-up);
            }

            &.artdeco-signal-monitoring-metrics__value--fall {
                color: var(--artdeco-down);
            }

            &.artdeco-signal-monitoring-metrics__value--gold {
                color: var(--artdeco-gold-primary);
            }
        }
    }

    .artdeco-signal-monitoring-metrics__distribution {
        .artdeco-signal-monitoring-metrics__item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: var(--artdeco-spacing-3) 0;
            border-bottom: 1px solid var(--artdeco-border-default);

            &:last-child {
                border-bottom: none;
            }
        }

        .artdeco-signal-monitoring-metrics__type-name {
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-base);
            font-weight: 600;
            color: var(--artdeco-fg-primary);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
        }

        .artdeco-signal-monitoring-metrics__type-desc {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-xs);
            color: var(--artdeco-fg-muted);
            margin-top: 2px;
        }

        .artdeco-signal-monitoring-metrics__type-stats {
            text-align: right;
        }

        .artdeco-signal-monitoring-metrics__type-count {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-xl);
            font-weight: 700;
            color: var(--artdeco-gold-primary);
        }

        .artdeco-signal-monitoring-metrics__type-accuracy {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-xs);
            color: var(--artdeco-fg-muted);
        }
    }

    .artdeco-signal-monitoring-metrics__corner {
        position: absolute;
        width: 16px;
        height: 16px;
        border-color: var(--artdeco-gold-primary);
        border-style: solid;
        opacity: 0.4;
        transition: opacity var(--artdeco-transition-base);
        z-index: 1;
    }

    .artdeco-signal-monitoring-metrics__corner--tl {
        top: -1px;
        left: -1px;
        border-width: 2px 0 0 2px;
    }

    .artdeco-signal-monitoring-metrics__corner--br {
        bottom: -1px;
        right: -1px;
        border-width: 0 2px 2px 0;
    }
</style>
