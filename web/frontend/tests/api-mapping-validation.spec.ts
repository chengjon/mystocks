/**
 * API Mapping Validation Tests
 *
 * 验证MenuConfig中的菜单项是否正确映射到后端API端点
 * 根据 ARTDECO_MENU_API_MAPPING.md 文档中的映射关系进行验证
 */

import { describe, it, expect } from 'vitest'
import { ARTDECO_MENU_ITEMS } from '@/layouts/MenuConfig'
import type { MenuItem } from '@/layouts/MenuConfig'

describe('API映射验证', () => {
  describe('ARTDECO_MENU_ITEMS基础验证', () => {
    it('应该包含所有6个顶层菜单项', () => {
      // 预期的6个顶层菜单路径
      const expectedPaths = [
        '/dashboard',        // 仪表盘
        '/market/data',      // 市场行情
        '/stocks/management', // 股票管理
        '/analysis/data',    // 投资分析
        '/risk/management',  // 风险管理
        '/strategy/trading', // 策略和交易管理
      ]

      const actualPaths = ARTDECO_MENU_ITEMS.map(item => item.path)

      expect(actualPaths).toEqual(expectedPaths)
      expect(ARTDECO_MENU_ITEMS).toHaveLength(6)
    })

    it('所有顶层菜单项都应该有apiEndpoint', () => {
      const itemsWithoutApiEndpoint = ARTDECO_MENU_ITEMS.filter(
        item => !item.apiEndpoint
      )

      expect(itemsWithoutApiEndpoint).toHaveLength(0)
      expect(
        itemsWithoutApiEndpoint,
        '所有顶层菜单项都应该配置apiEndpoint'
      ).toHaveLength(0)
    })

    it('所有顶层菜单项都应该有apiMethod', () => {
      const itemsWithoutApiMethod = ARTDECO_MENU_ITEMS.filter(
        item => !item.apiMethod
      )

      expect(itemsWithoutApiMethod).toHaveLength(0)
      expect(
        itemsWithoutApiMethod,
        '所有顶层菜单项都应该配置apiMethod'
      ).toHaveLength(0)
    })

    it('所有apiEndpoint都应该以/api开头', () => {
      const invalidEndpoints = ARTDECO_MENU_ITEMS.filter(
        item => item.apiEndpoint && !item.apiEndpoint.startsWith('/api')
      )

      expect(invalidEndpoints).toHaveLength(0)
      expect(
        invalidEndpoints,
        '所有API端点都应该以/api开头'
      ).toHaveLength(0)
    })

    it('所有apiMethod都应该是有效值', () => {
      const validMethods = ['GET', 'POST', 'PUT', 'DELETE']
      const invalidMethods = ARTDECO_MENU_ITEMS.filter(
        item => item.apiMethod && !validMethods.includes(item.apiMethod)
      )

      expect(invalidMethods).toHaveLength(0)
      expect(
        invalidMethods,
        '所有HTTP方法应该是GET、POST、PUT或DELETE'
      ).toHaveLength(0)
    })
  })

  describe('特定菜单项验证', () => {
    it('仪表盘菜单应该映射到正确的API端点', () => {
      const dashboard = ARTDECO_MENU_ITEMS.find(item => item.path === '/dashboard')

      expect(dashboard).toBeDefined()
      expect(dashboard?.label).toBe('仪表盘')
      expect(dashboard?.apiEndpoint).toBe('/api/dashboard/overview')
      expect(dashboard?.apiMethod).toBe('GET')
      expect(dashboard?.liveUpdate).toBe(false)
      expect(dashboard?.wsChannel).toBeUndefined()
      expect(dashboard?.priority).toBe('primary')
      expect(dashboard?.featured).toBe(true)
    })

    it('市场行情菜单应该映射到正确的API端点', () => {
      const market = ARTDECO_MENU_ITEMS.find(item => item.path === '/market/data')

      expect(market).toBeDefined()
      expect(market?.label).toBe('市场行情')
      expect(market?.apiEndpoint).toBe('/api/market/realtime-summary')
      expect(market?.apiMethod).toBe('GET')
      expect(market?.liveUpdate).toBe(true)
      expect(market?.wsChannel).toBe('market:summary')
      expect(market?.priority).toBe('primary')
      expect(market?.featured).toBe(true)
    })

    it('股票管理菜单应该映射到正确的API端点', () => {
      const stocks = ARTDECO_MENU_ITEMS.find(item => item.path === '/stocks/management')

      expect(stocks).toBeDefined()
      expect(stocks?.label).toBe('股票管理')
      expect(stocks?.apiEndpoint).toBe('/api/user/stock-management-summary')
      expect(stocks?.apiMethod).toBe('GET')
      expect(stocks?.liveUpdate).toBe(false)
      expect(stocks?.wsChannel).toBeUndefined()
      expect(stocks?.priority).toBe('secondary')
    })

    it('投资分析菜单应该映射到正确的API端点', () => {
      const analysis = ARTDECO_MENU_ITEMS.find(item => item.path === '/analysis/data')

      expect(analysis).toBeDefined()
      expect(analysis?.label).toBe('投资分析')
      expect(analysis?.apiEndpoint).toBe('/api/analysis/summary')
      expect(analysis?.apiMethod).toBe('GET')
      expect(analysis?.liveUpdate).toBe(false)
      expect(analysis?.wsChannel).toBeUndefined()
      expect(analysis?.priority).toBe('secondary')
    })

    it('风险管理菜单应该映射到正确的API端点', () => {
      const risk = ARTDECO_MENU_ITEMS.find(item => item.path === '/risk/management')

      expect(risk).toBeDefined()
      expect(risk?.label).toBe('风险管理')
      expect(risk?.apiEndpoint).toBe('/api/risk/overview')
      expect(risk?.apiMethod).toBe('GET')
      expect(risk?.liveUpdate).toBe(true)
      expect(risk?.wsChannel).toBe('risk:overview')
      expect(risk?.priority).toBe('secondary')
    })

    it('策略和交易管理菜单应该映射到正确的API端点', () => {
      const strategy = ARTDECO_MENU_ITEMS.find(item => item.path === '/strategy/trading')

      expect(strategy).toBeDefined()
      expect(strategy?.label).toBe('策略和交易管理')
      expect(strategy?.apiEndpoint).toBe('/api/strategy/overview')
      expect(strategy?.apiMethod).toBe('GET')
      expect(strategy?.liveUpdate).toBe(true)
      expect(strategy?.wsChannel).toBe('strategy:overview')
      expect(strategy?.priority).toBe('secondary')
    })
  })

  describe('WebSocket频道验证', () => {
    it('所有liveUpdate为true的菜单项都应该有wsChannel', () => {
      const itemsWithLiveUpdate = ARTDECO_MENU_ITEMS.filter(
        item => item.liveUpdate === true
      )

      const itemsWithoutWsChannel = itemsWithLiveUpdate.filter(
        item => !item.wsChannel
      )

      expect(itemsWithoutWsChannel).toHaveLength(0)
      expect(
        itemsWithoutWsChannel,
        '所有启用实时更新的菜单项都应该配置WebSocket频道'
      ).toHaveLength(0)
    })

    it('所有wsChannel都应该遵循命名规范', () => {
      const wsChannelPattern = /^[a-z]+:[a-z_]+$/

      const itemsWithWsChannel = ARTDECO_MENU_ITEMS.filter(
        item => item.wsChannel
      )

      const invalidChannels = itemsWithWsChannel.filter(
        item => !wsChannelPattern.test(item.wsChannel!)
      )

      expect(invalidChannels).toHaveLength(0)
      expect(
        invalidChannels,
        'WebSocket频道应该遵循格式: entity:action (如 market:summary)'
      ).toHaveLength(0)
    })

    it('应该有3个菜单项启用实时更新', () => {
      const itemsWithLiveUpdate = ARTDECO_MENU_ITEMS.filter(
        item => item.liveUpdate === true
      )

      expect(itemsWithLiveUpdate).toHaveLength(3)

      const channels = itemsWithLiveUpdate.map(item => item.wsChannel).sort()
      expect(channels).toEqual(['market:summary', 'risk:overview', 'strategy:overview'])
    })
  })

  describe('优先级和特色标记验证', () => {
    it('应该有2个primary优先级菜单项', () => {
      const primaryItems = ARTDECO_MENU_ITEMS.filter(
        item => item.priority === 'primary'
      )

      expect(primaryItems).toHaveLength(2)

      const paths = primaryItems.map(item => item.path).sort()
      expect(paths).toEqual(['/dashboard', '/market/data'])
    })

    it('应该有4个secondary优先级菜单项', () => {
      const secondaryItems = ARTDECO_MENU_ITEMS.filter(
        item => item.priority === 'secondary'
      )

      expect(secondaryItems).toHaveLength(4)

      const paths = secondaryItems.map(item => item.path).sort()
      expect(paths).toEqual([
        '/analysis/data',
        '/risk/management',
        '/stocks/management',
        '/strategy/trading'
      ])
    })

    it('应该有2个featured菜单项', () => {
      const featuredItems = ARTDECO_MENU_ITEMS.filter(
        item => item.featured === true
      )

      expect(featuredItems).toHaveLength(2)

      const paths = featuredItems.map(item => item.path).sort()
      expect(paths).toEqual(['/dashboard', '/market/data'])
    })

    it('所有featured菜单项都应该是primary优先级', () => {
      const featuredItems = ARTDECO_MENU_ITEMS.filter(
        item => item.featured === true
      )

      const nonPrimaryFeatured = featuredItems.filter(
        item => item.priority !== 'primary'
      )

      expect(nonPrimaryFeatured).toHaveLength(0)
    })
  })

  describe('API端点路径验证', () => {
    it('API端点路径应该使用正确的模块前缀', () => {
      const expectedModules = [
        'dashboard',   // /api/dashboard/*
        'market',      // /api/market/*
        'user',        // /api/user/*
        'analysis',    // /api/analysis/*
        'risk',        // /api/risk/*
        'strategy'     // /api/strategy/*
      ]

      ARTDECO_MENU_ITEMS.forEach(item => {
        expect(item.apiEndpoint).toBeTruthy()

        const endpointParts = item.apiEndpoint!.split('/')
        const module = endpointParts[2] // /api/MODULE/...

        expect(expectedModules).toContain(module)
      })
    })

    it('不应该有重复的API端点', () => {
      const endpoints = ARTDECO_MENU_ITEMS.map(item => item.apiEndpoint)
      const uniqueEndpoints = new Set(endpoints)

      expect(uniqueEndpoints.size).toBe(endpoints.length)
      expect(
        uniqueEndpoints.size,
        '不应该有重复的API端点'
      ).toBe(endpoints.length)
    })
  })

  describe('描述和图标验证', () => {
    it('所有菜单项都应该有图标', () => {
      const itemsWithoutIcon = ARTDECO_MENU_ITEMS.filter(
        item => !item.icon
      )

      expect(itemsWithoutIcon).toHaveLength(0)
    })

    it('所有菜单项都应该有描述', () => {
      const itemsWithoutDescription = ARTDECO_MENU_ITEMS.filter(
        item => !item.description
      )

      expect(itemsWithoutDescription).toHaveLength(0)
    })

    it('描述应该是中文', () => {
      const chinesePattern = /[\u4e00-\u9fa5]/

      ARTDECO_MENU_ITEMS.forEach(item => {
        expect(item.description).toMatch(chinesePattern)
      })
    })
  })

  describe('数据类型验证', () => {
    it('所有必需字段都应该存在', () => {
      const requiredFields: (keyof MenuItem)[] = [
        'path',
        'label',
        'icon',
        'apiEndpoint',
        'apiMethod'
      ]

      ARTDECO_MENU_ITEMS.forEach(item => {
        requiredFields.forEach(field => {
          expect(item[field]).toBeDefined()
          expect(item[field]).toBeTruthy()
        })
      })
    })

    it('可选字段应该有正确的类型', () => {
      ARTDECO_MENU_ITEMS.forEach(item => {
        if (item.liveUpdate !== undefined) {
          expect(typeof item.liveUpdate).toBe('boolean')
        }

        if (item.wsChannel !== undefined) {
          expect(typeof item.wsChannel).toBe('string')
        }

        if (item.priority !== undefined) {
          expect(['primary', 'secondary', 'tertiary']).toContain(item.priority)
        }

        if (item.featured !== undefined) {
          expect(typeof item.featured).toBe('boolean')
        }

        if (item.lastUpdate !== undefined) {
          expect(typeof item.lastUpdate).toBe('number')
        }

        if (item.count !== undefined) {
          expect(typeof item.count).toBe('number')
        }

        if (item.error !== undefined) {
          expect(typeof item.error).toBe('boolean')
        }

        if (item.status !== undefined) {
          expect(['idle', 'loading', 'success', 'error']).toContain(item.status)
        }
      })
    })
  })

  describe('与文档映射表一致性验证', () => {
    /**
     * 根据 docs/guides/ARTDECO_MENU_API_MAPPING.md 文档验证映射关系
     */

    it('应该与文档中的44个菜单项映射一致', () => {
      // 注：本文档验证仅验证顶层6个菜单项
      // 子菜单项的验证需要在后续添加

      const documentMapping = {
        '/dashboard': {
          apiEndpoint: '/api/dashboard/overview',
          apiMethod: 'GET',
          liveUpdate: false
        },
        '/market/data': {
          apiEndpoint: '/api/market/realtime-summary',
          apiMethod: 'GET',
          liveUpdate: true
        },
        '/stocks/management': {
          apiEndpoint: '/api/user/stock-management-summary',
          apiMethod: 'GET',
          liveUpdate: false
        },
        '/analysis/data': {
          apiEndpoint: '/api/analysis/summary',
          apiMethod: 'GET',
          liveUpdate: false
        },
        '/risk/management': {
          apiEndpoint: '/api/risk/overview',
          apiMethod: 'GET',
          liveUpdate: true
        },
        '/strategy/trading': {
          apiEndpoint: '/api/strategy/overview',
          apiMethod: 'GET',
          liveUpdate: true
        }
      }

      ARTDECO_MENU_ITEMS.forEach(item => {
        const expected = documentMapping[item.path as keyof typeof documentMapping]

        expect(expected).toBeDefined()
        expect(item.apiEndpoint).toBe(expected!.apiEndpoint)
        expect(item.apiMethod).toBe(expected!.apiMethod)
        expect(item.liveUpdate).toBe(expected!.liveUpdate)
      })
    })
  })
})
