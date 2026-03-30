import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 12', () => {
  it('removes runtime websocket route debug logs while keeping docs examples intact', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/composables/useWebSocketWithConfig.ts'), 'utf8')

    expect(source).not.toContain('console.log(`[WebSocket] 订阅路由 ${routeName} 的频道: ${channel}`)')
    expect(source).not.toContain('console.log(`[WebSocket] 取消订阅路由 ${routeName} 的频道: ${channel}`)')
    expect(source).not.toContain('console.log(`[WebSocket] 批量订阅 ${wsRoutes.length} 个路由的WebSocket频道`)')
    expect(source).not.toContain('console.log(`[WebSocket] 订阅 ${routeName} -> ${channel}`)')
    expect(source).not.toContain('console.log(`[WebSocket] 取消所有 ${unsubscribers.length} 个订阅`)')
    expect(source).not.toContain('console.log(`[WebSocket] 路由 ${routeName} 不需要WebSocket`)')

    expect(source).toContain("*   console.log('收到WebSocket消息:', data)")
  })
})
