/**
 * ArtDeco Menu Service
 *
 * 提供菜单相关的API调用和WebSocket连接管理
 * 集成ArtDeco设计令牌和实时数据更新
 *
 * @version 2.0
 * @updated 2026-01-20
 */

import { ref, reactive } from 'vue'
import type { MenuItem } from '@/layouts/MenuConfig.enhanced'
import { ARTDECO_MENU_ENHANCED } from '@/layouts/MenuConfig.enhanced'

// ========== 类型定义 ==========
export interface MenuApiResponse {
  path: string
  data: any
  timestamp: number
}

export interface MenuDataCache {
  [path: string]: {
    data: any
    timestamp: number
    ttl: number
  }
}

export interface WebSocketMessage {
  channel: string
  data: any
  timestamp: number
}

// ========== API基础配置 ==========
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000'

// ========== 缓存配置 ==========
const DEFAULT_CACHE_TTL = 60000 // 60秒
const CACHE: MenuDataCache = {}

// ========== WebSocket连接管理 ==========
class WebSocketManager {
  private ws: WebSocket | null = null
  private channels: Set<string> = new Set()
  private messageHandlers: Map<string, ((data: any) => void)[]> = new Map()
  private reconnectTimer: number | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5

  /**
   * 连接WebSocket
   */
  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return
    }

    try {
      this.ws = new WebSocket(`${WS_BASE_URL}/ws`)

      this.ws.onopen = () => {
        console.log('[WebSocket] Connected')
        this.reconnectAttempts = 0

        // 订阅所有频道
        this.channels.forEach(channel => {
          this.subscribe(channel)
        })
      }

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          this.handleMessage(message)
        } catch (error) {
          console.error('[WebSocket] Message parse error:', error)
        }
      }

      this.ws.onclose = () => {
        console.log('[WebSocket] Disconnected')
        this.scheduleReconnect()
      }

      this.ws.onerror = (error) => {
        console.error('[WebSocket] Error:', error)
      }
    } catch (error) {
      console.error('[WebSocket] Connection error:', error)
      this.scheduleReconnect()
    }
  }

  /**
   * 订阅频道
   */
  subscribe(channel: string, handler?: (data: any) => void): void {
    this.channels.add(channel)

    if (handler) {
      if (!this.messageHandlers.has(channel)) {
        this.messageHandlers.set(channel, [])
      }
      this.messageHandlers.get(channel)?.push(handler)
    }

    // 如果已连接，立即发送订阅消息
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action: 'subscribe', channel }))
    }
  }

  /**
   * 取消订阅频道
   */
  unsubscribe(channel: string, handler?: (data: any) => void): void {
    if (handler) {
      const handlers = this.messageHandlers.get(channel)
      if (handlers) {
        const index = handlers.indexOf(handler)
        if (index > -1) {
          handlers.splice(index, 1)
        }
      }
    } else {
      this.messageHandlers.delete(channel)
    }

    // 如果没有处理器了，从频道集合中移除
    if (!this.messageHandlers.has(channel)) {
      this.channels.delete(channel)

      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ action: 'unsubscribe', channel }))
      }
    }
  }

  /**
   * 处理消息
   */
  private handleMessage(message: WebSocketMessage): void {
    const handlers = this.messageHandlers.get(message.channel)
    if (handlers) {
      handlers.forEach(handler => handler(message.data))
    }
  }

  /**
   * 安排重连
   */
  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WebSocket] Max reconnect attempts reached')
      return
    }

    if (this.reconnectTimer) {
      return
    }

    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000)
    this.reconnectTimer = window.setTimeout(() => {
      this.reconnectAttempts++
      this.reconnectTimer = null
      this.connect()
    }, delay)
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    if (this.ws) {
      this.ws.close()
      this.ws = null
    }

    this.channels.clear()
    this.messageHandlers.clear()
  }
}

// 创建全局WebSocket管理器实例
const wsManager = new WebSocketManager()

// ========== Menu Service类 ==========
export class MenuService {
  private menus: MenuItem[]
  public loading = ref(false)
  public error = ref<string | null>(null)

  constructor(menus: MenuItem[]) {
    this.menus = menus
  }

  /**
   * 获取所有菜单配置
   */
  getMenus(): MenuItem[] {
    return this.menus
  }

