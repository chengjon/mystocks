import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 20', () => {
  it('removes legacy cache manager initialization log', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/utils/cache.legacy.js'), 'utf8')

    expect(source).not.toContain("console.log('🗂️ 前端缓存管理器初始化完成')")
  })
})
