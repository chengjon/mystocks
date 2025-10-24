/**
 * 路由工具函数
 *
 * 提供路由生成、权限检查、菜单激活状态等实用函数
 */

import { useRouter, useRoute } from 'vue-router'

/**
 * 根据菜单配置生成路由配置
 * @param {Array} menuList - 菜单配置列表
 * @param {Object} options - 选项配置
 * @returns {Array} 路由配置数组
 */
export const generateRoutesFromMenu = (menuList, options = {}) => {
  const {
    parentPath = '',
    layoutComponent = null,
    defaultComponent = null
  } = options

  const routes = []

  menuList.forEach(menu => {
    const route = {
      path: menu.path || `${parentPath}/${menu.id}`,
      name: menu.id,
      meta: {
        title: menu.title,
        icon: menu.icon,
        roles: menu.roles || [],
        disabled: menu.disabled || false
      }
    }

    // 如果有子菜单
    if (menu.children && menu.children.length > 0) {
      route.children = generateRoutesFromMenu(menu.children, {
        parentPath: route.path,
        layoutComponent,
        defaultComponent
      })

      // 父路由使用布局组件
      if (layoutComponent) {
        route.component = layoutComponent
      }
    } else {
      // 叶子路由使用默认组件或动态导入
      if (defaultComponent) {
        route.component = defaultComponent
      } else {
        // 动态导入对应的页面组件
        const componentPath = menu.path.replace(/^\//, '').replace(/\//g, '/')
        route.component = () => import(`@/views/${componentPath}.vue`)
      }
    }

    routes.push(route)
  })

  return routes
}

/**
 * 检查当前用户是否有权限访问路由
 * @param {Object} route - 路由对象
 * @param {Array} userRoles - 用户角色列表
 * @returns {boolean} 是否有权限
 */
export const hasRoutePermission = (route, userRoles = []) => {
  // 如果路由没有定义角色要求，默认允许访问
  if (!route.meta || !route.meta.roles || route.meta.roles.length === 0) {
    return true
  }

  // 检查用户角色是否在路由允许的角色列表中
  return route.meta.roles.some(role => userRoles.includes(role))
}

/**
 * 过滤路由列表，只保留有权限的路由
 * @param {Array} routes - 路由配置列表
 * @param {Array} userRoles - 用户角色列表
 * @returns {Array} 过滤后的路由列表
 */
export const filterRoutesByPermission = (routes, userRoles = []) => {
  return routes.filter(route => {
    const hasPermission = hasRoutePermission(route, userRoles)

    if (hasPermission && route.children) {
      // 递归过滤子路由
      route.children = filterRoutesByPermission(route.children, userRoles)
    }

    return hasPermission
  })
}

/**
 * 获取当前激活的菜单路径
 * @param {string} currentPath - 当前路由路径
 * @param {Array} menuList - 菜单配置列表
 * @returns {string} 激活的菜单路径
 */
export const getActiveMenuPath = (currentPath, menuList) => {
  for (const menu of menuList) {
    // 精确匹配
    if (menu.path === currentPath) {
      return menu.path
    }

    // 模糊匹配（用于子路由）
    if (currentPath.startsWith(menu.path + '/')) {
      return menu.path
    }

    // 递归查找子菜单
    if (menu.children) {
      const activePath = getActiveMenuPath(currentPath, menu.children)
      if (activePath) {
        return activePath
      }
    }
  }

  return currentPath
}

/**
 * 查找路由对象
 * @param {Array} routes - 路由配置列表
 * @param {string} path - 路由路径
 * @returns {Object|null} 路由对象或null
 */
export const findRoute = (routes, path) => {
  for (const route of routes) {
    if (route.path === path) {
      return route
    }

    if (route.children) {
      const found = findRoute(route.children, path)
      if (found) {
        return found
      }
    }
  }

  return null
}

/**
 * 获取路由的面包屑路径
 * @param {string} path - 当前路由路径
 * @param {Array} routes - 路由配置列表
 * @returns {Array} 面包屑数组
 */
export const getRouteBreadcrumb = (path, routes, breadcrumb = []) => {
  for (const route of routes) {
    const currentPath = [...breadcrumb, {
      path: route.path,
      title: route.meta?.title || route.name,
      icon: route.meta?.icon
    }]

    if (route.path === path) {
      return currentPath
    }

    if (route.children) {
      const found = getRouteBreadcrumb(path, route.children, currentPath)
      if (found) {
        return found
      }
    }
  }

  return null
}

/**
 * 扁平化路由配置（包含所有嵌套路由）
 * @param {Array} routes - 路由配置列表
 * @returns {Array} 扁平化的路由数组
 */
export const flattenRoutes = (routes) => {
  const result = []

  routes.forEach(route => {
    result.push(route)

    if (route.children) {
      result.push(...flattenRoutes(route.children))
    }
  })

  return result
}

/**
 * 获取默认首页路径
 * @param {Array} routes - 路由配置列表
 * @param {Array} userRoles - 用户角色列表
 * @returns {string} 默认首页路径
 */
export const getDefaultHomePath = (routes, userRoles = []) => {
  const accessibleRoutes = filterRoutesByPermission(routes, userRoles)

  if (accessibleRoutes.length === 0) {
    return '/404'
  }

  // 返回第一个有权限的路由
  const firstRoute = accessibleRoutes[0]

  // 如果有子路由，返回第一个子路由
  if (firstRoute.children && firstRoute.children.length > 0) {
    return firstRoute.children[0].path
  }

  return firstRoute.path
}

/**
 * 检查路径是否匹配（支持通配符）
 * @param {string} pattern - 模式字符串（支持*通配符）
 * @param {string} path - 待检查的路径
 * @returns {boolean} 是否匹配
 */
export const matchPath = (pattern, path) => {
  // 将通配符模式转换为正则表达式
  const regexPattern = pattern
    .replace(/\//g, '\\/')
    .replace(/\*/g, '.*')

  const regex = new RegExp(`^${regexPattern}$`)
  return regex.test(path)
}

/**
 * 导航到路由（带权限检查）
 * @param {Object} router - Vue Router实例
 * @param {string} path - 目标路径
 * @param {Array} userRoles - 用户角色列表
 * @param {Object} options - 导航选项
 * @returns {Promise} 导航Promise
 */
export const navigateTo = async (router, path, userRoles = [], options = {}) => {
  const {
    replace = false,
    query = {},
    params = {}
  } = options

  // 查找目标路由
  const routes = router.getRoutes()
  const targetRoute = routes.find(r => r.path === path)

  if (!targetRoute) {
    console.error(`Route not found: ${path}`)
    return router.push('/404')
  }

  // 检查权限
  if (!hasRoutePermission(targetRoute, userRoles)) {
    console.warn(`No permission to access: ${path}`)
    return router.push('/403')
  }

  // 执行导航
  const navigationMethod = replace ? router.replace : router.push

  return navigationMethod({
    path,
    query,
    params
  })
}

/**
 * 获取路由参数
 * @returns {Object} 路由参数对象
 */
export const useRouteParams = () => {
  const route = useRoute()

  return {
    params: route.params,
    query: route.query,
    hash: route.hash,
    fullPath: route.fullPath,
    path: route.path,
    name: route.name,
    meta: route.meta
  }
}

/**
 * 返回上一页（带回退检查）
 * @param {Object} router - Vue Router实例
 * @param {string} fallbackPath - 回退路径（当没有历史记录时）
 */
export const goBack = (router, fallbackPath = '/') => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push(fallbackPath)
  }
}

/**
 * 刷新当前路由
 * @param {Object} router - Vue Router实例
 * @param {Object} route - 当前路由对象
 */
export const refreshRoute = async (router, route) => {
  // 先跳转到一个临时路由
  await router.replace({
    path: '/redirect' + route.fullPath
  })
}

/**
 * 检查路由是否处于激活状态
 * @param {string} routePath - 路由路径
 * @param {string} currentPath - 当前路径
 * @param {boolean} exact - 是否精确匹配
 * @returns {boolean} 是否激活
 */
export const isRouteActive = (routePath, currentPath, exact = false) => {
  if (exact) {
    return routePath === currentPath
  }

  return currentPath.startsWith(routePath)
}

// 默认导出所有工具函数
export default {
  generateRoutesFromMenu,
  hasRoutePermission,
  filterRoutesByPermission,
  getActiveMenuPath,
  findRoute,
  getRouteBreadcrumb,
  flattenRoutes,
  getDefaultHomePath,
  matchPath,
  navigateTo,
  useRouteParams,
  goBack,
  refreshRoute,
  isRouteActive
}
