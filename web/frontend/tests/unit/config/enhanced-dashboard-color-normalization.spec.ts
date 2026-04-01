import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('EnhancedDashboard color normalization', () => {
  it('uses semantic stat tones instead of hex color mapping helpers', () => {
    const viewSource = readSource('src/views/EnhancedDashboard.vue')
    const composableSource = readSource('src/views/composables/useEnhancedDashboard.ts')

    expect(viewSource).toContain(':color="stat.tone"')
    expect(viewSource).not.toContain(':color="getColorType(stat.color)"')

    expect(composableSource).toContain("tone: 'blue'")
    expect(composableSource).toContain("tone: 'green'")
    expect(composableSource).toContain("tone: 'orange'")
    expect(composableSource).toContain("tone: 'red'")

    expect(composableSource).not.toContain('color: \'#409EFF\'')
    expect(composableSource).not.toContain('color: \'#67C23A\'')
    expect(composableSource).not.toContain('color: \'#E6A23C\'')
    expect(composableSource).not.toContain('color: \'#F56C6C\'')
    expect(composableSource).not.toContain('const getColorType')
  })
})
