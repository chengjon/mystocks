/**
 * @fileoverview 通用类型定义模块
 * @description 提供项目中通用的、跨模块使用的类型定义
 * @module types/common
 * @version 1.0.0
 */

/**
 * 分页信息类型
 */
export interface PaginationInfo {
  page: number;
  page_size: number;
  total: number;
  pages?: number;
}

/**
 * 通用分页响应类型
 */
export interface PaginatedResponse<T> {
  data: T[];
  pagination: PaginationInfo;
}

/**
 * API响应包装器
 */
export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data: T;
}

/**
 * 操作结果
 */
export interface OperationResult<T = any> {
  success: boolean;
  data?: T;
  error?: {
    field?: string;
    code: string;
    message: string;
  };
}
