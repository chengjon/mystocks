import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('RealtimePositionPanel style normalization', () => {
  it('moves the position table width into a semantic class', () => {
    const viewSource = readSource('src/components/realtime/RealtimePositionPanel.vue')
    const styleSource = readSource('src/components/realtime/styles/RealtimePositionPanel.scss')

    expect(viewSource).toContain('class="realtime-position-table"')
    expect(viewSource).not.toContain('style="width: 100%"')

    expect(styleSource).toContain('.realtime-position-table')
    expect(styleSource).toContain('width: 100%')
  })
})
