#!/usr/bin/env node
/**
 * Batch Page Configuration Generator
 * 
 * This script parses the router configuration and generates page configurations
 * for all routes, including API endpoints and WebSocket channels.
 * 
 * Usage:
 *   node scripts/dev/tools/generate-page-config.js [options]
 *   npm run generate-page-config -- [options]
 * 
 * Options:
 *   --dry-run    Show what would be generated without writing files
 *   --diff       Show diff between current and generated config
 *   --verbose    Show detailed output
 *   --help       Show this help message
 */

const fs = require('fs')
const path = require('path')

// ============================================================================
// Configuration
// ============================================================================

const CONFIG = {
  routerPath: path.resolve(__dirname, '../../../web/frontend/src/router/index.ts'),
  configOutputPath: path.resolve(__dirname, '../../../web/frontend/src/config/pageConfig.ts'),
  configBackupPath: path.resolve(__dirname, '../../../web/frontend/src/config/pageConfig.ts.bak'),
  
  routeConfigMap: {
    'dashboard': { apiEndpoint: '/api/dashboard/overview', wsChannel: 'dashboard:realtime', description: '仪表盘概览' },
    'market-realtime': { apiEndpoint: '/api/market/realtime', wsChannel: 'market:realtime', description: '实时行情' },
    'market-technical': { apiEndpoint: '/api/technical/indicators', wsChannel: 'market:technical', description: '技术指标' },
    'market-fund-flow': { apiEndpoint: '/api/market/fund-flow', wsChannel: 'market:fund-flow', description: '资金流向' },
    'market-etf': { apiEndpoint: '/api/market/etf', wsChannel: 'market:etf', description: 'ETF行情' },
    'market-concept': { apiEndpoint: '/api/market/concept', wsChannel: 'market:concept', description: '概念板块' },
    'market-auction': { apiEndpoint: '/api/market/auction', wsChannel: 'market:auction', description: '竞价抢筹' },
    'market-longhubang': { apiEndpoint: '/api/market/longhubang', wsChannel: 'market:longhubang', description: '龙虎榜' },
    'market-institution': { apiEndpoint: '/api/market/institution', wsChannel: 'market:institution', description: '机构荐股' },
    'market-wencai': { apiEndpoint: '/api/market/wencai', wsChannel: 'market:wencai', description: '问财选股' },
    'market-screener': { apiEndpoint: '/api/market/screener', wsChannel: 'market:screener', description: '股票筛选' },
    'stock-management': { apiEndpoint: '/api/stock/management', wsChannel: 'stock:management', description: '股票管理' },
    'stock-portfolio': { apiEndpoint: '/api/stock/portfolio', wsChannel: 'stock:portfolio', description: '我的持仓' },
    'trading-signals': { apiEndpoint: '/api/trading/signals', wsChannel: 'trading:signals', description: '交易信号' },
    'trading-history': { apiEndpoint: '/api/trading/history', wsChannel: 'trading:history', description: '历史订单' },
    'trading-positions': { apiEndpoint: '/api/trading/positions', wsChannel: 'trading:positions', description: '持仓监控' },
    'trading-attribution': { apiEndpoint: '/api/trading/attribution', wsChannel: 'trading:attribution', description: '绩效归因' },
    'strategy-design': { apiEndpoint: '/api/strategy/design', wsChannel: 'strategy:design', description: '策略设计' },
    'strategy-management': { apiEndpoint: '/api/strategy/management', wsChannel: 'strategy:management', description: '策略管理' },
    'strategy-backtest': { apiEndpoint: '/api/strategy/backtest', wsChannel: 'strategy:backtest', description: '策略回测' },
    'strategy-gpu-backtest': { apiEndpoint: '/api/strategy/gpu-backtest', wsChannel: 'strategy:gpu-backtest', description: 'GPU加速回测' },
    'strategy-optimization': { apiEndpoint: '/api/strategy/optimization', wsChannel: 'strategy:optimization', description: '参数优化' },
    'risk-overview': { apiEndpoint: '/api/risk/overview', wsChannel: 'risk:overview', description: '风险概览' },
    'risk-alerts': { apiEndpoint: '/api/risk/alerts', wsChannel: 'risk:alerts', description: '告警中心' },
    'risk-indicators': { apiEndpoint: '/api/risk/indicators', wsChannel: 'risk:indicators', description: '风险指标' },
    'risk-sentiment': { apiEndpoint: '/api/risk/sentiment', wsChannel: 'risk:sentiment', description: '舆情监控' },
    'risk-announcement': { apiEndpoint: '/api/risk/announcement', wsChannel: 'risk:announcement', description: '公告监控' },
    'system-monitoring': { apiEndpoint: '/api/system/monitoring', wsChannel: 'system:monitoring', description: '运维监控' },
    'system-settings': { apiEndpoint: '/api/system/settings', wsChannel: 'system:settings', description: '系统设置' },
    'system-data-update': { apiEndpoint: '/api/system/data-update', wsChannel: 'system:data-update', description: '数据更新' },
    'system-data-quality': { apiEndpoint: '/api/system/data-quality', wsChannel: 'system:data-quality', description: '数据质量' },
    'system-api-health': { apiEndpoint: '/api/system/api-health', wsChannel: 'system:api-health', description: 'API健康' },
  },
  
  monolithicTabs: {
    'ArtDecoMarketData.vue': [
      { id: 'fund-flow', apiEndpoint: '/api/market/fund-flow', wsChannel: 'market:fund-flow' },
      { id: 'etf', apiEndpoint: '/api/market/etf', wsChannel: 'market:etf' },
      { id: 'concepts', apiEndpoint: '/api/market/concept', wsChannel: 'market:concept' },
      { id: 'lhb', apiEndpoint: '/api/market/longhubang', wsChannel: 'market:longhubang' },
      { id: 'auction', apiEndpoint: '/api/market/auction', wsChannel: 'market:auction' },
      { id: 'institution', apiEndpoint: '/api/market/institution', wsChannel: 'market:institution' },
    ],
    'ArtDecoStockManagement.vue': [
      { id: 'overview', apiEndpoint: '/api/stock/overview', wsChannel: 'stock:overview' },
      { id: 'watchlist', apiEndpoint: '/api/stock/watchlist', wsChannel: 'stock:watchlist' },
      { id: 'positions', apiEndpoint: '/api/stock/positions', wsChannel: 'stock:positions' },
      { id: 'attribution', apiEndpoint: '/api/trading/attribution', wsChannel: 'trading:attribution' },
      { id: 'history', apiEndpoint: '/api/trading/history', wsChannel: 'trading:history' },
      { id: 'strategy', apiEndpoint: '/api/strategy/management', wsChannel: 'strategy:management' },
    ],
    'ArtDecoTradingManagement.vue': [
      { id: 'overview', apiEndpoint: '/api/trading/overview', wsChannel: 'trading:overview' },
      { id: 'signals', apiEndpoint: '/api/trading/signals', wsChannel: 'trading:signals' },
      { id: 'positions', apiEndpoint: '/api/trading/positions', wsChannel: 'trading:positions' },
      { id: 'history', apiEndpoint: '/api/trading/history', wsChannel: 'trading:history' },
      { id: 'attribution', apiEndpoint: '/api/trading/attribution', wsChannel: 'trading:attribution' },
    ],
    'ArtDecoTechnicalAnalysis.vue': [
      { id: 'analysis', apiEndpoint: '/api/technical/indicators', wsChannel: 'technical:indicators' },
      { id: 'backtest', apiEndpoint: '/api/strategy/backtest', wsChannel: 'strategy:backtest' },
      { id: 'optimization', apiEndpoint: '/api/strategy/optimization', wsChannel: 'strategy:optimization' },
    ],
    'ArtDecoRiskManagement.vue': [
      { id: 'overview', apiEndpoint: '/api/risk/overview', wsChannel: 'risk:overview' },
      { id: 'alerts', apiEndpoint: '/api/risk/alerts', wsChannel: 'risk:alerts' },
      { id: 'indicators', apiEndpoint: '/api/risk/indicators', wsChannel: 'risk:indicators' },
      { id: 'sentiment', apiEndpoint: '/api/risk/sentiment', wsChannel: 'risk:sentiment' },
      { id: 'announcement', apiEndpoint: '/api/risk/announcement', wsChannel: 'risk:announcement' },
    ],
  }
}

