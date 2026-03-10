export interface UpdateProfilePayload {
  displayName?: string
  avatar?: string
  bio?: string
  phone?: string
}

export interface ChangePasswordPayload {
  currentPassword: string
  newPassword: string
  confirmPassword: string
}

export interface UserStatistics {
  totalTrades: number
  winningTrades: number
  losingTrades: number
  winRate: number
  totalPnL: number
  totalPnLPercent: string
  averageReturn: number
  sharpeRatio: number
  maxDrawdown: number
  monthlyReturns: Array<{ month: string; return: number }>
  sectorPerformance: Array<{ sector: string; return: number }>
}

export interface GetWatchlistsParams {
  public?: boolean
  owner?: string
  tag?: string
  limit?: number
  offset?: number
}

export interface CreateWatchlistPayload {
  name: string
  description?: string
  isPublic?: boolean
  tags?: string[]
}

export interface UpdateWatchlistPayload {
  name?: string
  description?: string
  isPublic?: boolean
  tags?: string[]
}

export interface WatchlistStockAlert {
  type: string
  condition: string
  value: number
}

export interface AddWatchlistStockPayload {
  symbol: string
  notes?: string
  alerts?: WatchlistStockAlert[]
}

export interface WatchlistAlertPayload {
  type: string
  condition: string
  value: number
  notificationMethod?: string
  expiresAt?: string
}

export interface WatchlistPerformance {
  totalValue: number
  todayChange: number
  todayChangePercent: string
  periodReturn: number
  periodReturnPercent: string
  annualizedReturn: number
  volatility: number
  sharpeRatio: number
  maxDrawdown: number
  beta: number
  alpha: number
  performanceChart: Array<{ date: string; value: number; benchmark?: number }>
}

export interface WatchlistHistoryParams {
  startDate?: string
  endDate?: string
  limit?: number
}

export interface WatchlistHistoryEntry {
  date: string
  action: string
  symbol: string
  price: number
  notes?: string
}

export interface CopyWatchlistPayload {
  name?: string
  description?: string
}

export interface GetPopularWatchlistsParams {
  category?: string
  period?: string
  limit?: number
}

export interface SearchWatchlistsPayload {
  searchTerm: string
  filters?: {
    category?: string
    tags?: string[]
    owner?: string
    minStocks?: number
    maxStocks?: number
  }
  limit?: number
}

export interface GetNotificationsParams {
  type?: string
  isRead?: boolean
  category?: string
  startDate?: string
  endDate?: string
  limit?: number
  offset?: number
}

export interface NotificationCategorySetting {
  name: string
  enabled: boolean
  methods: string[]
}

export interface NotificationQuietHours {
  enabled: boolean
  start: string
  end: string
  timezone: string
}

export interface NotificationSettings {
  email: boolean
  push: boolean
  sms: boolean
  categories: NotificationCategorySetting[]
  quietHours: NotificationQuietHours
}

export interface UpdateNotificationSettingsPayload {
  email?: boolean
  push?: boolean
  sms?: boolean
  categories?: NotificationCategorySetting[]
  quietHours?: Partial<NotificationQuietHours>
}

export interface NotificationSubscription {
  endpoint: string
  keys: {
    p256dh: string
    auth: string
  }
}

export interface NotificationStatistics {
  total: number
  unread: number
  read: number
  byType: Record<string, number>
  byCategory: Record<string, number>
  todayReceived: number
  weekReceived: number
  monthReceived: number
}

export type WatchlistExportFormat = 'csv' | 'json' | 'excel'

export interface ImportWatchlistOptions {
  name?: string
  isPublic?: boolean
  tags?: string[]
}

export interface ActivityLogParams {
  type?: string
  startDate?: string
  endDate?: string
  limit?: number
  offset?: number
}

export interface ActivityLogEntry {
  id: string
  type: string
  action: string
  target: string
  details: Record<string, unknown>
  timestamp: string
  ipAddress?: string
  userAgent?: string
}

export interface ApiKey {
  id: string
  name: string
  key: string
  permissions: string[]
  lastUsed?: string
  expiresAt?: string
  isActive: boolean
  createdAt: string
}

export interface CreateApiKeyPayload {
  name: string
  permissions: string[]
  expiresAt?: string
}

export interface CreatedApiKey {
  id: string
  name: string
  key: string
  permissions: string[]
  expiresAt?: string
}
