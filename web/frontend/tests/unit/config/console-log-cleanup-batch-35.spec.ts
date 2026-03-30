import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 35', () => {
  it('removes artdeco risk management stub action logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/artdeco-pages/ArtDecoRiskManagement.vue'), 'utf8')

    expect(source).not.toContain("console.log('导出风险报告')")
    expect(source).not.toContain("console.log('打开设置')")
    expect(source).not.toContain("console.log('执行操作:', stock)")
    expect(source).not.toContain("console.log('打开股票选择弹窗')")
  })
})