// ============================================================================
// Utility Functions
// ============================================================================

function log(message, verbose = false) {
  if (verbose) {
    console.log(message)
  }
}

function parseRouterFile(filePath) {
  const routes = []
  
  try {
    const content = fs.readFileSync(filePath, 'utf-8')
    
    const routeBlockRegex = /path:\s*['"]([^'"]+)['"]\s*,\s*name:\s*['"]([^'"]+)['"]\s*,\s*component:\s*\(\)\s*=>\s*import\(['"]@\/views\/([^'"]+)['"]\)/g
    
    let match
    while ((match = routeBlockRegex.exec(content)) !== null) {
      const routePath = match[1]
      const routeName = match[2]
      const componentPath = match[3]
      const component = componentPath.split('/').pop()
      
      if (routeName === 'notFound' || routeName === 'login' || routeName === 'test' || routeName === 'artdeco-test') {
        continue
      }
      
      const routeEndIndex = content.indexOf('}', match.index)
      const routeBlock = content.substring(match.index, routeEndIndex + 1)
      
      let title = ''
      let requiresAuth = true
      let activeTab = ''
      let description = ''
      
      const titleMatch = routeBlock.match(/title:\s*['"]([^'"]+)['"]/)
      if (titleMatch) title = titleMatch[1]
      
      const authMatch = routeBlock.match(/requiresAuth:\s*(true|false)/)
      if (authMatch) requiresAuth = authMatch[1] === 'true'
      
      const tabMatch = routeBlock.match(/activeTab:\s*['"]([^'"]+)['"]/)
      if (tabMatch) activeTab = tabMatch[1]
      
      routes.push({
        path: routePath,
        name: routeName,
        component,
        meta: { title, requiresAuth, activeTab, description }
      })
    }
    
    return routes
  } catch (error) {
    throw new Error(`Failed to parse router file: ${error}`)
  }
}

