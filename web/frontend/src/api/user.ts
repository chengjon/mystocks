/**
 * User & Watchlist API Service
 *
 * Provides methods for managing user profiles, watchlists, and notifications.
 */

import { request } from '@/utils/request'
import { UserAdapter } from '@/utils/user-adapters'
import type {
  UserProfileResponse,
  WatchlistResponse,
  NotificationResponse
} from '@/api/types/additional-types'
import type {
  UserProfileVM,
  WatchlistVM,
  NotificationVM,
  UserPreferencesVM
} from '@/utils/user-adapters'

class UserApiService {
  private baseUrl = '/api/user'
  private watchlistUrl = '/api/watchlist'
  private notificationUrl = '/api/notification'

  /**
   * Get user profile
   */
  async getProfile(): Promise<UserProfileVM> {
    const rawData = await request.get(`${this.baseUrl}/profile`)
    return UserAdapter.toUserProfileVM(rawData)
  }

  /**
   * Update user profile
   */
  async updateProfile(profileData: {
    displayName?: string
    avatar?: string
    bio?: string
    phone?: string
  }): Promise<UserProfileVM> {
    const rawData = await request.put(`${this.baseUrl}/profile`, profileData)
    return UserAdapter.toUserProfileVM(rawData)
  }

  /**
   * Get user preferences
   */
  async getPreferences(): Promise<UserPreferencesVM> {
    const rawData = await request.get(`${this.baseUrl}/preferences`)
    return UserAdapter.toUserProfileVM({ ...rawData, userId: '', username: '', email: '' }).preferences
  }

  /**
   * Update user preferences
   */
  async updatePreferences(preferences: Partial<UserPreferencesVM>): Promise<void> {
    await request.put(`${this.baseUrl}/preferences`, preferences)
  }

  /**
   * Change password
   */
  async changePassword(data: {
    currentPassword: string
    newPassword: string
    confirmPassword: string
  }): Promise<void> {
    await request.post(`${this.baseUrl}/change-password`, data)
  }

  /**
   * Get user statistics
   */
  async getStatistics(period?: string): Promise<{
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
  }> {
    return request.get(`${this.baseUrl}/statistics`, {
      params: { period }
    })
  }

  /**
   * Get all watchlists
   */
  async getWatchlists(params?: {
    public?: boolean
    owner?: string
    tag?: string
    limit?: number
    offset?: number
  }): Promise<WatchlistVM[]> {
    const rawData = await request.get(`${this.watchlistUrl}`, { params })
    return UserAdapter.toWatchlistVM(rawData)
  }

  /**
   * Get watchlist details
   */
  async getWatchlist(watchlistId: string): Promise<WatchlistVM> {
    const rawData = await request.get(`${this.watchlistUrl}/${watchlistId}`)
    const watchlists = UserAdapter.toWatchlistVM([rawData])
    return watchlists[0]
  }

  /**
   * Create new watchlist
   */
  async createWatchlist(watchlistData: {
    name: string
    description?: string
    isPublic?: boolean
    tags?: string[]
  }): Promise<WatchlistVM> {
    const rawData = await request.post(`${this.watchlistUrl}`, watchlistData)
    const watchlists = UserAdapter.toWatchlistVM([rawData])
    return watchlists[0]
  }

  /**
   * Update watchlist
   */
  async updateWatchlist(watchlistId: string, updates: {
    name?: string
    description?: string
    isPublic?: boolean
    tags?: string[]
  }): Promise<WatchlistVM> {
    const rawData = await request.put(`${this.watchlistUrl}/${watchlistId}`, updates)
    const watchlists = UserAdapter.toWatchlistVM([rawData])
    return watchlists[0]
  }

  /**
   * Delete watchlist
   */
  async deleteWatchlist(watchlistId: string): Promise<void> {
    await request.delete(`${this.watchlistUrl}/${watchlistId}`)
  }

  /**
   * Add stock to watchlist
   */
  async addStockToWatchlist(watchlistId: string, stockData: {
    symbol: string
    notes?: string
    alerts?: Array<{
      type: string
      condition: string
      value: number
    }>
  }): Promise<void> {
    await request.post(`${this.watchlistUrl}/${watchlistId}/stocks`, stockData)
  }

  /**
   * Remove stock from watchlist
   */
  async removeStockFromWatchlist(watchlistId: string, symbol: string): Promise<void> {
    await request.delete(`${this.watchlistUrl}/${watchlistId}/stocks/${symbol}`)
  }

