<template>
    <div class="artdeco-test-page">
        <div class="container">
            <h1 class="page-title">🎭 MyStocks ArtDeco Design System</h1>
            <p class="page-subtitle">Art Deco风格量化交易界面测试</p>

            <!-- 统计卡片测试 -->
            <div class="test-section">
                <h2>📊 统计卡片 (Stat Cards)</h2>
                <div class="card-grid">
                    <ArtDecoStatCard
                        label="总资产"
                        :value="1256789.5"
                        change="2.5"
                        change-percent
                        description="较上日"
                        variant="gold"
                    />
                    <ArtDecoStatCard
                        label="当日盈亏"
                        :value="12567.89"
                        change="1.8"
                        change-percent
                        description="收益率"
                        variant="rise"
                    />
                    <ArtDecoStatCard
                        label="持仓成本"
                        :value="987654.32"
                        change="-0.5"
                        change-percent
                        description="成本控制"
                        variant="fall"
                    />
                </div>
            </div>

            <!-- 按钮测试 -->
            <div class="test-section">
                <h2>🔘 按钮组件 (Buttons)</h2>
                <div class="button-grid">
                    <ArtDecoButton>默认按钮</ArtDecoButton>
                    <ArtDecoButton variant="solid">实心按钮</ArtDecoButton>
                    <ArtDecoButton variant="outline">轮廓按钮</ArtDecoButton>
                    <ArtDecoButton variant="rise">买入</ArtDecoButton>
                    <ArtDecoButton variant="fall">卖出</ArtDecoButton>
                </div>
            </div>

            <!-- 表单控件测试 -->
            <div class="test-section">
                <h2>📝 表单控件 (Form Controls)</h2>
                <div class="form-grid">
                    <div class="form-item">
                        <label>股票代码</label>
                        <ArtDecoInput v-model="symbol" placeholder="输入股票代码，如: 600519" />
                    </div>
                    <div class="form-item">
                        <label>数量</label>
                        <ArtDecoInput v-model.number="quantity" type="number" placeholder="交易数量" />
                    </div>
                    <div class="form-item">
                        <label>选择周期</label>
                        <ArtDecoSelect v-model="period" :options="periodOptions" placeholder="选择时间周期" />
                    </div>
                </div>
            </div>

            <!-- 卡片布局测试 -->
            <div class="test-section">
                <h2>📄 卡片组件 (Cards)</h2>
                <div class="card-showcase">
                    <ArtDecoCard title="持仓信息" hoverable>
                        <div class="position-info">
                            <div class="position-item">
                                <span class="label">股票代码:</span>
                                <span class="value">600519</span>
                            </div>
                            <div class="position-item">
                                <span class="label">持仓数量:</span>
                                <span class="value">1000</span>
                            </div>
                            <div class="position-item">
                                <span class="label">成本价:</span>
                                <span class="value">¥125.50</span>
                            </div>
                            <div class="position-item">
                                <span class="label">市值:</span>
                                <span class="value">¥127,800.00</span>
                            </div>
                        </div>
                    </ArtDecoCard>

                    <ArtDecoCard title="交易记录" hoverable>
                        <div class="trade-records">
                            <div class="trade-item">
                                <span class="time">09:30:15</span>
                                <span class="action buy">买入</span>
                                <span class="symbol">600519</span>
                                <span class="quantity">500</span>
                                <span class="price">¥125.80</span>
                            </div>
                            <div class="trade-item">
                                <span class="time">14:25:30</span>
                                <span class="action sell">卖出</span>
                                <span class="symbol">000001</span>
                                <span class="quantity">200</span>
                                <span class="price">¥18.50</span>
                            </div>
                        </div>
                    </ArtDecoCard>
                </div>
            </div>

            <!-- 行情组件测试 -->
            <div class="test-section">
                <h2>📈 行情组件 (Market Components)</h2>
                <div class="market-grid">
                    <ArtDecoTicker
                        symbol="600519"
                        :price="125.8"
                        :change="2.5"
                        :change-percent="1.8"
                        :volume="1000000"
                    />

                    <ArtDecoTicker
                        symbol="000001"
                        :price="18.45"
                        :change="-0.8"
                        :change-percent="-0.5"
                        :volume="500000"
                    />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { ref } from 'vue'
    import {
        ArtDecoStatCard,
        ArtDecoButton,
        ArtDecoInput,
        ArtDecoSelect,
        ArtDecoCard,
        ArtDecoTicker
    } from '@/components/artdeco'

    // 响应式数据
    const symbol = ref('')
    const quantity = ref(100)
    const period = ref('')

    const periodOptions = [
        { label: '1分钟', value: '1m' },
        { label: '5分钟', value: '5m' },
        { label: '15分钟', value: '15m' },
        { label: '30分钟', value: '30m' },
        { label: '1小时', value: '1h' },
        { label: '日线', value: '1d' }
    ]
