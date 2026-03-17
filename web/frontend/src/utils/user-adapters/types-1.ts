
// @ts-nocheck
/**
 * User & Watchlist Module Data Adapters
 *
 * Transforms API responses into ViewModels for UI components.
 */

export type {
  UserProfileResponse,
  WatchlistResponse,
  NotificationResponse
} from '@/api/types/generated-types.ts'

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
  customFields?: Record<string, unknown>
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
  data?: Record<string, unknown>
  priority: 'low' | 'medium' | 'high' | 'urgent'
  isRead: boolean
  createdAt: string
  expiresAt?: string
  actionUrl?: string
  actionText?: string
  icon?: string
  category: string
}