  /**
   * Update stock notes
   */
  async updateStockNotes(watchlistId: string, symbol: string, notes: string): Promise<void> {
    await request.put(`${this.watchlistUrl}/${watchlistId}/stocks/${symbol}/notes`, { notes })
  }

  /**
   * Add stock alert
   */
  async addStockAlert(watchlistId: string, symbol: string, alert: {
    type: string
    condition: string
    value: number
    notificationMethod?: string
    expiresAt?: string
  }): Promise<void> {
    await request.post(`${this.watchlistUrl}/${watchlistId}/stocks/${symbol}/alerts`, alert)
  }

  /**
   * Remove stock alert
   */
  async removeStockAlert(watchlistId: string, symbol: string, alertId: string): Promise<void> {
    await request.delete(`${this.watchlistUrl}/${watchlistId}/stocks/${symbol}/alerts/${alertId}`)
  }

  /**
   * Toggle stock alert
   */
  async toggleStockAlert(watchlistId: string, symbol: string, alertId: string): Promise<void> {
    await request.post(`${this.watchlistUrl}/${watchlistId}/stocks/${symbol}/alerts/${alertId}/toggle`)
  }

  /**
   * Get watchlist performance
   */
  async getWatchlistPerformance(watchlistId: string, period?: string): Promise<{
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
  }> {
    return request.get(`${this.watchlistUrl}/${watchlistId}/performance`, {
      params: { period }
    })
  }

  /**
   * Get watchlist history
   */
  async getWatchlistHistory(watchlistId: string, params?: {
    startDate?: string
    endDate?: string
    limit?: number
  }): Promise<Array<{
    date: string
    action: string
    symbol: string
    price: number
    notes?: string
  }>> {
    return request.get(`${this.watchlistUrl}/${watchlistId}/history`, { params })
  }

  /**
   * Copy watchlist
   */
  async copyWatchlist(watchlistId: string, newData?: {
    name?: string
    description?: string
  }): Promise<WatchlistVM> {
    const rawData = await request.post(`${this.watchlistUrl}/${watchlistId}/copy`, newData)
    const watchlists = UserAdapter.toWatchlistVM([rawData])
    return watchlists[0]
  }

  /**
   * Follow watchlist
   */
  async followWatchlist(watchlistId: string): Promise<void> {
    await request.post(`${this.watchlistUrl}/${watchlistId}/follow`)
  }

  /**
   * Unfollow watchlist
   */
  async unfollowWatchlist(watchlistId: string): Promise<void> {
    await request.post(`${this.watchlistUrl}/${watchlistId}/unfollow`)
  }

  /**
   * Get following watchlists
   */
  async getFollowingWatchlists(): Promise<WatchlistVM[]> {
    const rawData = await request.get(`${this.watchlistUrl}/following`)
    return UserAdapter.toWatchlistVM(rawData)
  }

  /**
   * Get popular watchlists
   */
  async getPopularWatchlists(params?: {
    category?: string
    period?: string
    limit?: number
  }): Promise<WatchlistVM[]> {
    const rawData = await request.get(`${this.watchlistUrl}/popular`, { params })
    return UserAdapter.toWatchlistVM(rawData)
  }

  /**
   * Search watchlists
   */
  async searchWatchlists(query: {
    searchTerm: string
    filters?: {
      category?: string
      tags?: string[]
      owner?: string
      minStocks?: number
      maxStocks?: number
    }
    limit?: number
  }): Promise<WatchlistVM[]> {
    const rawData = await request.post(`${this.watchlistUrl}/search`, query)
    return UserAdapter.toWatchlistVM(rawData)
  }

  /**
   * Get notifications
   */
  async getNotifications(params?: {
    type?: string
    isRead?: boolean
    category?: string
    startDate?: string
    endDate?: string
    limit?: number
    offset?: number
  }): Promise<NotificationVM[]> {
    const rawData = await request.get(`${this.notificationUrl}`, { params })
    return UserAdapter.toNotificationVM(rawData)
  }

  /**
   * Mark notification as read
   */
  async markNotificationAsRead(notificationId: string): Promise<void> {
    await request.put(`${this.notificationUrl}/${notificationId}/read`)
  }

  /**
   * Mark all notifications as read
   */
  async markAllNotificationsAsRead(): Promise<void> {
    await request.put(`${this.notificationUrl}/read-all`)
  }

