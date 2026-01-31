<template>
    <ArtDecoLayout>
        <div class="artdeco-trading-management">
            <div class="artdeco-page-header">
                <h1 class="artdeco-title">交易管理中心</h1>
                <p class="artdeco-subtitle">智能交易执行和订单管理</p>
            </div>

            <div class="artdeco-content-grid">
                <!-- 交易概览 -->
                <ArtDecoCard class="trading-overview-card">
                    <template #header>
                        <h3>交易概览</h3>
                    </template>
                    <div class="trading-metrics">
                        <ArtDecoStatCard
                            label="今日成交"
                            title="今日成交"
                            :value="'1,247'"
                            unit="笔"
                            :trend="0.15"
                            :status="'success'"
                        />
                        <ArtDecoStatCard
                            label="成交金额"
                            title="成交金额"
                            :value="'8.45M'"
                            unit="CNY"
                            :trend="0.08"
                            :status="'success'"
                        />
                        <ArtDecoStatCard
                            label="平均滑点"
                            :value="'0.12%'"
                            :change="-0.05"
                            description="交易执行平均滑点"
                            variant="fall"
                        />
                        <ArtDecoStatCard
                            label="执行成功率"
                            :value="'98.7%'"
                            :change="0.02"
                            description="订单执行成功率"
                            variant="rise"
                        />
                    </div>
                </ArtDecoCard>

                <!-- 活跃订单 -->
                <ArtDecoCard class="active-orders-card">
                    <template #header>
                        <h3>活跃订单</h3>
                    </template>
                    <ArtDecoTable :data="activeOrders" :columns="orderColumns" class="orders-table" />
                </ArtDecoCard>

                <!-- 交易历史 -->
                <ArtDecoCard class="trading-history-card">
                    <template #header>
                        <h3>交易历史</h3>
                    </template>
                    <ArtDecoTable :data="tradingHistory" :columns="historyColumns" class="history-table" />
                </ArtDecoCard>

                <!-- 交易控制面板 -->
                <ArtDecoCard class="trading-controls-card">
                    <template #header>
                        <h3>交易控制</h3>
                    </template>
                    <div class="control-panel">
                        <div class="control-group">
                            <h4>交易设置</h4>
                            <div class="control-item">
                                <label>最大单笔金额</label>
                                <ArtDecoInput
                                    v-model="maxOrderAmount"
                                    type="number"
                                    :min="1000"
                                    :max="10000000"
                                    step="1000"
                                    unit="CNY"
                                />
                            </div>
                            <div class="control-item">
                                <label>滑点限制</label>
                                <ArtDecoInput
                                    v-model="slippageLimit"
                                    type="number"
                                    :min="0"
                                    :max="10"
                                    step="0.01"
                                    unit="%"
                                />
                            </div>
                        </div>

                        <div class="control-group">
                            <h4>风控设置</h4>
                            <div class="control-item">
                                <label>每日交易限额</label>
                                <ArtDecoInput
                                    v-model="dailyTradingLimit"
                                    type="number"
                                    :min="10000"
                                    :max="100000000"
                                    step="10000"
                                    unit="CNY"
                                />
                            </div>
                            <div class="control-item">
                                <label>单股票持仓限额</label>
                                <ArtDecoInput
                                    v-model="singleStockLimit"
                                    type="number"
                                    :min="1"
                                    :max="100"
                                    step="1"
                                    unit="%"
                                />
                            </div>
                        </div>

                        <div class="control-actions">
                            <ArtDecoButton @click="updateTradingSettings" variant="default">更新设置</ArtDecoButton>
                            <ArtDecoButton @click="pauseTrading" :variant="tradingPaused ? 'rise' : 'fall'">
                                {{ tradingPaused ? '恢复交易' : '暂停交易' }}
                            </ArtDecoButton>
                        </div>
                    </div>
                </ArtDecoCard>
            </div>
        </div>
    </ArtDecoLayout>
</template>

