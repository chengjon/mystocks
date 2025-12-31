/**
 * User & Watchlist Module Data Adapters
 *
 * Transforms API responses into ViewModels for UI components.
 */

import type {
  UserProfileResponse,
  WatchlistResponse,
  NotificationResponse
} from '@/api/types/generated-types'

// ViewModel interfaces
export interface UserProfileVM {
  userId: string
  username: string
  email: string
  displayName: string
  avatar?: string
  role: 'admin' | 'user' | 'premium'
  status: 'active' | 'inactive' | 'suspended'
  preferences: UserPreferencesVM
  permissions: UserPermissionsVM
  subscription: SubscriptionVM
  statistics: UserStatisticsVM
  createdAt: string
  lastLoginAt: string
  lastUpdateAt: string
}

export interface UserPreferencesVM {
  theme: 'light' | 'dark' | 'auto'
  language: 'zh-CN' | 'en-US'
  timezone: string
  dateFormat: 'YYYY-MM-DD' | 'MM/DD/YYYY' | 'DD/MM/YYYY'
  timeFormat: '24h' | '12h'
  defaultDashboard: string
  watchlistLayout: 'grid' | 'list' | 'card'
  chartSettings: {
    defaultPeriod: string
    showVolume: boolean
    showMA: boolean
    indicators: string[]
  }
  notifications: NotificationPreferencesVM
  privacy: PrivacyPreferencesVM
}

export interface NotificationPreferencesVM {
  email: boolean
  push: boolean
  sms: boolean
  priceAlerts: boolean
  orderStatus: boolean
  systemUpdates: boolean
  marketNews: boolean
  strategySignals: boolean
}

export interface PrivacyPreferencesVM {
  profileVisibility: 'public' | 'private' | 'friends'
  showRealName: boolean
  showEmail: boolean
  showTradingStats: boolean
  allowDirectMessages: boolean
  dataSharing: boolean
}

export interface UserPermissionsVM {
  canTrade: boolean
  canWithdraw: boolean
  canUseStrategies: boolean
  canAccessAdvancedFeatures: boolean
  canViewMarketData: boolean
  canExportData: boolean
  canManageUsers: boolean
  canViewAnalytics: boolean
  maxStrategies: number
  maxWatchlists: number
  maxApiCalls: number
}

export interface SubscriptionVM {
  plan: 'free' | 'basic' | 'premium' | 'enterprise'
  status: 'active' | 'inactive' | 'cancelled' | 'expired'
  startDate: string
  endDate: string
  trialEndDate?: string
  autoRenew: boolean
  features: string[]
  limits: {
    maxStrategies: number
    maxWatchlists: number
    maxApiCallsPerDay: number
    maxDataRetention: number
  }
  nextBillingAmount?: number
  nextBillingDate?: string
}

export interface UserStatisticsVM {
  totalTrades: number
  winningTrades: number
  losingTrades: number
  winRate: number
  totalPnL: number
  totalPnLPercent: string
  averageReturn: number
  sharpeRatio: number
  maxDrawdown: number
  totalCommission: number
  joinDate: string
  activeStrategies: number
  activeWatchlists: number
  followers: number
  following: number
}

export interface WatchlistVM {
  id: string
  name: string
  description?: string
  isDefault: boolean
  isPublic: boolean
  owner: {
    userId: string
    username: string
    displayName: string
  }
  stocks: WatchlistStockVM[]
  statistics: WatchlistStatisticsVM
  tags: string[]
  createdAt: string
  updatedAt: string
  lastViewedAt?: string
  sortOrder: number
}

export interface WatchlistStockVM {
  symbol: string
  name: string
  market: string
  currentPrice: number
  changeAmount: number
  changePercent: string
  volume: number
  marketCap: number
  pe?: number
  pb?: number
  addedAt: string
  notes?: string
  alerts: StockAlertVM[]
  customFields?: Record<string, any>
}

export interface StockAlertVM {
  id: string
  type: 'price' | 'percent' | 'volume' | 'technical'
  condition: 'above' | 'below' | 'equal'
  value: number
  isActive: boolean
  triggeredAt?: string
  expiresAt?: string
  notificationMethod: 'email' | 'push' | 'sms' | 'all'
}

export interface WatchlistStatisticsVM {
  totalStocks: number
  totalValue: number
  todayChange: number
  todayChangePercent: string
  bestPerformer: {
    symbol: string
    name: string
    changePercent: string
  }
  worstPerformer: {
    symbol: string
    name: string
    changePercent: string
  }
  sectors: Array<{
    name: string
    count: number
    weight: number
  }>
}

