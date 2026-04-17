/**
 * pageConfigExtended.example.ts
 *
 * 扩展配置示例 - 展示如何为聚合页添加局部 section 配置
 *
 * ⚠️ 这是一个示例文件，展示如何扩展统一配置
 * 当前仓库里 `/trade/terminal` 是聚合页，会组合调用多条 `/api/trading/*` 接口。
 * 示例中的 key 用于局部 section 管理，不代表真实路由名。
 */

import { PAGE_CONFIG as BASE_PAGE_CONFIG } from './pageConfig'

/**
 * 扩展的 section 配置 - 交易终端相关
 *
 * 这些配置展示了如何为聚合页的局部数据面板添加配置
 */
export const TRADING_ROUTES_CONFIG = {
  // 交易状态管理
  'trade-terminal-status': {
    apiEndpoint: '/api/trading/status',
    wsChannel: 'trading:status',
    realtime: true,
    description: '交易状态查询'
  },

  // 策略表现分析
  'trade-terminal-performance': {
    apiEndpoint: '/api/trading/strategies/performance',
    wsChannel: 'trading:performance',
    realtime: true,
    description: '策略表现分析'
  },

  // 交易市场快照
  'trade-terminal-market': {
    apiEndpoint: '/api/trading/market/snapshot',
    wsChannel: 'trading:market',
    realtime: true,
    description: '交易市场快照'
  },

  // 风险指标监控
  'trade-terminal-risk': {
    apiEndpoint: '/api/trading/risk/metrics',
    wsChannel: 'trading:risk',
    realtime: true,
    description: '交易风险指标'
  },

  // 策略管理
  'trade-terminal-strategies': {
    apiEndpoint: '/api/trading/strategies',
    wsChannel: 'trading:strategies',
    realtime: false,
    description: '交易策略管理'
  }
} as const

/**
 * 合并后的完整配置
 *
 * 展示如何将基础配置和扩展配置合并
 */
export const PAGE_CONFIG_EXTENDED = {
  ...BASE_PAGE_CONFIG,
  ...TRADING_ROUTES_CONFIG
} as const

/**
 * 扩展后的类型定义
 */
export type ExtendedRouteName = keyof typeof PAGE_CONFIG_EXTENDED
export type ExtendedPageConfig = typeof PAGE_CONFIG_EXTENDED[ExtendedRouteName]

/**
 * 验证扩展路由名称
 */
export function isValidExtendedRouteName(name: string): name is ExtendedRouteName {
  return name in PAGE_CONFIG_EXTENDED
}

/**
 * 获取扩展配置
 */
export function getExtendedPageConfig(routeName: string): ExtendedPageConfig | null {
  if (isValidExtendedRouteName(routeName)) {
    return PAGE_CONFIG_EXTENDED[routeName]
  }
  console.warn(`未配置的扩展路由: ${routeName}`)
  return null
}

/**
 * 使用示例：
 *
 * ```typescript
 * import { PAGE_CONFIG_EXTENDED, type ExtendedRouteName } from '@/config/pageConfigExtended.example'
 *
 * // 方式1: 直接访问配置
 * const config = PAGE_CONFIG_EXTENDED['trade-terminal-status']
 * console.log(config.apiEndpoint)  // '/api/trading/status'
 *
 * // 方式2: 使用辅助函数
 * const config = getExtendedPageConfig('trade-terminal-status')
 * if (config) {
 *   console.log(config.apiEndpoint)
 * }
 *
 * // 方式3: 类型安全的访问
 * function loadData(routeName: ExtendedRouteName) {
 *   const config = PAGE_CONFIG_EXTENDED[routeName]
 *   return axios.get(config.apiEndpoint)
 * }
 * ```
 */

/**
 * 迁移到生产环境的步骤：
 *
 * 1. **为聚合页建立 section 配置对象**:
 *    ```typescript
 *    const TRADE_TERMINAL_SECTION_CONFIG = {
 *      'trade-terminal-status': {
 *        apiEndpoint: '/api/trading/status',
 *        wsChannel: 'trading:status',
 *        realtime: true,
 *        description: '交易状态查询'
 *      },
 *      // ... 其他 section
 *    } as const
 *    ```
 *
 * 2. **更新局部类型定义**:
 *    ```typescript
 *    export type TradeTerminalSectionKey = keyof typeof TRADE_TERMINAL_SECTION_CONFIG
 *    // 现在包含: 'trade-terminal-status', 'trade-terminal-performance', 等
 *    ```
 *
 * 3. **删除示例文件**:
 *    ```bash
 *    rm src/config/pageConfigExtended.example.ts
 *    ```
 *
 * 4. **更新导入**:
 *    ```typescript
 *    // 从
 *    import { getExtendedPageConfig } from '@/config/pageConfigExtended.example'
 *
 *    // 改为
 *    import { getTradingConfig } from '@/views/examples/composables/useTradingDashboard.migrated'
 *    ```
 */
