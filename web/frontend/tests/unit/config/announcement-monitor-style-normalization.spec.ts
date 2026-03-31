import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('AnnouncementMonitor style normalization', () => {
  it('moves static filter widths, table widths, and keyword spacing into semantic classes', () => {
    const viewSource = readSource('src/views/announcement/AnnouncementMonitor.vue')
    const styleSource = readSource('src/views/announcement/styles/AnnouncementMonitor.scss')

    expect(viewSource).toContain('class="announcement-filter-input"')
    expect(viewSource).toContain('class="announcement-filter-type"')
    expect(viewSource).toContain('class="announcement-table"')
    expect(viewSource).toContain('class="keyword-tag"')
    expect(viewSource).toContain('class="importance-rate"')
    expect(viewSource).toContain('class="announcement-pagination"')

    expect(viewSource).not.toContain('style="width: 120px"')
    expect(viewSource).not.toContain('style="width: 150px"')
    expect(viewSource).not.toContain('style="width: 100%"')
    expect(viewSource).not.toContain('style="margin-right: 4px; margin-bottom: 4px;"')
    expect(viewSource).not.toContain('style="line-height: 24px;"')
    expect(viewSource).not.toContain('style="margin-top: 20px; text-align: right;"')

    expect(styleSource).toContain('.announcement-filter-input')
    expect(styleSource).toContain('.announcement-filter-type')
    expect(styleSource).toContain('.announcement-table')
    expect(styleSource).toContain('.keyword-tag')
    expect(styleSource).toContain('.importance-rate')
    expect(styleSource).toContain('.announcement-pagination')
  })
})
