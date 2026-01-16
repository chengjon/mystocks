<template>
    <div class="attribution-grid">
        <ArtDecoCard title="收益归因分析" hoverable class="attribution-chart-card">
            <div class="attribution-chart">
                <div class="chart-placeholder">
                    <div class="chart-title">收益来源分析</div>
                    <div class="attribution-items">
                        <div class="attribution-item" v-for="item in attributionData" :key="item.category">
                            <div class="category-name">{{ item.category }}</div>
                            <div class="category-value" :class="item.value >= 0 ? 'rise' : 'fall'">
                                {{ item.value >= 0 ? '+' : '' }}{{ item.value }}%
                            </div>
                            <div class="category-bar">
                                <div class="bar-fill" :style="{ width: Math.abs(item.value) * 5 + '%' }"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <ArtDecoCard title="关键交易分析" hoverable class="key-trades-card">
            <div class="key-trades-list">
                <div class="trade-analysis-item" v-for="trade in keyTrades" :key="trade.id">
                    <div class="trade-header">
                        <div class="trade-symbol">{{ trade.symbol }} {{ trade.name }}</div>
                        <div class="trade-type" :class="trade.type">{{ trade.typeText }}</div>
                    </div>
                    <div class="trade-details">
                        <div class="detail-item">
                            <span class="label">交易时间:</span>
                            <span class="value">{{ trade.time }}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">交易价格:</span>
                            <span class="value">¥{{ trade.price }}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">当前收益:</span>
                            <span class="value" :class="trade.currentPnL >= 0 ? 'rise' : 'fall'">
                                {{ trade.currentPnL >= 0 ? '+' : '' }}{{ trade.currentPnL }}%
                            </span>
                        </div>
                    </div>
                    <div class="trade-reason">
                        <div class="reason-label">交易理由:</div>
                        <div class="reason-text">{{ trade.reason }}</div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>
    </div>
</template>

<script setup lang="ts">
    import { ref } from 'vue'

    interface AttributionItem {
        category: string
        value: number
    }

    interface KeyTrade {
        id: number
        symbol: string
        name: string
        type: string
        typeText: string
        time: string
        price: number
        currentPnL: number
        reason: string
    }

    const attributionData = ref<AttributionItem[]>([
        { category: '选股收益', value: 8.5 },
        { category: '择时收益', value: 3.2 },
        { category: '行业配置', value: 2.1 },
        { category: '仓位管理', value: 1.5 },
        { category: '其他', value: 0.5 }
    ])

    const keyTrades = ref<KeyTrade[]>([
        {
            id: 1,
            symbol: '600519',
            name: '贵州茅台',
            type: 'buy',
            typeText: '买入',
            time: '2024-01-15 09:45:30',
            price: 1850.0,
            currentPnL: 12.5,
            reason: 'MA金叉+放量突破'
        },
        {
            id: 2,
            symbol: '300750',
            name: '宁德时代',
            type: 'buy',
            typeText: '买入',
            time: '2024-01-10 14:20:15',
            price: 238.0,
            currentPnL: 8.2,
            reason: 'RSI超卖+资金流入'
        }
    ])
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';
    @import '@/styles/artdeco-patterns.scss';

    .attribution-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--artdeco-spacing-4);
        position: relative;
        @include artdeco-geometric-corners(var(--artdeco-gold-primary), 16px, 2px);

        @media (max-width: 900px) {
            grid-template-columns: 1fr;
        }
    }

    .attribution-chart-card {
        .chart-placeholder {
            .chart-title {
                font-family: var(--artdeco-font-heading);
                font-size: var(--artdeco-text-base);
                font-weight: var(--artdeco-font-bold);
                margin-bottom: var(--artdeco-spacing-4);
                color: var(--artdeco-fg-primary);
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
            }

            .attribution-items {
                .attribution-item {
                    margin-bottom: var(--artdeco-spacing-3);

                    .category-name {
                        font-size: var(--artdeco-text-sm);
                        color: var(--artdeco-fg-muted);
                        margin-bottom: var(--artdeco-spacing-1);
                        text-transform: uppercase;
                        letter-spacing: var(--artdeco-tracking-wider);
                    }

                    .category-value {
                        font-family: var(--artdeco-font-mono);
                        font-size: var(--artdeco-text-lg);
                        font-weight: var(--artdeco-font-bold);
                        margin-bottom: var(--artdeco-spacing-2);

                        &.rise {
                            color: var(--artdeco-up);
                        }

                        &.fall {
                            color: var(--artdeco-down);
                        }
                    }

                    .category-bar {
                        height: 8px;
                        background: rgba(255, 255, 255, 0.1);
                        border-radius: var(--artdeco-radius-sm);
                        overflow: hidden;

                        .bar-fill {
                            height: 100%;
                            background: linear-gradient(90deg, var(--artdeco-gold-primary), var(--artdeco-gold-hover));
                            border-radius: var(--artdeco-radius-sm);
                            transition: width var(--artdeco-transition-base) var(--artdeco-ease-out);
                        }
                    }
                }
            }
        }
    }

    .key-trades-card {
        .key-trades-list {
            .trade-analysis-item {
                padding: var(--artdeco-spacing-3) 0;
                border-bottom: 1px solid var(--artdeco-border-default);

                &:last-child {
                    border-bottom: none;
                }

                .trade-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: var(--artdeco-spacing-2);

                    .trade-symbol {
                        font-weight: var(--artdeco-font-semibold);
                        color: var(--artdeco-fg-primary);
                    }

                    .trade-type {
                        padding: 2px 8px;
                        border-radius: var(--artdeco-radius-sm);
                        font-size: var(--artdeco-text-xs);
                        font-weight: var(--artdeco-font-bold);
                        text-transform: uppercase;
                        letter-spacing: var(--artdeco-tracking-wider);

                        &.buy {
                            background: rgba(255, 82, 82, 0.15);
                            color: var(--artdeco-up);
                        }

                        &.sell {
                            background: rgba(0, 230, 118, 0.15);
                            color: var(--artdeco-down);
                        }
                    }
                }

                .trade-details {
                    display: flex;
                    gap: var(--artdeco-spacing-4);
                    margin-bottom: var(--artdeco-spacing-2);

                    .detail-item {
                        .label {
                            font-size: var(--artdeco-text-xs);
                            color: var(--artdeco-fg-muted);
                            margin-right: var(--artdeco-spacing-1);
                            text-transform: uppercase;
                            letter-spacing: var(--artdeco-tracking-wide);
                        }

                        .value {
                            font-family: var(--artdeco-font-mono);
                            font-size: var(--artdeco-text-sm);
                            font-weight: var(--artdeco-font-medium);

                            &.rise {
                                color: var(--artdeco-down);
                            }

                            &.fall {
                                color: var(--artdeco-up);
                            }
                        }
                    }
                }

                .trade-reason {
                    .reason-label {
                        font-size: var(--artdeco-text-xs);
                        color: var(--artdeco-fg-muted);
                        margin-bottom: 2px;
                        text-transform: uppercase;
                        letter-spacing: var(--artdeco-tracking-wide);
                    }

                    .reason-text {
                        font-size: var(--artdeco-text-sm);
                        color: var(--artdeco-fg-muted);
                    }
                }
            }
        }
    }
</style>
