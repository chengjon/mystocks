#!/usr/bin/env node
/**
 * Page Configuration Validation Hook
 * 
 * Validates that all routes in the router have corresponding page configurations.
 * Run as a pre-commit hook to catch configuration drift.
 * 
 * Usage:
 *   node scripts/hooks/check-page-config.mjs [options]
 * 
 * Options:
 *   --fail     Exit with error code if validation fails
 *   --warn     Exit with warning code if issues found
 *   --json     Output results as JSON
 *   --verbose  Show detailed output
 *   --help     Show this help message
 */

import { readFileSync, existsSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join, relative } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)
const PROJECT_ROOT = join(__dirname, '../..')

// ============================================================================
// Configuration
// ============================================================================

const CONFIG = {
  routerPath: join(PROJECT_ROOT, 'web/frontend/src/router/index.ts'),
  configPath: join(PROJECT_ROOT, 'web/frontend/src/config/pageConfig.ts'),
  requiredFieldsPage: ['apiEndpoint', 'wsChannel', 'component'],
  requiredFieldsTab: ['id', 'apiEndpoint', 'wsChannel'],
  ignoreRoutes: ['notFound', 'login', 'test', 'artdeco-test', 'home']
}

// ============================================================================
// Types
// ============================================================================

class ValidationResult {
  constructor() {
    this.valid = true
    this.routesChecked = 0
    this.configuredRoutes = 0
    this.missingConfigs = []
    this.missingFields = []
    this.duplicateRoutes = []
    this.errors = []
    this.warnings = []
  }
  
  addError(message) {
    this.errors.push(message)
    this.valid = false
  }
  
  addWarning(message) {
    this.warnings.push(message)
  }
}

// ============================================================================
// Utility Functions
// ============================================================================

function log(message, verbose = false, options = {}) {
  const { prefix = '✓' } = options
  if (verbose || options.force) {
    console.log(`${prefix} ${message}`)
  }
}

function extractRoutes(routerContent) {
  const routes = []
  const routeRegex = /path:\s*['"]([^'"]+)['"]\s*,\s*name:\s*['"]([^'"]+)['"]\s*,\s*component:/g
  
  let match
  while ((match = routeRegex.exec(routerContent)) !== null) {
    const routeName = match[2]
    
    if (CONFIG.ignoreRoutes.includes(routeName)) {
      continue
    }
    
    routes.push(routeName)
  }
  
  return routes
}