  /**
   * 获取菜单数据（带缓存）
   */
  async getMenuData(menuItem: MenuItem, forceRefresh = false): Promise<any> {
    if (!menuItem.apiEndpoint) {
      return null
    }

    // 检查缓存
    if (!forceRefresh) {
      const cached = CACHE[menuItem.path]
      if (cached && Date.now() - cached.timestamp < cached.ttl) {
        return cached.data
      }
    }

    this.loading.value = true
    this.error.value = null

    try {
      const url = `${API_BASE_URL}${menuItem.apiEndpoint}`
      const method = menuItem.apiMethod || 'GET'

      const options: RequestInit = {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
      }

      if (method === 'POST' && menuItem.apiParams) {
        options.body = JSON.stringify(menuItem.apiParams)
      }

      const response = await fetch(url, options)

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()

      // 缓存数据
      CACHE[menuItem.path] = {
        data,
        timestamp: Date.now(),
        ttl: menuItem.liveUpdate ? 5000 : DEFAULT_CACHE_TTL, // 实时数据缓存5秒
      }

      return data
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      this.error.value = errorMessage
      console.error('[MenuService] Fetch error:', errorMessage)
      throw err
    } finally {
      this.loading.value = false
    }
  }

  /**
   * 批量获取菜单数据
   */
  async getBatchMenuData(menuItems: MenuItem[]): Promise<Map<string, any>> {
    const results = new Map<string, any>()

    await Promise.allSettled(
      menuItems.map(async (item) => {
        try {
          const data = await this.getMenuData(item)
          results.set(item.path, data)
        } catch (error) {
          console.error(`[MenuService] Failed to fetch ${item.path}:`, error)
          results.set(item.path, null)
        }
      })
    )

    return results
  }

  /**
   * 订阅菜单实时数据
   */
  subscribeToLiveUpdates(
    menuItem: MenuItem,
    callback: (data: any) => void
  ): () => void {
    if (!menuItem.wsChannel) {
      return () => {}
    }

    // 确保WebSocket已连接
    wsManager.connect()

    // 订阅频道
    wsManager.subscribe(menuItem.wsChannel, callback)

    // 返回取消订阅函数
    return () => {
      if (menuItem.wsChannel) {
        wsManager.unsubscribe(menuItem.wsChannel, callback)
      }
    }
  }

  /**
   * 获取所有实时更新菜单
   */
  getLiveUpdateMenus(): MenuItem[] {
    const liveMenus: MenuItem[] = []

    this.menus.forEach(menu => {
      if (menu.liveUpdate) {
        liveMenus.push(menu)
      }

      if (menu.children) {
        menu.children.forEach(child => {
          if (child.liveUpdate) {
            liveMenus.push(child)
          }
        })
      }
    })

    return liveMenus
  }

  /**
   * 清除缓存
   */
  clearCache(path?: string): void {
    if (path) {
      delete CACHE[path]
    } else {
      Object.keys(CACHE).forEach(key => {
        delete CACHE[key]
      })
    }
  }

  /**
   * 获取加载状态
   */
  isLoading() {
    return this.loading.value
  }

  /**
   * 获取错误信息
   */
  getError() {
    return this.error.value
  }
}

// ========== 创建全局实例 ==========
export const menuService = new MenuService(ARTDECO_MENU_ENHANCED)

// ========== 导出WebSocket管理器 ==========
export { wsManager }

// ========== 组合式API函数 ==========
export function useMenuService() {
  return {
    menus: menuService.getMenus(),
    loading: menuService.loading,  // Return Ref<boolean> instead of value
    error: menuService.error,      // Return Ref<string | null> instead of value
    getMenuData: (menuItem: MenuItem, forceRefresh?: boolean) =>
      menuService.getMenuData(menuItem, forceRefresh),
    getBatchMenuData: (menuItems: MenuItem[]) =>
      menuService.getBatchMenuData(menuItems),
    subscribeToLiveUpdates: (menuItem: MenuItem, callback: (data: any) => void) =>
      menuService.subscribeToLiveUpdates(menuItem, callback),
    getLiveUpdateMenus: () => menuService.getLiveUpdateMenus(),
    clearCache: (path?: string) => menuService.clearCache(path),
  }
}