function inferConfig(route) {
  if (CONFIG.routeConfigMap[route.name]) {
    return CONFIG.routeConfigMap[route.name]
  }
  
  const nameParts = route.name.split('-')
  const domain = nameParts[0]
  const subPath = nameParts.slice(1).join('/')
  
  let apiEndpoint = `/api/${domain}/${subPath}`
  if (subPath === domain) {
    apiEndpoint = `/api/${domain}`
  }
  
  let wsChannel = `${domain}:${subPath}`
  if (subPath === domain) {
    wsChannel = domain
  }
  
  return { apiEndpoint, wsChannel, description: route.meta.title || route.name }
}

function getMonolithicTabs(component) {
  const componentName = component.split('/').pop() || component
  return CONFIG.monolithicTabs[componentName] || []
}

function isMonolithicComponent(component) {
  const componentName = component.split('/').pop() || component
  return componentName in CONFIG.monolithicTabs
}

function generatePageConfig(routes) {
  const configs = []
  
  for (const route of routes) {
    const inferred = inferConfig(route)
    const tabs = getMonolithicTabs(route.component)
    
    const config = {
      routeName: route.name,
      routePath: route.path,
      title: route.meta.title || route.name,
      description: inferred.description || route.meta.description || '',
      apiEndpoint: inferred.apiEndpoint || '',
      wsChannel: inferred.wsChannel || '',
      component: route.component,
      tabs: tabs.length > 0 ? tabs : undefined,
      requiresAuth: route.meta.requiresAuth ?? true
    }
    
    configs.push(config)
  }
  
  return configs
}

