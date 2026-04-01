import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('StopLossMonitorTab style normalization', () => {
  it('moves risk level background variants into semantic classes', () => {
    const viewSource = readSource('src/views/artdeco-pages/risk-tabs/StopLossMonitorTab.vue')

    expect(viewSource).toContain("'risk-level-bar'")
    expect(viewSource).toContain("'risk-level-bar--critical'")
    expect(viewSource).toContain("'risk-level-bar--watch'")
    expect(viewSource).not.toContain(":style=\"{ background: Number(item.distance) < 2 ? 'var(--artdeco-rise)' : 'var(--artdeco-gold-dim)' }\"")

    expect(viewSource).toContain('.risk-level-bar--critical')
    expect(viewSource).toContain('.risk-level-bar--watch')
  })
})
