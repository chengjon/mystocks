import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 49', () => {
  it('removes advanced analysis websocket debug logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/composables/useAdvancedAnalysis.ts'), 'utf8')

    expect(source).not.toContain("console.log('WebSocket connected for advanced analysis')")
    expect(source).not.toContain("console.log('WebSocket disconnected')")
    expect(source).not.toContain("console.log('Analysis progress:', data)")
    expect(source).not.toContain("console.log('Analysis complete:', data)")
  })
})
