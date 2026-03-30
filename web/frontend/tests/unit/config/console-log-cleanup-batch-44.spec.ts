import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 44', () => {
  it('removes trading center readiness and action logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/artdeco-pages/ArtDecoTradingCenter.vue'), 'utf8')

    expect(source).not.toContain("console.log('Trading Center - 配置系统已就绪')")
    expect(source).not.toContain("console.log('Component action:', action)")
    expect(source).not.toContain("console.log('✅ Trading Center 数据刷新完成')")
  })
})