export interface NotificationVM {
  id: string
  type: 'system' | 'price_alert' | 'order' | 'strategy' | 'social' | 'market'
  title: string
  message: string
  data?: Record<string, any>
  priority: 'low' | 'medium' | 'high' | 'urgent'
  isRead: boolean
  createdAt: string
  expiresAt?: string
  actionUrl?: string
  actionText?: string
  icon?: string
  category: string
}

export class UserAdapter {
  /**
   * Convert user profile to ViewModel
   */
  static toUserProfileVM(data: UserProfileResponse): UserProfileVM {
    return {
      userId: data.userId || '',
      username: data.username || '',
      email: data.email || '',
      displayName: data.displayName || data.username || '',
      avatar: data.avatar,
      role: this.getUserRole(data.role),
      status: this.getUserStatus(data.status),
      preferences: this.toUserPreferencesVM(data.preferences),
      permissions: this.toUserPermissionsVM(data.permissions),
      subscription: this.toSubscriptionVM(data.subscription),
      statistics: this.toUserStatisticsVM(data.statistics),
      createdAt: this.formatDateTime(data.createdAt),
      lastLoginAt: this.formatDateTime(data.lastLoginAt),
      lastUpdateAt: this.formatDateTime(data.lastUpdateAt)
    }
  }

  /**
   * Convert watchlist to ViewModel
   */
  static toWatchlistVM(data: WatchlistResponse[]): WatchlistVM[] {
    return data.map(watchlist => ({
      id: watchlist.id || '',
      name: watchlist.name || '',
      description: watchlist.description,
      isDefault: watchlist.isDefault || false,
      isPublic: watchlist.isPublic || false,
      owner: {
        userId: watchlist.owner?.userId || '',
        username: watchlist.owner?.username || '',
        displayName: watchlist.owner?.displayName || ''
      },
      stocks: (watchlist.stocks || []).map(stock => ({
        symbol: stock.symbol || '',
        name: stock.name || '',
        market: stock.market || 'A',
        currentPrice: stock.currentPrice || 0,
        changeAmount: stock.changeAmount || 0,
        changePercent: this.formatPercent(stock.changePercent),
        volume: stock.volume || 0,
        marketCap: stock.marketCap || 0,
        pe: stock.pe,
        pb: stock.pb,
        addedAt: this.formatDateTime(stock.addedAt),
        notes: stock.notes,
        alerts: (stock.alerts || []).map(alert => ({
          id: alert.id || '',
          type: alert.type || 'price',
          condition: alert.condition || 'above',
          value: alert.value || 0,
          isActive: alert.isActive !== false,
          triggeredAt: this.formatDateTime(alert.triggeredAt),
          expiresAt: this.formatDateTime(alert.expiresAt),
          notificationMethod: alert.notificationMethod || 'push'
        })),
        customFields: stock.customFields
      })),
      statistics: this.toWatchlistStatisticsVM(watchlist.statistics),
      tags: watchlist.tags || [],
      createdAt: this.formatDateTime(watchlist.createdAt),
      updatedAt: this.formatDateTime(watchlist.updatedAt),
      lastViewedAt: this.formatDateTime(watchlist.lastViewedAt),
      sortOrder: watchlist.sortOrder || 0
    }))
  }

  /**
   * Convert notifications to ViewModel
   */
  static toNotificationVM(data: NotificationResponse[]): NotificationVM[] {
    return data.map(notification => ({
      id: notification.id || '',
      type: (notification.type || 'system') as any,
      title: notification.title || '',
      message: notification.message || '',
      data: notification.data,
      priority: this.getNotificationPriority(notification.priority),
      isRead: notification.isRead || false,
      createdAt: this.formatDateTime(notification.createdAt),
      expiresAt: this.formatDateTime(notification.expiresAt),
      actionUrl: notification.actionUrl,
      actionText: notification.actionText,
      icon: notification.icon,
      category: notification.category || 'general'
    }))
  }