function generateConfigFileContent(configs) {
  const lines = []
  
  lines.push(`/**
 * Page Configuration - Auto-generated by generate-page-config.js
 * 
 * This file is AUTO-GENERATED. Manual changes will be overwritten.
 * To make permanent changes, update the generation script and run:
 *   npm run generate-page-config
 * 
 * Generated at: ${new Date().toISOString()}
 * Routes processed: ${configs.length}
 */`)
  lines.push('')
  lines.push(`import type { PageConfigType, TabConfig, MonolithicPageConfig, StandardPageConfig, PageConfig } from '@/types/pageConfig'`)
  lines.push('')
  lines.push(`// Tab configurations for monolithic components`)
  lines.push(`const TAB_CONFIGS: Record<string, TabConfig[]> = {`)
  
  const tabByComponent = {}
  for (const config of configs) {
    if (config.tabs && config.tabs.length > 0) {
      tabByComponent[config.component] = config.tabs
    }
  }
  
  for (const [component, tabs] of Object.entries(tabByComponent)) {
    lines.push(`  '${component}': [`)
    for (const tab of tabs) {
      lines.push(`    {`)
      lines.push(`      id: '${tab.id}',`)
      if (tab.apiEndpoint) lines.push(`      apiEndpoint: '${tab.apiEndpoint}',`)
      if (tab.wsChannel) lines.push(`      wsChannel: '${tab.wsChannel}',`)
      lines.push(`    },`)
    }
    lines.push(`  ],`)
  }
  
  lines.push(`}`)
  lines.push('')
  lines.push(`// Standard page configurations (non-monolithic)`)
  lines.push(`const PAGE_CONFIGS: Record<string, StandardPageConfig> = {`)
  
  for (const config of configs) {
    if (!config.tabs || config.tabs.length === 0) {
      lines.push(`  '${config.routeName}': {`)
      lines.push(`    type: 'page',`)
      lines.push(`    routePath: '${config.routePath}',`)
      lines.push(`    title: '${config.title}',`)
      if (config.description) lines.push(`    description: '${config.description}',`)
      lines.push(`    apiEndpoint: '${config.apiEndpoint}',`)
      lines.push(`    wsChannel: '${config.wsChannel}',`)
      lines.push(`    component: '${config.component}',`)
      lines.push(`    requiresAuth: ${config.requiresAuth},`)
      lines.push(`  },`)
    }
  }
  
  lines.push(`}`)
  lines.push('')
  lines.push(`// Monolithic page configurations (components with multiple tabs)`)
  lines.push(`const MONOLITHIC_CONFIGS: Record<string, MonolithicPageConfig> = {`)
  
  for (const config of configs) {
    if (config.tabs && config.tabs.length > 0) {
      lines.push(`  '${config.routeName}': {`)
      lines.push(`    type: 'monolithic',`)
      lines.push(`    routePath: '${config.routePath}',`)
      lines.push(`    title: '${config.title}',`)
      if (config.description) lines.push(`    description: '${config.description}',`)
      lines.push(`    component: '${config.component}',`)
      lines.push(`    tabs: TAB_CONFIGS['${config.component}'] || [],`)
      lines.push(`    requiresAuth: ${config.requiresAuth},`)
      lines.push(`  },`)
    }
  }
  
  lines.push(`}`)
  lines.push('')
  lines.push(`// Combined PAGE_CONFIG for backward compatibility`)
  lines.push(`export const PAGE_CONFIG: Record<string, PageConfig> = {`)
  lines.push(`  ...PAGE_CONFIGS,`)
  lines.push(`  ...MONOLITHIC_CONFIGS,`)
  lines.push(`}`)
  lines.push('')
  lines.push(`// Type guards`)
  lines.push(`export function isRouteName(name: string): name is keyof typeof PAGE_CONFIG {`)
  lines.push(`  return name in PAGE_CONFIG`)
  lines.push(`}`)
  lines.push('')
  lines.push(`export function isMonolithicConfig(config: PageConfig): config is MonolithicPageConfig {`)
  lines.push(`  return config.type === 'monolithic'`)
  lines.push(`}`)
  lines.push('')
  lines.push(`export function isStandardConfig(config: PageConfig): config is StandardPageConfig {`)
  lines.push(`  return config.type === 'page'`)
  lines.push(`}`)
  lines.push('')
  lines.push(`// Helper functions`)
  lines.push(`export function getPageConfig(routeName: string): PageConfig | undefined {`)
  lines.push(`  return PAGE_CONFIG[routeName]`)
  lines.push(`}`)
  lines.push('')
  lines.push(`export function getTabConfig(routeName: string, tabId: string): TabConfig | undefined {`)
  lines.push(`  const config = PAGE_CONFIG[routeName]`)
  lines.push(`  if (isMonolithicConfig(config)) {`)
  lines.push(`    return config.tabs.find(tab => tab.id === tabId)`)
  lines.push(`  }`)
  lines.push(`  return undefined`)
  lines.push(`}`)
  lines.push('')
  lines.push(`export function getTabsForComponent(component: string): TabConfig[] {`)
  lines.push(`  return TAB_CONFIGS[component] || []`)
  lines.push(`}`)
  lines.push('')
  lines.push(`// Export types for external use`)
  lines.push(`export type { PageConfigType, TabConfig, MonolithicPageConfig, StandardPageConfig, PageConfig }`)
  lines.push('')
  
  return lines.join('\n')
}

