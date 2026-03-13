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
  optimizationPlanPath: path.resolve(__dirname, '../../../docs/plans/frontend-page-optimization-list.md'),
  
  routeConfigMap: {
    'dashboard': { apiEndpoint: '/api/dashboard/overview', wsChannel: 'dashboard:realtime', description: '交易室概览' },
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
  
  monolithicTabs: {}
}

// ============================================================================
// Utility Functions
// ============================================================================

function log(message, verbose = false) {
  if (verbose) {
    console.log(message)
  }
}

function parseStringConstantDeclarations(content, exportOnly = false) {
  const constants = {}
  const exportPrefix = exportOnly ? 'export\\s+' : '(?:export\\s+)?'
  const constRegex = new RegExp(
    `${exportPrefix}const\\s+([A-Za-z_$][\\w$]*)\\s*=\\s*(['"\`])([^\\2]*?)\\2`,
    'g'
  )

  let match
  while ((match = constRegex.exec(content)) !== null) {
    const [, name, , value] = match
    constants[name] = value
  }

  return constants
}

function resolveImportFilePath(baseDir, importPath) {
  const candidates = [
    importPath,
    `${importPath}.ts`,
    `${importPath}.js`,
    path.join(importPath, 'index.ts'),
    path.join(importPath, 'index.js')
  ]

  for (const candidate of candidates) {
    const resolvedPath = path.resolve(baseDir, candidate)
    if (fs.existsSync(resolvedPath)) {
      return resolvedPath
    }
  }

  return null
}

function parseImportedStringConstants(content, filePath) {
  const constants = {}
  const importRegex = /import\s+\{\s*([^}]+)\s*\}\s+from\s+['"]([^'"]+)['"]/g
  const baseDir = path.dirname(filePath)

  let match
  while ((match = importRegex.exec(content)) !== null) {
    const [, importedNames, importPath] = match

    if (!importPath.startsWith('.')) {
      continue
    }

    const resolvedImportPath = resolveImportFilePath(baseDir, importPath)
    if (!resolvedImportPath) {
      continue
    }

    const importedContent = fs.readFileSync(resolvedImportPath, 'utf-8')
    const exportedConstants = parseStringConstantDeclarations(importedContent, true)

    for (const importedName of importedNames.split(',').map(item => item.trim()).filter(Boolean)) {
      const [originalName, aliasName] = importedName.split(/\s+as\s+/).map(item => item.trim())
      const localName = aliasName || originalName

      if (exportedConstants[originalName]) {
        constants[localName] = exportedConstants[originalName]
      }
    }
  }

  return constants
}

function resolveRouteValue(rawValue, constants) {
  const value = rawValue.trim()

  if ((value.startsWith("'") && value.endsWith("'")) || (value.startsWith('"') && value.endsWith('"')) || (value.startsWith('`') && value.endsWith('`'))) {
    return value.slice(1, -1)
  }

  return constants[value] || null
}

function findBalancedSegment(text, startIdx, openChar, closeChar) {
  if (startIdx < 0 || startIdx >= text.length || text[startIdx] !== openChar) {
    throw new Error(`Invalid segment start for ${openChar}: ${startIdx}`)
  }

  let depth = 0
  let inString = null
  let escaped = false

  for (let idx = startIdx; idx < text.length; idx += 1) {
    const ch = text[idx]

    if (inString) {
      if (escaped) {
        escaped = false
        continue
      }
      if (ch === '\\') {
        escaped = true
        continue
      }
      if (ch === inString) {
        inString = null
      }
      continue
    }

    if (ch === "'" || ch === '"' || ch === '`') {
      inString = ch
      continue
    }

    if (ch === openChar) {
      depth += 1
    } else if (ch === closeChar) {
      depth -= 1
      if (depth === 0) {
        return [startIdx, idx]
      }
    }
  }

  throw new Error(`Unbalanced segment for ${openChar}${closeChar} at index ${startIdx}`)
}

function extractRoutesArray(content) {
  const markerIdx = content.indexOf('const routes')
  if (markerIdx < 0) {
    throw new Error('Cannot find `const routes` in router file')
  }

  const assignIdx = content.indexOf('=', markerIdx)
  if (assignIdx < 0) {
    throw new Error('Cannot find routes assignment')
  }

  const arrayStart = content.indexOf('[', assignIdx)
  if (arrayStart < 0) {
    throw new Error('Cannot find routes array start')
  }

  const [, arrayEnd] = findBalancedSegment(content, arrayStart, '[', ']')
  return content.slice(arrayStart + 1, arrayEnd)
}

