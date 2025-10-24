/**
 * 菜单配置文件
 *
 * 集中式菜单配置，支持一级/二级菜单定义和权限控制
 *
 * 菜单项配置说明:
 * - id: 菜单唯一标识
 * - title: 菜单显示标题
 * - path: 路由路径（无子菜单时必填）
 * - icon: 菜单图标（Element Plus Icons）
 * - disabled: 是否禁用
 * - roles: 允许访问的角色列表（可选，用于权限控制）
 * - children: 二级子菜单（可选）
 */

const menuConfig = [
  // 仪表盘
  {
    id: 'dashboard',
    title: '仪表盘',
    path: '/dashboard',
    icon: 'Monitor',
    disabled: false,
    roles: ['admin', 'user']
  },

  // 市场数据
  {
    id: 'market',
    title: '市场数据',
    icon: 'TrendCharts',
    disabled: false,
    roles: ['admin', 'user'],
    children: [
      {
        id: 'market-realtime',
        title: '实时行情',
        path: '/market/realtime',
        icon: 'DataLine',
        disabled: false
      },
      {
        id: 'market-kline',
        title: 'K线图',
        path: '/market/kline',
        icon: 'DataAnalysis',
        disabled: false
      },
      {
        id: 'market-wencai',
        title: '问财筛选',
        path: '/market/wencai',
        icon: 'Search',
        disabled: false
      }
    ]
  },

  // 技术分析
  {
    id: 'technical',
    title: '技术分析',
    icon: 'DataBoard',
    disabled: false,
    roles: ['admin', 'user'],
    children: [
      {
        id: 'technical-indicators',
        title: '技术指标',
        path: '/technical/indicators',
        icon: 'Histogram',
        disabled: false
      },
      {
        id: 'technical-analysis',
        title: '综合分析',
        path: '/technical/analysis',
        icon: 'Odometer',
        disabled: false
      }
    ]
  },

  // 量化策略
  {
    id: 'strategy',
    title: '量化策略',
    icon: 'SetUp',
    disabled: false,
    roles: ['admin', 'user'],
    children: [
      {
        id: 'strategy-management',
        title: '策略管理',
        path: '/strategy/management',
        icon: 'Management',
        disabled: false
      },
      {
        id: 'strategy-backtest',
        title: '回测分析',
        path: '/strategy/backtest',
        icon: 'DataBoard',
        disabled: false
      },
      {
        id: 'strategy-risk',
        title: '风险管理',
        path: '/strategy/risk',
        icon: 'Warning',
        disabled: false
      }
    ]
  },

  // 机器学习
  {
    id: 'ml',
    title: '机器学习',
    icon: 'Connection',
    disabled: false,
    roles: ['admin'],
    children: [
      {
        id: 'ml-training',
        title: '模型训练',
        path: '/ml/training',
        icon: 'School',
        disabled: false
      },
      {
        id: 'ml-prediction',
        title: '价格预测',
        path: '/ml/prediction',
        icon: 'TrendCharts',
        disabled: false
      }
    ]
  },

  // 自选股管理
  {
    id: 'watchlist',
    title: '自选股',
    path: '/watchlist',
    icon: 'Star',
    disabled: false,
    roles: ['admin', 'user']
  },

  // 数据管理
  {
    id: 'data',
    title: '数据管理',
    icon: 'FolderOpened',
    disabled: false,
    roles: ['admin'],
    children: [
      {
        id: 'data-import',
        title: '数据导入',
        path: '/data/import',
        icon: 'Upload',
        disabled: false
      },
      {
        id: 'data-quality',
        title: '数据质量',
        path: '/data/quality',
        icon: 'Checked',
        disabled: false
      }
    ]
  },

  // 系统管理
  {
    id: 'system',
    title: '系统管理',
    icon: 'Setting',
    disabled: false,
    roles: ['admin'],
    children: [
      {
        id: 'system-monitoring',
        title: '系统监控',
        path: '/system/monitoring',
        icon: 'Monitor',
        disabled: false
      },
      {
        id: 'system-logs',
        title: '系统日志',
        path: '/system/logs',
        icon: 'Document',
        disabled: false
      },
      {
        id: 'system-config',
        title: '系统配置',
        path: '/system/config',
        icon: 'Tools',
        disabled: false
      }
    ]
  }
]

/**
 * 根据用户角色过滤菜单
 * @param {Array} menus - 菜单配置数组
 * @param {Array} userRoles - 用户角色数组
 * @returns {Array} 过滤后的菜单
 */
export const filterMenuByRoles = (menus, userRoles = []) => {
  if (!userRoles || userRoles.length === 0) {
    return menus
  }

  return menus.filter(menu => {
    // 如果菜单没有定义roles，默认所有人都可以访问
    if (!menu.roles || menu.roles.length === 0) {
      return true
    }

    // 检查用户角色是否在菜单允许的角色列表中
    const hasPermission = menu.roles.some(role => userRoles.includes(role))

    if (hasPermission && menu.children) {
      // 递归过滤子菜单
      menu.children = filterMenuByRoles(menu.children, userRoles)
    }

    return hasPermission
  })
}

/**
 * 根据菜单路径查找菜单项
 * @param {Array} menus - 菜单配置数组
 * @param {string} path - 路由路径
 * @returns {Object|null} 菜单项对象或null
 */
export const findMenuByPath = (menus, path) => {
  for (const menu of menus) {
    if (menu.path === path) {
      return menu
    }

    if (menu.children) {
      const found = findMenuByPath(menu.children, path)
      if (found) {
        return found
      }
    }
  }

  return null
}

/**
 * 获取菜单的完整路径（面包屑）
 * @param {Array} menus - 菜单配置数组
 * @param {string} path - 路由路径
 * @param {Array} breadcrumb - 累积的面包屑路径
 * @returns {Array} 面包屑数组
 */
export const getMenuBreadcrumb = (menus, path, breadcrumb = []) => {
  for (const menu of menus) {
    const currentPath = [...breadcrumb, menu]

    if (menu.path === path) {
      return currentPath
    }

    if (menu.children) {
      const found = getMenuBreadcrumb(menu.children, path, currentPath)
      if (found) {
        return found
      }
    }
  }

  return null
}

/**
 * 将菜单配置转换为路由配置
 * @param {Array} menus - 菜单配置数组
 * @returns {Array} 路由配置数组
 */
export const menuToRoutes = (menus) => {
  const routes = []

  menus.forEach(menu => {
    if (menu.path) {
      routes.push({
        path: menu.path,
        name: menu.id,
        meta: {
          title: menu.title,
          icon: menu.icon,
          roles: menu.roles
        }
      })
    }

    if (menu.children) {
      routes.push(...menuToRoutes(menu.children))
    }
  })

  return routes
}

/**
 * 扁平化菜单配置（包含所有父子菜单）
 * @param {Array} menus - 菜单配置数组
 * @returns {Array} 扁平化的菜单数组
 */
export const flattenMenus = (menus) => {
  const result = []

  menus.forEach(menu => {
    result.push(menu)

    if (menu.children) {
      result.push(...flattenMenus(menu.children))
    }
  })

  return result
}

// 导出菜单配置
export default menuConfig
