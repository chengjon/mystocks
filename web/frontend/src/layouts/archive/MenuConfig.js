/**
 * MyStocks Web Frontend - Dynamic Menu Configuration
 * OpenSpec: implement-web-frontend-v2-navigation
 *
 * This file defines the menu configuration for Market and Stocks modules
 * with dynamic sidebar navigation system.
 */

export const MENU_CONFIG = {
    // Market Module Menu Configuration
    market: {
        title: '市场行情',
        icon: 'TrendCharts',
        items: [
            {
                key: 'realtime',
                title: '实时行情',
                icon: 'Monitor',
                path: '/market/realtime',
                description: '实时股票和指数行情监控'
            },
            {
                key: 'technical',
                title: '技术指标',
                icon: 'DataLine',
                path: '/market/technical',
                description: '实时技术指标计算和显示'
            },
            {
                key: 'tdx',
                title: '通达信接口',
                icon: 'Connection',
                path: '/market/tdx',
                description: '通达信数据源行情'
            },
            {
                key: 'capital-flow',
                title: '资金流向',
                icon: 'Money',
                path: '/market/capital-flow',
                description: '市场资金流向分析'
            },
            {
                key: 'etf',
                title: 'ETF行情',
                icon: 'TrendCharts',
                path: '/market/etf',
                description: 'ETF产品实时行情'
            },
            {
                key: 'concepts',
                title: '概念行情',
                icon: 'Box',
                path: '/market/concepts',
                description: '概念板块行情监控'
            },
            {
                key: 'auction',
                title: '竞价抢筹',
                icon: 'ShoppingCart',
                path: '/market/auction',
                description: '集合竞价阶段数据'
            },
            {
                key: 'lhb',
                title: '龙虎榜',
                icon: 'Flag',
                path: '/market/lhb',
                description: '龙虎榜数据分析'
            }
        ]
    },

    // Stocks Module Menu Configuration
    stocks: {
        title: '股票管理',
        icon: 'Grid',
        items: [
            {
                key: 'watchlist',
                title: '自选股管理',
                icon: 'Star',
                path: '/stocks/watchlist',
                description: '个人自选股列表管理'
            },
            {
                key: 'portfolio',
                title: '投资组合',
                icon: 'Folder',
                path: '/stocks/portfolio',
                description: '投资组合管理和分析'
            },
            {
                key: 'activity',
                title: '交易活动',
                icon: 'Tickets',
                path: '/stocks/activity',
                description: '交易记录和活动监控'
            },
            {
                key: 'screener',
                title: '股票筛选器',
                icon: 'Search',
                path: '/stocks/screener',
                description: '条件筛选股票工具'
            },
            {
                key: 'industry',
                title: '行业股票池',
                icon: 'Box',
                path: '/stocks/industry',
                description: '按行业分类的股票池'
            },
            {
                key: 'concept',
                title: '概念股票池',
                icon: 'Box',
                path: '/stocks/concept',
                description: '按概念分类的股票池'
            }
        ]
    }
}

/**
 * Get menu configuration for a specific module
 * @param {string} module - 'market' or 'stocks'
 * @returns {object} Menu configuration object
 */
export function getMenuConfig(module) {
    return MENU_CONFIG[module] || null
}

/**
 * Get all available modules
 * @returns {string[]} Array of module names
 */
export function getAvailableModules() {
    return Object.keys(MENU_CONFIG)
}

/**
 * Get menu item by module and key
 * @param {string} module - Module name
 * @param {string} key - Menu item key
 * @returns {object} Menu item object
 */
export function getMenuItem(module, key) {
    const config = getMenuConfig(module)
    if (!config) return null

    return config.items.find(item => item.key === key) || null
}
