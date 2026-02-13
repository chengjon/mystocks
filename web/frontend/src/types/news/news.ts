/**
 * @fileoverview 新闻模块类型定义
 * @description 提供新闻相关的类型定义
 * @module types/news
 * @version 1.0.0
 */

import type { UnifiedResponse, UnifiedPaginatedResponse } from '../common/response';

/**
 * 新闻分类
 */
export type NewsCategory =
  | 'market'
  | 'company'
  | 'industry'
  | 'policy'
  | 'international';

/**
 * 新闻优先级
 */
export type NewsPriority = 'low' | 'medium' | 'high' | 'breaking';

/**
 * 新闻项
 */
export interface NewsItem {
  id: string;
  title: string;
  summary: string;
  content?: string;
  category: NewsCategory;
  priority: NewsPriority;
  source?: string;
  author?: string;
  publishedAt?: string;
  updatedAt?: string;
  url?: string;
  imageUrl?: string;
  symbols?: string[];
  tags?: string[];
}

/**
 * 新闻列表响应
 */
export interface NewsListResponse extends UnifiedPaginatedResponse<NewsItem[]> {}

/**
 * 新闻详情响应
 */
export interface NewsDetailResponse extends UnifiedResponse<NewsItem> {}

/**
 * 新闻筛选条件
 */
export interface NewsFilter {
  category?: NewsCategory;
  priority?: NewsPriority;
  startDate?: string;
  endDate?: string;
  symbols?: string[];
  tags?: string[];
  keywords?: string;
}
