import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 73', () => {
  it('removes archive base layout interaction and fetch logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/layouts/archive/BaseLayout.vue'), 'utf8')

    expect(source).not.toContain("console.log('Command Palette opened')")
    expect(source).not.toContain("console.log('Command Palette closed')")
    expect(source).not.toContain("console.log('Navigated to:', path)")
    expect(source).not.toContain('console.log(`[BaseLayout] Fetching data for: ${item.label} from ${item.apiEndpoint}`)')
    expect(source).not.toContain('console.log(`[BaseLayout] Successfully fetched data for: ${item.label}`)')
    expect(source).not.toContain("console.log('Retrying API call for:', item.label);")
  })
})
