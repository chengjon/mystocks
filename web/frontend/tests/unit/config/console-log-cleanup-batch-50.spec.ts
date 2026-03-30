import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 50', () => {
  it('removes example risk management template stub logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/artdeco-pages/_templates/ExampleRiskManagement.vue'), 'utf8')

    expect(source).not.toContain("console.log('导出风险报告')")
    expect(source).not.toContain("console.log('打开设置')")
    expect(source).not.toContain("console.log('执行操作:', stock)")
    expect(source).not.toContain("console.log('打开股票选择弹窗')")
  })
})
