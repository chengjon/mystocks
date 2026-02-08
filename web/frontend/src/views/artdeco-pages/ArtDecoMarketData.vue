<template>
    <div class="artdeco-market-data">
        <!-- Page Header -->
        <div class="page-header">
            <div class="header-content">
                <h1 class="page-title">市场数据分析中心</h1>
                <p class="page-subtitle">深度分析市场资金动向，挖掘投资机会</p>
            </div>
            <div class="header-actions">
                <div class="time-display">
                    <span class="time-label">数据更新</span>
                    <span class="time-value">{{ lastUpdate }}</span>
                </div>
                <ArtDecoButton variant="outline" size="sm" @click="refreshData">刷新数据</ArtDecoButton>
            </div>
        </div>

        <!-- Navigation Tabs -->
        <nav class="main-tabs">
            <button
                v-for="tab in mainTabs"
                :key="tab.key"
                class="main-tab"
                :class="{ active: activeTab === tab.key }"
                @click="switchTab(tab.key)"
            >
                <span class="tab-icon">{{ tab.icon }}</span>
                <span class="tab-label">{{ tab.label }}</span>
                <span v-if="tab.badge" class="tab-badge">{{ tab.badge }}</span>
            </button>
        </nav>

        <!-- Tab Content -->
        <div class="tab-content">
            <div v-if="loading[activeTab]" class="loading-overlay">
                <div class="spinner"></div>
                <p>加载中...</p>
            </div>

            <template v-else>
                <!-- 资金流向 -->
                <MarketFundFlow 
                    v-if="activeTab === 'fund-flow'" 
                    :data="fundData" 
                />

                <!-- 概念板块 -->
                <MarketConcepts 
                    v-if="activeTab === 'concepts'" 
                    :data="conceptRanking" 
                />

                <!-- ETF分析 -->
                <MarketPlaceholder 
                    v-if="activeTab === 'etf'" 
                    title="ETF分析" 
                    :data="etfRanking" 
                />

                <!-- 龙虎榜 -->
                <MarketPlaceholder 
                    v-if="activeTab === 'lhb'" 
                    title="龙虎榜数据" 
                    :data="lhbData" 
                />

                <!-- 竞价抢筹 -->
                <MarketPlaceholder 
                    v-if="activeTab === 'auction'" 
                    title="竞价抢筹分析" 
                    :data="auctionData" 
                />

                <!-- 机构评级 -->
                <MarketPlaceholder 
                    v-if="activeTab === 'institutions'" 
                    title="机构评级分析" 
                    :data="{ stats: institutionData, list: latestRatings }" 
                />

                <!-- 问财搜索 -->
                <MarketPlaceholder 
                    v-if="activeTab === 'wencai'" 
                    title="问财智能搜索" 
                    :data="wencaiResults" 
                />
                
                <!-- 数据质量 (Was duplicated in original) -->
                <MarketPlaceholder 
                    v-if="activeTab === 'data-quality'" 
                    title="数据质量监控" 
                />
            </template>
        </div>
    </div>
</template>

<script setup>
import { ArtDecoButton } from '@/components/artdeco'
import { useMarketData } from '@/composables/market/useMarketData'

// Components
import MarketFundFlow from './components/MarketFundFlow.vue'
import MarketConcepts from './components/MarketConcepts.vue'
import MarketPlaceholder from './components/MarketPlaceholder.vue'

// Logic extracted to composable
const {
    loading,
    activeTab,
    lastUpdate,
    fundData,
    etfRanking,
    conceptRanking,
    lhbData,
    auctionData,
    institutionData,
    latestRatings,
    wencaiResults,
    switchTab,
    refreshData
} = useMarketData()

// Tabs Configuration
const mainTabs = [
    { key: 'data-quality', label: '数据质量', icon: '🛡️' },
    { key: 'fund-flow', label: '资金流向', icon: '💰' },
    { key: 'etf', label: 'ETF分析', icon: '🏷️' },
    { key: 'concepts', label: '概念板块', icon: '💡' },
    { key: 'lhb', label: '龙虎榜', icon: '🏆' },
    { key: 'auction', label: '竞价抢筹', icon: '⏰' },
    { key: 'institutions', label: '机构评级', icon: '🏢', badge: '新' },
    { key: 'wencai', label: '问财搜索', icon: '🔍' }
]
</script>

<style scoped>
.artdeco-market-data {
    padding: 20px;
    background: var(--artdeco-bg-primary);
    min-height: 100vh;
    color: var(--artdeco-text-primary);
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.page-title {
    font-size: 28px;
    font-weight: bold;
    background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}

.page-subtitle {
    color: var(--artdeco-text-secondary);
    font-size: 14px;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 20px;
}

.time-display {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
}

.time-label {
    font-size: 12px;
    color: var(--artdeco-text-secondary);
}

.time-value {
    font-family: 'JetBrains Mono', monospace;
    color: var(--artdeco-gold);
}

.main-tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 30px;
    background: rgba(255, 255, 255, 0.03);
    padding: 5px;
    border-radius: 12px;
    overflow-x: auto;
}

.main-tab {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 20px;
    background: transparent;
    border: none;
    color: var(--artdeco-text-secondary);
    cursor: pointer;
    border-radius: 8px;
    transition: all 0.3s ease;
    white-space: nowrap;
}

.main-tab.active {
    background: var(--artdeco-surface-hover);
    color: var(--artdeco-text-primary);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.tab-icon {
    font-size: 18px;
}

.tab-badge {
    background: #e74c3c;
    color: white;
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 10px;
    margin-left: 5px;
}

.loading-overlay {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 100px;
    color: var(--artdeco-text-secondary);
}

.spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(255, 255, 255, 0.1);
    border-radius: 50%;
    border-top-color: var(--artdeco-gold);
    animation: spin 1s linear infinite;
    margin-bottom: 15px;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}
</style>