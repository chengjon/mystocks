<template>
    <div class="activity-container">
        <div class="page-header">
            <div class="header-title-section">
                <h1 class="page-title">
                    <el-icon><Tickets /></el-icon>
                    TRADING ACTIVITY
                </h1>
                <p class="page-subtitle">TRANSACTION HISTORY AND ACTIVITY MONITORING</p>
            </div>
            <div class="header-actions">
                <el-button type="primary" @click="refreshActivity">
                    <template #icon><RefreshRight /></template>
                    REFRESH ACTIVITY
                </el-button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ref, reactive, computed } from 'vue'
    import { ElCard, ElButton, ElTable, ElTableColumn, ElSelect, ElOption, ElTag, ElMessage } from 'element-plus'
    import { Tickets, RefreshRight } from '@element-plus/icons-vue'

    const activityFilter = ref('all')

    const activityStats = reactive({
        totalTrades: 1247,
        todayTrades: 23,
        totalVolume: 45000000,
        successRate: 98.5
    })

    const tradingActivities = ref([
        {
            timestamp: '2025-01-12 14:32:15',
            symbol: '000001',
            type: 'buy',
            quantity: 1000,
            price: 12.85,
            amount: 12850,
            status: 'completed'
        },
        {
            timestamp: '2025-01-12 14:28:42',
            symbol: '000002',
            type: 'sell',
            quantity: 500,
            price: 18.95,
            amount: 9475,
            status: 'completed'
        },
        {
            timestamp: '2025-01-12 11:15:33',
            symbol: '600036',
            type: 'buy',
            quantity: 200,
            price: 42.8,
            amount: 8560,
            status: 'completed'
        }
    ])

    const filteredActivities = computed(() => {
        // Simple filtering - in real app would filter by date ranges
        return tradingActivities.value
    })

    const refreshActivity = async () => {
        await new Promise(resolve => setTimeout(resolve, 500))
        ElMessage.success('Activity data refreshed')
    }

    const getStatusType = (status: string) => {
        switch (status) {
            case 'completed':
                return 'success'
            case 'pending':
                return 'warning'
            case 'failed':
                return 'danger'
            default:
                return 'info'
        }
    }

    const formatVolume = (volume: number) => {
        if (volume >= 100000000) return (volume / 100000000).toFixed(1) + '亿'
        if (volume >= 10000) return (volume / 10000).toFixed(1) + '万'
        return volume.toString()
    }
</script>

<style scoped lang="scss">
    @import '@/styles/theme-tokens.scss';

    .activity-container {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-lg);
        padding: var(--spacing-lg);
        background: var(--color-bg-primary);
        min-height: 100vh;
    }

    .page-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: var(--spacing-lg);
        border-bottom: 2px solid var(--color-border);

        .page-title {
            display: flex;
            align-items: center;
            gap: var(--spacing-md);
            font-family: var(--font-family-sans);
            font-size: var(--font-size-2xl);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            color: var(--color-accent);

            .el-icon {
                font-size: var(--font-size-3xl);
                color: var(--color-accent);
            }
        }

        .page-subtitle {
            font-family: var(--font-family-sans);
            font-size: var(--font-size-xs);
            color: var(--color-text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.2em;
            margin: var(--spacing-sm) 0 0 0;
        }
    }

    .activity-overview .overview-card :deep(.el-card__body) {
        padding: var(--spacing-lg);
    }
    .overview-stats {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: var(--spacing-lg);
    }
    .stat-item {
        text-align: center;
        padding: var(--spacing-md);
        background: var(--color-bg-secondary);
        border-radius: var(--border-radius-md);
    }
    .stat-label {
        display: block;
        font-size: var(--font-size-xs);
        color: var(--color-text-tertiary);
        margin-bottom: var(--spacing-xs);
    }
    .stat-value {
        font-size: var(--font-size-xl);
        font-weight: 700;
        color: var(--color-text-primary);
    }

    .activity-card :deep(.el-card__header) {
        padding: var(--spacing-md) var(--spacing-lg);
        border-bottom: 1px solid var(--color-border);
    }
    .card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .card-title {
        font-family: var(--font-family-sans);
        font-size: var(--font-size-sm);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--color-accent);
    }

    .activity-table :deep(.el-table__header th) {
        background: var(--color-bg-secondary);
    }

    @media (max-width: 768px) {
        .activity-container {
            padding: var(--spacing-md);
        }
        .overview-stats {
            grid-template-columns: 1fr;
        }
        .page-header {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--spacing-md);
        }
    }
</style>