function splitTopLevelObjects(arrayContent) {
  const objects = []
  let depth = 0
  let inString = null
  let escaped = false
  let startIdx = -1

  for (let idx = 0; idx < arrayContent.length; idx += 1) {
    const ch = arrayContent[idx]

    if (inString) {
      if (escaped) {
        escaped = false
        continue
      }
      if (ch === '\\') {
        escaped = true
        continue
      }
      if (ch === inString) {
        inString = null
      }
      continue
    }

    if (ch === "'" || ch === '"' || ch === '`') {
      inString = ch
      continue
    }

    if (ch === '{') {
      if (depth === 0) {
        startIdx = idx
      }
      depth += 1
    } else if (ch === '}') {
      depth -= 1
      if (depth === 0 && startIdx >= 0) {
        objects.push(arrayContent.slice(startIdx, idx + 1))
        startIdx = -1
      }
    }
  }

  return objects
}

function findTopLevelPropertyIndex(objText, prop) {
  let depth = 0
  let inString = null
  let escaped = false

  for (let idx = 0; idx < objText.length; idx += 1) {
    const ch = objText[idx]

    if (inString) {
      if (escaped) {
        escaped = false
        continue
      }
      if (ch === '\\') {
        escaped = true
        continue
      }
      if (ch === inString) {
        inString = null
      }
      continue
    }

    if (ch === "'" || ch === '"' || ch === '`') {
      inString = ch
      continue
    }

    if (ch === '{') {
      depth += 1
      continue
    }

    if (ch === '}') {
      depth -= 1
      continue
    }

    if (depth !== 1) {
      continue
    }

    if (!objText.startsWith(prop, idx)) {
      continue
    }

    const before = idx === 0 ? '' : objText[idx - 1]
    const after = objText[idx + prop.length] || ''
    if (/[A-Za-z0-9_$]/.test(before) || /[A-Za-z0-9_$]/.test(after)) {
      continue
    }

    const remainder = objText.slice(idx + prop.length)
    if (/^\s*:/.test(remainder)) {
      return idx
    }
  }

  return -1
}

function extractPropertyToken(objText, prop) {
  const propertyIdx = findTopLevelPropertyIndex(objText, prop)
  if (propertyIdx < 0) {
    return null
  }

  const pattern = new RegExp(`^${prop}\\s*:\\s*(['"\`][^'"\`]+['"\`]|[A-Za-z_$][\\w$]*)`)
  const match = objText.slice(propertyIdx).match(pattern)
  return match ? match[1].trim() : null
}

function extractArrayProperty(objText, prop) {
  const propertyIdx = findTopLevelPropertyIndex(objText, prop)
  if (propertyIdx < 0) {
    return null
  }

  const arrayStart = objText.indexOf('[', propertyIdx)
  if (arrayStart < 0) {
    return null
  }

  const [, arrayEnd] = findBalancedSegment(objText, arrayStart, '[', ']')
  return objText.slice(arrayStart + 1, arrayEnd)
}

function extractComponentPath(objText) {
  const match = objText.match(/component\s*:\s*\(\)\s*=>\s*import\(\s*['"]@\/views\/([^'"]+)['"]\s*\)/)
  return match ? match[1].trim() : null
}

function extractObjectProperty(objText, prop) {
  const propertyIdx = findTopLevelPropertyIndex(objText, prop)
  if (propertyIdx < 0) {
    return null
  }

  const objectStart = objText.indexOf('{', propertyIdx)
  if (objectStart < 0) {
    return null
  }

  const [, objectEnd] = findBalancedSegment(objText, objectStart, '{', '}')
  return objText.slice(objectStart + 1, objectEnd)
}

function extractQuotedProperty(text, prop) {
  if (!text) {
    return null
  }

  const patterns = [
    new RegExp(`\\b${prop}\\s*:\\s*'([^']*)'`),
    new RegExp(`\\b${prop}\\s*:\\s*"([^"]*)"`),
  ]

  for (const pattern of patterns) {
    const match = text.match(pattern)
    if (match) {
      return match[1].trim()
    }
  }

  return null
}

function extractBooleanProperty(text, prop) {
  if (!text) {
    return undefined
  }

  const match = text.match(new RegExp(`\\b${prop}\\s*:\\s*(true|false)`))
  if (!match) {
    return undefined
  }
  return match[1] === 'true'
}

function joinPaths(basePath, childPath) {
  if (childPath.startsWith('/')) {
    return childPath
  }
  if (!basePath || basePath === '/') {
    return `/${childPath}`
  }
  return `${basePath.replace(/\/$/, '')}/${childPath}`
}

function shouldIgnoreRoute(route) {
  return (
    !route.name ||
    route.name === 'not-found' ||
    route.name.startsWith('qm-') ||
    route.fullPath.startsWith('/qm') ||
    route.fullPath.startsWith('/detail/')
  )
}