  /**
   * Convert user preferences to ViewModel
   */
  private static toUserPreferencesVM(preferences: any): UserPreferencesVM {
    return {
      theme: preferences.theme || 'auto',
      language: preferences.language || 'zh-CN',
      timezone: preferences.timezone || 'Asia/Shanghai',
      dateFormat: preferences.dateFormat || 'YYYY-MM-DD',
      timeFormat: preferences.timeFormat || '24h',
      defaultDashboard: preferences.defaultDashboard || 'overview',
      watchlistLayout: preferences.watchlistLayout || 'grid',
      chartSettings: {
        defaultPeriod: preferences.chartSettings?.defaultPeriod || '1D',
        showVolume: preferences.chartSettings?.showVolume !== false,
        showMA: preferences.chartSettings?.showMA !== false,
        indicators: preferences.chartSettings?.indicators || []
      },
      notifications: this.toNotificationPreferencesVM(preferences.notifications),
      privacy: this.toPrivacyPreferencesVM(preferences.privacy)
    }
  }

  /**
   * Convert notification preferences to ViewModel
   */
  private static toNotificationPreferencesVM(notifications: any): NotificationPreferencesVM {
    return {
      email: notifications?.email !== false,
      push: notifications?.push !== false,
      sms: notifications?.sms || false,
      priceAlerts: notifications?.priceAlerts !== false,
      orderStatus: notifications?.orderStatus !== false,
      systemUpdates: notifications?.systemUpdates !== false,
      marketNews: notifications?.marketNews !== false,
      strategySignals: notifications?.strategySignals !== false
    }
  }

  /**
   * Convert privacy preferences to ViewModel
   */
  private static toPrivacyPreferencesVM(privacy: any): PrivacyPreferencesVM {
    return {
      profileVisibility: privacy?.profileVisibility || 'private',
      showRealName: privacy?.showRealName || false,
      showEmail: privacy?.showEmail || false,
      showTradingStats: privacy?.showTradingStats !== false,
      allowDirectMessages: privacy?.allowDirectMessages !== false,
      dataSharing: privacy?.dataSharing || false
    }
  }

  /**
   * Convert user permissions to ViewModel
   */
  private static toUserPermissionsVM(permissions: any): UserPermissionsVM {
    return {
      canTrade: permissions?.canTrade !== false,
      canWithdraw: permissions?.canWithdraw !== false,
      canUseStrategies: permissions?.canUseStrategies !== false,
      canAccessAdvancedFeatures: permissions?.canAccessAdvancedFeatures || false,
      canViewMarketData: permissions?.canViewMarketData !== false,
      canExportData: permissions?.canExportData !== false,
      canManageUsers: permissions?.canManageUsers || false,
      canViewAnalytics: permissions?.canViewAnalytics !== false,
      maxStrategies: permissions?.maxStrategies || 5,
      maxWatchlists: permissions?.maxWatchlists || 10,
      maxApiCalls: permissions?.maxApiCalls || 1000
    }
  }

  /**
   * Convert subscription to ViewModel
   */
  private static toSubscriptionVM(subscription: any): SubscriptionVM {
    return {
      plan: subscription?.plan || 'free',
      status: subscription?.status || 'active',
      startDate: this.formatDate(subscription?.startDate),
      endDate: this.formatDate(subscription?.endDate),
      trialEndDate: this.formatDate(subscription?.trialEndDate),
      autoRenew: subscription?.autoRenew !== false,
      features: subscription?.features || [],
      limits: {
        maxStrategies: subscription?.limits?.maxStrategies || 5,
        maxWatchlists: subscription?.limits?.maxWatchlists || 10,
        maxApiCallsPerDay: subscription?.limits?.maxApiCallsPerDay || 1000,
        maxDataRetention: subscription?.limits?.maxDataRetention || 30
      },
      nextBillingAmount: subscription?.nextBillingAmount,
      nextBillingDate: this.formatDate(subscription?.nextBillingDate)
    }
  }

  /**
   * Convert user statistics to ViewModel
   */
  private static toUserStatisticsVM(statistics: any): UserStatisticsVM {
    const winRate = statistics?.totalTrades ? (statistics.winningTrades / statistics.totalTrades) * 100 : 0
    const totalPnLPercent = statistics?.totalInvested ? (statistics.totalPnL / statistics.totalInvested) * 100 : 0

    return {
      totalTrades: statistics?.totalTrades || 0,
      winningTrades: statistics?.winningTrades || 0,
      losingTrades: statistics?.losingTrades || 0,
      winRate,
      totalPnL: statistics?.totalPnL || 0,
      totalPnLPercent: this.formatPercent(totalPnLPercent),
      averageReturn: statistics?.averageReturn || 0,
      sharpeRatio: statistics?.sharpeRatio || 0,
      maxDrawdown: statistics?.maxDrawdown || 0,
      totalCommission: statistics?.totalCommission || 0,
      joinDate: this.formatDate(statistics?.joinDate),
      activeStrategies: statistics?.activeStrategies || 0,
      activeWatchlists: statistics?.activeWatchlists || 0,
      followers: statistics?.followers || 0,
      following: statistics?.following || 0
    }
  }

