import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 62', () => {
  it('removes base layout fetch and retry logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/layouts/BaseLayout.vue'), 'utf8')

    expect(source).not.toContain('console.log(`[BaseLayout] Fetching data for: ${item.label} from ${item.apiEndpoint}`)')
    expect(source).not.toContain('console.log(`[BaseLayout] Successfully fetched data for: ${item.label}`)')
    expect(source).not.toContain("console.log('Retrying API call for:', item.label);")
  })
})
