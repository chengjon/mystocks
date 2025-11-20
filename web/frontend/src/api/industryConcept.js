/**
 * 行业概念分析 API
 * 提供行业/概念分类数据的查询接口
 */

import request from '@/api'

// 行业概念分析 API
export const industryConceptApi = {
  /**
   * 获取行业列表
   */
  getIndustryList() {
    return request.get('/analysis/industry/list')
  },

  /**
   * 获取概念列表
   */
  getConceptList() {
    return request.get('/analysis/concept/list')
  },

  /**
   * 获取指定行业的成分股
   * @param {string} industryCode - 行业代码
   * @param {number} limit - 限制返回数量
   */
  getIndustryStocks(industryCode, limit = 100) {
    return request.get('/analysis/industry/stocks', {
      params: { industry_code: industryCode, limit }
    })
  },

  /**
   * 获取指定概念的成分股
   * @param {string} conceptCode - 概念代码
   * @param {number} limit - 限制返回数量
   */
  getConceptStocks(conceptCode, limit = 100) {
    return request.get('/analysis/concept/stocks', {
      params: { concept_code: conceptCode, limit }
    })
  },

  /**
   * 获取行业整体表现数据
   * @param {string} industryCode - 行业代码
   */
  getIndustryPerformance(industryCode) {
    return request.get('/analysis/industry/performance', {
      params: { industry_code: industryCode }
    })
  }
}

// 为了方便使用，导出单独的函数
export const getIndustryList = industryConceptApi.getIndustryList
export const getConceptList = industryConceptApi.getConceptList
export const getIndustryStocks = industryConceptApi.getIndustryStocks
export const getConceptStocks = industryConceptApi.getConceptStocks
export const getIndustryPerformance = industryConceptApi.getIndustryPerformance

export default industryConceptApi