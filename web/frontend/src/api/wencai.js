/**
 * Wencai API Service Layer
 *
 * Provides API methods for Wencai stock filtering
 * User Story 2 - Wencai Query Restoration
 */

import request from './index'

/**
 * Wencai API endpoints
 * T019, T022: API layer with error handling
 */
export const wencaiApi = {
  /**
   * Execute a preset query by ID
   * @param {string} queryId - Query ID (e.g., 'qs_1')
   * @param {object} conditions - Optional query conditions
   * @returns {Promise} Query execution result
   */
  async executePresetQuery(queryId, conditions = {}) {
    try {
      console.log(`[WencaiAPI] Executing preset query: ${queryId}`)

      const response = await request.post('/market/wencai/filter', {
        query_id: queryId,
        conditions,
        pages: 1
      })

      console.log(`[WencaiAPI] Query ${queryId} executed successfully:`, response)
      return response
    } catch (error) {
      console.error(`[WencaiAPI] Failed to execute query ${queryId}:`, error)

      // T022: Error handling and fallback strategy
      if (error.response) {
        const status = error.response.status
        const errorData = error.response.data

        // Map error codes to user-friendly messages
        switch (status) {
          case 400:
            throw new Error(errorData.detail || '查询参数无效，请检查筛选条件')
          case 429:
            throw new Error('查询频率过高，请稍后再试')
          case 500:
            throw new Error('服务器错误，请稍后重试')
          default:
            throw new Error(errorData.detail || `查询失败 (HTTP ${status})`)
        }
      } else if (error.request) {
        throw new Error('网络连接失败，请检查网络后重试')
      } else {
        throw new Error(error.message || '未知错误')
      }
    }
  },

  /**
   * Execute a custom query with text
   * @param {string} queryText - User input query text
   * @param {number} pages - Number of pages to fetch
   * @returns {Promise} Query results
   */
  async executeCustomQuery(queryText, pages = 1) {
    try {
      console.log(`[WencaiAPI] Executing custom query: "${queryText}"`)

      const response = await request.post('/market/wencai/query', {
        query_text: queryText,
        pages
      })

      console.log('[WencaiAPI] Custom query executed successfully')
      return response
    } catch (error) {
      console.error('[WencaiAPI] Custom query failed:', error)

      if (error.response?.status === 400) {
        throw new Error('查询语句无效，请修改后重试')
      } else if (error.response?.status === 429) {
        throw new Error('查询频率过高，请稍后再试')
      }

      throw error
    }
  },

  /**
   * Get query results by query ID (for pagination)
   * @param {string} queryId - Query ID
   * @param {number} page - Page number (1-indexed)
   * @param {number} pageSize - Items per page
   * @returns {Promise} Paginated results
   */
  async getResults(queryId, page = 1, pageSize = 20) {
    try {
      const offset = (page - 1) * pageSize

      const response = await request.get('/market/wencai/results', {
        params: {
          query_id: queryId,
          limit: pageSize,
          offset
        }
      })

      return response
    } catch (error) {
      console.error(`[WencaiAPI] Failed to get results for ${queryId}:`, error)
      throw error
    }
  },

  /**
   * Get list of saved queries (for tree view)
   * @returns {Promise} List of queries
   */
  async getQueries() {
    try {
      const response = await request.get('/market/wencai/queries')
      return response
    } catch (error) {
      console.error('[WencaiAPI] Failed to get queries:', error)
      throw error
    }
  },

  /**
   * Save a stock to a watchlist group
   * @param {string} symbol - Stock symbol
   * @param {string} groupName - Group name
   * @returns {Promise} Save result
   */
  async addToGroup(symbol, groupName) {
    try {
      const response = await request.post('/watchlist/stocks', {
        symbol,
        group_name: groupName
      })

      return response
    } catch (error) {
      console.error('[WencaiAPI] Failed to add to group:', error)

      if (error.response?.status === 400) {
        throw new Error('股票已在自选股中')
      } else if (error.response?.status === 404) {
        throw new Error('分组不存在')
      }

      throw error
    }
  }
}

/**
 * Export data to CSV format
 * @param {Array} data - Table data
 * @param {string} filename - CSV filename
 */
export function exportToCSV(data, filename = 'query-results.csv') {
  if (!data || data.length === 0) {
    throw new Error('没有数据可导出')
  }

  // Extract headers from first row
  const headers = Object.keys(data[0])

  // Build CSV content
  const csvRows = [
    headers.join(','), // Header row
    ...data.map(row =>
      headers.map(header => {
        const value = row[header]
        // Escape commas in values
        return typeof value === 'string' && value.includes(',')
          ? `"${value}"`
          : value
      }).join(',')
    )
  ]

  const csvContent = csvRows.join('\n')

  // Add BOM for UTF-8 encoding (Excel compatibility)
  const blob = new Blob(['\ufeff' + csvContent], {
    type: 'text/csv;charset=utf-8;'
  })

  // Trigger download
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', filename)
  link.click()

  // Cleanup
  URL.revokeObjectURL(url)
}

export default wencaiApi
