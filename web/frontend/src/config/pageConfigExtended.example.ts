/**
 * pageConfigExtended.example.ts
 *
 * 扩展配置示例 - 展示如何为PAGE_CONFIG添加新路由
 *
 * ⚠️ 这是一个示例文件，展示如何扩展统一配置
 * 实际使用时，应该将这些配置合并到 src/config/pageConfig.ts
 */

import { PAGE_CONFIG as BASE_PAGE_CONFIG } from './pageConfig'

/**
 * 扩展的路由配置 - 交易管理相关
 *
 * 这些配置展示了如何为特定业务领域（如交易管理）添加路由配置
 */
export const TRADING_ROUTES_CONFIG = {
  // 交易状态管理
  'trading-status': {
    apiEndpoint: '/api/trading/status',
    wsChannel: 'trading:status',
    realtime: true,
    description: '交易状态查询'
  },

  // 策略表现分析
  'trading-performance': {
    apiEndpoint: '/api/trading/strategies/performance',
    wsChannel: 'trading:performance',
    realtime: true,
    description: '策略表现分析'
  },

  // 交易市场快照
  'trading-market': {
    apiEndpoint: '/api/trading/market/snapshot',
    wsChannel: 'trading:market',
    realtime: true,
    description: '交易市场快照'
  },

  // 风险指标监控
  'trading-risk': {
    apiEndpoint: '/api/trading/risk/metrics',
    wsChannel: 'trading:risk',
    realtime: true,
    description: '交易风险指标'
  },

  // 策略管理
  'trading-strategies': {
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
 * const config = PAGE_CONFIG_EXTENDED['trading-status']
 * console.log(config.apiEndpoint)  // '/api/trading/status'
 *
 * // 方式2: 使用辅助函数
 * const config = getExtendedPageConfig('trading-status')
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
 * 1. **复制配置到 pageConfig.ts**:
 *    ```typescript
 *    // 在 src/config/pageConfig.ts 中添加
 *    export const PAGE_CONFIG = {
 *      // ... 现有8个路由
 *
 *      // 添加新路由
 *      'trading-status': {
 *        apiEndpoint: '/api/trading/status',
 *        wsChannel: 'trading:status',
 *        realtime: true,
 *        description: '交易状态查询'
 *      },
 *      // ... 其他4个交易路由
 *    } as const
 *    ```
 *
 * 2. **更新类型定义**:
 *    ```typescript
 *    // RouteName 类型会自动扩展
 *    export type RouteName = keyof typeof PAGE_CONFIG
 *    // 现在包含: 'trading-status', 'trading-performance', 等
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
 *    import { getPageConfig } from '@/config/pageConfigExtended.example'
 *
 *    // 改为
 *    import { getPageConfig } from '@/config/pageConfig'
 *    ```
 */