function parseRouteArray(arrayContent, basePath, constants, routes) {
  for (const obj of splitTopLevelObjects(arrayContent)) {
    const rawPath = extractPropertyToken(obj, 'path')
    if (!rawPath) {
      continue
    }

    const resolvedPath = resolveRouteValue(rawPath, constants)
    if (resolvedPath == null) {
      continue
    }

    const fullPath = joinPaths(basePath, resolvedPath)
    const rawName = extractPropertyToken(obj, 'name')
    const routeName = rawName ? resolveRouteValue(rawName, constants) : null
    const componentPath = extractComponentPath(obj)
    const component = componentPath ? componentPath.split('/').pop() : null
    const metaText = extractObjectProperty(obj, 'meta')

    if (routeName && component) {
      routes.push({
        path: resolvedPath,
        fullPath,
        name: routeName,
        component,
        meta: {
          title: extractQuotedProperty(metaText, 'title') || '',
          api: extractQuotedProperty(metaText, 'api') || '',
          requiresAuth: extractBooleanProperty(metaText, 'requiresAuth') ?? true,
        },
      })
    }

    const children = extractArrayProperty(obj, 'children')
    if (children !== null) {
      parseRouteArray(children, fullPath, constants, routes)
    }
  }
}

function parseRouterFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf-8')
    const constants = {
      ...parseStringConstantDeclarations(content),
      ...parseImportedStringConstants(content, filePath),
    }
    const routesArray = extractRoutesArray(content)
    const routes = []

    parseRouteArray(routesArray, '', constants, routes)

    return routes.filter((route) => !shouldIgnoreRoute(route))
  } catch (error) {
    throw new Error(`Failed to parse router file: ${error}`)
  }
}

function parseOptimizationPlan(filePath) {
  if (!fs.existsSync(filePath)) {
    return new Map()
  }

  const content = fs.readFileSync(filePath, 'utf-8')
  const lines = content.split(/\r?\n/)
  const headerIdx = lines.findIndex((line) => line.trim().startsWith('| # | 页面 | 路径 |'))
  if (headerIdx < 0) {
    return new Map()
  }

  const rows = new Map()
  const normalizeCell = (value) => value.trim().replace(/^`|`$/g, '').trim()

  for (const line of lines.slice(headerIdx + 2)) {
    const stripped = line.trim()
    if (!stripped.startsWith('|')) {
      break
    }

    const cols = stripped
      .replace(/^\|/, '')
      .replace(/\|$/, '')
      .split('|')
      .map(normalizeCell)

    if (cols.length < 9) {
      continue
    }

    const row = {
      index: cols[0],
      page: cols[1],
      path: cols[2],
      componentPath: cols[3],
      priority: cols[4],
      dataStatus: cols[5],
      api: cols[6],
      apiStatus: cols[7],
      notes: cols[8],
    }

    rows.set(row.path, row)
    if (row.path === '/dealing-room') {
      rows.set('/dashboard', row)
    }
  }

  return rows
}

function inferWsChannel(route, fallback) {
  if (route.name === 'login' || route.meta.requiresAuth === false) {
    return ''
  }

  if (fallback) {
    return fallback
  }

  const [domain, ...rest] = route.name.split('-')
  if (!domain) {
    return ''
  }

  const suffix = rest.join('-')
  return suffix ? `${domain}:${suffix}` : domain
}

function inferApiFromRouteName(route) {
  const [domain, ...rest] = route.name.split('-')
  if (!domain) {
    return ''
  }

  const suffix = rest.join('-')
  return suffix ? `/api/${domain}/${suffix}` : `/api/${domain}`
}

function inferConfig(route, optimizationRow) {
  const manual = CONFIG.routeConfigMap[route.name] || {}
  const apiEndpoint = route.meta.api || optimizationRow?.api || manual.apiEndpoint || inferApiFromRouteName(route)
  const wsChannel = inferWsChannel(route, manual.wsChannel)

  return {
    apiEndpoint,
    wsChannel,
    description: manual.description || route.meta.title || route.name,
  }
}

function getMonolithicTabs(component) {
  const componentName = component.split('/').pop() || component
  return CONFIG.monolithicTabs[componentName] || []
}

function isMonolithicComponent(component) {
  const componentName = component.split('/').pop() || component
  return componentName in CONFIG.monolithicTabs
}

function generatePageConfig(routes, optimizationRows) {
  const configs = []
  
  for (const route of routes) {
    const inferred = inferConfig(route, optimizationRows.get(route.fullPath))
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
    const optimizationRows = parseOptimizationPlan(CONFIG.optimizationPlanPath)
    result.routesFound = routes.length
    log(`Found ${routes.length} routes`, options.verbose)
    
    log('Generating page configurations...', options.verbose)
    const configs = generatePageConfig(routes, optimizationRows)
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