function extractConfiguredRoutes(configContent) {
  const routes = {}

  const monolithicRegex = /['"]([^'"]+)['"]:\s*\{\s*type:\s*['"]monolithic['"]/g
  const pageRegex = /['"]([^'"]+)['"]:\s*\{\s*type:\s*['"]page['"]/g

  let match
  while ((match = monolithicRegex.exec(configContent)) !== null) {
    routes[match[1]] = 'monolithic'
  }

  while ((match = pageRegex.exec(configContent)) !== null) {
    routes[match[1]] = 'page'
  }

  return routes
}

function validateRequiredFields(configBlock, configType, configContent) {
  const missing = []

  if (configType === 'page') {
    // For page configs, check top-level fields
    for (const field of CONFIG.requiredFieldsPage) {
      if (!configBlock.includes(field)) {
        missing.push(field)
      }
    }
  } else if (configType === 'monolithic') {
    // For monolithic configs, check that tabs have required fields
    const tabConfigsMatch = configBlock.match(/tabs:\s*TAB_CONFIGS\[['"][^'"]+['"]\]\s*\|\s*\[\]/)
    if (tabConfigsMatch) {
      // Extract the TAB_CONFIGS key to verify it exists
      const keyMatch = configBlock.match(/tabs:\s*TAB_CONFIGS\[['"]([^'"]+)['"]/)
      if (keyMatch) {
        const tabConfigKey = keyMatch[1]
        // Verify TAB_CONFIGS has entries for this key
        const tabConfigSection = configContent.match(new RegExp(`${tabConfigKey}:\\s*\\[([\\s\\S]*?)\\]`))
        if (tabConfigSection && tabConfigSection[1].trim().length > 0) {
          // Check that tabs have required fields
          const tabEntries = tabConfigSection[1].match(/\\{\\s*id:[^}]+apiEndpoint:[^}]+wsChannel:[^}]+\\}/g)
          if (!tabEntries || tabEntries.length === 0) {
            missing.push('tabs with apiEndpoint, wsChannel')
          }
        } else {
          missing.push('tabs definition')
        }
      } else {
        missing.push('tabs key reference')
      }
    } else if (!configBlock.includes('tabs:')) {
      missing.push('tabs property')
    }
  }

  return missing
}

function parseRouteBlock(content, startIndex) {
  let depth = 0
  let start = startIndex
  let end = startIndex
  
  for (let i = startIndex; i < content.length; i++) {
    if (content[i] === '{') {
      if (depth === 0) start = i
      depth++
    } else if (content[i] === '}') {
      depth--
      if (depth === 0) {
        end = i + 1
        break
      }
    }
  }
  
  return content.substring(start, end)
}

function extractRouteConfig(routeName, configContent) {
  const patterns = [
    new RegExp(`['"]${routeName}['"]:\\s*\\{[^}]+apiEndpoint:[^}]+\\}`, 's'),
    new RegExp(`['"]${routeName}['"]:\\s*\\{[^}]+\\}`, 's')
  ]
  
  for (const pattern of patterns) {
    const match = configContent.match(pattern)
    if (match) {
      return match[0]
    }
  }
  
  return null
}

function checkDuplicateRoutes(routes) {
  const seen = new Set()
  const duplicates = []
  
  for (const route of routes) {
    if (seen.has(route)) {
      duplicates.push(route)
    }
    seen.add(route)
  }
  
  return duplicates
}

// ============================================================================
// Validation Functions
// ============================================================================

function validateRoutes(options) {
  const result = new ValidationResult()
  
  log('Reading router file...', options.verbose)
  if (!existsSync(CONFIG.routerPath)) {
    result.addError(`Router file not found: ${CONFIG.routerPath}`)
    return result
  }
  
  const routerContent = readFileSync(CONFIG.routerPath, 'utf-8')
  const routes = extractRoutes(routerContent)
  result.routesChecked = routes.length
  
  log(`Found ${routes.length} routes in router`, options.verbose)
  
  if (!existsSync(CONFIG.configPath)) {
    result.addError(`Config file not found: ${CONFIG.configPath}`)
    result.missingConfigs = routes
    return result
  }
  
  const configContent = readFileSync(CONFIG.configPath, 'utf-8')
  const configuredRoutes = extractConfiguredRoutes(configContent)
  result.configuredRoutes = Object.keys(configuredRoutes).length
  
  log(`Found ${result.configuredRoutes} configured routes`, options.verbose)
  
  // Check for missing configurations
  for (const route of routes) {
    if (!configuredRoutes[route]) {
      result.missingConfigs.push(route)
    } else {
      // Validate required fields based on config type
      const configType = configuredRoutes[route]
      const configBlock = extractRouteConfig(route, configContent)
      if (configBlock) {
        const missingFields = validateRequiredFields(configBlock, configType, configContent)
        if (missingFields.length > 0) {
          result.missingFields.push({ route, fields: missingFields, type: configType })
        }
      }
    }
  }
  
  // Check for duplicate routes
  const duplicates = checkDuplicateRoutes(routes)
  result.duplicateRoutes = duplicates
  
  // Warnings for unused configurations
  for (const [route, type] of Object.entries(configuredRoutes)) {
    if (!routes.includes(route)) {
      result.addWarning(`Configuration exists for non-existent route: ${route}`)
    }
  }
  
  // Set validity
  if (result.missingConfigs.length > 0 || result.missingFields.length > 0) {
    result.valid = false
  }
  
  return result
}

// ============================================================================
// Output Functions
// ============================================================================

function printResult(result, options) {
  console.log('\n' + '='.repeat(60))
  console.log('Page Configuration Validation Report')
  console.log('='.repeat(60))
  console.log(`Routes checked: ${result.routesChecked}`)
  console.log(`Routes configured: ${result.configuredRoutes}`)
  console.log('')
  
  if (result.missingConfigs.length > 0) {
    console.log('❌ Missing Configurations:')
    for (const route of result.missingConfigs) {
      console.log(`   - ${route}`)
    }
    console.log('')
  }
  
  if (result.missingFields.length > 0) {
    console.log('⚠️  Missing Required Fields:')
    for (const { route, fields, type } of result.missingFields) {
      console.log(`   - ${route} (${type}): ${fields.join(', ')}`)
    }
    console.log('')
  }
  
  if (result.duplicateRoutes.length > 0) {
    console.log('⚠️  Duplicate Routes:')
    for (const route of result.duplicateRoutes) {
      console.log(`   - ${route}`)
    }
    console.log('')
  }
  
  if (result.errors.length > 0) {
    console.log('Errors:')
    for (const error of result.errors) {
      console.log(`   - ${error}`)
    }
    console.log('')
  }
  
  if (result.warnings.length > 0) {
    console.log('Warnings:')
    for (const warning of result.warnings) {
      console.log(`   - ${warning}`)
    }
    console.log('')
  }
  
  if (result.valid) {
    console.log('✅ All routes have valid configurations!')
  } else {
    console.log('❌ Validation failed. Fix the issues above.')
  }
  
  console.log('='.repeat(60))
}

function outputJson(result) {
  console.log(JSON.stringify({
    valid: result.valid,
    routesChecked: result.routesChecked,
    configuredRoutes: result.configuredRoutes,
    missingConfigs: result.missingConfigs,
    missingFields: result.missingFields,
    duplicateRoutes: result.duplicateRoutes,
    errors: result.errors,
    warnings: result.warnings
  }, null, 2))
}

// ============================================================================
// Main
// ============================================================================

function main() {
  const args = process.argv.slice(2)
  
  const options = {
    fail: args.includes('--fail') || args.includes('-f'),
    warn: args.includes('--warn') || args.includes('-w'),
    json: args.includes('--json') || args.includes('-j'),
    verbose: args.includes('--verbose') || args.includes('-v'),
    help: args.includes('--help') || args.includes('-h')
  }
  
  if (options.help) {
    console.log(`
Page Configuration Validation Hook

Usage:
  node scripts/hooks/check-page-config.mjs [options]

Options:
  --fail, -f    Exit with error code (1) if validation fails
  --warn, -w    Exit with warning code (2) if issues found
  --json, -j    Output results as JSON
  --verbose, -v Show detailed output
  --help, -h    Show this help message

Exit Codes:
  0 - All validations passed
  1 - Validation errors (missing configs/fields)
  2 - Warnings only (no errors)
  3 - Fatal error (file not found, etc.)

Examples:
  # Run validation with detailed output
  npm run validate-page-config
  
  # Fail on any issues
  npm run validate-page-config -- --fail
  
  # JSON output for CI/CD
  npm run validate-page-config -- --json

Pre-commit Hook Usage:
  Add to .pre-commit-config.yaml:
  
  - repo: local
    hooks:
      - id: check-page-config
        name: Check Page Configurations
        entry: node scripts/hooks/check-page-config.mjs --fail
        language: system
        pass_filenames: false
        stages: [pre-commit]
    `)
    return
  }
  
  console.log('Page Configuration Validator')
  console.log('='.repeat(60))
  
  try {
    const result = validateRoutes(options)
    
    if (options.json) {
      outputJson(result)
    } else {
      printResult(result, options)
    }
    
    // Exit with appropriate code
    if (result.errors.length > 0 && options.fail) {
      console.log('\n❌ Validation failed due to errors.')
      process.exit(1)
    } else if (!result.valid && options.fail) {
      console.log('\n❌ Validation failed.')
      process.exit(1)
    } else if (!result.valid) {
      console.log('\n⚠️  Validation completed with issues.')
      process.exit(2)
    }
    
  } catch (error) {
    console.error('Fatal error during validation:', error.message)
    process.exit(3)
  }
}

main()
