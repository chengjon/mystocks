/**
 * User & Watchlist API Service
 *
 * Provides methods for managing user profiles, watchlists, and notifications.
 */

import { request } from '@/utils/request.ts'
import { UserAdapter } from '@/utils/user-adapters.ts'
import type {
  NotificationVM,
  UserPreferencesVM,
  UserProfileVM,
  WatchlistVM,
} from '@/utils/user-adapters.ts'
import type {
  ActivityLogEntry,
  ActivityLogParams,
  AddWatchlistStockPayload,
  ApiKey,
  ChangePasswordPayload,
  CopyWatchlistPayload,
  CreateApiKeyPayload,
  CreatedApiKey,
  CreateWatchlistPayload,
  GetNotificationsParams,
  GetPopularWatchlistsParams,
  GetWatchlistsParams,
  ImportWatchlistOptions,
  NotificationSettings,
  NotificationStatistics,
  NotificationSubscription,
  SearchWatchlistsPayload,
  UpdateNotificationSettingsPayload,
  UpdateProfilePayload,
  UpdateWatchlistPayload,
  UserStatistics,
  WatchlistAlertPayload,
  WatchlistExportFormat,
  WatchlistHistoryEntry,
  WatchlistHistoryParams,
  WatchlistPerformance,
} from './user.types.ts'

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
  async updateProfile(profileData: UpdateProfilePayload): Promise<UserProfileVM> {
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
  async changePassword(data: ChangePasswordPayload): Promise<void> {
    await request.post(`${this.baseUrl}/change-password`, data)
  }

  /**
   * Get user statistics
   */
  async getStatistics(period?: string): Promise<UserStatistics> {
    return request.get(`${this.baseUrl}/statistics`, {
      params: { period }
    })
  }

  /**
   * Get all watchlists
   */
  async getWatchlists(params?: GetWatchlistsParams): Promise<WatchlistVM[]> {
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
  async createWatchlist(watchlistData: CreateWatchlistPayload): Promise<WatchlistVM> {
    const rawData = await request.post(`${this.watchlistUrl}`, watchlistData)
    const watchlists = UserAdapter.toWatchlistVM([rawData])
    return watchlists[0]
  }

  /**
   * Update watchlist
   */
  async updateWatchlist(watchlistId: string, updates: UpdateWatchlistPayload): Promise<WatchlistVM> {
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
  async addStockToWatchlist(watchlistId: string, stockData: AddWatchlistStockPayload): Promise<void> {
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
  async addStockAlert(watchlistId: string, symbol: string, alert: WatchlistAlertPayload): Promise<void> {
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
  async getWatchlistPerformance(watchlistId: string, period?: string): Promise<WatchlistPerformance> {
    return request.get(`${this.watchlistUrl}/${watchlistId}/performance`, {
      params: { period }
    })
  }

  /**
   * Get watchlist history
   */
  async getWatchlistHistory(
    watchlistId: string,
    params?: WatchlistHistoryParams
  ): Promise<WatchlistHistoryEntry[]> {
    return request.get(`${this.watchlistUrl}/${watchlistId}/history`, { params })
  }

  /**
   * Copy watchlist
   */
  async copyWatchlist(watchlistId: string, newData?: CopyWatchlistPayload): Promise<WatchlistVM> {
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
  async getPopularWatchlists(params?: GetPopularWatchlistsParams): Promise<WatchlistVM[]> {
    const rawData = await request.get(`${this.watchlistUrl}/popular`, { params })
    return UserAdapter.toWatchlistVM(rawData)
  }

  /**
   * Search watchlists
   */
  async searchWatchlists(query: SearchWatchlistsPayload): Promise<WatchlistVM[]> {
    const rawData = await request.post(`${this.watchlistUrl}/search`, query)
    return UserAdapter.toWatchlistVM(rawData)
  }

  /**
   * Get notifications
   */
  async getNotifications(params?: GetNotificationsParams): Promise<NotificationVM[]> {
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
  async getNotificationSettings(): Promise<NotificationSettings> {
    return request.get(`${this.notificationUrl}/settings`)
  }

  /**
   * Update notification settings
   */
  async updateNotificationSettings(settings: UpdateNotificationSettingsPayload): Promise<void> {
    await request.put(`${this.notificationUrl}/settings`, settings)
  }

  /**
   * Subscribe to notifications
   */
  async subscribeToNotifications(subscription: NotificationSubscription): Promise<void> {
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
  async getNotificationStatistics(): Promise<NotificationStatistics> {
    return request.get(`${this.notificationUrl}/statistics`)
  }

  /**
   * Export watchlist
   */
  async exportWatchlist(watchlistId: string, format: WatchlistExportFormat = 'csv'): Promise<Blob> {
    const response = await request.get(`${this.watchlistUrl}/${watchlistId}/export`, {
      params: { format },
      responseType: 'blob'
    })
    return response
  }

  /**
   * Import watchlist
   */
  async importWatchlist(file: File, options?: ImportWatchlistOptions): Promise<WatchlistVM> {
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
  async getActivityLog(params?: ActivityLogParams): Promise<ActivityLogEntry[]> {
    return request.get(`${this.baseUrl}/activity`, { params })
  }

  /**
   * Get API keys
   */
  async getApiKeys(): Promise<ApiKey[]> {
    return request.get(`${this.baseUrl}/api-keys`)
  }

  /**
   * Create API key
   */
  async createApiKey(keyData: CreateApiKeyPayload): Promise<CreatedApiKey> {
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
