import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('PyprofilingDemo tech section style normalization', () => {
  it('moves tech section spacing into semantic classes', () => {
    const viewSource = readSource('src/views/PyprofilingDemo.vue')
    const styleSource = readSource('src/views/styles/PyprofilingDemo.css')
    const sectionStart = viewSource.indexOf('CORE DEPENDENCIES')
    const sectionEnd = viewSource.indexOf('</div>\n    </el-card>\n  </div>\n</template>')
    const techSection = viewSource.slice(sectionStart, sectionEnd)

    expect(techSection).toContain('class="tech-table-offset"')
    expect(techSection).toContain('class="tech-section-heading"')
    expect(techSection).toContain('class="install-command-heading"')
    expect(techSection).toContain('class="install-command-input"')
    expect(techSection).toContain('class="install-command-note"')
    expect(techSection).toContain('class="install-command-code"')
    expect(techSection).toContain('class="tech-font-alert"')
    expect(techSection).toContain('class="font-config-code"')

    expect(techSection).not.toContain('style="margin-top: 15px"')
    expect(techSection).not.toContain('style="margin-top: 30px"')
    expect(techSection).not.toContain('style="margin-top: 10px"')
    expect(techSection).not.toContain('style="margin-top: 10px; color: var(--fg-muted); font-size: 13px"')
    expect(techSection).not.toContain('style="display: block; margin-top: 10px"')

    expect(styleSource).toContain('.tech-table-offset')
    expect(styleSource).toContain('.install-command-note')
    expect(styleSource).toContain('.font-config-code')
  })
})
