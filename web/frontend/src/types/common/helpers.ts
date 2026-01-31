/**
 * @fileoverview 通用工具函数类型定义模块
 * @description 提供项目中通用工具函数的类型定义
 * @module types/common
 * @version 1.0.0
 */

/**
 * 消息回调函数类型
 */
export type MessageCallback = (data: any) => void;

/**
 * 日期格式化选项
 */
export interface DateFormatOptions {
  format?: string;
  locale?: string;
  timezone?: string;
}

/**
 * 日期范围
 */
export interface DateRange {
  start: Date | string;
  end: Date | string;
}

/**
 * 排序选项
 */
export interface SortOptions {
  field: string;
  order: 'asc' | 'desc';
}

/**
 * 筛选条件
 */
export interface FilterCondition {
  field: string;
  operator: 'eq' | 'ne' | 'gt' | 'lt' | 'gte' | 'lte' | 'in' | 'contains';
  value: any;
}

/**
 * 批量操作结果
 */
export interface BatchOperationResult<T> {
  success: boolean;
  failed: number;
  total: number;
  items: T[];
  errors: string[];
}

/**
 * 防抖配置
 */
export interface DebounceConfig {
  delay: number;
  immediate?: boolean;
  maxWait?: number;
}

/**
 * 节流配置
 */
export interface ThrottleConfig {
  wait: number;
  leading?: boolean;
  trailing?: boolean;
}

/**
 * 缓存选项
 */
export interface CacheOptions {
  ttl?: number;
  maxSize?: number;
  strategy?: 'lru' | 'fifo' | 'lfu';
}
