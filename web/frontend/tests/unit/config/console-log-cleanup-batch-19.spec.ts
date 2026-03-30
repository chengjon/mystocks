import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 19', () => {
  it('removes indexeddb lifecycle console logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/utils/indexedDB.ts'), 'utf8')

    expect(source).not.toContain("console.log('✅ IndexedDB initialized successfully')")
    expect(source).not.toContain("console.log('📦 IndexedDB schema created/updated')")
    expect(source).not.toContain("console.log('🗑️ All IndexedDB data cleared')")
    expect(source).not.toContain("console.log('🔒 IndexedDB connection closed')")
  })
})
