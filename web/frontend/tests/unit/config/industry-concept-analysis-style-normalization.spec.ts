import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('IndustryConceptAnalysis style normalization', () => {
  it('moves stat palette variants into semantic classes', () => {
    const viewSource = readSource('src/views/IndustryConceptAnalysis.vue')
    const styleSource = readSource('src/views/styles/IndustryConceptAnalysis.scss')

    expect(viewSource).toContain("'stat-value'")
    expect(viewSource).toContain('`stat-value--${stats[0]?.color || \'gold\'}`')
    expect(viewSource).toContain('`stat-value--${stats[1]?.color || \'gold\'}`')
    expect(viewSource).toContain('`stat-value--${stats[2]?.color || \'gold\'}`')
    expect(viewSource).toContain('`stat-value--${stats[3]?.color || \'gold\'}`')

    expect(viewSource).not.toContain(":style=\"{ color: stats[0]?.color || '#D4AF37' }\"")
    expect(viewSource).not.toContain(":style=\"{ color: stats[1]?.color || '#D4AF37' }\"")
    expect(viewSource).not.toContain(":style=\"{ color: stats[2]?.color || '#D4AF37' }\"")
    expect(viewSource).not.toContain(":style=\"{ color: stats[3]?.color || '#D4AF37' }\"")

    expect(styleSource).toContain('.stat-value--gold')
    expect(styleSource).toContain('.stat-value--blue')
    expect(styleSource).toContain('.stat-value--green')
    expect(styleSource).toContain('.stat-value--red')
  })
})
