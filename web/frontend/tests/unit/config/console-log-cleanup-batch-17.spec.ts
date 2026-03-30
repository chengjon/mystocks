import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 17', () => {
  it('removes version negotiator console logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/services/versionNegotiator.ts'), 'utf8')

    expect(source).not.toContain("console.log('✅ API版本检测完成'")
    expect(source).not.toContain('console.log(`📋 ${endpoint}: ${version} (${source})`)')
  })
})
