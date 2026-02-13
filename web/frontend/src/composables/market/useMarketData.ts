import { ref } from 'vue'

export function useMarketData() {
    // Loading states
    type LoadingKeys = 'fundFlow' | 'etf' | 'concept' | 'longhub' | 'auction' | 'institutions' | 'wencai';
    const loading = ref<Record<LoadingKeys, boolean>>({
        fundFlow: false,
        etf: false,
        concept: false,
        longhub: false,
        auction: false,
        institutions: false,
        wencai: false
    })
    
    // State
    const activeTab = ref('fund-flow')
    const activeTimeFilter = ref('1day')
    const rankingType = ref('amount')
    const lhbDate = ref('today')
    const selectedConcept = ref(null)
    const lastUpdate = ref(new Date().toLocaleString())

    // Mock Data - Fund Flow
    const fundData = ref({
        shanghai: { amount: '28.6亿', change: 5.2 },
        shenzhen: { amount: '30.2亿', change: 8.9 },
        north: { amount: '58.8亿', change: 15.6 },
        main: { amount: '126.5亿', change: 68.0 }
    })

    const stockRanking = ref([
        { name: '贵州茅台', code: '600519', price: '1850.00', change: 2.1, inflow: '12.5', mainForce: '8.9' },
        { name: '宁德时代', code: '300750', price: '245.60', change: 3.5, inflow: '8.9', mainForce: '6.7' },
        { name: '中国石化', code: '600028', price: '4.85', change: -1.8, inflow: '-5.2', mainForce: '-3.1' },
        { name: '招商银行', code: '600036', price: '38.45', change: 1.2, inflow: '6.7', mainForce: '4.5' },
        { name: '万科A', code: '000002', price: '18.90', change: -0.9, inflow: '-3.1', mainForce: '-2.2' }
    ])

    // Mock Data - ETF
    const etfRanking = ref([
        { name: '沪深300ETF', code: '159919', type: '宽基指数', price: '3.456', change: 1.2, volume: '45.6' },
        { name: '创业板ETF', code: '159915', type: '行业主题', price: '2.189', change: -0.8, volume: '32.1' },
        { name: '半导体ETF', code: '159941', type: '行业主题', price: '0.856', change: 4.5, volume: '28.9' },
        { name: '新能源ETF', code: '159941', type: '行业主题', price: '0.723', change: 3.2, volume: '25.6' }
    ])

    // Mock Data - Concepts
    const conceptRanking = ref([
        { name: '人工智能', stockCount: 156, change: 3.2, heat: 85 },
        { name: '新能源汽车', stockCount: 98, change: 2.8, heat: 78 },
        { name: '半导体', stockCount: 87, change: -1.5, heat: 65 },
        { name: '医疗器械', stockCount: 134, change: 1.9, heat: 72 },
        { name: '云计算', stockCount: 76, change: 4.1, heat: 88 }
    ])

    // Mock Data - LHB
    const lhbData = ref([
        {
            name: 'N迈为股份',
            code: '300751',
            price: '456.78',
            change: 44.0,
            buyAmount: '8.9',
            sellAmount: '2.1',
            netBuy: '6.8'
        },
        {
            name: 'N爱德曼',
            code: '300751',
            price: '123.45',
            change: 123.0,
            buyAmount: '5.6',
            sellAmount: '1.2',
            netBuy: '4.4'
        },
        {
            name: 'N科创板',
            code: '300751',
            price: '89.12',
            change: 89.0,
            buyAmount: '4.3',
            sellAmount: '0.9',
            netBuy: '3.4'
        }
    ])

    // Mock Data - Auction
    const auctionData = ref([
        {
            name: 'N迈为股份',
            code: '300751',
            price: '456.78',
            change: 44.0,
            volume: '1234',
            amount: '5.6',
            robRate: 95
        },
        { name: 'N爱德曼', code: '300751', price: '123.45', change: 123.0, volume: '987', amount: '3.2', robRate: 88 },
        { name: 'N科创板', code: '300751', price: '89.12', change: 89.0, volume: '756', amount: '2.8', robRate: 82 }
    ])

    // Mock Data - Institutions
    const institutionData = ref({
        buyRating: { count: 156, percentage: 32.4 },
        holdRating: { count: 289, percentage: 60.1 },
        neutralRating: { count: 45, percentage: 9.4 },
        reduceRating: { count: 12, percentage: 2.5 },
        sellRating: { count: 5, percentage: 1.0 }
    })

    const latestRatings = ref([
        { stock: '600519', name: '贵州茅台', rating: '买入', institution: '中信证券', date: '2024-01-16', target: 1890 },
        { stock: '000001', name: '平安银行', rating: '增持', institution: '国泰君安', date: '2024-01-16', target: 12.8 },
        { stock: '300750', name: '宁德时代', rating: '买入', institution: '招商证券', date: '2024-01-15', target: 245 },
        { stock: '600036', name: '招商银行', rating: '中性', institution: '海通证券', date: '2024-01-15', target: 38.5 }
    ])

    // Wencai Logic
    const wencaiQuery = ref('')
    const wencaiLoading = ref(false)
    const wencaiResults = ref<Array<{
        code: string;
        name: string;
        price: string;
        change: string;
        volume: string;
        score: number;
    }>>([])
    const quickTags = ref([
        '涨停股', '创历史新高', '主力净流入', '北向资金买入',
        '技术指标金叉', '量能放大', '突破平台', '均线多头排列'
    ])

    // Actions
    const switchTab = (tabKey: string) => {
        activeTab.value = tabKey
    }

    const refreshData = () => {
        lastUpdate.value = new Date().toLocaleString()
        // Simulate refresh logic
        const tabKey = activeTab.value as LoadingKeys
        if (tabKey in loading.value) {
            loading.value[tabKey] = true
            setTimeout(() => {
                loading.value[tabKey] = false
            }, 1000)
        }
    }

    const handleSearch = () => {
        if (!wencaiQuery.value) return
        wencaiLoading.value = true
        setTimeout(() => {
            wencaiLoading.value = false
            // Mock results
            wencaiResults.value = [
                { code: '000001', name: '平安银行', price: '12.34', change: '1.2%', volume: '1.2亿', score: 98 },
                { code: '600519', name: '贵州茅台', price: '1850.00', change: '2.1%', volume: '0.5亿', score: 95 }
            ]
        }, 1000)
    }

    return {
        loading,
        activeTab,
        activeTimeFilter,
        rankingType,
        lhbDate,
        selectedConcept,
        lastUpdate,
        fundData,
        stockRanking,
        etfRanking,
        conceptRanking,
        lhbData,
        auctionData,
        institutionData,
        latestRatings,
        wencaiQuery,
        wencaiLoading,
        wencaiResults,
        quickTags,
        switchTab,
        refreshData,
        handleSearch
    }
}