  /**
   * Delete notification
   */
  async deleteNotification(notificationId: string): Promise<void> {
    await request.delete(`${this.notificationUrl}/${notificationId}`)
  }

  /**
   * Get notification settings
   */
  async getNotificationSettings(): Promise<{
    email: boolean
    push: boolean
    sms: boolean
    categories: Array<{
      name: string
      enabled: boolean
      methods: string[]
    }>
    quietHours: {
      enabled: boolean
      start: string
      end: string
      timezone: string
    }
  }> {
    return request.get(`${this.notificationUrl}/settings`)
  }

  /**
   * Update notification settings
   */
  async updateNotificationSettings(settings: {
    email?: boolean
    push?: boolean
    sms?: boolean
    categories?: Array<{
      name: string
      enabled: boolean
      methods: string[]
    }>
    quietHours?: {
      enabled?: boolean
      start?: string
      end?: string
      timezone?: string
    }
  }): Promise<void> {
    await request.put(`${this.notificationUrl}/settings`, settings)
  }

  /**
   * Subscribe to notifications
   */
  async subscribeToNotifications(subscription: {
    endpoint: string
    keys: {
      p256dh: string
      auth: string
    }
  }): Promise<void> {
    await request.post(`${this.notificationUrl}/subscribe`, subscription)
  }

  /**
   * Unsubscribe from notifications
   */
  async unsubscribeFromNotifications(endpoint: string): Promise<void> {
    await request.post(`${this.notificationUrl}/unsubscribe`, { endpoint })
  }

  /**
   * Get notification statistics
   */
  async getNotificationStatistics(): Promise<{
    total: number
    unread: number
    read: number
    byType: Record<string, number>
    byCategory: Record<string, number>
    todayReceived: number
    weekReceived: number
    monthReceived: number
  }> {
    return request.get(`${this.notificationUrl}/statistics`)
  }

  /**
   * Export watchlist
   */
  async exportWatchlist(watchlistId: string, format: 'csv' | 'json' | 'excel' = 'csv'): Promise<Blob> {
    const response = await request.get(`${this.watchlistUrl}/${watchlistId}/export`, {
      params: { format },
      responseType: 'blob'
    })
    return response
  }

  /**
   * Import watchlist
   */
  async importWatchlist(file: File, options?: {
    name?: string
    isPublic?: boolean
    tags?: string[]
  }): Promise<WatchlistVM> {
    const formData = new FormData()
    formData.append('file', file)
    if (options) {
      Object.entries(options).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          value.forEach(v => formData.append(key, v))
        } else {
          formData.append(key, value as string)
        }
      })
    }

    const rawData = await request.post(`${this.watchlistUrl}/import`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    const watchlists = UserAdapter.toWatchlistVM([rawData])
    return watchlists[0]
  }

  /**
   * Get user activity log
   */
  async getActivityLog(params?: {
    type?: string
    startDate?: string
    endDate?: string
    limit?: number
    offset?: number
  }): Promise<Array<{
    id: string
    type: string
    action: string
    target: string
    details: Record<string, any>
    timestamp: string
    ipAddress?: string
    userAgent?: string
  }>> {
    return request.get(`${this.baseUrl}/activity`, { params })
  }

  /**
   * Get API keys
   */
  async getApiKeys(): Promise<Array<{
    id: string
    name: string
    key: string
    permissions: string[]
    lastUsed?: string
    expiresAt?: string
    isActive: boolean
    createdAt: string
  }>> {
    return request.get(`${this.baseUrl}/api-keys`)
  }

  /**
   * Create API key
   */
  async createApiKey(keyData: {
    name: string
    permissions: string[]
    expiresAt?: string
  }): Promise<{
    id: string
    name: string
    key: string
    permissions: string[]
    expiresAt?: string
  }> {
    return request.post(`${this.baseUrl}/api-keys`, keyData)
  }

  /**
   * Revoke API key
   */
  async revokeApiKey(keyId: string): Promise<void> {
    await request.delete(`${this.baseUrl}/api-keys/${keyId}`)
  }

  /**
   * Toggle API key
   */
  async toggleApiKey(keyId: string): Promise<void> {
    await request.post(`${this.baseUrl}/api-keys/${keyId}/toggle`)
  }
}

// Export singleton instance
export const userApi = new UserApiService()

// Export class for dependency injection
export default UserApiService