<script setup lang="ts">
    import { ref, onMounted } from 'vue'
    import ArtDecoLayout from '@/layouts/ArtDecoLayout.vue'
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
    import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'
    import ArtDecoTable from '@/components/artdeco/trading/ArtDecoTable.vue'
    import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'
    import ArtDecoInput from '@/components/artdeco/base/ArtDecoInput.vue'

    // 交易设置
    const maxOrderAmount = ref(500000)
    const slippageLimit = ref(0.5)
    const dailyTradingLimit = ref(5000000)
    const singleStockLimit = ref(10)
    const tradingPaused = ref(false)

    // 活跃订单数据
    const activeOrders = ref([
        {
            id: 'ORD20250114001',
            symbol: '600519',
            name: '贵州茅台',
            side: '买入',
            quantity: 100,
            price: 1850.5,
            status: '部分成交',
            time: '14:32:15'
        },
        {
            id: 'ORD20250114002',
            symbol: '000002',
            name: '万科A',
            side: '卖出',
            quantity: 500,
            price: 18.65,
            status: '等待中',
            time: '14:28:42'
        },
        {
            id: 'ORD20250114003',
            symbol: '600036',
            name: '招商银行',
            side: '买入',
            quantity: 200,
            price: 38.9,
            status: '已成交',
            time: '14:25:18'
        }
    ])

    const orderColumns = ref([
        { key: 'id', label: '订单号', width: '140px' },
        { key: 'symbol', label: '代码', width: '80px' },
        { key: 'name', label: '名称', width: '100px' },
        { key: 'side', label: '方向', width: '60px' },
        { key: 'quantity', label: '数量', width: '80px' },
        { key: 'price', label: '价格', width: '80px' },
        { key: 'status', label: '状态', width: '80px' },
        { key: 'time', label: '时间', width: '80px' }
    ])

    // 交易历史数据
    const tradingHistory = ref([
        {
            time: '14:32:15',
            symbol: '600519',
            name: '贵州茅台',
            side: '买入',
            quantity: 50,
            price: 1850.5,
            amount: 92525.0,
            status: '成功'
        },
        {
            time: '14:28:42',
            symbol: '000858',
            name: '五粮液',
            side: '卖出',
            quantity: 100,
            price: 128.3,
            amount: 12830.0,
            status: '成功'
        },
        {
            time: '14:25:18',
            symbol: '600036',
            name: '招商银行',
            side: '买入',
            quantity: 200,
            price: 38.9,
            amount: 7780.0,
            status: '成功'
        },
        {
            time: '14:18:33',
            symbol: '000001',
            name: '平安银行',
            side: '买入',
            quantity: 300,
            price: 12.45,
            amount: 3735.0,
            status: '成功'
        },
        {
            time: '14:12:08',
            symbol: '600000',
            name: '浦发银行',
            side: '卖出',
            quantity: 400,
            price: 8.85,
            amount: 3540.0,
            status: '成功'
        }
    ])

    const historyColumns = ref([
        { key: 'time', label: '时间', width: '80px' },
        { key: 'symbol', label: '代码', width: '80px' },
        { key: 'name', label: '名称', width: '100px' },
        { key: 'side', label: '方向', width: '60px' },
        { key: 'quantity', label: '数量', width: '60px' },
        { key: 'price', label: '价格', width: '70px' },
        { key: 'amount', label: '金额', width: '90px' },
        { key: 'status', label: '状态', width: '60px' }
    ])

    const updateTradingSettings = () => {
        console.log('更新交易设置:', {
            maxOrderAmount: maxOrderAmount.value,
            slippageLimit: slippageLimit.value,
            dailyTradingLimit: dailyTradingLimit.value,
            singleStockLimit: singleStockLimit.value
        })
        // TODO: 实现交易设置更新逻辑
    }

    const pauseTrading = () => {
        tradingPaused.value = !tradingPaused.value
        console.log(tradingPaused.value ? '交易已暂停' : '交易已恢复')
        // TODO: 实现交易暂停/恢复逻辑
    }

    onMounted(() => {
        // TODO: 加载交易数据
    })
</script>

<style scoped>
    .artdeco-trading-management {
        padding: 2rem;
        max-width: 1400px;
        margin: 0 auto;
    }

    .artdeco-page-header {
        text-align: center;
        margin-bottom: 3rem;
    }

    .artdeco-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        background: linear-gradient(45deg, #ffd700, #ffa500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .artdeco-subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }

    .artdeco-content-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
        gap: 2rem;
    }

    .trading-overview-card {
        grid-column: 1 / -1;
    }

    .trading-metrics {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
    }

    .active-orders-card,
    .trading-history-card,
    .trading-controls-card {
        min-height: 400px;
    }

    .orders-table,
    .history-table {
        margin-top: 1rem;
    }

    .control-panel {
        display: flex;
        flex-direction: column;
        gap: 2rem;
    }

    .control-group {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .control-group h4 {
        margin: 0;
        font-size: 1.1rem;
        font-weight: bold;
        color: #333;
        border-bottom: 2px solid #ffd700;
        padding-bottom: 0.5rem;
    }

    .control-item {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .control-item label {
        font-weight: bold;
        color: #333;
        font-size: 0.9rem;
    }

    .control-actions {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin-top: 1rem;
    }

    @media (max-width: 768px) {
        .artdeco-trading-management {
            padding: 1rem;
        }

        .artdeco-content-grid {
            grid-template-columns: 1fr;
        }

        .trading-metrics {
            grid-template-columns: 1fr;
        }

        .control-actions {
            flex-direction: column;
            align-items: center;
        }
    }
</style>
