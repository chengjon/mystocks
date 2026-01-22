// web/frontend/tests/unit/components/ant-design-migration.spec.ts
import { describe, it, expect } from 'vitest'

describe('Dependency Migration Validation', () => {
  it('should not have ant-design-vue in runtime dependencies', () => {
    // This test validates that ant-design-vue has been removed from dependencies
    // by checking if it's available in the runtime
    try {
      // If ant-design-vue is still available, this would succeed
      // We expect it to fail, indicating successful removal
      require('ant-design-vue')
      expect(false).toBe(true) // Should not reach here
    } catch (error) {
      // Expected: ant-design-vue should not be available
      expect(error.message).toContain('Cannot find module')
    }
  })

  it('should have element-plus available', () => {
    // This validates that Element Plus is properly available
    try {
      const elementPlus = require('element-plus')
      expect(elementPlus).toBeDefined()
      expect(elementPlus).toHaveProperty('ElButton')
    } catch (error) {
      expect(error).toBeUndefined() // Should not throw
    }
  })

  it('should validate package.json structure', () => {
    const pkg = require('../../../package.json')

    // Should not have ant-design-vue
    expect(pkg.dependencies).not.toHaveProperty('ant-design-vue')
    expect(pkg.dependencies).not.toHaveProperty('@ant-design/icons-vue')

    // Should have element-plus
    expect(pkg.dependencies).toHaveProperty('element-plus')
    expect(pkg.dependencies).toHaveProperty('@element-plus/icons-vue')

    // Should have proper version constraints
    expect(pkg.dependencies['element-plus']).toMatch(/^[\^~]?2\./)
  })
})