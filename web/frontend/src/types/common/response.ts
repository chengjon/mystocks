/**
 * @fileoverview 通用API响应类型定义模块
 * @description 提供项目中API响应相关的通用类型定义
 * @module types/common
 * @version 1.0.0
 */

import type { PaginationInfo } from './pagination';

/**
 * 错误详情
 */
export interface ErrorDetail {
  errorCode: string;
  errorMessage: string;
  details?: Record<string, any>;
}

/**
 * 统一API响应类型（与后端UnifiedResponse匹配）
 */
export interface UnifiedResponse<T = any> {
  success: boolean;
  code: number;
  message: string;
  data: T | null;
  timestamp?: string;
  request_id?: string;
  errors?: ErrorDetail[];
}

/**
 * 分页API响应类型
 */
export interface UnifiedPaginatedResponse<T> extends UnifiedResponse<T> {
  pagination: PaginationInfo;
}

/**
 * 未授权响应（401）
 */
export interface UnauthorizedResponse {
  success: false;
  code: 401;
  message: string;
  data: null;
  timestamp: string;
  errors: ErrorDetail[];
}

/**
 * 禁止访问响应（403）
 */
export interface ForbiddenResponse {
  success: false;
  code: 403;
  message: string;
  data: null;
  timestamp: string;
  errors: ErrorDetail[];
}

/**
 * 未找到响应（404）
 */
export interface NotFoundResponse {
  success: false;
  code: 404;
  message: string;
  data: null;
  timestamp: string;
  errors: ErrorDetail[];
}

/**
 * 服务器错误响应（500）
 */
export interface ServerErrorResponse {
  success: false;
  code: 500;
  message: string;
  data: null;
  timestamp: string;
  errors: ErrorDetail[];
}