  /**
   * Convert watchlist statistics to ViewModel
   */
  private static toWatchlistStatisticsVM(statistics: any): WatchlistStatisticsVM {
    return {
      totalStocks: statistics?.totalStocks || 0,
      totalValue: statistics?.totalValue || 0,
      todayChange: statistics?.todayChange || 0,
      todayChangePercent: this.formatPercent(statistics?.todayChangePercent),
      bestPerformer: {
        symbol: statistics?.bestPerformer?.symbol || '',
        name: statistics?.bestPerformer?.name || '',
        changePercent: this.formatPercent(statistics?.bestPerformer?.changePercent)
      },
      worstPerformer: {
        symbol: statistics?.worstPerformer?.symbol || '',
        name: statistics?.worstPerformer?.name || '',
        changePercent: this.formatPercent(statistics?.worstPerformer?.changePercent)
      },
      sectors: (statistics?.sectors || []).map((sector: any) => ({
        name: sector.name || '',
        count: sector.count || 0,
        weight: sector.weight || 0
      }))
    }
  }

  /**
   * Get user role
   */
  private static getUserRole(role: string): 'admin' | 'user' | 'premium' {
    switch (role?.toLowerCase()) {
      case 'admin':
        return 'admin'
      case 'premium':
      case 'vip':
        return 'premium'
      default:
        return 'user'
    }
  }

  /**
   * Get user status
   */
  private static getUserStatus(status: string): 'active' | 'inactive' | 'suspended' {
    switch (status?.toLowerCase()) {
      case 'active':
        return 'active'
      case 'suspended':
      case 'banned':
        return 'suspended'
      default:
        return 'inactive'
    }
  }

  /**
   * Get notification priority
   */
  private static getNotificationPriority(priority: string): 'low' | 'medium' | 'high' | 'urgent' {
    switch (priority?.toLowerCase()) {
      case 'urgent':
        return 'urgent'
      case 'high':
        return 'high'
      case 'medium':
        return 'medium'
      default:
        return 'low'
    }
  }

  /**
   * Format percentage
   */
  private static formatPercent(value: number): string {
    if (!value) return '0.00%'
    const sign = value >= 0 ? '+' : ''
    return `${sign}${value.toFixed(2)}%`
  }

  /**
   * Format date and time
   */
  private static formatDateTime(timestamp: string | number | Date | undefined): string {
    if (!timestamp) return ''
    const date = new Date(timestamp)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  /**
   * Format date only
   */
  private static formatDate(timestamp: string | number | Date | undefined): string {
    if (!timestamp) return ''
    const date = new Date(timestamp)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  }

  /**
   * Format currency
   */
  static formatCurrency(amount: number, currency: string = '¥'): string {
    return `${currency}${amount.toLocaleString('zh-CN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`
  }

  /**
   * Format large number
   */
  static formatLargeNumber(num: number): string {
    if (num >= 100000000) {
      return `${(num / 100000000).toFixed(1)}亿`
    } else if (num >= 10000) {
      return `${(num / 10000).toFixed(1)}万`
    }
    return num.toLocaleString()
  }

  /**
   * Get status color
   */
  static getStatusColor(status: string): string {
    switch (status) {
      case 'active':
      case 'running':
      case 'healthy':
        return '#67C23A'
      case 'warning':
      case 'medium':
      case 'pending':
        return '#E6A23C'
      case 'critical':
      case 'error':
      case 'suspended':
      case 'urgent':
        return '#F56C6C'
      case 'inactive':
      case 'stopped':
        return '#909399'
      default:
        return '#409EFF'
    }
  }

  /**
   * Get role color
   */
  static getRoleColor(role: string): string {
    switch (role) {
      case 'admin':
        return '#F56C6C'
      case 'premium':
        return '#E6A23C'
      default:
        return '#909399'
    }
  }

  /**
   * Get priority color
   */
  static getPriorityColor(priority: string): string {
    switch (priority) {
      case 'urgent':
        return '#C62828'
      case 'high':
        return '#F56C6C'
      case 'medium':
        return '#E6A23C'
      default:
        return '#909399'
    }
  }
}

export default UserAdapter
