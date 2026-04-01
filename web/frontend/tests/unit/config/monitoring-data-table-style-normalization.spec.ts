import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('MonitoringDataTable style normalization', () => {
  it('moves default column alignment into semantic classes', () => {
    const viewSource = readSource('src/components/monitoring/MonitoringDataTable.vue')
    const styleSource = readSource('src/components/monitoring/styles/MonitoringDataTable.css')

    expect(viewSource).toContain('getColumnAlignClass(column.align)')
    expect(viewSource).toContain("column.width ? { width: column.width } : undefined")
    expect(viewSource).not.toContain(":style=\"{ width: column.width, textAlign: column.align || 'left' }\"")
    expect(viewSource).not.toContain(":style=\"{ textAlign: column.align || 'left' }\"")

    expect(styleSource).toContain('.column-align--left')
    expect(styleSource).toContain('.column-align--center')
    expect(styleSource).toContain('.column-align--right')
  })
})