function compareConfigs(current, generated) {
  const currentLines = current.split('\n')
  const generatedLines = generated.split('\n')
  const diff = []
  
  const maxLines = Math.max(currentLines.length, generatedLines.length)
  
  for (let i = 0; i < maxLines; i++) {
    const currentLine = currentLines[i] ?? ''
    const generatedLine = generatedLines[i] ?? ''
    
    if (currentLine !== generatedLine) {
      if (i < currentLines.length && i >= generatedLines.length) {
        diff.push(`- Line ${i + 1}: ${currentLine}`)
      } else if (i >= currentLines.length && i < generatedLines.length) {
        diff.push(`+ Line ${i + 1}: ${generatedLine}`)
      } else {
        diff.push(`- Line ${i + 1}: ${currentLine}`)
        diff.push(`+ Line ${i + 1}: ${generatedLine}`)
      }
    }
  }
  
  return diff
}

function runGeneration(options) {
  const result = { success: true, routesFound: 0, configsGenerated: 0, errors: [], warnings: [] }
  
  try {
    log('Parsing router file...', options.verbose)
    const routes = parseRouterFile(CONFIG.routerPath)
    result.routesFound = routes.length
    log(`Found ${routes.length} routes`, options.verbose)
    
    log('Generating page configurations...', options.verbose)
    const configs = generatePageConfig(routes)
    result.configsGenerated = configs.length
    
    const generatedContent = generateConfigFileContent(configs)
    
    if (options.dryRun) {
      console.log('\n=== DRY RUN - No files were written ===\n')
      console.log('Generated configuration preview:')
      console.log('='.repeat(60))
      console.log(generatedContent)
      console.log('='.repeat(60))
    } else if (options.diff) {
      let currentContent = ''
      try {
        currentContent = fs.readFileSync(CONFIG.configOutputPath, 'utf-8')
      } catch {
        result.warnings.push('Current config file not found, showing full generated content')
      }
      
      if (currentContent) {
        console.log('\n=== CONFIG DIFF ===\n')
        const diff = compareConfigs(currentContent, generatedContent)
        
        if (diff.length === 0) {
          console.log('No changes detected.')
        } else {
          console.log(`Showing first 50 lines of diff:`)
          console.log('='.repeat(60))
          console.log(diff.slice(0, 100).join('\n'))
          console.log('='.repeat(60))
          console.log(`\nTotal changes: ${diff.length} lines`)
        }
      } else {
        console.log('\n=== NEW CONFIG ===\n')
        console.log(generatedContent)
      }
    } else {
      if (fs.existsSync(CONFIG.configOutputPath)) {
        fs.writeFileSync(CONFIG.configBackupPath, fs.readFileSync(CONFIG.configOutputPath, 'utf-8'))
        console.log(`Backed up current config to: ${CONFIG.configBackupPath}`)
      }
      
      fs.writeFileSync(CONFIG.configOutputPath, generatedContent)
      console.log(`Generated page configuration: ${CONFIG.configOutputPath}`)
    }
    
    console.log('\n=== Generation Summary ===')
    console.log(`Routes found: ${result.routesFound}`)
    console.log(`Configs generated: ${result.configsGenerated}`)
    
    if (result.warnings.length > 0) {
      console.log('\nWarnings:')
      for (const warning of result.warnings) {
        console.log(`  - ${warning}`)
      }
    }
    
  } catch (error) {
    result.success = false
    result.errors.push(String(error))
    console.error('Generation failed:', error)
  }
  
  return result
}

function main() {
  const args = process.argv.slice(2)
  
  const options = {
    dryRun: args.includes('--dry-run') || args.includes('-n'),
    diff: args.includes('--diff') || args.includes('-d'),
    verbose: args.includes('--verbose') || args.includes('-v'),
    help: args.includes('--help') || args.includes('-h')
  }
  
  if (options.help) {
    console.log(`
Page Configuration Generator

Usage:
  node scripts/dev/tools/generate-page-config.js [options]

Options:
  --dry-run, -n    Show what would be generated without writing files
  --diff, -d       Show diff between current and generated config
  --verbose, -v    Show detailed output
  --help, -h       Show this help message

Examples:
  # Preview changes without writing
  npm run generate-page-config -- --dry-run
  
  # Show diff of changes
  npm run generate-page-config -- --diff
  
  # Generate with verbose output
  npm run generate-page-config -- --verbose

Output:
  Generates web/frontend/src/config/pageConfig.ts with all route configurations.
    `)
    return
  }
  
  console.log('Page Configuration Generator')
  console.log('='.repeat(60))
  
  const result = runGeneration(options)
  
  process.exit(result.success ? 0 : 1)
}

main()
