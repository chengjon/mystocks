/**
 * Watchlist API Service Layer
 *
 * Provides API methods for watchlist (自选股) management
 * User Story 3 - Watchlist Tabs Refactoring
 */

import request from './index'

/**
 * Watchlist API endpoints
 * T006: API layer for watchlist operations
 */
export const watchlistApi = {
  /**
   * Get all watchlist stocks with group information
   * @param {number} userId - User ID (optional, defaults to current user)
   * @returns {Promise} List of stocks with groups
   */
  async getAll(userId = null) {
    try {
      const params = userId ? { user_id: userId } : {}
      const response = await request.get('/watchlist/stocks', { params })
      return response
    } catch (error) {
      console.error('[WatchlistAPI] Failed to get all stocks:', error)
      throw error
    }
  },

  /**
   * Get watchlist stocks by category
   * @param {string} category - Category: 'user', 'system', 'strategy', 'monitor'
   * @returns {Promise} List of stocks in category
   */
  async getByCategory(category) {
    try {
      if (!['user', 'system', 'strategy', 'monitor'].includes(category)) {
        throw new Error(`Invalid category: ${category}`)
      }

      console.log(`[WatchlistAPI] Getting stocks for category: ${category}`)

      const response = await request.get('/watchlist/stocks', {
        params: { category }
      })

      console.log(`[WatchlistAPI] Found ${response.stocks?.length || 0} stocks in ${category}`)
      return response
    } catch (error) {
      console.error(`[WatchlistAPI] Failed to get stocks for category ${category}:`, error)

      // User-friendly error messages
      if (error.response?.status === 404) {
        throw new Error('该分类下暂无自选股')
      }

      throw error
    }
  },

  /**
   * Get watchlist stocks by group ID
   * @param {number} groupId - Group ID
   * @returns {Promise} List of stocks in group
   */
  async getByGroup(groupId) {
    try {
      const response = await request.get(`/watchlist/groups/${groupId}/stocks`)
      return response
    } catch (error) {
      console.error(`[WatchlistAPI] Failed to get stocks for group ${groupId}:`, error)

      if (error.response?.status === 404) {
        throw new Error('分组不存在')
      }

      throw error
    }
  },

  /**
   * Get all watchlist groups for current user
   * @returns {Promise} List of groups
   */
  async getGroups() {
    try {
      const response = await request.get('/watchlist/groups')
      return response
    } catch (error) {
      console.error('[WatchlistAPI] Failed to get groups:', error)
      throw error
    }
  },

  /**
   * Add a stock to watchlist
   * @param {string} symbol - Stock symbol (e.g., '600519')
   * @param {number} groupId - Group ID to add to
   * @param {object} options - Additional options (category, notes, etc.)
   * @returns {Promise} Added stock information
   */
  async addStock(symbol, groupId, options = {}) {
    try {
      console.log(`[WatchlistAPI] Adding stock ${symbol} to group ${groupId}`)

      const response = await request.post('/watchlist/stocks', {
        symbol,
        group_id: groupId,
        ...options
      })

      console.log('[WatchlistAPI] Stock added successfully')
      return response
    } catch (error) {
      console.error('[WatchlistAPI] Failed to add stock:', error)

      // User-friendly error messages
      if (error.response?.status === 400) {
        throw new Error('股票已在自选股中')
      } else if (error.response?.status === 404) {
        if (error.response.data?.detail?.includes('group')) {
          throw new Error('分组不存在')
        } else {
          throw new Error('股票代码不存在')
        }
      }

      throw error
    }
  },

  /**
   * Remove a stock from watchlist
   * @param {number} watchlistId - Watchlist item ID
   * @returns {Promise} Deletion result
   */
  async removeStock(watchlistId) {
    try {
      console.log(`[WatchlistAPI] Removing stock with ID ${watchlistId}`)

      const response = await request.delete(`/watchlist/stocks/${watchlistId}`)

      console.log('[WatchlistAPI] Stock removed successfully')
      return response
    } catch (error) {
      console.error('[WatchlistAPI] Failed to remove stock:', error)

      if (error.response?.status === 404) {
        throw new Error('自选股不存在')
      }

      throw error
    }
  },

  /**
   * Move stock to a different group
   * @param {number} watchlistId - Watchlist item ID
   * @param {number} newGroupId - New group ID
   * @returns {Promise} Update result
   */
  async moveStock(watchlistId, newGroupId) {
    try {
      console.log(`[WatchlistAPI] Moving stock ${watchlistId} to group ${newGroupId}`)

      const response = await request.patch(`/watchlist/stocks/${watchlistId}`, {
        group_id: newGroupId
      })

      console.log('[WatchlistAPI] Stock moved successfully')
      return response
    } catch (error) {
      console.error('[WatchlistAPI] Failed to move stock:', error)

      if (error.response?.status === 404) {
        throw new Error('自选股或分组不存在')
      }

      throw error
    }
  },

  /**
   * Create a new watchlist group
   * @param {string} groupName - Group name
   * @param {string} category - Category: 'user', 'system', 'strategy', 'monitor'
   * @param {object} options - Additional options (sort_order, etc.)
   * @returns {Promise} Created group
   */
  async createGroup(groupName, category = 'user', options = {}) {
    try {
      console.log(`[WatchlistAPI] Creating group: ${groupName} (${category})`)

      const response = await request.post('/watchlist/groups', {
        group_name: groupName,
        category,
        ...options
      })

      console.log('[WatchlistAPI] Group created successfully')
      return response
    } catch (error) {
      console.error('[WatchlistAPI] Failed to create group:', error)

      if (error.response?.status === 400) {
        throw new Error('分组名称已存在')
      }

      throw error
    }
  },

  /**
   * Delete a watchlist group
   * @param {number} groupId - Group ID
   * @returns {Promise} Deletion result
   */
  async deleteGroup(groupId) {
    try {
      console.log(`[WatchlistAPI] Deleting group ${groupId}`)

      const response = await request.delete(`/watchlist/groups/${groupId}`)

      console.log('[WatchlistAPI] Group deleted successfully')
      return response
    } catch (error) {
      console.error('[WatchlistAPI] Failed to delete group:', error)

      if (error.response?.status === 404) {
        throw new Error('分组不存在')
      } else if (error.response?.status === 400) {
        throw new Error('分组不为空，无法删除')
      }

      throw error
    }
  },

  /**
   * Update group information
   * @param {number} groupId - Group ID
   * @param {object} updates - Fields to update (group_name, category, sort_order, etc.)
   * @returns {Promise} Updated group
   */
  async updateGroup(groupId, updates) {
    try {
      console.log(`[WatchlistAPI] Updating group ${groupId}:`, updates)

      const response = await request.patch(`/watchlist/groups/${groupId}`, updates)

      console.log('[WatchlistAPI] Group updated successfully')
      return response
    } catch (error) {
      console.error('[WatchlistAPI] Failed to update group:', error)

      if (error.response?.status === 404) {
        throw new Error('分组不存在')
      } else if (error.response?.status === 400) {
        throw new Error('分组名称已存在')
      }

      throw error
    }
  }
}

export default watchlistApi
