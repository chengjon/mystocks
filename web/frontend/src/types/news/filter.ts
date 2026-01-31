/**
 * @fileoverview 新闻过滤模块类型定义
 * @description 提供新闻过滤相关的类型定义
 * @module types/news
 * @version 1.0.0
 */

import type { UnifiedResponse } from '../common/response';
import type { NewsItem } from './news';

/**
 * 保存的筛选条件
 */
export interface SavedNewsFilter {
  id: string;
  name: string;
  filters: {
    category?: string;
    priority?: string;
    startDate?: string;
    endDate?: string;
    symbols?: string[];
    tags?: string[];
  };
  createdAt: string;
}

/**
 * 保存的筛选条件列表响应
 */
export interface SavedNewsFilterListResponse extends UnifiedResponse<SavedNewsFilter[]> {}

/**
 * 创建保存筛选条件请求
 */
export interface CreateSavedFilterRequest {
  name: string;
  filters: {
    category?: string;
    priority?: string;
    startDate?: string;
    endDate?: string;
    symbols?: string[];
    tags?: string[];
  };
}

/**
 * 创建保存筛选条件响应
 */
export interface CreateSavedFilterResponse extends UnifiedResponse<SavedNewsFilter> {}

/**
 * 删除保存筛选条件请求
 */
export interface DeleteSavedFilterRequest {
  filterId: string;
}

/**
 * 删除保存筛选条件响应
 */
export interface DeleteSavedFilterResponse extends UnifiedResponse<null> {}

/**
 * 应用保存筛选条件请求
 */
export interface ApplySavedFilterRequest {
  filterId: string;
}

/**
 * 应用保存筛选条件响应
 */
export interface ApplySavedFilterResponse extends UnifiedResponse<NewsItem[]> {}
