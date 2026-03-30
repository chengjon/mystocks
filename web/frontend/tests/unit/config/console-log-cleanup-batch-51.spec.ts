import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 51', () => {
  it('removes batch analysis view stub action logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/components/artdeco/advanced/composables/useArtDecoBatchAnalysisView.ts'), 'utf8')

    expect(source).not.toContain("console.log('Refreshing batch progress...')")
    expect(source).not.toContain("console.log('Exporting batch report...')")
    expect(source).not.toContain("console.log('Generating batch report...')")
    expect(source).not.toContain("console.log('Saving batch report...')")
    expect(source).not.toContain("console.log('Sharing batch report...')")
    expect(source).not.toContain("console.log('Scheduling batch report...')")
  })
})
