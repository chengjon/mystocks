/**
 * User & Watchlist Module Data Adapters
 *
 * Transforms API responses into ViewModels for UI components.
 */

import type {
  UserProfileResponse,
  WatchlistResponse,
  NotificationResponse
} from '@/api/types/generated-types.ts'
import type {
  NotificationPreferencesVM,
  NotificationVM,
  PrivacyPreferencesVM,
  StockAlertVM,
  SubscriptionVM,
  UserPermissionsVM,
  UserPreferencesVM,
  UserProfileVM,
  UserStatisticsVM,
  WatchlistStatisticsVM,
  WatchlistVM,
} from './types-1.ts'

type AnyRecord = Record<string, unknown>

const asRecord = (value: unknown): AnyRecord =>
  typeof value === 'object' && value !== null ? (value as AnyRecord) : {}

const asArray = <T = unknown>(value: unknown): T[] =>
  Array.isArray(value) ? (value as T[]) : []

const asString = (value: unknown, fallback = ''): string =>
  typeof value === 'string' ? value : value == null ? fallback : String(value)

const asNumber = (value: unknown, fallback = 0): number =>
  typeof value === 'number' && Number.isFinite(value) ? value : fallback

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
      avatar: data.avatar || undefined,
      role: this.getUserRole(data.role || ''),
      status: this.getUserStatus(data.status || ''),
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
      description: watchlist.description || undefined,
      isDefault: watchlist.isDefault || false,
      isPublic: watchlist.isPublic || false,
      owner: {
        userId: asString(watchlist.owner?.userId),
        username: asString(watchlist.owner?.username),
        displayName: asString(watchlist.owner?.displayName)
      },
      stocks: (watchlist.stocks || []).map(stock => ({
        symbol: stock.symbol || '',
        name: stock.name || '',
        market: stock.market || 'A',
        currentPrice: stock.currentPrice || 0,
        changeAmount: stock.changeAmount || 0,
        changePercent: this.formatPercent(stock.changePercent ?? 0),
        volume: stock.volume || 0,
        marketCap: stock.marketCap || 0,
        pe: stock.pe ?? undefined,
        pb: stock.pb ?? undefined,
        addedAt: this.formatDateTime(stock.addedAt),
        notes: stock.notes || undefined,
        alerts: asArray(stock.alerts).map(alert => this.toStockAlertVM(alert)),
        customFields: stock.customFields || undefined
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
      type: this.getNotificationType(notification.type),
      title: notification.title || '',
      message: notification.message || '',
      data: notification.data || undefined,
      priority: this.getNotificationPriority(notification.priority || ''),
      isRead: notification.isRead || false,
      createdAt: this.formatDateTime(notification.createdAt),
      expiresAt: this.formatDateTime(notification.expiresAt),
      actionUrl: notification.actionUrl || undefined,
      actionText: notification.actionText || undefined,
      icon: notification.icon || undefined,
      category: notification.category || 'general'
    }))
  }

  private static toStockAlertVM(alert: unknown): StockAlertVM {
    const record = asRecord(alert)

    return {
      id: asString(record.id),
      type: (asString(record.type, 'price') as StockAlertVM['type']),
      condition: (asString(record.condition, 'above') as StockAlertVM['condition']),
      value: asNumber(record.value),
      isActive: record.isActive !== false,
      triggeredAt: this.formatDateTime(record.triggeredAt),
      expiresAt: this.formatDateTime(record.expiresAt),
      notificationMethod: (asString(record.notificationMethod, 'push') as StockAlertVM['notificationMethod']),
    }
  }

  /**
   * Convert user preferences to ViewModel
   */
  private static toUserPreferencesVM(preferences: unknown): UserPreferencesVM {
    const record = asRecord(preferences)
    const chartSettings = asRecord(record.chartSettings)

    return {
      theme: asString(record.theme, 'auto') as UserPreferencesVM['theme'],
      language: asString(record.language, 'zh-CN') as UserPreferencesVM['language'],
      timezone: asString(record.timezone, 'Asia/Shanghai'),
      dateFormat: asString(record.dateFormat, 'YYYY-MM-DD') as UserPreferencesVM['dateFormat'],
      timeFormat: asString(record.timeFormat, '24h') as UserPreferencesVM['timeFormat'],
      defaultDashboard: asString(record.defaultDashboard, 'overview'),
      watchlistLayout: asString(record.watchlistLayout, 'grid') as UserPreferencesVM['watchlistLayout'],
      chartSettings: {
        defaultPeriod: asString(chartSettings.defaultPeriod, '1D'),
        showVolume: chartSettings.showVolume !== false,
        showMA: chartSettings.showMA !== false,
        indicators: asArray<string>(chartSettings.indicators)
      },
      notifications: this.toNotificationPreferencesVM(record.notifications),
      privacy: this.toPrivacyPreferencesVM(record.privacy)
    }
  }

  /**
   * Convert notification preferences to ViewModel
   */
  private static toNotificationPreferencesVM(notifications: unknown): NotificationPreferencesVM {
    const record = asRecord(notifications)

    return {
      email: record.email !== false,
      push: record.push !== false,
      sms: record.sms === true,
      priceAlerts: record.priceAlerts !== false,
      orderStatus: record.orderStatus !== false,
      systemUpdates: record.systemUpdates !== false,
      marketNews: record.marketNews !== false,
      strategySignals: record.strategySignals !== false
    }
  }

  /**
   * Convert privacy preferences to ViewModel
   */
  private static toPrivacyPreferencesVM(privacy: unknown): PrivacyPreferencesVM {
    const record = asRecord(privacy)

    return {
      profileVisibility: asString(record.profileVisibility, 'private') as PrivacyPreferencesVM['profileVisibility'],
      showRealName: record.showRealName === true,
      showEmail: record.showEmail === true,
      showTradingStats: record.showTradingStats !== false,
      allowDirectMessages: record.allowDirectMessages !== false,
      dataSharing: record.dataSharing === true
    }
  }

  /**
   * Convert user permissions to ViewModel
   */
  private static toUserPermissionsVM(permissions: unknown): UserPermissionsVM {
    const record = asRecord(permissions)

    return {
      canTrade: record.canTrade !== false,
      canWithdraw: record.canWithdraw !== false,
      canUseStrategies: record.canUseStrategies !== false,
      canAccessAdvancedFeatures: record.canAccessAdvancedFeatures === true,
      canViewMarketData: record.canViewMarketData !== false,
      canExportData: record.canExportData !== false,
      canManageUsers: record.canManageUsers === true,
      canViewAnalytics: record.canViewAnalytics !== false,
      maxStrategies: asNumber(record.maxStrategies, 5),
      maxWatchlists: asNumber(record.maxWatchlists, 10),
      maxApiCalls: asNumber(record.maxApiCalls, 1000)
    }
  }

  /**
   * Convert subscription to ViewModel
   */
  private static toSubscriptionVM(subscription: unknown): SubscriptionVM {
    const record = asRecord(subscription)
    const limits = asRecord(record.limits)

    return {
      plan: asString(record.plan, 'free') as SubscriptionVM['plan'],
      status: asString(record.status, 'active') as SubscriptionVM['status'],
      startDate: this.formatDate(record.startDate),
      endDate: this.formatDate(record.endDate),
      trialEndDate: this.formatDate(record.trialEndDate) || undefined,
      autoRenew: record.autoRenew !== false,
      features: asArray<string>(record.features),
      limits: {
        maxStrategies: asNumber(limits.maxStrategies, 5),
        maxWatchlists: asNumber(limits.maxWatchlists, 10),
        maxApiCallsPerDay: asNumber(limits.maxApiCallsPerDay, 1000),
        maxDataRetention: asNumber(limits.maxDataRetention, 30)
      },
      nextBillingAmount: typeof record.nextBillingAmount === 'number' ? record.nextBillingAmount : undefined,
      nextBillingDate: this.formatDate(record.nextBillingDate) || undefined
    }
  }

  /**
   * Convert user statistics to ViewModel
   */
  private static toUserStatisticsVM(statistics: unknown): UserStatisticsVM {
    const record = asRecord(statistics)
    const totalTrades = asNumber(record.totalTrades)
    const winningTrades = asNumber(record.winningTrades)
    const totalInvested = asNumber(record.totalInvested)
    const totalPnL = asNumber(record.totalPnL)
    const winRate = totalTrades ? (winningTrades / totalTrades) * 100 : 0
    const totalPnLPercent = totalInvested ? (totalPnL / totalInvested) * 100 : 0

    return {
      totalTrades,
      winningTrades,
      losingTrades: asNumber(record.losingTrades),
      winRate,
      totalPnL,
      totalPnLPercent: this.formatPercent(totalPnLPercent),
      averageReturn: asNumber(record.averageReturn),
      sharpeRatio: asNumber(record.sharpeRatio),
      maxDrawdown: asNumber(record.maxDrawdown),
      totalCommission: asNumber(record.totalCommission),
      joinDate: this.formatDate(record.joinDate),
      activeStrategies: asNumber(record.activeStrategies),
      activeWatchlists: asNumber(record.activeWatchlists),
      followers: asNumber(record.followers),
      following: asNumber(record.following)
    }
  }

  /**
   * Convert watchlist statistics to ViewModel
   */
  private static toWatchlistStatisticsVM(statistics: unknown): WatchlistStatisticsVM {
    const record = asRecord(statistics)
    const bestPerformer = asRecord(record.bestPerformer)
    const worstPerformer = asRecord(record.worstPerformer)

    return {
      totalStocks: asNumber(record.totalStocks),
      totalValue: asNumber(record.totalValue),
      todayChange: asNumber(record.todayChange),
      todayChangePercent: this.formatPercent(asNumber(record.todayChangePercent)),
      bestPerformer: {
        symbol: asString(bestPerformer.symbol),
        name: asString(bestPerformer.name),
        changePercent: this.formatPercent(asNumber(bestPerformer.changePercent))
      },
      worstPerformer: {
        symbol: asString(worstPerformer.symbol),
        name: asString(worstPerformer.name),
        changePercent: this.formatPercent(asNumber(worstPerformer.changePercent))
      },
      sectors: asArray(record.sectors).map((sector) => {
        const sectorRecord = asRecord(sector)
        return {
          name: asString(sectorRecord.name),
          count: asNumber(sectorRecord.count),
          weight: asNumber(sectorRecord.weight)
        }
      })
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

  private static getNotificationType(type: string | undefined): NotificationVM['type'] {
    switch (type) {
      case 'price_alert':
      case 'order':
      case 'strategy':
      case 'social':
      case 'market':
        return type
      default:
        return 'system'
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
  private static formatDateTime(timestamp: unknown): string {
    if (!timestamp) return ''
    const normalizedTimestamp =
      timestamp instanceof Date || typeof timestamp === 'string' || typeof timestamp === 'number'
        ? timestamp
        : asString(timestamp)
    const date = new Date(normalizedTimestamp)
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
  private static formatDate(timestamp: unknown): string {
    if (!timestamp) return ''
    const normalizedTimestamp =
      timestamp instanceof Date || typeof timestamp === 'string' || typeof timestamp === 'number'
        ? timestamp
        : asString(timestamp)
    const date = new Date(normalizedTimestamp)
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
