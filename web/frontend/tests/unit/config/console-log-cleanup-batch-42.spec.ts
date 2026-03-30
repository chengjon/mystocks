import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 42', () => {
  it('removes artdeco trading management stub action logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/artdeco-pages/composables/useArtDecoTradingManagement.ts'), 'utf8')

    expect(source).not.toContain("console.log('导出CSV')")
    expect(source).not.toContain("console.log('批量执行')")
    expect(source).not.toContain("console.log('刷新数据 - API端点:', apiEndpoint.value)")
    expect(source).not.toContain("console.log('打开设置')")
    expect(source).not.toContain("console.log('停止交易信号')")
    expect(source).not.toContain("console.log('更新配置:', config)")
    expect(source).not.toContain("console.log('关闭持仓:', positionId)")
    expect(source).not.toContain("console.log('调整持仓:', positionId, adjustment)")
    expect(source).not.toContain("console.log('执行信号:', signalId)")
    expect(source).not.toContain("console.log('取消信号:', signalId)")
    expect(source).not.toContain("console.log('历史筛选:', filters)")
    expect(source).not.toContain("console.log('导出历史:', format)")
    expect(source).not.toContain("console.log('Loading more history...')")
  })
})
