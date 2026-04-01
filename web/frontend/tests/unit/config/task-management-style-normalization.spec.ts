import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('TaskManagement style normalization', () => {
  it('moves stat icon border colors into semantic tone classes', () => {
    const viewSource = readSource('src/views/TaskManagement.vue')
    const styleSource = readSource('src/views/styles/TaskManagement.scss')

    expect(viewSource).toContain("'stat-icon'")
    expect(viewSource).toContain('`stat-icon--${stat.tone}`')
    expect(viewSource).toContain("tone: 'info' as const")
    expect(viewSource).toContain("tone: 'success' as const")
    expect(viewSource).toContain("tone: 'warning' as const")

    expect(viewSource).not.toContain(":style=\"{ borderColor: stat.color }\"")
    expect(viewSource).not.toContain("color: '#409eff'")
    expect(viewSource).not.toContain("color: '#67c23a'")
    expect(viewSource).not.toContain("color: '#e6a23c'")

    expect(styleSource).toContain('&--info')
    expect(styleSource).toContain('&--success')
    expect(styleSource).toContain('&--warning')
  })
})
