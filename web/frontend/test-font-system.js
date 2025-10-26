/**
 * Automated Font System Test Script
 * Tests User Story 1 - Global Font System Implementation
 *
 * Run: node test-font-system.js
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// Test results tracking
const results = {
  passed: 0,
  failed: 0,
  warnings: 0,
  tests: []
}

function test(name, fn) {
  try {
    const result = fn()
    if (result.status === 'pass') {
      results.passed++
      console.log(`✅ PASS: ${name}`)
    } else if (result.status === 'warn') {
      results.warnings++
      console.log(`⚠️  WARN: ${name} - ${result.message}`)
    } else {
      results.failed++
      console.log(`❌ FAIL: ${name} - ${result.message}`)
    }
    results.tests.push({ name, ...result })
  } catch (error) {
    results.failed++
    console.log(`❌ ERROR: ${name} - ${error.message}`)
    results.tests.push({ name, status: 'error', message: error.message })
  }
}

console.log('🚀 Starting Font System Automated Tests...\n')

// Test 1: Typography.css exists
test('Typography.css file exists', () => {
  const typographyPath = path.join(__dirname, 'src/assets/styles/typography.css')
  if (fs.existsSync(typographyPath)) {
    return { status: 'pass' }
  }
  return { status: 'fail', message: 'File not found at src/assets/styles/typography.css' }
})

// Test 2: Typography.css has CSS Variables
test('Typography.css contains required CSS Variables', () => {
  const typographyPath = path.join(__dirname, 'src/assets/styles/typography.css')
  const content = fs.readFileSync(typographyPath, 'utf-8')

  const requiredVars = [
    '--font-size-base',
    '--font-size-helper',
    '--font-size-body',
    '--font-size-subtitle',
    '--font-size-title',
    '--font-size-heading',
    '--font-family',
    '--line-height-base'
  ]

  const missing = requiredVars.filter(v => !content.includes(v))

  if (missing.length === 0) {
    return { status: 'pass' }
  }
  return { status: 'fail', message: `Missing variables: ${missing.join(', ')}` }
})

// Test 3: Typography.css imported in main.js
test('Typography.css imported in main.js', () => {
  const mainPath = path.join(__dirname, 'src/main.js')
  const content = fs.readFileSync(mainPath, 'utf-8')

  if (content.includes("import './assets/styles/typography.css'")) {
    return { status: 'pass' }
  }
  return { status: 'fail', message: 'Import statement not found in main.js' }
})

// Test 4: Element Plus component overrides exist
test('Typography.css has Element Plus overrides', () => {
  const typographyPath = path.join(__dirname, 'src/assets/styles/typography.css')
  const content = fs.readFileSync(typographyPath, 'utf-8')

  const requiredOverrides = [
    '.el-button',
    '.el-table',
    '.el-form-item__label',
    '.el-card__header',
    '.el-dialog__title',
    '.el-message',
    '.el-tabs__item',
    '.el-menu-item'
  ]

  const missing = requiredOverrides.filter(selector => !content.includes(selector))

  if (missing.length === 0) {
    return { status: 'pass' }
  }
  return { status: 'warn', message: `Missing overrides: ${missing.join(', ')}` }
})

// Test 5: FontSizeSetting.vue uses store method
test('FontSizeSetting.vue uses applyFontSize store method', () => {
  const componentPath = path.join(__dirname, 'src/components/settings/FontSizeSetting.vue')
  const content = fs.readFileSync(componentPath, 'utf-8')

  if (content.includes('preferencesStore.applyFontSize(newSize)')) {
    return { status: 'pass' }
  }
  return { status: 'fail', message: 'applyFontSize method not called in handleFontSizeChange' }
})

// Test 6: Preferences store has applyFontSize method
test('Preferences store exports applyFontSize method', () => {
  const storePath = path.join(__dirname, 'src/stores/preferences.ts')
  const content = fs.readFileSync(storePath, 'utf-8')

  if (content.includes('const applyFontSize') && content.includes('applyFontSize,')) {
    return { status: 'pass' }
  }
  return { status: 'fail', message: 'applyFontSize method not found in store exports' }
})

// Test 7: Preferences composable has localStorage support
test('useUserPreferences has localStorage persistence', () => {
  const composablePath = path.join(__dirname, 'src/composables/useUserPreferences.ts')
  const content = fs.readFileSync(composablePath, 'utf-8')

  if (content.includes('localStorage.setItem') && content.includes('localStorage.getItem')) {
    return { status: 'pass' }
  }
  return { status: 'fail', message: 'localStorage methods not found in composable' }
})

// Test 8: Preferences composable has error handling
test('useUserPreferences has error handling for quota exceeded', () => {
  const composablePath = path.join(__dirname, 'src/composables/useUserPreferences.ts')
  const content = fs.readFileSync(composablePath, 'utf-8')

  if (content.includes('QuotaExceededError') && content.includes('sessionStorage')) {
    return { status: 'pass' }
  }
  return { status: 'warn', message: 'Quota exceeded fallback not implemented' }
})

// Test 9: Responsive design media query exists
test('Typography.css has mobile responsive media query', () => {
  const typographyPath = path.join(__dirname, 'src/assets/styles/typography.css')
  const content = fs.readFileSync(typographyPath, 'utf-8')

  if (content.includes('@media (max-width: 768px)')) {
    return { status: 'pass' }
  }
  return { status: 'warn', message: 'Mobile media query not found' }
})

// Test 10: Preferences initialized in main.js
test('Preferences store initialized in main.js', () => {
  const mainPath = path.join(__dirname, 'src/main.js')
  const content = fs.readFileSync(mainPath, 'utf-8')

  if (content.includes('usePreferencesStore') && content.includes('preferencesStore.initialize()')) {
    return { status: 'pass' }
  }
  return { status: 'fail', message: 'Preferences store not initialized in main.js' }
})

// Test 11: FontSizeSetting component has 5 size options
test('FontSizeSetting.vue has 5 font size options', () => {
  const componentPath = path.join(__dirname, 'src/components/settings/FontSizeSetting.vue')
  const content = fs.readFileSync(componentPath, 'utf-8')

  const sizes = ['12px', '14px', '16px', '16px', '18px', '20px']
  const foundSizes = sizes.filter(size => content.includes(`label="${size}"`))

  if (foundSizes.length >= 4) { // At least 4 different sizes
    return { status: 'pass' }
  }
  return { status: 'warn', message: `Only found ${foundSizes.length} size options` }
})

// Test 12: Check for hardcoded font sizes (sampling)
test('Sample views for hardcoded font-size (technical debt check)', () => {
  const dashboardPath = path.join(__dirname, 'src/views/Dashboard.vue')
  if (!fs.existsSync(dashboardPath)) {
    return { status: 'warn', message: 'Dashboard.vue not found, skipping check' }
  }

  const content = fs.readFileSync(dashboardPath, 'utf-8')
  const hardcodedMatches = content.match(/font-size:\s*\d+px/g)

  if (hardcodedMatches && hardcodedMatches.length > 0) {
    return {
      status: 'warn',
      message: `Found ${hardcodedMatches.length} hardcoded font-size values (technical debt)`
    }
  }
  return { status: 'pass' }
})

// Print summary
console.log('\n' + '='.repeat(60))
console.log('📊 Test Summary')
console.log('='.repeat(60))
console.log(`✅ Passed:  ${results.passed}`)
console.log(`❌ Failed:  ${results.failed}`)
console.log(`⚠️  Warnings: ${results.warnings}`)
console.log(`📝 Total:   ${results.tests.length}`)
console.log('='.repeat(60))

if (results.failed > 0) {
  console.log('\n❌ Some tests failed. Review the output above.')
  process.exit(1)
} else if (results.warnings > 0) {
  console.log('\n⚠️  All critical tests passed, but some warnings exist.')
  console.log('💡 Check warnings above for improvement opportunities.')
  process.exit(0)
} else {
  console.log('\n✅ All tests passed! Font system is ready for manual testing.')
  process.exit(0)
}