</script>

<style scoped lang="scss">
    .artdeco-test-page {
        min-height: 100vh;
        background: var(--artdeco-bg-global);
        color: var(--artdeco-fg-primary);
        padding: var(--artdeco-spacing-6);
    }

    .container {
        max-width: var(--artdeco-max-w-7xl);
        margin: 0 auto;
    }

    .page-title {
        font-family: var(--artdeco-font-display);
        font-size: var(--artdeco-text-5xl);
        font-weight: 700;
        color: var(--artdeco-gold-primary);
        text-align: center;
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-widest);
        margin-bottom: var(--artdeco-spacing-2);
    }

    .page-subtitle {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-lg);
        color: var(--artdeco-fg-muted);
        text-align: center;
        margin-bottom: var(--artdeco-spacing-8);
    }

    .test-section {
        margin-bottom: var(--artdeco-spacing-12);
        border-bottom: 1px solid rgba(212, 175, 55, 0.1);
        padding-bottom: var(--artdeco-spacing-8);

        &:last-child {
            border-bottom: none;
        }

        h2 {
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-3xl);
            font-weight: 600;
            color: var(--artdeco-gold-primary);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
            margin-bottom: var(--artdeco-spacing-6);
            display: flex;
            align-items: center;
            gap: var(--artdeco-spacing-3);
        }
    }

    .card-grid,
    .button-grid,
    .market-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: var(--artdeco-spacing-6);
        margin-bottom: var(--artdeco-spacing-8);
    }

    .form-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: var(--artdeco-spacing-6);
    }

    .form-item {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-3);

        label {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            font-weight: 600;
            color: var(--artdeco-gold-primary);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
        }
    }

    .card-showcase {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
        gap: var(--artdeco-spacing-6);
    }

    .position-info,
    .trade-records {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-3);
    }

    .position-item,
    .trade-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--artdeco-spacing-2) 0;
        border-bottom: 1px solid rgba(212, 175, 55, 0.1);

        &:last-child {
            border-bottom: none;
        }

        .label {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            color: var(--artdeco-fg-muted);
        }

        .value {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-base);
            font-weight: 600;
            color: var(--artdeco-fg-primary);
        }
    }

    .trade-item {
        .time {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-sm);
            color: var(--artdeco-fg-muted);
        }

        .action {
            padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
            border-radius: var(--artdeco-radius-none);
            font-size: var(--artdeco-text-xs);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);

            &.buy {
                background: rgba(255, 82, 82, 0.1);
                color: var(--artdeco-up);
            }

            &.sell {
                background: rgba(0, 230, 118, 0.1);
                color: var(--artdeco-down);
            }
        }

        .symbol {
            font-family: var(--artdeco-font-mono);
            font-weight: 600;
            color: var(--artdeco-gold-primary);
        }

        .quantity {
            font-family: var(--artdeco-font-mono);
            color: var(--artdeco-fg-primary);
        }

        .price {
            font-family: var(--artdeco-font-mono);
            font-weight: 600;
            color: var(--artdeco-fg-primary);
        }
    }

    // 响应式设计（仅支持桌面端，但保持基本的响应式布局）
    @media (max-width: 768px) {
        .container {
            padding: var(--artdeco-spacing-4);
        }

        .card-grid,
        .button-grid,
        .market-grid,
        .form-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
