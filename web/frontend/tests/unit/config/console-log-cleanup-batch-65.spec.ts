import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 65', () => {
  it('removes market service request and response logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/services/api/marketService.ts'), 'utf8')

    expect(source).not.toContain('console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {')
    expect(source).not.toContain('console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, {')
  })
})
