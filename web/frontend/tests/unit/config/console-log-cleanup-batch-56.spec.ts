import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 56', () => {
  it('removes artdeco dialog trading setting logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/components/artdeco/base/ArtDecoDialog.vue'), 'utf8')

    expect(source).not.toContain("console.log('更新交易设置:', {")
    expect(source).not.toContain("console.log(tradingPaused.value ? '交易已暂停' : '交易已恢复')")
  })
})
